import base64
import hashlib
from urllib.parse import parse_qs, urlparse

from sqlalchemy import func, select

from app import models as m
from tests.conftest import login, login_vk


def _query(r) -> dict:
    return parse_qs(urlparse(r.headers["location"]).query)


def test_login_redirects_to_vk_id_with_pkce(client):
    r = client.get("/api/auth/vk/login", params={"next": "/control"}, follow_redirects=False)
    assert r.status_code == 302
    url = urlparse(r.headers["location"])
    assert f"{url.scheme}://{url.netloc}{url.path}" == "https://id.vk.com/authorize"
    q = parse_qs(url.query)
    assert q["response_type"] == ["code"]
    assert q["client_id"] == ["test-vk"]
    assert q["redirect_uri"] == ["http://testserver/auth/login-vk"]
    assert q["code_challenge_method"] == ["S256"]
    assert q["scope"] == ["email"]
    assert q["provider"] == ["vkid"]
    assert len(q["state"][0]) > 20
    assert len(q["code_challenge"][0]) == 43


def test_provider_choice(client):
    for ours, theirs in (("vk", "vkid"), ("ok", "ok_ru"), ("mail", "mail_ru"), ("bogus", "vkid")):
        r = client.get("/api/auth/vk/login", params={"provider": ours}, follow_redirects=False)
        assert _query(r)["provider"] == [theirs]


def test_verifier_matches_challenge_and_device_id_is_passed(client, vk):
    r = client.get("/api/auth/vk/login", follow_redirects=False)
    q = _query(r)
    client.get("/auth/login-vk", params={"code": "7", "state": q["state"][0], "device_id": "dev-x"},
               follow_redirects=False)
    sent = vk.exchanges[-1]
    digest = hashlib.sha256(sent["verifier"].encode()).digest()
    assert base64.urlsafe_b64encode(digest).rstrip(b"=").decode() == q["code_challenge"][0]
    assert sent["device_id"] == "dev-x"
    assert sent["state"] == q["state"][0]


def test_callback_signs_in_and_returns_to_next(client, db):
    r = login_vk(client, "201", next="/control")
    assert r.status_code == 302
    assert r.headers["location"] == "/control"

    me = client.get("/api/auth/me").json()
    assert me == {
        "id": me["id"],
        "provider": "vk",
        "login": None,
        "name": "Ivan Vk201",
        "email": "vk201@mail.ru",
        "avatar_url": "https://sun.userapi.com/201.jpg",
    }
    user = db.scalar(select(m.User).where(m.User.vk_id == "201"))
    assert user is not None and user.yandex_id is None


def test_repeat_login_reuses_user(client, db):
    login_vk(client, "202")
    first = client.get("/api/auth/me").json()["id"]
    client.post("/api/auth/logout")
    login_vk(client, "202", provider="ok")
    assert client.get("/api/auth/me").json()["id"] == first
    assert db.scalar(select(func.count()).select_from(m.User).where(m.User.vk_id == "202")) == 1


def test_vk_and_yandex_accounts_stay_separate(client):
    login(client, "203")
    ya = client.get("/api/auth/me").json()
    client.post("/api/auth/logout")
    login_vk(client, "203")
    vk = client.get("/api/auth/me").json()
    assert ya["id"] != vk["id"]
    assert (ya["provider"], vk["provider"]) == ("yandex", "vk")


def test_callback_rejects_wrong_state(client):
    client.get("/api/auth/vk/login", follow_redirects=False)
    r = client.get("/auth/login-vk", params={"code": "1", "state": "forged", "device_id": "d"},
                   follow_redirects=False)
    assert r.status_code == 400
    assert client.get("/api/auth/me").status_code == 401


def test_callback_without_login_start(client):
    r = client.get("/auth/login-vk", params={"code": "1", "state": "x", "device_id": "d"}, follow_redirects=False)
    assert r.status_code == 400


def test_callback_requires_device_id(client):
    state = _query(client.get("/api/auth/vk/login", follow_redirects=False))["state"][0]
    r = client.get("/auth/login-vk", params={"code": "1", "state": state}, follow_redirects=False)
    assert r.status_code == 400


def test_state_is_single_use(client):
    state = _query(client.get("/api/auth/vk/login", follow_redirects=False))["state"][0]
    params = {"code": "1", "state": state, "device_id": "d"}
    assert client.get("/auth/login-vk", params=params, follow_redirects=False).status_code == 302
    client.post("/api/auth/logout")
    assert client.get("/auth/login-vk", params=params, follow_redirects=False).status_code == 400


def test_open_redirect_is_blocked(client):
    for bad in ("//evil.example", "https://evil.example", "/\\evil.example", "control", ""):
        client.post("/api/auth/logout")
        assert login_vk(client, "204", next=bad).headers["location"] == "/"


def test_user_denied_access(client):
    client.get("/api/auth/vk/login", follow_redirects=False)
    r = client.get("/auth/login-vk", params={"error": "access_denied"}, follow_redirects=False)
    assert r.headers["location"] == "/?auth_error=1"
    assert client.get("/api/auth/me").status_code == 401


def test_provider_failure(client, vk):
    vk.fail = True
    r = login_vk(client, "205")
    assert r.headers["location"] == "/?auth_error=1"
    assert client.get("/api/auth/me").status_code == 401
