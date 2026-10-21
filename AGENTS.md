# Agent instructions

This repo benchmarks two AI decision models, the OpenAI Decisions API and Typesafe JEV, on one job: scoring B2B leads against an ideal customer profile (`ICP.md`). The published results are in `README.md` and `report.md`. When the user asks to compare the two models, or to benchmark lead scoring on their own leads:

1. Follow the skill in `skills/compare-models/SKILL.md` step by step.
2. Show the user the labels before you use them, and run the 10-lead test before the full benchmark.
3. Setup detail and the file list are in `docs/run-on-your-leads.md`.
4. If the user wants n8n instead, follow `docs/n8n.md` with them one step at a time: you cannot click inside n8n, so say exactly what to do, wait for their confirmation, and check their sheet has the seven columns before the import.

Confirm with the user before every call that saves, sends or changes anything, including a full benchmark run (it calls both paid APIs and overwrites `report.md` and `results.csv`). Never ask for or handle an API key in the chat: the user writes the keys into `.env`. Never commit `.env` or `data/raw-*.json`.
