"""Label every lead in data/leads.csv with the ICP.md rubric, written down as rules.

Six must-haves are checked: industry, size, location, outbound sales team, function, seniority.
Each is pass, fail or unknown. A disqualifier makes the lead "No fit".

    Strong fit   6 of 6 pass
    Partial fit  5 of 6 pass (one fails or is unknown)
    Weak fit     1 to 4 pass
    No fit       0 pass, or a disqualifier

data/overrides.csv (id,label,reason) corrects the cases the rules read wrong; each override is
written down with its reason. Run: python3 label_leads.py
"""
import csv
import re
from pathlib import Path

HERE = Path(__file__).parent
NAMES = ["No fit", "Weak fit", "Partial fit", "Strong fit"]

INDUSTRIES = ["software development", "it services", "technology, information and internet",
              "information technology", "computer software", "saas", "staffing and recruiting",
              "data security software", "computer and network security", "internet"]
EUROPE = ["united kingdom", "england", "ireland", "france", "germany", "spain", "italy", "netherlands", "belgium",
          "sweden", "norway", "denmark", "finland", "poland", "portugal", "switzerland", "austria", "czech",
          "romania", "greece", "hungary", "estonia", "latvia", "lithuania", "luxembourg", "scotland", "wales",
          "slovakia", "slovenia", "croatia", "bulgaria", "serbia", "iceland", "europe"]
NORTH_AMERICA = ["united states", "canada", "mexico"]
FUNCTION = re.compile(r"\b(sales|business develop(?:ment|er)|biz ?dev|bd|growth|revenue|rev ?ops|commercial|gtm|"
                      r"go[- ]to[- ]market|partnerships|alliances|account executive)\b", re.I)
SENIOR = re.compile(r"\b(head|director|vp|vice president|chief|c[ers]o|cro|founder|co-founder|cofounder|"
                    r"president|partner|owner|managing director|svp|evp|gm|general manager)\b", re.I)
DISQUALIFY_TITLE = re.compile(r"\b(student|intern|internship|job seeker|looking for|freelance|freelancer)\b", re.I)
DISQUALIFY_INDUSTRY = ["government", "education", "higher education", "non-profit", "nonprofit",
                       "public administration", "armed forces", "e-learning"]
# Vendors that sell lead data, email finding or outbound automation: Evaboot's competitors.
COMPETITORS = re.compile(r"\b(b2b rocket|apollo\.io|zoominfo|lusha|cognism|kaspr|dropcontact|hunter\.io|"
                         r"snov|seamless\.ai|lemlist|clay|phantombuster|waalaxy)\b", re.I)


def employees(row):
    raw = (row["Company employees"] or "").replace(",", "").strip()
    if raw.isdigit():
        return int(raw)
    nums = [int(n) for n in re.findall(r"\d+", (row["Company employee range"] or "").replace(",", ""))]
    return nums[0] if nums else None


def checks(row):
    # "Product owner" is a product role, not a business owner.
    title = re.sub(r"product owner", "product role", row["Job title"], flags=re.I)
    industry = (row["Company industry"] or "").lower()
    location = (row["Company location"] or "").lower()
    size = employees(row)
    sales = (row["Sales team size"] or "").strip()
    result = {
        "industry": None if not industry else any(i in industry for i in INDUSTRIES),
        "size": None if size is None else 11 <= size <= 500,
        "location": None if not location else any(c in location for c in EUROPE + NORTH_AMERICA),
        "outbound team": None if not sales.isdigit() else int(sales) >= 3,
        # Founders and CEOs own sales in an 11-500 company, and ICP.md names Founder as a buyer.
        # Sales engineers are pre-sales technical staff, not the sales function.
        "function": not re.search(r"engineer", title, re.I) and bool(
            FUNCTION.search(title) or re.search(r"\b(founder|co-founder|cofounder|ceo|owner)\b", title, re.I)),
        "seniority": bool(SENIOR.search(title)),
    }
    disqualifiers = []
    if DISQUALIFY_TITLE.search(f"{title} {row['Company']}"):
        disqualifiers.append("student, intern, job seeker or freelancer")
    if size is not None and size > 5000:
        disqualifiers.append("more than 5,000 employees")
    if any(d in industry for d in DISQUALIFY_INDUSTRY):
        disqualifiers.append("government, education or non-profit")
    if COMPETITORS.search(f"{row['Company']} {row['Company description']}"):
        disqualifiers.append("lead-data or outbound vendor (competitor)")
    return result, disqualifiers


def label(row):
    result, disqualifiers = checks(row)
    passes = sum(v is True for v in result.values())
    if disqualifiers:
        return "No fit", "disqualifier: " + "; ".join(disqualifiers)
    level = 3 if passes == 6 else 2 if passes == 5 else 1 if passes >= 1 else 0
    missing = [k for k, v in result.items() if v is not True]
    why = "all six must-haves" if not missing else "fails or unknown: " + ", ".join(
        f"{k} ({'unknown' if result[k] is None else 'no'})" for k in missing)
    return NAMES[level], why


def main():
    leads = list(csv.DictReader(open(HERE / "data" / "leads.csv")))
    overrides = {}
    if (HERE / "data" / "overrides.csv").exists():
        overrides = {r["id"]: r for r in csv.DictReader(open(HERE / "data" / "overrides.csv"))}
    out, counts = [], {n: 0 for n in NAMES}
    for row in leads:
        lab, why = label(row)
        if row["id"] in overrides:
            lab, why = overrides[row["id"]]["label"], "override: " + overrides[row["id"]]["reason"]
        counts[lab] += 1
        out.append({"id": row["id"], "label": lab, "reason": why})
    with open(HERE / "data" / "labels.csv", "w", newline="") as f:
        w = csv.DictWriter(f, ["id", "label", "reason"])
        w.writeheader()
        w.writerows(out)
    print(len(out), "labels:", counts)


if __name__ == "__main__":
    main()
