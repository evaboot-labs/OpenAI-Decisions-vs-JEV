# OpenAI Decisions API vs JEV: ICP lead scoring

147 leads, 882 scored calls, 0 errors.

| Model | Exact level | Within one level | Mean error (0-3) | Leads that changed level between runs | Score spread between runs | Median time | 95th pct time | Input tokens | Cost per 1,000 leads |
|---|---|---|---|---|---|---|---|---|---|
| openai | 41% | 90% | 0.71 | 0% | 0.000 | 0.26 s | 0.33 s | 596 | $0.060 |
| jev | 73% | 97% | 0.41 | 7% | 0.031 | 0.27 s | 0.35 s | 816 | $0.034 |

The two models gave the same level on 78 of 147 leads (53%), first run each.

## Accuracy by label

| Label | Leads | OpenAI exact | JEV exact |
|---|---|---|---|
| No fit | 25 | 84% | 84% |
| Weak fit | 37 | 14% | 70% |
| Partial fit | 25 | 36% | 64% |
| Strong fit | 60 | 42% | 73% |

## Same test with each model's most likely level (instead of the rounded score)

| Model | Exact level |
|---|---|
| openai | 46% |
| jev | 67% |

## Where openai puts each label (rows = label, columns = answer, rounded score)

| Label | No fit | Weak fit | Partial fit | Strong fit |
|---|---|---|---|---|
| No fit | 21 | 1 | 2 | 1 |
| Weak fit | 32 | 5 | 0 | 0 |
| Partial fit | 5 | 9 | 9 | 2 |
| Strong fit | 2 | 5 | 28 | 25 |

## Where jev puts each label (rows = label, columns = answer, rounded score)

| Label | No fit | Weak fit | Partial fit | Strong fit |
|---|---|---|---|---|
| No fit | 21 | 0 | 2 | 2 |
| Weak fit | 9 | 26 | 2 | 0 |
| Partial fit | 0 | 5 | 16 | 4 |
| Strong fit | 0 | 1 | 15 | 44 |
