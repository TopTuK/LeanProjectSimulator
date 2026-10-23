from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import models as m
from app.engine.clock import WORK_HOURS_PER_DAY
from app.seed import webshop


CONTENT_TABLES = [
    m.DefaultAssignment, m.Dependency, m.Activity, m.ResourceWeek, m.Resource, m.ScenarioEvent,
]


def seed(db: Session) -> None:
    """Write the built-in scenario. Runs on every start, so content edits reach existing databases.

    Sessions only refer to activities and people by number, so replacing the rows is safe.
    """
    s = webshop
    code = s.CODE
    scenario = db.get(m.Scenario, code)
    if scenario is None:
        db.add(m.Scenario(**s.SCENARIO))
    else:
        for k, v in s.SCENARIO.items():
            setattr(scenario, k, v)
        decision_ids = select(m.Decision.id).where(m.Decision.scenario_code == code)
        db.execute(delete(m.DecisionOption).where(m.DecisionOption.decision_id.in_(decision_ids)))
        db.execute(delete(m.Decision).where(m.Decision.scenario_code == code))
        for table in CONTENT_TABLES:
            db.execute(delete(table).where(table.scenario_code == code))
    db.flush()

    rates = {r[0]: r[5] for r in s.RESOURCES}
    for no, en, ru, days, milestone in s.ACTIVITIES:
        team = s.DEFAULT_ASSIGNMENTS.get(no, [])
        share = sum(p for _, p in team) / 100
        effort = days * WORK_HOURS_PER_DAY * share
        avg_rate = sum(rates[r] * p for r, p in team) / (share * 100) if share else 0
        db.add(m.Activity(
            scenario_code=code, no=no, name={"en": en, "ru": ru}, duration_days=days,
            effort_hours=effort, planned_cost=round(effort * avg_rate, 2), milestone=milestone,
        ))
        for r, p in team:
            db.add(m.DefaultAssignment(scenario_code=code, activity_no=no, resource_no=r, percent=p))

    for act, preds in s.DEPENDENCIES.items():
        for p in preds:
            db.add(m.Dependency(scenario_code=code, activity_no=act, predecessor_no=p))

    for no, en, ru, role_en, role_ru, rate in s.RESOURCES:
        db.add(m.Resource(
            scenario_code=code, no=no, name={"en": en, "ru": ru},
            role={"en": role_en, "ru": role_ru}, rate=rate,
        ))
        special = s.RESOURCE_WEEKS.get(no, {})
        for w in range(1, s.SCENARIO["weeks"] + 1):
            db.add(m.ResourceWeek(scenario_code=code, resource_no=no, week=w, state=special.get(w, "payroll")))

    for d in s.DECISIONS:
        dec = m.Decision(scenario_code=code, key=d["key"], prompt=d["prompt"], default_option=d["default_option"])
        dec.options = [m.DecisionOption(**o) for o in d["options"]]
        db.add(dec)

    for key, week, weekday, hour, dur, channel, sender, subject, body, effects, decision in s.EVENTS:
        db.add(m.ScenarioEvent(
            scenario_code=code, key=key, week=week, weekday=weekday, hour=hour, duration_h=dur,
            channel=channel, sender=sender, subject=subject, body=body, effects=effects,
            decision_key=decision,
        ))
    db.commit()
