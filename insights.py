"""Which recorded features go with bad outcomes? Honest version: counts + Wilson 95% intervals.

    python3 insights.py [--data data/snapshots.jsonl] [--horizon 24]

"Bad" = measured within 1.5x the horizon AND (pair vanished, OR liquidity fell by half, OR price fell by half).
Only tokens that had liquidity at first sighting are judged. This is descriptive research on a small,
self-collected sample. It must NOT be used to auto-tune filters: look, then test on NEW data.
"""
import argparse
import math
import re
import statistics

from collector import load, LATE


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d, (c + r) / d


def labelled(rows, horizon=24):
    """Join entries with the outcome at `horizon`; returns list of (entry, bad)."""
    entries = {r["mint"]: r for r in rows if r["kind"] == "entry"}
    out = []
    for r in rows:
        if r["kind"] != "outcome" or r["horizon_h"] != horizon:
            continue
        e = entries.get(r["mint"])
        if not e or e["liq"] <= 0 or (r["ts"] - e["ts"]) / 3600 > LATE * horizon:
            continue
        bad = r["gone"] or r["liq"] <= e["liq"] * 0.5 or (e["price"] > 0 and r["price"] <= e["price"] * 0.5)
        out.append((e, bool(bad)))
    return out


def _fmt(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:4.0%}  (95% CI {lo:3.0%}-{hi:3.0%})" if n else "n=0"


def numeric_table(data, key, label, bins=4, min_bin=8):
    data = [(e, b) for e, b in data if e.get(key) is not None]
    vals = sorted(e[key] for e, _ in data)
    if len(vals) < 2 * min_bin:
        return [f"{label}: too few tokens"]
    k = max(2, min(bins, len(vals) // min_bin))
    cuts = [vals[int(len(vals) * i / k)] for i in range(1, k)]
    groups = [[] for _ in range(k)]
    for e, bad in data:
        v = e[key]
        groups[sum(v >= c for c in cuts)].append(bad)
    lines = [f"**{label}**", "", "| range | bad outcomes |", "|---|---|"]
    edges = [None] + cuts + [None]
    for i, g in enumerate(groups):
        lo, hi = edges[i], edges[i + 1]
        rng = f"< {hi:,.4g}" if lo is None else (f">= {lo:,.4g}" if hi is None else f"{lo:,.4g} to {hi:,.4g}")
        lines.append(f"| {rng} | {_fmt(sum(g), len(g))} |")
    return lines + [""]


def flag_table(data, min_n=5):
    names = {}
    for e, bad in data:
        for r in (e.get("flags") or []):
            names.setdefault(re.sub(r"^RugCheck danger: ", "", r), []).append(bad)
    lines = ["**Safety flags present at first sighting**", "", "| flag | bad outcomes |", "|---|---|"]
    shown = False
    for name, g in sorted(names.items(), key=lambda x: -len(x[1])):
        if len(g) >= min_n:
            lines.append(f"| {name} | {_fmt(sum(g), len(g))} |")
            shown = True
    if not shown:
        lines.append(f"| (no flag seen on {min_n}+ judged tokens yet) | |")
    return lines + [""]


def report(rows, horizon=24, since=0.0):
    rows = [r for r in rows if r.get("ts", 0) >= since or r["kind"] == "outcome"]
    data = labelled(rows, horizon)
    if not data:
        return f"# Insights\n\nNo judged tokens yet for the {horizon}h horizon.\n"
    base_k = sum(b for _, b in data)
    passed = [b for e, b in data if e["pass"]]
    rejected = [b for e, b in data if not e["pass"]]
    ratio = lambda e: (e.get("vol24", 0) or 0) / max(e["liq"], 1)
    data2 = [({**e, "vol_liq": ratio(e)}, b) for e, b in data]
    L = [f"# Insights ({horizon}h horizon)", "",
         f"Judged tokens (had liquidity at first sighting): **{len(data)}**. Base rate of a bad outcome: **{_fmt(base_k, len(data))}**.", "",
         "**Risk agent verdict**", "", "| verdict | bad outcomes |", "|---|---|",
         f"| PASSED | {_fmt(sum(passed), len(passed))} |", f"| REJECTED | {_fmt(sum(rejected), len(rejected))} |", ""]
    for key, label in (("liq", "Liquidity at first sighting (USD)"), ("age_min", "Token age at first sighting (minutes)"),
                       ("top10", "Top-10 holder share (%, pool excluded)"), ("vol_liq", "24h volume / liquidity"),
                       ("total_holders", "Total holders"), ("creator_pct", "Creator holding (%)"),
                       ("buy_ratio_h1", "Buy share of last-hour trades"), ("chg_h1", "Price change in the hour before (%)")):
        if any(e.get(key) is not None and key in e for e, _ in data2):
            L += numeric_table(data2, key, label)
    L += flag_table(data2)
    L += ["Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, "
          "which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.", "",
          "Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/snapshots.jsonl")
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--since", default="", help="only tokens first seen on/after this UTC date (YYYY-MM-DD): use it to test a hypothesis on NEW data")
    a = ap.parse_args()
    import datetime
    since = datetime.datetime.fromisoformat(a.since).replace(tzinfo=datetime.timezone.utc).timestamp() if a.since else 0.0
    print(report(load(a.data), a.horizon, since))
