# Run it on your own leads

You need Python 3.9 or later. No packages to install.

1. Copy the env file and add both keys:
   ```bash
   cp .env.example .env
   ```
   OpenAI key: https://platform.openai.com/api-keys. JEV key: https://typesafe.ai (waitlist).
2. Replace [`ICP.md`](../ICP.md) with your own profile.
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

Step-by-step setup: [`n8n.md`](n8n.md).

Back to the [README](../README.md).
