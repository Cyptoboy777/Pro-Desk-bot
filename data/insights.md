# Insights (24h horizon)

Judged tokens (had liquidity at first sighting): **214**. Base rate of a bad outcome: **97/214 =  45%  (95% CI 39%-52%)**.

**Risk agent verdict**

| verdict | bad outcomes |
|---|---|
| PASSED | 31/39 =  79%  (95% CI 64%-89%) |
| REJECTED | 66/175 =  38%  (95% CI 31%-45%) |

**Liquidity at first sighting (USD)**

| range | bad outcomes |
|---|---|
| < 2,247 | 1/53 =   2%  (95% CI  0%-10%) |
| 2,247 to 7,855 | 23/54 =  43%  (95% CI 30%-56%) |
| 7,855 to 1.729e+04 | 34/53 =  64%  (95% CI 51%-76%) |
| >= 1.729e+04 | 39/54 =  72%  (95% CI 59%-82%) |

**Token age at first sighting (minutes)**

| range | bad outcomes |
|---|---|
| < 52.5 | 36/53 =  68%  (95% CI 55%-79%) |
| 52.5 to 101.1 | 24/54 =  44%  (95% CI 32%-58%) |
| 101.1 to 159.6 | 15/53 =  28%  (95% CI 18%-42%) |
| >= 159.6 | 22/54 =  41%  (95% CI 29%-54%) |

**Top-10 holder share (%, pool excluded)**

| range | bad outcomes |
|---|---|
| < 9.49 | 10/53 =  19%  (95% CI 11%-31%) |
| 9.49 to 18.47 | 23/53 =  43%  (95% CI 31%-57%) |
| 18.47 to 24.76 | 31/54 =  57%  (95% CI 44%-70%) |
| >= 24.76 | 33/54 =  61%  (95% CI 48%-73%) |

**24h volume / liquidity**

| range | bad outcomes |
|---|---|
| < 7.172 | 32/53 =  60%  (95% CI 47%-72%) |
| 7.172 to 20.24 | 32/54 =  59%  (95% CI 46%-71%) |
| 20.24 to 57.45 | 24/53 =  45%  (95% CI 33%-59%) |
| >= 57.45 | 9/54 =  17%  (95% CI  9%-29%) |

**Total holders**

| range | bad outcomes |
|---|---|
| < 242 | 1/9 =  11%  (95% CI  2%-44%) |
| 242 to 515 | 4/9 =  44%  (95% CI 19%-73%) |
| 515 to 839 | 3/9 =  33%  (95% CI 12%-65%) |
| >= 839 | 7/10 =  70%  (95% CI 40%-89%) |

**Creator holding (%)**

| range | bad outcomes |
|---|---|
| < 0 | n=0 |
| 0 to 0 | n=0 |
| 0 to 0 | n=0 |
| >= 0 | 15/37 =  41%  (95% CI 26%-57%) |

**Buy share of last-hour trades**

| range | bad outcomes |
|---|---|
| < 0.478 | 0/9 =   0%  (95% CI  0%-30%) |
| 0.478 to 0.5398 | 5/9 =  56%  (95% CI 27%-81%) |
| 0.5398 to 0.6087 | 6/9 =  67%  (95% CI 35%-88%) |
| >= 0.6087 | 4/10 =  40%  (95% CI 17%-69%) |

**Price change in the hour before (%)**

| range | bad outcomes |
|---|---|
| < -64.23 | 3/9 =  33%  (95% CI 12%-65%) |
| -64.23 to -12.85 | 4/9 =  44%  (95% CI 19%-73%) |
| -12.85 to 1.28 | 3/9 =  33%  (95% CI 12%-65%) |
| >= 1.28 | 5/10 =  50%  (95% CI 24%-76%) |

**Safety flags present at first sighting**

| flag | bad outcomes |
|---|---|
| Low Liquidity | 7/84 =   8%  (95% CI  4%-16%) |
| Creator history of rugged tokens | 6/14 =  43%  (95% CI 21%-67%) |
| Large Amount of LP Unlocked | 2/5 =  40%  (95% CI 12%-77%) |

Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.

Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.

