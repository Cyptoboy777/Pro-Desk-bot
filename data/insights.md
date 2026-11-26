# Insights (24h horizon)

Judged tokens (had liquidity at first sighting): **243**. Base rate of a bad outcome: **115/243 =  47%  (95% CI 41%-54%)**.

**Risk agent verdict**

| verdict | bad outcomes |
|---|---|
| PASSED | 40/48 =  83%  (95% CI 70%-91%) |
| REJECTED | 75/195 =  38%  (95% CI 32%-45%) |

**Liquidity at first sighting (USD)**

| range | bad outcomes |
|---|---|
| < 2,336 | 1/60 =   2%  (95% CI  0%- 9%) |
| 2,336 to 7,886 | 26/61 =  43%  (95% CI 31%-55%) |
| 7,886 to 1.775e+04 | 43/61 =  70%  (95% CI 58%-80%) |
| >= 1.775e+04 | 45/61 =  74%  (95% CI 62%-83%) |

**Token age at first sighting (minutes)**

| range | bad outcomes |
|---|---|
| < 52.6 | 40/59 =  68%  (95% CI 55%-78%) |
| 52.6 to 94.7 | 29/62 =  47%  (95% CI 35%-59%) |
| 94.7 to 154.9 | 20/61 =  33%  (95% CI 22%-45%) |
| >= 154.9 | 26/61 =  43%  (95% CI 31%-55%) |

**Top-10 holder share (%, pool excluded)**

| range | bad outcomes |
|---|---|
| < 9.26 | 13/60 =  22%  (95% CI 13%-34%) |
| 9.26 to 18.47 | 27/61 =  44%  (95% CI 33%-57%) |
| 18.47 to 24.64 | 35/61 =  57%  (95% CI 45%-69%) |
| >= 24.64 | 40/61 =  66%  (95% CI 53%-76%) |

**24h volume / liquidity**

| range | bad outcomes |
|---|---|
| < 7.172 | 39/60 =  65%  (95% CI 52%-76%) |
| 7.172 to 17.41 | 37/61 =  61%  (95% CI 48%-72%) |
| 17.41 to 49.65 | 30/61 =  49%  (95% CI 37%-61%) |
| >= 49.65 | 9/61 =  15%  (95% CI  8%-26%) |

**Total holders**

| range | bad outcomes |
|---|---|
| < 317 | 3/16 =  19%  (95% CI  7%-43%) |
| 317 to 624 | 8/17 =  47%  (95% CI 26%-69%) |
| 624 to 1,195 | 6/16 =  38%  (95% CI 18%-61%) |
| >= 1,195 | 16/17 =  94%  (95% CI 73%-99%) |

**Creator holding (%)**

| range | bad outcomes |
|---|---|
| < 0 | n=0 |
| 0 to 0 | n=0 |
| 0 to 0 | n=0 |
| >= 0 | 33/66 =  50%  (95% CI 38%-62%) |

**Buy share of last-hour trades**

| range | bad outcomes |
|---|---|
| < 0.4851 | 1/16 =   6%  (95% CI  1%-28%) |
| 0.4851 to 0.5522 | 10/17 =  59%  (95% CI 36%-78%) |
| 0.5522 to 0.6087 | 11/16 =  69%  (95% CI 44%-86%) |
| >= 0.6087 | 11/17 =  65%  (95% CI 41%-83%) |

**Price change in the hour before (%)**

| range | bad outcomes |
|---|---|
| < -52.9 | 4/16 =  25%  (95% CI 10%-49%) |
| -52.9 to -10.47 | 9/17 =  53%  (95% CI 31%-74%) |
| -10.47 to 12.07 | 6/16 =  38%  (95% CI 18%-61%) |
| >= 12.07 | 14/17 =  82%  (95% CI 59%-94%) |

**Safety flags present at first sighting**

| flag | bad outcomes |
|---|---|
| Low Liquidity | 8/94 =   9%  (95% CI  4%-16%) |
| Creator history of rugged tokens | 7/19 =  37%  (95% CI 19%-59%) |
| Large Amount of LP Unlocked | 3/6 =  50%  (95% CI 19%-81%) |

Caution: liquidity, age and verdict are tangled together. The Risk agent only passes tokens with liquidity of $20k or more, which selects tokens that already graduated to a pool and are in their most volatile phase. Do not read one row alone.

Intervals that overlap are not different. With small n, treat every row as a question to test on new data, not an answer.

