"""Desk agents. Rule-based and deterministic on purpose: an LLM may comment or
veto, but can never override a RiskAgent rejection."""
from collections import defaultdict, deque
from .models import Verdict


class ScoutAgent:
    """Finds candidates: enough liquidity/volume and fresh upward momentum."""

    def __init__(self, lookback=3, min_move=0.05, min_vol_liq=0.5):
        self.hist = defaultdict(lambda: deque(maxlen=lookback + 1))
        self.lookback, self.min_move, self.min_vol_liq = lookback, min_move, min_vol_liq

    def scan(self, tokens):
        picks = []
        for t in tokens:
            h = self.hist[t.mint]
            h.append(t.price)
            if len(h) <= self.lookback:
                continue
            move = h[-1] / h[0] - 1
            if move >= self.min_move and t.volume_24h / max(t.liquidity_usd, 1) >= self.min_vol_liq:
                picks.append((t, move))
        return sorted(picks, key=lambda x: -x[1])


class RiskAgent:
    """Hard checks before entry. Any failure = reject. Mirrors what rug-check APIs report."""

    def __init__(self, min_liq=20_000, max_top10=40, min_lp_burned=90, max_size_vs_liq=0.02, min_age=10):
        self.min_liq, self.max_top10, self.min_lp, self.max_size, self.min_age = \
            min_liq, max_top10, min_lp_burned, max_size_vs_liq, min_age

    def check(self, t, size_usd):
        r = []
        if not t.mint_authority_disabled:
            r.append("mint authority enabled")
        if not t.freeze_authority_disabled:
            r.append("freeze authority enabled")
        if t.lp_burned_pct < self.min_lp:
            r.append(f"LP burned only {t.lp_burned_pct:.0f}%")
        if t.top10_holders_pct > self.max_top10:
            r.append(f"top10 holders {t.top10_holders_pct:.0f}%")
        if t.liquidity_usd < self.min_liq:
            r.append(f"liquidity ${t.liquidity_usd:,.0f}")
        if size_usd > self.max_size * t.liquidity_usd:
            r.append("position too large vs liquidity")
        if t.age_minutes < self.min_age:
            r.append("too new")
        return Verdict(not r, r)


class ExitAgent:
    """Stop-loss, trailing stop, rug trigger (liquidity collapse), max hold."""

    def __init__(self, stop=0.15, trail_after=0.20, trail=0.15, rug_liq_drop=0.30, max_hold=60):
        self.stop, self.trail_after, self.trail, self.rug, self.max_hold = \
            stop, trail_after, trail, rug_liq_drop, max_hold

    def decide(self, pos, t, tick):
        pos.peak_price = max(pos.peak_price, t.price)
        if t.liquidity_usd < pos.entry_liquidity * (1 - self.rug):
            return "RUG: liquidity dropped"
        if t.price <= pos.entry_price * (1 - self.stop):
            return "stop-loss"
        if pos.peak_price >= pos.entry_price * (1 + self.trail_after) and t.price <= pos.peak_price * (1 - self.trail):
            return "trailing stop"
        if tick - pos.opened_tick >= self.max_hold:
            return "max hold"
        return None
