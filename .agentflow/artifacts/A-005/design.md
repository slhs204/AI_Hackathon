# Post-demo token rotation and cost check

We will replace the long-lived cloud demo token and reconnect the existing one-window launcher to it. Every reachable service route must reject the old token. Cost checks are read-only and distinguish reported gross usage, credits and amounts due, including reporting delay.

## Scope and sequence

Owner A005 explicitly authorizes demo-token rotation and cost inspection. DEMO_API_TOKEN/phish-demo-token is the target; Tinker provider key is retained. Loopback tokens already regenerate each launch. No public IAM, provider-key rotation, account creation, billing changes, paid inference, artifact deletion or new proxy.

Planning route: tools-disabled Claude Opus5.5/medium draft, Codex host challenge/synthesis. Adopt byte-exact CSPRNG secret upload, total tag inventory and session-only validation. Use Python secrets.token_urlsafe and subprocess byte stdin on Windows, not echo/Bash. Latest-token launcher acceptance is proven by the authenticated session, while Cloud Run remains numerically pinned; mismatch fails closed. No extra metadata call or new configuration system.

Snapshot service/IAM/secret-version metadata. Generate one new high-entropy token in memory and upload byte-exact stdin, never log/store its value. Verify readback equality and version identity. Deploy mock rules backup first using the exact current P1 image digest, new app version and no provider key; then deploy AI using the same image with existing provider key and new app version. Both start at0% tagged canaries. Session/guard matrix proves new-token200,old401,anonymous403 without model calls. Atomic cutover sets100%AI and exactlyp1-ai/rules-only tags, removing old and temporary routes. Old revisions remain unrouted; historical rollback requires a new-token rebind. Disable old secret version only after cutover verifies; never destroy it. Check base/current/rules and obsolete tag URLs plus unchanged IAM/resources. Record identities before retrying any uncertain operation.

Fix the launcher cloud token version1 pin to latest and update its PS5.1 regression and affected guidance/bundle. Provider-secret fallback behavior remains unchanged. Existing processes caching the old cloud token must restart; the new loopback token must be pasted again.

## Invariants

Registry is empty and unchanged at baseline799abba52d25a3e5a8192fc551d972f11e40c77ab107ced3a7e310a42ba18f12. Existing privacy/no-payment contracts apply; no new durable registry rule is proposed.

- INV-1: New/old token values stay in process/SecretManager, never files, argv, chat, reports or bundles.
- INV-2: No IAM expansion, public access or model inference; same AI image/provider/resources and mock backup without provider key.
- INV-3: After completion, no reachable old or temporary route accepts the old token; old version disabled, not destroyed.
- INV-4: Costs are attributed only as supported, with time window/cutoff/credits/estimation uncertainty. No guessed bill from request counts or stale price estimates.

## Acceptance criteria

- AC-1: Launcher reads current app token and preserves one-window behavior; PS5.1 tests cover newest version and no leakage/restoration.
- AC-2: New AI100%/rules backup0%, exact tag set, old-token401/new200/anonymous403 on reachable session routes; obsolete routes not200; version1 disabled. Image/config/IAM comparison and actual connector session pass without paid inference.
- AC-3: Tinker usage/storage and GoogleCloud reports checked via authorized read-only sources; report actual versus estimated/credits/delay and any unavailable balance. Project versus organization scope explicit.
- AC-4: Independent security/result review, relevant checks, matching credential-free bundle, settled processes and authorized local Git delivery.

## Validation and minimality

Reuse SecretManager versions, existing CloudRun service/image and launcher. No build, extra proxy, credential framework or provider call. Use durable operation receipts, session/guard checks, metadata comparison and actual one-window connector startup. Existing backend/extension tests reused where no source changes. Costs require actual provider/UI observations; missing/current-day data remains unavailable rather than zero. Secrets are disabled reversibly only after replacement works.
