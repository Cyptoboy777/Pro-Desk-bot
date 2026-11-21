"""Live paper trader: real tokens, real prices, simulated fills. NO orders, NO keys.

    python3 paper_live.py run      # one poll: update watchlist, exits, entries, save state
    python3 paper_live.py report   # equity, trades, win rate

Each run is one tick. State lives in data/paper_state.json, the decision log in
data/paper_events.jsonl (append-only), so it works from a scheduled job.

Honest limits: polling every ~30 min cannot honour fast stops (fills happen at the price seen
at the poll, like a slow bot would get), and DexScreener prices are not executable quotes.
"""
import argparse
import datetime
import json
import os
import time
from collections import deque
from dataclasses import asdict

from desk import live
from desk.broker import PaperBroker
from desk.head import HeadOfDesk, Config
from desk.models import Token, Position

LIVE_CFG = Config(guard_n=3, guard_window=8, guard_pause=8, cooldown=4, edge_n=8, max_hold=12, take_profit=0.3)
MAX_WATCH, WATCH_TICKS, SAFETY_TTL = 40, 12, 12
STATE, EVENTS = "data/paper_state.json", "data/paper_events.jsonl"


def new_state(bankroll=1000.0):
    return {"tick": 0, "start": bankroll, "cash": bankroll, "realized": 0.0, "positions": {}, "hist": {},
            "cool_until": {}, "bad_exits": [], "pause_until": -1, "closed": [], "halted": False,
            "stats": None, "needs_human": [], "watch": {}, "safety": {}, "curve": []}


def _restore(st):
    b = PaperBroker(st["start"])
    b.cash, b.realized = st["cash"], st["realized"]
    b.positions = {m: Position(**p) for m, p in st["positions"].items()}
    h = HeadOfDesk(b, cfg=LIVE_CFG)
    for m, vals in st["hist"].items():
        h.scout.hist[m] = deque(vals, maxlen=h.scout.lookback + 1)
    h.cool_until, h.bad_exits, h.pause_until = st["cool_until"], st["bad_exits"], st["pause_until"]
    h.closed, h.halted, h.needs_human = st["closed"], st["halted"], st["needs_human"]
    if st["stats"]:
        h.stats = st["stats"]
    return b, h


def run_once(st, fetch_market, fetch_safety, new_mints, now=None):
    """Advance the paper desk by one tick. Returns (state, events)."""
    tick = st["tick"] + 1
    for m in new_mints:
        if len(st["watch"]) < MAX_WATCH:
            st["watch"].setdefault(m, tick)
    st["watch"] = {m: t for m, t in st["watch"].items() if tick - t <= WATCH_TICKS or m in st["positions"]}
    tokens = []
    for m in list(st["watch"]):
        try:
            mk = fetch_market(m)
        except Exception:
            continue                            # network hiccup: skip this token this tick
        if mk is None:                          # pair vanished
            if m in st["positions"]:            # open position in a vanished token = total loss
                p = st["positions"][m]
                tokens.append(Token(m, p["symbol"], 0.0, 0.0, 0.0, 0.0, 100.0, False, False, 0.0))
            else:
                st["watch"].pop(m)
            continue
        sf = st["safety"].get(m)
        if not sf or tick - sf["tick"] > SAFETY_TTL:
            sf = {"tick": tick, **fetch_safety(m)}
            st["safety"][m] = sf
        tokens.append(Token(m, **mk, **{k: v for k, v in sf.items() if k != "tick"}))
    b, h = _restore(st)
    h.step(tick, tokens)
    prices = {t.mint: t.price for t in tokens}
    st.update(tick=tick, cash=b.cash, realized=b.realized, positions={m: asdict(p) for m, p in b.positions.items()},
              hist={m: list(d) for m, d in h.scout.hist.items() if m in st["watch"]},
              cool_until=h.cool_until, bad_exits=h.bad_exits[-50:], pause_until=h.pause_until, closed=h.closed,
              halted=h.halted, stats=h.stats, needs_human=h.needs_human)
    st["safety"] = {m: v for m, v in st["safety"].items() if m in st["watch"]}
    st["curve"].append(round(b.equity(prices), 2))
    stamp = datetime.datetime.fromtimestamp(time.time() if now is None else now, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    return st, [{**e, "ts": stamp} for e in h.events if e["kind"] != "SCAN"]


def morning_table(st, events, last_n=40):
    """Markdown report: summary + every decision in a table (newest last)."""
    rows = [e for e in events if e["kind"] in ("ENTER", "EXIT", "HALT", "PAUSE")][-last_n:]
    out = [f"# Paper desk report", "", report(st, events), "", "| time (UTC) | action | token | size / pnl | reason |", "|---|---|---|---|---|"]
    for e in rows:
        amt = f"{e['size_pct']}% of equity" if e["kind"] == "ENTER" else (f"{e['pnl']:+.2f} USD" if "pnl" in e else "")
        out.append(f"| {e.get('ts', '')} | {e['kind'].lower()} | {e['sym']} | {amt} | {e['reason']} |")
    if not rows:
        out.append("| - | no trades yet | - | - | - |")
    return "\n".join(out) + "\n"


def load_state(path=STATE):
    return json.load(open(path)) if os.path.exists(path) else new_state()


def save(st, events, path=STATE, epath=EVENTS):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    json.dump(st, open(path, "w"))
    with open(epath, "a") as f:
        for e in events:
            f.write(json.dumps(e, separators=(",", ":")) + "\n")


def report(st, events):
    ex = [e for e in events if e["kind"] == "EXIT"]
    w = sum(e["pnl"] > 0 for e in ex)
    eq = st["curve"][-1] if st["curve"] else st["start"]
    lines = [f"ticks {st['tick']} | equity ${eq:,.2f} ({(eq / st['start'] - 1) * 100:+.2f}%) | open {len(st['positions'])} "
             f"| closed {len(ex)} (wins {w}, losses {len(ex) - w}) | halted {st['halted']}"]
    if ex:
        lines.append(f"realized pnl ${sum(e['pnl'] for e in ex):+,.2f} | avg ${sum(e['pnl'] for e in ex) / len(ex):+.2f} per closed trade")
    lines += [f"flag: {x}" for x in st["needs_human"]]
    lines.append("Paper results on real prices with simulated fills. Small samples mean nothing.")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    ap.add_argument("--table", action="store_true", help="markdown morning report")
    a = ap.parse_args()
    if a.cmd == "run":
        pol = lambda fn: (lambda m: (time.sleep(0.5), fn(m))[1])
        st, ev = run_once(load_state(), pol(live.fetch_market), pol(live.fetch_safety), live.latest_solana_mints(30))
        save(st, ev)
        print(report(st, ev))
    else:
        evs = [json.loads(x) for x in open(EVENTS)] if os.path.exists(EVENTS) else []
        print(morning_table(load_state(), evs) if a.table else report(load_state(), evs))
