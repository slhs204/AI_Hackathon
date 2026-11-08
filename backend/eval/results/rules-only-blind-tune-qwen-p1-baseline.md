# Eval report (blind) — 2026-11-08 10:02 UTC

Model: `rules-only`, prompt `-`, split `tune`. 100 public/synthetic cases. Warning presence is independent of completeness; no-findings is not an all-clear. Counts only; not a real-world accuracy claim.
Existing blind test partition has historical Anthropic/rule exposure; it is not a newly untouched benchmark.

| metric | gmail |
|---|---|
| phishing_flagged | 14/50 |
| legit_false_alarms | 3/50 |
| ambiguous_flagged | 0/0 |
| must_flag_misses | 0 |
| incomplete_results | 100 |
| model_findings_kept | 0 |
| model_findings_discarded | 0 |
| model_unavailable | 0 |
| all_input_warnings | {'n': 100, 'tp': 14, 'fp': 3, 'tn': 47, 'fn': 36, 'precision': {'numerator': 14, 'denominator': 17, 'rate': 0.8235294117647058, 'wilson95': [0.5897054143116588, 0.9380887336237901]}, 'recall': {'numerator': 14, 'denominator': 50, 'rate': 0.28, 'wilson95': [0.17474170665911232, 0.4166512369595657]}, 'false_positive_rate': {'numerator': 3, 'denominator': 50, 'rate': 0.06, 'wilson95': [0.02061497034897397, 0.16217091688838173]}} |
| provider_success_warnings | {'n': 0, 'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0, 'precision': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'recall': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'false_positive_rate': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}} |
| complete_only_warnings | {'n': 0, 'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0, 'precision': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'recall': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'false_positive_rate': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}} |
| completion_coverage | {'numerator': 0, 'denominator': 100, 'rate': 0.0, 'wilson95': [3.469446951953614e-18, 0.03699349820698568]} |
| provider_success_coverage | {'numerator': 0, 'denominator': 100, 'rate': 0.0, 'wilson95': [3.469446951953614e-18, 0.03699349820698568]} |
| outcomes_by_label | {'phishing': {'n': 50, 'warnings': 14, 'no_findings': 36, 'incomplete': 50, 'unfinished_no_findings': 36, 'provider_failures': 0}, 'legit': {'n': 50, 'warnings': 3, 'no_findings': 47, 'incomplete': 50, 'unfinished_no_findings': 47, 'provider_failures': 0}, 'ambiguous': {'n': 0, 'warnings': 0, 'no_findings': 0, 'incomplete': 0, 'unfinished_no_findings': 0, 'provider_failures': 0}} |
| model_calls | 0 |
| corrections | 0 |
| latency_ms_median | 0 |
| latency_ms_max | 16 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| legit-001 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-003 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-005 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-007 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-009 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-011 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-013 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-015 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-017 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-019 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-021 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-023 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-025 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-027 | legit | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 14 |
| legit-029 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-031 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-033 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-035 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-037 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-039 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-041 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-043 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-045 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-047 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-049 | legit | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 0 |
| legit-051 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-053 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-055 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-057 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-059 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-061 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-063 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-065 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-067 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-069 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-071 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-073 | legit | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 0 |
| legit-075 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-077 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-079 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-081 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 16 |
| legit-083 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-085 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-087 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-089 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-091 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-093 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-095 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-097 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-099 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0001 | phishing | insufficient_evidence | verify | 46 | 3 | sender_impersonation, urgency_pressure | — | 0 |
| phish-0003 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0005 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0007 | phishing | insufficient_evidence | stop | 65 | 3 | payment_or_data_request, sender_impersonation | — | 0 |
| phish-0009 | phishing | insufficient_evidence | stop | 28 | 2 | payment_or_data_request, urgency_pressure | — | 0 |
| phish-0011 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0013 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 15 |
| phish-0015 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0017 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0019 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0021 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0023 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0025 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0027 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0029 | phishing | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 0 |
| phish-0031 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0033 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0035 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0037 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0039 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 14 |
| phish-0041 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0043 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0045 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0047 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0049 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0051 | phishing | insufficient_evidence | stop | 28 | 2 | payment_or_data_request, urgency_pressure | — | 0 |
| phish-0053 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0055 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0057 | phishing | insufficient_evidence | stop | 65 | 3 | payment_or_data_request, sender_impersonation | — | 0 |
| phish-0059 | phishing | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 0 |
| phish-0061 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0063 | phishing | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 0 |
| phish-0065 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0067 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 16 |
| phish-0069 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0071 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0073 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0075 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0077 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0079 | phishing | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 0 |
| phish-0081 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0083 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0085 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0087 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0089 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0091 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0093 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0095 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0097 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 16 |
| phish-0099 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
