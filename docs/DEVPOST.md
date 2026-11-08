# Dobby’s Catch — Devpost copy and demo

Dobby’s Catch helps payroll staff inspect warning signs in an open Gmail message. The Chrome extension shows evidence and explanations, while a private backend checks the evidence and suggests payroll verification steps. The copy below describes the demonstrated prototype; it makes no real-world accuracy claim. Benchmark figures come from one small public dataset with historical test exposure.

## Submission timing

**Devpost submission closes November 8, 2026 at 9:00 AM EST (UTC−05:00), or 14:00 UTC.** The [official Devpost dates page](https://triangle-ai-hackathon-2026.devpost.com/details/dates) specifies EST. The [organizer schedule](https://triangle-ai-hackathon-site.vercel.app/schedule) separately lists hacking ending at **8:30 AM** and the Devpost deadline at **9:00 AM** on Sunday, November 8. Finish implementation by 8:30; use the remaining submission window for the entry and its materials.

## Project name

Dobby’s Catch

## Tagline

A phishing coach that helps payroll staff understand warning signs before acting.

## Inspiration

Payroll teams handle requests to change bank details, share employee information and approve payments. A warning alone does not explain what to check. We wanted to make warning signs understandable within the email someone is already reading.

## What it does

Dobby’s Catch is a Chrome extension for Gmail. When a user requests an analysis, it identifies concerning words or links, explains why they matter and suggests a safer next step from payroll procedures. Users can inspect the evidence, challenge a finding with additional context and practice recognizing similar warning signs.

“No warning signs” is never an all-clear. The tool does not authenticate a sender or authorize payments.

## How we built it

We connected a Chrome extension to a Python FastAPI backend on private Google Cloud Run. The demonstrated AI path uses Tinker with the Qwen/Qwen3-8B base model. The backend combines payroll-focused checks with model analysis and verifies quoted evidence against the email before displaying it.

Provider credentials stay on the backend. The extension requires explicit per-session permission before sending email content for Tinker analysis. A one-window Windows launcher connects the extension to the private service through an authenticated local connector.

## Challenges we ran into

The team’s early clients used different request and response formats. We aligned the backend contract while preserving the supported fields. We also had to handle partial Gmail extraction, unverifiable model evidence, stale results when switching messages and private Cloud Run access during a browser demonstration.

## Accomplishments that we’re proud of

On the earlier A003 revision, extension 0.3.6 completed a synthetic T23 analysis and challenge flow in real Chrome; partial extraction was flagged and revoking consent blocked further analysis. The P1 browser check used the T10 canary result: routine-content interpretation and deadline notes were corrected while the sender-identity warning remained. These checks establish integration, not detection accuracy. Separately, the frozen Qwen-assisted test warned on 49/50 phishing-labelled and 2/50 legitimate-labelled public inputs, with no provider failures. All 100 remained incomplete under Gmail extraction limits. The existing test had historical Anthropic/rule exposure; this is one small dataset, not real-world accuracy. See [metrics and remaining errors](QWEN_EVALUATION.md) and the historical [P0 acceptance](P0_ACCEPTANCE.md).

## What we learned

An explanation is useful only when it points to evidence the user can inspect. We also learned to separate integration checks from detection evaluation and to keep payroll approval procedures central to the suggested next action.

## What’s next

Evaluate broader fresh datasets and malicious-attachment coverage, and test whether payroll users understand the explanations and choose the appropriate verification step. Preserve the frozen test result without tuning from its errors.

## Built with

Chrome Extensions, JavaScript, Python, FastAPI, Google Cloud Run, Tinker, Qwen3-8B.

## Demo script — 45–60 seconds

Before recording, double-click `Start-Demo.cmd` and keep its single terminal open. In extension 0.3.6, choose the one-click connection, paste the temporary loopback token into the password field and explicitly enable Tinker. Open the synthetic T23 email in Gmail. Keep tokens and account details outside the recording. Run a fresh T23 analysis and challenge through the current one-click backend before recording to check inference time; the narration below is approximately 55 seconds, excluding model waits.

1. **0–10 seconds:** “This is Dobby’s Catch, a phishing coach for payroll staff. We’re using a synthetic Gmail message, extension 0.3.6 and a private Cloud Run backend.”
2. **10–25 seconds:** Click analysis, then select a finding to show its evidence. “When I request a check, Qwen3-8B through Tinker helps explain the warning signs. Selecting a finding shows the exact evidence and the payroll verification step.”
3. **25–40 seconds:** Submit a short challenge using synthetic context. “I can add context and challenge the finding. The response reconsiders that context while keeping the company’s verification procedure in view.”
4. **40–55 seconds:** Show the extraction notice or limitations text. “Gmail extraction is partial. Our small public-data test does not establish real-world accuracy. No warning signs does not mean safe, and this tool never authorizes a payment.”

## Fields still requiring owner input

- Final Devpost team membership and profile selection.
- Demo video URL after recording and upload.
- Public live demo URL, if the team chooses to provide one. The demonstrated Cloud Run service is private; its authenticated endpoint is not a public try-it link. The verified repository is [slhs204/Dobbys-Catch](https://github.com/slhs204/Dobbys-Catch).
- Final track/prize selections and any event-specific submission questions shown in the actual form.

## Evidence used for this draft

- [Current implementation and acceptance summary](../README.md): extension 0.3.6, private Cloud Run Qwen3-8B path, synthetic T23 analysis/challenge acceptance, consent and limitations. This draft does not reuse Claude evaluation figures as Qwen results.
- [One-window demo startup guide](../scripts/README.md): current launcher, local connector, temporary loopback token and explicit Tinker permission.
- [Official submission dates](https://triangle-ai-hackathon-2026.devpost.com/details/dates) and [organizer schedule](https://triangle-ai-hackathon-site.vercel.app/schedule): deadline and hacking-end distinction, checked November 8, 2026.


[A003 T23 cloud AI screenshot](assets/demo-ai.png) is a pre-P1 UI illustration, not evidence of the current P1 assessment.


The cloud app token is used only by the connector and is never pasted into the extension. Paste only the temporary loopback token displayed by the launcher.
