# Eval report (blind) — 2026-11-08 10:14 UTC

Model: `rules-only`, prompt `-`, split `test`. 100 public/synthetic cases. Warning presence is independent of completeness; no-findings is not an all-clear. Counts only; not a real-world accuracy claim.
Existing blind test partition has historical Anthropic/rule exposure; it is not a newly untouched benchmark.

| metric | gmail |
|---|---|
| phishing_flagged | 12/50 |
| legit_false_alarms | 1/50 |
| ambiguous_flagged | 0/0 |
| must_flag_misses | 0 |
| incomplete_results | 100 |
| model_findings_kept | 0 |
| model_findings_discarded | 0 |
| model_unavailable | 0 |
| all_input_warnings | {'n': 100, 'tp': 12, 'fp': 1, 'tn': 49, 'fn': 38, 'precision': {'numerator': 12, 'denominator': 13, 'rate': 0.9230769230769231, 'wilson95': [0.6668604907890041, 0.9862895787574435]}, 'recall': {'numerator': 12, 'denominator': 50, 'rate': 0.24, 'wilson95': [0.1429739139699173, 0.3741268375794292]}, 'false_positive_rate': {'numerator': 1, 'denominator': 50, 'rate': 0.02, 'wilson95': [0.003539259271646236, 0.10495443589637815]}} |
| provider_success_warnings | {'n': 0, 'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0, 'precision': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'recall': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'false_positive_rate': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}} |
| complete_only_warnings | {'n': 0, 'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0, 'precision': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'recall': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}, 'false_positive_rate': {'numerator': 0, 'denominator': 0, 'rate': None, 'wilson95': None}} |
| completion_coverage | {'numerator': 0, 'denominator': 100, 'rate': 0.0, 'wilson95': [3.469446951953614e-18, 0.03699349820698568]} |
| provider_success_coverage | {'numerator': 0, 'denominator': 100, 'rate': 0.0, 'wilson95': [3.469446951953614e-18, 0.03699349820698568]} |
| outcomes_by_label | {'phishing': {'n': 50, 'warnings': 12, 'no_findings': 38, 'incomplete': 50, 'unfinished_no_findings': 38, 'provider_failures': 0}, 'legit': {'n': 50, 'warnings': 1, 'no_findings': 49, 'incomplete': 50, 'unfinished_no_findings': 49, 'provider_failures': 0}, 'ambiguous': {'n': 0, 'warnings': 0, 'no_findings': 0, 'incomplete': 0, 'unfinished_no_findings': 0, 'provider_failures': 0}} |
| model_calls | 0 |
| corrections | 0 |
| latency_ms_median | 0 |
| latency_ms_max | 16 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| legit-002 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 15 |
| legit-004 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-006 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-008 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-010 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-012 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-014 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-016 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-018 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-020 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-022 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-024 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-026 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-028 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-030 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-032 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-034 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-036 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-038 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-040 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-042 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-044 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-046 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-048 | legit | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| legit-050 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-052 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-054 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-056 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-058 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-060 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-062 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-064 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-066 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-068 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-070 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-072 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-074 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-076 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-078 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-080 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-082 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-084 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-086 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-088 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-090 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-092 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 16 |
| legit-094 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-096 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-098 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| legit-100 | legit | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0002 | phishing | insufficient_evidence | verify | 16 | 2 | urgency_pressure | — | 0 |
| phish-0004 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0006 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0008 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0010 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0012 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0014 | phishing | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 0 |
| phish-0016 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0018 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 16 |
| phish-0020 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0022 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0024 | phishing | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 0 |
| phish-0026 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0028 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0030 | phishing | insufficient_evidence | verify | 20 | 1 | payment_or_data_request | — | 0 |
| phish-0032 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0034 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0036 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0038 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 14 |
| phish-0040 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0042 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0044 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0046 | phishing | insufficient_evidence | verify | 30 | 1 | sender_impersonation | — | 0 |
| phish-0048 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0050 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0052 | phishing | insufficient_evidence | verify | 8 | 1 | urgency_pressure | — | 0 |
| phish-0054 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0056 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0058 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0060 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0062 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 16 |
| phish-0064 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0066 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0068 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0070 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0072 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0074 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0076 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0078 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0080 | phishing | insufficient_evidence | verify | 20 | 1 | payment_or_data_request | — | 0 |
| phish-0082 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0084 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0086 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0088 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 14 |
| phish-0090 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0092 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0094 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0096 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0098 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
| phish-0100 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 0 |
