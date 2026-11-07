# Deploy the Backend: Simple Guide

This guide creates a small FastAPI service with one endpoint: `GET /health`.

It does not add email analysis, model calls, token checking, or the Chrome extension. Those are separate tasks.

Use **Bash in Google Cloud Shell**, not Windows PowerShell. Run one block at a time. If a command fails, stop and fix it before continuing.

## 1. Choose your Google Cloud project

Open [Google Cloud Console](https://console.cloud.google.com/). Select your project and check that billing is linked to the correct account.

Copy the **Project ID**, not the project name or project number. Open Cloud Shell using the terminal button in the Console.

Run:

```bash
read -r -p "Google Cloud project ID: " PROJECT_ID
```

Enter your real project ID. Then run:

```bash
export REGION="us-central1"
export SERVICE="phish-coach-health-demo"
gcloud config set project "$PROJECT_ID"
gcloud projects describe "$PROJECT_ID" --format="yaml(projectId,projectNumber,lifecycleState)"
gcloud billing projects describe "$PROJECT_ID"
```

Check for `ACTIVE` and `billingEnabled: true`. Billing being enabled does not prove that a credit covers your planned services.

## 2. Enable the cloud services

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com iam.googleapis.com --project="$PROJECT_ID"
```

Wait for a success message. Your account needs permission to enable services.

## 3. Create the small backend

Use a new directory so existing application files are not overwritten:

```bash
BACKEND_DIR="$(mktemp -d "$HOME/phish-coach-demo.XXXXXX")"
cd "$BACKEND_DIR"
printf 'Backend folder: %s\n' "$BACKEND_DIR"
```

Write down the full folder path. If Cloud Shell reconnects or you open a new terminal, check the variables again: rerun Step 1, restore the saved path with the command below, and recalculate the account variables in Step 4. Do not assume the working folder or variables survived.

```bash
read -r -p "Full saved backend folder path: " BACKEND_DIR
test -d "$BACKEND_DIR" && cd "$BACKEND_DIR"
```

Create the Python application:

```bash
test -d "$BACKEND_DIR" && cat > "$BACKEND_DIR/main.py" <<'PY'
from fastapi import FastAPI

app = FastAPI(title="Phishing Coach API")


@app.get("/health")
def health():
    return {"status": "ok", "service": "phishing-coach"}
PY
```

Create the dependency list:

```bash
test -d "$BACKEND_DIR" && cat > "$BACKEND_DIR/requirements.txt" <<'EOF'
fastapi
uvicorn
EOF
```

Create the container instructions:

```bash
test -d "$BACKEND_DIR" && cat > "$BACKEND_DIR/Dockerfile" <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
EOF
```

The application listens on Cloud Run's port. No GPU or local Docker installation is needed.

Keep local secrets and temporary files out of the build upload:

```bash
test -d "$BACKEND_DIR" && cat > "$BACKEND_DIR/.gcloudignore" <<'EOF'
.git
.venv
__pycache__
.env
.env.*
*.log
EOF
cp "$BACKEND_DIR/.gcloudignore" "$BACKEND_DIR/.dockerignore"
python3 -m py_compile "$BACKEND_DIR/main.py"
```

A successful syntax check prints no output.

## 4. Set up service accounts

The build account creates the container. The runtime account runs the application. They have different jobs.

Get your project number:

```bash
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
RUNTIME_SA="phish-runtime@$PROJECT_ID.iam.gserviceaccount.com"
```

For the standard Cloud Run source-build setup, grant the Compute Engine default account the builder role:

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" --role="roles/run.builder"
```

If your project uses a different build account, grant the role to that actual account instead. IAM changes may take a few minutes to work.

Create the runtime account for a new setup:

```bash
gcloud iam service-accounts create phish-runtime --display-name="Phishing Coach Runtime" --project="$PROJECT_ID"
```

If it already exists, do not recreate it. Confirm the account instead:

```bash
gcloud iam service-accounts describe "$RUNTIME_SA" --project="$PROJECT_ID"
```

## 5. Deploy to Cloud Run

Use a new service name for this health-only demo if your project already has a working application. The next command replaces the named service's code when it already exists.

```bash
test -n "$PROJECT_ID" && test -n "$REGION" && test -n "$SERVICE" && test -n "$RUNTIME_SA" && test -f "$BACKEND_DIR/main.py" && test -f "$BACKEND_DIR/Dockerfile" && test -f "$BACKEND_DIR/requirements.txt" && gcloud run deploy "$SERVICE" --source="$BACKEND_DIR" --project="$PROJECT_ID" --region="$REGION" --service-account="$RUNTIME_SA" --allow-unauthenticated --cpu=1 --memory=512Mi --min-instances=0 --max-instances=2
```

The checks at the start prevent deployment if setup variables or required files are missing. If nothing runs, restore the Step 1 and Step 4 variables, then check `BACKEND_DIR` and its files before trying again. The explicit source path avoids uploading a different current folder.

If asked to create an Artifact Registry repository, answer `y`.

Cloud Build builds the image. Artifact Registry stores it. Cloud Run starts the service. Wait for the final service URL.

This demo is public because it only returns a health response. Do not add an unprotected paid model endpoint.

## 6. Test the deployed service

```bash
SERVICE_URL="$(gcloud run services describe "$SERVICE" --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)')"
curl --fail-with-body -i "$SERVICE_URL/health"
```

Expected result: HTTP 200 and this JSON:

```json
{"status":"ok","service":"phishing-coach"}
```

Open `SERVICE_URL/docs` in a browser, replacing `SERVICE_URL` with the actual URL. The root path `/` may return 404; use `/health` or `/docs`.

## 7. Optional: prepare secrets for future AI code

Skip this section for the health-only service. It does not call a model or use a token. No AI service has been completed yet.

Use this section only after the team has implemented and deployed its AI backend. Confirm the real target service first; do not assume it is the health demo.

```bash
read -r -p "Existing AI service name: " AI_SERVICE
read -r -p "AI service region: " AI_REGION
gcloud run services describe "$AI_SERVICE" --region="$AI_REGION" --project="$PROJECT_ID" --format="yaml(metadata.name,spec.template.spec.serviceAccountName)"
```

Check that the output is the intended AI application. If it is the health-only demo, stop and wait for the team's AI implementation. Read that service's runtime account:

```bash
AI_RUNTIME_SA="$(gcloud run services describe "$AI_SERVICE" --region="$AI_REGION" --project="$PROJECT_ID" --format='value(spec.template.spec.serviceAccountName)')"
```

When the team adds Claude code, it can read `ANTHROPIC_API_KEY` from an environment variable. An OpenAI implementation would use its own provider key and variable. Never put either key in GitHub.

Enter the provider key privately:

```bash
read -r -s -p "Anthropic API key: " MODEL_API_KEY
```

Then run:

```bash
test -n "$MODEL_API_KEY" && printf '%s' "$MODEL_API_KEY" | gcloud secrets create phish-model-key --replication-policy=automatic --data-file=- --project="$PROJECT_ID"
```

A blank result can mean the variable was empty. Continue only after the command reports that secret version 1 was created. Then clear the local variable:

```bash
unset MODEL_API_KEY
```

Create a separate random token for demo access:

```bash
openssl rand -hex 32 | tr -d '\n' | gcloud secrets create phish-demo-token --replication-policy=automatic --data-file=- --project="$PROJECT_ID"
```

These commands are for new secrets. If a name already exists, stop and check its purpose and versions instead of overwriting or guessing a version.

Grant the runtime account access to only these two secrets:

```bash
for SECRET in phish-model-key phish-demo-token; do
  gcloud secrets add-iam-policy-binding "$SECRET" --member="serviceAccount:$AI_RUNTIME_SA" --role="roles/secretmanager.secretAccessor" --project="$PROJECT_ID"
done
```

Attach the secret versions:

```bash
gcloud run services update "$AI_SERVICE" --update-secrets="ANTHROPIC_API_KEY=phish-model-key:1,DEMO_API_TOKEN=phish-demo-token:1" --region="$AI_REGION" --project="$PROJECT_ID"
```

This makes environment variables available to the container. **It does not add AI code or token validation.** The backend developer must check the demo token before any paid model call and enforce usage limits.

Share demo access privately. A token inside a browser extension can be extracted, so it is not production authentication.

## 8. Update and check costs

For the health demo, keep the saved source folder and rerun Step 5 after editing its files.

For the future AI application, use the team's own deployment instructions, its real source directory, service name, and region. Check the current service settings first with `gcloud run services describe`. Do not copy this demo's public-access and resource flags onto a different application, and do not deploy the health-only example over it.

Cloud Run can scale down when idle. The maximum instance count is not a spending cap. Cloud Build, stored images, secrets, and model requests can have separate charges. Budget alerts notify you; they do not automatically stop spending.

Check costs and credit coverage in Billing. Remove unused test resources when the demo is finished.

## Common problems

| Problem | What to check |
|---|---|
| Project permission denied | Correct account and Project ID; ask an administrator for the required access |
| Cannot enable APIs | Service Usage Admin permission |
| Build permission denied | Builder role on the account actually used for the build |
| Secret access denied | Secret Accessor role on the secret for the runtime account |
| Service fails to start | Dockerfile, installed dependencies, startup command, and port |
| `/analyze` returns 404 | Expected: that endpoint is not implemented yet |

Do not solve permission errors by broadly granting every account the Owner role.

## Official references

- [Deploy source code to Cloud Run](https://docs.cloud.google.com/run/docs/deploying-source-code)
- [Use Secret Manager with Cloud Run](https://docs.cloud.google.com/run/docs/configuring/services/secrets)
- [Budget alerts](https://docs.cloud.google.com/billing/docs/how-to/budgets)
