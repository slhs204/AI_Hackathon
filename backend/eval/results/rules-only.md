# Eval report — 2026-11-07 16:38 UTC

Model: `rules-only`. 14 synthetic cases. Counts only; not a real-world accuracy claim.

| metric | full | gmail |
|---|---|---|
| phishing_flagged | 9/9 | 9/9 |
| legit_false_alarms | 0/3 | 0/3 |
| ambiguous_flagged | 2/2 | 2/2 |
| must_flag_misses | 0 | 0 |
| incomplete_results | 0 | 0 |
| model_findings_kept | 0 | 0 |
| model_findings_discarded | 0 | 0 |
| latency_ms_median | 0 | 0 |
| latency_ms_max | 1 | 0 |

## Per case — full

| case | label | assessment | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|
| ceo-w2-request | phishing | needs_verification | 100 | 12 | authentication_failure, authority_impersonation, payment_or_data_request, reply_to_mismatch, sender_impersonation, urgency_pressure | — | 1 |
| ceo-wire | phishing | needs_verification | 100 | 13 | authentication_failure, authority_impersonation, payment_or_data_request, reply_to_mismatch, sender_impersonation, urgency_pressure | — | 0 |
| cfo-gift-cards | phishing | needs_verification | 90 | 6 | authority_impersonation, payment_or_data_request, urgency_pressure | — | 0 |
| fake-docusign | phishing | needs_verification | 100 | 8 | authentication_failure, deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| legit-cfo-memo | legit | no_obvious_indicators | 0 | 0 | — | — | 0 |
| legit-vendor-invoice | legit | no_obvious_indicators | 0 | 0 | — | — | 0 |
| m365-password | phishing | needs_verification | 78 | 5 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| new-supplier-onboarding | ambiguous | needs_verification | 40 | 4 | payment_or_data_request, risky_attachment | — | 0 |
| payroll-direct-deposit | phishing | needs_verification | 79 | 8 | authority_impersonation, payment_or_data_request, urgency_pressure | — | 0 |
| vendor-bank-change | phishing | needs_verification | 100 | 14 | authentication_failure, payment_or_data_request, reply_to_mismatch, sender_impersonation, urgency_pressure | — | 0 |
| x-ambiguous-internal-change | ambiguous | needs_verification | 20 | 2 | payment_or_data_request | — | 0 |
| x-code-link | phishing | needs_verification | 50 | 3 | deceptive_link, sender_impersonation | — | 0 |
| x-legit-internal-reminder | legit | no_obvious_indicators | 0 | 0 | — | — | 0 |
| x-prompt-injection | phishing | needs_verification | 20 | 1 | payment_or_data_request | — | 0 |

## Per case — gmail

| case | label | assessment | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|
| ceo-w2-request | phishing | needs_verification | 100 | 10 | authority_impersonation, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| ceo-wire | phishing | needs_verification | 100 | 9 | authority_impersonation, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| cfo-gift-cards | phishing | needs_verification | 90 | 6 | authority_impersonation, payment_or_data_request, urgency_pressure | — | 0 |
| fake-docusign | phishing | needs_verification | 86 | 6 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| legit-cfo-memo | legit | no_obvious_indicators | 0 | 0 | — | — | 0 |
| legit-vendor-invoice | legit | no_obvious_indicators | 0 | 0 | — | — | 0 |
| m365-password | phishing | needs_verification | 78 | 5 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| new-supplier-onboarding | ambiguous | needs_verification | 20 | 3 | payment_or_data_request | — | 0 |
| payroll-direct-deposit | phishing | needs_verification | 79 | 8 | authority_impersonation, payment_or_data_request, urgency_pressure | — | 0 |
| vendor-bank-change | phishing | needs_verification | 96 | 10 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 0 |
| x-ambiguous-internal-change | ambiguous | needs_verification | 20 | 2 | payment_or_data_request | — | 0 |
| x-code-link | phishing | needs_verification | 50 | 3 | deceptive_link, sender_impersonation | — | 0 |
| x-legit-internal-reminder | legit | no_obvious_indicators | 0 | 0 | — | — | 0 |
| x-prompt-injection | phishing | needs_verification | 20 | 1 | payment_or_data_request | — | 0 |
