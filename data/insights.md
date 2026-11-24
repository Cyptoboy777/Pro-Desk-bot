# Insights (24h horizon)

Judged tokens (had liquidity at first sighting): **165**. Base rate of a bad outcome: **75/165 =  45%  (95% CI 38%-53%)**.

**Risk agent verdict**

| verdict | bad outcomes |
|---|---|
| PASSED | 24/31 =  77%  (95% CI 60%-89%) |
| REJECTED | 51/134 =  38%  (95% CI 30%-47%) |

**Liquidity at first sighting (USD)**

| range | bad outcomes |
|---|---|
| < 2,247 | 1/41 =   2%  (95% CI  0%-13%) |
| 2,247 to 7,865 | 17/41 =  41%  (95% CI 28%-57%) |
| 7,865 to 1.823e+04 | 28/41 =  68%  (95% CI 53%-80%) |
| >= 1.823e+04 | 29/42 =  69%  (95% CI 54%-81%) |

**Token age at first sighting (minutes)**

| range | bad outcomes |
|---|---|
| < 53.1 | 29/41 =  71%  (95% CI 56%-82%) |
| 53.1 to 106 | 19/41 =  46%  (95% CI 32%-61%) |
| 106 to 164.3 | 10/41 =  24%  (95% CI 14%-39%) |
| >= 164.3 | 17/42 =  40%  (95% CI 27%-56%) |

**Top-10 holder share (%, pool excluded)**

| range | bad outcomes |
|---|---|
| < 9.49 | 7/41 =  17%  (95% CI  9%-31%) |
| 9.49 to 18.47 | 19/41 =  46%  (95% CI 32%-61%) |
| 18.47 to 24.76 | 24/41 =  59%  (95% CI 43%-72%) |
| >= 24.76 | 25/42 =  60%  (95% CI 44%-73%) |

**24h volume / liquidity**

| range | bad outcomes |
|---|---|
| < 7.437 | 25/41 =  61%  (95% CI 46%-74%) |
| 7.437 to 22.51 | 26/41 =  63%  (95% CI 48%-76%) |
| 22.51 to 61.55 | 18/41 =  44%  (95% CI 30%-59%) |
| >= 61.55 | 6/42 =  14%  (95% CI  7%-28%) |

**Safety flags present at first sighting**

| flag | bad outcomes |
|---|---|
| Low Liquidity | 5/65 =   8%  (95% CI  3%-17%) |
| Creator history of rugged tokens | 4/11 =  36%  (95% CI 15%-65%) |
| Large Amount of LP Unlocked | 2/5 =  40%  (95% CI 12%-77%) |

Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.

Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.

