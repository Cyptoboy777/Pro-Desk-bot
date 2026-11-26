"""Descriptive statistics over append-only forward-test observations; no edge claims from weak evidence."""
import argparse
import math
import re

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
    entries = {r["mint"]: r for r in rows if r.get("kind") == "entry"}
    out = []
    for r in rows:
        if r.get("kind") != "outcome" or r.get("horizon_h") != horizon:
            continue
        e = entries.get(r["mint"])
        if not e or e.get("liq", 0) <= 0 or (r["ts"] - e["ts"]) / 3600 > LATE * horizon:
            continue
        bad = r["gone"] or r["liq"] <= e["liq"] * 0.5 or (e.get("price", 0) > 0 and r["price"] <= e["price"] * 0.5)
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
        groups[sum(e[key] >= c for c in cuts)].append(bad)
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
    rows = [r for r in rows if r.get("ts", 0) >= since or r.get("kind") == "outcome"]
    data = labelled(rows, horizon)
    if not data:
        return f"# Insights\n\nNo judged tokens yet for the {horizon}h horizon.\n"
    base_k = sum(b for _, b in data)
    passed = [b for e, b in data if e["pass"]]
    rejected = [b for e, b in data if not e["pass"]]
    data2 = [({**e, "vol_liq": (e.get("vol24") or 0) / max(e["liq"], 1)}, b) for e, b in data]
    lines = [f"# Insights ({horizon}h horizon)", "", f"Judged tokens (had liquidity at first sighting): **{len(data)}**. Base rate of a bad outcome: **{_fmt(base_k, len(data))}**.", "",
             "**Risk agent verdict**", "", "| verdict | bad outcomes |", "|---|---|",
             f"| PASSED | {_fmt(sum(passed), len(passed))} |", f"| REJECTED | {_fmt(sum(rejected), len(rejected))} |", ""]
    for key, label in (("liq", "Liquidity at first sighting (USD)"), ("age_min", "Token age at first sighting (minutes)"),
                       ("top10", "Top-10 holder share (%, pool excluded)"), ("vol_liq", "24h volume / liquidity"),
                       ("total_holders", "Total holders"), ("creator_pct", "Creator holding (%)"),
                       ("buy_ratio_h1", "Buy share of last-hour trades"), ("chg_h1", "Price change in the hour before (%)")):
        if any(e.get(key) is not None for e, _ in data2):
            lines += numeric_table(data2, key, label)
    lines += flag_table(data2)
    lines += ["Caution: these observational signals are confounded by selection and market regime; no individual row is causal.", "",
              "Intervals that overlap are not different. Low samples are preliminary hypotheses, not answers.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/snapshots.jsonl")
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--since", default="")
    a = ap.parse_args()
    import datetime
    since = datetime.datetime.fromisoformat(a.since).replace(tzinfo=datetime.timezone.utc).timestamp() if a.since else 0.0
    print(report(load(a.data), a.horizon, since))
