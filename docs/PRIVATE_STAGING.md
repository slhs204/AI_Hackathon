# Update the existing private staging backend

This guide is for the already-created `phish-staging` service in `lateral-nomad-514001-c7`, `us-central1`. It does not create secrets, accounts, IAM grants or public access. The root `DEPLOYMENT.md` is a historical health-only example and must not be used to update this application.

## Current AI verification status

The historical P1 `d08fe1b` revision suffix identifies its base commit. Deployed working-tree source is identified by the SHA-256 provenance in the [evaluation report](QWEN_EVALUATION.md#method-and-provenance), rather than by treating that base commit as the complete P1 source.

Current P2 revision `phish-staging-p2-ai-b3b3e19-a005` serves 100% base-service traffic, with tag `p1-ai`. The `rules-only` tag points to `phish-staging-p2-rules-b3b3e19-a005` at 0% base traffic; that backup uses `MODEL_PROVIDER=mock` and has no Tinker key. These are the only retained tags. Obsolete `p0-ai` and `a002-ai` routes were removed and returned 404. The P1 revision `phish-staging-p1-d08fe1b-a004` and its original promotion remain historical evidence. Its [frozen evaluation](QWEN_EVALUATION.md) is complete, with the benchmark limits reported separately from deployment checks.

Before the historical P1 promotion, the P1 tagged canary returned anonymous 403, wrong app token 401, missing-AI and rules-only guards 409, and authenticated session/analysis/challenge 200. The complete synthetic fixture produced 16 findings in 7,266 ms; challenge returned `still_concerning` in 2,484 ms. These are canary observations, not a rerun of paid analysis/challenge at the promoted base URL. Six known synthetic canary cases passed: T06 retained the bank-change request, T09/T10/T11/T14/T22 dropped their previous routine-content overinterpretations, T10 kept deadline notes, T11 had no payment finding, and T22 retained its identity warning.

Real Chrome displayed the P1 canary T10 result with one outside-domain identity warning, a routine-content AI summary, deadline notes and the partial-extraction notice. That identity warning still contributes to both sender and pressure rubric dimensions. This is evidence for that browser path, not general accuracy or all-case browser acceptance.

The service uses Tinker base model `Qwen/Qwen3-8B`, without sampler expiry. Provider credentials stay in Cloud Run. The default Windows launcher still starts its foreground authenticated connector on loopback 8081 in one window. See [startup instructions](../scripts/README.md). `Start-Demo.cmd -Local` preserves the earlier sampler-backed fallback, whose checkpoint still expires. The optional 8080 rules-only connection must use the retained `rules-only` tagged route rather than the base URL.

Current backend validation is 238 passed and 1 skipped. The 110 extension tests and Windows PowerShell 5.1 launcher checks pass. The P1 runtime audit passed 57 required assertions against immediate A004 before/after observations: IAM bindings, runtime account, environment/secret references and resources remained unchanged, with no public IAM grant. All 24 source files matched working, staged and frozen manifests; this is source equality, not extraction from the running container. Promoted-base checks returned session 200 with Tinker on all model routes, anonymous 403, wrong token 401 and request guards 409. Paid analysis/challenge checks remain the earlier tagged-canary observations.

A003's earlier base-route session, analysis/challenge timings and synthetic T23 browser check remain historical in [P0 acceptance](P0_ACCEPTANCE.md). The existing T23 screenshot is an A003 UI illustration, not proof of the P1 prompt or fixes.

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
git clone --branch main --single-branch https://github.com/slhs204/Dobbys-Catch.git "$WORK"
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


P1 Qwen-assisted evaluation is complete: the frozen test run warned on 49/50 phishing-labelled and 2/50 legitimate-labelled public inputs. All 100 analyses remained incomplete under Gmail extraction limits. Known routine-content errors were repaired on development cases; remaining errors and historical test exposure are disclosed in the [evaluation report](QWEN_EVALUATION.md). The [P0 acceptance record](P0_ACCEPTANCE.md) remains historical integration evidence.

Before P2 rotation, the historical rules-only route returned session 200 with rules-only on all routes. It also returned a rules-only response despite `X-Require-Tinker`; that legacy behavior was preserved, not attributed to P1. The historical P1 route rejected the wrong guard with 409, and the connector validates the exact required model and refuses a wrong-model response.


## P2 app-token rotation

Both current revisions pin `phish-demo-token` numeric version `2`. Byte-exact readback passed; version `1` is disabled. Base, `p1-ai` and `rules-only` sessions returned 200 with the new token, 401 with the old token and 403 anonymously. The launcher reads `latest`, currently version `2`; its stock Windows PowerShell 5.1 production entry returned session 200 with all three Tinker model labels and no inference. Restart cached connectors before reconnecting.

The deployed image is identical to P1 (`sha256:52bd7107937420557611aa885f3f3aadaadcea52de5cfaaec4a8a378a74963bf`); IAM bindings, runtime account and resources were unchanged. Rotation verified sessions and authentication only: it did not rerun paid analysis/challenge or change the frozen P1 evaluation results. The earlier 57-assertion runtime audit, synthetic browser observations and paid canary timings above belong to P1, not a new P2 browser or inference acceptance run. Historical revisions still bound to secret version `1` cannot be used for rollback until rebound to the current token. See [post-demo operations](POST_DEMO.md).
