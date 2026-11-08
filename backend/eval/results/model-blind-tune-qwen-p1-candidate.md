# Eval report (blind) — 2026-11-08 10:07 UTC

Model: `tinker:Qwen/Qwen3-8B`, prompt `v3`, split `tune`. 100 public/synthetic cases. Warning presence is independent of completeness; no-findings is not an all-clear. Counts only; not a real-world accuracy claim.
Existing blind test partition has historical Anthropic/rule exposure; it is not a newly untouched benchmark.

| metric | gmail |
|---|---|
| phishing_flagged | 49/50 |
| legit_false_alarms | 0/50 |
| ambiguous_flagged | 0/0 |
| must_flag_misses | 0 |
| incomplete_results | 100 |
| model_findings_kept | 58 |
| model_findings_discarded | 6 |
| model_unavailable | 0 |
| all_input_warnings | {'n': 100, 'tp': 49, 'fp': 0, 'tn': 50, 'fn': 1, 'precision': {'numerator': 49, 'denominator': 49, 'rate': 1.0, 'wilson95': [0.9273021807795035, 0.9999999999999999]}, 'recall': {'numerator': 49, 'denominator': 50, 'rate': 0.98, 'wilson95': [0.8950455641036219, 0.9964607407283539]}, 'false_positive_rate': {'numerator': 0, 'denominator': 50, 'rate': 0.0, 'wilson95': [6.938893903907228e-18, 0.07134759913335872]}} |
| provider_success_warnings | {'n': 100, 'tp': 49, 'fp': 0, 'tn': 50, 'fn': 1, 'precision': {'numerator': 49, 'denominator': 49, 'rate': 1.0, 'wilson95': [0.9273021807795035, 0.9999999999999999]}, 'recall': {'numerator': 49, 'denominator': 50, 'rate': 0.98, 'wilson95': [0.8950455641036219, 0.9964607407283539]}, 'false_positive_rate': {'numerator': 0, 'denominator': 50, 'rate': 0.0, 'wilson95': [6.938893903907228e-18, 0.07134759913335872]}} |
| complete_only_warnings | {'n': 0, 'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0, 'precision': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'recall': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'false_positive_rate': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}} |
| completion_coverage | {'numerator': 0, 'denominator': 100, 'rate': 0.0, 'wilson95': [3.469446951953614e-18, 0.03699349820698568]} |
| provider_success_coverage | {'numerator': 100, 'denominator': 100, 'rate': 1.0, 'wilson95': [0.9630065017930143, 1.0]} |
| outcomes_by_label | {'phishing': {'n': 50, 'warnings': 49, 'no_findings': 1, 'incomplete': 50, 'unfinished_no_findings': 1, 'provider_failures': 0}, 'legit': {'n': 50, 'warnings': 0, 'no_findings': 50, 'incomplete': 50, 'unfinished_no_findings': 50, 'provider_failures': 0}, 'ambiguous': {'n': 0, 'warnings': 0, 'no_findings': 0, 'incomplete': 0, 'unfinished_no_findings': 0, 'provider_failures': 0}} |
| model_calls | 100 |
| corrections | 0 |
| latency_ms_median | 1889 |
| latency_ms_max | 5625 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| legit-001 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2608 |
| legit-003 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2375 |
| legit-005 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2735 |
| legit-007 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1233 |
| legit-009 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2625 |
| legit-011 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1875 |
| legit-013 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1687 |
| legit-015 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1203 |
| legit-017 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1766 |
| legit-019 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 3233 |
| legit-021 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1985 |
| legit-023 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1468 |
| legit-025 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2093 |
| legit-027 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1641 |
| legit-029 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2812 |
| legit-031 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1156 |
| legit-033 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1156 |
| legit-035 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1891 |
| legit-037 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1639 |
| legit-039 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2031 |
| legit-041 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1219 |
| legit-043 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1187 |
| legit-045 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1657 |
| legit-047 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1437 |
| legit-049 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1577 |
| legit-051 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2187 |
| legit-053 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1952 |
| legit-055 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1828 |
| legit-057 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1609 |
| legit-059 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 3422 |
| legit-061 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1391 |
| legit-063 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1343 |
| legit-065 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1937 |
| legit-067 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1578 |
| legit-069 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1797 |
| legit-071 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2561 |
| legit-073 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1406 |
| legit-075 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1890 |
| legit-077 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1796 |
| legit-079 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2266 |
| legit-081 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1500 |
| legit-083 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1266 |
| legit-085 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1281 |
| legit-087 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1250 |
| legit-089 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2092 |
| legit-091 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1858 |
| legit-093 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1389 |
| legit-095 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1250 |
| legit-097 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1766 |
| legit-099 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 1531 |
| phish-0001 | phishing | insufficient_evidence | stop | 54 | 4 | deceptive_link, sender_impersonation, urgency_pressure | — | 1889 |
| phish-0003 | phishing | insufficient_evidence | stop | 38 | 2 | deceptive_link, sender_impersonation | — | 2797 |
| phish-0005 | phishing | insufficient_evidence | stop | 38 | 2 | risky_attachment, sender_impersonation | — | 2218 |
| phish-0007 | phishing | insufficient_evidence | stop | 73 | 4 | deceptive_link, payment_or_data_request, sender_impersonation | — | 1483 |
| phish-0009 | phishing | insufficient_evidence | stop | 44 | 4 | payment_or_data_request, risky_attachment, sender_impersonation, urgency_pressure | — | 1858 |
| phish-0011 | phishing | insufficient_evidence | stop | 38 | 2 | risky_attachment, sender_impersonation | — | 2172 |
| phish-0013 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2250 |
| phish-0015 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 2296 |
| phish-0017 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 2109 |
| phish-0019 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2952 |
| phish-0021 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2172 |
| phish-0023 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2375 |
| phish-0025 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 3343 |
| phish-0027 | phishing | insufficient_evidence | stop | 38 | 2 | deceptive_link, sender_impersonation | — | 2296 |
| phish-0029 | phishing | insufficient_evidence | verify | 16 | 2 | risky_attachment, urgency_pressure | — | 2156 |
| phish-0031 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2610 |
| phish-0033 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 2110 |
| phish-0035 | phishing | insufficient_evidence | stop | 16 | 2 | reply_to_mismatch, risky_attachment | — | 2781 |
| phish-0037 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2000 |
| phish-0039 | phishing | insufficient_evidence | stop | 16 | 2 | risky_attachment, sender_impersonation | — | 2218 |
| phish-0041 | phishing | insufficient_evidence | stop | 16 | 2 | authority_impersonation, deceptive_link | — | 2375 |
| phish-0043 | phishing | insufficient_evidence | stop | 16 | 2 | reply_to_mismatch, risky_attachment | — | 2985 |
| phish-0045 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 3592 |
| phish-0047 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2641 |
| phish-0049 | phishing | insufficient_evidence | verify | 16 | 2 | reply_to_mismatch, sender_impersonation | — | 3672 |
| phish-0051 | phishing | insufficient_evidence | stop | 36 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 2172 |
| phish-0053 | phishing | insufficient_evidence | stop | 38 | 2 | deceptive_link, sender_impersonation | — | 1563 |
| phish-0055 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 1703 |
| phish-0057 | phishing | insufficient_evidence | stop | 73 | 4 | deceptive_link, payment_or_data_request, sender_impersonation | — | 2125 |
| phish-0059 | phishing | insufficient_evidence | stop | 24 | 3 | payment_or_data_request, risky_attachment, urgency_pressure | — | 2843 |
| phish-0061 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 1342 |
| phish-0063 | phishing | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 5625 |
| phish-0065 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 1828 |
| phish-0067 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 2108 |
| phish-0069 | phishing | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, sender_impersonation | — | 3140 |
| phish-0071 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2467 |
| phish-0073 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1389 |
| phish-0075 | phishing | insufficient_evidence | stop | 16 | 2 | reply_to_mismatch, risky_attachment | — | 2452 |
| phish-0077 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1360 |
| phish-0079 | phishing | insufficient_evidence | verify | 16 | 2 | risky_attachment, urgency_pressure | — | 1625 |
| phish-0081 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1422 |
| phish-0083 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 1875 |
| phish-0085 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 2327 |
| phish-0087 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1452 |
| phish-0089 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 1421 |
| phish-0091 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1358 |
| phish-0093 | phishing | insufficient_evidence | stop | 16 | 2 | reply_to_mismatch, risky_attachment | — | 1735 |
| phish-0095 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 2733 |
| phish-0097 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1437 |
| phish-0099 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1782 |
