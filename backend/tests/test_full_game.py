from datetime import timedelta

from app import models as m
from app.engine import risks, sim
from app.engine.clock import DAY_MIN, WEEK_MIN, factor, to_minute
from app.engine.rules import initial_state
from app.models import utcnow


def cfg(mode="full", risk=False):
    return {
        "scenario": "webshop", "locale": "en", "mode": mode, "speed": "test", "risk": risk,
        "already_planned": True,
    }


def _rewind(db, sid, seconds):
    s = db.get(m.SimSession, sid)
    s.last_tick_at = utcnow() - timedelta(seconds=seconds)
    db.commit()


def test_full_content_is_coherent(scn):
    assert scn.weeks == 9
    assert scn.total_days == 45
    assert list(scn.activities) == list(range(1, 41))
    assert max(a.ef for a in scn.activities.values()) == 45
    assert len(scn.decisions) == 32
    assert len(scn.risks) == 12
    assigned = {a for a, _, _ in scn.default_assignments}
    for activity in scn.activities.values():
        assert activity.name["en"] and activity.name["ru"]
        assert activity.no in assigned
        assert all(p in scn.activities for p in activity.preds)
    for event in scn.events:
        assert event["minute"] <= 45 * DAY_MIN
        assert not event["decision"] or event["decision"] in scn.decisions
    for risk in scn.risks.values():
        assert risk.identify_event in {e["key"] for e in scn.events}
        assert risk.occurrence_event in {e["key"] for e in scn.events}
        assert risk.decision in scn.decisions
        for text in (risk.name, risk.description, risk.category):
            assert text["en"] and text["ru"]
        for option in scn.decisions[risk.decision]["options"].values():
            assert option["learning_point"]["en"] and option["learning_point"]["ru"]


def test_demo_remains_one_week_and_disables_risks(db, scn):
    s = sim.create_session(db, cfg(mode="demo", risk=True))
    assert s.config["risk"] is False
    assert sim.end_minutes(scn, s.config) == WEEK_MIN
    assert len(sim.build_state(db, s)["decisions"]) == 0


def test_full_session_reaches_week_nine(auth_client, db):
    client = auth_client
    r = client.post("/api/sessions", json=cfg(risk=True))
    assert r.status_code == 201
    sid = r.json()["id"]
    assert r.json()["clock"]["end_minutes"] == 45 * DAY_MIN
    assert len(r.json()["activities"]) == 40

    client.post(f"/api/sessions/{sid}/clock/start")
    _rewind(db, sid, 5400)
    st = client.get(f"/api/sessions/{sid}").json()
    assert st["status"] == "ended"
    assert st["clock"]["week"] == 9 and st["clock"]["weekday"] == 4 and st["clock"]["hour"] == 19
    assert len(st["decisions"]) == 32
    assert all(d["status"] == "resolved" for d in st["decisions"])
    assert len(st["risks"]) == 12
    assert all(r["status"] in ("occurred", "avoided") for r in st["risks"])
    assert 0 <= st["game"]["score"] <= 100
    assert len(client.get(f"/api/sessions/{sid}/snapshots").json()) == 496
    assert client.post(f"/api/sessions/{sid}/clock/start").status_code == 409


def test_full_session_can_disable_risks(db):
    s = sim.create_session(db, cfg())
    sim.start(db, s)
    sim.advance(db, s, s.last_tick_at + timedelta(seconds=5400))
    db.commit()
    st = sim.build_state(db, s)
    assert st["status"] == "ended"
    assert len(st["decisions"]) == 20
    assert st["risks"] == []
    assert not any("Risk identified" in m["subject"] for m in st["messages"])


def test_risk_response_changes_exposure(db):
    s = sim.create_session(db, cfg(risk=True))
    sim.start(db, s)
    seconds = to_minute(2, 0, 9) / factor("test")
    sim.advance(db, s, s.last_tick_at + timedelta(seconds=seconds))
    db.commit()
    st = sim.build_state(db, s)
    vendor = next(r for r in st["risks"] if r["key"] == "vendor")
    assert vendor["status"] == "open"
    assert vendor["probability"] == 45.0
    before = s.state["other_cost"]
    sim.decide(db, s, vendor["decision_id"], "b")
    db.commit()
    vendor = next(r for r in sim.build_state(db, s)["risks"] if r["key"] == "vendor")
    assert vendor["status"] == "responded"
    assert vendor["probability"] == 20.2
    assert s.state["other_cost"] == before + 500


def test_deterministic_risk_outcome_and_scaled_impact(scn, monkeypatch):
    risk = scn.risks["vendor"]
    option = scn.decisions[risk.decision]["options"]["b"]
    assert risks.draw("session-a", "vendor") == risks.draw("session-a", "vendor")
    assert risks.draw("session-a", "vendor") != risks.draw("session-b", "vendor")
    assert risks.probability(risk, option, {"difficulty_risk": "easy"}) < risks.probability(risk, option, {})
    assert risks.probability(risk, option, {"difficulty_risk": "hard"}) > risks.probability(risk, option, {})
    monkeypatch.setattr(risks, "draw", lambda _sid, _key: 0.1)
    state = initial_state(scn)
    outcome = risks.occur(scn, state, risk, option, {}, "session-a", 0)
    assert outcome["occurred"] is True
    assert state["other_cost"] == 700
    assert state["effort"]["6"] == scn.activities[6].effort + 16 * 0.7
    monkeypatch.setattr(risks, "draw", lambda _sid, _key: 0.9)
    state = initial_state(scn)
    assert risks.occur(scn, state, risk, option, {}, "session-a", 0)["occurred"] is False
    assert state["other_cost"] == 0


def test_reasonable_playthrough_can_complete_project(db):
    s = sim.create_session(db, cfg())
    proposal = sim.propose_leveling(db, s)
    sim.set_assignments(db, s, proposal["assignments"])
    sim.start(db, s)
    now = s.last_tick_at
    for day in range(45):
        if day == 35:
            sim.pause(db, s)
            assignments = sim.assignments_of(db, s) + [(22, 11, 100), (24, 11, 100)]
            sim.set_assignments(db, s, [
                {"activity_no": a, "resource_no": r, "percent": p} for a, r, p in assignments
            ])
            sim.start(db, s)
            s.last_tick_at = now
        for _ in range(2):
            now += timedelta(seconds=60)
            sim.advance(db, s, now)
            for d in sim.build_state(db, s)["decisions"]:
                if d["status"] == "open":
                    option = "c" if d["key"] in ("remote", "teamevent", "photos") else "b"
                    sim.decide(db, s, d["id"], option)
            db.commit()
    st = sim.build_state(db, s)
    assert st["status"] == "ended"
    assert all(a["status"] == "done" for a in st["activities"]), [
        (a["no"], a["progress"], a["status"]) for a in st["activities"] if a["status"] != "done"
    ]
    assert st["game"]["completion"] == 100
    assert st["game"]["auto_decisions"] == 0
    assert st["game"]["score"] >= 90
