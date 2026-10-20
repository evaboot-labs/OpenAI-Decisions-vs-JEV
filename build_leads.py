"""Turn Evaboot export JSON files (data/raw-*.json) into data/leads.csv, one row per lead.

Names and LinkedIn URLs are left out on purpose: the benchmark does not use them, and the file is public."""
import csv, glob, json
from pathlib import Path

HERE = Path(__file__).parent
COLS = ["id", "Job title", "Company", "Company industry", "Company employees", "Company employee range",
        "Company location", "Lead location", "Sales team size", "Company description", "Source"]
seen, rows = set(), []
for f in sorted(glob.glob(str(HERE / "data" / "raw-*.json"))):
    data = json.load(open(f))
    for p in data.get("prospects") or []:
        url = p.get("Linkedin URL Public") or p.get("Linkedin URL Unique ID")
        if not url or url in seen:
            continue
        seen.add(url)
        rows.append({
            "Job title": (p.get("Current Job") or "").strip(),
            "Company": p.get("Company Name") or "",
            "Company industry": p.get("Company Industry") or "",
            "Company employees": p.get("Company Employee Exact Count") or "",
            "Company employee range": p.get("Company Employee Range") or "",
            "Company location": p.get("Company Location") or "",
            "Lead location": p.get("Location") or "",
            "Sales team size": p.get("Sales Team Size") or "",
            "Company description": " ".join((p.get("Company Description") or "").split())[:600],
            "Source": data.get("search_name") or Path(f).stem,
        })
for i, r in enumerate(rows, 1):
    r["id"] = f"L{i:03d}"
with open(HERE / "data" / "leads.csv", "w", newline="") as f:
    w = csv.DictWriter(f, COLS)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "leads")
