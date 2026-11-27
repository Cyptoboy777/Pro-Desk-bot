wrote data/REPORT.md
elemetry — Empirical Report

Generated from the append-only forward-test data. Descriptive research; not financial advice or a trading recommendation.

- Recorded tokens: **570**
- Judged at 24h: **279**
- v1 (live rules), full sample: **NO_EDGE** — pass-group survival is not separable from reject-group survival (95% Wilson intervals overlap, or pass is worse)
- v2 (shadow rubric), full sample: **NO_EDGE** — pass-group survival is not separable from reject-group survival (95% Wilson intervals overlap, or pass is worse)

## Full-sample comparison (24h) — in-sample for v2

| version | group | bad / n | bad rate | 95% Wilson CI |
|---|---|---:|---:|---:|
| v1 | pass | 45/55 | 81.8% | 69.7%–89.8% |
| v1 | reject | 87/224 | 38.8% | 32.7%–45.4% |
| v2 shadow | pass | 22/36 | 61.1% | 44.9%–75.2% |
| v2 shadow | reject | 110/243 | 45.3% | 39.1%–51.5% |

## Out-of-time comparison (24h): tokens first seen on/after 2026-11-24 only

Judged tokens in the held-out window: **78**. v2 defaults were designed and locked on tokens first seen before this date.

| version | group | bad / n | bad rate | 95% Wilson CI |
|---|---|---:|---:|---:|
| v1 | pass | 14/16 | 87.5% | 64.0%–96.5% |
| v1 | reject | 23/62 | 37.1% | 26.2%–49.5% |
| v2 shadow | pass | 5/8 | 62.5% | 30.6%–86.3% |
| v2 shadow | reject | 32/70 | 45.7% | 34.6%–57.3% |

- v1 held-out status: **INSUFFICIENT_DATA**
- v2 shadow held-out status: **INSUFFICIENT_DATA**

## Time-series coverage

| window | expected | observed | missing | status | median LP delta % | median holder growth/h | median volume ratio |
|---|---:|---:|---:|---|---:|---:|---:|
| T+0m | 570 | 570 | 0 | NONE | n/a | n/a | n/a |
| T+30m | 547 | 15 | 532 | PARTIAL | -100 | n/a | 0 |
| T+2h | 547 | 15 | 532 | PARTIAL | -100 | n/a | 0 |
| T+6h | 547 | 15 | 532 | PARTIAL | -100 | n/a | 0 |
| T+24h | 506 | 15 | 491 | PARTIAL | -100 | n/a | 0 |

## Signals (24h)

| signal | flagged / known | sample (smaller group) | status | bad if flagged | lift over base rate | p-value (Fisher exact, two-sided) |
|---|---:|---:|---|---:|---:|---:|
| Buys < 40% of last-hour trades | 19/102 | 19 | INSUFFICIENT_DATA | 11% | 0.215x | 0.000215 |
| Rejected by v1 rules | 224/279 | 55 | PRELIMINARY | 39% | 0.821x | 8.11e-09 |
| Liquidity < $20k | 216/279 | 63 | PRELIMINARY | 39% | 0.822x | 1.59e-07 |
| 24h volume >= 200x liquidity | 21/279 | 21 | INSUFFICIENT_DATA | 10% | 0.201x | 0.000193 |
| Insider-linked wallets present | 44/102 | 44 | PRELIMINARY | 39% | 0.788x | 0.0756 |
| Top-10 holders >= 25% | 67/279 | 67 | PRELIMINARY | 60% | 1.26x | 0.0245 |
| Rejected by v2 rules | 243/279 | 36 | PRELIMINARY | 45% | 0.957x | 0.106 |
| Token younger than 4h | 251/279 | 28 | INSUFFICIENT_DATA | 49% | 1.03x | 0.233 |
| No social links | 2/102 | 2 | INSUFFICIENT_DATA | 50% | 1.02x | 1 |
| Single wallet >= 10% | 0/0 | 0 | INSUFFICIENT_DATA | n/a | n/ax | n/a |
| Liquidity < 3% of market cap | 0/0 | 0 | INSUFFICIENT_DATA | n/a | n/ax | n/a |

## Interpretation

`STATISTICAL_EDGE_DETECTED` is reserved for a comparison with 30+ judged tokens per group and non-overlapping Wilson intervals; otherwise the status is `NO_EDGE` or `INSUFFICIENT_DATA`. Signal p-values are unadjusted for multiple comparisons, so with a dozen signals one will look significant by chance; only out-of-time confirmation counts. Holder-count and rolling-volume deltas are proxies: the data does not identify unique wallets, early-wallet distributions or causal mechanisms. No trading edge is asserted.
