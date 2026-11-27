"""Rewrite the results block of README.md from docs/api/v1/summary.json so the numbers never go stale.

    python tools/update_readme_counts.py [--summary docs/api/v1/summary.json] [--readme README.md]
Only the text between the COUNTS markers is replaced.
"""
import argparse
import datetime
import json
import re

START, END = "<!-- COUNTS:START -->", "<!-- COUNTS:END -->"


def cell(g):
    if not g["n"]:
        return "n=0"
    lo, hi = g["bad_ci95"]
    return f"{g['bad']}/{g['n']} = {g['bad_rate']:.0%} (CI {lo:.0%}-{hi:.0%})"


def block(s):
    pv = s["pass_vs_reject_24h"]
    day = datetime.datetime.fromtimestamp(s["generated_at"], datetime.timezone.utc).strftime("%Y-%m-%d")
    oot = s.get("out_of_time") or {}
    rows = [START, "| engine | passed: bad outcomes | rejected: bad outcomes | edge status |", "|---|---|---|---|",
            f"| v1 rules (live) | {cell(pv['v1']['pass'])} | {cell(pv['v1']['reject'])} | `{s['edge_status']}` |",
            f"| v2 rubric (shadow) | {cell(pv['v2_shadow']['pass'])} | {cell(pv['v2_shadow']['reject'])} | `{s['edge_status_v2_shadow']}` |", "",
            f"(**{s['tokens_recorded']} recorded tokens, {s['judged_24h']} judged at 24h**, as of {day} UTC, auto-updated from `summary.json`. "
            f"Held-out window (first seen on/after {oot.get('cutoff', '2026-11-24')}): {oot.get('judged_24h', 'n/a')} judged.)", END]
    return "\n".join(rows)


def update(readme_text, summary):
    if START not in readme_text or END not in readme_text:
        raise ValueError("COUNTS markers missing from README")
    return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block(summary), readme_text, flags=re.S)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--summary", default="docs/api/v1/summary.json"); ap.add_argument("--readme", default="README.md")
    a = ap.parse_args()
    new = update(open(a.readme).read(), json.load(open(a.summary)))
    open(a.readme, "w").write(new); print("README counts updated")
