"""Tests parsing logic against ASSUMED payload shapes (not captured from the live APIs).
Their main job: prove the adapter FAILS CLOSED when fields are missing or wrong."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from desk.live import parse_market, parse_safety
from desk.agents import RiskAgent
from desk.models import Token


def test_empty_or_missing_safety_data_is_unsafe():
    for rep in (None, {}, {"markets": []}):
        s = parse_safety(rep)
        assert not s["mint_authority_disabled"] and not s["freeze_authority_disabled"]
        assert s["top10_holders_pct"] == 100.0 and s["lp_burned_pct"] == 0.0


def test_clean_report_parses_safe():
    rep = {"mintAuthority": None, "freezeAuthority": None,
           "topHolders": [{"pct": 3}] * 10, "markets": [{"lp": {"lpLockedPct": 99}}]}
    s = parse_safety(rep)
    assert s["mint_authority_disabled"] and s["freeze_authority_disabled"]
    assert s["top10_holders_pct"] == 30 and s["lp_burned_pct"] == 99


def test_enabled_mint_authority_is_unsafe():
    assert not parse_safety({"mintAuthority": "SomeKey", "freezeAuthority": None})["mint_authority_disabled"]


def test_market_picks_deepest_pair_for_mint_only():
    pairs = [{"baseToken": {"address": "A", "symbol": "A"}, "priceUsd": "1", "liquidity": {"usd": 10}},
             {"baseToken": {"address": "A", "symbol": "A"}, "priceUsd": "2", "liquidity": {"usd": 500},
              "volume": {"h24": 9}, "pairCreatedAt": (time.time() - 600) * 1000},
             {"baseToken": {"address": "B", "symbol": "B"}, "priceUsd": "3", "liquidity": {"usd": 9999}}]
    m = parse_market(pairs, "A")
    assert m["price"] == 2 and m["liquidity_usd"] == 500 and 9 < m["age_minutes"] < 11
    assert parse_market([], "A") is None


def test_unverified_data_never_passes_risk_agent():
    s = parse_safety(None)
    t = Token("X", "X", 1.0, 1e6, 1e6, 999, **s)
    assert not RiskAgent().check(t, 25).ok


# ---- fixture transcribed from a REAL RugCheck /report response (2026-11-19, one pump.fun-style token)
POOL = "97VYacToT9utEG9TwporrFswbS3otTq88GSgpETBmLZe"
REAL = {
    "mintAuthority": None, "freezeAuthority": None, "rugged": False, "risks": [], "transferFee": {"pct": 0},
    "token_extensions": {"permanentDelegate": None, "transferHook": None, "nonTransferable": False},
    "markets": [{"pubkey": POOL, "liquidityA": "HsYf", "liquidityB": "FZfj", "lp": {"lpLockedPct": 100}}],
    "topHolders": [{"address": "HsYf", "pct": 19.19, "owner": POOL, "insider": False}]
    + [{"address": f"H{i}", "pct": p, "owner": f"O{i}", "insider": False}
       for i, p in enumerate([3.63, 2.87, 2.60, 2.27, 1.86, 1.82, 1.74, 1.60, 1.57, 1.54])],
}


def test_real_payload_excludes_pool_from_top10():
    s = parse_safety(REAL)
    assert s["mint_authority_disabled"] and s["freeze_authority_disabled"]
    assert s["lp_burned_pct"] == 100 and s["risk_flags"] == []
    assert 21 < s["top10_holders_pct"] < 22      # not 39% (which counted the pool)


def test_token2022_and_rugcheck_flags_reject():
    import copy
    for patch, expect in (({"token_extensions": {"permanentDelegate": "X"}}, "permanent delegate"),
                          ({"token_extensions": {"transferHook": "X"}}, "transfer hook"),
                          ({"transferFee": {"pct": 10}}, "transfer fee"),
                          ({"rugged": True}, "rugged"),
                          ({"risks": [{"name": "Mutable metadata", "level": "danger"}]}, "danger")):
        rep = copy.deepcopy(REAL); rep.update(patch)
        s = parse_safety(rep)
        assert any(expect in f for f in s["risk_flags"]), patch
        t = Token("X", "X", 1.0, 1e6, 1e6, 999, **s)
        assert not RiskAgent().check(t, 25).ok


def test_real_token_rejected_only_for_low_liquidity():
    s = parse_safety(REAL)
    m = parse_market([{"baseToken": {"address": "M", "symbol": "TTWO"}, "priceUsd": "0.00005199",
                       "liquidity": {"usd": 18643.05}, "volume": {"h24": 124239},
                       "pairCreatedAt": (time.time() - 1290) * 1000}], "M")
    t = Token("M", **m, **s)
    assert RiskAgent().check(t, 25).reasons == ["liquidity $18,643"]
