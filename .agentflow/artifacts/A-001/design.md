# A direct-local demo with a verified Tinker model

The browser extension will send a selected synthetic email directly to a backend on this computer. A single Windows launcher prepares and runs that backend; no Cloud Run proxy is needed. Existing private Cloud Run remains a separate rules-only fallback. First establish a real Tinker sampler and prove the existing smoke test, then use the same configuration for the demo.

## Authority and scope

Owner Ask A-001 requests first real Tinker inference, near-one-click deployment without extra terminals/proxy, and current deployment status. Host synthesis of the bounded Claude Opus5.5 draft: use fixed local port8081 to coexist with the unrelated health-only8080 listener; preserve legacy staging8080. Explicit per-session Tinker opt-in is needed to make the requested inference available in the existing demo. Do not silently enable AI on an existing rules-only connection. No Cloud Run/IAM mutation, model training, public endpoint, arbitrary URL configuration, automatic checkpoint recreation or installer is included.

## Interfaces and lifecycle

- One-time controlled setup obtains phish-tinker-key in process memory, creates/reuses one sampler with24h TTL and no training, stores only sampler path/expiry in private/tinker-model.json, then runs eval.smoke_tinker --allow-paid on synthetic fixture.
- Start-Demo.cmd calls scripts/start-demo.ps1. It selects the installed Python, uses a local venv/dependencies, gets the existing secret without printing it, reads the sampler file, generates an ephemeral app token and starts uvicorn directly on127.0.0.1:8081 in the same window. No paid smoke or sampler creation on normal launch. Clear failures for occupied port, missing tools/key/checkpoint/expiry; no process killing.
- The connect panel chooses one of two fixed endpoints: existing private staging8080 (default) or direct local8081. Tinker permission is an unchecked session-only checkbox with a clear selected-email-to-model notice. Store endpoint/permission with the token; disconnect clears them.
- Rules-only clients retain X-Require-Rules-Only:1 and exact rules-only validation. Opted-in clients accept only a consistent exact tinker model label observed from /session; recheck before each call. Preserve request/response validation, redirects:error, stale-result protections, evidence validation and fail-closed behavior. AI failure is never a success/all-clear.
- AI results display TINKER AI and missing-information notes. Local demo stays free/offline. Provider credentials never enter the browser.

## Invariants

SYS registry is empty (baseline799abba52d25a3e5a8192fc551d972f11e40c77ab107ced3a7e310a42ba18f12); no promotion needed. Reuse existing PROJECT_SPEC constraints.

- INV-1: missing/wrong app token or absent opt-in cannot trigger paid inference; Cloud Run remains IAM-private mock.
- INV-2: startup binds loopback and never kills a foreign listener or logs provider secrets.
- INV-3: unverifiable/failed/incomplete model output stays incomplete; no payment approval and no stale-email result.

## Acceptance criteria

- AC-1: record current Cloud Run revision/provider/auth and local listener; anonymous cloud health403.
- AC-2: existing smoke test produces LIVE TINKER PASS with tiny JSON and complete synthetic analysis, recording only nonsecret model identity/timing.
- AC-3: one launch entry reaches local8081 with Tinker without proxy/extra terminal; repeat normal launch does not create sampler or pay for a smoke test. Occupied port fails safely.
- AC-4: default connection refuses Tinker before email transmission; explicit opt-in permits only Tinker at a fixed loopback endpoint; disconnect/reconnect and provider switch remain safe.
- AC-5: real local HTTP synthetic analyze succeeds with model label; wrong token and rules-only guard reject before model; relevant backend/extension tests and independent review pass.

## Validation

Run installed backend/extension suites, launcher-focused self-checks with fake process/cloud dependencies, actual Windows launcher to health/session and synthetic HTTP analysis, and rendered panel checks where tool availability allows. No real mailbox data or whole-inbox scan. Checkpoint TTL must be disclosed. Do not claim Chrome/Gmail E2E without observing it.

## Minimality check

Retain one launcher, existing backend and two fixed loopback addresses; no new server framework, gateway, daemon, cloud infrastructure or arbitrary endpoint option. Keeping8080-only would require stopping another program, violating safe coexistence; a hidden gcloud proxy retains the deployment burden the owner wants removed. Tinker opt-in is the smallest explicit privacy/cost control; merely deleting rules-only checks would silently send mail to a paid model. Normal launch reuses sampler and never trains.

## Planning route

External draft: Claude Opus5.5 medium, safe mode, tools disabled, session71686 exited0. Host Codex synthesis chooses fixed second port and explicit opt-in to satisfy usable proxy-free demo while preserving legacy behavior. No delegated source copy needed: planner received only approved exact public source and observations; no tools or secrets.
