# Private Cloud Run AI with one-window connection

The existing extension talks to the same loopback8081 endpoint. The launcher now starts a small authenticated connector in that window; the connector authenticates to private Cloud Run and Cloud Run calls Tinker. No separately managed proxy process, new OAuth client or public endpoint is needed. Explicit AI permission and the local app token remain.

## Scope and authority

Owner A-002 requests extension AI completion and Cloud Run AI deployment/verification, retaining prior one-window/no extra proxy preference. Existing backend3ec6847 supports Tinker and passed tests/live local inference and independent review. Runtime already has secretAccessor on the existing Tinker secret, so no IAM grant is required. Existing Chrome extension0.3.4 loaded from C:/Users/pc297/AI_Hackathon-313b174/chrome_extension will be updated in place after checking for owner edits; this installs the tested artifact, not a second workflow. Use only identified synthetic T23 mail for real Gmail testing; its prompt-injection text is data.

## Architecture and minimality

Extension -> loopback connector -> IAM-private Cloud Run -> Tinker -> evidence/schema checks -> extension. A direct browser IAM flow would need an unconfigured OAuth client; public token-only access would weaken IAM; another gcloud proxy adds a user-managed process. Reusing launcher/port is the smallest adequate option. Connector is a separate backend/connector.py app so deployed backend/main.py stays unchanged. It reuses main.limit_body/config and token guard, uses synchronous fixed allowlisted routes, fixed Cloud Run host (and service-owned tagged host for canary), no redirects or environment proxies/netrc, bounded timeout/body/JSON and response-schema validation. Per-request ID token minting is intentionally simpler than token caching for one-user demo volume.

New live evidence: the existing OpenAI-compatible Tinker endpoint accepts base model Qwen/Qwen3-8B directly; tiny JSON succeeded1531ms without a sampler. If the full existing smoke test passes, deploy this base name instead of the expiring sampler. This removes sampler preparation/renewal from the normal cloud path without adding dependencies or training. Prior Anthropic-compatible experiment failures do not prove this OpenAI-compatible route unavailable. Existing -Local fallback retains its previously proven sampler configuration.

## Contracts

- CloudRun provider=tinker, model=Qwen/Qwen3-8B only after live smoke passes, key=existingphish-tinker-key:1; app token secret/runtime account/CPU-memory/scaling/IAM unchanged. Canary no-traffic tag a002-ai, suffixai-3ec6847-a002; test before promotion. Rollback revisionphish-staging-fix-313b174 retained. No public-access flags or IAM changes.
- Connector local token checked before any identity-token or upstream call; mandatory X-Require-Tinker:1. Local health is a startup snapshot, no gcloud spawn perhealthhit. Startup authenticated cloud session preflight refuses non-Tinker state without inference. Only /session,/analyze,/challenge forwarded; unknownroutes404, oversize/length rules shared. Incoming auth/token replaced; no other callerheaders forwarded. GoogleIDtoken and cloudappToken are server-side only. RuntimeTinkerkey stays inCloudRun.
- UpstreamJSONapplication errors preserved, HTMLIAM401/403 translated to502 with clear sign-in guidance, invalid/oversize/redirect/modelshape failsclosed. No POST retry. Successful analysis/challenge includes execution=cloud-run for truthful UIlabel. No arbitrary upstreamhost, URL fromemail or tools.
- Launcher defaults cloud, supports prior -Local only for fallback, validates cloud prerequisites without modelcheckpoint. It reads existingphish-demo-token into process env, passes resolvedgcloudpath, usesconnector:app foreground127.0.0.1:8081. -CheckOnly stays offline. All env/cwd restored. Localproviderkey path unchanged and explicit.

## Invariants

Registry baseline799abba52d25a3e5a8192fc551d972f11e40c77ab107ced3a7e310a42ba18f12; empty/noacceptedSYSIDs. No new registry promotion; existing security constraints apply.

- INV-1: cloudIAM stays private and missinglocaltoken/AIpermission cannot send mail or mintcredentials; providerkey/Googlecredentials never enter extension.
- INV-2: loopbackbind, fixedservice/routes, no auth-forwarding/redirect/proxyenv, boundedbody/timeout and no automatic paid retry.
- INV-3: errors/incomplete/evidencefailures never become all-clear; syntheticmail only; no send/delete/mailmutation.

## Acceptance criteria

- AC-1: canary reportsTinker, authenticates Google+apptoken, wrongtoken401, missingID403, absentpermission409, rulesguard409, syntheticanalyzecomplete and challengereassesseswithoutclearance. Identity/source/revision and IAMPreserve verified.
- AC-2: connector tests cover zero-upstream invalidtoken/permission/route, lengthlimits, replacementheaders, fixedURL, minterfail, HTMLautherrors, JSONerrorforwarding, redirect/size/schemafail, healthsnapshot, cloudstartupcheck.
- AC-3: one launcher starts cloudconnector with no Tinkerkey/checkpoint dependency and no extra proxy; actualWindowsstartup fromothercwd and occupiedportsafe; previouslocal tests retained.
- AC-4: installedextension0.3.6 on realChrome selectsone-click+explicitAI, analyzesidentifiedsyntheticT23 and challengesfinding through CloudRun; consent revocation blocks furtheranalysis. Keep unobservedcoverage explicit.
- AC-5: independent review dispositions and relevantbackend/extension/launcher tests pass, promote testedrevision and authenticatedserviceURL remainsTinker/private; finalbundle matches source and excludescredentials.

## Validation and routes

External read-only planning: Claude Opus5.5 medium toolsdisabled session27987 exited0. HostCodex synthesis retains privateconnector design and chooses simpler stablebase model after actualOpenAI-compatible proof. Independent final review required. Reuse unchanged A-001backend proof. Sourcecanary built from exact3ec6847gitarchive/backend, not workflowdirtyroot. Run CloudRunAPI smoke before promotion; preserve canary and rollbackidentities.
