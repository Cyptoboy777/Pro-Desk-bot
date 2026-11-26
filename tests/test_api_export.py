import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import api_export as A


def rows(n_pass_bad, n_pass, n_rej_bad, n_rej):
    out, i = [], 0
    for passed, n, nb in ((True, n_pass, n_pass_bad), (False, n_rej, n_rej_bad)):
        for j in range(n):
            i += 1
            m = f"M{i}"
            out.append({"kind": "entry", "ts": 0.0, "mint": m, "symbol": "S", "price": 1.0, "liq": 30000, "vol24": 1000,
                        "age_min": 300, "top10": 10, "lp": 100, "flags": [], "pass": passed, "reasons": [], "auth_ok": True})
            out.append({"kind": "outcome", "ts": 24 * 3600.0, "mint": m, "horizon_h": 24, "price": 0.1 if j < nb else 1.0,
                        "liq": 30000, "gone": False})
    return out


def test_insufficient_data_is_the_default_claim():
    s = A.build(rows(1, 5, 2, 5), now=1)["summary"]
    assert s["edge_status"] == "INSUFFICIENT_DATA"


def test_no_edge_when_pass_is_worse():
    s = A.build(rows(40, 50, 10, 50), now=1)["summary"]
    assert s["edge_status"] == "NO_EDGE" and s["pass_vs_reject_24h"]["v1"]["pass"]["bad_rate"] == 0.8


def test_edge_only_when_intervals_separate():
    s = A.build(rows(2, 60, 55, 60), now=1)["summary"]
    assert s["edge_status"] == "STATISTICAL_EDGE_DETECTED"
    assert s["pass_vs_reject_24h"]["v1"]["pass"]["survival_ci95"][0] > s["pass_vs_reject_24h"]["v1"]["reject"]["survival_ci95"][1]


def test_files_are_valid_json_and_features_have_precision_recall(tmp_path):
    b = A.build(rows(10, 40, 20, 40), now=1)
    A.write(str(tmp_path), b)
    for n in ("summary", "features", "recent_scans", "rubric"):
        assert json.load(open(tmp_path / f"{n}.json"))["schema"] == "1.0"
    f = {x["key"]: x for x in b["features"]["features"]}
    assert f["v1_rejected"]["precision"] is not None and f["v1_rejected"]["recall"] is not None
    assert b["recent_scans"]["scans"][0]["outcomes"]["24h"] is not None
