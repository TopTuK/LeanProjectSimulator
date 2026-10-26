import os
import tempfile
from urllib.parse import parse_qs, urlparse

_db = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db}"
os.environ["SESSION_SECRET"] = "test-session-secret"
os.environ["COOKIE_SECURE"] = "false"
os.environ["YANDEX_CLIENT_ID"] = "test-client"
os.environ["YANDEX_CLIENT_SECRET"] = "test-secret"
os.environ["YANDEX_REDIRECT_URI"] = "http://testserver/auth/login-yandex"
os.environ["VK_CLIENT_ID"] = "test-vk"
os.environ["VK_REDIRECT_URI"] = "http://testserver/auth/login-vk"
os.environ["GOOGLE_CLIENT_ID"] = "test-google.apps.googleusercontent.com"
os.environ["GOOGLE_CLIENT_SECRET"] = "test-google-secret"
os.environ["GOOGLE_REDIRECT_URI"] = "http://testserver/auth/login-google"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.auth import (  # noqa: E402
    GoogleClient,
    GoogleError,
    VkClient,
    VkError,
    YandexClient,
    YandexError,
    get_google,
    get_vk,
    get_yandex,
)
from app.db import SessionLocal  # noqa: E402
from app.engine.scenario import get_scenario  # noqa: E402
from app.main import app, init_db  # noqa: E402

init_db()


class FakeYandex(YandexClient):
    """Yandex ID without the network: the authorization code is the Yandex user id."""

    def __init__(self):
        super().__init__("test-client", "test-secret", "http://testserver/auth/login-yandex")
        self.fail = False

    def exchange_code(self, code: str) -> str:
        if self.fail:
            raise YandexError("boom")
        return f"token-{code}"

    def user_info(self, token: str) -> dict:
        uid = token.removeprefix("token-")
        return {
            "id": uid,
            "login": f"user{uid}",
            "default_email": f"user{uid}@yandex.ru",
            "display_name": f"User {uid}",
            "default_avatar_id": "123/abc",
            "is_avatar_empty": False,
        }


def login(client: TestClient, yandex_id: str = "1", next: str | None = None):
    """Walk the real redirect flow; returns the callback response."""
    params = {"next": next} if next is not None else {}
    r = client.get("/api/auth/yandex/login", params=params, follow_redirects=False)
    state = parse_qs(urlparse(r.headers["location"]).query)["state"][0]
    return client.get("/auth/login-yandex", params={"code": yandex_id, "state": state}, follow_redirects=False)


class FakeVk(VkClient):
    """VK ID without the network: the authorization code is the VK user id."""

    def __init__(self):
        super().__init__("test-vk", "http://testserver/auth/login-vk")
        self.fail = False
        self.exchanges: list[dict] = []

    def exchange_code(self, code: str, verifier: str, device_id: str, state: str) -> str:
        if self.fail:
            raise VkError("boom")
        self.exchanges.append({"code": code, "verifier": verifier, "device_id": device_id, "state": state})
        return f"token-{code}"

    def user_info(self, token: str) -> dict:
        uid = token.removeprefix("token-")
        return {
            "user_id": uid,
            "first_name": "Ivan",
            "last_name": f"Vk{uid}",
            "email": f"vk{uid}@mail.ru",
            "avatar": f"https://sun.userapi.com/{uid}.jpg",
        }


def login_vk(client: TestClient, vk_id: str = "1", provider: str | None = None, next: str | None = None):
    """Walk the VK ID redirect flow; returns the callback response."""
    params = {k: v for k, v in (("next", next), ("provider", provider)) if v is not None}
    r = client.get("/api/auth/vk/login", params=params, follow_redirects=False)
    state = parse_qs(urlparse(r.headers["location"]).query)["state"][0]
    return client.get(
        "/auth/login-vk", params={"code": vk_id, "state": state, "device_id": "dev-1"}, follow_redirects=False,
    )


class FakeGoogle(GoogleClient):
    """Google without the network: the authorization code is the Google "sub"."""

    def __init__(self):
        super().__init__("test-google.apps.googleusercontent.com", "test-google-secret",
                         "http://testserver/auth/login-google")
        self.fail = False
        self.email_verified = True
        self.exchanges: list[dict] = []

    def exchange_code(self, code: str, verifier: str) -> str:
        if self.fail:
            raise GoogleError("boom")
        self.exchanges.append({"code": code, "verifier": verifier})
        return f"token-{code}"

    def user_info(self, token: str) -> dict:
        uid = token.removeprefix("token-")
        return {
            "sub": uid,
            "name": f"Anna G{uid}",
            "email": f"g{uid}@gmail.com",
            "email_verified": self.email_verified,
            "picture": f"https://lh3.googleusercontent.com/a/{uid}",
        }


def login_google(client: TestClient, google_id: str = "1", next: str | None = None):
    """Walk the Google redirect flow; returns the callback response."""
    params = {"next": next} if next is not None else {}
    r = client.get("/api/auth/google/login", params=params, follow_redirects=False)
    state = parse_qs(urlparse(r.headers["location"]).query)["state"][0]
    return client.get("/auth/login-google", params={"code": google_id, "state": state}, follow_redirects=False)


@pytest.fixture
def google():
    fake = FakeGoogle()
    app.dependency_overrides[get_google] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_google, None)


@pytest.fixture
def vk():
    fake = FakeVk()
    app.dependency_overrides[get_vk] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_vk, None)


@pytest.fixture
def yandex():
    fake = FakeYandex()
    app.dependency_overrides[get_yandex] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_yandex, None)


@pytest.fixture
def client(yandex, vk, google):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_client(client):
    login(client)
    return client


@pytest.fixture
def db():
    with SessionLocal() as s:
        yield s


@pytest.fixture
def scn(db):
    return get_scenario(db, "webshop")
