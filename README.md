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
| Private staging on Cloud Run | IAM-protected Tinker revision `phish-staging-p2-ai-b3b3e19-a005` serves 100% traffic after app-token rotation; unchanged P1 image and historical P1 canary/evaluation evidence retained; current session and rotated-token checks passed without inference |
| Tinker | Stable base model `Qwen/Qwen3-8B` passed real Cloud Run analysis and challenge without an expiring sampler. The Qwen-assisted frozen test warned on 49/50 phishing-labelled and 2/50 legitimate-labelled inputs; see the evaluation report |
| Windows demo | Double-click `Start-Demo.cmd`: one-window cloud connector on loopback 8081, no separately managed proxy. `-Local` retains the sampler-backed fallback; see [startup guide](scripts/README.md) |
| Tests | 238 backend tests pass, 1 is skipped; 110 extension tests and Windows PowerShell 5.1 launcher checks pass |
| Chrome/Gmail acceptance | Synthetic T23 analysis and challenge passed; partial extraction correctly flagged. Revoking consent blocked further analysis |

## Evaluation (summary)

The Qwen-assisted pipeline matched 97/100 labels in one frozen Gmail-view test: 49/50 phishing-labelled inputs warned, 2/50 legitimate-labelled inputs falsely warned. Rules alone warned on 12/50 phishing and 1/50 legitimate inputs on that same test. All inputs remained incomplete; no result authenticated a sender or approved payment.

In-sample development false alarms fell from 44/50 to 0/50 while warned phishing cases fell from 50/50 to 49/50. The 100-case test comes from one public MIT dataset and had historical Anthropic/rule exposure; it is not a newly untouched or real-world benchmark. See [full metrics, confidence intervals, errors and provenance](docs/QWEN_EVALUATION.md). Historical Claude results remain in [stored reports](backend/eval/results/).

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

For the prepared Windows demo, use [Start-Demo.cmd](Start-Demo.cmd). It starts a connector in one window using your Google Cloud sign-in and the existing cloud app token. The provider key stays in private Cloud Run; the default cloud base model needs no sampler or local checkpoint. Choose the one-click connection in the extension, explicitly allow Tinker, and paste the temporary loopback token displayed in the window. Startup checks the remote session without inference. Use synthetic emails only; API inference uses credits. P2 serves the unchanged P1 image at 100% traffic after rotating the cloud app token to version `2` and disabling version `1`; restart cached connectors and reconnect with a new temporary token; see [deployment status](docs/PRIVATE_STAGING.md).

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


P1 Qwen-assisted evaluation is complete: the frozen test run warned on 49/50 phishing-labelled and 2/50 legitimate-labelled public inputs. All 100 analyses remained incomplete under Gmail extraction limits. Known routine-content errors were repaired on development cases; remaining errors and historical test exposure are disclosed in the [evaluation report](docs/QWEN_EVALUATION.md). The [P0 acceptance record](docs/P0_ACCEPTANCE.md) remains historical integration evidence.


The cloud app token is used only by the connector and is never pasted into the extension. Paste only the temporary loopback token displayed by the launcher.
