"""Run the paper-trading desk on the simulated market.

    python run_desk.py            # one run, seed 1
    python run_desk.py --seeds 50 # distribution over 50 different markets
"""
import argparse
import json
import statistics

from desk.sim import SimMarket
from desk.broker import PaperBroker
from desk.head import HeadOfDesk, claude_review


def run(seed, db=":memory:"):
    mkt, broker = SimMarket(seed=seed), PaperBroker(db=db)
    head = HeadOfDesk(broker)
    prices = {}
    while not mkt.done():
        toks = mkt.tick()
        prices = {t.mint: t.price for t in toks}
        head.step(mkt.t, toks)
    # close what is still open at the end so the result is realised
    last = {t.mint: t for t in toks}
    for m in list(broker.positions):
        broker.sell(last[m], mkt.t, "end of run")
    return head.summary(prices), broker


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=1)
    a = ap.parse_args()
    if a.seeds == 1:
        s, b = run(1, db="journal.sqlite")
        print(json.dumps(s, indent=2))
        note = claude_review(json.dumps(s))
        if note:
            print("\nClaude review:\n" + note)
    else:
        rets = [run(sd)[0]["return_pct"] for sd in range(1, a.seeds + 1)]
        print(f"{a.seeds} simulated markets | mean {statistics.mean(rets):+.2f}% | median "
              f"{statistics.median(rets):+.2f}% | worst {min(rets):+.2f}% | best {max(rets):+.2f}% | "
              f"losing runs {sum(r < 0 for r in rets)}/{a.seeds}")
