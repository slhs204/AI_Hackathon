# Dobby’s Catch (Phishing Coach)

A hackathon project for payroll staff. A Chrome extension checks an open Gmail message, points to the exact words or links that need attention, explains each warning sign in plain language, and suggests a safer next step from the company's payroll procedures.

It never says an email is safe and never authorizes a payment. “No warning signs” is not an all-clear.

## What works now

| Part | Status |
|---|---|
| Chrome extension (Gmail, version 0.3.6) | Built. Simple results, evidence highlights, challenge, practice, title checks, offline demo, and explicit per-session Tinker permission |
| Backend (FastAPI, `backend/`) | Built. `/health`, `/session`, `/analyze`, `/triage`, `/challenge`; demo-token check fails closed |
| Rule engine (`backend/phishhook/`) | Built. 8 detectors plus payroll-specific checks |
| Evidence checks | Built. Every quote shown to the user is checked against the email; unverifiable output becomes “Analysis incomplete” |
| Claude integration | Built and evaluated offline: Claude Haiku 5.5 for inbox triage, Claude Sonnet 5.5 for per-email analysis |
| Private staging on Cloud Run | IAM-protected Tinker revision `phish-staging-ai-3ec6847-a002` serves 100% traffic; post-promotion session and anonymous-denial checks passed. Runtime account, IAM and resource limits preserved |
| Tinker | Stable base model `Qwen/Qwen3-8B` passed real Cloud Run analysis and challenge without an expiring sampler. This proves connectivity, not accuracy |
| Windows demo | Double-click `Start-Demo.cmd`: one-window cloud connector on loopback 8081, no separately managed proxy. `-Local` retains the sampler-backed fallback; see [startup guide](scripts/README.md) |
| Tests | 187 backend tests pass, 1 is skipped; 99 extension tests and Windows PowerShell 5.1 launcher checks pass |
| Chrome/Gmail acceptance | Synthetic T23 analysis and challenge passed; partial extraction correctly flagged. Revoking consent blocked further analysis |

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

For the prepared Windows demo, use [Start-Demo.cmd](Start-Demo.cmd). It starts a connector in one window using your Google Cloud sign-in and the existing cloud app token. The provider key stays in private Cloud Run; the default cloud base model needs no sampler or local checkpoint. Choose the one-click connection in the extension, explicitly allow Tinker, and paste the temporary app token displayed in the window. Startup checks the remote session without inference. Use synthetic emails only; API inference uses credits. The independently reviewed AI revision now serves 100% traffic; see [deployment status](docs/PRIVATE_STAGING.md).

Use `Start-Demo.cmd -Local` only for the previous direct-local fallback. That mode still needs its valid, expiring sampler; it does not renew it automatically.

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
