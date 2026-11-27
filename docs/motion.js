/* Motion layer for the research dashboard: vanilla JS, no build step, read-only.
   Honors prefers-reduced-motion (everything renders in its final state, nothing animates). */
(function (root) {
  const RM = root.matchMedia && root.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (id) => document.getElementById(id);
  const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
  const ease = (t) => 1 - Math.pow(1 - t, 3);

  /* number tween: Motion.tween(node, to, {fmt, ms}) */
  const state = new WeakMap();
  function tween(node, to, o) {
    o = o || {}; const fmt = o.fmt || ((v) => Math.round(v).toLocaleString("en-US"));
    if (RM || !isFinite(to)) { node.textContent = fmt(to); state.set(node, to); return; }
    const from = state.has(node) ? state.get(node) : 0, ms = o.ms || 700, t0 = performance.now();
    state.set(node, to);
    (function step(now) {
      const k = Math.min(1, (now - t0) / ms);
      node.textContent = fmt(from + (to - from) * ease(k));
      if (k < 1 && state.get(node) === to) requestAnimationFrame(step);
    })(t0);
  }

  /* scroll reveal with stagger */
  function reveal(selector) {
    const items = [].slice.call(document.querySelectorAll(selector));
    if (RM || !("IntersectionObserver" in root)) { items.forEach((x) => x.classList.add("in")); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    }), { threshold: 0.08 });
    items.forEach((x, i) => { x.style.transitionDelay = Math.min(i % 4, 3) * 70 + "ms"; io.observe(x); });
  }

  /* pointer spotlight on panels */
  function spotlight(selector) {
    if (RM) return;
    document.querySelectorAll(selector).forEach((p) => p.addEventListener("pointermove", (e) => {
      const r = p.getBoundingClientRect();
      p.style.setProperty("--mx", e.clientX - r.left + "px"); p.style.setProperty("--my", e.clientY - r.top + "px");
    }));
  }

  /* hero constellation: drifting "tokens"; pauses when hidden */
  function hero(canvas) {
    const ctx = canvas.getContext("2d"); let W = 0, H = 0, pts = [], run = true, mouse = null;
    const dpr = Math.min(root.devicePixelRatio || 1, 2);
    function size() {
      const r = canvas.getBoundingClientRect(); W = r.width; H = r.height;
      canvas.width = W * dpr; canvas.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.max(18, Math.min(56, Math.round(W * H / 14000)));
      pts = []; for (let i = 0; i < n; i++) pts.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35, r: 1 + Math.random() * 2, g: Math.random() < .22 });
    }
    function draw() {
      ctx.clearRect(0, 0, W, H);
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i];
        if (!RM) { p.x += p.vx; p.y += p.vy; if (p.x < 0 || p.x > W) p.vx *= -1; if (p.y < 0 || p.y > H) p.vy *= -1; }
        for (let j = i + 1; j < pts.length; j++) {
          const q = pts[j], d = Math.hypot(p.x - q.x, p.y - q.y);
          if (d < 120) { ctx.strokeStyle = "rgba(154,140,255," + (0.22 * (1 - d / 120)) + ")"; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke(); }
        }
        if (mouse) { const d = Math.hypot(p.x - mouse.x, p.y - mouse.y); if (d < 140 && !RM) { p.x += (mouse.x - p.x) * .004; p.y += (mouse.y - p.y) * .004; } }
        ctx.fillStyle = p.g ? "rgba(74,222,128,.9)" : "rgba(154,140,255,.8)"; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill();
      }
      if (run && !RM) requestAnimationFrame(draw);
    }
    canvas.parentNode.addEventListener("pointermove", (e) => { const r = canvas.getBoundingClientRect(); mouse = { x: e.clientX - r.left, y: e.clientY - r.top }; });
    canvas.parentNode.addEventListener("pointerleave", () => { mouse = null; });
    document.addEventListener("visibilitychange", () => { run = !document.hidden; if (run) draw(); });
    root.addEventListener("resize", size); size(); draw();
  }

  /* interactive pipeline flow with a travelling pulse; click a step to pin it */
  function flow(host, s) {
    const cov = ((s.time_series_coverage || {}).windows) || {}, w24 = cov["T+24h"] || {}, w30 = cov["T+30m"] || {};
    const pv = (s.pass_vs_reject_24h || {}).v2_shadow || {};
    const steps = [
      ["Discover", "New Solana token profiles from DexScreener.", s.tokens_recorded + " tokens recorded so far"],
      ["Snapshot", "Price, liquidity, volume, holders, authorities and LP lock at first sighting (RugCheck + DexScreener).", "append-only rows on the live-data branch"],
      ["Score", "v1 rules (live) and the v2 rubric 0-100 (shadow) judge it with written reasons.", pv.pass ? "v2 passes " + pv.pass.n + " of " + (pv.pass.n + pv.reject.n) + " judged tokens" : "rubric v2.0.0"],
      ["Wait", "Revisit at T+30m, 2h, 6h and 24h and record liquidity, holder and volume changes.", "T+30m seen " + (w30.observed || 0) + "/" + (w30.expected || 0) + " · T+24h seen " + (w24.observed || 0) + "/" + (w24.expected || 0)],
      ["Judge", "Bad = vanished, or liquidity or price halved. Wilson 95% intervals, never a bare percentage.", s.judged_24h + " judged at 24h · status " + s.edge_status],
      ["Publish", "Static versioned JSON + this page. Zero wallet, zero signing, enforced by CI.", "generated " + new Date(s.generated_at * 1000).toUTCString().slice(5, 22) + " UTC"],
    ];
    host.textContent = "";
    const track = el("div", "fl-track"), rail = el("div", "fl-rail"), pulse = el("i", "fl-pulse"); rail.appendChild(pulse); track.appendChild(rail);
    const btns = steps.map((st, i) => { const b = el("button", "fl-step"); b.type = "button"; b.setAttribute("aria-pressed", "false");
      b.appendChild(el("span", "fl-n", String(i + 1))); b.appendChild(el("span", "fl-t", st[0])); track.appendChild(b); return b; });
    const info = el("div", "fl-info"), it = el("div", "fl-it"), id = el("div", "sub"), iv = el("div", "fl-iv");
    info.appendChild(it); info.appendChild(id); info.appendChild(iv);
    const ctl = el("button", "fl-play", RM ? "Play" : "Pause"); ctl.type = "button";
    host.appendChild(track); host.appendChild(info); host.appendChild(ctl);
    let cur = 0, timer = null, playing = !RM;
    function set(i) {
      cur = i; btns.forEach((b, k) => { b.classList.toggle("on", k === i); b.classList.toggle("done", k < i); b.setAttribute("aria-pressed", String(k === i)); });
      pulse.style.setProperty("--p", (i / (steps.length - 1)) * 100 + "%");
      info.classList.remove("swap"); void info.offsetWidth; info.classList.add("swap");
      it.textContent = (i + 1) + ". " + steps[i][0]; id.textContent = steps[i][1]; iv.textContent = steps[i][2];
    }
    function tick() { set((cur + 1) % steps.length); }
    function play() { if (timer) clearInterval(timer); timer = setInterval(tick, 2400); playing = true; ctl.textContent = "Pause"; }
    function stop() { if (timer) clearInterval(timer); timer = null; playing = false; ctl.textContent = "Play"; }
    btns.forEach((b, i) => b.addEventListener("click", () => { stop(); set(i); }));
    ctl.addEventListener("click", () => (playing ? stop() : play()));
    set(0); if (playing) play();
  }

  /* token life replay: scrub or play through REAL recorded outcomes (entry, +1h, +6h, +24h) */
  function replay(host, scans) {
    const list = (scans || []).filter((x) => x.outcomes && (x.outcomes["1h"] || x.outcomes["6h"] || x.outcomes["24h"])).slice(0, 40);
    host.textContent = "";
    if (!list.length) { host.appendChild(el("div", "sub", "No token has follow-up outcomes yet. Replays appear after the first scored runs.")); return; }
    const sel = el("select"); sel.setAttribute("aria-label", "Recorded token");
    list.forEach((x, i) => { const o = el("option", null, (x.symbol || "?") + " · " + (x.v2_passed ? "v2 pass" : "v2 reject") + " · score " + x.v2_risk_score); o.value = i; sel.appendChild(o); });
    const cv = el("canvas", "rp-cv"); cv.height = 150;
    const rng = el("input"); rng.type = "range"; rng.min = 0; rng.max = 3; rng.step = 0.01; rng.value = 3; rng.setAttribute("aria-label", "Time since first sighting");
    const play = el("button", null, "Replay"); play.type = "button";
    const row = el("div", "row"); row.appendChild(sel); row.appendChild(play);
    const read = el("div", "rp-read"), why = el("div", "sub");
    host.appendChild(row); host.appendChild(cv); host.appendChild(rng); host.appendChild(read); host.appendChild(why);
    const labels = ["first seen", "+1h", "+6h", "+24h"];
    function series(x) {
      const pts = [{ t: 0, v: 0, gone: false }]; [["1h", 1], ["6h", 2], ["24h", 3]].forEach(([k, t]) => { const o = x.outcomes[k]; if (o) pts.push({ t, v: o.gone ? -100 : o.price_change_pct, gone: o.gone, liq: o.liq }); });
      return pts;
    }
    function draw(x, pos) {
      const W = cv.clientWidth || 300, H = 150, d = Math.min(root.devicePixelRatio || 1, 2); cv.width = W * d; const c = cv.getContext("2d"); c.setTransform(d, 0, 0, d, 0, 0); c.clearRect(0, 0, W, H);
      const pts = series(x), vals = pts.map((p) => p.v), lo = Math.min(-10, ...vals), hi = Math.max(10, ...vals), X = (t) => 12 + t / 3 * (W - 24), Y = (v) => H - 18 - (v - lo) / (hi - lo) * (H - 36);
      c.strokeStyle = "#363641"; c.setLineDash([4, 4]); c.beginPath(); c.moveTo(0, Y(0)); c.lineTo(W, Y(0)); c.stroke(); c.setLineDash([]);
      c.fillStyle = "#9392a0"; c.font = "11px ui-monospace,monospace"; labels.forEach((l, i) => c.fillText(l, Math.min(W - 52, Math.max(2, X(i) - 20)), H - 3));
      let last = pts[0], col = "#4ade80";
      c.lineWidth = 2; c.beginPath(); c.moveTo(X(0), Y(0));
      for (let i = 1; i < pts.length; i++) {
        const p = pts[i], prev = pts[i - 1]; if (pos <= prev.t) break;
        const k = Math.min(1, (pos - prev.t) / (p.t - prev.t)), t = prev.t + (p.t - prev.t) * k, v = prev.v + (p.v - prev.v) * k;
        c.lineTo(X(t), Y(v)); last = { t, v, gone: p.gone, liq: p.liq, at: k >= 1 ? p : prev };
      }
      col = last.v < -50 ? "#ff6b6b" : last.v < 0 ? "#f3da4f" : "#4ade80"; c.strokeStyle = col; c.stroke();
      c.fillStyle = col; c.beginPath(); c.arc(X(last.t), Y(last.v), 5, 0, 6.283); c.fill();
      read.textContent = labels[Math.min(3, Math.round(pos))] + ": " + (last.gone ? "pair gone (counted as -100%)" : (last.v >= 0 ? "+" : "") + Number(last.v).toFixed(1) + "% vs first sighting") + (last.liq != null && !last.gone ? " · liquidity $" + Math.round(last.liq).toLocaleString("en-US") : "");
      read.style.color = col;
    }
    let raf = null;
    function show() { const x = list[+sel.value]; draw(x, +rng.value); why.textContent = "Rubric v2 said: " + (x.failed_reasons[0] || "no risk points") + (x.bad_24h == null ? "" : " · judged at 24h: " + (x.bad_24h ? "BAD" : "survived")); }
    function go() { if (raf) cancelAnimationFrame(raf); if (RM) { rng.value = 3; show(); return; } const t0 = performance.now(), ms = 4200; rng.value = 0;
      (function f(n) { const k = Math.min(1, (n - t0) / ms); rng.value = 3 * ease(k); show(); if (k < 1) raf = requestAnimationFrame(f); })(t0); }
    sel.addEventListener("change", go); rng.addEventListener("input", () => { if (raf) cancelAnimationFrame(raf); show(); }); play.addEventListener("click", go);
    root.addEventListener("resize", show); go();
  }

  root.Motion = { tween, reveal, spotlight, hero, flow, replay, reduced: RM };
})(typeof self !== "undefined" ? self : this);
