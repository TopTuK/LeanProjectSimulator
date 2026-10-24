import httpx
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from app import auth
from app.auth import VkClient, VkError, pkce_pair
from app.main import upgrade_schema
from tests.test_yandex_client import FakeResponse


@pytest.fixture
def vk():
    return VkClient("54851437", "https://pmsim.pmi.moscow/auth/login-vk")


def _capture(monkeypatch, body: dict, status: int = 200) -> dict:
    seen = {}

    def post(url, data, timeout):
        seen.update(url=url, data=data)
        return FakeResponse(status, body)

    monkeypatch.setattr(auth.httpx, "post", post)
    return seen


def test_exchange_code_posts_pkce(vk, monkeypatch):
    seen = _capture(monkeypatch, {"access_token": "tok", "user_id": 1})
    assert vk.exchange_code("c0de", "verif", "dev", "st") == "tok"
    assert seen["url"] == "https://id.vk.com/oauth2/auth"
    assert seen["data"] == {
        "grant_type": "authorization_code", "code": "c0de", "code_verifier": "verif", "client_id": "54851437",
        "device_id": "dev", "redirect_uri": "https://pmsim.pmi.moscow/auth/login-vk", "state": "st",
    }


def test_exchange_code_error_body(vk, monkeypatch):
    # VK ID can report errors with HTTP 200
    _capture(monkeypatch, {"error": "invalid_grant", "error_description": "code expired"})
    with pytest.raises(VkError):
        vk.exchange_code("c", "v", "d", "s")


def test_exchange_code_bad_status(vk, monkeypatch):
    _capture(monkeypatch, {"error": "invalid_request"}, status=400)
    with pytest.raises(VkError):
        vk.exchange_code("c", "v", "d", "s")


def test_exchange_code_network_error(vk, monkeypatch):
    def post(*a, **k):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(auth.httpx, "post", post)
    with pytest.raises(VkError):
        vk.exchange_code("c", "v", "d", "s")


def test_user_info(vk, monkeypatch):
    seen = _capture(monkeypatch, {"user": {"user_id": "42", "first_name": "Ivan", "avatar": "https://x/a.jpg"}})
    assert vk.user_info("tok")["first_name"] == "Ivan"
    assert seen["url"] == "https://id.vk.com/oauth2/user_info"
    assert seen["data"] == {"client_id": "54851437", "access_token": "tok"}


def test_user_info_error(vk, monkeypatch):
    _capture(monkeypatch, {"error": "invalid_token"})
    with pytest.raises(VkError):
        vk.user_info("old")


def test_authorize_url(vk):
    url = vk.authorize_url("st", "chal", "mail")
    assert url.startswith("https://id.vk.com/authorize?")
    assert "redirect_uri=https%3A%2F%2Fpmsim.pmi.moscow%2Fauth%2Flogin-vk" in url
    assert "code_challenge=chal" in url and "provider=mail_ru" in url


def test_pkce_pair_is_random_and_urlsafe():
    (v1, c1), (v2, c2) = pkce_pair(), pkce_pair()
    assert v1 != v2 and c1 != c2
    assert 43 <= len(v1) <= 128 and "=" not in c1


def test_upgrade_makes_yandex_optional_and_adds_vk(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with eng.begin() as conn:
        conn.execute(text(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, yandex_id VARCHAR(64) NOT NULL UNIQUE, "
            "login VARCHAR(255), email VARCHAR(255), name VARCHAR(255), avatar_id VARCHAR(255), "
            "created_at DATETIME, last_login_at DATETIME)"
        ))
        conn.execute(text("CREATE TABLE sessions (id VARCHAR(36) PRIMARY KEY, user_id INTEGER REFERENCES users(id))"))
        conn.execute(text(
            "INSERT INTO users (id, yandex_id, name, created_at, last_login_at) "
            "VALUES (5, 'y5', 'Old', '2026-01-01 00:00:00', '2026-01-01 00:00:00')"
        ))
    upgrade_schema(eng)
    upgrade_schema(eng)  # idempotent
    columns = {c["name"]: c for c in inspect(eng).get_columns("users")}
    assert columns["yandex_id"]["nullable"] and "vk_id" in columns
    with eng.begin() as conn:
        assert conn.execute(text("SELECT yandex_id, name FROM users WHERE id = 5")).one() == ("y5", "Old")
        insert = text("INSERT INTO users (vk_id, created_at, last_login_at) VALUES ('v1', '2026-01-01', '2026-01-01')")
        conn.execute(insert)
        with pytest.raises(IntegrityError):
            conn.execute(insert)
