# Title scan, direct mail selection and live-demo script

Check inbox titles should be the first step in the demo: scan the visible Gmail subjects, finish the visual sweep, then show selectable titles so the presenter can open each message without manual search. Body analysis remains a separate explicit action.

## Authority and scope

Owner corrected the manual-search workflow and requested a full subject-targeted animation before results, then asked to continue that task and provide a2–3minute key-point live-demo script. Same A005 remains owned; prior token-rotation/cost delivery still needs closeout and must not be lost. No global mailbox search, paging, body extraction during title scan or automatic AI call.

Host planning is proportionate: existing title snapshot/navigation and finite body sweep are understood; extend them rather than introduce a service, framework or second animation dependency. This is local frontend work with unchanged backend contract and permissions.

Return all checked visible title items, preserving flagged subset/count for compatibility. Render unflagged titles neutrally with body-not-checked wording; never force a test subject to be suspicious. Clicking any captured title opens its Gmail message, retains the list and requires Analyze separately. Existing scope/thread-id/loading/stale guards apply to all items. Up to100currentlyrendered rows; no hidden/off-page traversal.

Use finite pointer-transparent overlays on actual subject rectangles. Checks and animation may run concurrently, but neither row marks nor results appear until the complete sweep acknowledges the matching snapshot/request. Prefer existing body scan primitives/styles/timing. Reduced motion finishes without forced delay; cancellation/navigation/tab changes/panel closure/new checks clear overlays and suppress late results. Deadline watchdog never implies safety/completion for a replaced snapshot. Snapshot validation just before result release must detect changed list/subjects/account. No indefinite loops or artificial second sweep.

## Invariants

Empty registry baseline799abba52d25a3e5a8192fc551d972f11e40c77ab107ced3a7e310a42ba18f12 unchanged; no new promotion. T-INV1: subject checks remain local/read-only and do not send bodies/senders/previews to model. T-INV2: finite animation is presentation, not a verdict; only matching complete scan releases results. T-INV3: stale selections cannot open/analyze wrong mail, and title selection never sends AI requests. T-INV4: script narrates observed functionality, keeps benchmark scope and sender/payment uncertainty.

## Acceptance criteria

T-AC1: One click from Gmail list produces a full actual-title sweep then complete selectable checked-title list, including T06/T11 even if unflagged. Count/flags/cap/missing titles remain truthful.

T-AC2: Fast checks do not show results/marks early; reduced-motion, cancellation, repeated checks, navigation/account/tab/panel interruptions and lost animation event recover without late results/overlays. Body animation/navigation tests remain passing.

T-AC3: Actual browser demonstrates title scan→selection→explicitbodyAnalyze workflow on synthetic mail, or a concrete tool blocker is disclosed without claiming E2E. Updated bundle and loaded-source location are verified before reload.

T-AC4: TraditionalChinese spoken script is2–3minutes including short UI actions/waits, covers problem/localtitlecheck/AI/evidence/challenge/limits and avoids claiming modeltraining or realworld97%accuracy. Save script in authorized project docs and deliverable bundle; finalchat can show requested script.

## Validation and minimality

Meaningful red/green extension tests for gating/all-items/stale cleanup plus full extension suite. Reuse backend/launcher evidence unless changed. Independent finalsource/script review; actual Chrome proof if safe tool access permits. Reuse existing styles/transport/snapshots; no dependencies, backend/mail API changes, auto-sends or test-case-specific flags.
