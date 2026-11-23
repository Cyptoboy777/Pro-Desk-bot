# Insights (24h horizon)

Judged tokens (had liquidity at first sighting): **152**. Base rate of a bad outcome: **68/152 =  45%  (95% CI 37%-53%)**.

**Risk agent verdict**

| verdict | bad outcomes |
|---|---|
| PASSED | 21/26 =  81%  (95% CI 62%-91%) |
| REJECTED | 47/126 =  37%  (95% CI 29%-46%) |

**Liquidity at first sighting (USD)**

| range | bad outcomes |
|---|---|
| < 2,225 | 1/38 =   3%  (95% CI  0%-13%) |
| 2,225 to 7,215 | 13/38 =  34%  (95% CI 21%-50%) |
| 7,215 to 1.795e+04 | 28/38 =  74%  (95% CI 58%-85%) |
| >= 1.795e+04 | 26/38 =  68%  (95% CI 53%-81%) |

**Token age at first sighting (minutes)**

| range | bad outcomes |
|---|---|
| < 53.2 | 26/38 =  68%  (95% CI 53%-81%) |
| 53.2 to 106 | 17/38 =  45%  (95% CI 30%-60%) |
| 106 to 173.3 | 9/38 =  24%  (95% CI 13%-39%) |
| >= 173.3 | 16/38 =  42%  (95% CI 28%-58%) |

**Top-10 holder share (%, pool excluded)**

| range | bad outcomes |
|---|---|
| < 9.13 | 5/38 =  13%  (95% CI  6%-27%) |
| 9.13 to 18.8 | 18/38 =  47%  (95% CI 32%-63%) |
| 18.8 to 25.07 | 22/38 =  58%  (95% CI 42%-72%) |
| >= 25.07 | 23/38 =  61%  (95% CI 45%-74%) |

**24h volume / liquidity**

| range | bad outcomes |
|---|---|
| < 7.518 | 24/38 =  63%  (95% CI 47%-77%) |
| 7.518 to 23.92 | 22/38 =  58%  (95% CI 42%-72%) |
| 23.92 to 62.99 | 16/38 =  42%  (95% CI 28%-58%) |
| >= 62.99 | 6/38 =  16%  (95% CI  7%-30%) |

**Safety flags present at first sighting**

| flag | bad outcomes |
|---|---|
| Low Liquidity | 4/62 =   6%  (95% CI  3%-15%) |
| Creator history of rugged tokens | 4/10 =  40%  (95% CI 17%-69%) |
| Large Amount of LP Unlocked | 2/5 =  40%  (95% CI 12%-77%) |

Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.

Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.

