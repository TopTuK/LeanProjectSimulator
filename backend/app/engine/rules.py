"""Simulation rules. Pure functions over (scenario, state, assignments).

Formulas (all original to this project):

* Work: each work hour, every person assigned to a *ready* activity (all
  predecessors finished) contributes `share × pace` hours of progress, where
  `share` is their percent, scaled down if their total load on ready
  activities exceeds 100%. They are paid `share × rate`.
* pace = (0.7 + 0.3 × motivation/100) × schedule-difficulty pace.
* Over-allocation: every over-allocated person costs 0.4 motivation and
  0.15 quality per work hour (scaled by difficulty).
* Schedule index = SPI = EV / PV.
* Cost index = budget at completion / estimate at completion.
* Quality and motivation start at 100 and move with decisions and overload.
* Decision effects that hurt are multiplied by the matching difficulty.
"""

import math
from collections import defaultdict

from app.engine.clock import work_days
from app.engine.scenario import ScenarioData

EPS = 1e-6
DIFFICULTY = {"easy": 0.7, "standard": 1.0, "hard": 1.3}
PACE = {"easy": 1.05, "standard": 1.0, "hard": 0.92}
WORKING_STATES = {"payroll", "available"}
INDEX_MIN, INDEX_MAX = 0.0, 120.0

Assignments = list[tuple[int, int, int]]  # (activity_no, resource_no, percent)


def initial_state(scn: ScenarioData) -> dict:
    return {
        "quality": 100.0,
        "motivation": 100.0,
        "other_cost": 0.0,
        "pm_cost": 0.0,
        "hours": 0.0,
        "progress": {str(n): {"done": 0.0, "cost": 0.0, "start": None, "end": None} for n in scn.activities},
        "effort": {str(n): a.effort for n, a in scn.activities.items()},
        "overrides": {},
        "delivered": [],
    }


def difficulty(cfg: dict, key: str) -> float:
    return DIFFICULTY.get(cfg.get(f"difficulty_{key}", "standard"), 1.0)


def resource_state(scn: ScenarioData, state: dict, res_no: int, week: int) -> str:
    override = state["overrides"].get(str(res_no), {}).get(str(week))
    return override or scn.resources[res_no].weeks.get(week, "payroll")


def is_done(state: dict, no: int) -> bool:
    return state["progress"][str(no)]["done"] >= state["effort"][str(no)] - EPS


def is_ready(scn: ScenarioData, state: dict, no: int) -> bool:
    return not is_done(state, no) and all(is_done(state, p) for p in scn.activities[no].preds)


def pace(state: dict, cfg: dict) -> float:
    mot = min(state["motivation"], 110.0)
    return (0.7 + 0.3 * mot / 100) * PACE.get(cfg.get("difficulty_schedule", "standard"), 1.0)


def load_by_resource(assignments: Assignments, active: set[int]) -> dict[int, float]:
    load: dict[int, float] = defaultdict(float)
    for act, res, pct in assignments:
        if act in active:
            load[res] += pct / 100
    return load


def work_hour(scn: ScenarioData, state: dict, assignments: Assignments, week: int, minute: float, cfg: dict) -> None:
    """Apply one work hour ending at `minute` (mutates state)."""
    active = {n for n in scn.activities if is_ready(scn, state, n)}
    load = load_by_resource(assignments, active)
    p_rate = pace(state, cfg)
    overloaded = 0
    for res, total in load.items():
        if total > 1 + EPS and resource_state(scn, state, res, week) in WORKING_STATES:
            overloaded += 1

    for act, res, pct in assignments:
        if act not in active or pct <= 0:
            continue
        if resource_state(scn, state, res, week) not in WORKING_STATES:
            continue
        share = pct / 100 / max(1.0, load[res])
        prog = state["progress"][str(act)]
        if prog["start"] is None:
            prog["start"] = minute - 60
        prog["done"] += share * p_rate
        prog["cost"] += share * scn.resources[res].rate
        state["hours"] += share

    for act in active:
        prog = state["progress"][str(act)]
        effort = state["effort"][str(act)]
        if prog["done"] >= effort - EPS:
            prog["done"] = effort
            prog["end"] = minute

    if overloaded:
        state["motivation"] = _clamp(state["motivation"] - 0.4 * overloaded * difficulty(cfg, "motivation"))
        state["quality"] = _clamp(state["quality"] - 0.15 * overloaded * difficulty(cfg, "quality"))
    state["pm_cost"] += scn.pm_rate


def apply_effects(scn: ScenarioData, state: dict, effects: dict, cfg: dict, minute: float) -> None:
    cost = effects.get("cost", 0)
    if cost:
        state["other_cost"] += cost * (difficulty(cfg, "cost") if cost > 0 else 1)
    for act, hours in (effects.get("effort") or {}).items():
        if hours > 0:
            hours *= difficulty(cfg, "schedule")
        prog = state["progress"][str(act)]
        state["effort"][str(act)] = max(prog["done"], state["effort"][str(act)] + hours, 0)
        if prog["done"] >= state["effort"][str(act)] - EPS and prog["start"] is not None and prog["end"] is None:
            prog["end"] = minute
    for key in ("quality", "motivation"):
        v = effects.get(key, 0)
        if v:
            state[key] = _clamp(state[key] + v * (difficulty(cfg, key) if v < 0 else 1))
    res = effects.get("resource")
    if res:
        state["overrides"].setdefault(str(res["no"]), {})[str(res["week"])] = res["state"]


def money(scn: ScenarioData, state: dict, assignments: Assignments, minutes: float) -> dict:
    # work is booked at the end of each hour, so plan against completed hours too
    days = work_days(math.floor(minutes / 60 + 1e-9) * 60)
    by_act: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for act, res, pct in assignments:
        if pct > 0:
            by_act[act].append((res, pct))

    pv = ev = labour = labour_eac = 0.0
    per_activity: dict[int, dict] = {}
    for n, a in scn.activities.items():
        prog = state["progress"][str(n)]
        effort = state["effort"][str(n)]
        frac = min(prog["done"] / effort, 1.0) if effort else 1.0
        if a.duration:
            pv += a.planned_cost * _clamp((days - a.es) / a.duration, 0, 1)
        elif days >= a.es:
            pv += a.planned_cost
        a_ev = a.planned_cost * frac
        ev += a_ev
        labour += prog["cost"]
        team = by_act.get(n)
        rate = sum(scn.resources[r].rate * p for r, p in team) / sum(p for _, p in team) if team else a.planned_rate
        eac = prog["cost"] + max(effort - prog["done"], 0) * rate
        labour_eac += eac
        per_activity[n] = {"progress": frac, "actual": prog["cost"], "eac": eac, "ev": a_ev}

    elapsed = min(days / scn.total_days, 1.0)
    other_eac = max(scn.other_budget, state["other_cost"] + scn.other_budget * (1 - elapsed))
    pm_eac = scn.pm_budget
    eac = labour_eac + pm_eac + scn.material_budget + other_eac
    bac = scn.total_budget
    ac = labour + state["other_cost"]
    return {
        "pv": pv, "ev": ev, "ac": ac, "labour_actual": labour, "labour_budget": scn.labour_budget,
        "labour_eac": labour_eac, "pm_actual": state["pm_cost"], "pm_budget": scn.pm_budget,
        "material_actual": 0.0, "material_budget": scn.material_budget,
        "other_actual": state["other_cost"], "other_budget": scn.other_budget, "other_eac": other_eac,
        "bac": bac, "eac": eac, "hours": state["hours"], "days": days,
        "cpi": ev / labour if labour > EPS else 1.0,
        "spi": ev / pv if pv > EPS else 1.0,
        "per_activity": per_activity,
    }


def indexes(state: dict, mon: dict) -> dict:
    return {
        "cost": round(100 * mon["bac"] / mon["eac"], 1) if mon["eac"] > EPS else 100.0,
        "schedule": round(100 * mon["spi"], 1),
        "quality": round(state["quality"], 1),
        "motivation": round(state["motivation"], 1),
    }


def _clamp(v: float, lo: float = INDEX_MIN, hi: float = INDEX_MAX) -> float:
    return max(lo, min(hi, v))

