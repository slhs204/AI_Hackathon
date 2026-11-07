# Eval report (core) — 2026-11-07 19:46 UTC

Model: `rules-only`. 23 synthetic cases. Counts only; not a real-world accuracy claim.

| metric | full | gmail |
|---|---|---|
| phishing_flagged | 13/14 | 13/14 |
| legit_false_alarms | 2/7 | 2/7 |
| ambiguous_flagged | 2/2 | 2/2 |
| must_flag_misses | 1 | 1 |
| incomplete_results | 0 | 0 |
| model_findings_kept | 0 | 0 |
| model_findings_discarded | 0 | 0 |
| latency_ms_median | 0 | 0 |
| latency_ms_max | 2 | 0 |

## Per case — full

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| ceo-w2-request | phishing | needs_verification | stop | 100 | 13 | authentication_failure, authority_impersonation, payment_or_data_request, reply_to_mismatch, sender_impersonation, urgency_pressure | — | 2 |
| ceo-wire | phishing | needs_verification | stop | 100 | 13 | authentication_failure, authority_impersonation, payment_or_data_request, reply_to_mismatch, sender_impersonation, urgency_pressure | — | 0 |
| cfo-gift-cards | phishing | needs_verification | stop | 90 | 6 | authority_impersonation, payment_or_data_request, urgency_pressure | — | 0 |
| fake-docusign | phishing | needs_verification | stop | 100 | 8 | authentication_failure, deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| h-apple-cards | phishing | needs_verification | verify | 33 | 2 | authority_impersonation, urgency_pressure | — | 0 |
| h-compromised-vendor | phishing | no_obvious_indicators | pay | 0 | 0 | — | payment_or_data_request | 0 |
| h-helpdesk-password | phishing | needs_verification | verify | 66 | 4 | deceptive_link, sender_impersonation, urgency_pressure | — | 0 |
| h-legit-benefits | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| h-legit-ceo-review | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| h-legit-urgent-cutoff | legit | needs_verification | pay | 24 | 4 | urgency_pressure | — | 0 |
| h-legit-vendor-no-change | legit | needs_verification | verify | 20 | 3 | payment_or_data_request | — | 0 |
| h-ssn-benefits | phishing | needs_verification | verify | 50 | 2 | payment_or_data_request, sender_impersonation | — | 0 |
| h-thread-hijack | phishing | needs_verification | verify | 20 | 2 | payment_or_data_request | — | 0 |
| legit-cfo-memo | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| legit-vendor-invoice | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| m365-password | phishing | needs_verification | stop | 78 | 5 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| new-supplier-onboarding | ambiguous | needs_verification | verify | 40 | 4 | payment_or_data_request, risky_attachment | — | 0 |
| payroll-direct-deposit | phishing | needs_verification | stop | 79 | 9 | authority_impersonation, payment_or_data_request, urgency_pressure | — | 0 |
| vendor-bank-change | phishing | needs_verification | stop | 100 | 15 | authentication_failure, payment_or_data_request, reply_to_mismatch, sender_impersonation, urgency_pressure | — | 0 |
| x-ambiguous-internal-change | ambiguous | needs_verification | verify | 20 | 2 | payment_or_data_request | — | 0 |
| x-code-link | phishing | needs_verification | verify | 50 | 3 | deceptive_link, sender_impersonation | — | 0 |
| x-legit-internal-reminder | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| x-prompt-injection | phishing | needs_verification | verify | 50 | 3 | payment_or_data_request, sender_impersonation | — | 0 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| ceo-w2-request | phishing | needs_verification | stop | 100 | 11 | authority_impersonation, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| ceo-wire | phishing | needs_verification | stop | 100 | 9 | authority_impersonation, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| cfo-gift-cards | phishing | needs_verification | stop | 90 | 6 | authority_impersonation, payment_or_data_request, urgency_pressure | — | 0 |
| fake-docusign | phishing | needs_verification | stop | 86 | 6 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| h-apple-cards | phishing | needs_verification | verify | 33 | 2 | authority_impersonation, urgency_pressure | — | 0 |
| h-compromised-vendor | phishing | no_obvious_indicators | pay | 0 | 0 | — | payment_or_data_request | 0 |
| h-helpdesk-password | phishing | needs_verification | verify | 66 | 4 | deceptive_link, sender_impersonation, urgency_pressure | — | 0 |
| h-legit-benefits | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| h-legit-ceo-review | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| h-legit-urgent-cutoff | legit | needs_verification | pay | 24 | 4 | urgency_pressure | — | 0 |
| h-legit-vendor-no-change | legit | needs_verification | verify | 20 | 3 | payment_or_data_request | — | 0 |
| h-ssn-benefits | phishing | needs_verification | verify | 50 | 2 | payment_or_data_request, sender_impersonation | — | 0 |
| h-thread-hijack | phishing | needs_verification | verify | 20 | 2 | payment_or_data_request | — | 0 |
| legit-cfo-memo | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| legit-vendor-invoice | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| m365-password | phishing | needs_verification | stop | 78 | 5 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| new-supplier-onboarding | ambiguous | needs_verification | verify | 20 | 3 | payment_or_data_request | — | 0 |
| payroll-direct-deposit | phishing | needs_verification | stop | 79 | 9 | authority_impersonation, payment_or_data_request, urgency_pressure | — | 0 |
| vendor-bank-change | phishing | needs_verification | stop | 96 | 11 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| x-ambiguous-internal-change | ambiguous | needs_verification | verify | 20 | 2 | payment_or_data_request | — | 0 |
| x-code-link | phishing | needs_verification | verify | 50 | 3 | deceptive_link, sender_impersonation | — | 0 |
| x-legit-internal-reminder | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 0 |
| x-prompt-injection | phishing | needs_verification | verify | 50 | 3 | payment_or_data_request, sender_impersonation | — | 0 |
