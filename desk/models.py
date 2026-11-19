"""Shared data types. Paper trading only: nothing here can touch a wallet."""
from dataclasses import dataclass, field


@dataclass
class Token:
    mint: str
    symbol: str
    price: float
    liquidity_usd: float
    volume_24h: float
    age_minutes: float
    top10_holders_pct: float
    mint_authority_disabled: bool
    freeze_authority_disabled: bool
    lp_burned_pct: float
    risk_flags: list = field(default_factory=list)


@dataclass
class Verdict:
    ok: bool
    reasons: list = field(default_factory=list)


@dataclass
class Position:
    mint: str
    symbol: str
    entry_price: float
    qty: float
    cost_usd: float
    peak_price: float
    entry_liquidity: float
    opened_tick: int
