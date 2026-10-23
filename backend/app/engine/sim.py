"""Session lifecycle: create, advance the clock, deliver events, decide, build the view."""

import copy
import math
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app import models as m
from app.engine import rules
from app.engine.clock import (
    DEMO_WEEKS, WEEK_MIN, describe, factor, is_work_hour, to_minute, week_of_hour, work_days,
)
from app.engine.leveling import level
from app.engine.scenario import ScenarioData, get_scenario
from app.models import utcnow

END_MINUTES = DEMO_WEEKS * WEEK_MIN


class SimError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


# ---------------------------------------------------------------- helpers


def tr(text: dict | None, locale: str) -> str | None:
    if text is None:
        return None
    return text.get(locale) or text.get("en")


def load_session(db: Session, session_id: str, lock: bool = False, owner_id: int | None = None) -> m.SimSession:
    s = db.get(m.SimSession, session_id, with_for_update=lock)
    # someone else's session looks the same as a missing one
    if s is None or (owner_id is not None and s.user_id != owner_id):
        raise SimError(404, "session not found")
    return s


def scenario_for(db: Session, s: m.SimSession) -> ScenarioData:
    scn = get_scenario(db, s.scenario_code)
    if scn is None:
        raise SimError(500, "scenario missing")
    return scn


def assignments_of(db: Session, s: m.SimSession) -> rules.Assignments:
    rows = db.scalars(select(m.Assignment).where(m.Assignment.session_id == s.id).order_by(m.Assignment.id))
    return [(a.activity_no, a.resource_no, a.percent) for a in rows]


def seen_action(db: Session, s: m.SimSession, client_action_id: str | None) -> bool:
    if not client_action_id:
        return False
    return db.scalar(
        select(m.ActionLog.id).where(
            m.ActionLog.session_id == s.id, m.ActionLog.client_action_id == client_action_id
        )
    ) is not None


def log_action(db: Session, s: m.SimSession, action: str, payload: dict, client_action_id: str | None) -> None:
    db.add(m.ActionLog(
        session_id=s.id, client_action_id=client_action_id, action=action, payload=payload, minute=s.minutes,
    ))


def _save_state(s: m.SimSession, state: dict) -> None:
    s.state = state
    flag_modified(s, "state")


# ---------------------------------------------------------------- lifecycle


def create_session(db: Session, cfg: dict, user_id: int | None = None) -> m.SimSession:
    scn = get_scenario(db, cfg["scenario"])
    if scn is None:
        raise SimError(400, "unknown scenario")
    s = m.SimSession(
        id=str(uuid.uuid4()), user_id=user_id, scenario_code=scn.code, locale=cfg["locale"], config=cfg,
        status="ready", minutes=0.0, state=rules.initial_state(scn),
    )
    db.add(s)
    db.flush()
    if cfg.get("already_planned", True):
        for act, res, pct in scn.default_assignments:
            db.add(m.Assignment(session_id=s.id, activity_no=act, resource_no=res, percent=pct))
    state = copy.deepcopy(s.state)
    _deliver(db, s, scn, state)
    _save_state(s, state)
    db.flush()
    _snapshot(db, s, scn, state, assignments_of(db, s))
    log_action(db, s, "create", cfg, None)
    db.commit()
    return s


def advance(db: Session, s: m.SimSession, now: datetime | None = None) -> bool:
    """Move a running clock forward to `now`. Returns True if anything changed."""
    if s.status != "running":
        return False
    now = now or utcnow()
    last = s.last_tick_at or now
    if last.tzinfo is None:
        last = last.replace(tzinfo=now.tzinfo)
    elapsed = max((now - last).total_seconds(), 0.0)
    s.last_tick_at = now
    target = min(s.minutes + elapsed * factor(s.config.get("speed", "demo")), END_MINUTES)
    if target <= s.minutes:
        return False

    scn = scenario_for(db, s)
    state = copy.deepcopy(s.state)
    assignments = assignments_of(db, s)
    while True:
        boundary = (math.floor(s.minutes / 60 + 1e-9) + 1) * 60
        if boundary > target + 1e-9:
            break
        hour_index = int(boundary // 60) - 1
        if is_work_hour(hour_index):
            rules.work_hour(scn, state, assignments, week_of_hour(hour_index), boundary, s.config)
        s.minutes = float(boundary)
        _deliver(db, s, scn, state)
        _auto_resolve(db, s, scn, state)
        _snapshot(db, s, scn, state, assignments)
    s.minutes = target
    _deliver(db, s, scn, state)
    _auto_resolve(db, s, scn, state)

    if s.minutes >= END_MINUTES - 1e-9:
        s.minutes = float(END_MINUTES)
        _auto_resolve(db, s, scn, state, force=True)
        s.status = "ended"
        log_action(db, s, "end", {}, None)
    _save_state(s, state)
    return True


def start(db: Session, s: m.SimSession) -> None:
    if s.status == "ended":
        raise SimError(409, "simulation has ended")
    if s.status != "running":
        s.status = "running"
        s.last_tick_at = utcnow()


def pause(db: Session, s: m.SimSession) -> None:
    if s.status == "running":
        advance(db, s)
        if s.status == "running":
            s.status = "paused"
            s.last_tick_at = None


def set_assignments(db: Session, s: m.SimSession, items: list[dict]) -> None:
    if s.status == "running":
        raise SimError(409, "pause the clock before changing assignments")
    if s.status == "ended":
        raise SimError(409, "simulation has ended")
    scn = scenario_for(db, s)
    seen: set[tuple[int, int]] = set()
    for it in items:
        if it["activity_no"] not in scn.activities or it["resource_no"] not in scn.resources:
            raise SimError(422, "unknown activity or resource")
        key = (it["activity_no"], it["resource_no"])
        if key in seen:
            raise SimError(422, "duplicate assignment")
        seen.add(key)
    for row in db.scalars(select(m.Assignment).where(m.Assignment.session_id == s.id)):
        db.delete(row)
    for it in items:
        if it["percent"] > 0:
            db.add(m.Assignment(session_id=s.id, **it))


def propose_leveling(db: Session, s: m.SimSession) -> dict:
    scn = scenario_for(db, s)
    proposal, changes = level(scn, s.state, assignments_of(db, s), s.minutes)
    return {
        "assignments": [{"activity_no": a, "resource_no": r, "percent": p} for a, r, p in proposal],
        "changes": changes,
    }


def mark_read(db: Session, s: m.SimSession, message_id: int) -> None:
    msg = db.get(m.Message, message_id)
    if msg is None or msg.session_id != s.id:
        raise SimError(404, "message not found")
    msg.read = True


def decide(db: Session, s: m.SimSession, decision_id: int, option: str) -> None:
    if s.status == "ended":
        raise SimError(409, "simulation has ended")
    sd = db.get(m.SessionDecision, decision_id)
    if sd is None or sd.session_id != s.id:
        raise SimError(404, "decision not found")
    if sd.option_key is not None:
        raise SimError(409, "decision already taken")
    scn = scenario_for(db, s)
    dec = scn.decisions[sd.decision_key]
    if option == "postpone":
        week = describe(s.minutes)["week"]
        deadline = to_minute(week, 4, 12)
        if sd.postponed or deadline <= s.minutes:
            raise SimError(409, "cannot postpone this decision")
        sd.postponed = True
        sd.deadline_minute = deadline
        return
    if option not in dec["options"]:
        raise SimError(422, "unknown option")
    state = copy.deepcopy(s.state)
    _resolve(db, s, scn, state, sd, option, "team")
    _save_state(s, state)
    _snapshot(db, s, scn, state, assignments_of(db, s))


# ---------------------------------------------------------------- internals


def _deliver(db: Session, s: m.SimSession, scn: ScenarioData, state: dict) -> None:
    for ev in scn.events:
        if ev["minute"] > s.minutes + 1e-9:
            break
        if ev["key"] in state["delivered"]:
            continue
        state["delivered"].append(ev["key"])
        if ev["effects"]:
            rules.apply_effects(scn, state, ev["effects"], s.config, s.minutes)
        if ev["channel"] in ("mail", "phone"):
            db.add(m.Message(session_id=s.id, event_key=ev["key"], minute=ev["minute"]))
        if ev["decision"]:
            dec = scn.decisions[ev["decision"]]
            db.add(m.SessionDecision(
                session_id=s.id, decision_key=dec["key"], event_key=ev["key"], opened_minute=ev["minute"],
                deadline_minute=ev["minute"] + dec["deadline_hours"] * 60,
            ))
    db.flush()


def _auto_resolve(db: Session, s: m.SimSession, scn: ScenarioData, state: dict, force: bool = False) -> None:
    rows = db.scalars(
        select(m.SessionDecision).where(m.SessionDecision.session_id == s.id, m.SessionDecision.option_key.is_(None))
    )
    for sd in rows:
        if force or sd.deadline_minute <= s.minutes + 1e-9:
            _resolve(db, s, scn, state, sd, scn.decisions[sd.decision_key]["default"], "auto")


def _resolve(db: Session, s: m.SimSession, scn: ScenarioData, state: dict, sd: m.SessionDecision, option: str, by: str) -> None:
    opt = scn.decisions[sd.decision_key]["options"][option]
    rules.apply_effects(scn, state, opt["effects"], s.config, s.minutes)
    sd.option_key = option
    sd.resolved_by = by
    sd.resolved_minute = s.minutes


def _snapshot(db: Session, s: m.SimSession, scn: ScenarioData, state: dict, assignments: rules.Assignments) -> None:
    mon = rules.money(scn, state, assignments, s.minutes)
    idx = rules.indexes(state, mon)
    db.add(m.Snapshot(
        session_id=s.id, minute=s.minutes, cost_idx=idx["cost"], schedule_idx=idx["schedule"],
        quality_idx=idx["quality"], motivation_idx=idx["motivation"], ac=mon["labour_actual"], ev=mon["ev"],
        pv=mon["pv"], hours=mon["hours"],
    ))


# ---------------------------------------------------------------- view


def build_state(db: Session, s: m.SimSession) -> dict:
    scn = scenario_for(db, s)
    loc = s.locale
    state = s.state
    assignments = assignments_of(db, s)
    mon = rules.money(scn, state, assignments, s.minutes)
    week_now = describe(s.minutes)["week"]
    ready = {n for n in scn.activities if rules.is_ready(scn, state, n)}

    activities = []
    for n, a in scn.activities.items():
        prog = state["progress"][str(n)]
        pa = mon["per_activity"][n]
        if rules.is_done(state, n):
            status = "done"
        elif n in ready:
            status = "active" if prog["start"] is not None else "ready"
        else:
            status = "waiting"
        activities.append({
            "no": n, "name": tr(a.name, loc), "duration": a.duration, "milestone": a.milestone,
            "preds": a.preds, "es": a.es, "ef": a.ef, "ls": a.ls, "lf": a.lf, "slack": a.slack,
            "critical": a.critical, "level": a.level,
            "planned_effort": a.effort, "effort": state["effort"][str(n)], "done": prog["done"],
            "planned_cost": a.planned_cost, "actual_cost": pa["actual"], "eac": pa["eac"],
            "progress": pa["progress"], "status": status,
            "started_minute": prog["start"], "finished_minute": prog["end"],
        })

    # weekly load per person, from the baseline windows of unfinished work
    resources = []
    for r in scn.resources.values():
        weeks = []
        for w in range(1, scn.weeks + 1):
            day_lo, day_hi = (w - 1) * 5, w * 5
            acts = []
            peak = 0
            for day in range(day_lo, day_hi):
                day_load = 0
                for act, res, pct in assignments:
                    a = scn.activities[act]
                    if res == r.no and a.es <= day < max(a.ef, a.es + 1) and not rules.is_done(state, act):
                        day_load += pct
                        if act not in acts:
                            acts.append(act)
                peak = max(peak, day_load)
            weeks.append({"week": w, "state": rules.resource_state(scn, state, r.no, w), "load": peak, "activities": acts})
        resources.append({
            "no": r.no, "name": tr(r.name, loc), "role": tr(r.role, loc), "rate": r.rate,
            "state_now": rules.resource_state(scn, state, r.no, week_now), "weeks": weeks,
        })

    events = {e["key"]: e for e in scn.events}
    msgs = db.scalars(select(m.Message).where(m.Message.session_id == s.id).order_by(m.Message.minute.desc(), m.Message.id.desc()))
    decision_rows = list(db.scalars(
        select(m.SessionDecision).where(m.SessionDecision.session_id == s.id).order_by(m.SessionDecision.opened_minute)
    ))
    decision_by_event = {d.event_key: d.id for d in decision_rows}
    messages = []
    for msg in msgs:
        e = events[msg.event_key]
        messages.append({
            "id": msg.id, "channel": e["channel"], "sender": tr(e["sender"], loc), "subject": tr(e["subject"], loc),
            "body": tr(e["body"], loc), "minute": msg.minute, "time": describe(msg.minute), "read": msg.read,
            "decision_id": decision_by_event.get(msg.event_key),
        })

    decisions = []
    learning = []
    for sd in decision_rows:
        dec = scn.decisions[sd.decision_key]
        chosen = dec["options"].get(sd.option_key) if sd.option_key else None
        if chosen and chosen["learning_point"]:
            learning.append(tr(chosen["learning_point"], loc))
        decisions.append({
            "id": sd.id, "key": sd.decision_key, "subject": tr(events[sd.event_key]["subject"], loc),
            "prompt": tr(dec["prompt"], loc),
            "options": [{"key": o["key"], "label": tr(o["label"], loc)} for o in dec["options"].values()],
            "opened_minute": sd.opened_minute, "deadline_minute": sd.deadline_minute,
            "deadline": describe(sd.deadline_minute), "postponed": sd.postponed,
            "status": "open" if sd.option_key is None else "resolved",
            "option_key": sd.option_key, "option_label": tr(chosen["label"], loc) if chosen else None,
            "resolved_by": sd.resolved_by, "feedback": tr(chosen["feedback"], loc) if chosen else None,
            "learning_point": tr(chosen["learning_point"], loc) if chosen else None,
            "effects": chosen["effects"] if chosen else None,
        })

    calendar = [
        {"key": e["key"], "week": e["week"], "weekday": e["weekday"], "hour": e["hour"],
         "duration": e["duration"], "channel": e["channel"], "title": tr(e["subject"], loc),
         "body": tr(e["body"], loc), "delivered": e["key"] in state["delivered"]}
        for e in scn.events if e["channel"] == "meeting"
    ]

    ended = s.status == "ended"
    return {
        "id": s.id,
        "status": s.status,
        "locale": loc,
        "config": s.config,
        "clock": {
            "minutes": s.minutes, "end_minutes": END_MINUTES, "factor": factor(s.config.get("speed", "demo")),
            "work_days": work_days(s.minutes), **describe(s.minutes, at_end=ended),
        },
        "indexes": rules.indexes(state, mon),
        "money": {k: v for k, v in mon.items() if k != "per_activity"},
        "scenario": {
            "code": scn.code, "title": tr(scn.title, loc), "description": tr(scn.description, loc),
            "weeks": scn.weeks, "currency": scn.currency, "total_days": scn.total_days,
        },
        "activities": activities,
        "resources": resources,
        "assignments": [{"activity_no": a, "resource_no": r, "percent": p} for a, r, p in assignments],
        "messages": messages,
        "decisions": decisions,
        "learning_points": learning,
        "calendar": calendar,
    }


def snapshots(db: Session, s: m.SimSession) -> list[dict]:
    rows = db.scalars(select(m.Snapshot).where(m.Snapshot.session_id == s.id).order_by(m.Snapshot.minute, m.Snapshot.id))
    return [
        {"minute": r.minute, "cost": r.cost_idx, "schedule": r.schedule_idx, "quality": r.quality_idx,
         "motivation": r.motivation_idx, "ac": r.ac, "ev": r.ev, "pv": r.pv, "hours": r.hours}
        for r in rows
    ]
