"""Resource leveling: propose moving work off over-allocated or unavailable people.

Greedy pass in planned-start order. For each assignment that lands on a day
where its person is above 100% or not available, look for someone who is
free for the whole remaining window. Prefer the same role, then the lower rate.
The result is a proposal; the team accepts it or not.
"""

import math
from collections import defaultdict

from app.engine.clock import DAYS_PER_WEEK, work_days
from app.engine.rules import WORKING_STATES, Assignments, is_done, resource_state
from app.engine.scenario import ScenarioData


def level(scn: ScenarioData, state: dict, assignments: Assignments, minutes: float) -> tuple[Assignments, list[dict]]:
    today = math.floor(work_days(minutes))
    windows: dict[int, range] = {}
    for n, a in scn.activities.items():
        if is_done(state, n):
            continue
        start = max(int(a.es), today)
        end = max(int(a.ef), start + 1)
        windows[n] = range(start, end)

    def week(day: int) -> int:
        return day // DAYS_PER_WEEK + 1

    def unavailable(res: int, day: int) -> bool:
        return resource_state(scn, state, res, week(day)) not in WORKING_STATES

    load: dict[tuple[int, int], int] = defaultdict(int)
    for act, res, pct in assignments:
        for d in windows.get(act, ()):
            load[(res, d)] += pct

    result = [list(x) for x in assignments]
    changes: list[dict] = []
    order = sorted(windows, key=lambda n: (scn.activities[n].es, n))
    for act in order:
        days = windows[act]
        for entry in [e for e in result if e[0] == act]:
            _, res, pct = entry
            if not any(load[(res, d)] > 100 or unavailable(res, d) for d in days):
                continue
            on_task = {e[1] for e in result if e[0] == act}
            role = scn.resources[res].role.get("en")
            candidates = [
                r for r in scn.resources.values()
                if r.no not in on_task
                and all(load[(r.no, d)] + pct <= 100 and not unavailable(r.no, d) for d in days)
            ]
            if not candidates:
                continue
            best = min(candidates, key=lambda r: (r.role.get("en") != role, r.rate))
            for d in days:
                load[(res, d)] -= pct
                load[(best.no, d)] += pct
            entry[1] = best.no
            changes.append({"activity": act, "from": res, "to": best.no, "percent": pct})

    return [tuple(e) for e in result], changes
