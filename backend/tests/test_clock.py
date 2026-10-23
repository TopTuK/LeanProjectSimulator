from app.engine.clock import WEEK_MIN, describe, factor, is_work_hour, to_minute, work_days
from app.engine.schedule import cpm


def test_describe_start_and_rollover():
    assert describe(0) == {"week": 1, "weekday": 0, "hour": 8, "minute": 0}
    assert describe(660) == {"week": 1, "weekday": 1, "hour": 8, "minute": 0}
    assert describe(WEEK_MIN) == {"week": 2, "weekday": 0, "hour": 8, "minute": 0}
    assert describe(to_minute(1, 2, 13) + 30) == {"week": 1, "weekday": 2, "hour": 13, "minute": 30}


def test_describe_end_shows_friday_evening():
    assert describe(WEEK_MIN, at_end=True) == {"week": 1, "weekday": 4, "hour": 19, "minute": 0}


def test_work_hours_and_days():
    assert not is_work_hour(0)  # 8-9
    assert is_work_hour(1)  # 9-10
    assert not is_work_hour(9)  # 17-18
    assert is_work_hour(12)  # Tue 9-10
    assert work_days(0) == 0
    assert work_days(to_minute(1, 0, 13)) == 0.5
    assert work_days(to_minute(1, 0, 18)) == 1.0
    assert work_days(WEEK_MIN) == 5


def test_demo_speed_is_12_5_minutes_per_week():
    assert abs(WEEK_MIN / factor("demo") - 750) < 1e-9


def test_cpm_critical_path():
    sched = cpm({1: 2, 2: 3, 3: 1, 4: 2}, {2: [1], 3: [1], 4: [2, 3]})
    assert sched[4]["ef"] == 7
    assert sched[3]["slack"] == 2
    assert [a for a in sched if sched[a]["critical"]] == [1, 2, 4]
