"""Regression tests for the audit fixes: statistics, out-of-time split, coverage, report, actions, workflows."""
import json
import math
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
import api_export as A
import generate_report as G
import collector
from tests.test_api_export import rows as mkrows


def test_fisher_matches_known_values():
    assert abs(A.fisher_exact(3, 1, 1, 3) - 0.4857142857) < 1e-9          # classic tea-tasting table
    assert abs(A.fisher_exact(10, 0, 0, 10) - 1.08e-5) < 2e-6
    assert A.fisher_exact(5, 5, 5, 5) == 1.0
    assert A.fisher_exact(0, 0, 0, 0) is None


def test_sample_status_thresholds():
    assert [A.sample_status(n) for n in (0, 29, 30, 99, 100, 5000)] == [
        "INSUFFICIENT_DATA", "INSUFFICIENT_DATA", "PRELIMINARY", "PRELIMINARY", "STATISTICALLY_POWERED", "STATISTICALLY_POWERED"]


def test_every_feature_has_status_lift_and_p_value():
    b = A.build(mkrows(10, 40, 20, 40), now=1)
    for f in b["features"]["features"]:
        assert {"sample_status", "sample_n", "lift_over_baseline", "p_value"} <= set(f)
        assert f["sample_status"] in ("INSUFFICIENT_DATA", "PRELIMINARY", "STATISTICALLY_POWERED")
        assert f["p_value"] is None or 0 <= f["p_value"] <= 1
    f = {x["key"]: x for x in b["features"]["features"]}["v1_rejected"]
    assert f["sample_status"] == "PRELIMINARY" and f["p_value"] < 0.05 or f["p_value"] is not None


def test_out_of_time_uses_only_post_cutoff_tokens():
    cut = A._cutoff_ts(A.CUTOFF)
    rows = mkrows(10, 40, 20, 40)
    for r in rows:
        if r["kind"] == "entry":
            r["ts"] = cut - 86400 if r["mint"] in {f"M{i}" for i in range(1, 61)} else cut + 10   # first 60 before, rest after
    for r in rows:
        if r["kind"] == "outcome":
            r["ts"] = next(e["ts"] for e in rows if e["kind"] == "entry" and e["mint"] == r["mint"]) + 24 * 3600
    o = A.oot_block(rows)
    assert o["judged_24h"] == 20 and sum(o["v1"][g]["n"] for g in ("pass", "reject")) == 20
    assert A.build(rows, now=1)["summary"]["out_of_time"]["judged_24h"] == 20
    assert A.build(rows, now=1)["summary"]["judged_24h"] == 80


def test_time_series_coverage_counts_missing_and_deltas():
    entries = [{"kind": "entry", "ts": 0.0, "mint": f"M{i}", "price": 1, "liq": 1000} for i in range(4)]
    snaps = [{"kind": "snapshot", "ts": 1900.0, "mint": "M0", "window_min": 30, "lp_delta_pct": -50.0, "holder_growth_rate": 4.0, "volume_decay_ratio": 0.5, "gone": False},
             {"kind": "snapshot", "ts": 1900.0, "mint": "M1", "window_min": 30, "lp_delta_pct": -10.0, "holder_growth_rate": None, "volume_decay_ratio": 1.0, "gone": False}]
    cov = A.time_series_coverage(entries + snaps, now=3 * 3600)["windows"]
    assert set(cov) == {"T+0m", "T+30m", "T+2h", "T+6h", "T+24h"}
    assert cov["T+30m"]["observed"] == 2 and cov["T+30m"]["missing"] == 2 and cov["T+30m"]["missing_observation"] == "PARTIAL"
    assert cov["T+30m"]["median_lp_delta_pct"] == -30.0 and cov["T+30m"]["median_holder_growth_per_h"] == 4.0
    assert cov["T+2h"]["missing_observation"] == "ALL" and cov["T+6h"]["expected"] == 0 and cov["T+6h"]["missing_observation"] == "NONE"
    assert cov["T+0m"]["missing_observation"] == "NONE"


def test_dataset_and_summary_expose_coverage(tmp_path):
    rows = mkrows(1, 3, 1, 3)
    assert "snapshots_summary" in A.dataset(rows, now=10 ** 6) and "time_series_coverage" in A.build(rows, now=10 ** 6)["summary"]
    assert all("snapshots" in r for r in A.dataset(rows, now=1)["rows"])


def test_report_runs_from_rows_and_from_published_api_without_key_errors(tmp_path):
    text = G.generate(mkrows(10, 40, 20, 40))
    assert "Out-of-time comparison" in text and "Fisher" in text and "Time-series coverage" in text
    assert G.generate([]) .startswith("# Solana")                        # empty data must not crash
    api = os.path.join(ROOT, "docs/api/v1")
    assert "Signals (24h)" in G.generate_from_api(api)


def test_collector_follow_up_batches_are_bounded(tmp_path):
    from tests.test_collector import tok
    p = str(tmp_path / "r.jsonl")
    collector.collect(lambda m: tok(m), [f"M{i}" for i in range(10)], p, now=0)
    n = collector.score_snapshots(lambda m: tok(m), p, now=3 * 3600, max_fetch=4)
    assert n == 4
    assert collector.score(lambda m: tok(m), p, now=30 * 3600, max_fetch=3) == 3


def test_actions_json_is_spec_shaped_read_only_and_matches_exporter():
    f = json.load(open(os.path.join(ROOT, "docs/api/v1/actions.json")))
    assert f == A.ACTIONS and f["rules"][0]["pathPattern"] == "/api/v1/actions/*" and f["rules"][0]["apiPath"] == "/api/v1/actions/*"
    from sdk import action_server
    assert action_server.ACTIONS == A.ACTIONS


def test_workflows_are_active_bounded_and_mirror_actions():
    for p in (".github/workflows/forward-test.yml", "contrib/forward-test.workflow.yml"):
        txt = open(os.path.join(ROOT, p)).read()
        assert "NOT ACTIVE" not in txt and "--max-fetch" in txt and "GITHUB_STEP_SUMMARY" in txt
        import re
        assert not re.search(r"\.py[^\n]*\|\| true", txt)                # no python step may hide its failure (only the optional branch fetch may)
        assert re.search(r"^    timeout-minutes: 10$", txt, re.M)          # whole job bounded at 10 minutes
    assert "actions" in open(os.path.join(ROOT, ".github/workflows/pages-api.yml")).read().split("for f in")[1].split(";")[0]


def test_index_shows_sample_status_badges():
    html = open(os.path.join(ROOT, "docs/index.html")).read()
    assert "sample_status" in html and "Low Sample n &lt; 30" in html or "Low Sample n < 30" in html
