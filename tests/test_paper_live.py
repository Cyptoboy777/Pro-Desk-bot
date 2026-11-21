import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import paper_live as pl

SAFE = dict(mint_authority_disabled=True, freeze_authority_disabled=True, top10_holders_pct=20, lp_burned_pct=99, risk_flags=[])


def mk(price, liq=100_000):
    return {"symbol": "AAA", "price": price, "liquidity_usd": liq, "volume_24h": 200_000, "age_minutes": 60}


def drive(prices, liqs=None, safety=SAFE):
    st, evs = pl.new_state(), []
    for i, p in enumerate(prices):
        fm = (lambda m, p=p, i=i: None if p is None else mk(p, (liqs or {}).get(i, 100_000)))
        st, e = pl.run_once(json.loads(json.dumps(st)), fm, lambda m: dict(safety), ["AAA"])   # state survives JSON round-trip
        evs += e
    return st, evs


def test_enters_on_momentum_once_and_survives_persistence():
    st, evs = drive([1.0, 1.06, 1.12, 1.19, 1.25, 1.31])
    assert len([e for e in evs if e["kind"] == "ENTER"]) == 1
    assert "AAA" in st["positions"] and st["tick"] == 6 and len(st["curve"]) == 6


def test_unsafe_token_never_enters():
    bad = dict(SAFE, mint_authority_disabled=False)
    st, evs = drive([1.0, 1.06, 1.12, 1.19, 1.25], safety=bad)
    assert not st["positions"] and any(e["kind"] == "FILTERED" for e in evs)


def test_vanished_token_is_total_loss_and_closed():
    st, evs = drive([1.0, 1.06, 1.12, 1.19, 1.25, None])
    ex = [e for e in evs if e["kind"] == "EXIT"]
    assert ex and ex[0]["reason"].startswith("RUG") and ex[0]["pnl"] < -20
    assert not st["positions"] and st["cash"] < 1000


def test_liquidity_collapse_triggers_rug_exit():
    st, evs = drive([1.0, 1.06, 1.12, 1.19, 1.25, 0.2], liqs={5: 3_000})
    assert any(e["kind"] == "EXIT" and e["reason"].startswith("RUG") for e in evs)


def test_report_runs():
    st, evs = drive([1.0, 1.06, 1.12, 1.19, 1.25, None])
    assert "equity" in pl.report(st, evs)


def test_morning_table_lists_trades_with_timestamps():
    st, evs = pl.new_state(), []
    for i, p in enumerate([1.0, 1.06, 1.12, 1.19, 1.25, None]):
        fm = (lambda m, p=p: None if p is None else mk(p))
        st, e = pl.run_once(json.loads(json.dumps(st)), fm, lambda m: dict(SAFE), ["AAA"], now=1_800_000_000 + i * 1800)
        evs += e
    t = pl.morning_table(st, evs)
    assert t.startswith("# Paper desk report") and "| enter |" in t and "| exit |" in t and "2027-" in t


def test_zero_liquidity_token_does_not_crash_the_desk():
    st = pl.new_state()
    for i, p in enumerate([1.0, 1.1, 1.2, 1.3, 1.4]):
        st, _ = pl.run_once(json.loads(json.dumps(st)), lambda m, p=p: mk(p, liq=0), lambda m: dict(SAFE), ["AAA"])
    assert st["tick"] == 5 and not st["positions"]
