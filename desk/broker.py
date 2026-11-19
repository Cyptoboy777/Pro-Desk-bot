"""Paper broker with slippage, price impact and fees. No wallet, no keys, no network."""
import sqlite3
import time
from .models import Position

FEE = 0.003          # 0.3% per side
BASE_SLIPPAGE = 0.003


class PaperBroker:
    def __init__(self, bankroll=1000.0, db=":memory:"):
        self.cash = bankroll
        self.start = bankroll
        self.positions = {}
        self.realized = 0.0
        self.db = sqlite3.connect(db)
        self.db.execute("create table if not exists trades(ts real, tick int, side text, symbol text, "
                        "price real, qty real, usd real, pnl real, reason text)")

    @staticmethod
    def _impact(usd, liquidity):
        return BASE_SLIPPAGE + 2.0 * usd / max(liquidity, 1.0)

    def buy(self, tok, usd, tick, reason):
        if usd > self.cash or tok.mint in self.positions:
            return None
        fill = tok.price * (1 + self._impact(usd, tok.liquidity_usd))
        qty = (usd * (1 - FEE)) / fill
        self.cash -= usd
        self.positions[tok.mint] = Position(tok.mint, tok.symbol, fill, qty, usd, fill, tok.liquidity_usd, tick)
        self._log(tick, "BUY", tok.symbol, fill, qty, usd, 0.0, reason)
        return self.positions[tok.mint]

    def sell(self, tok, tick, reason):
        pos = self.positions.pop(tok.mint, None)
        if not pos:
            return None
        gross = pos.qty * tok.price
        fill_usd = gross * (1 - self._impact(gross, tok.liquidity_usd)) * (1 - FEE)
        fill_usd = max(fill_usd, 0.0)
        pnl = fill_usd - pos.cost_usd
        self.cash += fill_usd
        self.realized += pnl
        self._log(tick, "SELL", tok.symbol, tok.price, pos.qty, fill_usd, pnl, reason)
        return pnl

    def equity(self, prices):
        return self.cash + sum(p.qty * prices.get(m, 0.0) for m, p in self.positions.items())

    def _log(self, tick, side, sym, price, qty, usd, pnl, reason):
        self.db.execute("insert into trades values(?,?,?,?,?,?,?,?,?)",
                        (time.time(), tick, side, sym, price, qty, usd, pnl, reason))
