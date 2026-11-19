import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from bot.telegram_bot import handle, HELP
from desk.models import Token

ADDR = "Hhcyc5MBHPophkGjsfpJmma4NoztommaQGq7D4RVpump"


def tok(**kw):
    d = dict(mint=ADDR, symbol="TTWO", price=1.0, liquidity_usd=18643, volume_24h=1e5, age_minutes=21,
             top10_holders_pct=21.5, mint_authority_disabled=True, freeze_authority_disabled=True, lp_burned_pct=100)
    d.update(kw); return Token(**d)


def test_help_and_bad_input():
    assert handle("/start", None) == HELP
    assert "does not look like" in handle("hhcyc5mbhpophkgjsfpjmma4noztommaqgq7d4rvpump0", None)   # contains '0' (not base58)
    assert "does not look like" in handle("hello", None)


def test_reject_reports_reasons_and_accepts_check_command():
    r = handle(f"/check {ADDR}", lambda a: tok())
    assert "REJECT" in r and "liquidity $18,643" in r and "Not financial advice" in r


def test_pass_message():
    assert "PASSES" in handle(ADDR, lambda a: tok(liquidity_usd=90_000))


def test_fail_closed_on_errors_and_missing_pair():
    def boom(a): raise RuntimeError("x")
    assert "unsafe" in handle(ADDR, boom)
    assert "unsafe" in handle(ADDR, lambda a: None)
