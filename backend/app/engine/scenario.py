"""In-memory view of a scenario, loaded once from the database and cached."""

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models as m
from app.engine.clock import DAYS_PER_WEEK, WORK_HOURS_PER_DAY, to_minute
from app.engine.schedule import cpm


@dataclass
class ActivityDef:
    no: int
    name: dict
    duration: int
    effort: float
    planned_cost: float
    milestone: bool
    preds: list[int]
    es: float = 0
    ef: float = 0
    ls: float = 0
    lf: float = 0
    slack: float = 0
    critical: bool = False
    level: int = 0

    @property
    def planned_rate(self) -> float:
        return self.planned_cost / self.effort if self.effort else 0


@dataclass
class ResourceDef:
    no: int
    name: dict
    role: dict
    rate: float
    weeks: dict[int, str]


@dataclass
class ScenarioData:
    code: str
    title: dict
    description: dict
    weeks: int
    currency: str
    pm_rate: float
    material_budget: float
    other_budget: float
    activities: dict[int, ActivityDef] = field(default_factory=dict)
    resources: dict[int, ResourceDef] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)  # sorted by minute
    decisions: dict[str, dict] = field(default_factory=dict)
    default_assignments: list[tuple[int, int, int]] = field(default_factory=list)

    @property
    def total_days(self) -> int:
        return self.weeks * DAYS_PER_WEEK

    @property
    def labour_budget(self) -> float:
        return sum(a.planned_cost for a in self.activities.values())

    @property
    def pm_budget(self) -> float:
        return self.pm_rate * WORK_HOURS_PER_DAY * self.total_days

    @property
    def total_budget(self) -> float:
        return self.labour_budget + self.pm_budget + self.material_budget + self.other_budget


_cache: dict[str, ScenarioData] = {}


def get_scenario(db: Session, code: str) -> ScenarioData | None:
    if code in _cache:
        return _cache[code]
    sc = db.get(m.Scenario, code)
    if sc is None:
        return None
    data = ScenarioData(
        code=sc.code, title=sc.title, description=sc.description, weeks=sc.weeks,
        currency=sc.currency, pm_rate=sc.pm_rate, material_budget=sc.material_budget,
        other_budget=sc.other_budget,
    )
    preds: dict[int, list[int]] = {}
    for d in db.scalars(select(m.Dependency).where(m.Dependency.scenario_code == code)):
        preds.setdefault(d.activity_no, []).append(d.predecessor_no)
    for a in db.scalars(select(m.Activity).where(m.Activity.scenario_code == code)):
        data.activities[a.no] = ActivityDef(
            no=a.no, name=a.name, duration=a.duration_days, effort=a.effort_hours,
            planned_cost=a.planned_cost, milestone=a.milestone, preds=sorted(preds.get(a.no, [])),
        )
    sched = cpm({n: a.duration for n, a in data.activities.items()}, preds)
    for n, info in sched.items():
        for k, v in info.items():
            setattr(data.activities[n], k, v)
    data.activities = dict(sorted(data.activities.items()))

    weeks: dict[int, dict[int, str]] = {}
    for rw in db.scalars(select(m.ResourceWeek).where(m.ResourceWeek.scenario_code == code)):
        weeks.setdefault(rw.resource_no, {})[rw.week] = rw.state
    for r in db.scalars(select(m.Resource).where(m.Resource.scenario_code == code).order_by(m.Resource.no)):
        data.resources[r.no] = ResourceDef(no=r.no, name=r.name, role=r.role, rate=r.rate, weeks=weeks.get(r.no, {}))

    for e in db.scalars(select(m.ScenarioEvent).where(m.ScenarioEvent.scenario_code == code)):
        data.events.append({
            "key": e.key, "week": e.week, "weekday": e.weekday, "hour": e.hour,
            "duration": e.duration_h, "channel": e.channel, "sender": e.sender,
            "subject": e.subject, "body": e.body, "effects": e.effects or {},
            "decision": e.decision_key, "minute": to_minute(e.week, e.weekday, e.hour),
        })
    data.events.sort(key=lambda e: (e["minute"], e["key"]))

    for d in db.scalars(
        select(m.Decision).where(m.Decision.scenario_code == code).options(selectinload(m.Decision.options))
    ):
        data.decisions[d.key] = {
            "key": d.key, "prompt": d.prompt, "default": d.default_option,
            "deadline_hours": d.deadline_hours,
            "options": {
                o.key: {"key": o.key, "label": o.label, "feedback": o.feedback,
                        "effects": o.effects or {}, "learning_point": o.learning_point}
                for o in d.options
            },
        }

    for da in db.scalars(select(m.DefaultAssignment).where(m.DefaultAssignment.scenario_code == code)):
        data.default_assignments.append((da.activity_no, da.resource_no, da.percent))

    _cache[code] = data
    return data


def clear_cache() -> None:
    _cache.clear()
