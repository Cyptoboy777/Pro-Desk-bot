# Insights (24h horizon)

Judged tokens (had liquidity at first sighting): **227**. Base rate of a bad outcome: **105/227 =  46%  (95% CI 40%-53%)**.

**Risk agent verdict**

| verdict | bad outcomes |
|---|---|
| PASSED | 35/43 =  81%  (95% CI 67%-90%) |
| REJECTED | 70/184 =  38%  (95% CI 31%-45%) |

**Liquidity at first sighting (USD)**

| range | bad outcomes |
|---|---|
| < 2,336 | 1/56 =   2%  (95% CI  0%- 9%) |
| 2,336 to 7,882 | 25/57 =  44%  (95% CI 32%-57%) |
| 7,882 to 1.752e+04 | 38/57 =  67%  (95% CI 54%-78%) |
| >= 1.752e+04 | 41/57 =  72%  (95% CI 59%-82%) |

**Token age at first sighting (minutes)**

| range | bad outcomes |
|---|---|
| < 52.5 | 38/56 =  68%  (95% CI 55%-79%) |
| 52.5 to 98.9 | 26/57 =  46%  (95% CI 33%-58%) |
| 98.9 to 158.9 | 18/57 =  32%  (95% CI 21%-44%) |
| >= 158.9 | 23/57 =  40%  (95% CI 29%-53%) |

**Top-10 holder share (%, pool excluded)**

| range | bad outcomes |
|---|---|
| < 9.56 | 12/56 =  21%  (95% CI 13%-34%) |
| 9.56 to 18.47 | 24/56 =  43%  (95% CI 31%-56%) |
| 18.47 to 24.64 | 33/58 =  57%  (95% CI 44%-69%) |
| >= 24.64 | 36/57 =  63%  (95% CI 50%-74%) |

**24h volume / liquidity**

| range | bad outcomes |
|---|---|
| < 7.12 | 35/56 =  62%  (95% CI 49%-74%) |
| 7.12 to 19.61 | 34/57 =  60%  (95% CI 47%-71%) |
| 19.61 to 52.36 | 27/57 =  47%  (95% CI 35%-60%) |
| >= 52.36 | 9/57 =  16%  (95% CI  9%-27%) |

**Total holders**

| range | bad outcomes |
|---|---|
| < 288 | 2/12 =  17%  (95% CI  5%-45%) |
| 288 to 599 | 6/13 =  46%  (95% CI 23%-71%) |
| 599 to 1,124 | 4/12 =  33%  (95% CI 14%-61%) |
| >= 1,124 | 11/13 =  85%  (95% CI 58%-96%) |

**Creator holding (%)**

| range | bad outcomes |
|---|---|
| < 0 | n=0 |
| 0 to 0 | n=0 |
| 0 to 0 | n=0 |
| >= 0 | 23/50 =  46%  (95% CI 33%-60%) |

**Buy share of last-hour trades**

| range | bad outcomes |
|---|---|
| < 0.4824 | 1/12 =   8%  (95% CI  1%-35%) |
| 0.4824 to 0.5522 | 8/13 =  62%  (95% CI 36%-82%) |
| 0.5522 to 0.6087 | 7/12 =  58%  (95% CI 32%-81%) |
| >= 0.6087 | 7/13 =  54%  (95% CI 29%-77%) |

**Price change in the hour before (%)**

| range | bad outcomes |
|---|---|
| < -55.19 | 3/12 =  25%  (95% CI  9%-53%) |
| -55.19 to -12.85 | 7/13 =  54%  (95% CI 29%-77%) |
| -12.85 to 2.51 | 4/12 =  33%  (95% CI 14%-61%) |
| >= 2.51 | 9/13 =  69%  (95% CI 42%-87%) |

**Safety flags present at first sighting**

| flag | bad outcomes |
|---|---|
| Low Liquidity | 7/87 =   8%  (95% CI  4%-16%) |
| Creator history of rugged tokens | 7/16 =  44%  (95% CI 23%-67%) |
| Large Amount of LP Unlocked | 2/5 =  40%  (95% CI 12%-77%) |

Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.

Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.

