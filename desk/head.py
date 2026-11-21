"""Head of Desk v2: routes data between agents, applies sizing + protections, writes the
event log the UI replays. Never trades on its own judgement. Optional Claude review is
read-only text.

Config defaults reproduce the v1 baseline (fixed ticket, no protections) so every fix
can be switched on and measured on its own.
"""
import json
import os
import urllib.request
from dataclasses import dataclass, field

from .agents import ScoutAgent, RiskAgent, ExitAgent


def claude_review(summary: str):
    """Optional commentary from Claude. Needs ANTHROPIC_API_KEY. Returns None if unset/failing.
    Claude only writes text here; it has no tool or path to place orders."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    body = json.dumps({
        "model": os.getenv("DESK_MODEL", "claude-sonnet-5-5"),
        "max_tokens": 400,
        "messages": [{"role": "user", "content":
                      "You are the risk reviewer for a PAPER-trading desk. In 5 bullet points, flag "
                      "anything suspicious or fragile in this run. Do not suggest increasing risk.\n\n" + summary}],
    }).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", body, {
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["content"][0]["text"]
    except Exception as e:  # never let commentary break the desk
        return f"(review unavailable: {e})"


@dataclass
class Config:
    # sizing
    sizing: str = "fixed"            # "fixed" | "risk"
    fixed_usd: float = 25.0
    risk_pct: float = 0.01           # equity lost if the stop-loss is hit (risk sizing)
    max_pos_pct: float = 0.10        # hard cap per position, share of equity
    max_exposure_pct: float = 1.0    # cap on total open cost, share of equity
    max_open: int = 5
    daily_loss_halt: float = 0.05
    # entry filter
    max_chase: float = 9.9           # skip if the scout's lookback move is larger than this
    # protections (Freqtrade-style)
    cooldown: int = 0                # ticks a token is locked after we exit it
    guard_n: int = 0                 # StoplossGuard: this many bad exits ...
    guard_window: int = 20           # ... within this many ticks ...
    guard_pause: int = 20            # ... pauses ALL entries for this many ticks
    # edge gate: shrink size while the desk's own recent closed trades have negative expectancy
    edge_n: int = 0                  # window of closed trades (0 = off)
    edge_mult: float = 0.25
    # risk agent
    min_age: float = 10
    max_top10: float = 40
    min_liq: float = 20_000
    min_lp: float = 90
    # exits
    stop: float = 0.15
    take_profit: float = 0.0         # 0 = off; e.g. 0.5 closes at +50%
    max_hold: int = 60


class SizerAgent:
    """Sizes from account equity and stop distance, then caps by liquidity and exposure."""

    def __init__(self, cfg):
        self.cfg = cfg

    def size(self, tok, equity, cash, open_cost):
        c = self.cfg
        if c.sizing == "fixed":
            want = c.fixed_usd
        else:
            want = equity * c.risk_pct / c.stop
        caps = [equity * c.max_pos_pct, 0.02 * tok.liquidity_usd, cash,
                equity * c.max_exposure_pct - open_cost]
        return max(0.0, min([want] + caps))


class HeadOfDesk:
    def __init__(self, broker, size_usd=25.0, max_open=5, daily_loss_halt=0.05, cfg=None):
        self.cfg = cfg or Config(fixed_usd=size_usd, max_open=max_open, daily_loss_halt=daily_loss_halt)
        c = self.cfg
        self.broker = broker
        self.scout = ScoutAgent()
        self.risk = RiskAgent(min_liq=c.min_liq, max_top10=c.max_top10, min_lp_burned=c.min_lp, min_age=c.min_age)
        self.exit = ExitAgent(stop=c.stop, max_hold=c.max_hold, take_profit=c.take_profit)
        self.sizer = SizerAgent(c)
        self.halted = False
        self.stats = {"scanned": 0, "candidates": 0, "rejected": 0, "skipped": 0, "executed": 0, "rug_exits": 0}
        self.needs_human = []
        self.events, self.curve = [], []
        self.cool_until, self.bad_exits, self.pause_until = {}, [], -1
        self.closed = []                 # realised pnl of closed trades, in order

    # ---- helpers
    def _ev(self, tick, kind, sym, reason="", **kw):
        self.events.append({"t": tick, "kind": kind, "sym": sym, "reason": reason, **kw})

    def step(self, tick, tokens):
        c, b = self.cfg, self.broker
        by_mint = {t.mint: t for t in tokens}
        prices = {t.mint: t.price for t in tokens}
        # 1) exits first
        for mint, pos in list(b.positions.items()):
            t = by_mint.get(mint)
            if t is None:
                continue
            why = self.exit.decide(pos, t, tick)
            if why:
                pnl = b.sell(t, tick, why)
                self.closed.append(pnl)
                self._ev(tick, "EXIT", t.symbol, why, pnl=round(pnl, 2))
                self.cool_until[mint] = tick + c.cooldown
                if why.startswith("RUG"):
                    self.stats["rug_exits"] += 1
                if why.startswith("RUG") or why == "stop-loss":
                    self.bad_exits.append(tick)
        eq = b.equity(prices)
        self.curve.append(round(eq, 2))
        # 2) circuit breaker + StoplossGuard
        if not self.halted and eq < b.start * (1 - c.daily_loss_halt):
            self.halted = True
            self.needs_human.append(f"tick {tick}: HALTED, equity ${eq:,.0f} is below the loss limit")
            self._ev(tick, "HALT", "-", f"equity ${eq:,.0f} below loss limit")
        if self.halted:
            return
        if c.guard_n:
            recent = [x for x in self.bad_exits if x > tick - c.guard_window]
            if len(recent) >= c.guard_n and tick > self.pause_until:
                self.pause_until = tick + c.guard_pause
                self._ev(tick, "PAUSE", "-", f"{len(recent)} bad exits in {c.guard_window} ticks")
        if tick <= self.pause_until:
            return
        # 3) entries
        self.stats["scanned"] += len(tokens)
        for t, move in self.scout.scan(tokens):
            self.stats["candidates"] += 1
            self._ev(tick, "SCAN", t.symbol, f"spike +{move:.0%} · vol {t.volume_24h / max(t.liquidity_usd, 1):.1f}x")
            if len(b.positions) >= c.max_open:
                break
            if move > c.max_chase or self.cool_until.get(t.mint, -1) >= tick:
                self.stats["skipped"] += 1
                self._ev(tick, "SKIP", t.symbol, "already ran" if move > c.max_chase else "cooldown")
                continue
            open_cost = sum(p.cost_usd for p in b.positions.values())
            usd = self.sizer.size(t, eq, b.cash, open_cost)
            if c.edge_n and len(self.closed) >= c.edge_n and sum(self.closed[-c.edge_n:]) < 0:
                usd *= c.edge_mult
            v = self.risk.check(t, usd if usd > 0 else c.fixed_usd)
            if not v.ok or usd < 1.0:
                self.stats["rejected"] += 1
                self._ev(tick, "FILTERED", t.symbol, "; ".join(v.reasons) or "no size available")
                continue
            reason = f"vol {t.volume_24h / max(t.liquidity_usd, 1):.1f}x + LP burned {t.lp_burned_pct:.0f}%"
            pos = b.buy(t, usd, tick, reason)
            if pos:
                self.stats["executed"] += 1
                self._ev(tick, "ENTER", t.symbol, reason, size_pct=round(usd / eq * 100, 1),
                         slip=round((pos.entry_price / t.price - 1) * 100, 2))

    def summary(self, prices):
        eq = self.broker.equity(prices)
        return {**self.stats, "open": len(self.broker.positions),
                "equity": round(eq, 2), "return_pct": round((eq / self.broker.start - 1) * 100, 2),
                "halted": self.halted, "needs_human": self.needs_human}
