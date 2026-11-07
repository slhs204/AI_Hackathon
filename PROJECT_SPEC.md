# Phishing Coach: Project Spec

**Status date: November 7, 2026**

## 1. The idea

We are building a Chrome extension that helps payroll staff understand suspicious emails.

Instead of showing only a warning, the tool will point to exact evidence and explain a useful next step. The first planned email platform is Gmail web. The team still needs to confirm this target.

The goal is both safer decisions and practical learning. There is no measured detection accuracy or learning result yet.

## 2. Current progress

| Part | Status |
|---|---|
| Google Cloud project and billing | Set up |
| Cloud Run backend | Deployed |
| `GET /health` | Tested: HTTP 200 |
| Secret Manager setup | Completed for existing demo credentials |
| Email-analysis endpoint | Not built |
| Claude or OpenAI integration | Not built |
| Browser extension | Not built |
| Evidence highlighting and hook animation | Not built |
| Challenge flow and practice question | Not built |

The live health and API-schema checks were made on November 7, 2026, at 06:01 UTC. The schema listed only `/health`. Cloud account and secret settings were confirmed earlier through operator output, not rechecked during that HTTP test.

This public package contains documentation only. The deployment guide shows how to recreate a small health-check backend. The team's existing application source has not been added here.

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
    -> FastAPI backend on Cloud Run
    -> Approved checks and company policies
    -> Model API
    -> Evidence validation
    -> Highlights, explanations, and learning
```

The model helps explain and assess the email. The harness is the backend code that controls tools, limits calls, and checks the model's output.

Planned tools:

- Inspect link text and actual destinations without opening the links.
- Compare sender domains with a company-provided list.
- Look up approved payroll verification rules.
- Retrieve reviewed examples and practice questions.

A matching domain does not prove that the sender is trustworthy. An account can be compromised.

## 5. Model plan

- First candidate: Claude Sonnet 5.5, `claude-sonnet-5-5`.
- Comparison candidate: GPT-6.1 Sol, `gpt-6.1-sol`.

These are candidates, not tested winners. The team reports access to both APIs, but neither has been tested in this app.

Use the same tools and held-out email examples to compare them. Check missed cases, false alarms, evidence quality, speed, and cost before choosing the deployed model.

No model fine-tuning or reinforcement learning has been done. User corrections are not automatically trusted training labels.

## 6. API plan

| Endpoint | Purpose | Status |
|---|---|---|
| `GET /health` | Check whether the backend is running | Available |
| `POST /analyze` | Analyze one email | Planned |
| `POST /challenge` | Reassess a result with more context | Planned |

Before integration, the backend and extension developers must agree on the exact JSON contract.

The analysis request should include an email ID, sender, subject, text blocks with IDs, and links with IDs and actual URLs.

Each finding should include its evidence reference, a plain-language explanation, and a suggested action. The backend must confirm that the evidence exists in the submitted email.

If evidence cannot be validated, show “Analysis incomplete” and suggest manual verification. Do not turn a failed analysis into an all-clear.

Both planned POST endpoints must check `X-Demo-Token` before any paid model call. Attaching a secret to Cloud Run does not implement this check.

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

## 8. Team tasks

| Person | Next task |
|---|---|
| Team lead | Share application source, manage secrets, deploy, and coordinate integration |
| Backend / AI developer | Build protected analysis, tools, evidence checks, and model comparison |
| Extension / UI developer | Build email extraction, token entry, highlights, explanations, and learning interactions |

The extension developer can use mock responses while the backend is built.

## 9. Done means

- A missing or wrong token cannot trigger model inference.
- The chosen model works inside Cloud Run.
- Every displayed clue points to verified evidence.
- Invalid evidence produces an incomplete result.
- Email instructions cannot grant new tool permissions.
- The challenge and short learning exercise work.
- The full extension-to-backend flow is demonstrated.
- Test results and limits are written down.

These checks are not completed yet.

Full-inbox scanning, attachment scanning, automatic blocking, multiple email platforms, dashboards, and model training are outside the first version.
