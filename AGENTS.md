# Agent instructions

This repo compares the OpenAI Decisions API and Typesafe JEV on ICP lead scoring. When the user asks to compare the two models, or to benchmark lead scoring on their leads:

1. Check that `.env` has `OPENAI_API_KEY` and `JEV_API_KEY`. If one is missing, tell the user how to get it from README.md and stop.
2. Read `ICP.md`. If it still holds the example profile, ask the user for their own and rewrite the file first.
3. Check that `data/leads.csv` holds the user's leads. If the user has an Evaboot export, save its JSON as `data/raw-<name>.json` and run `python3 build_leads.py`.
4. Check that `data/labels.csv` has a correct level for each lead. If not, propose labels with the user's ICP, show them as a table, and let the user correct them. Never invent labels without showing them.
5. Run `python3 benchmark.py --limit 10 --runs 1` and show the table from `report.md`.
6. When the user agrees, run `python3 benchmark.py` and summarise: accuracy, how strict each model is, consistency between runs, speed and cost.

Never commit `.env` or `data/raw-*.json`.
