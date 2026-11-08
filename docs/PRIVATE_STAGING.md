# Update the existing private staging backend

This guide is for the already-created `phish-staging` service in `lateral-nomad-514001-c7`, `us-central1`. It does not create secrets, accounts, IAM grants or public access. The root `DEPLOYMENT.md` is a historical health-only example and must not be used to update this application.

## Current AI verification status

The IAM-private AI revision `phish-staging-ai-3ec6847-a002` now serves 100% traffic after independent review and API verification. It uses Tinker base model `Qwen/Qwen3-8B` directly, without a sampler expiry. Synthetic analysis completed in 7,922 ms and challenge in 1,453 ms. Post-promotion authenticated base `/session` returned Tinker; anonymous access returned 403, IAM bindings remained unchanged, and the unmodified Windows launcher connected to the base URL from another working directory.

The existing runtime account, IAM protections and resource limits remain preserved. Provider credentials stay in Cloud Run. The default Windows launcher starts a foreground authenticated connector on loopback 8081 in one window; it reads the existing cloud app token, checks the remote session and requires no separately managed proxy. See [startup instructions](../scripts/README.md). `Start-Demo.cmd -Local` preserves the earlier sampler-backed fallback, whose checkpoint still expires.

Mock revision `phish-staging-fix-313b174` is retained under the `rules-only` tag alongside the `a002-ai` tag. Its authenticated session still returns rules-only after promotion. The optional legacy 8080 connection must use `gcloud run services proxy phish-staging --project=lateral-nomad-514001-c7 --region=us-central1 --tag=rules-only --port=8080`, so it stays rules-only after the base service receives AI traffic. The default cloud connector still needs only its single launcher window.

Validation: 187 backend tests passed with 1 skipped, 99 extension tests passed, and launcher checks passed under Windows PowerShell 5.1. Real Chrome with extension 0.3.6 passed synthetic T23 analysis and challenge; partial Gmail extraction was correctly flagged, and revoking AI consent blocked subsequent analysis. These checks do not measure phishing accuracy or authorize payment.

For the AI API path, authenticated requests need both Google IAM authentication and the app token, plus `X-Require-Tinker: 1`. Missing/wrong app token, absent permission and the rules-only guard must fail before inference. Never expose Google credentials or the cloud app token to the extension; it receives only the temporary loopback token.

## Historical rules-only deployment procedure

The commands below document the earlier rules-only release. They deliberately set `MODEL_PROVIDER=mock` and must not be used to promote or verify the AI canary.

For that historical procedure, use Google Cloud Shell with your existing authorized account. Pin `EXPECTED_SHA` to its exact tested commit (PR #5 is merged, so its commits are on `main`). Do not deploy from a dirty or unrelated folder.

```bash
set -euo pipefail
PROJECT_ID=lateral-nomad-514001-c7
REGION=us-central1
SERVICE=phish-staging
read -r -p 'Exact tested PR commit SHA: ' EXPECTED_SHA
[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo 'Use the full 40-character tested SHA.'; exit 1; }
WORK=$(mktemp -d "$HOME/phish-staging-update.XXXXXX")
git clone --branch main --single-branch https://github.com/slhs204/AI_Hackathon.git "$WORK"
cd "$WORK"
git checkout --detach "$EXPECTED_SHA"
test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"
test -z "$(git status --porcelain)"

# Inspect existing settings without reading secret values.
gcloud run services describe "$SERVICE" --project="$PROJECT_ID" --region="$REGION" \
  --format=json > "$WORK/service-before.json"
python3 - "$WORK/service-before.json" <<'PYCODE'
import json,sys
s=json.load(open(sys.argv[1])); a=s.get('metadata',{}).get('annotations',{})
assert a.get('run.googleapis.com/invoker-iam-disabled','false') != 'true', 'STOP: IAM authentication is disabled'
e=s['spec']['template']['spec']['containers'][0].get('env',[])
print('Service:', s['metadata']['name'])
print('Runtime account:',s['spec']['template']['spec'].get('serviceAccountName'))
print('Environment names:', [x['name'] for x in e])
assert any(x['name']=='DEMO_API_TOKEN' and 'secretKeyRef' in x.get('valueFrom',{}) for x in e), 'STOP: expected existing token secret reference'
PYCODE
gcloud run services get-iam-policy "$SERVICE" --project="$PROJECT_ID" --region="$REGION" --format=json > "$WORK/iam-before.json"
python3 - "$WORK/iam-before.json" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
assert not any(m in {'allUsers','allAuthenticatedUsers'} for b in p.get('bindings',[]) for m in b.get('members',[])), 'STOP: unexpected broad IAM access'
PY
# The source directory is backend/, not this repo root.
# No access flags, secret mappings or service-account changes: preserve the existing private configuration.
gcloud run deploy "$SERVICE" --source="$WORK/backend" --project="$PROJECT_ID" --region="$REGION" \
  --update-env-vars=MODEL_PROVIDER=mock --revision-suffix="safe-${EXPECTED_SHA:0:10}" --quiet

gcloud run services describe "$SERVICE" --project="$PROJECT_ID" --region="$REGION" \
  --format='yaml(status.latestReadyRevisionName,status.latestCreatedRevisionName,status.traffic,status.url)'
gcloud run services get-iam-policy "$SERVICE" --project="$PROJECT_ID" --region="$REGION" --format=json > "$WORK/iam-after.json"
python3 - "$WORK/iam-before.json" "$WORK/iam-after.json" <<'PY'
import json,sys
before,after=(json.load(open(p)) for p in sys.argv[1:])
assert before.get('bindings',[])==after.get('bindings',[]), 'STOP: review unexpected IAM change'
print('IAM bindings unchanged.')
PY
```

Do not paste secret-bearing environment values or tokens into chat. The service should retain the existing Secret Manager reference for DEMO_API_TOKEN. If a source-build permission, API enablement, IAM change, new secret, billing commitment or other unexpected prompt is needed, stop and review it rather than granting broad roles. Deployment has ordinary Cloud Build/Run costs; this does not enable paid AI.

After the revision is ready, run the previously verified synthetic health/analyze/challenge smoke checks with the existing authenticated request headers, adding `X-Require-Rules-Only: 1`. Also request `GET /session` with those headers. Expect 200 and rules-only model labels. Without the app token, `/session` must return 401; without Google IAM authentication, the private service must remain inaccessible. Confirm the deployed revision suffix matches the exact tested commit and traffic points to it.

For that historical rules-only procedure, follow [the extension connection and Chrome acceptance checklist](../chrome_extension/README.md). Source upload/deployment success alone is not Chrome E2E success. Current AI acceptance results are recorded above.
