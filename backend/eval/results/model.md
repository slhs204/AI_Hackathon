# Eval report (core) — 2026-11-07 20:02 UTC

Model: `anthropic:claude-sonnet-5-5`. 23 synthetic cases. Counts only; not a real-world accuracy claim.

| metric | full | gmail |
|---|---|---|
| phishing_flagged | 14/14 | 14/14 |
| legit_false_alarms | 3/7 | 3/7 |
| ambiguous_flagged | 2/2 | 2/2 |
| must_flag_misses | 0 | 0 |
| incomplete_results | 0 | 0 |
| model_findings_kept | 33 | 32 |
| model_findings_discarded | 0 | 0 |
| model_unavailable | 0 | 0 |
| latency_ms_median | 4312 | 3704 |
| latency_ms_max | 8205 | 6128 |

## Per case — full

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| ceo-w2-request | phishing | needs_verification | stop | 100 | 15 | authentication_failure, authority_impersonation, manipulation_cue, payment_or_data_request, reply_to_mismatch, sender_impersonation, urgency_pressure | — | 6845 |
| ceo-wire | phishing | needs_verification | stop | 100 | 16 | authentication_failure, authority_impersonation, manipulation_cue, payment_or_data_request, reply_to_mismatch, sender_impersonation, urgency_pressure | — | 8205 |
| cfo-gift-cards | phishing | needs_verification | stop | 98 | 8 | authority_impersonation, manipulation_cue, payment_or_data_request, urgency_pressure | — | 6762 |
| fake-docusign | phishing | needs_verification | stop | 100 | 10 | authentication_failure, deceptive_link, manipulation_cue, payment_or_data_request, sender_impersonation, urgency_pressure | — | 7052 |
| h-apple-cards | phishing | needs_verification | verify | 49 | 4 | authority_impersonation, manipulation_cue, payment_or_data_request, urgency_pressure | — | 4312 |
| h-compromised-vendor | phishing | needs_verification | verify | 16 | 3 | manipulation_cue, payment_or_data_request, risky_attachment | — | 4658 |
| h-helpdesk-password | phishing | needs_verification | stop | 74 | 5 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 4315 |
| h-legit-benefits | legit | needs_verification | pay | 16 | 2 | deceptive_link, urgency_pressure | — | 4673 |
| h-legit-ceo-review | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1827 |
| h-legit-urgent-cutoff | legit | needs_verification | pay | 24 | 4 | urgency_pressure | — | 2207 |
| h-legit-vendor-no-change | legit | needs_verification | verify | 20 | 3 | payment_or_data_request | — | 2447 |
| h-ssn-benefits | phishing | needs_verification | verify | 66 | 4 | manipulation_cue, payment_or_data_request, sender_impersonation, urgency_pressure | — | 4634 |
| h-thread-hijack | phishing | needs_verification | verify | 36 | 5 | manipulation_cue, payment_or_data_request, risky_attachment, urgency_pressure | — | 4304 |
| legit-cfo-memo | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1665 |
| legit-vendor-invoice | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2094 |
| m365-password | phishing | needs_verification | stop | 86 | 6 | deceptive_link, manipulation_cue, payment_or_data_request, sender_impersonation, urgency_pressure | — | 4447 |
| new-supplier-onboarding | ambiguous | needs_verification | verify | 48 | 5 | manipulation_cue, payment_or_data_request, risky_attachment | — | 3675 |
| payroll-direct-deposit | phishing | needs_verification | stop | 87 | 11 | authority_impersonation, manipulation_cue, payment_or_data_request, urgency_pressure | — | 5431 |
| vendor-bank-change | phishing | needs_verification | stop | 100 | 17 | authentication_failure, manipulation_cue, payment_or_data_request, reply_to_mismatch, sender_impersonation, urgency_pressure | — | 5733 |
| x-ambiguous-internal-change | ambiguous | needs_verification | verify | 36 | 4 | manipulation_cue, payment_or_data_request, urgency_pressure | — | 4224 |
| x-code-link | phishing | needs_verification | verify | 58 | 4 | deceptive_link, sender_impersonation, urgency_pressure | — | 3316 |
| x-legit-internal-reminder | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1531 |
| x-prompt-injection | phishing | needs_verification | verify | 66 | 5 | manipulation_cue, payment_or_data_request, sender_impersonation, urgency_pressure | — | 3968 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| ceo-w2-request | phishing | needs_verification | stop | 100 | 12 | authority_impersonation, manipulation_cue, payment_or_data_request, sender_impersonation, urgency_pressure | — | 4191 |
| ceo-wire | phishing | needs_verification | stop | 100 | 12 | authority_impersonation, manipulation_cue, payment_or_data_request, sender_impersonation, urgency_pressure | — | 6128 |
| cfo-gift-cards | phishing | needs_verification | stop | 98 | 9 | authority_impersonation, manipulation_cue, payment_or_data_request, urgency_pressure | — | 5533 |
| fake-docusign | phishing | needs_verification | stop | 94 | 8 | deceptive_link, manipulation_cue, payment_or_data_request, sender_impersonation, urgency_pressure | — | 5333 |
| h-apple-cards | phishing | needs_verification | verify | 49 | 5 | authority_impersonation, manipulation_cue, payment_or_data_request, urgency_pressure | — | 5008 |
| h-compromised-vendor | phishing | needs_verification | verify | 16 | 3 | manipulation_cue, payment_or_data_request, sender_impersonation | — | 5312 |
| h-helpdesk-password | phishing | needs_verification | stop | 74 | 5 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 3555 |
| h-legit-benefits | legit | needs_verification | pay | 16 | 2 | deceptive_link, urgency_pressure | — | 3704 |
| h-legit-ceo-review | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1760 |
| h-legit-urgent-cutoff | legit | needs_verification | pay | 24 | 4 | urgency_pressure | — | 2198 |
| h-legit-vendor-no-change | legit | needs_verification | verify | 20 | 3 | payment_or_data_request | — | 2425 |
| h-ssn-benefits | phishing | needs_verification | verify | 58 | 3 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 3752 |
| h-thread-hijack | phishing | needs_verification | verify | 36 | 5 | manipulation_cue, payment_or_data_request, risky_attachment, urgency_pressure | — | 4436 |
| legit-cfo-memo | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2058 |
| legit-vendor-invoice | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1310 |
| m365-password | phishing | needs_verification | stop | 86 | 6 | deceptive_link, manipulation_cue, payment_or_data_request, sender_impersonation, urgency_pressure | — | 3634 |
| new-supplier-onboarding | ambiguous | needs_verification | verify | 28 | 4 | manipulation_cue, payment_or_data_request | — | 3092 |
| payroll-direct-deposit | phishing | needs_verification | stop | 87 | 10 | authority_impersonation, manipulation_cue, payment_or_data_request, urgency_pressure | — | 3535 |
| vendor-bank-change | phishing | needs_verification | stop | 100 | 13 | manipulation_cue, payment_or_data_request, sender_impersonation, urgency_pressure | — | 4839 |
| x-ambiguous-internal-change | ambiguous | needs_verification | verify | 36 | 4 | manipulation_cue, payment_or_data_request, urgency_pressure | — | 3737 |
| x-code-link | phishing | needs_verification | verify | 58 | 4 | deceptive_link, sender_impersonation, urgency_pressure | — | 3197 |
| x-legit-internal-reminder | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1176 |
| x-prompt-injection | phishing | needs_verification | verify | 66 | 5 | authority_impersonation, manipulation_cue, payment_or_data_request, sender_impersonation | — | 4142 |
