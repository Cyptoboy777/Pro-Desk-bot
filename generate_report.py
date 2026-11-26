"""Generate a reproducible Markdown report from available forward-test JSONL data."""
import argparse
import os
from api_export import build
from collector import load


def generate(rows):
    result = build(rows)
    s = result["summary"]
    lines = ["# Solana Token Risk Telemetry — Empirical Report", "",
             "Generated from the current append-only snapshot data. Descriptive research; not financial advice or a trading recommendation.", "",
             f"- Recorded entries: **{s['tokens_recorded']}**", f"- Judged at 24h: **{s['judged_24h']}**",
             f"- v1 conclusion: **{s['edge_status']}** — {s['edge_note']}",
             f"- v2 shadow conclusion: **{s['edge_status_v2_shadow']}** — {s['edge_note_v2_shadow']}", "",
             "## Out-of-time comparison (24h)", "", "| version | group | bad / n | bad rate | 95% Wilson CI |", "|---|---|---:|---:|---:|"]
    for version, obj in (("v1", s["pass_vs_reject_24h"]["v1"]), ("v2 shadow", s["pass_vs_reject_24h"]["v2_shadow"])):
        for group in ("pass", "reject"):
            x = obj[group]
            ci = "n/a" if x["bad_ci95"] is None else f"{x['bad_ci95'][0]:.1%}–{x['bad_ci95'][1]:.1%}"
            rate = "n/a" if x["bad_rate"] is None else f"{x['bad_rate']:.1%}"
            lines.append(f"| {version} | {group} | {x['bad']}/{x['n']} | {rate} | {ci} |")
    lines += ["", "## Signal sample sizes", "", "| feature | flagged n | status | lift over base rate | p-value (Fisher exact) |", "|---|---:|---|---:|---:|"]
    for x in result["features"]["features"]:
        lift = "n/a" if x["lift_over_baseline"] is None else f"{x['lift_over_baseline']:.3g}x"
        p = "n/a" if x["p_value"] is None else f"{x['p_value']:.4g}"
        lines.append(f"| {x['label']} | {x['n_flagged']}/{x['n_known']} | {x['sample_status']} | {lift} | {p} |")
    lines += ["", "## Interpretation", "", "`EDGE_DETECTED` is reserved for a pre-specified, sufficiently powered out-of-time comparison with non-overlapping Wilson intervals. Otherwise the conclusion is `NO_EDGE` or `INSUFFICIENT_DATA`. No trading edge is asserted here. Rolling 24h volume and holder-count deltas are proxies; the data does not identify unique wallets, early-wallet distributions, or causal mechanisms.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/snapshots.jsonl")
    p.add_argument("--out", default="REPORT.md")
    a = p.parse_args()
    text = generate(load(a.data))
    with open(a.out, "w") as f:
        f.write(text)
    print("wrote", a.out)
