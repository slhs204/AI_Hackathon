# Eval report (blind) — 2026-11-08 10:04 UTC

Model: `tinker:Qwen/Qwen3-8B`, prompt `v1`, split `tune`. 100 public/synthetic cases. Warning presence is independent of completeness; no-findings is not an all-clear. Counts only; not a real-world accuracy claim.
Existing blind test partition has historical Anthropic/rule exposure; it is not a newly untouched benchmark.

| metric | gmail |
|---|---|
| phishing_flagged | 50/50 |
| legit_false_alarms | 44/50 |
| ambiguous_flagged | 0/0 |
| must_flag_misses | 0 |
| incomplete_results | 100 |
| model_findings_kept | 165 |
| model_findings_discarded | 53 |
| model_unavailable | 0 |
| all_input_warnings | {'n': 100, 'tp': 50, 'fp': 44, 'tn': 6, 'fn': 0, 'precision': {'numerator': 50, 'denominator': 94, 'rate': 0.5319148936170213, 'wilson95': [0.4317826374815637, 0.6295410597764227]}, 'recall': {'numerator': 50, 'denominator': 50, 'rate': 1.0, 'wilson95': [0.9286524008666414, 1.0]}, 'false_positive_rate': {'numerator': 44, 'denominator': 50, 'rate': 0.88, 'wilson95': [0.7619518261679701, 0.9438239984906773]}} |
| provider_success_warnings | {'n': 100, 'tp': 50, 'fp': 44, 'tn': 6, 'fn': 0, 'precision': {'numerator': 50, 'denominator': 94, 'rate': 0.5319148936170213, 'wilson95': [0.4317826374815637, 0.6295410597764227]}, 'recall': {'numerator': 50, 'denominator': 50, 'rate': 1.0, 'wilson95': [0.9286524008666414, 1.0]}, 'false_positive_rate': {'numerator': 44, 'denominator': 50, 'rate': 0.88, 'wilson95': [0.7619518261679701, 0.9438239984906773]}} |
| complete_only_warnings | {'n': 0, 'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0, 'precision': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'recall': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'false_positive_rate': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}} |
| completion_coverage | {'numerator': 0, 'denominator': 100, 'rate': 0.0, 'wilson95': [3.469446951953614e-18, 0.03699349820698568]} |
| provider_success_coverage | {'numerator': 100, 'denominator': 100, 'rate': 1.0, 'wilson95': [0.9630065017930143, 1.0]} |
| outcomes_by_label | {'phishing': {'n': 50, 'warnings': 50, 'no_findings': 0, 'incomplete': 50, 'unfinished_no_findings': 0, 'provider_failures': 0}, 'legit': {'n': 50, 'warnings': 44, 'no_findings': 6, 'incomplete': 50, 'unfinished_no_findings': 6, 'provider_failures': 0}, 'ambiguous': {'n': 0, 'warnings': 0, 'no_findings': 0, 'incomplete': 0, 'unfinished_no_findings': 0, 'provider_failures': 0}} |
| model_calls | 105 |
| corrections | 5 |
| latency_ms_median | 3999 |
| latency_ms_max | 15266 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| legit-001 | legit | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, reply_to_mismatch | — | 7608 |
| legit-003 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 4717 |
| legit-005 | legit | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, sender_impersonation | — | 6327 |
| legit-007 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2483 |
| legit-009 | legit | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, reply_to_mismatch | — | 3453 |
| legit-011 | legit | insufficient_evidence | verify | 16 | 3 | manipulation_cue, reply_to_mismatch, urgency_pressure | — | 3703 |
| legit-013 | legit | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, reply_to_mismatch | — | 2500 |
| legit-015 | legit | insufficient_evidence | verify | 16 | 2 | manipulation_cue, reply_to_mismatch | — | 3843 |
| legit-017 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 2625 |
| legit-019 | legit | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, sender_impersonation | — | 3985 |
| legit-021 | legit | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, urgency_pressure | — | 12485 |
| legit-023 | legit | insufficient_evidence | verify | 8 | 1 | payment_or_data_request | — | 2375 |
| legit-025 | legit | insufficient_evidence | verify | 16 | 2 | manipulation_cue, reply_to_mismatch | — | 4266 |
| legit-027 | legit | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, urgency_pressure | — | 3983 |
| legit-029 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 2968 |
| legit-031 | legit | insufficient_evidence | verify | 16 | 3 | reply_to_mismatch, sender_impersonation, urgency_pressure | — | 4296 |
| legit-033 | legit | insufficient_evidence | verify | 16 | 2 | reply_to_mismatch, sender_impersonation | — | 3530 |
| legit-035 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 3391 |
| legit-037 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 3437 |
| legit-039 | legit | insufficient_evidence | verify | 16 | 2 | manipulation_cue, reply_to_mismatch | — | 5422 |
| legit-041 | legit | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, reply_to_mismatch | — | 3421 |
| legit-043 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 3703 |
| legit-045 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 3062 |
| legit-047 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 5046 |
| legit-049 | legit | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 6562 |
| legit-051 | legit | insufficient_evidence | verify | 8 | 1 | sender_impersonation | — | 4094 |
| legit-053 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 4108 |
| legit-055 | legit | insufficient_evidence | stop | 16 | 2 | manipulation_cue, payment_or_data_request | — | 6264 |
| legit-057 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 3562 |
| legit-059 | legit | insufficient_evidence | stop | 16 | 3 | payment_or_data_request, reply_to_mismatch, sender_impersonation | — | 3485 |
| legit-061 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 4062 |
| legit-063 | legit | insufficient_evidence | verify | 16 | 2 | manipulation_cue, reply_to_mismatch | — | 4485 |
| legit-065 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 9125 |
| legit-067 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 2750 |
| legit-069 | legit | insufficient_evidence | verify | 8 | 1 | payment_or_data_request | — | 2938 |
| legit-071 | legit | insufficient_evidence | verify | 8 | 1 | manipulation_cue | — | 3406 |
| legit-073 | legit | insufficient_evidence | verify | 16 | 2 | reply_to_mismatch, urgency_pressure | — | 4750 |
| legit-075 | legit | insufficient_evidence | verify | 16 | 3 | manipulation_cue, reply_to_mismatch, sender_impersonation | — | 2889 |
| legit-077 | legit | insufficient_evidence | verify | 8 | 1 | reply_to_mismatch | — | 3797 |
| legit-079 | legit | insufficient_evidence | stop | 16 | 3 | manipulation_cue, payment_or_data_request, reply_to_mismatch | — | 4125 |
| legit-081 | legit | insufficient_evidence | stop | 16 | 3 | manipulation_cue, payment_or_data_request, reply_to_mismatch | — | 4046 |
| legit-083 | legit | insufficient_evidence | verify | 8 | 1 | manipulation_cue | — | 5171 |
| legit-085 | legit | insufficient_evidence | verify | 8 | 1 | manipulation_cue | — | 3781 |
| legit-087 | legit | insufficient_evidence | verify | 8 | 1 | manipulation_cue | — | 4014 |
| legit-089 | legit | insufficient_evidence | verify | 16 | 3 | manipulation_cue, reply_to_mismatch, urgency_pressure | — | 7141 |
| legit-091 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 3139 |
| legit-093 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 4781 |
| legit-095 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 4625 |
| legit-097 | legit | insufficient_evidence | verify | 16 | 2 | manipulation_cue, reply_to_mismatch | — | 4796 |
| legit-099 | legit | insufficient_evidence | verify | 16 | 3 | manipulation_cue, reply_to_mismatch, sender_impersonation | — | 12358 |
| phish-0001 | phishing | insufficient_evidence | stop | 62 | 5 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 7359 |
| phish-0003 | phishing | insufficient_evidence | stop | 46 | 3 | deceptive_link, payment_or_data_request, sender_impersonation | — | 10233 |
| phish-0005 | phishing | insufficient_evidence | stop | 46 | 3 | payment_or_data_request, risky_attachment, sender_impersonation | — | 7437 |
| phish-0007 | phishing | insufficient_evidence | stop | 73 | 4 | deceptive_link, payment_or_data_request, sender_impersonation | — | 8375 |
| phish-0009 | phishing | insufficient_evidence | stop | 44 | 5 | payment_or_data_request, reply_to_mismatch, risky_attachment, sender_impersonation, urgency_pressure | — | 5531 |
| phish-0011 | phishing | insufficient_evidence | stop | 38 | 2 | risky_attachment, sender_impersonation | — | 9110 |
| phish-0013 | phishing | insufficient_evidence | stop | 16 | 3 | deceptive_link, manipulation_cue, payment_or_data_request | — | 3139 |
| phish-0015 | phishing | insufficient_evidence | stop | 16 | 3 | reply_to_mismatch, risky_attachment, sender_impersonation | — | 4422 |
| phish-0017 | phishing | insufficient_evidence | verify | 16 | 2 | risky_attachment, urgency_pressure | — | 9702 |
| phish-0019 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, urgency_pressure | — | 4828 |
| phish-0021 | phishing | insufficient_evidence | stop | 16 | 3 | payment_or_data_request, reply_to_mismatch, urgency_pressure | — | 6452 |
| phish-0023 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, urgency_pressure | — | 2343 |
| phish-0025 | phishing | insufficient_evidence | stop | 16 | 3 | payment_or_data_request, risky_attachment, urgency_pressure | — | 4766 |
| phish-0027 | phishing | insufficient_evidence | stop | 46 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 2858 |
| phish-0029 | phishing | insufficient_evidence | verify | 16 | 2 | risky_attachment, urgency_pressure | — | 5516 |
| phish-0031 | phishing | insufficient_evidence | stop | 16 | 3 | deceptive_link, manipulation_cue, reply_to_mismatch | — | 2531 |
| phish-0033 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 2360 |
| phish-0035 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 2796 |
| phish-0037 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 1812 |
| phish-0039 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 2735 |
| phish-0041 | phishing | insufficient_evidence | verify | 16 | 3 | reply_to_mismatch, sender_impersonation, urgency_pressure | — | 3891 |
| phish-0043 | phishing | insufficient_evidence | verify | 16 | 2 | risky_attachment, urgency_pressure | — | 3702 |
| phish-0045 | phishing | insufficient_evidence | verify | 16 | 2 | risky_attachment, urgency_pressure | — | 1952 |
| phish-0047 | phishing | insufficient_evidence | stop | 16 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 4343 |
| phish-0049 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, urgency_pressure | — | 2234 |
| phish-0051 | phishing | insufficient_evidence | stop | 36 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 15266 |
| phish-0053 | phishing | insufficient_evidence | stop | 46 | 3 | deceptive_link, payment_or_data_request, sender_impersonation | — | 8312 |
| phish-0055 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 7858 |
| phish-0057 | phishing | insufficient_evidence | stop | 73 | 4 | deceptive_link, payment_or_data_request, sender_impersonation | — | 5360 |
| phish-0059 | phishing | insufficient_evidence | stop | 24 | 3 | payment_or_data_request, risky_attachment, urgency_pressure | — | 4985 |
| phish-0061 | phishing | insufficient_evidence | verify | 16 | 3 | manipulation_cue, risky_attachment, urgency_pressure | — | 3983 |
| phish-0063 | phishing | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, urgency_pressure | — | 4781 |
| phish-0065 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 3953 |
| phish-0067 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 4218 |
| phish-0069 | phishing | insufficient_evidence | stop | 16 | 2 | payment_or_data_request, sender_impersonation | — | 3422 |
| phish-0071 | phishing | insufficient_evidence | stop | 16 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 2906 |
| phish-0073 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, manipulation_cue | — | 2031 |
| phish-0075 | phishing | insufficient_evidence | stop | 16 | 2 | reply_to_mismatch, risky_attachment | — | 3813 |
| phish-0077 | phishing | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 2235 |
| phish-0079 | phishing | insufficient_evidence | verify | 16 | 2 | risky_attachment, urgency_pressure | — | 3389 |
| phish-0081 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 4500 |
| phish-0083 | phishing | insufficient_evidence | verify | 16 | 2 | payment_or_data_request, risky_attachment | — | 3546 |
| phish-0085 | phishing | insufficient_evidence | stop | 16 | 3 | manipulation_cue, payment_or_data_request, risky_attachment | — | 4358 |
| phish-0087 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, payment_or_data_request | — | 4547 |
| phish-0089 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 3657 |
| phish-0091 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, payment_or_data_request | — | 2343 |
| phish-0093 | phishing | insufficient_evidence | verify | 16 | 2 | payment_or_data_request, risky_attachment | — | 3047 |
| phish-0095 | phishing | insufficient_evidence | verify | 8 | 1 | risky_attachment | — | 4765 |
| phish-0097 | phishing | insufficient_evidence | verify | 16 | 2 | deceptive_link, payment_or_data_request | — | 2327 |
| phish-0099 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 5358 |
