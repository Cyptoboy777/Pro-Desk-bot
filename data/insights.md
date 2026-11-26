# Insights (24h horizon)

Judged tokens (had liquidity at first sighting): **251**. Base rate of a bad outcome: **118/251 =  47%  (95% CI 41%-53%)**.

**Risk agent verdict**

| verdict | bad outcomes |
|---|---|
| PASSED | 41/49 =  84%  (95% CI 71%-91%) |
| REJECTED | 77/202 =  38%  (95% CI 32%-45%) |

**Liquidity at first sighting (USD)**

| range | bad outcomes |
|---|---|
| < 2,336 | 1/62 =   2%  (95% CI  0%- 9%) |
| 2,336 to 7,882 | 28/63 =  44%  (95% CI 33%-57%) |
| 7,882 to 1.795e+04 | 43/63 =  68%  (95% CI 56%-78%) |
| >= 1.795e+04 | 46/63 =  73%  (95% CI 61%-82%) |

**Token age at first sighting (minutes)**

| range | bad outcomes |
|---|---|
| < 52.6 | 40/61 =  66%  (95% CI 53%-76%) |
| 52.6 to 98.7 | 30/64 =  47%  (95% CI 35%-59%) |
| 98.7 to 154.9 | 21/63 =  33%  (95% CI 23%-46%) |
| >= 154.9 | 27/63 =  43%  (95% CI 31%-55%) |

**Top-10 holder share (%, pool excluded)**

| range | bad outcomes |
|---|---|
| < 9.26 | 14/62 =  23%  (95% CI 14%-34%) |
| 9.26 to 18.47 | 27/62 =  44%  (95% CI 32%-56%) |
| 18.47 to 24.49 | 36/64 =  56%  (95% CI 44%-68%) |
| >= 24.49 | 41/63 =  65%  (95% CI 53%-76%) |

**24h volume / liquidity**

| range | bad outcomes |
|---|---|
| < 7.437 | 40/62 =  65%  (95% CI 52%-75%) |
| 7.437 to 17.41 | 37/63 =  59%  (95% CI 46%-70%) |
| 17.41 to 51.53 | 31/63 =  49%  (95% CI 37%-61%) |
| >= 51.53 | 10/63 =  16%  (95% CI  9%-27%) |

**Total holders**

| range | bad outcomes |
|---|---|
| < 317 | 3/18 =  17%  (95% CI  6%-39%) |
| 317 to 624 | 9/19 =  47%  (95% CI 27%-68%) |
| 624 to 1,195 | 7/18 =  39%  (95% CI 20%-61%) |
| >= 1,195 | 17/19 =  89%  (95% CI 69%-97%) |

**Creator holding (%)**

| range | bad outcomes |
|---|---|
| < 0 | n=0 |
| 0 to 0 | n=0 |
| 0 to 0 | n=0 |
| >= 0 | 36/74 =  49%  (95% CI 38%-60%) |

**Buy share of last-hour trades**

| range | bad outcomes |
|---|---|
| < 0.4634 | 2/18 =  11%  (95% CI  3%-33%) |
| 0.4634 to 0.5437 | 9/19 =  47%  (95% CI 27%-68%) |
| 0.5437 to 0.5979 | 13/18 =  72%  (95% CI 49%-88%) |
| >= 0.5979 | 12/19 =  63%  (95% CI 41%-81%) |

**Price change in the hour before (%)**

| range | bad outcomes |
|---|---|
| < -52.9 | 5/18 =  28%  (95% CI 12%-51%) |
| -52.9 to -10.47 | 10/19 =  53%  (95% CI 32%-73%) |
| -10.47 to 12.07 | 7/18 =  39%  (95% CI 20%-61%) |
| >= 12.07 | 14/19 =  74%  (95% CI 51%-88%) |

**Safety flags present at first sighting**

| flag | bad outcomes |
|---|---|
| Low Liquidity | 9/98 =   9%  (95% CI  5%-17%) |
| Creator history of rugged tokens | 7/19 =  37%  (95% CI 19%-59%) |
| Large Amount of LP Unlocked | 3/6 =  50%  (95% CI 19%-81%) |

Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.

Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.

