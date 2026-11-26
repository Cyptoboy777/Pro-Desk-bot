import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from desk.risk_engine import assess, RiskConfig, row_from_token, feature_vector, ENGINE_VERSION
from desk.models import Token


def row(**kw):
    d = dict(liq=50_000, vol24=500_000, age_min=300, top10=12, lp=100, flags=[], auth_ok=True, mcap=400_000,
             top1=4, insiders=0, buy_ratio_h1=0.55)
    d.update(kw); return d


def test_clean_mature_token_passes_with_full_breakdown():
    r = assess(row())
    assert r["passed"] and r["risk_score"] == 0 and r["failed_reasons"] == [] and r["engine_version"] == ENGINE_VERSION
    assert set(r) >= {"risk_score", "passed", "failed_reasons", "feature_vector", "components"}
    assert r["feature_vector"]["vol_liq"] == 10 and r["feature_vector"]["unknown"] == ["chg_h1", "creator_pct", "total_holders"]


def test_hard_rules_always_fail_whatever_the_score():
    for kw, text in (({"auth_ok": False}, "authority"), ({"flags": ["RugCheck danger: X"]}, "RugCheck danger"),
                     ({"lp": 20}, "LP locked"), ({"liq": 500}, "below minimum")):
        r = assess(row(**kw))
        assert not r["passed"] and any(text in x for x in r["failed_reasons"]), kw


def test_old_rows_derive_authority_from_v1_reasons():
    assert not assess(row(auth_ok=None, reasons=["mint authority enabled"]))["passed"]
    assert assess(row(auth_ok=None, reasons=[]))["passed"]


def test_maturity_is_the_main_driver_and_points_explain_the_score():
    young = assess(row(age_min=20))
    assert young["components"]["maturity"] == 40 and not young["passed"]
    assert any("token age 20m" in x for x in young["failed_reasons"])
    a = assess(row(age_min=150))
    assert a["passed"] and a["risk_score"] == 10 and any("+10" in x for x in a["failed_reasons"])   # passes, but still explains its points
    assert not assess(row(age_min=45, top10=30))["passed"]            # 30 + 20


def test_unknown_features_add_no_points():
    r = assess(row(top1=None, insiders=None, buy_ratio_h1=None, mcap=None))
    assert r["risk_score"] == 0 and {"top1_pct", "insiders", "buy_ratio_h1", "liq_mcap"} <= set(r["feature_vector"]["unknown"])


def test_concentration_bundle_and_liquidity_signals():
    r = assess(row(top10=45, top1=20, insiders=3, mcap=5_000_000, vol24=50_000 * 300, buy_ratio_h1=0.2))
    c = r["components"]
    assert c["concentration"] == 30 and c["liquidity"] == 30        # both capped
    assert r["risk_score"] == 60 and not r["passed"]


def test_config_roundtrip_and_threshold_changes_decision():
    cfg = RiskConfig.from_dict(RiskConfig().to_dict())
    assert cfg == RiskConfig() and isinstance(cfg.age_bounds, tuple)
    lenient = RiskConfig(pass_threshold=60)
    assert assess(row(age_min=45, top10=30), lenient)["passed"]


def test_token_adapter():
    t = Token("M", "T", 1.0, 50_000, 100_000, 300, 12, True, True, 100, buys_h1=60, sells_h1=40, mcap=400_000, top1_pct=4)
    r = row_from_token(t)
    assert r["buy_ratio_h1"] == 0.6 and r["auth_ok"] is True and assess(r)["passed"]
