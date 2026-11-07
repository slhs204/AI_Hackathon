# Phishing Coach backend (FastAPI)

Owner: Sunday (AI, tools & evaluation). Wraps Albert's rule engine (`phishhook/`, copied unchanged)
and adds the model layer, evidence checks, payroll policies, `/challenge`, and the eval.

## Run locally

```bash
cd backend
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt
.venv/bin/uvicorn main:app --reload --port 8080      # rules only, no key needed
.venv/bin/python -m pytest -q                        # 45 tests
.venv/bin/python -m eval.run_eval                    # writes eval/results/rules-only.md
.venv/bin/python -m eval.smoke_tinker                # first real Tinker call (needs key + model)
```

Full request/response reference: [`docs/API_CONTRACT.md`](../docs/API_CONTRACT.md).
Open issues for the team: [`docs/TEAM_NOTES.md`](../docs/TEAM_NOTES.md).

## Files

| Path | What it does |
|---|---|
| `main.py` | FastAPI app: routes, CORS, body-size limit, demo-token check, "no token → no paid model" |
| `app/schemas.py` | Request/response shapes and limits; accepts Albert's and Hookline's link formats |
| `app/analyze.py` | The `/analyze` pipeline (rules → extra checks → model → verify → policies) |
| `app/challenge.py` | `/challenge`: reassess one finding; never clears it |
| `app/evidence.py` | Verifies every quote against the email and snaps it to the exact original text |
| `app/llm.py` | The only code that calls Tinker; timeout, token cap, JSON parsing, one retry |
| `app/prompts.py` | System prompts; the email is passed as delimited untrusted data |
| `app/config.py` | Env settings and loading of the JSON data files |
| `app/tools/extra_links.py` | `javascript:` links and `real.com@evil.example` tricks |
| `app/tools/payroll_checks.py` | "change my salary account" and company-name-in-domain checks the engine misses |
| `app/tools/lookup.py` | Payroll policy lookup and practice question from the drill bank |
| `data/policies.json` | Synthetic Acme payroll procedures (source of `next_action`) |
| `phishhook/` | Albert's rule engine, copied unchanged |
| `eval/run_eval.py` | Runs all fixtures in "full headers" and "Gmail-visible" views, writes `eval/results/` |
| `eval/smoke_tinker.py` | One tiny call + one full analysis to prove the Tinker setup works |
| `tests/` | 45 tests: evidence, pipeline, API/token, Hookline compatibility |
| `../fixtures/` | `build_fixtures.py` turns Albert's .eml samples + handwritten cases into requests |

## Environment

| Variable | Meaning |
|---|---|
| `MODEL_PROVIDER` | `mock` (default: no model call) or `tinker` |
| `DEMO_API_TOKEN` | Required header `X-Demo-Token` on POST routes. If unset, the paid model is **disabled** even when `MODEL_PROVIDER=tinker`. |
| `TINKER_API_KEY` | From Secret Manager. Never in the extension or Git. |
| `TINKER_MODEL` | The model/checkpoint the team's smoke test proved works (not yet confirmed here) |
| `TINKER_BASE_URL` | Optional; defaults to Tinker's documented OpenAI-compatible endpoint |
| `ALLOWED_ORIGINS` | CORS, comma-separated; default `https://mail.google.com`. Chrome extension origins are allowed. |
| `MODEL_TIMEOUT_S`, `MODEL_MAX_TOKENS` | Defaults 30 s and 1500 tokens |

## Endpoints

- `GET /health`
- `POST /analyze`: same request and response as Albert's `engine.analyze_contract`
  (`sender`, `subject`, `blocks`, `links`, optional `reply_to`, `authentication_results`, `attachments`).
  Added response fields (extensions may ignore them): `finding.source` (`rules`/`tool`/`model`),
  `finding.evidence_verified`, `finding.policy_id`, `summary`, `policies`, `practice`, `model`, `elapsed_ms`.
- `POST /challenge`: `{email, finding, user_context}` → `{finding_id, assessment: still_concerning|less_concerning,
  message, still_unresolved, next_action, model}`. Never clears a finding; never stored or used for training.

## How a result is built

1. Albert's 8 rule detectors.
2. Extra checks: `javascript:` / `data:` links, `https://real.com@evil.example` tricks, payroll wording
   ("change my salary account"), and the company name inside an unknown sender domain.
3. Optional model pass: at most 3 extra signs plus a summary. The email is sent as delimited untrusted data.
4. Every quote is re-checked against the email (case/whitespace-tolerant, snapped back to the original text).
   A model quote that isn't in the email is discarded and the result becomes `insufficient_evidence`.
5. Bad model output → one retry → rules-only result with a limitation note. Never an all-clear.
6. `next_action` comes from `data/policies.json` (bank change, employee data, payments, passwords);
   a practice question comes from `phishhook/drill_bank.json`.

## Not done / not verified

- **No real Tinker call has been made from this code.** The OpenAI-compatible endpoint is beta, and its docs
  show checkpoint paths (`tinker://...`) as the model name. Confirm `TINKER_MODEL` with the team's smoke test.
- 23 fixtures: Albert's 10 samples (his rules were written against them, so optimistic), 4 extra cases,
  and 9 harder cases written to probe false alarms and misses. Rules-only today: 13/14 phishing flagged,
  2/7 legitimate emails falsely flagged, 1 miss (a real vendor account asking to move banks).
  Held-out emails written by someone who hasn't seen the rules are still needed.
- Logging records ids, counts and timing only, never email bodies.
