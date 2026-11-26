"""Build the static, versioned JSON API from the append-only data. Read-only; no network.

    python3 api_export.py --data data/snapshots.jsonl --state data/paper_state.json --out api/v1

Writes summary.json, features.json, recent_scans.json, rubric.json. Plain static files: CORS-friendly on
raw.githubusercontent.com and GitHub Pages. Schema changes bump the /v1/ path, never silently.
"""
import argparse
import json
import math
import os
import time

from collector import load, HORIZONS_H, LATE
from insights import labelled, wilson
from desk.risk_engine import assess, DEFAULT, ENGINE_VERSION

SCHEMA = "1.0"
MIN_GROUP = 30          # per group, before any edge claim is even considered
EDGE_TEXT = {"INSUFFICIENT_DATA": f"fewer than {MIN_GROUP} judged tokens in the pass or reject group: no claim possible",
             "NO_EDGE": "pass-group survival is not separable from reject-group survival (95% Wilson intervals overlap, or pass is worse)",
             "STATISTICAL_EDGE_DETECTED": "pass-group bad-outcome interval lies entirely below the reject group's (descriptive, not a trading claim)"}


def _grp(bads):
    n, k = len(bads), sum(bads)
    lo, hi = wilson(k, n)
    return {"n": n, "bad": k, "survived": n - k, "bad_rate": round(k / n, 4) if n else None,
            "survival_rate": round(1 - k / n, 4) if n else None,
            "bad_ci95": [round(lo, 4), round(hi, 4)] if n else None,
            "survival_ci95": [round(1 - hi, 4), round(1 - lo, 4)] if n else None}


def edge_status(p, r):
    if p["n"] < MIN_GROUP or r["n"] < MIN_GROUP:
        return "INSUFFICIENT_DATA"
    return "STATISTICAL_EDGE_DETECTED" if p["bad_ci95"][1] < r["bad_ci95"][0] else "NO_EDGE"


def _engine_block(data, passed_fn):
    p = _grp([b for e, b in data if passed_fn(e)])
    r = _grp([b for e, b in data if not passed_fn(e)])
    st = edge_status(p, r)
    return {"pass": p, "reject": r, "edge_status": st, "edge_note": EDGE_TEXT[st]}


def _signals(cfg=DEFAULT):
    """Binary 'warning' signals mirroring the rubric. key -> (label, test(entry)->bool|None)."""
    def vl(e):
        return (e.get("vol24") or 0) / max(e["liq"], 1)
    return {
        "age_under_240m": ("Token younger than 4h", lambda e: None if e.get("age_min") is None else e["age_min"] < 240),
        "top10_ge_25": ("Top-10 holders >= 25%", lambda e: None if e.get("top10") is None else e["top10"] >= 25),
        "top1_ge_10": ("Single wallet >= 10%", lambda e: None if e.get("top1") is None else e["top1"] >= cfg.top1_warn),
        "insiders_any": ("Insider-linked wallets present", lambda e: None if e.get("insiders") is None else e["insiders"] > 0),
        "liq_lt_20k": ("Liquidity < $20k", lambda e: e["liq"] < 20_000),
        "liq_mcap_low": ("Liquidity < 3% of market cap", lambda e: None if not e.get("mcap") else e["liq"] / e["mcap"] < cfg.liq_mcap_min),
        "wash_volume": ("24h volume >= 200x liquidity", lambda e: vl(e) >= cfg.wash_vol_liq),
        "sell_heavy": ("Buys < 40% of last-hour trades", lambda e: None if e.get("buy_ratio_h1") is None else e["buy_ratio_h1"] < cfg.sell_heavy_ratio),
        "no_socials": ("No social links", lambda e: None if e.get("has_socials") is None else not e["has_socials"]),
        "v1_rejected": ("Rejected by v1 rules", lambda e: not e["pass"]),
        "v2_rejected": ("Rejected by v2 rules", lambda e: not assess(e)["passed"]),
    }


def _corr(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return None if not sx or not sy else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def features(data):
    total_bad = sum(b for _, b in data)
    out = []
    for key, (label, fn) in _signals().items():
        known = [(fn(e), b) for e, b in data]
        known = [(f, b) for f, b in known if f is not None]
        flagged = [b for f, b in known if f]
        clear = [b for f, b in known if not f]
        k_bad = sum(b for _, b in known)
        tp = sum(flagged)
        prec = tp / len(flagged) if flagged else None
        rec = tp / k_bad if k_bad else None
        c = _corr([1.0 if f else 0.0 for f, _ in known], [1.0 if b else 0.0 for _, b in known])
        out.append({"key": key, "label": label, "n_known": len(known), "n_flagged": len(flagged),
                    "bad_rate_flagged": _grp(flagged)["bad_rate"], "bad_ci95_flagged": _grp(flagged)["bad_ci95"],
                    "bad_rate_clear": _grp(clear)["bad_rate"], "bad_ci95_clear": _grp(clear)["bad_ci95"],
                    "precision": None if prec is None else round(prec, 4), "recall": None if rec is None else round(rec, 4),
                    "correlation_with_bad": None if c is None else round(c, 4),
                    "separates": bool(flagged and clear and (_grp(flagged)["bad_ci95"][0] > _grp(clear)["bad_ci95"][1]
                                                              or _grp(flagged)["bad_ci95"][1] < _grp(clear)["bad_ci95"][0]))})
    out.sort(key=lambda f: -abs(f["correlation_with_bad"] or 0))
    return {"schema": SCHEMA, "horizon_h": 24, "base_bad_rate": round(total_bad / len(data), 4) if data else None,
            "n": len(data), "ranked_by": "abs(correlation_with_bad)",
            "note": "precision = P(bad | flagged); recall = P(flagged | bad). 'separates' means the 95% intervals do not overlap. "
                    "Features are correlated with each other and with market regime; this is not causal.",
            "features": out}


def paper_block(state_path):
    if not os.path.exists(state_path):
        return None
    st = json.load(open(state_path))
    curve = st.get("curve", [])
    eq = curve[-1] if curve else st["start"]
    return {"start": st["start"], "equity": round(eq, 2), "return_pct": round((eq / st["start"] - 1) * 100, 3),
            "runs": st.get("tick"), "open_positions": len(st.get("positions", {})), "curve": [round(x, 2) for x in curve[-500:]],
            "assumptions": "fills use a 0.3% fee plus slippage/price-impact model against real liquidity; no wallet, no orders"}


def build(rows, state_path=None, now=None):
    now = time.time() if now is None else now
    entries = [r for r in rows if r["kind"] == "entry"]
    data = labelled(rows, 24)
    horizons = {}
    for h in HORIZONS_H:
        d = labelled(rows, h)
        horizons[f"{h}h"] = {"judged": len(d), "v1": _engine_block(d, lambda e: e["pass"]),
                             "v2_shadow": _engine_block(d, lambda e: assess(e)["passed"])}
    v1, v2 = horizons["24h"]["v1"], horizons["24h"]["v2_shadow"]
    summary = {"schema": SCHEMA, "generated_at": int(now), "engine_version": ENGINE_VERSION,
               "tokens_recorded": len(entries), "judged_24h": len(data),
               "first_seen": int(min((e["ts"] for e in entries), default=0)) or None,
               "bad_outcome_definition": "within 1.5x the horizon: pair vanished, OR liquidity <= 50% of entry, OR price <= 50% of entry",
               "edge_status": v1["edge_status"], "edge_note": v1["edge_note"],
               "edge_status_v2_shadow": v2["edge_status"], "edge_note_v2_shadow": v2["edge_note"],
               "pass_vs_reject_24h": {"v1": {k: v1[k] for k in ("pass", "reject")}, "v2_shadow": {k: v2[k] for k in ("pass", "reject")}},
               "horizons": horizons, "paper": paper_block(state_path) if state_path else None,
               "disclaimer": "Research telemetry only. Not financial advice. This project never executes trades."}
    recent = []
    outs = {(r["mint"], r["horizon_h"]): r for r in rows if r["kind"] == "outcome"}
    ok24 = {e["mint"]: b for e, b in data}
    for e in sorted(entries, key=lambda x: -x["ts"])[:200]:
        a = assess(e)
        recent.append({"mint": e["mint"], "symbol": e.get("symbol"), "first_seen": int(e["ts"]),
                       "liquidity_usd": e["liq"], "age_min": e.get("age_min"), "top10_pct": e.get("top10"),
                       "v1_passed": e["pass"], "v2_risk_score": a["risk_score"], "v2_passed": a["passed"],
                       "failed_reasons": a["failed_reasons"][:6],
                       "outcomes": {f"{h}h": ({"gone": outs[(e["mint"], h)]["gone"], "liq": outs[(e["mint"], h)]["liq"],
                                               "price_change_pct": round((outs[(e["mint"], h)]["price"] / e["price"] - 1) * 100, 1) if e["price"] else None}
                                              if (e["mint"], h) in outs else None) for h in HORIZONS_H},
                       "bad_24h": ok24.get(e["mint"])})
    return {"summary": summary, "features": features(data),
            "recent_scans": {"schema": SCHEMA, "generated_at": int(now), "count": len(recent), "scans": recent},
            "rubric": {"schema": SCHEMA, "engine_version": ENGINE_VERSION, "config": DEFAULT.to_dict(),
                       "note": "Defaults designed on tokens first seen before 2026-11-24, then locked. See METHODOLOGY.md."}}


def write(out_dir, built):
    os.makedirs(out_dir, exist_ok=True)
    for name, obj in built.items():
        with open(os.path.join(out_dir, name + ".json"), "w") as f:
            json.dump(obj, f, separators=(",", ":"))
    # dataset for the in-browser simulator: only fields needed, 24h-labelled rows
    return list(built)


def dataset(rows):
    keys = ("mint", "symbol", "ts", "price", "liq", "vol24", "age_min", "top10", "lp", "mcap", "top1", "insiders", "buy_ratio_h1",
            "total_holders", "creator_pct", "chg_h1", "has_socials", "auth_ok", "flags", "pass")
    outs = {(r["mint"], r["horizon_h"]): r for r in rows if r["kind"] == "outcome"}
    lab = {e["mint"]: b for e, b in labelled(rows, 24)}
    res = []
    for e in (r for r in rows if r["kind"] == "entry"):
        d = {k: e.get(k) for k in keys}
        o = outs.get((e["mint"], 24))
        d["bad_24h"] = lab.get(e["mint"])
        d["ret_24h"] = (round(o["price"] / e["price"] - 1, 4) if o and e["price"] and not o["gone"] and d["bad_24h"] is not None else (-1.0 if o and o["gone"] and d["bad_24h"] is not None else None))
        res.append(d)
    return {"schema": SCHEMA, "count": len(res), "rows": res}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/snapshots.jsonl")
    ap.add_argument("--state", default="data/paper_state.json")
    ap.add_argument("--out", default="api/v1")
    a = ap.parse_args()
    rows = load(a.data)
    built = build(rows, a.state)
    built["dataset"] = dataset(rows)
    print("wrote", ", ".join(write(a.out, built)), "->", a.out)
