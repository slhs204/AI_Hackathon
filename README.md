# Phishing Coach

Phishing Coach is a hackathon project for payroll staff. It aims to help people spot suspicious emails, understand the warning signs, and learn a safer next step.

## What works now?

A small Python backend is running on Google Cloud Run. Its `GET /health` endpoint works.

The browser extension, email analysis, AI tools, and learning activities are still planned. This package is documentation, not the finished application.

## What will the product do?

1. Check one email when the user asks.
2. Highlight the exact words or links that need attention.
3. Explain each clue in simple language.
4. Let the user add context and question the result.
5. Offer a short practice question.

Clues can appear as clickable pieces of a fishing hook. No hook does not mean the email is safe.

## Read these files

- [PROJECT_SPEC.md](PROJECT_SPEC.md): the product, current progress, and team tasks.
- [DEPLOYMENT.md](DEPLOYMENT.md): a step-by-step guide to deploy the health-check backend.
- [.gitignore](.gitignore): rules to keep private files out of future Git commits.

The deployment guide includes the small backend example. No application source was exported from Cloud Run.

## AI model plan

Start by testing Claude Sonnet 5.5. Compare it with GPT-6.1 Sol using the same email examples. Neither is connected to the deployed app yet.

Keep model API keys on the backend. Do not put them in the extension or in GitHub.

## How to upload this package to GitHub

1. Open this upload folder.
2. Create a new, empty GitHub repository. Leave the options to add a README or .gitignore unchecked.
3. Upload the four files in this folder to the repository root.
4. Keep their names unchanged so the links work.

If you received a ZIP, unzip it first. Upload its contents, not the ZIP itself.

Upload only these four files. This package contains project documents and setup steps only. A `.gitignore` file does not filter files manually selected in GitHub's upload screen.

## Project limits

This is a prototype. It does not prove that an email is safe, replace company approval rules, or authorize payments. Use synthetic emails for the demo.
