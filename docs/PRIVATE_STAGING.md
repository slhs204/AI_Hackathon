# Update the existing private staging backend

This guide is for the already-created `phish-staging` service in `lateral-nomad-514001-c7`, `us-central1`. It does not create secrets, accounts, IAM grants or public access. The root `DEPLOYMENT.md` is a historical health-only example and must not be used to update this application.

Use Google Cloud Shell with your existing authorized account. Pin `EXPECTED_SHA` to the tested commit supplied with this release (PR #5 is merged, so its commits are on `main`). Do not deploy from a dirty or unrelated folder.

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

Then follow [the extension connection and Chrome acceptance checklist](../chrome_extension/README.md). Source upload/deployment success alone is not Chrome E2E success.
