"""Project time.

The clock counts *project minutes* since Monday 8:00 of week 1. A project
day runs 8:00-19:00 (11 hours on the clock); people work 9:00-17:00.
Weekends are skipped, so Friday 19:00 rolls straight into Monday 8:00.
"""

DAY_START = 8
DAY_END = 19
DAY_MIN = (DAY_END - DAY_START) * 60  # 660
DAYS_PER_WEEK = 5
WEEK_MIN = DAY_MIN * DAYS_PER_WEEK  # 3300

WORK_START = 9
WORK_END = 17
WORK_HOURS_PER_DAY = WORK_END - WORK_START  # 8

# Real seconds for one project week.
SPEEDS = {"test": 45, "fast": 180, "demo": 750}
DEMO_WEEKS = 1


def factor(speed: str) -> float:
    """Project minutes per real second."""
    return WEEK_MIN / SPEEDS[speed]


def to_minute(week: int, weekday: int, hour: float) -> float:
    return (week - 1) * WEEK_MIN + weekday * DAY_MIN + (hour - DAY_START) * 60


def describe(minutes: float, at_end: bool = False) -> dict:
    """Week/weekday/hour for display. At the very end show Friday 19:00, not Monday 8:00."""
    m = int(minutes)
    if at_end and m > 0 and m % DAY_MIN == 0:
        m -= 1
        week, rest = divmod(m, WEEK_MIN)
        return {"week": week + 1, "weekday": rest // DAY_MIN, "hour": DAY_END, "minute": 0}
    week, rest = divmod(m, WEEK_MIN)
    day, in_day = divmod(rest, DAY_MIN)
    return {"week": week + 1, "weekday": day, "hour": DAY_START + in_day // 60, "minute": in_day % 60}


def hour_of_day(hour_index: int) -> int:
    """Clock hour for the global hour slot `hour_index` (slot 0 = Monday 8:00-9:00, week 1)."""
    return DAY_START + hour_index % (DAY_END - DAY_START)


def is_work_hour(hour_index: int) -> bool:
    return WORK_START <= hour_of_day(hour_index) < WORK_END


def week_of_hour(hour_index: int) -> int:
    return hour_index * 60 // WEEK_MIN + 1


def work_days(minutes: float) -> float:
    """Working days elapsed (fractional), used for planned value and the Gantt 'today' line."""
    day, in_day = divmod(minutes, DAY_MIN)
    worked = min(max(in_day / 60 - (WORK_START - DAY_START), 0), WORK_HOURS_PER_DAY)
    return day + worked / WORK_HOURS_PER_DAY
