# Notes from the backend side (Sunday, 2026-11-07)

Things to decide or change together. Numbers come from `backend/eval/results/rules-only.md`.

## For everyone: one contract

Albert's prototype and Jenessa's Hookline send and expect slightly different JSON. The backend accepts
both today (see `docs/API_CONTRACT.md`), so nothing is blocked. We should still pick one shape before
the demo so nobody is surprised.

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

Gaps found by the eval. I did **not** edit `engine.py`; the backend patches them in
`backend/app/tools/payroll_checks.py` until you decide.

1. **"Please change my salary account today" is not a payment request** for `PAYMENT_PATTERNS`. That's
   our own demo email, so the hook would show only "urgency" without the patch.
2. **`acme-payroll-support.com` is not flagged**: the brand-inside-domain check needs the whole
   "acmecorp". Domains containing just "acme" slip through.
3. **Missed entirely:** `h-compromised-vendor` (real vendor domain, "we have moved banks ... new account
   ... routing 011000138"). No rule pattern matches; this is the case the model is for.
4. **False alarms:** a real CFO email saying "URGENT: payroll cutoff today" and the real vendor's
   "our bank details have not changed" notice both get flagged (urgency / keyword match).
5. The prototype's `/api/analyze` calls the LLM **without checking the demo token**, and the token is
   compared with `!=` (timing-safe compare is better). The FastAPI backend fixes both.
6. Deployment: `backend/Dockerfile` should work with the `gcloud run deploy --source backend` flow in
   DEPLOYMENT.md (not tried yet; I have no GCP access). Secrets needed: `TINKER_API_KEY`, `DEMO_API_TOKEN`; plus env `MODEL_PROVIDER=tinker`,
   `TINKER_MODEL=<value from the smoke test>`.

## Open questions

- Which Tinker model? Proposal: compare a cheap one (e.g. Qwen3.5-9B) and a strong one (e.g. Kimi-K2.6)
  with `python -m eval.run_eval --model`. Each full eval costs well under $1.
- Does the OpenAI-compatible Tinker endpoint accept a base model name, or only a `tinker://` checkpoint
  path? `python -m eval.smoke_tinker` answers this in one run.
- Held-out test emails: ideally written by someone who hasn't seen the rules.
