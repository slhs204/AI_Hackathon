# Qwen-assisted warning evaluation

Rules and Qwen inspect the same visible message and return evidence-backed warning findings. This evaluation asks whether at least one warning is present for each dataset-labelled email; it measures the combined product, not Qwen alone or whether an email is safe.

The frozen candidate warned on 49/50 phishing-labelled test messages and 2/50 legitimate-labelled messages: 97/100 matched the dataset labels. All 100 provider reviews succeeded. Every analysis remained incomplete because the Gmail view deliberately omits information. These are results from one small public dataset with historical test exposure, not a real-world accuracy guarantee.

Use the results below to understand detection and false-alarm tradeoffs. [Method and provenance](#method-and-provenance) explain the denominators and single final run; [remaining errors](#remaining-errors) explain the limits that matter when using the demo.

## Measured results

Tune rows are in-sample development results; the frozen test row is the reserved evaluation estimate, subject to the historical exposure described below. Each cell gives numerator/denominator, percentage, and a Wilson 95% interval. A true positive (TP) is a phishing-labelled input with findings; a false positive (FP) is a legitimate-labelled input with findings. True negatives (TN) and false negatives (FN) have no findings. Notes do not count as warnings.

| Run | TP / FP / TN / FN | Warning accuracy | Recall | False-positive rate | Precision |
|---|---|---|---|---|---|
| [Qwen baseline, tune, v1](../backend/eval/results/model-blind-tune-qwen-p1-baseline.json) | 50 / 44 / 6 / 0 | 56/100 = 56.0% (46.2%–65.3%) | 50/50 = 100.0% (92.9%–100.0%) | 44/50 = 88.0% (76.2%–94.4%) | 50/94 = 53.2% (43.2%–63.0%) |
| [Qwen candidate, tune, v3](../backend/eval/results/model-blind-tune-qwen-p1-candidate.json) | 49 / 0 / 50 / 1 | 99/100 = 99.0% (94.6%–99.8%) | 49/50 = 98.0% (89.5%–99.6%) | 0/50 = 0.0% (0.0%–7.1%) | 49/49 = 100.0% (92.7%–100.0%) |
| [Qwen frozen final test, v3](../backend/eval/results/model-blind-test-qwen-p1-test.json) | 49 / 2 / 48 / 1 | 97/100 = 97.0% (91.5%–99.0%) | 49/50 = 98.0% (89.5%–99.6%) | 2/50 = 4.0% (1.1%–13.5%) | 49/51 = 96.1% (86.8%–98.9%) |
| [Rules baseline, tune](../backend/eval/results/rules-only-blind-tune-qwen-p1-baseline.json) | 14 / 3 / 47 / 36 | 61/100 = 61.0% (51.2%–70.0%) | 14/50 = 28.0% (17.5%–41.7%) | 3/50 = 6.0% (2.1%–16.2%) | 14/17 = 82.4% (59.0%–93.8%) |
| [Rules candidate, tune](../backend/eval/results/rules-only-blind-tune-qwen-p1-candidate.json) | 13 / 0 / 50 / 37 | 63/100 = 63.0% (53.2%–71.8%) | 13/50 = 26.0% (15.9%–39.6%) | 0/50 = 0.0% (0.0%–7.1%) | 13/13 = 100.0% (77.2%–100.0%) |
| [Rules frozen final test](../backend/eval/results/rules-only-blind-test-qwen-p1-test.json) | 12 / 1 / 49 / 38 | 61/100 = 61.0% (51.2%–70.0%) | 12/50 = 24.0% (14.3%–37.4%) | 1/50 = 2.0% (0.4%–10.5%) | 12/13 = 92.3% (66.7%–98.6%) |

On the same 100 development inputs, false alarms fell from 44 to 0, while one previously warned phishing-labelled case lost its warning. The rules comparator uses identical Gmail inputs and extraction limits. On the final test, adding Qwen increased warned phishing-labelled cases from 12 to 49, with false alarms increasing from 1 to 2. These are paired sample comparisons, not independent evidence that every finding is semantically correct.

| Paid benchmark run | Successful provider reviews | Underlying calls | Validation corrections | Median / maximum latency |
|---|---|---|---|---|
| Qwen baseline, tune, v1 | 100/100 | 105 | 5 | 3,999 / 15,266 ms |
| Qwen candidate, tune, v3 | 100/100 | 100 | 0 | 1,889 / 5,625 ms |
| Qwen frozen final test, v3 | 100/100 | 100 | 0 | 1,812 / 5,516 ms |

The benchmark used 305 underlying paid calls for 300 analyses, including five validation corrections. No benchmark review fell back to rules because of provider failure. Provider-success coverage is 100/100 in each paid run (Wilson 95%: 96.3–100%); its confusion matrix therefore equals the all-input matrix. Rules-only runs make zero provider calls and have no provider-success subset.

Completion coverage is 0/100 in every run (Wilson 95%: 0–3.7%). All 50 phishing and 50 legitimate messages in each partition have `analysis_complete=false` and `assessment=insufficient_evidence`; the complete-only subset is empty and its rates are undefined, not zero accuracy. Warning/no-findings and incomplete are separate axes. In the final test, 49 phishing and 2 legitimate inputs had warnings; 1 phishing and 48 legitimate inputs had no findings. All 100 remained unfinished in scope, and none received payment approval.

## Remaining errors

These final-test cases were inspected only after the frozen run completed. No runtime change or retuning followed that inspection.

- **[legit-028](../fixtures/blind/legit-028.json) — model false alarm.** A routine two-factor-authentication reminder from `security@gmail.com` received a sender-impersonation finding. The explanation treats a generic address as impersonation without establishing a claimed official identity. The quoted body is present, but that does not establish the interpretation. Result: one model finding, `verify`.

- **[legit-048](../fixtures/blind/legit-048.json) — rules false alarm against the dataset label.** A cloud-backup notification from `support@google-drive.com` triggered the existing Google look-alike-domain rule. The dataset calls it legitimate; the visible address does not authenticate Google. Count the label disagreement as an FP without asserting that the domain is safe. Result: one rules finding, `verify`.

- **[phish-0070](../fixtures/blind/phish-0070.json) — missed warning.** The HR-policy message only asks the reader to review `hr_policy.pdf`. The dataset labels its attachment a malicious payload; Gmail input omits attachment metadata and the product does not inspect attachment contents. The visible body still names the PDF, but neither rules nor Qwen warned. Result: no findings, incomplete, `verify`; this is an FN, not an all-clear.

The development loss was **[phish-0085](../fixtures/blind/phish-0085.json)**, another PDF-attachment case. After routine-message clarification, it had no warning. An attachment filename or benign-looking review request cannot establish malware. This recall cost was disclosed before the final run and was not repaired using test outcomes.

Per-case observations, finding source/category/quote/explanation, limitations and latency are retained in the linked [final-test JSON](../backend/eval/results/model-blind-test-qwen-p1-test.json) and [readable table](../backend/eval/results/model-blind-test-qwen-p1-test.md). The [public input fixtures](../fixtures/blind/) retain dataset labels and provenance; this report does not relabel them.

## Known synthetic regressions

The 13 already identified synthetic Gmail requests are development regressions and are excluded from all benchmark figures. They retain realistic partial extraction and the synthetic outside-Gmail sender, so directory-name/address mismatch warnings are interpreted separately from routine content.

The v3 development check removed the five previously documented content overinterpretations in T09, T10, T11, T14 and T22. Routine document comments, timesheet deadlines and unchanged-bank language no longer produced those old model/payment warnings. T22 retained its actual outside-domain executive-name rule warning; T10 retained that identity warning while pressure words became notes. Thus these are repairs to specific semantic false alarms, not a claim that all five messages have no findings.

T06 initially lost its bank-redirection warning. A generic rule for sending payments to a new account repaired that shared detection path; one additional paid T06 check then retained a `payment_or_data_request` finding and a `verify` verdict. Existing controls preserve changed-bank, credential, secrecy and sender-mismatch warnings. No attachment-malware inspection was added.

The first known-case check used 14 calls for 13 analyses (one validation correction); the final T06 recheck used one call. Together with the benchmark this is 320 underlying calls for 314 recorded evaluation/regression analyses. Deployment smoke checks are separate from this count. The known-case results remain development evidence, not an extra test partition.

## Method and provenance

The source dataset is [Teddyha/phishing_benign_email_dataset](https://huggingface.co/datasets/Teddyha/phishing_benign_email_dataset), recorded as MIT-licensed in the [local source notes](../fixtures/external/teddyha/README.md). Its 200 retained examples are split deterministically into 100 tune and 100 test inputs, each with 50 phishing and 50 legitimate labels. The source notes describe mostly credential and malware examples, one BEC example and no payroll examples. This does not validate payroll-fraud coverage or learning outcomes.

The existing test partition had historical Anthropic/rule exposure. It was reserved from this Qwen development work, not newly untouched. Split IDs and all 200 fixture hashes were frozen before development; duplicate, overlap, missing-ID and coverage checks ran before inference. Development used tune and known synthetic cases only. One v1 baseline and one v3 candidate tune run preceded the single v3 final test; no second candidate benchmark or replacement final-test run occurred.

For every run, Gmail processing removes Reply-To, raw authentication results and attachments, marks extraction partial, and retains explicit limitations. The warning outcome is `bool(findings)`, independently of assessment, completeness or verdict. An unavailable model cannot count as a Qwen success; successful review requires an actual underlying call and exact configured model label. No model-only score is claimed.

The journal flushes and synchronizes an attempted record before transmission, records each underlying call and writes each completion immediately under a lock. Matching completed inputs can be skipped on resume. A configuration mismatch, torn record or uncertain attempted request blocks automatic replay. The accepted final-test policy was to report an interrupted run inconclusive, without editing its journal or starting a replacement. No interruption occurred; all 100 final cases completed. The successful candidate run and final T06 positive check served as preflight.

Final runtime source was checked unchanged before and after the test. Prompt-version reporting resolves the actual selected version, unsupported views fail before inference, and partial pressure-note text refers to visible content. Independent review conditions were resolved or explicitly retained as limits before freeze. Verification recorded 238 backend tests passed and 1 skipped; the unchanged 99-extension-test and launcher evidence was reused, not rerun as a new browser acceptance claim.

The base checkout revision is `d08fe1bd1d7a3887922aa753bc2fa5945342ed86`; the evaluated working-tree changes are identified by SHA-256 hashes, not by pretending that base commit contains the candidate. Full source/data/input identities and endpoint hash are embedded in each result JSON. The final configuration fingerprint is `374016ed605f355dedfa6ffffb244b9381f5ac98324a4d7f26f41f00987a388c`.

| Final identity | SHA-256 |
|---|---|
| `Split manifest` | `29f1ed1cd6f5f196ae83413851850a164a5b89b3268094a42e2fa56de108963d` |
| `Selected v3 prompt` | `1beeb3a6c6bacf7cf11d1a7d498b38a2ba0b340711cebee37bafb68458ad41d3` |
| `Selected schema` | `44cf68eadef6593496d41cec966d2e49251e1451070e940012c8129b375244c0` |
| `app/analyze.py` | `220b3bce5050131faa27c2ed091ff3d97d19ab1aec85724f238540072418939a` |
| `app/prompts.py` | `73f0aa27331b20c63630b1d74755a6217bc771901c618e0fbf51ef884ee42af4` |
| `eval/run_eval.py` | `e0f8d6fb707628a4816882148ca8b90d8400f1f724a9884ec08e5defb4cc1137` |
| `phishhook/engine.py` | `16f3fa0180d9c10a59cdbb844632e34dd4b5178edd28cee06d81d3f81c441db7` |

The configured model is `tinker:Qwen/Qwen3-8B`. Declared generation settings are temperature 0.2, maximum output 4,000 tokens, timeout 30 seconds, zero transport retries, and at most one validation correction. Hashed provider source binds the actual implementation. Requests ran with at most three workers; credentials and raw model responses are excluded from reports and journals.

## Use and remaining limits

Use the existing one-window [Windows launcher](../scripts/README.md) and retain explicit Tinker permission and synthetic-demo restrictions. Deployment status belongs in [private staging guidance](PRIVATE_STAGING.md); this evaluation alone does not prove that a candidate serves production traffic or that its result was displayed in Chrome.

Exact quote validation proves textual grounding, not semantic truth. Narrow bank-negation patterns do not cover every English phrasing; negation handling is local to its clause. The v3 default also enables the existing v2 routine-notification gating: medium-confidence model signs may be dropped when no rule fired, and a routine reading can reduce a rubric-only red verdict to amber when at most one rule kind remains. The score can still require red; the partial Gmail flow never becomes `pay`.

Pressure demotion and routine-message clarification can lose warnings on superficially ordinary malicious attachment requests. Neither sender authentication nor attachment contents were established. A small balanced sample from one public dataset cannot establish real-world prevalence, performance on new campaigns or payroll-specific accuracy. Model calls are stochastic, and one final run does not measure repeat-run variability. No findings never means safe; independent verification and company payment controls still apply.

## Deployment and browser observations

After the final evaluation, Cloud Run readback confirmed revision `phish-staging-p1-d08fe1b-a004` at 100% traffic with tag `p1-ai`, retaining earlier AI and rules-only routes. Before promotion, tagged-canary checks returned anonymous 403, wrong token 401, both request guards 409, and session/analysis/challenge 200. The complete synthetic analysis returned 16 findings in 7,266 ms; challenge returned `still_concerning` in 2,484 ms. Those paid calls were not repeated at the promoted base URL for this evidence.

All six known synthetic canary checks passed. Actual Chrome displayed T10's P1 canary result with its retained identity warning, routine-content summary, pressure notes and incomplete scope. Identity still contributes to sender and pressure rubric dimensions. This demonstrates that specific rendering path; it does not change the benchmark counts or imply sender authentication. The existing A003 T23 image remains a historical UI illustration. [Private staging guidance](PRIVATE_STAGING.md) owns current runtime/base-route verification status.

Promoted-base verification then returned session 200 with Tinker for all routes, anonymous 403, wrong token 401 and guards 409. The immediate before/after P1 runtime audit passed 57 required assertions with unchanged IAM/runtime/environment/secret references/resources and no public IAM. Twenty-four source files matched working, staged and frozen manifests; no running-container extraction is claimed. The retained legacy rules-only route reports rules-only, including when given the AI guard; current P1 guards reject mismatches, and connector model validation refuses wrong-model replies.
