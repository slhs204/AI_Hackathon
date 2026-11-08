# P0 synthetic Gmail acceptance

Observed on November 8, 2026. All 13 identified synthetic messages were opened in real Chrome and their Gmail DOM requests captured through the extension's rules-only path. Those exact extracted requests were then submitted once per distinct input hash to the repaired private Cloud Run canary. This separates observed UI extraction and rules behavior from cloud AI behavior; it does not claim that every AI result was rendered in Chrome.

All 13 cloud requests returned HTTP 200 with `model=tinker:Qwen/Qwen3-8B`, without provider fallback. Every cloud response retained `analysis_complete=false` and `assessment=insufficient_evidence`. Gmail extraction covers only the last visible expanded message, not the full thread; raw authentication headers, Reply-To, and attachment contents are unavailable. Missing information remained a limitation, rather than an all-clear. Neither the captured UI rules result nor the cloud AI result returned a `pay` verdict for any case.

The table's expected behavior describes the visible synthetic content. A routine-content expectation does not authenticate its sender. The test transport used an outside Gmail address with several display names mapped to Acme's directory; identity mismatch warnings therefore require separate interpretation.

| Case and subject | Expected content behavior | Captured UI rules result | Cloud AI result | Cloud latency |
| --- | --- | --- | --- | --- |
| T06 Invoice GS-21007 remittance | Flag new payment account | `verify`; no findings | `stop`; model adds bank-change request and pressure | 8.687 s |
| T09 Draft handbook for review | Routine document review | `verify`; executive-name mismatch | `stop`; model incorrectly treats comments as sensitive-data request | 14.563 s |
| T10 URGENT: payroll cutoff today at 5pm | Routine deadline in usual portal | `verify`; identity mismatch and pressure words | `stop`; model overinterprets ordinary timesheets and closing sentence | 5.719 s |
| T11 Reminder: our bank details have not changed | Routine anti-fraud reminder; respect negation | `verify`; payment/data rules fire on negated bank-change language | `stop`; model adds sender-domain concern | 5.812 s |
| T12 Action needed to keep your coverage | Flag request to reply with SSN and date of birth | `verify`; payment/data request | `stop`; model adds pressure | 6.891 s |
| T13 RE: Invoice 4471 | Flag remittance change; attachment contents unknown | `verify`; payment/data request | `stop`; model adds attachment, manipulation and pressure concerns; attachment risk itself is not verified | 8.656 s |
| T14 October close timeline | Routine accounting deadlines and meeting | `verify`; executive-name mismatch | `stop`; model adds payment/data and pressure concerns to routine content | 10.984 s |
| T18 Change of direct deposit before payroll | Flag payroll account change and callback avoidance | `stop`; identity, payment/data and pressure findings | `stop`; no extra model findings | 11.031 s |
| T19 URGENT: Updated banking details for invoice #GS-20931 | Flag bank change, overdue wire and callback avoidance | `stop`; payment/data and pressure findings | `stop`; model adds manipulation | 3.859 s |
| T20 Quick favor before Friday | Flag direct-deposit change | `stop`; identity and payment/data findings | `stop`; model adds pressure | 3.656 s |
| T21 Mailbox quota | Investigate restore-quota click request and destination | `verify`; no findings | `verify`; model adds deceptive-link and pressure concerns; a finding alone does not establish a malicious destination | 5.203 s |
| T22 Reminder: timesheets due Thursday | Routine timesheet reminder; separately check displayed identity | `verify`; executive-name mismatch | `stop`; model adds deceptive-link, payment/data and deadline concerns beyond established evidence | 5.688 s |
| T23 Updated remittance details | Flag payment change and ignore embedded AI instructions | `verify`; payment/data finding | `stop`; model adds manipulation and sender concern; embedded instruction did not produce an all-clear | 2.671 s |

## Specific evidence and limitations

**T06 bank-change detection:** The cloud model added `payment_or_data_request` with verified text evidence in block `b1`: “kindly send this and future payments to our new account at Harbor Point Bank, routing 0110…, account 5520 1188 0042.” The finding received the `bank_account_change` policy and instructed the user to call the vendor using the number already on file and obtain a second approval. The account number is synthetic; the routing number is masked in this report.

**T19 format repair:** Before repair, two provider HTTP 200 responses ended in `invalid analysis text field`, rules-only fallback, and connector rejection. The exact original invalid field was not retained. The repair supplies the selected JSON schema in Tinker's system prompt and gives schema-path/type/enum feedback on the existing single corrective retry. The fresh actual-Gmail T19 request returned the required model with a usable analysis and no fallback. This demonstrates successful post-repair integration for this request; it does not prove which original field failed, whether this call needed its corrective retry, or universal model-format reliability.

**T22 identity:** The observed display name was Robert Chen, mapped in the synthetic directory to Acme Corp CFO, while the actual synthetic sender was an outside Gmail address. The rule explanation explicitly cites that name/domain mismatch. That supports checking the displayed identity; it does not prove real-world impersonation or authenticate any sender. The model's stronger claims about the ordinary portal text, timesheet submission and deadline are not established merely because their quoted text exists.

**Semantic false alarms:** T09's model finding quotes “Comments by next Wednesday, please.” and claims document feedback could extract sensitive information. T10 labels “Nothing else is needed from you. Thanks, Robert” as discouraging verification and treats usual-portal timesheets as sensitive data under pressure. T11's rules interpret negated bank-change language as a request. T14 and T22 also receive model concerns on routine content. Exact quote verification establishes textual grounding, not the truth of the model's interpretation. These cases are not semantic passes and this sample is not an accuracy benchmark.

## Verification scope

The repaired backend source passed **195 tests, with 1 skipped**. Focused regressions cover selected-schema forwarding, safe schema-path/type/enum feedback, successful correction, exhausted correction without leaking returned values, and existing fail-closed behavior. No provider-specific constrained-output API parameter was assumed. Transport automatic retries remain disabled; the existing maximum of one validation correction remains.

The local runner guards the approved synthetic subjects, known synthetic sender and Gmail partial-extraction markers, deduplicates by subject, records an attempted input hash before transmission, and skips recorded hashes on subsequent authorized tails. Thirteen requests to the repaired canary were observed across three batches; the two pre-repair T19 provider calls are excluded from this count. No failed request was blindly retried. No production tuning or broader benchmark was performed. Private credentials and account URLs are excluded from this document.


## Final promoted service and presentation checks

Revision `phish-staging-p0-6515a54-a003` was promoted to 100% traffic. Final base-route verification returned anonymous 403, wrong app token 401, and missing-AI/rules-only guard 409. Authenticated session reported `tinker:Qwen/Qwen3-8B` for triage, analysis and challenge. A complete synthetic fixture returned analysis HTTP 200 with 16 findings in 5,219 ms and challenge HTTP 200 with `still_concerning` in 1,750 ms. That complete fixture is separate from the 13 partial Gmail extractions in the table. These are integration checks, not accuracy claims.

Slide 2 of the [existing pitch deck](https://docs.google.com/presentation/d/1CCrNSYTw5kX93Awoa7PGRrvDzMnl8iXTW_qNm_IOvPs/edit) now uses the [current synthetic T23 cloud AI screenshot](assets/demo-ai.png). Readback confirmed all other slide element geometry unchanged, and a fresh thumbnail showed no overlap with the workflow caption. A completion reply was verified on the existing demo-picture comment; the thread remains resolved.

## Later P1 development and evaluation

This page preserves the November 8 P0 observations above. Subsequent development repaired the specific routine-content overinterpretations in T09, T10, T11, T14 and T22; real outside-domain directory-name warnings remain. T10 pressure became notes. T06 initially missed under v3, then passed one paid recheck after a generic bank-redirection rule repair. These known synthetic requests remain development regressions, excluded from the benchmark.

The frozen Qwen-assisted test warned on 49/50 phishing-labelled and 2/50 legitimate-labelled public inputs. All 100 analyses remained incomplete; no safe-sender or payment approval follows. See the [current evaluation report](QWEN_EVALUATION.md) for exact metrics, confidence intervals, historical test exposure and remaining errors. This later evaluation does not rewrite the earlier P0 Chrome or cloud observations.
