"""Benchmark OpenAI's Decisions API against Typesafe JEV on ICP lead scoring.

Both models get the same input (ICP.md + the lead), the same instructions and the same four
fit levels. Each lead is scored RUNS times by each model, so the report shows accuracy against
your labels, agreement between the models, consistency over runs, speed and cost.

    python3 benchmark.py                    # score data/leads.csv, write results.csv + report.md
    python3 benchmark.py --limit 10 --runs 1   # quick check
    python3 benchmark.py --report-only      # rebuild report.md from results.csv

Settings come from .env: OPENAI_API_KEY, JEV_API_KEY.
"""
import argparse
import csv
import json
import os
import statistics as st
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
for line in (HERE / ".env").read_text().splitlines() if (HERE / ".env").exists() else []:
    if "=" in line and not line.lstrip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

LEVELS = [
    ("No fit", "Fails a disqualifier, or matches none of the must-haves."),
    ("Weak fit", "Matches one must-have. The other must-haves fail or are unknown."),
    ("Partial fit", "Matches most must-haves, but one fails or is unknown."),
    ("Strong fit", "Matches every must-have and no disqualifier."),
]
NAMES = [name for name, _ in LEVELS]
INSTRUCTIONS = "How well does this lead match the ideal customer profile?"
# USD per million input tokens, from each provider's pricing page on 2026-10-20. Output is not billed
# by JEV and is 0 tokens for an OpenAI score question.
PRICE = {"openai": 0.10, "jev": 0.042}
FIELDS = ["model", "run", "lead_id", "score", "level", "top_level", "confidence", "seconds", "input_tokens", "error"]


def call(url, key, body):
    req = urllib.request.Request(url, method="POST", data=json.dumps(body).encode(), headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "decision-benchmark/1.0"})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r), time.perf_counter() - start
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code}: {e.read().decode()[:200]}")


def state(icp, lead):
    return f"Ideal customer profile:\n{icp}\n\nLead:\n{lead}"


def score_openai(icp, lead):
    body, secs = call("https://api.openai.com/v1/decisions", os.environ["OPENAI_API_KEY"], {
        "model": "gpt-6-luna",
        "input": state(icp, lead),
        "questions": [{"type": "score", "name": "icp_fit", "instructions": INSTRUCTIONS,
                       "levels": [{"label": n, "description": d} for n, d in LEVELS]}],
    })
    a = body["answers"][0]
    top = max(a["probabilities"], key=lambda p: p["probability"])["value"]
    return a["score"], a["confidence"], secs, body["usage"]["input_tokens"], top


def score_jev(icp, lead):
    body, secs = call("https://api.typesafe.ai/v1/systemone", os.environ["JEV_API_KEY"], {
        "model": "jev-latest",
        "state": state(icp, lead),
        "questions": {"icp_fit": {"type": "score", "instructions": INSTRUCTIONS,
                                  "criteria": [f"{n}: {d}" for n, d in LEVELS]}},
    })
    a = body["answers"]["icp_fit"]
    top = int(max(a["probabilities"], key=lambda k: a["probabilities"][k]))
    return a["score"], a["confidence"], secs, body["usage"]["input_tokens"], top


MODELS = {"openai": score_openai, "jev": score_jev}


def describe(row):
    keys = ["Job title", "Company", "Company industry", "Company employees", "Company employee range",
            "Company location", "Lead location", "Sales team size", "Company description"]
    return "\n".join(f"{k}: {row[k] or 'unknown'}" for k in keys)


def run_one(task):
    model, run, row, icp = task
    try:
        score, conf, secs, tokens, top = MODELS[model](icp, describe(row))
        return {"model": model, "run": run, "lead_id": row["id"], "score": round(score, 3),
                "level": NAMES[round(score)], "top_level": NAMES[top], "confidence": round(conf, 3),
                "seconds": round(secs, 3),
                "input_tokens": tokens, "error": ""}
    except Exception as e:  # keep going; the report counts errors
        return {"model": model, "run": run, "lead_id": row["id"], "score": "", "level": "", "top_level": "",
                "confidence": "",
                "seconds": "", "input_tokens": "", "error": str(e)[:200]}


def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "n/a"


def report(results, labels):
    ok = [r for r in results if not r["error"]]
    lines = ["# OpenAI Decisions API vs JEV: ICP lead scoring", "",
             f"{len({r['lead_id'] for r in ok})} leads, {len(ok)} scored calls, "
             f"{len(results) - len(ok)} errors.", ""]
    rows = []
    by = {}
    for r in ok:
        by.setdefault((r["model"], r["lead_id"]), []).append(r)
    for model in MODELS:
        mine = [r for r in ok if r["model"] == model]
        first = {lid: rs for (m, lid), rs in by.items() if m == model}
        labelled = [lid for lid in first if lid in labels]
        exact = sum(NAMES.index(first[lid][0]["level"]) == labels[lid] for lid in labelled)
        within = sum(abs(NAMES.index(first[lid][0]["level"]) - labels[lid]) <= 1 for lid in labelled)
        mae = st.mean(abs(float(first[lid][0]["score"]) - labels[lid]) for lid in labelled) if labelled else 0
        flips = sum(len({r["level"] for r in rs}) > 1 for rs in first.values())
        spread = st.mean(st.pstdev([float(r["score"]) for r in rs]) for rs in first.values() if len(rs) > 1) \
            if any(len(rs) > 1 for rs in first.values()) else 0
        secs = sorted(float(r["seconds"]) for r in mine)
        tokens = st.mean(int(r["input_tokens"]) for r in mine)
        rows.append([model, pct(exact, len(labelled)), pct(within, len(labelled)), f"{mae:.2f}",
                     pct(flips, len(first)), f"{spread:.3f}", f"{st.median(secs):.2f} s",
                     f"{secs[int(0.95 * (len(secs) - 1))]:.2f} s", f"{tokens:.0f}",
                     f"${tokens * 1000 * PRICE[model] / 1e6:.3f}"])
    lines += ["| Model | Exact level | Within one level | Mean error (0-3) | Leads that changed level between runs "
              "| Score spread between runs | Median time | 95th pct time | Input tokens | Cost per 1,000 leads |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    both = [lid for (m, lid) in by if m == "openai" and ("jev", lid) in by]
    same = sum(by[("openai", lid)][0]["level"] == by[("jev", lid)][0]["level"] for lid in both)
    lines += ["", f"The two models gave the same level on {same} of {len(both)} leads ({pct(same, len(both))}), "
              "first run each."]
    lines += ["", "## Accuracy by label", "", "| Label | Leads | OpenAI exact | JEV exact |", "|---|---|---|---|"]
    for i, name in enumerate(NAMES):
        ids = [lid for lid, lab in labels.items() if lab == i and ("openai", lid) in by and ("jev", lid) in by]
        oe = sum(NAMES.index(by[("openai", lid)][0]["level"]) == i for lid in ids)
        je = sum(NAMES.index(by[("jev", lid)][0]["level"]) == i for lid in ids)
        lines.append(f"| {name} | {len(ids)} | {pct(oe, len(ids))} | {pct(je, len(ids))} |")
    lines += ["", "## Same test with each model's most likely level (instead of the rounded score)", "",
              "| Model | Exact level |", "|---|---|"]
    for model in MODELS:
        ids = [lid for (m, lid) in by if m == model and lid in labels]
        hit = sum(NAMES.index(by[(model, lid)][0]["top_level"]) == labels[lid] for lid in ids)
        lines.append(f"| {model} | {pct(hit, len(ids))} |")
    for model in MODELS:
        lines += ["", f"## Where {model} puts each label (rows = label, columns = answer, rounded score)", "",
                  "| Label | " + " | ".join(NAMES) + " |", "|---|" + "---|" * len(NAMES)]
        for i, name in enumerate(NAMES):
            ids = [lid for lid, lab in labels.items() if lab == i and (model, lid) in by]
            cells = [str(sum(by[(model, lid)][0]["level"] == n for lid in ids)) for n in NAMES]
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leads", default=str(HERE / "data" / "leads.csv"))
    ap.add_argument("--labels", default=str(HERE / "data" / "labels.csv"))
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    labels = {}
    if Path(args.labels).exists():
        labels = {r["id"]: NAMES.index(r["label"]) for r in csv.DictReader(open(args.labels))}
    out = HERE / "results.csv"
    if not args.report_only:
        icp = (HERE / "ICP.md").read_text()
        rows = list(csv.DictReader(open(args.leads)))[: args.limit]
        tasks = [(m, run, row, icp) for run in range(1, args.runs + 1) for row in rows for m in MODELS]
        print(f"Scoring {len(rows)} leads x {args.runs} runs x {len(MODELS)} models = {len(tasks)} calls...")
        with ThreadPoolExecutor(args.workers) as pool:
            results = list(pool.map(run_one, tasks))
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, FIELDS)
            w.writeheader()
            w.writerows(results)
    results = list(csv.DictReader(open(out)))
    text = report(results, labels)
    (HERE / "report.md").write_text(text)
    print(text)


if __name__ == "__main__":
    sys.exit(main())
