"""Export real paper runs (final config) as JSON for the dashboard."""
import json
from dataclasses import replace, asdict
from desk.sim import SimMarket
from desk.broker import PaperBroker
from desk.head import HeadOfDesk, Config
from experiments import HOLDOUT

FINAL = replace(Config(), guard_n=3, cooldown=10, edge_n=8)


def run(seed, cfg=FINAL, **kw):
    m, b = SimMarket(seed=seed, **kw), PaperBroker(1000.0)
    h = HeadOfDesk(b, cfg=cfg)
    toks = []
    while not m.done():
        toks = m.tick()
        h.step(m.t, toks)
    last = {t.mint: t for t in toks}
    for mint in list(b.positions):
        pnl = b.sell(last[mint], m.t, "end of run")
        h._ev(m.t, "EXIT", last[mint].symbol, "end of run", pnl=round(pnl, 2))
        h.closed.append(pnl)
    h.curve[-1] = round(b.cash, 2)
    return {"seed": seed, "start": 1000.0, "final": round(b.cash, 2), "events": h.events, "curve": h.curve,
            "stats": h.stats, "needs_human": h.needs_human}


if __name__ == "__main__":
    runs = sorted((run(s) for s in HOLDOUT), key=lambda r: r["final"])
    pick = {"worst": runs[0], "median": runs[len(runs) // 2], "best": runs[-1]}
    for k, r in pick.items():
        r["label"] = k
        print(k, r["seed"], r["final"], len(r["events"]))
    json.dump({"cfg": asdict(FINAL), "runs": list(pick.values())}, open("dashboard_data.json", "w"))
