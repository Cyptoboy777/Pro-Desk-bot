"""Forward-test collection and scheduled time-window snapshots.

Read-only public market telemetry. These observations are descriptive, not returns.
"""
import argparse
import json
import os
import statistics
import time

from desk import live
from desk.agents import RiskAgent

HORIZONS_H = (1, 6, 24)
SNAPSHOT_WINDOWS_MIN = (0, 30, 120, 360, 1440)
LATE = 1.5
RUG_LIQ_DROP = 0.5


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
                     "flags": t.risk_flags, "pass": v.ok, "reasons": v.reasons,
                     "total_holders": t.total_holders, "creator_pct": t.creator_pct, "insiders": t.insider_networks,
                     "buy_ratio_h1": (t.buys_h1 / (t.buys_h1 + t.sells_h1)
                                      if t.buys_h1 is not None and t.sells_h1 is not None and (t.buys_h1 + t.sells_h1) > 0 else None),
                     "chg_h1": t.chg_h1, "has_socials": t.has_socials, "mcap": t.mcap, "top1": t.top1_pct,
                     "auth_ok": bool(t.mint_authority_disabled and t.freeze_authority_disabled)})
    append(path, rows)
    return len(rows)


def snapshot_features(entry, token, observed_at):
    """Return transparent deltas. Holder count is a proxy, not wallet identity/distribution."""
    elapsed_h = max((observed_at - entry["ts"]) / 3600, 0)
    base_liq, base_vol = entry.get("liq") or 0, entry.get("vol24") or 0
    liq = token.liquidity_usd if token else 0
    holders = token.total_holders if token else None
    base_holders = entry.get("total_holders")
    vol = token.volume_24h if token else 0
    return {
        "lp_delta_pct": ((liq / base_liq - 1) * 100 if base_liq > 0 else None),
        "holder_growth_rate": ((holders - base_holders) / elapsed_h if holders is not None and base_holders is not None and elapsed_h > 0 else None),
        "volume_decay_ratio": (vol / base_vol if base_vol > 0 else None),
        "holder_metric_note": "holder-count change only; unique-holder identities and early-wallet dumping are not observed",
        "volume_metric_note": "ratio of API-reported rolling 24h volume; not launch-window volume",
    }


def score_snapshots(fetch_token, path, now=None, max_fetch=None):
    """Append one observation per entry/window when due; retries transient fetch failures."""
    now = time.time() if now is None else now
    rows = load(path)
    done = {(r["mint"], r.get("window_min")) for r in rows if r.get("kind") == "snapshot"}
    entries = {r["mint"]: r for r in rows if r.get("kind") == "entry"}
    out, fetched = [], 0
    for mint, entry in entries.items():
        for window in SNAPSHOT_WINDOWS_MIN:
            if window == 0 or (mint, window) in done or now < entry["ts"] + window * 60:
                continue
            if max_fetch is not None and fetched >= max_fetch:
                break                         # budget spent: the rest stays due and is picked up next run
            fetched += 1
            try:
                token = fetch_token(mint)
            except Exception:
                continue
            feats = snapshot_features(entry, token, now)
            out.append({"kind": "snapshot", "ts": now, "mint": mint, "window_min": window,
                        "price": token.price if token else 0.0, "liq": token.liquidity_usd if token else 0.0,
                        "vol24": token.volume_24h if token else 0.0,
                        "total_holders": token.total_holders if token else None, "gone": token is None,
                        **feats})
    append(path, out)
    return len(out)


def score(fetch_token, path, now=None, max_fetch=None):
    now = time.time() if now is None else now
    rows = load(path)
    done = {(r["mint"], r["horizon_h"]) for r in rows if r["kind"] == "outcome"}
    out, fetched = [], 0
    for e in (r for r in rows if r["kind"] == "entry"):
        for h in HORIZONS_H:
            if (e["mint"], h) in done or now < e["ts"] + h * 3600:
                continue
            if max_fetch is not None and fetched >= max_fetch:
                break
            fetched += 1
            try:
                t = fetch_token(e["mint"])
            except Exception:
                continue
            out.append({"kind": "outcome", "ts": now, "mint": e["mint"], "horizon_h": h,
                        "price": t.price if t else 0.0, "liq": t.liquidity_usd if t else 0.0, "gone": t is None})
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
                if e["liq"] > 0:
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
    def wrapped(m):
        time.sleep(pause)
        return fn(m)
    return wrapped


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["collect", "score", "report"])
    ap.add_argument("--data", default="data/snapshots.jsonl")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--max-fetch", type=int, default=60, help="cap on follow-up fetches per run, per kind (keeps runs inside the Actions timeout)")
    a = ap.parse_args()
    if a.cmd == "collect":
        mints = live.latest_solana_mints(a.limit)
        print("recorded", collect(polite(live.fetch_token), mints, a.data), "of", len(mints), "tokens")
    elif a.cmd == "score":
        fetch = polite(live.fetch_token)
        print("recorded", score_snapshots(fetch, a.data, max_fetch=a.max_fetch), "time-window snapshots")
        print("scored", score(fetch, a.data, max_fetch=a.max_fetch), "outcomes")
    else:
        print(report(a.data))
