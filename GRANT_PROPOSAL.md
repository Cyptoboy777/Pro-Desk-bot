# Grant proposal: Open Solana Risk Telemetry Infrastructure

**Requested:** $3,000–$5,000 USDG, three two-week milestones. **License:** MIT. **Repository:** https://github.com/Cyptoboy777/Pro-Desk-bot

**Author:** Chapala Narendra Varma (cryptoboy777) | **GitHub:** https://github.com/Cyptoboy777 | **X:** @Cryptotelugu12 | **LinkedIn:** https://www.linkedin.com/in/narendra-varma-sodexmod

## Public-good objective
Build and maintain open, reproducible, read-only telemetry for early Solana token markets. The deliverable is durable public data, schemas, statistical reporting and developer interfaces, not trading execution or claims of predictive performance.

**Evidence status: `NO_EDGE`.** On 251 tokens judged at 24h (547 recorded), tokens that passed the basic static checks went bad more often (41/49 = 84%) than tokens the same rules rejected (77/202 = 38%). The v2 shadow rubric does not separate survivors from rugs either, and the held-out window (tokens first seen on/after 2026-11-24, 50 judged) is too small to conclude anything. The proposal funds the measurement infrastructure, not a claimed signal.

## Completed foundations (already in the repository, verifiable)
- **v2 shadow risk rubric** (`desk/risk_engine.py`): explainable 0–100 score with hard rules and capped maturity / concentration / liquidity components, run in shadow mode next to the live v1 rules.
- **Python/JS parity tests**: `docs/rubric.js` must give identical scores and reasons to the Python engine (300 randomized cases under Node 22).
- **Zero-wallet CI guard** (`tests/test_safety_policy.py`): fails the build on private-key, seed-phrase, signing, swap or wallet-connect patterns in any `.py/.js/.html/.yml/.json` file, on unapproved workflow secrets and on unapproved network hosts.
- **547-token collector**: append-only snapshots on the `live-data` branch via GitHub Actions, with +1h/+6h/+24h outcomes and (new) T+30m/T+2h/T+6h time-window snapshots for tokens recorded since they were added.
- **Static JSON API** (`docs/api/v1/`: summary, features, recent_scans, rubric, dataset, actions) with Wilson 95% intervals, per-signal sample status, lift, Fisher exact p-values, an explicit out-of-time block and time-series coverage.
- **Read-only SDKs** (JS and Python) with TTL caching and schema validation, a research dashboard with filter simulator and token inspector, `REPORT.md` generator, and a reference read-only risk-check server (`sdk/action_server.py`).

## Planned grant milestones (not yet done)

### Milestone 1 (weeks 1–2): 1,500+ token multi-snapshot longitudinal corpus
- Run collection at a steadier cadence and add retries so the T+30m, T+2h, T+6h and T+24h observations actually exist for most tokens (today the schedule is best effort and those windows are mostly empty).
- Grow to 1,500+ recorded tokens with per-token snapshot series; publish a versioned dataset release with schema and migration notes. No backfilled or fabricated observations.
- **Acceptance:** coverage table in `summary.json` shows few missing observations per window; CI safety guard green.

### Milestone 2 (weeks 3–4): hosted Solana Actions/Blinks risk-check edge worker
- Deploy the reference server as a small hosted read-only worker that serves `/api/v1/actions/risk-check?mint=…` and `/actions.json` (today only the routing file and a local reference server exist; static GitHub Pages cannot run the dynamic route).
- Validate against the Solana Actions specification and extend the CI guard to the worker. It returns an informational risk report only and never builds, requests or signs a transaction.
- **Acceptance:** public endpoint documented and rate-limited; safety tests cover the worker code.

### Milestone 3 (weeks 5–6): published npm / PyPI SDK packages and research report
- Publish the existing zero-dependency clients as `npm` and PyPI packages with typed docs and examples.
- Release an open research report on Solana memecoin rug patterns from the corpus, including negative results and the limits of the label, with out-of-time evaluation on the larger held-out window.
- **Acceptance:** packages installable and tested in CI from a clean environment; report released under CC-BY.

## Budget and success measures
Funding supports engineering, tests, documentation and public dataset/API maintenance. Hosting stays on GitHub Actions/Pages except the small Milestone 2 worker. Success is measured by data coverage and freshness, reproducible CI, schema consumers and documented limitations, not token performance or trading returns. Any external-usage numbers (stars, installs) will be reported as they really are.

## Risks and honesty
Upstream APIs may change or rate-limit (fail-closed parsing). GitHub schedules are best effort. Holder and volume deltas are count/rolling-window proxies, not wallet-level identity. Signal p-values are unadjusted for multiple comparisons. The signal may simply not exist; the open measurement is still the deliverable. Not financial advice; the project never executes trades.
