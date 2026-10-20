# OpenAI Decisions API vs JEV: ICP lead scoring

147 leads, 882 scored calls, 0 errors.

| Model | Exact level | Within one level | Mean error (0-3) | Leads that changed level between runs | Score spread between runs | Median time | 95th pct time | Input tokens | Cost per 1,000 leads |
|---|---|---|---|---|---|---|---|---|---|
| openai | 39% | 88% | 0.74 | 0% | 0.000 | 0.26 s | 0.33 s | 596 | $0.060 |
| jev | 72% | 96% | 0.42 | 7% | 0.031 | 0.27 s | 0.35 s | 816 | $0.034 |

The two models gave the same level on 78 of 147 leads (53%), first run each.

## Accuracy by label

| Label | Leads | OpenAI exact | JEV exact |
|---|---|---|---|
| No fit | 25 | 84% | 84% |
| Weak fit | 34 | 9% | 71% |
| Partial fit | 27 | 33% | 63% |
| Strong fit | 61 | 41% | 72% |

## Same test with each model's most likely level (instead of the rounded score)

| Model | Exact level |
|---|---|
| openai | 46% |
| jev | 69% |

## Where openai puts each label (rows = label, columns = answer, rounded score)

| Label | No fit | Weak fit | Partial fit | Strong fit |
|---|---|---|---|---|
| No fit | 21 | 1 | 2 | 1 |
| Weak fit | 31 | 3 | 0 | 0 |
| Partial fit | 6 | 10 | 9 | 2 |
| Strong fit | 2 | 6 | 28 | 25 |

## Where jev puts each label (rows = label, columns = answer, rounded score)

| Label | No fit | Weak fit | Partial fit | Strong fit |
|---|---|---|---|---|
| No fit | 21 | 0 | 2 | 2 |
| Weak fit | 9 | 24 | 1 | 0 |
| Partial fit | 0 | 6 | 17 | 4 |
| Strong fit | 0 | 2 | 15 | 44 |
