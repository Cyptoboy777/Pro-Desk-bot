wrote data/REPORT.md
elemetry — Empirical Report

Generated from the append-only forward-test data. Descriptive research; not financial advice or a trading recommendation.

- Recorded tokens: **585**
- Judged at 24h: **287**
- v1 (live rules), full sample: **NO_EDGE** — pass-group survival is not separable from reject-group survival (95% Wilson intervals overlap, or pass is worse)
- v2 (shadow rubric), full sample: **NO_EDGE** — pass-group survival is not separable from reject-group survival (95% Wilson intervals overlap, or pass is worse)

## Full-sample comparison (24h) — in-sample for v2

| version | group | bad / n | bad rate | 95% Wilson CI |
|---|---|---:|---:|---:|
| v1 | pass | 46/56 | 82.1% | 70.2%–90.0% |
| v1 | reject | 91/231 | 39.4% | 33.3%–45.8% |
| v2 shadow | pass | 22/36 | 61.1% | 44.9%–75.2% |
| v2 shadow | reject | 115/251 | 45.8% | 39.8%–52.0% |

## Out-of-time comparison (24h): tokens first seen on/after 2026-11-24 only

Judged tokens in the held-out window: **86**. v2 defaults were designed and locked on tokens first seen before this date.

| version | group | bad / n | bad rate | 95% Wilson CI |
|---|---|---:|---:|---:|
| v1 | pass | 15/17 | 88.2% | 65.7%–96.7% |
| v1 | reject | 27/69 | 39.1% | 28.5%–50.9% |
| v2 shadow | pass | 5/8 | 62.5% | 30.6%–86.3% |
| v2 shadow | reject | 37/78 | 47.4% | 36.7%–58.4% |

- v1 held-out status: **INSUFFICIENT_DATA**
- v2 shadow held-out status: **INSUFFICIENT_DATA**

## Time-series coverage

| window | expected | observed | missing | status | median LP delta % | median holder growth/h | median volume ratio |
|---|---:|---:|---:|---|---:|---:|---:|
| T+0m | 585 | 585 | 0 | NONE | n/a | n/a | n/a |
| T+30m | 570 | 30 | 540 | PARTIAL | -90.7 | n/a | 0 |
| T+2h | 570 | 30 | 540 | PARTIAL | -90.7 | n/a | 0 |
| T+6h | 570 | 30 | 540 | PARTIAL | -90.7 | n/a | 0 |
| T+24h | 528 | 30 | 498 | PARTIAL | -90.7 | n/a | 0 |

## Signals (24h)

| signal | flagged / known | sample (smaller group) | status | bad if flagged | lift over base rate | p-value (Fisher exact, two-sided) |
|---|---:|---:|---|---:|---:|---:|
| Buys < 40% of last-hour trades | 20/110 | 20 | INSUFFICIENT_DATA | 10% | 0.2x | 0.000105 |
| Rejected by v1 rules | 231/287 | 56 | PRELIMINARY | 39% | 0.825x | 5.52e-09 |
| Liquidity < $20k | 221/287 | 66 | PRELIMINARY | 40% | 0.834x | 1.17e-06 |
| 24h volume >= 200x liquidity | 22/287 | 22 | INSUFFICIENT_DATA | 9% | 0.19x | 9.38e-05 |
| Insider-linked wallets present | 51/110 | 51 | PRELIMINARY | 41% | 0.824x | 0.126 |
| Top-10 holders >= 25% | 70/287 | 70 | PRELIMINARY | 59% | 1.23x | 0.0399 |
| Rejected by v2 rules | 251/287 | 36 | PRELIMINARY | 46% | 0.96x | 0.108 |
| Token younger than 4h | 257/287 | 30 | PRELIMINARY | 49% | 1.04x | 0.122 |
| No social links | 3/110 | 3 | INSUFFICIENT_DATA | 33% | 0.667x | 1 |
| Single wallet >= 10% | 0/0 | 0 | INSUFFICIENT_DATA | n/a | n/ax | n/a |
| Liquidity < 3% of market cap | 0/0 | 0 | INSUFFICIENT_DATA | n/a | n/ax | n/a |

## Interpretation

`STATISTICAL_EDGE_DETECTED` is reserved for a comparison with 30+ judged tokens per group and non-overlapping Wilson intervals; otherwise the status is `NO_EDGE` or `INSUFFICIENT_DATA`. Signal p-values are unadjusted for multiple comparisons, so with a dozen signals one will look significant by chance; only out-of-time confirmation counts. Holder-count and rolling-volume deltas are proxies: the data does not identify unique wallets, early-wallet distributions or causal mechanisms. No trading edge is asserted.
