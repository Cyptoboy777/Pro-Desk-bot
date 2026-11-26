# Methodology

## Scope and the zero-execution rule
Read-only research. No keys, signing, swaps or order routing, enforced by `tests/test_safety_policy.py` over all code files, workflow secrets and network hosts.

## Data
- Discovery: DexScreener latest token profiles (Solana). Market data: DexScreener token pairs (price, liquidity, volume, transaction counts, market cap, pair age). Safety data: RugCheck report (authorities, LP, holders with pool accounts excluded, insider networks, danger risks).
- Every sighting is appended once to `snapshots.jsonl` (`kind: entry`). Outcome rows (`kind: outcome`) record price and liquidity at +1h, +6h, +24h or `gone: true` if the pair disappeared. Append-only, committed to the `live-data` branch, so history is auditable with `git log`.
- Schema is backward compatible: new fields (`mcap`, `top1`, `auth_ok`) are optional; older rows lack them and the engine treats them as unknown.

## Outcome label
A token is **bad** at horizon h if, measured within 1.5x h of first sighting, the pair vanished, OR liquidity fell to 50% or less of entry, OR price fell to 50% or less. Only tokens with liquidity above 0 at first sighting are judged. Outcomes measured later than 1.5x h (sparse scheduler runs) are excluded. **Survival** is the complement. The label is a proxy for rugs and dumps, not proof of fraud, and price falls can also be ordinary decay.

## Statistics
- Rates carry 95% Wilson score intervals.
- `edge_status`: `INSUFFICIENT_DATA` if either group has fewer than 30 judged tokens; `STATISTICAL_EDGE_DETECTED` if the pass group's bad-rate upper bound is below the reject group's lower bound; else `NO_EDGE`. This is deliberately conservative and descriptive: it is about survival, not tradable profit.
- Per-signal table: precision = P(bad | flagged), recall = P(flagged | bad), point-biserial correlation with bad, and whether the flagged and clear intervals are disjoint. No multiple-comparison correction is applied; with a dozen signals, one will look significant by chance, so only out-of-time confirmation counts.

## Risk rubric v2
Hard rules fail outright. Otherwise points are added in three capped components (maturity 40, concentration 30, liquidity quality 30) and a token passes at score <= 20. Defaults come from priors about memecoin behaviour and a train-only look at tokens first seen before 2026-11-24, then were **locked**. Proxies: transaction-count buy share (not unique wallets); RugCheck insider count (not block-level sniper detection); liquidity / market cap from DexScreener. LP depth stability over time is not yet measured: it needs repeated snapshots per token (planned, Milestone 1).

## Validation protocol
1. Design on tokens first seen before 2026-11-24 (train, 201 judged).
2. Lock config; evaluate once on later tokens (test, 50 judged at lock time). Result: no separation (v2 pass 5/7 bad vs reject 18/43 bad), too small to conclude either way.
3. Keep v2 in **shadow mode**: the live paper desk still uses v1 rules until v2 shows a separated interval on new data.
4. Report growth of the test set in `summary.json` as data accrues.

## Paper trading
Fills use a 0.3% fee per side and slippage/price impact against the token's real liquidity; stops, trailing, take-profit and a circuit breaker apply. Outcomes at a fixed horizon in the simulator use raw price at +24h and a crude cost model; they are not achievable fills.

## Known limitations
Small and regime-dependent sample; selection by the discovery endpoint; survivorship in who stays listed; DexScreener field changes can break parsing (fail-closed); GitHub scheduling jitter; the label cannot separate rugs from normal decay; correlated signals; no causal claims.
