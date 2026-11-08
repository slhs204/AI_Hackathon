# Dobby’s Catch (Phishing Coach): Project Spec

**Status date: November 8, 2026 (private Cloud Run AI deployed and verified)**

## 1. The idea

We built a Chrome extension that helps payroll staff understand suspicious emails.

Instead of showing only a warning, the tool points to exact evidence and explains a useful next step. The supported email platform is Gmail web. Outlook is not implemented.

The goal is both safer decisions and practical learning. Detection has been measured offline (see section 5); learning outcomes have not been measured.

## 2. Current progress

| Part | Status |
|---|---|
| Google Cloud project and billing | Set up |
| Private Cloud Run staging (`phish-staging`) | IAM-private Tinker revision `phish-staging-ai-3ec6847-a002` serves 100% traffic; base URL verified. Runtime account, IAM and limits preserved; see `docs/PRIVATE_STAGING.md` |
| `GET /health`, `GET /session` | Built |
| `POST /analyze` (rules, extra checks, optional model, evidence check, payroll policy) | Built |
| `POST /triage` (inbox priority from sender, subject, preview) | Built |
| `POST /challenge` | Built; never clears a finding |
| Claude integration (Haiku 5.5 triage, Sonnet 5.5 analysis) | Built and evaluated offline; not enabled on staging |
| Browser extension (Gmail, 0.3.6) | Built: simple result view, evidence highlights, challenge, practice question, local inbox-title check, local demo and explicit session AI permission |
| Evidence highlighting and scan animation | Built |
| Automated tests | 187 backend pass, 1 skip; 99 extension pass; Windows PowerShell 5.1 launcher checks pass |
| Real Chrome/Gmail acceptance test | Synthetic T23 analysis and challenge passed; partial extraction correctly flagged; revoked consent blocked analysis. Broader checklist remains in `chrome_extension/README.md` |

## 3. The user experience

1. The user opens an email and clicks “Check this email.”
2. The extension reads only that email.
3. The backend checks evidence and asks the model for an assessment.
4. The extension highlights the relevant text or link.
5. The user clicks a clue to see why it matters and how to check it.
6. The user can add context, such as “I spoke to this employee yesterday.”
7. The system reassesses the case and offers one short practice question.

Example: “Change my salary account today. Do not call me.”

The tool could highlight “Do not call me” and explain that the request discourages independent verification. The next step is to follow the company's account-change procedure.

“No obvious warning signs” must never be presented as “safe.”

## 4. Technical plan

```text
Chrome extension
    -> One-window authenticated connector on loopback 8081
    -> FastAPI backend on Cloud Run
    -> Approved checks and company policies
    -> Model API
    -> Evidence validation
    -> Highlights, explanations, and learning
```

The model helps explain and assess the email. The harness is the backend code that controls tools, limits calls, and checks the model's output.

Backend checks (run in code, not as model tools):

- Inspect link text and actual destinations without opening the links.
- Compare sender domains with a company-provided list.
- Look up approved payroll verification rules.
- Retrieve reviewed examples and practice questions.

A matching domain does not prove that the sender is trustworthy. An account can be compromised.

## 5. Model plan and results

- Claude Haiku 5.5 (`claude-haiku-5-5`) for `/triage` and Claude Sonnet 5.5 (`claude-sonnet-5-5`) for `/analyze` and `/challenge` remain supported and evaluated offline.
- Tinker (`MODEL_PROVIDER=tinker`) base model `Qwen/Qwen3-8B` passed real private Cloud Run canary analysis (7,922 ms) and challenge (1,453 ms), without an expiring sampler. The Windows launcher defaults to a one-window cloud connector on loopback 8081; the extension requires explicit session permission. Independent review passed; the AI revision serves 100% traffic and retains private IAM and a rules-only rollback tag. These results do not establish model accuracy.
- `Start-Demo.cmd -Local` retains the earlier direct-local sampler fallback. Its checkpoint still expires and requires separate renewal.
- GPT-6.1 Sol was a comparison candidate and has not been tested.

Offline results on a 200-email public blind set (Gmail view): rules only flag 18/100 phishing with 5/100 false alarms; Sonnet 5.5 flags 100/100 phishing with 24/100 false alarms; Haiku 5.5 with prompt v2 and the pressure-words rule flags 48/50 phishing with 0/50 false alarms on the tuning half. The held-out test half still needs one run. Details are in `backend/eval/results/`.

No model fine-tuning or reinforcement learning has been done. User corrections are not automatically trusted training labels.

## 6. API plan

| Endpoint | Purpose | Status |
|---|---|---|
| `GET /health` | Check whether the backend is running | Available |
| `GET /session` | Check the demo token and selected provider mode before sending email | Available |
| `POST /analyze` | Analyze one email | Available |
| `POST /triage` | Sort up to 50 inbox rows by risk | Available |
| `POST /challenge` | Reassess one finding with more context | Available |

The exact JSON contract is in `docs/API_CONTRACT.md`.

The analysis request should include an email ID, sender, subject, text blocks with IDs, and links with IDs and actual URLs.

Each finding should include its evidence reference, a plain-language explanation, and a suggested action. The backend must confirm that the evidence exists in the submitted email.

If evidence cannot be validated, show “Analysis incomplete” and suggest manual verification. Do not turn a failed analysis into an all-clear.

All POST endpoints check `X-Demo-Token` before any model call and fail closed when no token is configured. `X-Require-Rules-Only: 1` makes the backend refuse any non-mock provider.

## 7. Safety and privacy

- Treat email content, extension input, and user comments as untrusted.
- Keep provider keys in Secret Manager, not the browser.
- Use synthetic emails for the demo. Real payroll data needs authorization before it is sent to a model provider.
- Do not put email bodies in normal logs.
- Limit request size, calls, output tokens, tool steps, and time.
- Do not send, delete, or change emails, open suspicious URLs, or run attachments.
- Clear old results when the user selects another email.
- Use readable text, keyboard access, and reduced motion. Do not rely on color alone.

The team lead gives testers the demo token privately. Testers enter it in the extension. Keep it only for that session and rotate it after the demo. It is not a substitute for production login or server-side usage limits.

## 8. Remaining work

| Area | Next step |
|---|---|
| Evaluation | Run the chosen model once on the held-out test half (`--split test`) and record the numbers |
| Staging | Done: independent review passed, AI serves 100% traffic, private base URL and rules-only rollback tag verified |
| Extension | Complete broader Chrome/Gmail checklist beyond the passed synthetic T23 analysis/challenge and consent checks |
| Team | Settle the open items in `docs/TEAM_NOTES.md` |

## 9. Done means

| Check | Status |
|---|---|
| A missing or wrong token cannot trigger model inference | Done (tested) |
| Every displayed clue points to verified evidence | Done (tested) |
| Invalid evidence produces an incomplete result | Done (tested) |
| Email instructions cannot grant new tool permissions | Done: the email is passed as delimited untrusted data; the model has no tools |
| The challenge and short learning exercise work | Done (stub tests) |
| The chosen model works inside Cloud Run | Done: private Tinker revision serves 100% traffic and base session verified |
| The full extension-to-backend flow is demonstrated | Real Chrome synthetic T23 analysis/challenge passed through the one-window connector; partial extraction flagged and consent revocation blocked analysis |
| Test results and limits are written down | Done: `backend/eval/results/`, `docs/PROGRESS_REPORT.zh-TW.md` |

Attachment scanning, automatic blocking, multiple email platforms, dashboards, and model training are outside the first version. Full-inbox scanning is limited to a local keyword check of visible subject lines.
