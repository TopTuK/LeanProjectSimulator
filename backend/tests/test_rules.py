from app.engine import rules
from app.engine.clock import to_minute
from app.engine.leveling import level

CFG = {"difficulty_schedule": "standard", "difficulty_cost": "standard",
       "difficulty_quality": "standard", "difficulty_motivation": "standard"}


def test_plan_matches_schedule(scn):
    assert max(a.ef for a in scn.activities.values()) <= scn.total_days
    assert scn.activities[1].critical and scn.activities[15].critical
    assert not scn.activities[6].critical


def test_on_plan_work_keeps_indexes_at_100(scn):
    state = rules.initial_state(scn)
    asg = scn.default_assignments
    # Monday and Tuesday: activity 1 runs exactly to plan
    for day in range(2):
        for h in range(9, 17):
            rules.work_hour(scn, state, asg, 1, to_minute(1, day, h + 1), CFG)
    assert rules.is_done(state, 1)
    mon = rules.money(scn, state, asg, to_minute(1, 1, 18))
    idx = rules.indexes(state, mon)
    assert idx["schedule"] == 100.0
    assert idx["cost"] == 100.0
    assert abs(mon["cpi"] - 1) < 1e-9


def test_waiting_activity_does_not_progress(scn):
    state = rules.initial_state(scn)
    rules.work_hour(scn, state, scn.default_assignments, 1, to_minute(1, 0, 10), CFG)
    assert state["progress"]["2"]["done"] == 0
    assert state["progress"]["1"]["done"] == 2


def test_over_allocation_splits_time_and_hurts_motivation(scn):
    state = rules.initial_state(scn)
    state["progress"]["1"]["done"] = state["effort"]["1"]  # 1 done -> 2, 3, 5 ready
    rules.work_hour(scn, state, [(2, 2, 100), (3, 2, 100)], 1, to_minute(1, 2, 10), CFG)
    assert state["progress"]["2"]["done"] == 0.5
    assert state["progress"]["3"]["done"] == 0.5
    assert state["motivation"] < 100 and state["quality"] < 100


def test_unavailable_person_does_not_work(scn):
    state = rules.initial_state(scn)
    rules.apply_effects(scn, state, {"resource": {"no": 1, "week": 1, "state": "sick"}}, CFG, 0)
    rules.work_hour(scn, state, [(1, 1, 100)], 1, to_minute(1, 0, 10), CFG)
    assert state["progress"]["1"]["done"] == 0


def test_effects_and_difficulty(scn):
    state = rules.initial_state(scn)
    rules.apply_effects(scn, state, {"cost": 1000, "motivation": -10, "effort": {"7": 10}}, {**CFG, "difficulty_cost": "hard", "difficulty_motivation": "easy"}, 0)
    assert state["other_cost"] == 1300
    assert state["motivation"] == 93
    assert state["effort"]["7"] == scn.activities[7].effort + 10
    mon = rules.money(scn, state, scn.default_assignments, 0)
    assert rules.indexes(state, mon)["cost"] < 100


def test_leveling_moves_work_off_sick_person(scn):
    state = rules.initial_state(scn)
    state["progress"]["1"]["done"] = state["effort"]["1"]
    rules.apply_effects(scn, state, {"resource": {"no": 7, "week": 1, "state": "sick"}}, CFG, 0)
    proposal, changes = level(scn, state, scn.default_assignments, to_minute(1, 2, 9))
    assert any(c["activity"] == 5 and c["from"] == 7 for c in changes)
    assert (5, 7, 100) not in proposal
