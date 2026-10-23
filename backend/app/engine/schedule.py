"""Critical path method over the baseline plan (durations in working days)."""


def cpm(durations: dict[int, int], preds: dict[int, list[int]]) -> dict[int, dict]:
    order = _topo(durations, preds)
    es: dict[int, float] = {}
    ef: dict[int, float] = {}
    for a in order:
        es[a] = max((ef[p] for p in preds.get(a, [])), default=0)
        ef[a] = es[a] + durations[a]
    end = max(ef.values(), default=0)

    succs: dict[int, list[int]] = {a: [] for a in durations}
    for a, ps in preds.items():
        for p in ps:
            succs[p].append(a)
    ls: dict[int, float] = {}
    lf: dict[int, float] = {}
    for a in reversed(order):
        lf[a] = min((ls[s] for s in succs[a]), default=end)
        ls[a] = lf[a] - durations[a]

    level: dict[int, int] = {}
    for a in order:
        level[a] = max((level[p] + 1 for p in preds.get(a, [])), default=0)

    return {
        a: {
            "es": es[a], "ef": ef[a], "ls": ls[a], "lf": lf[a],
            "slack": ls[a] - es[a], "critical": abs(ls[a] - es[a]) < 1e-9, "level": level[a],
        }
        for a in durations
    }


def _topo(durations: dict[int, int], preds: dict[int, list[int]]) -> list[int]:
    seen: set[int] = set()
    out: list[int] = []

    def visit(a: int, stack: tuple[int, ...] = ()) -> None:
        if a in seen:
            return
        if a in stack:
            raise ValueError(f"dependency cycle at activity {a}")
        for p in preds.get(a, []):
            visit(p, stack + (a,))
        seen.add(a)
        out.append(a)

    for a in sorted(durations):
        visit(a)
    return out
