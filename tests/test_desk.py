import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from desk.models import Token
from desk.agents import RiskAgent, ExitAgent
from desk.broker import PaperBroker
from desk.head import HeadOfDesk


def tok(**kw):
    d = dict(mint="X", symbol="X", price=1.0, liquidity_usd=100_000, volume_24h=100_000, age_minutes=60,
             top10_holders_pct=20, mint_authority_disabled=True, freeze_authority_disabled=True, lp_burned_pct=99)
    d.update(kw)
    return Token(**d)


def test_risk_accepts_clean():
    assert RiskAgent().check(tok(), 25).ok


def test_risk_rejects_each_red_flag():
    for kw in ({"mint_authority_disabled": False}, {"freeze_authority_disabled": False},
               {"lp_burned_pct": 10}, {"top10_holders_pct": 80}, {"liquidity_usd": 5_000}, {"age_minutes": 1}):
        assert not RiskAgent().check(tok(**kw), 25).ok, kw


def test_risk_rejects_oversized_position():
    assert not RiskAgent().check(tok(liquidity_usd=20_000), 1_000).ok


def test_exit_rug_trigger_and_stop():
    b = PaperBroker()
    b.buy(tok(), 25, 0, "t")
    pos = b.positions["X"]
    ex = ExitAgent()
    assert ex.decide(pos, tok(liquidity_usd=50_000), 1).startswith("RUG")
    assert ex.decide(pos, tok(price=pos.entry_price * 0.8), 1) == "stop-loss"
    assert ex.decide(pos, tok(price=pos.entry_price * 1.05), 1) is None


def test_trailing_stop():
    b = PaperBroker()
    b.buy(tok(), 25, 0, "t")
    pos = b.positions["X"]
    ex = ExitAgent()
    assert ex.decide(pos, tok(price=pos.entry_price * 1.5), 1) is None
    assert ex.decide(pos, tok(price=pos.entry_price * 1.5 * 0.8), 2) == "trailing stop"


def test_broker_costs_make_round_trip_lossy():
    b = PaperBroker(1000)
    b.buy(tok(), 100, 0, "t")
    pnl = b.sell(tok(), 1, "t")
    assert pnl < 0          # fees + slippage, same price
    assert abs(b.cash + 0 - (1000 + pnl)) < 1e-9


def test_circuit_breaker_halts_and_flags_human():
    b = PaperBroker(1000)
    h = HeadOfDesk(b)
    b.cash = 900  # simulate a >5% drawdown
    h.step(1, [tok()])
    assert h.halted and h.needs_human


def test_max_open_positions_respected():
    b = PaperBroker(10_000)
    h = HeadOfDesk(b, max_open=2)
    for i in range(10):
        toks = [tok(mint=f"M{j}", symbol=f"M{j}", price=1.0 + 0.1 * i) for j in range(6)]
        h.step(i + 1, toks)
    assert len(b.positions) <= 2
