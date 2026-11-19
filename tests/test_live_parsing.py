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
