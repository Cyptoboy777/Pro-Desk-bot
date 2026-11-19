"""Paper-trading experiment harness.

Discipline: tune on TRAIN seeds, report on HOLDOUT seeds the fixes never saw.
    python experiments.py
"""
import statistics
from dataclasses import replace

from desk.sim import SimMarket
from desk.broker import PaperBroker
from desk.head import HeadOfDesk, Config

TRAIN = range(1, 101)
HOLDOUT = range(1001, 1101)


def run_one(cfg, seed, stealth=0.30, drift=0.004):
    mkt, b = SimMarket(seed=seed, stealth=stealth, drift=drift), PaperBroker()
    h = HeadOfDesk(b, cfg=cfg)
    toks = []
    while not mkt.done():
        toks = mkt.tick()
        h.step(mkt.t, toks)
    last = {t.mint: t for t in toks}
    for m in list(b.positions):
        b.sell(last[m], mkt.t, "end of run")
    final = b.cash
    peak, mdd = 0.0, 0.0
    for e in h.curve:
        peak = max(peak, e)
        mdd = max(mdd, (peak - e) / peak if peak else 0)
    n = b.db.execute("select count(*) from trades where side='SELL'").fetchone()[0]
    return {"ret": (final / b.start - 1) * 100, "mdd": mdd * 100, "trades": n,
            "rugs": h.stats["rug_exits"], "halted": h.halted}


def evaluate(cfg, seeds, **kw):
    rs = [run_one(cfg, s, **kw) for s in seeds]
    r = [x["ret"] for x in rs]
    q = sorted(r)
    return {"mean": statistics.mean(r), "median": statistics.median(r), "p10": q[len(q) // 10],
            "worst": q[0], "lose%": 100 * sum(x < 0 for x in r) / len(r),
            "mdd": statistics.mean(x["mdd"] for x in rs), "trades": statistics.mean(x["trades"] for x in rs),
            "rugs": statistics.mean(x["rugs"] for x in rs)}


def row(name, cfg, **kw):
    a, h = evaluate(cfg, TRAIN, **kw), evaluate(cfg, HOLDOUT, **kw)
    print(f"{name:34s} | train mean {a['mean']:+6.2f}% lose {a['lose%']:3.0f}% | "
          f"HOLDOUT mean {h['mean']:+6.2f}% p10 {h['p10']:+6.2f}% worst {h['worst']:+6.2f}% "
          f"lose {h['lose%']:3.0f}% mdd {h['mdd']:4.1f}% trades {h['trades']:4.1f} rugs {h['rugs']:3.1f}")
    return a, h


if __name__ == "__main__":
    base = Config()
    print("== one fix at a time vs baseline (v1: fixed $25 ticket, no protections)")
    row("0 baseline", base)
    row("1 +anti-chase (skip >25% ran)", replace(base, max_chase=0.25))
    row("2 +risk sizing (1% eq at stop)", replace(base, sizing="risk"))
    row("3 +cooldown 10 ticks", replace(base, cooldown=10))
    row("4 +stoploss guard (3 in 20)", replace(base, guard_n=3))
    row("5 +stricter risk (age>=30,top10<=30)", replace(base, min_age=30, max_top10=30))


def sensitivity():
    """Holdout only: does the desk survive when there is NO edge, and keep upside when there is?"""
    cfgs = {
        "baseline": Config(),
        "guard+cooldown": replace(Config(), guard_n=3, cooldown=10),
        "+edge gate": replace(Config(), guard_n=3, cooldown=10, edge_n=8),
        "+edge gate +risk 0.5%": replace(Config(), guard_n=3, cooldown=10, edge_n=8, sizing="risk", risk_pct=0.005),
    }
    print(f"{'market':28s}" + "".join(f"| {k:24s}" for k in cfgs))
    for stealth in (0.1, 0.3):
        for drift in (0.0, 0.004, 0.02):
            out = []
            for cfg in cfgs.values():
                h = evaluate(cfg, HOLDOUT, stealth=stealth, drift=drift)
                out.append(f"{h['mean']:+6.2f}% w{h['worst']:+6.1f}% L{h['lose%']:3.0f}%")
            print(f"stealth {stealth:.1f} drift {drift:.3f}      " + "| ".join(f"{o:23s}" for o in out))
