# Insights (24h horizon)

Judged tokens (had liquidity at first sighting): **177**. Base rate of a bad outcome: **82/177 =  46%  (95% CI 39%-54%)**.

**Risk agent verdict**

| verdict | bad outcomes |
|---|---|
| PASSED | 25/32 =  78%  (95% CI 61%-89%) |
| REJECTED | 57/145 =  39%  (95% CI 32%-47%) |

**Liquidity at first sighting (USD)**

| range | bad outcomes |
|---|---|
| < 2,247 | 1/44 =   2%  (95% CI  0%-12%) |
| 2,247 to 7,855 | 19/44 =  43%  (95% CI 30%-58%) |
| 7,855 to 1.752e+04 | 31/44 =  70%  (95% CI 56%-82%) |
| >= 1.752e+04 | 31/45 =  69%  (95% CI 54%-80%) |

**Token age at first sighting (minutes)**

| range | bad outcomes |
|---|---|
| < 53.1 | 30/44 =  68%  (95% CI 53%-80%) |
| 53.1 to 106 | 22/44 =  50%  (95% CI 36%-64%) |
| 106 to 171.2 | 11/44 =  25%  (95% CI 15%-39%) |
| >= 171.2 | 19/45 =  42%  (95% CI 29%-57%) |

**Top-10 holder share (%, pool excluded)**

| range | bad outcomes |
|---|---|
| < 9.93 | 9/44 =  20%  (95% CI 11%-35%) |
| 9.93 to 18.47 | 18/43 =  42%  (95% CI 28%-57%) |
| 18.47 to 24.76 | 28/45 =  62%  (95% CI 48%-75%) |
| >= 24.76 | 27/45 =  60%  (95% CI 45%-73%) |

**24h volume / liquidity**

| range | bad outcomes |
|---|---|
| < 7.437 | 27/44 =  61%  (95% CI 47%-74%) |
| 7.437 to 21.66 | 27/44 =  61%  (95% CI 47%-74%) |
| 21.66 to 59.02 | 20/44 =  45%  (95% CI 32%-60%) |
| >= 59.02 | 8/45 =  18%  (95% CI  9%-31%) |

**Safety flags present at first sighting**

| flag | bad outcomes |
|---|---|
| Low Liquidity | 6/69 =   9%  (95% CI  4%-18%) |
| Creator history of rugged tokens | 5/13 =  38%  (95% CI 18%-64%) |
| Large Amount of LP Unlocked | 2/5 =  40%  (95% CI 12%-77%) |

Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.

Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.

