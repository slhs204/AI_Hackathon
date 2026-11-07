# API contract: extension ↔ backend

Status: **draft for team review** (Sunday, updated 2026-11-08). The backend in `backend/` implements this today
and serves all three clients: Albert's v3.1 extension / Outlook pane, Albert's older prototype, and Jenessa's Hookline.
Run `cd backend && .venv/bin/uvicorn main:app --port 8080` and open `http://localhost:8080/docs`
for the live schema.

All POST routes need header `X-Demo-Token: <token>`. **Fail closed** (same as Albert's v3.1): if the server has no
`DEMO_API_TOKEN` configured, POST routes return 503; a wrong or missing token returns 401. Locally, start the
server with `DEMO_API_TOKEN=dev` and send `X-Demo-Token: dev`.

## `GET /health`

```json
{"status": "ok", "service": "phishing-coach", "model": "rules-only"}
```

## `POST /analyze`

### Request

```json
{
  "email_id": "gmail-abc123",
  "sender": {"name": "Payroll Support", "address": "support@example.test"},
  "subject": "Urgent account update",
  "blocks": [{"id": "b1", "text": "Hello, Please change my salary account today."}],
  "links": [{"id": "l1", "text": "Review", "url": "https://example.test/x"}],

  "reply_to": "",                 // optional, Gmail DOM can't read it today
  "authentication_results": "",   // optional, same
  "attachments": [{"name": "invoice.html"}]   // optional
}
```

- Links may use **either** `{id, text, url}` (Hookline) **or** `{id, block_id, display_text, href}` (Albert).
  If `block_id` is missing, the backend uses the first block that contains the link text.
- Limits: 200 blocks, 50 links, 20 000 characters of text in total (one block may hold all of it). Over the limit: HTTP 422.

### Response

```json
{
  "analysis_id": "analysis-3142737833",
  "email_id": "demo-001",
  "assessment": "needs_verification",        // or insufficient_evidence | no_obvious_indicators
  "analysis_complete": true,
  "risk_score": 44, "risk_level": "medium", "payroll_weighted": false,
  "scam_type": "Suspicious email",
  "summary": "Asks you to change where someone's pay goes.",   // empty in rules-only mode
  "disclaimer": "No warning signs found does not mean the email is safe.",
  "findings": [
    // f1–f4 (urgency_pressure: "Urgent", "today", "urgent", "Do not tell") omitted here
    {
      "id": "f5",
      "category": "payment_or_data_request",
      "title": "Asks for money, bank changes, data or a login",
      "evidence": {"kind": "text", "block_id": "b1", "quote": "change my salary account"},
      "explanation": "Why it matters ...",
      "next_action": "How to check ... (from the company policy)",
      "points": 20,
      "source": "tool",               // rules | tool | model
      "evidence_verified": true,
      "policy_id": "bank_account_change"
    }
  ],
  "recommended_actions": ["Do not send money or change bank details. Call ..."],
  "limitations": ["Displayed sender details do not establish sender authenticity.", "..."],
  "policies": [{"id": "bank_account_change", "title": "...", "steps": ["..."]}],
  "practice": {"id": "...", "category": "bank_change", "subject": "...", "body": "...", "answer": "report", "lesson": "..."},
  "model": "rules-only",
  "elapsed_ms": 3,

  // engine v3.1 fields, read by Albert's v3 extension and Outlook pane
  "verdict": {"key": "verify", "label": "Call back first"},      // pay | verify | stop
  "callback": {"name": "...", "role": "vendor", "phone": "...", "source": "vendor master file"},  // or null
  "hold_scenario": "bank_change",                                  // or null
  "stages": [
    {"stage": "subject", "score": 24, "flags": [{"n": 1, "category": "urgency_pressure", "points": 8, "tags": ["urgent"], "finding_ids": ["f1"]}]},
    {"stage": "body", "score": 36, "flags": [{"n": 1, "category": "payment_or_data_request", "points": 20, "tags": ["bank change"], "finding_ids": ["f5"]}]}
  ],
  "ai_summary": null                                               // = summary when the model ran
}
```

Each finding also carries `tag` (short chip text such as `"bank change"`, `"look-alike domain"`) and, when the
model ran, `ai_explanation` (a plain-English rewording; the rule's `explanation` stays).
`stages[].flags[].finding_ids` always point at ids in `findings`. The backend's extra findings are added to the
right stage. `verdict` is recomputed after the extra findings: a payment request or an incomplete analysis is
never "OK to proceed".

**Evidence rules (important for highlighting):**

| `evidence.kind` | Fields | Can the extension highlight it? |
|---|---|---|
| `text` | `block_id`, `quote` | Yes. `quote` is an exact, case-sensitive substring of that block. |
| `link` | `link_id`, plus `block_id` + `quote` (the link text) when the link text is in a block | Yes, when `block_id` is present |
| `metadata` | `field` (`sender.address`, `sender.name`, `reply_to`, `subject`, `authentication_results`, `attachments`), `value`, `quote` (= value) | No: show the card with the quote, no highlight |

Every quote is verified against the request before it is returned. Model claims that can't be verified are
removed and the result becomes `insufficient_evidence` ("Analysis incomplete, verify manually").

**Points and the hook:** like the rule engine, only the first finding of each category has `points > 0`.
Show one hook piece per finding with `points > 0`, or one per finding. That's a UI decision; both work.

**Categories:** `sender_impersonation`, `reply_to_mismatch`, `authentication_failure`, `authority_impersonation`,
`deceptive_link`, `risky_attachment`, `urgency_pressure`, `payment_or_data_request`, `manipulation_cue` (model only).

## `POST /challenge`

### Request (either form)

```json
{"email": { ...same as /analyze... }, "finding_id": "f1", "context": "I called Maria on her desk phone."}
```
```json
{"email": { ... }, "finding": { ...whole finding object... }, "user_context": "..."}
```

With only `finding_id`, the backend re-runs the free rules-only analysis to find it. That works for rule
and tool findings. For model findings (`source: "model"`), send the whole `finding`. Unknown id: HTTP 422.

### Response

```json
{
  "finding_id": "f1",
  "assessment": "less_concerning",          // or still_concerning. Never "safe".
  "message": "That context helps ...",
  "still_unresolved": "... Procedure: Changing an employee's or vendor's bank details — ...",
  "next_action": "Don't change anything from this email. Call ...",
  "explanation": "message + still_unresolved (the one text Hookline shows)",
  "model": "rules-only"
}
```

A challenge updates the current view only. It is not stored and is never used as a training label.
