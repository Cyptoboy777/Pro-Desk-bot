"""Read-only live alerts. Places NO orders, holds NO keys.

    python alerts.py --probe          # print raw API JSON once, to verify field names
    python alerts.py --once           # one scan
    python alerts.py                  # poll every 60s
Optional Telegram alerts: export TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

from desk import live
from desk.agents import ScoutAgent, RiskAgent


def telegram(text):
    tok, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not (tok and chat):
        return
    data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/sendMessage", data, timeout=15)
    except Exception as e:
        print("telegram failed:", e)


def probe():
    mints = live.latest_solana_mints(3)
    print("mints:", mints)
    if mints:
        print(json.dumps(live._get(f"{live.DEX}/tokens/v1/solana/{mints[0]}"), indent=1)[:2500])
        print(json.dumps(live._get(f"{live.RUG}/tokens/{mints[0]}/report"), indent=1)[:2500])


def scan(scout, risk, seen):
    toks = []
    for m in live.latest_solana_mints():
        try:
            t = live.fetch_token(m)
        except Exception as e:
            print("skip", m, e)
            continue
        if t:
            toks.append(t)
        time.sleep(0.5)  # be polite to free APIs
    for t, move in scout.scan(toks):
        v = risk.check(t, 25)
        tag = "PASSES risk checks" if v.ok else "REJECTED: " + "; ".join(v.reasons)
        msg = f"{t.symbol} ({t.mint[:6]}…) +{move:.0%} liq ${t.liquidity_usd:,.0f} | {tag}\nhttps://dexscreener.com/solana/{t.mint}"
        if (t.mint, v.ok) not in seen:
            seen.add((t.mint, v.ok))
            print(msg, "\n")
            if v.ok:
                telegram("DESK ALERT (not advice, verify manually)\n" + msg)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--every", type=int, default=60)
    a = ap.parse_args()
    if a.probe:
        probe()
        raise SystemExit
    scout, risk, seen = ScoutAgent(), RiskAgent(), set()
    while True:
        scan(scout, risk, seen)
        if a.once:
            break
        time.sleep(a.every)
