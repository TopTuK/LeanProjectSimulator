import base64
import hashlib
from urllib.parse import parse_qs, urlparse

from sqlalchemy import func, select

from app import models as m
from tests.conftest import login, login_google, login_vk


def _query(r) -> dict:
    return parse_qs(urlparse(r.headers["location"]).query)


def test_login_redirects_to_google_with_pkce(client):
    r = client.get("/api/auth/google/login", params={"next": "/control"}, follow_redirects=False)
    assert r.status_code == 302
    url = urlparse(r.headers["location"])
    assert f"{url.scheme}://{url.netloc}{url.path}" == "https://accounts.google.com/o/oauth2/v2/auth"
    q = parse_qs(url.query)
    assert q["response_type"] == ["code"]
    assert q["client_id"] == ["test-google.apps.googleusercontent.com"]
    assert q["redirect_uri"] == ["http://testserver/auth/login-google"]
    assert q["scope"] == ["openid email profile"]
    assert q["code_challenge_method"] == ["S256"]
    assert len(q["state"][0]) > 20
    assert len(q["code_challenge"][0]) == 43


def test_verifier_matches_challenge(client, google):
    q = _query(client.get("/api/auth/google/login", follow_redirects=False))
    client.get("/auth/login-google", params={"code": "7", "state": q["state"][0]}, follow_redirects=False)
    sent = google.exchanges[-1]
    digest = hashlib.sha256(sent["verifier"].encode()).digest()
    assert base64.urlsafe_b64encode(digest).rstrip(b"=").decode() == q["code_challenge"][0]
    assert sent["code"] == "7"


def test_callback_signs_in_and_returns_to_next(client, db):
    r = login_google(client, "301", next="/control")
    assert r.status_code == 302
    assert r.headers["location"] == "/control"

    me = client.get("/api/auth/me").json()
    assert me == {
        "id": me["id"],
        "provider": "google",
        "login": None,
        "name": "Anna G301",
        "email": "g301@gmail.com",
        "avatar_url": "https://lh3.googleusercontent.com/a/301",
    }
    user = db.scalar(select(m.User).where(m.User.google_id == "301"))
    assert user is not None and user.yandex_id is None and user.vk_id is None


def test_unverified_email_is_not_stored(client, google):
    google.email_verified = False
    login_google(client, "302")
    assert client.get("/api/auth/me").json()["email"] is None


def test_repeat_login_reuses_user(client, db):
    login_google(client, "303")
    first = client.get("/api/auth/me").json()["id"]
    client.post("/api/auth/logout")
    login_google(client, "303")
    assert client.get("/api/auth/me").json()["id"] == first
    assert db.scalar(select(func.count()).select_from(m.User).where(m.User.google_id == "303")) == 1


def test_google_vk_and_yandex_accounts_stay_separate(client):
    ids = {}
    for provider, sign_in in (("yandex", login), ("vk", login_vk), ("google", login_google)):
        client.post("/api/auth/logout")
        sign_in(client, "304")
        me = client.get("/api/auth/me").json()
        assert me["provider"] == provider
        ids[provider] = me["id"]
    assert len(set(ids.values())) == 3


def test_callback_rejects_wrong_state(client):
    client.get("/api/auth/google/login", follow_redirects=False)
    r = client.get("/auth/login-google", params={"code": "1", "state": "forged"}, follow_redirects=False)
    assert r.status_code == 400
    assert client.get("/api/auth/me").status_code == 401


def test_callback_without_login_start(client):
    r = client.get("/auth/login-google", params={"code": "1", "state": "x"}, follow_redirects=False)
    assert r.status_code == 400


def test_state_is_single_use(client):
    state = _query(client.get("/api/auth/google/login", follow_redirects=False))["state"][0]
    params = {"code": "1", "state": state}
    assert client.get("/auth/login-google", params=params, follow_redirects=False).status_code == 302
    client.post("/api/auth/logout")
    assert client.get("/auth/login-google", params=params, follow_redirects=False).status_code == 400


def test_open_redirect_is_blocked(client):
    for bad in ("//evil.example", "https://evil.example", "/\\evil.example", "control", ""):
        client.post("/api/auth/logout")
        assert login_google(client, "305", next=bad).headers["location"] == "/"


def test_user_denied_access(client):
    client.get("/api/auth/google/login", follow_redirects=False)
    r = client.get("/auth/login-google", params={"error": "access_denied"}, follow_redirects=False)
    assert r.headers["location"] == "/?auth_error=1"
    assert client.get("/api/auth/me").status_code == 401


def test_provider_failure(client, google):
    google.fail = True
    r = login_google(client, "306")
    assert r.headers["location"] == "/?auth_error=1"
    assert client.get("/api/auth/me").status_code == 401
