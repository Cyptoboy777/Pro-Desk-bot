"""Push new paper-desk decisions to Telegram (read-only: it only SENDS messages).

    TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... python3 notify.py

Without both variables it does nothing except advance its marker. The marker file
(data/notified.txt) holds how many event lines were already handled; if it does not exist yet,
history is skipped so enabling alerts never floods your phone.
"""
import json
import os
import urllib.parse
import urllib.request

EVENTS, MARKER = "data/paper_events.jsonl", "data/notified.txt"
SHOW = ("ENTER", "EXIT", "HALT", "PAUSE")


def fmt(e):
    t = e.get("ts", "")
    if e["kind"] == "ENTER":
        return f"BUY (paper) {e['sym']} | {e.get('size_pct', '?')}% of equity | {e['reason']} | {t} UTC"
    if e["kind"] == "EXIT":
        return f"SELL (paper) {e['sym']} | {e.get('pnl', 0):+.2f} USD | {e['reason']} | {t} UTC"
    return f"{e['kind']}: {e['reason']} | {t} UTC"


def pending(events_path=EVENTS, marker_path=MARKER):
    lines = [l for l in open(events_path).read().splitlines() if l.strip()] if os.path.exists(events_path) else []
    if not os.path.exists(marker_path):
        return [], len(lines)                       # first run: skip history
    done = int(open(marker_path).read().strip() or 0)
    ev = [json.loads(l) for l in lines[done:]]
    return [e for e in ev if e["kind"] in SHOW], len(lines)


def send(token, chat, text):
    data = urllib.parse.urlencode({"chat_id": chat, "text": text, "disable_web_page_preview": "true"}).encode()
    urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data, timeout=20).read()


def run(events_path=EVENTS, marker_path=MARKER, token=None, chat=None, sender=send):
    ev, total = pending(events_path, marker_path)
    sent = 0
    if token and chat and ev:
        for i in range(0, len(ev), 8):
            body = "\n".join(fmt(e) for e in ev[i:i + 8]) + "\n\nPaper trading only. Not advice."
            sender(token, chat, body[:4000])
            sent += len(ev[i:i + 8])
    os.makedirs(os.path.dirname(marker_path) or ".", exist_ok=True)
    open(marker_path, "w").write(str(total))
    return sent


if __name__ == "__main__":
    t, c = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    n = run(token=t, chat=c)
    print(f"sent {n} event(s)" if t and c else "alerts off (no Telegram secrets set)")
