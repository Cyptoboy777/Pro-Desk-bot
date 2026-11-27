"""Generate REPORT.md from the published API JSON (docs/api/v1) or straight from snapshot rows.

    python generate_report.py --api docs/api/v1            # from the published JSON
    python generate_report.py --data data/snapshots.jsonl  # from raw rows (e.g. the live-data branch)

The out-of-time table uses ONLY tokens first seen on/after the cutoff (default 2026-11-24), never the full dataset.
"""
import argparse
import json
import os

from api_export import build, CUTOFF


def _ci(x):
    return "n/a" if not x.get("bad_ci95") else f"{x['bad_ci95'][0]:.1%}–{x['bad_ci95'][1]:.1%}"


def _rate(x):
    return "n/a" if x.get("bad_rate") is None else f"{x['bad_rate']:.1%}"


def _group_rows(label, obj):
    return [f"| {label} | {g} | {obj[g]['bad']}/{obj[g]['n']} | {_rate(obj[g])} | {_ci(obj[g])} |" for g in ("pass", "reject")]


def render(summary, features):
    s, oot = summary, summary.get("out_of_time") or {}
    head = "| version | group | bad / n | bad rate | 95% Wilson CI |\n|---|---|---:|---:|---:|"
    L = ["# Solana Token Risk Telemetry — Empirical Report", "",
         "Generated from the append-only forward-test data. Descriptive research; not financial advice or a trading recommendation.", "",
         f"- Recorded tokens: **{s.get('tokens_recorded')}**", f"- Judged at 24h: **{s.get('judged_24h')}**",
         f"- v1 (live rules), full sample: **{s.get('edge_status')}** — {s.get('edge_note')}",
         f"- v2 (shadow rubric), full sample: **{s.get('edge_status_v2_shadow')}** — {s.get('edge_note_v2_shadow')}", "",
         "## Full-sample comparison (24h) — in-sample for v2", "", head]
    pv = s.get("pass_vs_reject_24h", {})
    for name, key in (("v1", "v1"), ("v2 shadow", "v2_shadow")):
        if key in pv:
            L += _group_rows(name, pv[key])
    L += ["", f"## Out-of-time comparison (24h): tokens first seen on/after {oot.get('cutoff', CUTOFF)} only", ""]
    if oot:
        L += [f"Judged tokens in the held-out window: **{oot['judged_24h']}**. v2 defaults were designed and locked on tokens first seen before this date.", "", head]
        for name, key in (("v1", "v1"), ("v2 shadow", "v2_shadow")):
            L += _group_rows(name, oot[key])
        L += ["", f"- v1 held-out status: **{oot['v1']['edge_status']}**", f"- v2 shadow held-out status: **{oot['v2_shadow']['edge_status']}**"]
    else:
        L.append("Not available in this API snapshot.")
    L += ["", "## Time-series coverage", "", "| window | expected | observed | missing | status | median LP delta % | median holder growth/h | median volume ratio |", "|---|---:|---:|---:|---|---:|---:|---:|"]
    f = lambda v: "n/a" if v is None else f"{v:.3g}"
    for label, w in ((s.get("time_series_coverage") or {}).get("windows") or {}).items():
        L.append(f"| {label} | {w['expected']} | {w['observed']} | {w['missing']} | {w['missing_observation']} | {f(w['median_lp_delta_pct'])} | {f(w['median_holder_growth_per_h'])} | {f(w['median_volume_decay_ratio'])} |")
    L += ["", "## Signals (24h)", "", "| signal | flagged / known | sample (smaller group) | status | bad if flagged | lift over base rate | p-value (Fisher exact, two-sided) |", "|---|---:|---:|---|---:|---:|---:|"]
    for x in (features or {}).get("features", []):
        g = lambda k: x.get(k)
        L.append(f"| {x['label']} | {x['n_flagged']}/{x['n_known']} | {g('sample_n') if g('sample_n') is not None else 'n/a'} | {g('sample_status') or 'n/a'} | "
                 f"{'n/a' if x.get('bad_rate_flagged') is None else format(x['bad_rate_flagged'], '.0%')} | {f(g('lift_over_baseline'))}x | {f(g('p_value'))} |")
    L += ["", "## Interpretation", "",
          "`STATISTICAL_EDGE_DETECTED` is reserved for a comparison with 30+ judged tokens per group and non-overlapping Wilson intervals; otherwise the status is `NO_EDGE` or `INSUFFICIENT_DATA`. "
          "Signal p-values are unadjusted for multiple comparisons, so with a dozen signals one will look significant by chance; only out-of-time confirmation counts. "
          "Holder-count and rolling-volume deltas are proxies: the data does not identify unique wallets, early-wallet distributions or causal mechanisms. No trading edge is asserted.", ""]
    return "\n".join(L)


def generate(rows, state_path=None):
    b = build(rows, state_path)
    return render(b["summary"], b["features"])


def generate_from_api(api_dir):
    load = lambda n: json.load(open(os.path.join(api_dir, n + ".json")))
    return render(load("summary"), load("features"))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--api", default="")
    p.add_argument("--data", default="")
    p.add_argument("--state", default="")
    p.add_argument("--out", default="REPORT.md")
    a = p.parse_args()
    if a.data:
        from collector import load
        text = generate(load(a.data), a.state or None)
    else:
        text = generate_from_api(a.api or "docs/api/v1")
    with open(a.out, "w") as f:
        f.write(text)
    print("wrote", a.out)
