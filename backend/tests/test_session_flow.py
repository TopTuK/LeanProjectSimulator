from datetime import timedelta

from app import models as m
from app.models import utcnow


def _rewind(db, sid, seconds):
    s = db.get(m.SimSession, sid)
    s.last_tick_at = utcnow() - timedelta(seconds=seconds)
    db.commit()


def test_full_demo_week(auth_client, db):
    client = auth_client
    r = client.post("/api/sessions", json={"locale": "ru", "speed": "test"})
    assert r.status_code == 201
    st = r.json()
    sid = st["id"]
    assert st["status"] == "ready"
    assert st["indexes"] == {"cost": 100.0, "schedule": 100.0, "quality": 100.0, "motivation": 100.0}
    assert st["messages"][0]["subject"] == "Добро пожаловать"
    assert len(st["assignments"]) > 10

    st = client.post(f"/api/sessions/{sid}/clock/start", json={"client_action_id": "a1"}).json()
    assert st["status"] == "running"

    # test speed: 45 s per week -> 15 s is Wednesday morning-ish
    _rewind(db, sid, 15)
    st = client.get(f"/api/sessions/{sid}").json()
    assert st["clock"]["weekday"] >= 1
    open_dec = [d for d in st["decisions"] if d["status"] == "open"]
    resolved = [d for d in st["decisions"] if d["status"] == "resolved"]
    assert resolved or open_dec
    assert st["activities"][0]["progress"] > 0.5

    # editing assignments while running is refused
    r = client.put(f"/api/sessions/{sid}/assignments", json={"assignments": []})
    assert r.status_code == 409

    st = client.post(f"/api/sessions/{sid}/clock/pause").json()
    assert st["status"] == "paused"
    for d in st["decisions"]:
        if d["status"] == "open":
            st = client.post(f"/api/sessions/{sid}/decisions/{d['id']}", json={"option": d["options"][0]["key"]}).json()
    assert all(d["status"] == "resolved" for d in st["decisions"])
    assert any(d["resolved_by"] == "team" for d in st["decisions"])

    lv = client.post(f"/api/sessions/{sid}/leveling").json()
    r = client.put(f"/api/sessions/{sid}/assignments", json={"assignments": lv["assignments"]})
    assert r.status_code == 200

    client.post(f"/api/sessions/{sid}/clock/start")
    _rewind(db, sid, 60)
    st = client.get(f"/api/sessions/{sid}").json()
    assert st["status"] == "ended"
    assert st["clock"]["weekday"] == 4 and st["clock"]["hour"] == 19
    assert all(d["status"] == "resolved" for d in st["decisions"])
    assert len(st["decisions"]) == 4
    snaps = client.get(f"/api/sessions/{sid}/snapshots").json()
    assert len(snaps) >= 55

    r = client.post(f"/api/sessions/{sid}/clock/start")
    assert r.status_code == 409


def test_idempotent_actions(auth_client):
    client = auth_client
    sid = client.post("/api/sessions", json={}).json()["id"]
    client.post(f"/api/sessions/{sid}/clock/start", json={"client_action_id": "x"})
    client.post(f"/api/sessions/{sid}/clock/pause", json={"client_action_id": "y"})
    st = client.post(f"/api/sessions/{sid}/clock/start", json={"client_action_id": "x"}).json()
    assert st["status"] == "paused"


def test_unknown_session(auth_client):
    client = auth_client
    assert client.get("/api/sessions/nope").status_code == 404
