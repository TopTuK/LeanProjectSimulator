import pytest

from tests.conftest import login


@pytest.mark.parametrize("method,path", [
    ("post", "/api/sessions"),
    ("get", "/api/sessions/any"),
    ("get", "/api/sessions/any/snapshots"),
    ("get", "/api/sessions/any/stream"),
    ("post", "/api/sessions/any/clock/start"),
    ("post", "/api/sessions/any/clock/pause"),
    ("put", "/api/sessions/any/assignments"),
    ("post", "/api/sessions/any/leveling"),
    ("post", "/api/sessions/any/messages/1/read"),
    ("post", "/api/sessions/any/decisions/1"),
])
def test_anonymous_is_refused(client, method, path):
    r = client.get(path) if method == "get" else getattr(client, method)(path, json={})
    assert r.status_code == 401
    assert r.json()["detail"] == "login required"


def test_public_endpoints(client):
    assert client.get("/api/health").status_code == 200
    r = client.get("/api/scenarios")
    assert r.status_code == 200
    assert r.json()[0]["code"] == "webshop"


def test_session_belongs_to_creator(client):
    login(client, "201")
    sid = client.post("/api/sessions", json={"speed": "test"}).json()["id"]
    assert client.get(f"/api/sessions/{sid}").status_code == 200

    client.post("/api/auth/logout")
    login(client, "202")
    assert client.get(f"/api/sessions/{sid}").status_code == 404
    assert client.post(f"/api/sessions/{sid}/clock/start").status_code == 404
    assert client.get(f"/api/sessions/{sid}/stream").status_code == 404

    client.post("/api/auth/logout")
    login(client, "201")
    assert client.post(f"/api/sessions/{sid}/clock/start").json()["status"] == "running"


def test_logout_ends_access(auth_client):
    sid = auth_client.post("/api/sessions", json={}).json()["id"]
    auth_client.post("/api/auth/logout")
    assert auth_client.get(f"/api/sessions/{sid}").status_code == 401
