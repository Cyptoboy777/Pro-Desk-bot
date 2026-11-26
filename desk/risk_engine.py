"""Risk engine v2: explainable, configurable scoring of a Solana token. Read-only, no execution.

    assess(row) -> {"risk_score": 0-100, "passed": bool, "failed_reasons": [...],
                    "feature_vector": {...}, "components": {...}, "engine_version": "2.0.0"}

Design rules
- Hard rules first (authorities, danger flags, LP, minimum liquidity). Any hard failure means `passed=False`.
- Then additive penalty points in three components: maturity, concentration, liquidity quality.
  Lower score is safer. A token passes when it has no hard failure and score <= pass_threshold.
- Unknown features (None) add no points and are listed in `feature_vector["unknown"]`; they never count as safe evidence.
- Honest naming: DexScreener exposes transaction COUNTS, not unique wallets, so the velocity signal is a
  buy/sell transaction ratio. "Early-block sniper clustering" has no verified data source here; the
  RugCheck insider-network count is used as a proxy for bundled/clustered wallets.

Defaults were designed on tokens first seen before 2026-11-24 and then LOCKED. See METHODOLOGY.md.
"""
from dataclasses import dataclass, asdict, fields

ENGINE_VERSION = "2.0.0"


@dataclass
class RiskConfig:
    # hard rules
    min_liq: float = 10_000
    min_lp: float = 90
    require_authorities_disabled: bool = True
    reject_on_flags: bool = True
    # maturity: age (minutes) below age_bounds[i] costs age_pts[i] (first match wins)
    age_bounds: tuple = (30, 60, 120, 240)
    age_pts: tuple = (40, 30, 20, 10)
    # concentration: non-pool top-10 share (%) at or above top10_bounds[i] costs top10_pts[i] (highest match wins)
    top10_bounds: tuple = (15, 25, 40)
    top10_pts: tuple = (10, 20, 30)
    top1_warn: float = 10
    top1_pts: int = 10
    insider_pts: int = 10
    # liquidity quality
    liq_mcap_min: float = 0.03
    liq_mcap_pts: int = 15
    wash_vol_liq: float = 200.0
    wash_pts: int = 10
    sell_heavy_ratio: float = 0.40
    sell_pts: int = 10
    # component caps and decision
    cap_maturity: int = 40
    cap_concentration: int = 30
    cap_liquidity: int = 30
    pass_threshold: int = 20

    def to_dict(self):
        return {k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(self).items()}

    @classmethod
    def from_dict(cls, d):
        names = {f.name for f in fields(cls)}
        return cls(**{k: (tuple(v) if isinstance(v, list) else v) for k, v in d.items() if k in names})


DEFAULT = RiskConfig()


def row_from_token(t):
    """Normalise a desk.models.Token into the snapshot-row shape the engine and the API use."""
    return {"liq": t.liquidity_usd, "vol24": t.volume_24h, "age_min": t.age_minutes, "top10": t.top10_holders_pct,
            "lp": t.lp_burned_pct, "flags": list(t.risk_flags or []), "total_holders": t.total_holders,
            "creator_pct": t.creator_pct, "insiders": t.insider_networks, "mcap": t.mcap, "top1": t.top1_pct,
            "buy_ratio_h1": (t.buys_h1 / (t.buys_h1 + t.sells_h1)
                             if t.buys_h1 is not None and t.sells_h1 is not None and (t.buys_h1 + t.sells_h1) > 0 else None),
            "chg_h1": t.chg_h1, "has_socials": t.has_socials,
            "auth_ok": bool(t.mint_authority_disabled and t.freeze_authority_disabled)}


def feature_vector(r):
    liq, vol, mcap = r.get("liq"), r.get("vol24"), r.get("mcap")
    fv = {"liquidity_usd": liq, "age_min": r.get("age_min"), "top10_pct": r.get("top10"), "top1_pct": r.get("top1"),
          "insiders": r.get("insiders"), "buy_ratio_h1": r.get("buy_ratio_h1"), "lp_locked_pct": r.get("lp"),
          "vol_liq": (vol / max(liq, 1)) if vol is not None and liq is not None else None,
          "liq_mcap": (liq / mcap) if liq is not None and mcap else None,
          "total_holders": r.get("total_holders"), "creator_pct": r.get("creator_pct"), "chg_h1": r.get("chg_h1")}
    fv["unknown"] = sorted(k for k, v in fv.items() if v is None)
    return fv


def _auth_ok(r):
    if r.get("auth_ok") is not None:                                   # recorded directly (newer rows)
        return bool(r["auth_ok"])
    return not any("authority" in x for x in (r.get("reasons") or []))  # older rows: derive from v1 reasons


def assess(r, cfg=DEFAULT):
    fv = feature_vector(r)
    hard, pts, why = [], {"maturity": 0, "concentration": 0, "liquidity": 0}, []
    if cfg.require_authorities_disabled and not _auth_ok(r):
        hard.append("mint or freeze authority still enabled")
    if cfg.reject_on_flags and r.get("flags"):
        hard.extend(str(f) for f in r["flags"])
    if fv["lp_locked_pct"] is not None and fv["lp_locked_pct"] < cfg.min_lp:
        hard.append(f"LP locked only {fv['lp_locked_pct']:.0f}% (min {cfg.min_lp:.0f}%)")
    if fv["liquidity_usd"] is None or fv["liquidity_usd"] < cfg.min_liq:
        hard.append(f"liquidity ${(fv['liquidity_usd'] or 0):,.0f} below minimum ${cfg.min_liq:,.0f}")

    a = fv["age_min"]
    if a is not None:
        for b, p in zip(cfg.age_bounds, cfg.age_pts):
            if a < b:
                pts["maturity"] += p
                why.append(f"token age {a:.0f}m is under {b}m: +{p}")
                break
    t10 = fv["top10_pct"]
    if t10 is not None:
        hit = [(b, p) for b, p in zip(cfg.top10_bounds, cfg.top10_pts) if t10 >= b]
        if hit:
            b, p = hit[-1]
            pts["concentration"] += p
            why.append(f"top-10 holders hold {t10:.0f}% (>= {b}%): +{p}")
    if fv["top1_pct"] is not None and fv["top1_pct"] >= cfg.top1_warn:
        pts["concentration"] += cfg.top1_pts
        why.append(f"single wallet holds {fv['top1_pct']:.1f}% (>= {cfg.top1_warn}%): +{cfg.top1_pts}")
    if (fv["insiders"] or 0) > 0:
        pts["concentration"] += cfg.insider_pts
        why.append(f"{fv['insiders']} insider-linked wallets (bundle proxy): +{cfg.insider_pts}")
    if fv["liq_mcap"] is not None and fv["liq_mcap"] < cfg.liq_mcap_min:
        pts["liquidity"] += cfg.liq_mcap_pts
        why.append(f"liquidity is {fv['liq_mcap']:.1%} of market cap (< {cfg.liq_mcap_min:.0%}): +{cfg.liq_mcap_pts}")
    if fv["vol_liq"] is not None and fv["vol_liq"] >= cfg.wash_vol_liq:
        pts["liquidity"] += cfg.wash_pts
        why.append(f"24h volume is {fv['vol_liq']:.0f}x liquidity (wash-trading pattern): +{cfg.wash_pts}")
    if fv["buy_ratio_h1"] is not None and fv["buy_ratio_h1"] < cfg.sell_heavy_ratio:
        pts["liquidity"] += cfg.sell_pts
        why.append(f"only {fv['buy_ratio_h1']:.0%} of last-hour transactions are buys: +{cfg.sell_pts}")

    comp = {"maturity": min(pts["maturity"], cfg.cap_maturity), "concentration": min(pts["concentration"], cfg.cap_concentration),
            "liquidity": min(pts["liquidity"], cfg.cap_liquidity)}
    score = min(100, sum(comp.values()))
    over = score > cfg.pass_threshold
    reasons = hard + why
    if over and not hard:
        reasons.insert(0, f"risk score {score} is above the pass threshold {cfg.pass_threshold}")
    return {"risk_score": score, "passed": not hard and not over, "failed_reasons": reasons,
            "feature_vector": fv, "components": comp, "engine_version": ENGINE_VERSION}
