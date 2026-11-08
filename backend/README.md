# Phishing Coach backend (FastAPI)

Owner: Sunday (AI, tools & evaluation). Wraps Albert's rule engine (`phishhook/`, with bounded bank-negation/redirection repairs)
and adds the model layer, evidence checks, payroll policies, `/challenge`, and the eval.

The prepared Windows demo now defaults to a one-window authenticated connector on loopback 8081, reaching IAM-private Cloud Run with Tinker base model `Qwen/Qwen3-8B`; no local sampler is needed. The repaired revision `phish-staging-p1-d08fe1b-a004` now serves 100% traffic; P1 canary checks passed before promotion. Promoted-base session/guard checks and the 57-assertion runtime audit passed separately. See [startup](../scripts/README.md) and [deployment status](../docs/PRIVATE_STAGING.md).

Current verification: 238 backend tests passed with 1 skipped. Passing evidence for the unchanged 99 extension tests and Windows PowerShell 5.1 launcher checks is reused. Real Chrome with extension 0.3.6 passed synthetic T23 analysis and challenge, correctly flagged partial extraction, and blocked analysis after consent revocation.

## Run locally

```bash
cd backend
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt
DEMO_API_TOKEN=dev .venv/bin/uvicorn main:app --reload --port 8080   # rules only; send X-Demo-Token: dev
.venv/bin/python -m pytest -q                        # backend tests
.venv/bin/python -m eval.run_eval                    # writes eval/results/rules-only.md
.venv/bin/python -m eval.run_eval --set blind        # 200 public MIT examples; existing test has historical exposure
.venv/bin/python -m eval.smoke_tinker --preflight    # configuration only; no inference
.venv/bin/python -m eval.smoke_tinker --allow-paid   # explicit tiny JSON + synthetic analysis
.venv/bin/python -m eval.smoke_anthropic             # first real Haiku + Sonnet calls (needs ANTHROPIC_API_KEY)
```

Full request/response reference: [`docs/API_CONTRACT.md`](../docs/API_CONTRACT.md).
Open issues for the team: [`docs/TEAM_NOTES.md`](../docs/TEAM_NOTES.md).

## Files

| Path | What it does |
|---|---|
| `main.py` | FastAPI app: routes, CORS, body-size limit, demo-token check, "no token → no paid model" |
| `connector.py` | Foreground loopback connector: local token/AI-permission checks, Google IAM authentication, fixed private Cloud Run upstream and validated responses |
| `app/schemas.py` | Request/response shapes and limits; accepts Albert's and Hookline's link formats |
| `app/analyze.py` | The `/analyze` pipeline (rules → extra checks → model → verify → policies) |
| `app/triage.py` | `/triage`: rules on sender/subject/preview, then the triage model (Haiku) may raise priorities |
| `app/challenge.py` | `/challenge`: reassess one finding; never clears it |
| `app/evidence.py` | Verifies every quote against the email and snaps it to the exact original text |
| `app/llm.py` | The only code that calls a model (Tinker or Claude: Haiku for triage, Sonnet for analysis); structured outputs, timeout, refusal handling, one retry |
| `app/prompts.py` | System prompts; the email is passed as delimited untrusted data |
| `app/config.py` | Env settings and loading of the JSON data files |
| `app/tools/extra_links.py` | `javascript:` links and `real.com@evil.example` tricks |
| `app/tools/payroll_checks.py` | "change my salary account" and company-name-in-domain checks the engine misses |
| `app/tools/lookup.py` | Payroll policy lookup and practice question from the drill bank |
| `data/policies.json` | Synthetic Acme payroll procedures (source of `next_action`) |
| `phishhook/` | Albert's rule engine (v3.1), with bounded bank-negation/redirection repairs |
| `eval/run_eval.py` | Runs all fixtures in "full headers" and "Gmail-visible" views, writes `eval/results/` |
| `eval/smoke_tinker.py` | One tiny call + one full analysis to prove the Tinker setup works |
| `eval/smoke_anthropic.py` | Haiku triage of a 3-email inbox + one Sonnet analysis |
| `tests/` | Evidence, pipeline, API/token, fail-closed, rubric, connector, Hookline compatibility and container permissions; 238 pass, 1 skip |
| `../fixtures/` | `build_fixtures.py` (core set) and `convert_teddyha.py` (blind set from `external/teddyha`, MIT) |

## Environment

| Variable | Meaning |
|---|---|
| `MODEL_PROVIDER` | `mock` (default: no model call), `tinker`, or `anthropic` |
| `ANTHROPIC_API_KEY` | For `anthropic`. From Secret Manager. |
| `ANTHROPIC_TRIAGE_MODEL` / `ANTHROPIC_ANALYSIS_MODEL` | Defaults `claude-haiku-5-5` (for `/triage`) and `claude-sonnet-5-5` (for `/analyze`, `/challenge`) |
| `ANTHROPIC_FALLBACKS` | Default `1`: Sonnet requests use the server-side refusal fallback (`fallbacks: "default"`). `0` turns it off. |
| `DEMO_API_TOKEN` | Required header `X-Demo-Token` on POST routes. **Fail closed:** unset → POST routes return 503 (same as Albert's v3.1). |
| `TINKER_API_KEY` | From Secret Manager. Never in the extension or Git. |
| `TINKER_MODEL` | Cloud deployment: verified base model `Qwen/Qwen3-8B`, no sampler expiry. `-Local` fallback: separately prepared expiring sampler path |
| `TINKER_BASE_URL` | Optional; defaults to Tinker's documented OpenAI-compatible endpoint |
| `ALLOWED_ORIGINS` | CORS, comma-separated; default Gmail + Outlook web origins. Chrome extension origins are allowed. |
| `MODEL_TIMEOUT_S`, `MODEL_MAX_TOKENS` | Defaults 30 s and 4000 output tokens (thinking counts toward the cap) |

## Endpoints

- `GET /health`
- `POST /analyze`: same request and response as Albert's `engine.analyze_contract`
  (`sender`, `subject`, `blocks`, `links`, optional `reply_to`, `authentication_results`, `attachments`).
  Added response fields (extensions may ignore them): `finding.source` (`rules`/`tool`/`model`),
  `finding.evidence_verified`, `finding.policy_id`, `summary`, `policies`, `practice`, `model`, `elapsed_ms`.
- `POST /triage`: `{emails:[{email_id, sender, subject, snippet}]}` (max 50) → one priority
  (`high`/`medium`/`low`) and reason per email. Rules first; the triage model may raise a priority, never lower it.
  Sender, subject and preview only, and only when the user asks.
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

## Evaluation and verification limits

- The frozen Qwen-assisted Gmail test warned on 49/50 phishing-labelled and 2/50 legitimate-labelled inputs. Rules alone warned on 12/50 and 1/50 respectively. Every input remained incomplete. The [evaluation report](../docs/QWEN_EVALUATION.md) owns current results, method, confidence intervals, paid-call accounting and remaining errors; historical Claude/core results remain in `eval/results/`.
- Tinker defaults analysis to prompt v3; other providers retain their existing default. Explicit `--prompt` selects v1/v2/v3 for evaluation. No model-only, sender-authentication, malware-inspection or payment-approval claim follows from the figures.
- The retained `-Local` fallback alone uses the earlier expiring sampler and requires separate renewal; see [Windows startup](../scripts/README.md).
- Logging records ids, counts and timing only, never email bodies.

## Fail-closed staging contract

- `X-Require-Rules-Only: 1` on any POST rejects with 409 before provider selection unless
  `MODEL_PROVIDER=mock`. The retained legacy staging selection uses this guard.
- Both the default cloud connector and direct-local fallback require explicit Tinker permission and use `X-Require-Tinker: 1`; a provider mismatch returns 409 before any model selection. Transport retries are disabled for Tinker; malformed model JSON still has the existing one correction attempt. No inference runs on normal launcher startup.
- `AnalyzeRequest.extraction_complete` (default `true`) describes extraction of the submitted
  visible content, not authenticity. Gmail DOM clients should send `false` when headers,
  attachments, or full content are unavailable. `extraction_limitations` accepts up to ten
  strings (300 characters each). Partial extraction, missing body/sender, and failed AI review
  set `analysis_complete=false` and `assessment=insufficient_evidence`.
- Sender identity remains `unknown` without a warning, including known directory domains:
  displayed addresses and supplied headers are not independent authentication. The final
  rubric therefore does not grant `pay` merely because rules found no signs.
- Valid JSON with a malformed analysis/challenge/triage shape retries once, then preserves
  rules-only results with the model-unavailable label. No provider calls are made by tests.
- Pressure findings can become notes when visible text has no risky action and no links or known attachments, including partial extraction and retained identity warnings. Limitations state the visible scope; partial results remain incomplete and never authorize payment.


P1 Qwen-assisted evaluation is complete: the frozen test run warned on 49/50 phishing-labelled and 2/50 legitimate-labelled public inputs. All 100 analyses remained incomplete under Gmail extraction limits. Known routine-content errors were repaired on development cases; remaining errors and historical test exposure are disclosed in the [evaluation report](../docs/QWEN_EVALUATION.md). The [P0 acceptance record](../docs/P0_ACCEPTANCE.md) remains historical integration evidence.

## Reproducing evaluation

Paid evaluation requires an explicit journal path; use a unique tag to preserve previous reports. This example is a recipe, not authorization to repeat the recorded final test:

```bash
MODEL_PROVIDER=tinker TINKER_MODEL=Qwen/Qwen3-8B .venv/bin/python -m eval.run_eval --model --set blind --split tune --views gmail --workers 3 --prompt v3 --tag my-development-run --journal ../work/my-development-run.jsonl
```

Supply the provider key through the existing process environment. The runner validates split IDs, fingerprints source/data/prompt/configuration, records attempts before transmission and flushes completions immediately. Reusing a matching journal skips completed cases; configuration mismatches or uncertain attempts block automatic replay. An interrupted final test must be reported inconclusive rather than rerun. Journals belong outside the source distribution and contain only public/synthetic evaluation content, never provider credentials or raw model replies.
