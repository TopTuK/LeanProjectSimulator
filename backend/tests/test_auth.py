from urllib.parse import parse_qs, urlparse

from sqlalchemy import func, select

from app import models as m
from tests.conftest import login


def _state(r) -> str:
    return parse_qs(urlparse(r.headers["location"]).query)["state"][0]


def test_login_redirects_to_yandex(client):
    r = client.get("/api/auth/yandex/login", params={"next": "/control"}, follow_redirects=False)
    assert r.status_code == 302
    url = urlparse(r.headers["location"])
    assert f"{url.scheme}://{url.netloc}{url.path}" == "https://oauth.yandex.ru/authorize"
    q = parse_qs(url.query)
    assert q["response_type"] == ["code"]
    assert q["client_id"] == ["test-client"]
    assert q["redirect_uri"] == ["http://testserver/auth/login-yandex"]
    assert len(q["state"][0]) > 20


def test_callback_signs_in_and_returns_to_next(client, db):
    r = login(client, "101", next="/control")
    assert r.status_code == 302
    assert r.headers["location"] == "/control"

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json() == {
        "id": me.json()["id"],
        "login": "user101",
        "name": "User 101",
        "email": "user101@yandex.ru",
        "avatar_url": "https://avatars.yandex.net/get-yapic/123/abc/islands-68",
    }
    assert db.scalar(select(m.User).where(m.User.yandex_id == "101")) is not None


def test_repeat_login_reuses_user(client, db):
    login(client, "102")
    first = client.get("/api/auth/me").json()["id"]
    client.post("/api/auth/logout")
    login(client, "102")
    assert client.get("/api/auth/me").json()["id"] == first
    assert db.scalar(select(func.count()).select_from(m.User).where(m.User.yandex_id == "102")) == 1


def test_callback_rejects_wrong_state(client):
    client.get("/api/auth/yandex/login", follow_redirects=False)
    r = client.get("/auth/login-yandex", params={"code": "1", "state": "forged"}, follow_redirects=False)
    assert r.status_code == 400
    assert client.get("/api/auth/me").status_code == 401


def test_callback_without_login_start(client):
    r = client.get("/auth/login-yandex", params={"code": "1", "state": "x"}, follow_redirects=False)
    assert r.status_code == 400


def test_state_is_single_use(client):
    state = _state(client.get("/api/auth/yandex/login", follow_redirects=False))
    ok = client.get("/auth/login-yandex", params={"code": "1", "state": state}, follow_redirects=False)
    assert ok.status_code == 302
    client.post("/api/auth/logout")
    again = client.get("/auth/login-yandex", params={"code": "1", "state": state}, follow_redirects=False)
    assert again.status_code == 400


def test_open_redirect_is_blocked(client):
    for bad in ("//evil.example", "https://evil.example", "/\\evil.example", "control", ""):
        client.post("/api/auth/logout")
        assert login(client, "103", next=bad).headers["location"] == "/"


def test_user_denied_access(client):
    client.get("/api/auth/yandex/login", follow_redirects=False)
    r = client.get("/auth/login-yandex", params={"error": "access_denied"}, follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/?auth_error=1"
    assert client.get("/api/auth/me").status_code == 401


def test_yandex_failure_redirects_with_error(client, yandex):
    yandex.fail = True
    r = login(client, "104")
    assert r.headers["location"] == "/?auth_error=1"
    assert client.get("/api/auth/me").status_code == 401


def test_me_and_logout(client):
    assert client.get("/api/auth/me").status_code == 401
    login(client, "105")
    assert client.get("/api/auth/me").status_code == 200
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_session_cookie_flags(client):
    cookie = login(client, "106").headers["set-cookie"].lower()
    assert "simultrain_session=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
