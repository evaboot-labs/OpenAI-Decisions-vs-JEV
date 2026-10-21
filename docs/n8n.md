# Run the comparison in n8n

The n8n workflow scores every lead in a Google Sheet with the OpenAI Decisions API and
Typesafe JEV, and writes both scores back to the row. No code to run.

File: [`n8n/openai-vs-jev-lead-scoring.json`](../n8n/openai-vs-jev-lead-scoring.json)

## 1. Put your leads in a Google Sheet

One row per lead, with these columns: `LinkedIn URL`, `Job title`, `Company`,
`Company industry`, `Company employees`, `Company location`, `Company description`.
An Evaboot export of a Sales Navigator search has all of them.

Copy the sheet URL while the right tab is open, so it ends with `gid=...`.

## 2. Import the workflow

In n8n, open an empty workflow, then either:

- paste the JSON onto the canvas (open the raw file, copy all, paste), or
- use **... > Import from File** and pick the downloaded JSON.

You get eight nodes: Test run, Your settings, Read the leads, Build the input,
Ask OpenAI Decisions, Ask JEV, Compare the answers, Write both scores.

## 3. Add three credentials

| Node | Credential | What to enter |
|---|---|---|
| Read the leads, Write both scores | Google Sheets (OAuth2) | Sign in with the Google account that owns the sheet |
| Ask OpenAI Decisions | OpenAI | Your key from https://platform.openai.com/api-keys |
| Ask JEV | Header Auth | Name `Authorization`, value `Bearer YOUR_JEV_KEY` (key from https://console.typesafe.ai/keys, early access) |

## 4. Fill in Your settings

Open the **Your settings** node:

- `sheetUrl`: the URL from step 1 (with `gid=`).
- `icp`: your ideal customer profile. Start from [`ICP.md`](../ICP.md) and replace it with yours.

## 5. Run it

Click **Execute workflow**. Each row gets five new columns: `OpenAI score`, `OpenAI fit`,
`JEV score`, `JEV fit` and `Same level`.

Look at the rows where `Same level` is `no` first: that is where the two models disagree
about your profile.

For accuracy against your own labels, consistency over runs, speed and cost, run the Python
benchmark instead (see the README).
