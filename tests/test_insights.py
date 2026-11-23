import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import insights


def rows(n=40):
    r = []
    for i in range(n):
        bad = i % 2 == 0
        r.append({"kind": "entry", "ts": 0, "mint": f"M{i}", "price": 1.0, "liq": 50_000, "pass": i < 10, "age_min": i,
                  "top10": 10 + i, "vol24": 1e5, "flags": ["RugCheck danger: X"] if bad else []})
        r.append({"kind": "outcome", "ts": 24 * 3600, "mint": f"M{i}", "horizon_h": 24, "price": 0.1 if bad else 1.0,
                  "liq": 1000 if bad else 50_000, "gone": False})
    return r


def test_wilson_interval_sane():
    lo, hi = insights.wilson(5, 10)
    assert 0.2 < lo < 0.5 < hi < 0.8 and insights.wilson(0, 0) == (0.0, 1.0)


def test_report_has_base_rate_verdict_and_flag_tables():
    t = insights.report(rows())
    assert "Base rate" in t and "20/40" in t and "PASSED" in t and "REJECTED" in t and "| X |" in t


def test_since_filters_old_entries_and_missing_features_do_not_crash():
    assert "No judged tokens" in insights.report(rows(), since=10)
    assert "Total holders" not in insights.report(rows())          # feature absent in rows => skipped
