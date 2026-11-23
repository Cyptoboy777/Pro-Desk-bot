# Insights (24h horizon)

Judged tokens (had liquidity at first sighting): **138**. Base rate of a bad outcome: **60/138 =  43%  (95% CI 35%-52%)**.

**Risk agent verdict**

| verdict | bad outcomes |
|---|---|
| PASSED | 17/21 =  81%  (95% CI 60%-92%) |
| REJECTED | 43/117 =  37%  (95% CI 29%-46%) |

**Liquidity at first sighting (USD)**

| range | bad outcomes |
|---|---|
| < 2,182 | 1/34 =   3%  (95% CI  1%-15%) |
| 2,182 to 6,799 | 10/35 =  29%  (95% CI 16%-45%) |
| 6,799 to 1.73e+04 | 25/34 =  74%  (95% CI 57%-85%) |
| >= 1.73e+04 | 24/35 =  69%  (95% CI 52%-81%) |

**Token age at first sighting (minutes)**

| range | bad outcomes |
|---|---|
| < 54.3 | 22/34 =  65%  (95% CI 48%-79%) |
| 54.3 to 107.3 | 15/35 =  43%  (95% CI 28%-59%) |
| 107.3 to 173.9 | 8/34 =  24%  (95% CI 12%-40%) |
| >= 173.9 | 15/35 =  43%  (95% CI 28%-59%) |

**Top-10 holder share (%, pool excluded)**

| range | bad outcomes |
|---|---|
| < 9.13 | 4/34 =  12%  (95% CI  5%-27%) |
| 9.13 to 18.47 | 15/34 =  44%  (95% CI 29%-61%) |
| 18.47 to 25.13 | 20/35 =  57%  (95% CI 41%-72%) |
| >= 25.13 | 21/35 =  60%  (95% CI 44%-74%) |

**24h volume / liquidity**

| range | bad outcomes |
|---|---|
| < 7.518 | 21/34 =  62%  (95% CI 45%-76%) |
| 7.518 to 24.02 | 19/35 =  54%  (95% CI 38%-70%) |
| 24.02 to 62.99 | 15/34 =  44%  (95% CI 29%-61%) |
| >= 62.99 | 5/35 =  14%  (95% CI  6%-29%) |

**Safety flags present at first sighting**

| flag | bad outcomes |
|---|---|
| Low Liquidity | 4/58 =   7%  (95% CI  3%-16%) |
| Creator history of rugged tokens | 4/10 =  40%  (95% CI 17%-69%) |
| Large Amount of LP Unlocked | 2/5 =  40%  (95% CI 12%-77%) |

Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.

Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.

