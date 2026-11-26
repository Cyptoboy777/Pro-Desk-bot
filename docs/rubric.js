/* Risk rubric v2 - JavaScript twin of desk/risk_engine.py. Same config, same arithmetic; tests/test_rubric_parity.py
   keeps the two identical. Pure functions: no network, no wallet, no execution. */
(function (root) {
  const DEFAULT = {
    min_liq: 10000, min_lp: 90, require_authorities_disabled: true, reject_on_flags: true,
    age_bounds: [30, 60, 120, 240], age_pts: [40, 30, 20, 10],
    top10_bounds: [15, 25, 40], top10_pts: [10, 20, 30], top1_warn: 10, top1_pts: 10, insider_pts: 10,
    liq_mcap_min: 0.03, liq_mcap_pts: 15, wash_vol_liq: 200, wash_pts: 10, sell_heavy_ratio: 0.4, sell_pts: 10,
    cap_maturity: 40, cap_concentration: 30, cap_liquidity: 30, pass_threshold: 20
  };
  const nn = v => v !== null && v !== undefined;
  function featureVector(r) {
    const liq = r.liq, vol = r.vol24, mcap = r.mcap;
    const fv = {
      liquidity_usd: nn(liq) ? liq : null, age_min: nn(r.age_min) ? r.age_min : null, top10_pct: nn(r.top10) ? r.top10 : null,
      top1_pct: nn(r.top1) ? r.top1 : null, insiders: nn(r.insiders) ? r.insiders : null,
      buy_ratio_h1: nn(r.buy_ratio_h1) ? r.buy_ratio_h1 : null, lp_locked_pct: nn(r.lp) ? r.lp : null,
      vol_liq: nn(vol) && nn(liq) ? vol / Math.max(liq, 1) : null, liq_mcap: nn(liq) && mcap ? liq / mcap : null,
      total_holders: nn(r.total_holders) ? r.total_holders : null, creator_pct: nn(r.creator_pct) ? r.creator_pct : null,
      chg_h1: nn(r.chg_h1) ? r.chg_h1 : null
    };
    fv.unknown = Object.keys(fv).filter(k => fv[k] === null).sort();
    return fv;
  }
  function authOk(r) {
    if (nn(r.auth_ok)) return !!r.auth_ok;
    return !(r.reasons || []).some(x => x.includes("authority"));
  }
  const fix = (x, d) => Number(x).toFixed(d);
  function assess(r, cfg) {
    cfg = Object.assign({}, DEFAULT, cfg || {});
    const fv = featureVector(r), hard = [], pts = { maturity: 0, concentration: 0, liquidity: 0 }, why = [];
    if (cfg.require_authorities_disabled && !authOk(r)) hard.push("mint or freeze authority still enabled");
    if (cfg.reject_on_flags && r.flags && r.flags.length) r.flags.forEach(f => hard.push(String(f)));
    if (fv.lp_locked_pct !== null && fv.lp_locked_pct < cfg.min_lp) hard.push(`LP locked only ${fix(fv.lp_locked_pct, 0)}% (min ${fix(cfg.min_lp, 0)}%)`);
    if (fv.liquidity_usd === null || fv.liquidity_usd < cfg.min_liq) hard.push(`liquidity $${Math.round(fv.liquidity_usd || 0).toLocaleString("en-US")} below minimum $${Math.round(cfg.min_liq).toLocaleString("en-US")}`);
    const a = fv.age_min;
    if (a !== null) for (let i = 0; i < cfg.age_bounds.length; i++) if (a < cfg.age_bounds[i]) { pts.maturity += cfg.age_pts[i]; why.push(`token age ${fix(a, 0)}m is under ${cfg.age_bounds[i]}m: +${cfg.age_pts[i]}`); break; }
    const t10 = fv.top10_pct;
    if (t10 !== null) {
      let hit = null;
      cfg.top10_bounds.forEach((b, i) => { if (t10 >= b) hit = [b, cfg.top10_pts[i]]; });
      if (hit) { pts.concentration += hit[1]; why.push(`top-10 holders hold ${fix(t10, 0)}% (>= ${hit[0]}%): +${hit[1]}`); }
    }
    if (fv.top1_pct !== null && fv.top1_pct >= cfg.top1_warn) { pts.concentration += cfg.top1_pts; why.push(`single wallet holds ${fix(fv.top1_pct, 1)}% (>= ${cfg.top1_warn}%): +${cfg.top1_pts}`); }
    if ((fv.insiders || 0) > 0) { pts.concentration += cfg.insider_pts; why.push(`${fv.insiders} insider-linked wallets (bundle proxy): +${cfg.insider_pts}`); }
    if (fv.liq_mcap !== null && fv.liq_mcap < cfg.liq_mcap_min) { pts.liquidity += cfg.liq_mcap_pts; why.push(`liquidity is ${fix(fv.liq_mcap * 100, 1)}% of market cap (< ${Math.round(cfg.liq_mcap_min * 100)}%): +${cfg.liq_mcap_pts}`); }
    if (fv.vol_liq !== null && fv.vol_liq >= cfg.wash_vol_liq) { pts.liquidity += cfg.wash_pts; why.push(`24h volume is ${fix(fv.vol_liq, 0)}x liquidity (wash-trading pattern): +${cfg.wash_pts}`); }
    if (fv.buy_ratio_h1 !== null && fv.buy_ratio_h1 < cfg.sell_heavy_ratio) { pts.liquidity += cfg.sell_pts; why.push(`only ${fix(fv.buy_ratio_h1 * 100, 0)}% of last-hour transactions are buys: +${cfg.sell_pts}`); }
    const comp = { maturity: Math.min(pts.maturity, cfg.cap_maturity), concentration: Math.min(pts.concentration, cfg.cap_concentration), liquidity: Math.min(pts.liquidity, cfg.cap_liquidity) };
    const score = Math.min(100, comp.maturity + comp.concentration + comp.liquidity), over = score > cfg.pass_threshold;
    let reasons = hard.concat(why);
    if (over && !hard.length) reasons.unshift(`risk score ${score} is above the pass threshold ${cfg.pass_threshold}`);
    return { risk_score: score, passed: !hard.length && !over, failed_reasons: reasons, feature_vector: fv, components: comp, engine_version: "2.0.0" };
  }
  const api = { DEFAULT, assess, featureVector };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Rubric = api;
})(typeof self !== "undefined" ? self : this);
