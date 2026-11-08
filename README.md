# Dobby’s Catch (Phishing Coach)

A hackathon project for payroll staff. A Chrome extension checks an open Gmail message, points to the exact words or links that need attention, explains each warning sign in plain language, and suggests a safer next step from the company's payroll procedures.

It never says an email is safe and never authorizes a payment. “No warning signs” is not an all-clear.

## What works now

| Part | Status |
|---|---|
| Chrome extension (Gmail, version 0.3.4) | Built. Simple result view (Don't pay yet / Check first / Can't tell yet), evidence highlights, challenge flow, practice question, local inbox-title check, local demo mode |
| Backend (FastAPI, `backend/`) | Built. `/health`, `/session`, `/analyze`, `/triage`, `/challenge`; demo-token check fails closed |
| Rule engine (`backend/phishhook/`) | Built. 8 detectors plus payroll-specific checks |
| Evidence checks | Built. Every quote shown to the user is checked against the email; unverifiable output becomes “Analysis incomplete” |
| Claude integration | Built and evaluated offline: Claude Haiku 5.5 for inbox triage, Claude Sonnet 5.5 for per-email analysis |
| Private staging on Cloud Run | IAM-protected service `phish-staging`, run **rules only** (`MODEL_PROVIDER=mock`). The extension refuses paid-model mode |
| Tests | 143 backend tests and 90 extension tests pass. They use stubs; real Chrome/Gmail end-to-end checks are still manual |

## Evaluation (summary)

- Blind set: 200 emails from a public MIT-licensed dataset that nobody on the team tuned to (`fixtures/external/teddyha`).
- Rules only, Gmail view: 18/100 phishing flagged, 5/100 legitimate emails falsely flagged.
- Claude Sonnet 5.5: 100/100 phishing flagged, 24/100 false alarms.
- Claude Haiku 5.5 with prompt v2 and the “pressure words alone are notes” rule (tuning half, recomputed offline): 48/50 phishing flagged, 0/50 false alarms. Not yet confirmed on the held-out test half.

Details: [`backend/eval/results/`](backend/eval/results/) and [`docs/PROGRESS_REPORT.zh-TW.md`](docs/PROGRESS_REPORT.zh-TW.md).

## Repository layout

| Path | What it is |
|---|---|
| [`chrome_extension/`](chrome_extension/) | The Gmail extension. Install, connect and test steps are in its README |
| [`backend/`](backend/) | FastAPI backend, rule engine, model layer, tests and evaluation scripts |
| [`fixtures/`](fixtures/) | Synthetic test emails and the public blind set |
| [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) | Request and response reference between extension and backend |
| [`docs/PRIVATE_STAGING.md`](docs/PRIVATE_STAGING.md) | How to update the private Cloud Run staging service |
| [`docs/TEAM_NOTES.md`](docs/TEAM_NOTES.md) | Open decisions for the team |
| [`PROJECT_SPEC.md`](PROJECT_SPEC.md) | Product spec, design rules and status |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Historical health-check-only deployment example. Do not use it for the real service |

## Run it locally

Backend (rules only, no model calls):

```bash
cd backend
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt
cp .env.example .env    # fill in values; never commit .env
DEMO_API_TOKEN=dev .venv/bin/uvicorn main:app --reload --port 8080
.venv/bin/python -m pytest -q
```

Extension tests:

```bash
node --test chrome_extension/tests/*.test.cjs
```

To try the extension, load `chrome_extension/` with **Load unpacked** at `chrome://extensions` and use **Try demo**, which runs locally and sends nothing. Connecting to the staging backend is described in [`chrome_extension/README.md`](chrome_extension/README.md).

## Limits

This is a prototype. It does not prove that an email is safe, authenticate a sender, replace company approval rules, or authorize payments. Gmail extraction is partial (no raw headers or attachment contents). Use synthetic emails for demos. Keep model API keys on the backend, never in the extension or in Git.
