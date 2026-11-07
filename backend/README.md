# Phishing Coach backend (FastAPI)

Owner: Sunday (AI, tools & evaluation). Wraps Albert's rule engine (`phishhook/`, copied unchanged)
and adds the model layer, evidence checks, payroll policies, `/challenge`, and the eval.

## Run locally

```bash
cd backend
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt
.venv/bin/uvicorn main:app --reload --port 8080      # rules only, no key needed
.venv/bin/python -m pytest -q                        # 35 tests
.venv/bin/python -m eval.run_eval                    # writes eval/results/rules-only.md
```

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
2. Extra link checks: `javascript:` / `data:` links and `https://real.com@evil.example` tricks.
3. Optional model pass: at most 3 extra signs plus a summary. The email is sent as delimited untrusted data.
4. Every quote is re-checked against the email (case/whitespace-tolerant, snapped back to the original text).
   A model quote that isn't in the email is discarded and the result becomes `insufficient_evidence`.
5. Bad model output → one retry → rules-only result with a limitation note. Never an all-clear.
6. `next_action` comes from `data/policies.json` (bank change, employee data, payments, passwords);
   a practice question comes from `phishhook/drill_bank.json`.

## Not done / not verified

- **No real Tinker call has been made from this code.** The OpenAI-compatible endpoint is beta, and its docs
  show checkpoint paths (`tinker://...`) as the model name. Confirm `TINKER_MODEL` with the team's smoke test.
- The fixtures include Albert's 10 samples, which his rules were written against, so the rules-only
  numbers are optimistic. Held-out emails written by someone else are needed.
- Logging records ids, counts and timing only, never email bodies.
