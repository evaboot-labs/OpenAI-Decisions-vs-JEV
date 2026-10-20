# OpenAI Decisions API vs JEV for lead scoring

A benchmark of two AI decision models on one job: scoring B2B leads against an ideal
customer profile. Both get the same input, the same question and the same four fit levels:

| Level | Meaning |
|---|---|
| No fit | Fails a disqualifier, or matches none of the must-haves |
| Weak fit | Matches one must-have |
| Partial fit | Matches most must-haves, one fails or is unknown |
| Strong fit | Matches every must-have and no disqualifier |

- **OpenAI Decisions API**: `POST https://api.openai.com/v1/decisions`, model `gpt-6-luna`
- **Typesafe JEV**: `POST https://api.typesafe.ai/v1/systemone`, model `jev-latest` (early access)

Built by [Evaboot](https://evaboot.com). The leads come from LinkedIn Sales Navigator,
exported with Evaboot.

## Results (2026-10-20)

998 leads, each scored 3 times by each model: 5,988 calls, 0 errors.
Full tables, per-label accuracy and confusion matrices: [`report.md`](report.md).

| | OpenAI | JEV |
|---|---|---|
| Exact level (vs our labels) | 46% | 71% |
| Within one level | 90% | 99% |
| Mean error (levels 0 to 3) | 0.65 | 0.40 |
| Leads that changed level between runs | 0% | 10% |
| Median response time | 0.27 s | 0.26 s |
| Input tokens per lead | 598 | 819 |
| Cost per 1,000 leads | $0.060 | $0.034 |

What it means:

- **Both rank leads the same way.** Spearman correlation with our labels is 0.85 (OpenAI) and
  0.87 (JEV), and 0.94 between the two models. Of the top 100 leads by score, 95 are Strong
  fit for both.
- **OpenAI is one level stricter.** It put 171 of 254 "Weak fit" leads in "No fit", and 168 of
  307 "Strong fit" leads in "Partial fit". If you filter on the level name, this matters.
- **OpenAI is deterministic.** Same lead, same answer, every run. JEV moved 10% of leads by one
  level between runs.
- **JEV is cheaper per lead**, but it is early access only.

The leads come from 12 Sales Navigator exports picked to cover every fit level: ICP sales
leaders in Europe and North America, sales leaders at companies over 1,000 staff, in other
industries and outside the region, other functions, junior sales roles and the public sector.

Limits: one ICP, labels written by us as rules (`label_leads.py`), one day. Run it on your own
leads before you choose.

The lead list itself is not in this repo: those are real people. `data/labels.csv` and
`results.csv` keep every label, every answer and the reason for each label, by lead id.

## Run it on your own leads

You need Python 3.9 or later. No packages to install.

1. Copy the env file and add both keys:
   ```bash
   cp .env.example .env
   ```
   OpenAI key: https://platform.openai.com/api-keys. JEV key: https://typesafe.ai (waitlist).
2. Replace [`ICP.md`](ICP.md) with your own profile.
3. Put your leads in `data/leads.csv` with the columns `id`, `Job title`, `Company`,
   `Company industry`, `Company employees`, `Company employee range`, `Company location`,
   `Lead location`, `Sales team size`, `Company description`. An Evaboot export has all of
   them: save the export JSON as `data/raw-<anything>.json` and run `python3 build_leads.py`.
4. Write the correct level for each lead in `data/labels.csv` (`id,label`). Do it by hand,
   or adapt the rules in `label_leads.py`, which encode our `ICP.md`.
5. Run the benchmark:
   ```bash
   python3 benchmark.py --limit 10 --runs 1   # quick check
   python3 benchmark.py                       # full run, 3 runs per model
   ```
   It writes `results.csv` (one row per call) and `report.md`.

## Files

| File | What it is |
|---|---|
| `benchmark.py` | Sends every lead to both models, writes `results.csv` and `report.md` |
| `ICP.md` | The ideal customer profile both models read |
| `build_leads.py` | Turns Evaboot export JSON into `data/leads.csv` (not committed) |
| `label_leads.py` | Our rubric: six must-haves and four disqualifiers, written as rules |
| `n8n/openai-vs-jev-lead-scoring.json` | n8n template: score a Google Sheet with both models side by side |

## n8n template

Import `n8n/openai-vs-jev-lead-scoring.json` in n8n. It reads a Google Sheet, sends each row
to both models and writes OpenAI score, OpenAI fit, JEV score, JEV fit and Same level back to
the row. The setup steps are on the sticky note inside the workflow.

## With an AI agent

Open this folder in Claude Code, Codex or Cursor and ask: "compare OpenAI and JEV on my
leads". The agent follows [`AGENTS.md`](AGENTS.md).
