wrote data/REPORT.md
elemetry — Empirical Report

Generated from the append-only forward-test data. Descriptive research; not financial advice or a trading recommendation.

- Recorded tokens: **622**
- Judged at 24h: **300**
- v1 (live rules), full sample: **NO_EDGE** — pass-group survival is not separable from reject-group survival (95% Wilson intervals overlap, or pass is worse)
- v2 (shadow rubric), full sample: **NO_EDGE** — pass-group survival is not separable from reject-group survival (95% Wilson intervals overlap, or pass is worse)

## Full-sample comparison (24h) — in-sample for v2

| version | group | bad / n | bad rate | 95% Wilson CI |
|---|---|---:|---:|---:|
| v1 | pass | 49/59 | 83.0% | 71.5%–90.5% |
| v1 | reject | 94/241 | 39.0% | 33.1%–45.3% |
| v2 shadow | pass | 24/38 | 63.2% | 47.3%–76.6% |
| v2 shadow | reject | 119/262 | 45.4% | 39.5%–51.5% |

## Out-of-time comparison (24h): tokens first seen on/after 2026-11-24 only

Judged tokens in the held-out window: **99**. v2 defaults were designed and locked on tokens first seen before this date.

| version | group | bad / n | bad rate | 95% Wilson CI |
|---|---|---:|---:|---:|
| v1 | pass | 18/20 | 90.0% | 69.9%–97.2% |
| v1 | reject | 30/79 | 38.0% | 28.1%–49.0% |
| v2 shadow | pass | 7/10 | 70.0% | 39.7%–89.2% |
| v2 shadow | reject | 41/89 | 46.1% | 36.1%–56.4% |

- v1 held-out status: **INSUFFICIENT_DATA**
- v2 shadow held-out status: **INSUFFICIENT_DATA**

## Time-series coverage

| window | expected | observed | missing | status | median LP delta % | median holder growth/h | median volume ratio |
|---|---:|---:|---:|---|---:|---:|---:|
| T+0m | 622 | 622 | 0 | NONE | n/a | n/a | n/a |
| T+30m | 603 | 60 | 543 | PARTIAL | -95.4 | n/a | 0 |
| T+2h | 603 | 60 | 543 | PARTIAL | -95.4 | n/a | 0 |
| T+6h | 585 | 60 | 525 | PARTIAL | -95.4 | n/a | 0 |
| T+24h | 547 | 60 | 487 | PARTIAL | -95.4 | n/a | 0 |

## Signals (24h)

| signal | flagged / known | sample (smaller group) | status | bad if flagged | lift over base rate | p-value (Fisher exact, two-sided) |
|---|---:|---:|---|---:|---:|---:|
| Buys < 40% of last-hour trades | 23/123 | 23 | INSUFFICIENT_DATA | 9% | 0.175x | 1.2e-05 |
| Rejected by v1 rules | 241/300 | 59 | PRELIMINARY | 39% | 0.818x | 6.92e-10 |
| Liquidity < $20k | 231/300 | 69 | PRELIMINARY | 39% | 0.826x | 2.15e-07 |
| 24h volume >= 200x liquidity | 24/300 | 24 | INSUFFICIENT_DATA | 8% | 0.175x | 2.73e-05 |
| Insider-linked wallets present | 58/123 | 58 | PRELIMINARY | 41% | 0.834x | 0.105 |
| Top-10 holders >= 25% | 71/300 | 71 | PRELIMINARY | 59% | 1.24x | 0.0299 |
| Rejected by v2 rules | 262/300 | 38 | PRELIMINARY | 45% | 0.953x | 0.055 |
| Token younger than 4h | 268/300 | 32 | PRELIMINARY | 49% | 1.03x | 0.263 |
| No social links | 3/123 | 3 | INSUFFICIENT_DATA | 33% | 0.672x | 1 |
| Single wallet >= 10% | 0/13 | 0 | INSUFFICIENT_DATA | n/a | n/ax | n/a |
| Liquidity < 3% of market cap | 0/13 | 0 | INSUFFICIENT_DATA | n/a | n/ax | n/a |

## Interpretation

`STATISTICAL_EDGE_DETECTED` is reserved for a comparison with 30+ judged tokens per group and non-overlapping Wilson intervals; otherwise the status is `NO_EDGE` or `INSUFFICIENT_DATA`. Signal p-values are unadjusted for multiple comparisons, so with a dozen signals one will look significant by chance; only out-of-time confirmation counts. Holder-count and rolling-volume deltas are proxies: the data does not identify unique wallets, early-wallet distributions or causal mechanisms. No trading edge is asserted.
