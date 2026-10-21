"""Build the n8n template JSON for this benchmark. Run: python3 n8n/build_workflow.py"""
import json
import uuid
from pathlib import Path

HERE = Path(__file__).parent
ICP = (HERE.parent / "ICP.md").read_text()
SHEETS_CRED = {"googleSheetsOAuth2Api": {"id": "", "name": "Google Sheets"}}
OPENAI_CRED = {"openAiApi": {"id": "", "name": "OpenAI"}}
JEV_CRED = {"httpHeaderAuth": {"id": "", "name": "Typesafe JEV API key"}}
S = "$('Your settings').first().json"


def node(name, type_, version, position, parameters, **extra):
    return {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "decision-benchmark/" + name)), "name": name, "type": type_,
            "typeVersion": version, "position": position, "parameters": parameters, **extra}


def sticky(name, position, width, height, content, color=7):
    return node(name, "n8n-nodes-base.stickyNote", 1, position,
                {"color": color, "width": width, "height": height, "content": content})


LEVELS = [
    ("No fit", "Fails a disqualifier, or matches none of the must-haves."),
    ("Weak fit", "Matches one must-have. The other must-haves fail or are unknown."),
    ("Partial fit", "Matches most must-haves, but one fails or is unknown."),
    ("Strong fit", "Matches every must-have and no disqualifier."),
]

BUILD_INPUT = """// The same text goes to both models: your ICP, then the lead.
const keys = ['Job title', 'Company', 'Company industry', 'Company employees', 'Company location', 'Company description'];
const lead = keys.map(k => `${k}: ${$json[k] || 'unknown'}`).join('\\n');
return { ...$json, decisionInput: `Ideal customer profile:\\n${$('Your settings').first().json.icp}\\n\\nLead:\\n${lead}` };"""

OPENAI_BODY = """={{ JSON.stringify({
  model: 'gpt-6-luna',
  input: $json.decisionInput,
  questions: [{ type: 'score', name: 'icp_fit', instructions: 'How well does this lead match the ideal customer profile?',
    levels: %s }]
}) }}""" % json.dumps([{"label": n, "description": d} for n, d in LEVELS]).replace('"', "'")

JEV_BODY = """={{ JSON.stringify({
  model: 'jev-latest',
  state: $('Build the input').item.json.decisionInput,
  questions: { icp_fit: { type: 'score', instructions: 'How well does this lead match the ideal customer profile?',
    criteria: %s } }
}) }}""" % json.dumps([f"{n}: {d}" for n, d in LEVELS]).replace('"', "'")

COMPARE = """// Both answers are a score from 0 to 3. Store the score out of 100 and the nearest level.
const levels = ['No fit', 'Weak fit', 'Partial fit', 'Strong fit'];
const row = $('Build the input').item.json;
const openai = $('Ask OpenAI Decisions').item.json.answers[0];
const jev = $json.answers.icp_fit;
const out = { ...row };
delete out.decisionInput;
out['OpenAI score'] = Math.round(openai.score / 3 * 100);
out['OpenAI fit'] = levels[Math.round(openai.score)];
out['JEV score'] = Math.round(jev.score / 3 * 100);
out['JEV fit'] = levels[Math.round(jev.score)];
out['Same level'] = out['OpenAI fit'] === out['JEV fit'] ? 'yes' : 'no';
return out;"""

OVERVIEW = """## Score a lead list with OpenAI and JEV side by side

**Who it's for:** anyone choosing a decision model for lead scoring who wants to test both on their own leads before deciding.

**What it does:** reads every row of a Google Sheet, sends the same input (your ICP + the lead) to the OpenAI Decisions API and to Typesafe's JEV, and writes both scores, both fit levels and a "Same level" column back to the row.

### How to set up
1. Make a Google Sheet with the columns: LinkedIn URL, Job title, Company, Company industry, Company employees, Company location, Company description. An Evaboot export has all of them.
2. Add credentials: **Google Sheets**, **OpenAI**, and **Header Auth** for JEV (name `Authorization`, value `Bearer YOUR_JEV_KEY`).
3. Fill in **Your settings**: the sheet URL (copied while the right tab is open, so it ends with `gid=`) and your ICP.
4. Click **Execute workflow**. Each row gets OpenAI score, OpenAI fit, JEV score, JEV fit and Same level.

### Requirements
An OpenAI API key, a Typesafe JEV key (early access), a Google account.

### How to customize
Change the four fit levels in both scoring nodes. For accuracy, speed, consistency and cost over several runs, use the Python benchmark: github.com/evaboot-labs/openai-decisions-vs-jev"""

nodes = [
    sticky("Template overview", [-760, -300], 520, 820, OVERVIEW),
    sticky("Step 1", [-180, -120], 900, 420,
           "### 1. Read the leads\nYour settings holds the sheet URL and your ICP. Every row of the sheet is one lead."),
    sticky("Step 2", [760, -120], 1300, 420,
           "### 2. Ask both models the same question\nThe same input goes to OpenAI and to JEV, with the same four levels. The scores are stored side by side, and the row is updated in place, matched on LinkedIn URL."),
    node("Test run", "n8n-nodes-base.manualTrigger", 1, [-140, 40], {}),
    node("Your settings", "n8n-nodes-base.set", 3.4, [60, 40], {
        "mode": "manual",
        "assignments": {"assignments": [
            {"id": "sheet", "name": "sheetUrl", "type": "string",
             "value": "https://docs.google.com/spreadsheets/d/REPLACE_WITH_YOUR_SHEET_ID/edit#gid=0"},
            {"id": "icp", "name": "icp", "type": "string", "value": ICP},
        ]}, "options": {}}, executeOnce=True),
    node("Read the leads", "n8n-nodes-base.googleSheets", 4.5, [280, 40], {
        "documentId": {"__rl": True, "mode": "url", "value": f"={{{{ {S}.sheetUrl }}}}"},
        "sheetName": {"__rl": True, "mode": "url", "value": f"={{{{ {S}.sheetUrl }}}}"},
        "options": {}}, credentials=SHEETS_CRED),
    node("Build the input", "n8n-nodes-base.code", 2, [500, 40], {"mode": "runOnceForEachItem", "jsCode": BUILD_INPUT}),
    node("Ask OpenAI Decisions", "n8n-nodes-base.httpRequest", 4.2, [820, 40], {
        "method": "POST", "url": "https://api.openai.com/v1/decisions", "authentication": "predefinedCredentialType",
        "nodeCredentialType": "openAiApi", "sendBody": True, "specifyBody": "json", "jsonBody": OPENAI_BODY,
        "options": {}}, credentials=OPENAI_CRED),
    node("Ask JEV", "n8n-nodes-base.httpRequest", 4.2, [1040, 40], {
        "method": "POST", "url": "https://api.typesafe.ai/v1/systemone", "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth", "sendBody": True, "specifyBody": "json", "jsonBody": JEV_BODY,
        "options": {}}, credentials=JEV_CRED),
    node("Compare the answers", "n8n-nodes-base.code", 2, [1260, 40], {"mode": "runOnceForEachItem", "jsCode": COMPARE}),
    node("Write both scores", "n8n-nodes-base.googleSheets", 4.5, [1480, 40], {
        "operation": "appendOrUpdate",
        "documentId": {"__rl": True, "mode": "url", "value": f"={{{{ {S}.sheetUrl }}}}"},
        "sheetName": {"__rl": True, "mode": "url", "value": f"={{{{ {S}.sheetUrl }}}}"},
        "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": ["LinkedIn URL"], "schema": []},
        "options": {}}, credentials=SHEETS_CRED),
]

order = ["Test run", "Your settings", "Read the leads", "Build the input", "Ask OpenAI Decisions", "Ask JEV",
         "Compare the answers", "Write both scores"]
connections = {a: {"main": [[{"node": b, "type": "main", "index": 0}]]} for a, b in zip(order, order[1:])}
workflow = {"name": "Score a lead list with OpenAI and JEV side by side", "nodes": nodes,
            "connections": connections, "settings": {"executionOrder": "v1"}}
out = HERE / "openai-vs-jev-lead-scoring.json"
out.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n")
print(f"Wrote {out} ({len(nodes)} nodes)")
