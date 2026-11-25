# Insights (24h horizon)

Judged tokens (had liquidity at first sighting): **201**. Base rate of a bad outcome: **95/201 =  47%  (95% CI 40%-54%)**.

**Risk agent verdict**

| verdict | bad outcomes |
|---|---|
| PASSED | 31/39 =  79%  (95% CI 64%-89%) |
| REJECTED | 64/162 =  40%  (95% CI 32%-47%) |

**Liquidity at first sighting (USD)**

| range | bad outcomes |
|---|---|
| < 2,342 | 1/50 =   2%  (95% CI  0%-10%) |
| 2,342 to 7,886 | 23/50 =  46%  (95% CI 33%-60%) |
| 7,886 to 1.795e+04 | 35/50 =  70%  (95% CI 56%-81%) |
| >= 1.795e+04 | 36/51 =  71%  (95% CI 57%-81%) |

**Token age at first sighting (minutes)**

| range | bad outcomes |
|---|---|
| < 51.6 | 34/50 =  68%  (95% CI 54%-79%) |
| 51.6 to 98.9 | 23/50 =  46%  (95% CI 33%-60%) |
| 98.9 to 159.6 | 16/50 =  32%  (95% CI 21%-46%) |
| >= 159.6 | 22/51 =  43%  (95% CI 31%-57%) |

**Top-10 holder share (%, pool excluded)**

| range | bad outcomes |
|---|---|
| < 9.56 | 11/50 =  22%  (95% CI 13%-35%) |
| 9.56 to 18.47 | 22/49 =  45%  (95% CI 32%-59%) |
| 18.47 to 25.07 | 31/51 =  61%  (95% CI 47%-73%) |
| >= 25.07 | 31/51 =  61%  (95% CI 47%-73%) |

**24h volume / liquidity**

| range | bad outcomes |
|---|---|
| < 7.12 | 30/50 =  60%  (95% CI 46%-72%) |
| 7.12 to 20.23 | 32/50 =  64%  (95% CI 50%-76%) |
| 20.23 to 57.42 | 24/50 =  48%  (95% CI 35%-61%) |
| >= 57.42 | 9/51 =  18%  (95% CI 10%-30%) |

**Total holders**

| range | bad outcomes |
|---|---|
| < 323 | 1/8 =  12%  (95% CI  2%-47%) |
| 323 to 932 | 5/8 =  62%  (95% CI 31%-86%) |
| >= 932 | 7/8 =  88%  (95% CI 53%-98%) |

**Creator holding (%)**

| range | bad outcomes |
|---|---|
| < 0 | n=0 |
| 0 to 0 | n=0 |
| >= 0 | 13/24 =  54%  (95% CI 35%-72%) |

**Buy share of last-hour trades**

| range | bad outcomes |
|---|---|
| < 0.5271 | 2/8 =  25%  (95% CI  7%-59%) |
| 0.5271 to 0.5979 | 6/8 =  75%  (95% CI 41%-93%) |
| >= 0.5979 | 5/8 =  62%  (95% CI 31%-86%) |

**Price change in the hour before (%)**

| range | bad outcomes |
|---|---|
| < -47.52 | 3/8 =  38%  (95% CI 14%-69%) |
| -47.52 to 0.37 | 4/8 =  50%  (95% CI 22%-78%) |
| >= 0.37 | 6/8 =  75%  (95% CI 41%-93%) |

**Safety flags present at first sighting**

| flag | bad outcomes |
|---|---|
| Low Liquidity | 7/75 =   9%  (95% CI  5%-18%) |
| Creator history of rugged tokens | 6/14 =  43%  (95% CI 21%-67%) |
| Large Amount of LP Unlocked | 2/5 =  40%  (95% CI 12%-77%) |

Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.

Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.

