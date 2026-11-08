# Tinker inference and simple demo startup

Goal: prove one live synthetic Tinker analysis, reduce demo startup to one entry point, and report actual cloud/local state. State: DONE (4/4).

## Tasks

- [DONE] T-1 — Confirm deployed and local environment
  - Source: owner Ask A-001. Inspect Cloud Run revision/provider/auth and local listener identity. No IAM changes or unrelated process termination.

- [DONE] T-2 — Complete first live Tinker inference
  - Run existing smoke test with a valid sampler and Secret Manager key. Synthetic data only; no training. Pass requires LIVE TINKER PASS, not fallback or preflight.

- [DONE] T-3 — Simplify the demo launch
  - Choose the smallest direct-local option after bounded external planning. One launcher; no extra managed proxy or extra terminal. Preserve token validation and private Cloud Run.

- [DONE] T-4 — Verify, review and deliver
  - Check changed journeys, error paths, scripts and applicable existing backend/extension tests. Independent review required before acceptance.

## Recovery

2026-11-08: all requested local outcomes verified; independent delta review PASS. Prepared source bundle matches final code and includes only a nonsecret expiring sampler reference. All task-owned verification servers and browser sessions stopped;8081 free. No cloud or remote Git publication performed. Git delivery is local on detached HEAD; no target branch inferred. Next: owner can launch the delivered Start-Demo.cmd and load/reload extension0.3.5. Real GmailE2E remains an explicitly disclosed unproved check, outside the observed HTTP/layout proof.

## Evidence

Registry baseline SHA256: 799abba52d25a3e5a8192fc551d972f11e40c77ab107ced3a7e310a42ba18f12. Empty scaffold; no SYS-INV IDs accepted. Existing PROJECT_SPEC safety constraints retained.

Detailed checks and recovery: [round evidence](../../.tmp/A-001.md).
Design: [design](design.md).
