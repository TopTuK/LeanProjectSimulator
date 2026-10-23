import httpx
import pytest
from sqlalchemy import create_engine, inspect, text

from app import auth
from app.auth import YandexClient, YandexError, safe_next
from app.main import upgrade_schema


class FakeResponse:
    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self._body = body

    def json(self):
        return self._body


@pytest.fixture
def ya():
    return YandexClient("cid", "csecret", "https://pmsim.pmi.moscow/auth/login-yandex")


def test_exchange_code_posts_credentials(ya, monkeypatch):
    seen = {}

    def post(url, data, timeout):
        seen.update(url=url, data=data)
        return FakeResponse(200, {"access_token": "tok", "token_type": "bearer"})

    monkeypatch.setattr(auth.httpx, "post", post)
    assert ya.exchange_code("c0de") == "tok"
    assert seen["url"] == "https://oauth.yandex.ru/token"
    assert seen["data"] == {
        "grant_type": "authorization_code", "code": "c0de", "client_id": "cid", "client_secret": "csecret",
    }


def test_exchange_code_bad_code(ya, monkeypatch):
    monkeypatch.setattr(auth.httpx, "post", lambda *a, **k: FakeResponse(400, {"error": "invalid_grant"}))
    with pytest.raises(YandexError):
        ya.exchange_code("bad")


def test_exchange_code_network_error(ya, monkeypatch):
    def post(*a, **k):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(auth.httpx, "post", post)
    with pytest.raises(YandexError):
        ya.exchange_code("c")


def test_user_info_sends_oauth_header(ya, monkeypatch):
    seen = {}

    def get(url, params, headers, timeout):
        seen.update(url=url, params=params, headers=headers)
        return FakeResponse(200, {"id": "42", "login": "ivan"})

    monkeypatch.setattr(auth.httpx, "get", get)
    assert ya.user_info("tok")["login"] == "ivan"
    assert seen["url"] == "https://login.yandex.ru/info"
    assert seen["params"] == {"format": "json"}
    assert seen["headers"] == {"Authorization": "OAuth tok"}


def test_user_info_expired_token(ya, monkeypatch):
    monkeypatch.setattr(auth.httpx, "get", lambda *a, **k: FakeResponse(401, {}))
    with pytest.raises(YandexError):
        ya.user_info("old")


def test_authorize_url(ya):
    url = ya.authorize_url("st")
    assert url.startswith("https://oauth.yandex.ru/authorize?")
    assert "redirect_uri=https%3A%2F%2Fpmsim.pmi.moscow%2Fauth%2Flogin-yandex" in url
    assert "state=st" in url


@pytest.mark.parametrize("value,expected", [
    (None, "/"), ("", "/"), ("/control", "/control"), ("/sim/1/office?x=1", "/sim/1/office?x=1"),
    ("//evil.example", "/"), ("https://evil.example", "/"), ("/\\evil.example", "/"), ("control", "/"),
])
def test_safe_next(value, expected):
    assert safe_next(value) == expected


def test_upgrade_adds_owner_column(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with eng.begin() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY)"))
        conn.execute(text("CREATE TABLE sessions (id VARCHAR(36) PRIMARY KEY)"))
    upgrade_schema(eng)
    upgrade_schema(eng)  # idempotent
    assert "user_id" in {c["name"] for c in inspect(eng).get_columns("sessions")}
