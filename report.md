# OpenAI Decisions API vs JEV: ICP lead scoring

998 leads, 5988 scored calls, 0 errors.

| Model | Exact level | Within one level | Mean error (0-3) | Leads that changed level between runs | Score spread between runs | Median time | 95th pct time | Input tokens | Cost per 1,000 leads |
|---|---|---|---|---|---|---|---|---|---|
| openai | 46% | 90% | 0.65 | 0% | 0.000 | 0.27 s | 0.33 s | 598 | $0.060 |
| jev | 71% | 99% | 0.40 | 10% | 0.033 | 0.26 s | 0.31 s | 819 | $0.034 |

The two models gave the same level on 551 of 998 leads (55%), first run each.

## Accuracy by label

| Label | Leads | OpenAI exact | JEV exact |
|---|---|---|---|
| No fit | 164 | 98% | 95% |
| Weak fit | 254 | 26% | 63% |
| Partial fit | 273 | 43% | 66% |
| Strong fit | 307 | 39% | 69% |

## Same test with each model's most likely level (instead of the rounded score)

| Model | Exact level |
|---|---|
| openai | 48% |
| jev | 69% |

## Where openai puts each label (rows = label, columns = answer, rounded score)

| Label | No fit | Weak fit | Partial fit | Strong fit |
|---|---|---|---|---|
| No fit | 160 | 1 | 2 | 1 |
| Weak fit | 171 | 65 | 18 | 0 |
| Partial fit | 75 | 68 | 118 | 12 |
| Strong fit | 4 | 15 | 168 | 120 |

## Where jev puts each label (rows = label, columns = answer, rounded score)

| Label | No fit | Weak fit | Partial fit | Strong fit |
|---|---|---|---|---|
| No fit | 155 | 5 | 1 | 3 |
| Weak fit | 36 | 161 | 56 | 1 |
| Partial fit | 1 | 60 | 180 | 32 |
| Strong fit | 0 | 2 | 94 | 211 |
