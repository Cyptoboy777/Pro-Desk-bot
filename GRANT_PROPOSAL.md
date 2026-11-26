# Grant proposal: Solana Token Risk & Forward-Test Telemetry (open-source public good)

**Requested:** $3,000-$5,000 USDG, three 2-week milestones. **Applicant:** [name, contact, GitHub: Cyptoboy777]. **License:** MIT. **Repo:** https://github.com/Cyptoboy777/Pro-Desk-bot

## Problem
Memecoin risk tools show static checks (mint authority, LP lock, holder counts) as if they mean "safe". Our own forward test says otherwise: of 49 tokens that passed such checks and were judged at 24h, 41 (84%) still vanished or lost at least half their liquidity or price, worse than the tokens the same rules rejected. No open, continuously-updated dataset exists that lets wallets and researchers measure which signals actually matter.

## What exists today (verifiable in the repo)
Automated read-only collector on GitHub Actions with append-only data on a `live-data` branch; 528 tokens recorded, 251 judged at 24h; Wilson-interval statistics; an explainable risk rubric v2 in Python and JavaScript with a parity test; static JSON API; interactive dashboard with filter simulator; and a CI test that fails the build if wallet, key, signing or swap code appears. **Current honest status: `NO_EDGE`.** We will not market a signal that the data does not support.

## Why fund it
A public, reproducible, honest benchmark is the missing piece. The output is infrastructure and evidence that other builders can reuse, including a negative-result record that stops people shipping false safety badges.

## Milestones

**Milestone 1 (weeks 1-2): Risk engine v2 + dataset + CI safety**
- Add repeated per-token snapshots to measure LP depth stability; improve insider/sniper proxies where public data allows.
- Grow the forward-test dataset to 1,000 judged-or-pending tokens; publish a versioned dataset release.
- Expand CI safety tests (already scanning .py/.js/.html/.yml/.json, workflow secrets and network hosts) with a documented threat model.
- *Done when:* 1,000 tokens recorded, v2 evaluated on a pre-registered out-of-time split, CI badge green.

**Milestone 2 (weeks 3-4): Public API + simulator + Blink**
- Stabilise `api/v1` (schema docs, changelog, uptime check).
- Harden the Filter Backtest Simulator (confidence intervals, train/test toggle, shareable URLs).
- A Solana Action/Blink risk-check endpoint that returns the rubric breakdown for a mint. It must be read-only: it returns a risk report and a link, and never builds, requests or signs a transaction. The zero-execution CI guard stays in force and is extended to it.
- *Done when:* public endpoints documented, Blink unfurls a risk card for a mint, safety tests cover the new code.

**Milestone 3 (weeks 5-6): SDK + research report**
- Lightweight `npm` and `pip` clients (fetch and type the JSON API; run the rubric locally). No wallet dependencies.
- Open research report on Solana memecoin rug patterns using the dataset, including negative results and the limits of the label.
- *Done when:* packages published, README quickstarts tested, report released under CC-BY.

## Budget (indicative)
Engineering time for the three milestones; hosting is free (GitHub Actions and Pages). Any paid RPC or data tier is optional and listed separately if needed.

## Success metrics
Dataset size and freshness; API availability; number of external consumers (stars, forks, SDK installs; we will report whatever the real numbers are); CI safety guard unbroken; one published report.

## Risks and honesty
Upstream APIs may change or rate-limit (fail-closed parsing, retries). GitHub schedules are best effort. The signal may simply not exist; the deliverable is still the open measurement. Not financial advice; the project never executes trades.
