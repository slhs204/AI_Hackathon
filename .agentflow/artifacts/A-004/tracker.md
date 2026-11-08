# Finish P1 Qwen evaluation and semantic repairs

State: DONE5/5. Source: owner A004. The current pipeline needs honest metrics, development-only repair and one frozen test run.

## Tasks

- [DONE] T-1 â€” Validate split and repair evaluation accounting

  Scope: existing eval runner and focused tests; journal/provenance and provider/completeness metrics. AC-1/2, INV-1/4.

- [DONE] T-2 â€” Measure current tune baseline

  Scope:100publictune cases/Gmail view/currentv1,3workersmaximum. Record rules comparator and underlyingcalls. AC-2.

- [DONE] T-3 â€” Fix known semantic false alarms and compare development results

  Scope: prompts, shared bank-negation path, regression pairs and known synthetic inputs; no test inspection. AC-3,INV-2/3.

- [DONE] T-4 â€” Freeze candidate and evaluate existing test partition once

  Scope:100test inputs, exact frozen hashes; no retuning from test. Report historical exposure and full denominators. AC-1/2,INV-4.

- [DONE] T-5 â€” Review, deploy checked candidate and deliver

  Scope: independent review, private cloud acceptance, documentation, matching source bundle, cleanup/localGit. AC-4.

## Recovery

All accepted A004 work is complete. Frozen finaltestTP49FP2TN48FN1,100provider-success/100partial, no test-driven tuning. Knownfivecontentoverinterpretations repaired while realbank/identity warnings remain. Source/test/Cloud/browser/bundle observations and limits are retained in the linked report and safe verification.

Finalsource/delta reviews32154 and74449 exited0 PASS with docconditions applied.238backendpass1skip; unchanged99extension/PS5.1launcher evidence reused.332ownedbundlefiles equal source;335credentialscans0matches. Runtimeaudit57assertionsPASS, immediateIAM/resources/configsame; A004100%traffic andoldrollbacktagsretained. Base session/guards checked; analysis/challenge evidence is taggedcanary, not falsely claimed base rerun.

All workers and paid/deploy/reviewoperations settled. Taskconnector56515/PID9220 stopped and settled,8081free;foreign8080 preserved. CUAcompleted. Named localcommit follows this record; detachedHEAD blocksautopush toorigin without a branch, no branch guessed. No further runtime tuning is authorized from the finaltest results in this round.

## Evidence

[Design](design.md), [baseline identity](baseline-source.json), [final freeze](final-freeze.json), [deployment source](cloud-source.json), [safe verification](verification.json), [review disposition](review.md), [round evidence](../../.tmp/A-004.md), [product report](../../../docs/QWEN_EVALUATION.md).
