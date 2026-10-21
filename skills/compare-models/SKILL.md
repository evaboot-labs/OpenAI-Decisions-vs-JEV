---
name: compare-models
description: Benchmark the OpenAI Decisions API against Typesafe JEV on the user's own leads and ICP. Use when the user asks to compare the two models, or to test which one scores their leads better.
---

# Compare OpenAI Decisions and JEV on the user's leads

Run this inside a clone of `evaboot-labs/openai-decisions-vs-jev`. `benchmark.py` overwrites `report.md` and `results.csv`, so the published results change once it runs; tell the user before the first run.

1. Check that `.env` has `OPENAI_API_KEY` and `JEV_API_KEY`. If one is missing, tell the user how to get it from `docs/run-on-your-leads.md` and stop. The user writes the keys into `.env`; never ask for a key in the chat.
2. Read `ICP.md`. If it still holds the example profile, ask the user for their own and rewrite the file first.
3. Check that `data/leads.csv` holds the user's leads. If the user has an Evaboot export, save its JSON as `data/raw-<name>.json` and run `python3 build_leads.py`.
4. Check that `data/labels.csv` has a correct level for each lead. If not, propose labels with the user's ICP, show them as a table, and let the user correct them. Never invent labels without showing them.
5. Run `python3 benchmark.py --limit 10 --runs 1` and show the table from `report.md`.
6. When the user agrees, run `python3 benchmark.py` and summarise: accuracy, how strict each model is, consistency between runs, speed and cost.

Never commit `.env` or `data/raw-*.json`: the raw exports hold real people's data.
