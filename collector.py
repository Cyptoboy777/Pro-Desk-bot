"""Forward test: record real new Solana tokens, then score what happened later.

    python3 collector.py collect   # snapshot new tokens + the Risk agent's verdict
    python3 collector.py score     # revisit tokens after 1h / 6h and record price + liquidity
    python3 collector.py report    # compare tokens that PASSED vs were REJECTED

Read-only: public DexScreener / RugCheck endpoints, no keys, no orders. The data file is
append-only JSONL so it can be committed, diffed and audited.
Outcome numbers are raw price changes, NOT tradable returns (no fees, slippage or exit liquidity).
"""
import argparse
import json
import os
import statistics
import time

from desk import live
from desk.agents import RiskAgent

HORIZONS_H = (1, 6, 24)
LATE = 1.5                  # an outcome counts for horizon h only if measured within LATE*h hours
RUG_LIQ_DROP = 0.5          # liquidity fell by half or more => counted as rugged


def load(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(x) for x in f if x.strip()]


def append(path, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")


def collect(fetch_token, mints, path, now=None, risk=None, size_usd=25.0):
    now, risk = (time.time() if now is None else now), risk or RiskAgent()
    seen = {r["mint"] for r in load(path) if r["kind"] == "entry"}
    rows = []
    for m in mints:
        if m in seen:
            continue
        try:
            t = fetch_token(m)
        except Exception:
            continue
        if t is None:
            continue
        v = risk.check(t, size_usd)
        rows.append({"kind": "entry", "ts": now, "mint": m, "symbol": t.symbol, "price": t.price,
                     "liq": t.liquidity_usd, "vol24": t.volume_24h, "age_min": round(t.age_minutes, 1),
                     "top10": round(t.top10_holders_pct, 2), "lp": t.lp_burned_pct,
                     "flags": t.risk_flags, "pass": v.ok, "reasons": v.reasons})
    append(path, rows)
    return len(rows)


def score(fetch_token, path, now=None):
    now = time.time() if now is None else now
    rows = load(path)
    done = {(r["mint"], r["horizon_h"]) for r in rows if r["kind"] == "outcome"}
    out = []
    for e in (r for r in rows if r["kind"] == "entry"):
        for h in HORIZONS_H:
            if (e["mint"], h) in done or now < e["ts"] + h * 3600:
                continue
            try:
                t = fetch_token(e["mint"])
            except Exception:
                continue                      # network hiccup: try again next run, record nothing
            out.append({"kind": "outcome", "ts": now, "mint": e["mint"], "horizon_h": h,
                        "price": t.price if t else 0.0, "liq": t.liquidity_usd if t else 0.0,
                        "gone": t is None})
    append(path, out)
    return len(out)


def report(path):
    rows = load(path)
    entries = {r["mint"]: r for r in rows if r["kind"] == "entry"}
    outs = {(r["mint"], r["horizon_h"]): r for r in rows if r["kind"] == "outcome"}
    lines = [f"{len(entries)} tokens recorded, {sum(e['pass'] for e in entries.values())} passed the Risk agent"]
    for h in HORIZONS_H:
        lines.append(f"\n== about {h}h after first sighting (raw price change, before any costs)")
        late = 0
        for label, want in (("PASSED", True), ("REJECTED", False)):
            ch, rugged, rug_n, n, el = [], 0, 0, 0, []
            for m, e in entries.items():
                o = outs.get((m, h))
                if e["pass"] != want or not o:
                    continue
                hrs = (o["ts"] - e["ts"]) / 3600
                if hrs > LATE * h:
                    late += 1
                    continue
                n += 1
                el.append(hrs)
                ch.append((o["price"] / e["price"] - 1) * 100 if e["price"] else 0.0)
                if e["liq"] > 0:                       # a rug is only measurable if there was liquidity
                    rug_n += 1
                    rugged += o["gone"] or o["liq"] <= e["liq"] * (1 - RUG_LIQ_DROP)
            if not n:
                lines.append(f"{label:9s} n=0")
                continue
            lines.append(f"{label:9s} n={n:3d} | median {statistics.median(ch):+7.1f}% | mean {statistics.mean(ch):+8.1f}% "
                         f"| up {sum(c > 0 for c in ch) / n:4.0%} | rugged/gone {rugged}/{rug_n} "
                         f"| measured after {statistics.median(el):.1f}h")
        if late:
            lines.append(f"({late} outcomes excluded: measured later than {LATE}x the horizon because runs were sparse)")
    lines.append("\nSmall samples mean nothing. Wait for 100+ tokens per group before trusting any number.")
    return "\n".join(lines)


def polite(fn, pause=0.5):
    """Wrap a fetcher so free APIs are not hammered."""
    def wrapped(m):
        time.sleep(pause)
        return fn(m)
    return wrapped


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["collect", "score", "report"])
    ap.add_argument("--data", default="data/snapshots.jsonl")
    ap.add_argument("--limit", type=int, default=30)
    a = ap.parse_args()
    if a.cmd == "collect":
        mints = live.latest_solana_mints(a.limit)
        print("recorded", collect(polite(live.fetch_token), mints, a.data), "of", len(mints), "tokens")
    elif a.cmd == "score":
        print("scored", score(polite(live.fetch_token), a.data), "outcomes")
    else:
        print(report(a.data))
