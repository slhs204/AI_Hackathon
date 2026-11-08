# Qwen evaluation and semantic false-alarm repair

We will measure the existing Qwen-assisted email pipeline, fix the routine-message mistakes using development inputs, and then evaluate the frozen version once on the existing test partition. Rules and Qwen work together, so these results describe the combined product rather than Qwen alone.

## Scope and method

Owner A004 authorizes P1 Qwen accuracy evaluation and known semantic false-alarm fixes. Use only public MIT fixtures and the already identified synthetic Gmail cases. No personal mail, new benchmark infrastructure, sender-authentication claims, payment approval, or final submission. Keep the one-window demo path. Fixes must reach the default demo and distributed source; use existing private Cloud Run deployment controls if promoting reviewed fixes.

Plan route: external Claude Opus5.5/medium draft, Codex host challenge/final synthesis. Native read-only audit found metric conflation and prior test exposure. Retain existing runner; add bounded crash-safe per-case records and provenance. Reject separate raw-output cache and new response API fields: exact model label equality and existing response fields suffice; journals preserve final observations. Frozen source hashes provide identity without requiring an unreviewed clean-tree commit.

Primary view is Gmail (header fields omitted), identical across baseline and candidate. Explicitly set extraction_complete false and limitations for product-realistic extraction; warning presence is measured independently of completeness. Also report no-findings/unfinished separately, never counting unfinished as a warning. Main metrics: finding-presence confusion matrix across all binary-labelled inputs; provider-success subset and complete-only subset with denominators; abstention/coverage/providerfailure by true label, precision/recall/FPR, Wilson95% intervals, latency. Failed model outputs are not Qwen successes. Rules-only comparator uses identical inputs. No implication of safe-to-pay.

Freeze committed split IDs and fixture hashes before development:100tune(50phishing/50legit),100test(50/50), disjoint. Existing test has historical Anthropic/rule exposure; this is a Qwen evaluation on an existing test partition, not a newly untouched benchmark. Do not inspect test content/results during tuning. Baseline100tune with currentv1; candidate100tune after generic prompt/negation repairs; at most2candidate prompt revisions on development only. Freeze final code/prompt/config, then100test once. No retuning from test. Known13synthetic requests are development regressions and excluded from benchmark figures.

At most3workers; existing Tinker transport retry0, at most one validation correction.300benchmark analyses plus boundedknown-case regression checks are authorized initially; any interrupted attempted request is uncertain and never auto-replayed. A second candidate is allowed only for a concrete failed development criterion, recorded with added calls. No dollar amount can be enforced by the API; count actual underlying calls/corrections.

## Invariants

Registry is empty and unchanged at SHA256799abba52d25a3e5a8192fc551d972f11e40c77ab107ced3a7e310a42ba18f12. No promotion proposed; existing PROJECT_SPEC/privacy guarantees remain.

- INV-1: Inputs are public/synthetic only; credentials remain process-local and absent from reports/bundle.
- INV-2: Preserve exact evidence validation, fail-closed model errors, partial extraction warnings, unverified identity and no payment approval.
- INV-3: Generic benign-message fixes cannot erase real bank-change, credential, secrecy or sender-mismatch warnings. Negation applies to its local clause only.
- INV-4: Test membership stays fixed; no runtime tuning after the final test; report historical exposure and every failed/unfinished call.

## Acceptance criteria

- AC-1: Split/input/source/prompt/schema/generation identities and live-provider status are recorded; per-case attempts persist before calls, completions persist immediately. Resume skips exact completed entries and refuses uncertain attempts/config mismatch; tests prove it.
- AC-2: Baseline/candidate tune and frozen test report finding-based TP/FP/TN/FN, provider failures, incomplete outcomes, denominators, confidence intervals and latency. No fallback counted as successful Qwen.
- AC-3: Known routine feedback, deadlines and unchanged-bank statements stop producing their spurious model/payment warnings; genuine changed-bank/credential/secrecy controls and actual outside-domain sender warning remain. Retain partial-scope/verification guidance. Record any unresolved case explicitly.
- AC-4: Relevant tests and independent source/result review pass; final reviewed candidate reaches the existing cloud/demo path with private IAM and rollback retained, live synthetic acceptance and source bundle equality.

## Validation

Harness metric/provenance/journal unit tests; production semantic regression pairs; existing backend suite, unchanged extension/launcher proof reused. Live tune/test are paid Tinker calls with exact model label and bounded workers; known synthetic cases prove behavior separately. Frozen source identity checked before/after final test. Existing private cloud/session/analyze guards and rules rollback checked after any promotion. Current docs/report distinguish measured integration/detection, semantic interpretation and generalization limits.

## Minimality check

Reuse the existing eval runner, split, provider wrapper and one-window launcher. No model retraining, dependency, new proxy or broad allowlist. Prompt clarification addresses model overinterpretation; a narrow clause-level negation check addresses the deterministic bank-details false alarm. Per-case journal is necessary to avoid paying again after interruption; a second cache or evaluator service adds no required proof.
