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
    # extra features (None = not reported). Seen in real DexScreener / RugCheck payloads.
    total_holders: int = None
    creator_pct: float = None
    insider_networks: int = None
    buys_h1: int = None
    sells_h1: int = None
    chg_h1: float = None
    chg_m5: float = None
    has_socials: bool = None


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
