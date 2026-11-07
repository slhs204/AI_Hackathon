# Notes from the backend side (Sunday, updated 2026-11-08)

Things to decide or change together. Numbers come from `backend/eval/results/rules-only.md`.

## Blind test (new)

200 emails from the public Teddyha dataset (MIT, `fixtures/external/teddyha`), which nobody on the team wrote or
tuned rules to. Rules only: **34/100 phishing flagged when attachment names are sent, 18/100 without them**
(today's extensions don't send attachments); **5/100 legitimate falsely flagged** (all 5 for urgency words).
Sending attachment names from the extension would catch 16 more (malware attachments: 1/13 → 10/13).
Most misses are generic fake-Google/Dropbox/bank mail with look-alike domains the directory doesn't know. The rules
were written for Acme payroll scams, so this mostly measures how much the model has to add. With **Claude Sonnet 5.5** (Gmail view, 2026-11-07): **100/100 phishing flagged, 24/100 legitimate falsely
flagged** (19 of those only because of the model, mostly a single `manipulation_cue` on ordinary account
notifications such as "Contact support if this wasn't you"). 0 model quotes failed verification; median 2.8 s per
email. Core set with Sonnet: 14/14 phishing (the compromised-vendor email the rules miss is now caught), 3/7 false
alarms (rules: 2/7). Trade-off to decide: the model closes the misses but raises false alarms. Proposed fix: tell
the model to add a sign only when the email asks for a risky action, and show model-only weak signs as "low concern".

## Models: Haiku for the inbox, Sonnet per email

As discussed with Albert: `MODEL_PROVIDER=anthropic` uses **Claude Haiku 5.5** for `POST /triage` (sort the inbox by
risk using sender, subject and preview) and **Claude Sonnet 5.5** for `/analyze` and `/challenge`. Model names can be
changed with env vars. Tinker stays available with `MODEL_PROVIDER=tinker` (sponsor credits). Note: I couldn't find
this plan in Albert's v3.1 files, so please confirm.

Privacy: v3.1 chose "scan only on request". Triage should follow the same rule: run it only when the user clicks
something like "Check inbox", and send only sender, subject and the preview line.

## For everyone: one backend

Albert's v3.1 now has its own FastAPI `main.py`, and the repo has `backend/` (merged in PR #1). We should deploy
**one**. Proposal: deploy `backend/`, which already wraps Albert's v3.1 engine unchanged and returns every field his
v3 extension and Outlook pane read (`verdict`, `callback`, `hold_scenario`, `stages`, `tag`, `ai_explanation`),
plus what v3.1 doesn't have yet:

| | Albert v3.1 `main.py` | `backend/` |
|---|---|---|
| Rules (8 detectors, stages, verdict) | yes | same engine, copied unchanged |
| AI | rewords explanations only; its extra flags are dropped on the `/analyze` path | rewords explanations **and** adds up to 3 verified extra signs |
| Checks every AI quote against the email | n/a | yes; unverifiable → "Analysis incomplete" |
| `/challenge` | no | yes |
| Payroll policy as `next_action` | no | yes (`data/policies.json`) |
| Hookline's `{text,url}` links / `finding_id` challenge | no | yes |
| Fixes for the demo-email misses below | no | yes (`app/tools/payroll_checks.py`) |
| Token fail closed, CORS for Gmail + Outlook | yes | yes (aligned to v3.1) |
| Web demo pages, `.eml` upload, `/api/report`, Outlook taskpane files | yes | no: keep serving those from Albert's app |

## For everyone: one contract

Albert's prototype and Jenessa's Hookline send and expect slightly different JSON. The backend accepts
both today (see `docs/API_CONTRACT.md`), so nothing is blocked. We should still pick one shape before
the demo so nobody is surprised.

## For Albert (v3 extension)

Point the v3 extension's backend URL at `backend/` (locally `DEMO_API_TOKEN=dev uvicorn main:app --port 8080`).
It sends `{blocks, links:{block_id,display_text,href}}` and reads `verdict/callback/stages/tag`, all supported.
Not tried in a browser yet.

## For Jenessa (Hookline)

To switch `background.js` from mock to the real backend:

1. `MOCK_MODE = false` and `API_BASE_URL = "<Cloud Run URL from Albert>"`.
2. Send the demo token. In `callBackend()`:
   ```js
   headers: { "Content-Type": "application/json", "X-Demo-Token": demoToken },
   ```
   (`demoToken` entered by the tester once and kept in memory, like Albert's prototype does.)
3. Add the exact Cloud Run host to `manifest.json` `host_permissions`.
4. Nothing else should need changing: findings now carry `title`, `evidence.quote`, `explanation`,
   `next_action`; challenge replies carry `explanation` and `next_action`.
5. Findings with `evidence.kind = "metadata"` (sender domain, Reply-To) have a `quote` but no `block_id`.
   Your highlighter already returns "No valid block and quote" for those, which is correct: show the card
   without a highlight.
6. Optional: `analysis.practice` has a reviewed practice email (from Albert's drill bank) if you want to
   replace the fixed practice question.

## For Albert (rule engine / deployment)

Gaps found by the eval, still present in v3.1. I did **not** edit `engine.py`; the backend patches them in
`backend/app/tools/payroll_checks.py` until you decide.

1. **"Please change my salary account today" is not a payment request** for `PAYMENT_PATTERNS`. That's
   our own demo email, so the hook would show only "urgency" without the patch.
2. **`acme-payroll-support.com` is not flagged**: the brand-inside-domain check needs the whole
   "acmecorp". Domains containing just "acme" slip through.
3. **Missed entirely:** `h-compromised-vendor` (real vendor domain, "we have moved banks ... new account
   ... routing 011000138"). No rule pattern matches; this is the case the model is for.
4. **False alarms:** a real CFO email saying "URGENT: payroll cutoff today" and the real vendor's
   "our bank details have not changed" notice both get flagged (urgency / keyword match).
5. Fixed in v3.1: `/analyze` now fails closed and uses `hmac.compare_digest`. Still open in v3.1:
   `/api/analyze` (web demo) calls the LLM without a token when a key is set. Fine on a laptop; don't expose it
   publicly with a key configured.
6. Deployment: `backend/Dockerfile` should work with the `gcloud run deploy --source backend` flow in
   DEPLOYMENT.md (not tried yet; I have no GCP access). Secrets needed: `DEMO_API_TOKEN`, plus `TINKER_API_KEY` (env `MODEL_PROVIDER=tinker`,
   `TINKER_MODEL=<value from the smoke test>`) or `ANTHROPIC_API_KEY` (env `MODEL_PROVIDER=anthropic`).

## Open questions

- Which Tinker model? Proposal: compare a cheap one (e.g. Qwen3.5-9B) and a strong one (e.g. Kimi-K2.6)
  with `python -m eval.run_eval --model`. Each full eval costs well under $1.
- Does the OpenAI-compatible Tinker endpoint accept a base model name, or only a `tinker://` checkpoint
  path? `python -m eval.smoke_tinker` answers this in one run.
- Held-out test emails: ideally written by someone who hasn't seen the rules.
