# Solana Token Risk Telemetry — Empirical Report

Generated from the append-only forward-test data. Descriptive research; not financial advice or a trading recommendation.

- Recorded tokens: **547**
- Judged at 24h: **251**
- v1 (live rules), full sample: **NO_EDGE** — pass-group survival is not separable from reject-group survival (95% Wilson intervals overlap, or pass is worse)
- v2 (shadow rubric), full sample: **NO_EDGE** — pass-group survival is not separable from reject-group survival (95% Wilson intervals overlap, or pass is worse)

## Full-sample comparison (24h) — in-sample for v2

| version | group | bad / n | bad rate | 95% Wilson CI |
|---|---|---:|---:|---:|
| v1 | pass | 41/49 | 83.7% | 71.0%–91.5% |
| v1 | reject | 77/202 | 38.1% | 31.7%–45.0% |
| v2 shadow | pass | 22/35 | 62.9% | 46.3%–76.8% |
| v2 shadow | reject | 96/216 | 44.4% | 38.0%–51.1% |

## Out-of-time comparison (24h): tokens first seen on/after 2026-11-24 only

Judged tokens in the held-out window: **50**. v2 defaults were designed and locked on tokens first seen before this date.

| version | group | bad / n | bad rate | 95% Wilson CI |
|---|---|---:|---:|---:|
| v1 | pass | 10/10 | 100.0% | 72.2%–100.0% |
| v1 | reject | 13/40 | 32.5% | 20.1%–48.0% |
| v2 shadow | pass | 5/7 | 71.4% | 35.9%–91.8% |
| v2 shadow | reject | 18/43 | 41.9% | 28.4%–56.7% |

- v1 held-out status: **INSUFFICIENT_DATA**
- v2 shadow held-out status: **INSUFFICIENT_DATA**

## Time-series coverage

| window | expected | observed | missing | status | median LP delta % | median holder growth/h | median volume ratio |
|---|---:|---:|---:|---|---:|---:|---:|
| T+0m | 547 | 547 | 0 | NONE | n/a | n/a | n/a |
| T+30m | 547 | 0 | 547 | ALL | n/a | n/a | n/a |
| T+2h | 547 | 0 | 547 | ALL | n/a | n/a | n/a |
| T+6h | 547 | 0 | 547 | ALL | n/a | n/a | n/a |
| T+24h | 506 | 0 | 506 | ALL | n/a | n/a | n/a |

## Signals (24h)

| signal | flagged / known | sample (smaller group) | status | bad if flagged | lift over base rate | p-value (Fisher exact, two-sided) |
|---|---:|---:|---|---:|---:|---:|
| Buys < 40% of last-hour trades | 13/74 | 13 | INSUFFICIENT_DATA | 8% | 0.158x | 0.00146 |
| Rejected by v1 rules | 202/251 | 49 | PRELIMINARY | 38% | 0.811x | 6.68e-09 |
| Liquidity < $20k | 196/251 | 55 | PRELIMINARY | 38% | 0.814x | 2.21e-07 |
| 24h volume >= 200x liquidity | 19/251 | 19 | INSUFFICIENT_DATA | 0% | 0x | 3.25e-06 |
| Top-10 holders >= 25% | 58/251 | 58 | PRELIMINARY | 62% | 1.32x | 0.0107 |
| Rejected by v2 rules | 216/251 | 35 | PRELIMINARY | 44% | 0.945x | 0.0466 |
| No social links | 1/74 | 1 | INSUFFICIENT_DATA | 100% | 2.06x | 0.486 |
| Token younger than 4h | 224/251 | 27 | INSUFFICIENT_DATA | 48% | 1.03x | 0.312 |
| Insider-linked wallets present | 33/74 | 33 | PRELIMINARY | 45% | 0.934x | 0.647 |
| Single wallet >= 10% | 0/0 | 0 | INSUFFICIENT_DATA | n/a | n/ax | n/a |
| Liquidity < 3% of market cap | 0/0 | 0 | INSUFFICIENT_DATA | n/a | n/ax | n/a |

## Interpretation

`STATISTICAL_EDGE_DETECTED` is reserved for a comparison with 30+ judged tokens per group and non-overlapping Wilson intervals; otherwise the status is `NO_EDGE` or `INSUFFICIENT_DATA`. Signal p-values are unadjusted for multiple comparisons, so with a dozen signals one will look significant by chance; only out-of-time confirmation counts. Holder-count and rolling-volume deltas are proxies: the data does not identify unique wallets, early-wallet distributions or causal mechanisms. No trading edge is asserted.
