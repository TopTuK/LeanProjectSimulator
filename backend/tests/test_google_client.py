import httpx
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from app import auth
from app.auth import GoogleClient, GoogleError
from app.main import upgrade_schema
from tests.test_yandex_client import FakeResponse


@pytest.fixture
def google():
    return GoogleClient("cid.apps.googleusercontent.com", "csecret", "https://pmsim.pmi.moscow/auth/login-google")


def _capture(monkeypatch, body, status: int = 200) -> dict:
    seen = {}

    def request(method, url, timeout, **kwargs):
        seen.update(method=method, url=url, **kwargs)
        return FakeResponse(status, body)

    monkeypatch.setattr(auth.httpx, "request", request)
    return seen


def test_exchange_code_posts_secret_and_pkce(google, monkeypatch):
    seen = _capture(monkeypatch, {"access_token": "tok", "id_token": "jwt", "token_type": "Bearer"})
    assert google.exchange_code("c0de", "verif") == "tok"
    assert (seen["method"], seen["url"]) == ("POST", "https://oauth2.googleapis.com/token")
    assert seen["data"] == {
        "grant_type": "authorization_code", "code": "c0de", "code_verifier": "verif",
        "client_id": "cid.apps.googleusercontent.com", "client_secret": "csecret",
        "redirect_uri": "https://pmsim.pmi.moscow/auth/login-google",
    }


def test_exchange_code_bad_status(google, monkeypatch):
    _capture(monkeypatch, {"error": "invalid_grant"}, status=400)
    with pytest.raises(GoogleError):
        google.exchange_code("c", "v")


def test_exchange_code_without_token(google, monkeypatch):
    _capture(monkeypatch, {"token_type": "Bearer"})
    with pytest.raises(GoogleError):
        google.exchange_code("c", "v")


def test_exchange_code_non_object_body(google, monkeypatch):
    _capture(monkeypatch, ["unexpected"])
    with pytest.raises(GoogleError, match="bad response"):
        google.exchange_code("c", "v")


def test_exchange_code_network_error(google, monkeypatch):
    def request(*a, **k):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(auth.httpx, "request", request)
    with pytest.raises(GoogleError):
        google.exchange_code("c", "v")


def test_user_info(google, monkeypatch):
    seen = _capture(monkeypatch, {"sub": "42", "name": "Anna", "picture": "https://x/a.jpg"})
    assert google.user_info("tok")["name"] == "Anna"
    assert (seen["method"], seen["url"]) == ("GET", "https://openidconnect.googleapis.com/v1/userinfo")
    assert seen["headers"] == {"Authorization": "Bearer tok"}


def test_user_info_without_sub(google, monkeypatch):
    _capture(monkeypatch, {"name": "Anna"})
    with pytest.raises(GoogleError):
        google.user_info("tok")


def test_user_info_error(google, monkeypatch):
    _capture(monkeypatch, {"error": "invalid_token"}, status=401)
    with pytest.raises(GoogleError):
        google.user_info("old")


def test_authorize_url(google):
    url = google.authorize_url("st", "chal")
    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "redirect_uri=https%3A%2F%2Fpmsim.pmi.moscow%2Fauth%2Flogin-google" in url
    assert "code_challenge=chal" in url and "scope=openid+email+profile" in url
    assert "client_secret" not in url


def test_upgrade_adds_google_id(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with eng.begin() as conn:
        conn.execute(text(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, yandex_id VARCHAR(64) UNIQUE, vk_id VARCHAR(64), "
            "login VARCHAR(255), email VARCHAR(255), name VARCHAR(255), avatar_id VARCHAR(255), "
            "created_at DATETIME, last_login_at DATETIME)"
        ))
        conn.execute(text("CREATE TABLE sessions (id VARCHAR(36) PRIMARY KEY, user_id INTEGER REFERENCES users(id))"))
        conn.execute(text(
            "INSERT INTO users (id, vk_id, name, created_at, last_login_at) "
            "VALUES (5, 'v5', 'Old', '2026-01-01 00:00:00', '2026-01-01 00:00:00')"
        ))
    upgrade_schema(eng)
    upgrade_schema(eng)  # idempotent
    assert "google_id" in {c["name"] for c in inspect(eng).get_columns("users")}
    with eng.begin() as conn:
        assert conn.execute(text("SELECT vk_id, name FROM users WHERE id = 5")).one() == ("v5", "Old")
        insert = text("INSERT INTO users (google_id, created_at, last_login_at) VALUES ('g1', '2026-01-01', '2026-01-01')")
        conn.execute(insert)
        with pytest.raises(IntegrityError):
            conn.execute(insert)
