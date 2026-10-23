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

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.auth import YandexClient, YandexError, get_yandex  # noqa: E402
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


@pytest.fixture
def yandex():
    fake = FakeYandex()
    app.dependency_overrides[get_yandex] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_yandex, None)


@pytest.fixture
def client(yandex):
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
