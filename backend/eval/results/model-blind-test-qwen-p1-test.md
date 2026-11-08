# Eval report (blind) — 2026-11-08 10:13 UTC

Model: `tinker:Qwen/Qwen3-8B`, prompt `v3`, split `test`. 100 public/synthetic cases. Warning presence is independent of completeness; no-findings is not an all-clear. Counts only; not a real-world accuracy claim.
Existing blind test partition has historical Anthropic/rule exposure; it is not a newly untouched benchmark.

| metric | gmail |
|---|---|
| phishing_flagged | 49/50 |
| legit_false_alarms | 2/50 |
| ambiguous_flagged | 0/0 |
| must_flag_misses | 0 |
| incomplete_results | 100 |
| model_findings_kept | 54 |
| model_findings_discarded | 3 |
| model_unavailable | 0 |
| all_input_warnings | {'n': 100, 'tp': 49, 'fp': 2, 'tn': 48, 'fn': 1, 'precision': {'numerator': 49, 'denominator': 51, 'rate': 0.9607843137254902, 'wilson95': [0.8678369434463774, 0.9891789166471329]}, 'recall': {'numerator': 49, 'denominator': 50, 'rate': 0.98, 'wilson95': [0.8950455641036219, 0.9964607407283539]}, 'false_positive_rate': {'numerator': 2, 'denominator': 50, 'rate': 0.04, 'wilson95': [0.011038884327619805, 0.1346009068750702]}} |
| provider_success_warnings | {'n': 100, 'tp': 49, 'fp': 2, 'tn': 48, 'fn': 1, 'precision': {'numerator': 49, 'denominator': 51, 'rate': 0.9607843137254902, 'wilson95': [0.8678369434463774, 0.9891789166471329]}, 'recall': {'numerator': 49, 'denominator': 50, 'rate': 0.98, 'wilson95': [0.8950455641036219, 0.9964607407283539]}, 'false_positive_rate': {'numerator': 2, 'denominator': 50, 'rate': 0.04, 'wilson95': [0.011038884327619805, 0.1346009068750702]}} |
| complete_only_warnings | {'n': 0, 'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0, 'precision': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'recall': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'false_positive_rate': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}} |
| completion_coverage | {'numerator': 0, 'denominator': 100, 'rate': 0.0, 'wilson95': [3.469446951953614e-18, 0.03699349820698568]} |
| provider_success_coverage | {'numerator': 100, 'denominator': 100, 'rate': 1.0, 'wilson95': [0.9630065017930143, 1.0]} |
| outcomes_by_label | {'phishing': {'n': 50, 'warnings': 49, 'no_findings': 1, 'incomplete': 50, 'unfinished_no_findings': 1, 'provider_failures': 0}, 'legit': {'n': 50, 'warnings': 2, 'no_findings': 48, 'incomplete': 50, 'unfinished_no_findings': 48, 'provider_failures': 0}, 'ambiguous': {'n': 0, 'warnings': 0, 'no_findings': 0, 'incomplete': 0, 'unfinished_no_findings': 0, 'provider_failures': 0}} |
| model_calls | 100 |
| corrections | 0 |
| latency_ms_median | 1812 |
| latency_ms_max | 5516 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| legit-002 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2811 |
| legit-004 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 3250 |
| legit-006 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2781 |
| legit-008 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1500 |
| legit-010 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1672 |
| legit-012 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1391 |
| legit-014 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1953 |
| legit-016 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1781 |
| legit-018 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1687 |
| legit-020 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2281 |
| legit-022 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2328 |
| legit-024 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1812 |
| legit-026 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 3389 |
| legit-028 | legit | insufficient_evidence | verify | 8 | 1 | sender_impersonation | — | 2827 |
| legit-030 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1593 |
| legit-032 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1641 |
| legit-034 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2906 |
| legit-036 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2938 |
| legit-038 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1546 |
| legit-040 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1500 |
| legit-042 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1827 |
| legit-044 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 3078 |
| legit-046 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 3812 |
| legit-048 | legit | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 2016 |
| legit-050 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1687 |
| legit-052 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1406 |
| legit-054 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1733 |
| legit-056 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1313 |
| legit-058 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1327 |
| legit-060 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1640 |
| legit-062 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1641 |
| legit-064 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1485 |
| legit-066 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1875 |
| legit-068 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2312 |
| legit-070 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1844 |
| legit-072 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1687 |
| legit-074 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1515 |
| legit-076 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1281 |
| legit-078 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2796 |
| legit-080 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1203 |
| legit-082 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1516 |
| legit-084 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2391 |
| legit-086 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2343 |
| legit-088 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1562 |
| legit-090 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1093 |
| legit-092 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2093 |
| legit-094 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1296 |
| legit-096 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2093 |
| legit-098 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1514 |
| legit-100 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1812 |
| phish-0002 | phishing | insufficient_evidence | verify | 24 | 3 | risky_attachment, urgency_pressure | — | 2281 |
| phish-0004 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1875 |
| phish-0006 | phishing | insufficient_evidence | stop | 38 | 2 | deceptive_link, sender_impersonation | — | 3500 |
| phish-0008 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2218 |
| phish-0010 | phishing | insufficient_evidence | stop | 38 | 2 | deceptive_link, sender_impersonation | — | 2343 |
| phish-0012 | phishing | insufficient_evidence | stop | 38 | 2 | deceptive_link, sender_impersonation | — | 1983 |
| phish-0014 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, urgency_pressure | — | 2250 |
| phish-0016 | phishing | insufficient_evidence | stop | 38 | 2 | deceptive_link, sender_impersonation | — | 1811 |
| phish-0018 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2641 |
| phish-0020 | phishing | insufficient_evidence | stop | 24 | 3 | reply_to_mismatch, risky_attachment, urgency_pressure | — | 3547 |
| phish-0022 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 1718 |
| phish-0024 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, urgency_pressure | — | 1766 |
| phish-0026 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2093 |
| phish-0028 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2062 |
| phish-0030 | phishing | insufficient_evidence | verify | 28 | 2 | deceptive_link, payment_or_data_request | — | 2156 |
| phish-0032 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 3031 |
| phish-0034 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1781 |
| phish-0036 | phishing | insufficient_evidence | stop | 38 | 2 | deceptive_link, sender_impersonation | — | 1937 |
| phish-0038 | phishing | insufficient_evidence | verify | 8 | 1 | sender_impersonation | — | 2547 |
| phish-0040 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2062 |
| phish-0042 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, payment_or_data_request | — | 1467 |
| phish-0044 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1343 |
| phish-0046 | phishing | insufficient_evidence | stop | 38 | 2 | deceptive_link, sender_impersonation | — | 1592 |
| phish-0048 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 1516 |
| phish-0050 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1657 |
| phish-0052 | phishing | insufficient_evidence | verify | 16 | 2 | risky_attachment, urgency_pressure | — | 1562 |
| phish-0054 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1485 |
| phish-0056 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1514 |
| phish-0058 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1625 |
| phish-0060 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1656 |
| phish-0062 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1406 |
| phish-0064 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, urgency_pressure | — | 2436 |
| phish-0066 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1453 |
| phish-0068 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 3125 |
| phish-0070 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 2296 |
| phish-0072 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 1610 |
| phish-0074 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1500 |
| phish-0076 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1297 |
| phish-0078 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1532 |
| phish-0080 | phishing | insufficient_evidence | verify | 28 | 2 | deceptive_link, payment_or_data_request | — | 1717 |
| phish-0082 | phishing | insufficient_evidence | stop | 16 | 2 | deceptive_link, sender_impersonation | — | 1688 |
| phish-0084 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1608 |
| phish-0086 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1812 |
| phish-0088 | phishing | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 2936 |
| phish-0090 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1812 |
| phish-0092 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 4515 |
| phish-0094 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 5516 |
| phish-0096 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1953 |
| phish-0098 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 2453 |
| phish-0100 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2141 |
