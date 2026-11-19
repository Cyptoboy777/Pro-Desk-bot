import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import collector
from desk.models import Token


def tok(mint, price=1.0, liq=100_000, bad=False):
    return Token(mint, mint, price, liq, 200_000, 60, 20, not bad, True, 99)


def test_collect_records_verdicts_and_dedupes(tmp_path):
    p = str(tmp_path / "s.jsonl")
    fetch = lambda m: tok(m, bad=(m == "BAD"))
    assert collector.collect(fetch, ["OK", "BAD"], p, now=1000) == 2
    assert collector.collect(fetch, ["OK", "BAD", "NEW"], p, now=2000) == 1      # no duplicates
    e = {r["mint"]: r for r in collector.load(p)}
    assert e["OK"]["pass"] and not e["BAD"]["pass"] and "mint authority enabled" in e["BAD"]["reasons"]


def test_collect_skips_failed_and_missing_tokens(tmp_path):
    p = str(tmp_path / "s.jsonl")
    def fetch(m):
        if m == "ERR": raise RuntimeError("net")
        return None if m == "NONE" else tok(m)
    assert collector.collect(fetch, ["ERR", "NONE", "OK"], p, now=1) == 1


def test_score_waits_for_horizon_and_never_double_scores(tmp_path):
    p = str(tmp_path / "s.jsonl")
    collector.collect(lambda m: tok(m), ["A"], p, now=0)
    assert collector.score(lambda m: tok(m, 2.0), p, now=1800) == 0              # 30 min: too early
    assert collector.score(lambda m: tok(m, 2.0), p, now=3600) == 1              # 1h outcome
    assert collector.score(lambda m: tok(m, 2.0), p, now=3700) == 0              # not repeated
    assert collector.score(lambda m: tok(m, 3.0), p, now=6 * 3600) == 1          # 6h outcome


def test_network_error_records_nothing_but_missing_token_counts_as_gone(tmp_path):
    p = str(tmp_path / "s.jsonl")
    collector.collect(lambda m: tok(m), ["A"], p, now=0)
    def boom(m): raise RuntimeError("net")
    assert collector.score(boom, p, now=3600) == 0
    assert collector.score(lambda m: None, p, now=3600) == 1
    o = [r for r in collector.load(p) if r["kind"] == "outcome"][0]
    assert o["gone"] and o["price"] == 0.0


def test_report_separates_passed_and_rejected_and_counts_rugs(tmp_path):
    p = str(tmp_path / "s.jsonl")
    fetch = lambda m: tok(m, bad=m.startswith("BAD"))
    collector.collect(fetch, ["OK1", "OK2", "BAD1"], p, now=0)
    after = {"OK1": tok("OK1", 2.0), "OK2": tok("OK2", 0.1, liq=1_000), "BAD1": tok("BAD1", 0.5)}
    collector.score(lambda m: after[m], p, now=3600)
    r = collector.report(p)
    assert "3 tokens recorded, 2 passed" in r
    assert "PASSED    n=  2" in r and "rugged/gone  50%" in r      # OK2 lost 99% of its liquidity
    assert "REJECTED  n=  1" in r
