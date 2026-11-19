"""Telegram token risk-check bot (read-only).

    export TELEGRAM_BOT_TOKEN=...       # from @BotFather
    python3 -m bot.telegram_bot

Send a Solana token address (copy-paste it: addresses are case-sensitive) or /check <address>.
The bot only reads public DexScreener / RugCheck data. It holds no wallet and places no orders.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

from desk import live
from desk.agents import RiskAgent

B58 = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
HELP = ("Send a Solana token address (paste it, addresses are case-sensitive) or /check <address>.\n"
        "I run read-only safety checks on public data. Not financial advice: checks cannot catch every rug.")


def handle(text, fetch_token, risk=None):
    risk = risk or RiskAgent()
    parts = (text or "").strip().split()
    if not parts or parts[0] in ("/start", "/help"):
        return HELP
    addr = parts[1] if parts[0].startswith("/check") and len(parts) > 1 else parts[0]
    if not B58.match(addr):
        return "That does not look like a Solana address. Paste it exactly (capital letters matter) or use /check <address>."
    try:
        t = fetch_token(addr)
    except Exception:
        return "Data unavailable right now. Treat the token as unsafe until checks can run."
    if t is None:
        return "No trading pair found for that address (or no liquidity). Treat as unsafe."
    v = risk.check(t, 25)
    head = (f"{t.symbol} | liquidity ${t.liquidity_usd:,.0f} | age {t.age_minutes:.0f}m | "
            f"top-10 holders {t.top10_holders_pct:.1f}% | LP locked {t.lp_burned_pct:.0f}%")
    body = "PASSES the basic checks" if v.ok else "REJECT: " + "; ".join(v.reasons)
    return f"{head}\n{body}\nNot financial advice. Stealth rugs can pass every check.\nhttps://dexscreener.com/solana/{addr}"


def _api(token, method, **params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/{method}", data, timeout=70) as r:
        return json.load(r)


def run():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    offset, last = 0, {}
    while True:
        try:
            for u in _api(token, "getUpdates", offset=offset, timeout=50).get("result", []):
                offset = u["update_id"] + 1
                m = u.get("message") or {}
                chat = (m.get("chat") or {}).get("id")
                if not chat or time.time() - last.get(chat, 0) < 3:      # 1 request / 3 s / chat
                    continue
                last[chat] = time.time()
                _api(token, "sendMessage", chat_id=chat, text=handle(m.get("text"), live.fetch_token),
                     disable_web_page_preview="true")
        except Exception as e:
            print("poll error:", e)
            time.sleep(5)


if __name__ == "__main__":
    run()
