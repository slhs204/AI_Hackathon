# Eval report (blind) — 2026-11-07 20:05 UTC

Model: `anthropic:claude-sonnet-5-5`. 200 synthetic cases. Counts only; not a real-world accuracy claim.

| metric | gmail |
|---|---|
| phishing_flagged | 100/100 |
| legit_false_alarms | 24/100 |
| ambiguous_flagged | 0/0 |
| must_flag_misses | 0 |
| incomplete_results | 0 |
| model_findings_kept | 231 |
| model_findings_discarded | 0 |
| model_unavailable | 0 |
| latency_ms_median | 2834 |
| latency_ms_max | 4722 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| legit-001 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 3013 |
| legit-002 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2807 |
| legit-003 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2814 |
| legit-004 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 4269 |
| legit-005 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1748 |
| legit-006 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1796 |
| legit-007 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1252 |
| legit-008 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1934 |
| legit-009 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1986 |
| legit-010 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1206 |
| legit-011 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1352 |
| legit-012 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1262 |
| legit-013 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1775 |
| legit-014 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1822 |
| legit-015 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1943 |
| legit-016 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1930 |
| legit-017 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1753 |
| legit-018 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1964 |
| legit-019 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1292 |
| legit-020 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1613 |
| legit-021 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1244 |
| legit-022 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2879 |
| legit-023 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1605 |
| legit-024 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1869 |
| legit-025 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2093 |
| legit-026 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1621 |
| legit-027 | legit | needs_verification | pay | 16 | 2 | manipulation_cue, urgency_pressure | — | 3154 |
| legit-028 | legit | needs_verification | pay | 8 | 1 | sender_impersonation | — | 2670 |
| legit-029 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1865 |
| legit-030 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1898 |
| legit-031 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1329 |
| legit-032 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1431 |
| legit-033 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1611 |
| legit-034 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 3574 |
| legit-035 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2414 |
| legit-036 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1639 |
| legit-037 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1691 |
| legit-038 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1672 |
| legit-039 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1295 |
| legit-040 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1545 |
| legit-041 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1293 |
| legit-042 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1737 |
| legit-043 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1983 |
| legit-044 | legit | needs_verification | pay | 8 | 1 | urgency_pressure | — | 2119 |
| legit-045 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1665 |
| legit-046 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 3216 |
| legit-047 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1358 |
| legit-048 | legit | needs_verification | pay | 8 | 1 | sender_impersonation | — | 2977 |
| legit-049 | legit | needs_verification | pay | 8 | 1 | urgency_pressure | — | 2024 |
| legit-050 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1235 |
| legit-051 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1891 |
| legit-052 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1611 |
| legit-053 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1803 |
| legit-054 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2683 |
| legit-055 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1723 |
| legit-056 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1803 |
| legit-057 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1233 |
| legit-058 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1913 |
| legit-059 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1615 |
| legit-060 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1590 |
| legit-061 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2601 |
| legit-062 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1865 |
| legit-063 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1841 |
| legit-064 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1803 |
| legit-065 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2791 |
| legit-066 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1222 |
| legit-067 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 3354 |
| legit-068 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1727 |
| legit-069 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2810 |
| legit-070 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1797 |
| legit-071 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1545 |
| legit-072 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2785 |
| legit-073 | legit | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1882 |
| legit-074 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1727 |
| legit-075 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 3029 |
| legit-076 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1797 |
| legit-077 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1942 |
| legit-078 | legit | needs_verification | pay | 16 | 2 | sender_impersonation, urgency_pressure | — | 2858 |
| legit-079 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1840 |
| legit-080 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1619 |
| legit-081 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1681 |
| legit-082 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1745 |
| legit-083 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1705 |
| legit-084 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 3156 |
| legit-085 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1148 |
| legit-086 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1292 |
| legit-087 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1531 |
| legit-088 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1428 |
| legit-089 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2997 |
| legit-090 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1737 |
| legit-091 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 3264 |
| legit-092 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1640 |
| legit-093 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1705 |
| legit-094 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1291 |
| legit-095 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1915 |
| legit-096 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 3032 |
| legit-097 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1742 |
| legit-098 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1569 |
| legit-099 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2843 |
| legit-100 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1840 |
| phish-0001 | phishing | needs_verification | verify | 32 | 4 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 3933 |
| phish-0002 | phishing | needs_verification | pay | 24 | 3 | risky_attachment, urgency_pressure | — | 2967 |
| phish-0003 | phishing | needs_verification | verify | 16 | 3 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 3711 |
| phish-0004 | phishing | needs_verification | verify | 16 | 3 | authority_impersonation, deceptive_link, payment_or_data_request | — | 3794 |
| phish-0005 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, sender_impersonation | — | 3278 |
| phish-0006 | phishing | needs_verification | pay | 16 | 2 | sender_impersonation, urgency_pressure | — | 3661 |
| phish-0007 | phishing | needs_verification | verify | 36 | 4 | deceptive_link, payment_or_data_request, sender_impersonation | — | 4667 |
| phish-0008 | phishing | needs_verification | verify | 16 | 3 | deceptive_link, payment_or_data_request, sender_impersonation | — | 4367 |
| phish-0009 | phishing | needs_verification | verify | 44 | 4 | authority_impersonation, payment_or_data_request, risky_attachment, urgency_pressure | — | 3991 |
| phish-0010 | phishing | needs_verification | verify | 16 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 4092 |
| phish-0011 | phishing | needs_verification | verify | 46 | 3 | risky_attachment, sender_impersonation, urgency_pressure | — | 3800 |
| phish-0012 | phishing | needs_verification | pay | 16 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 3928 |
| phish-0013 | phishing | needs_verification | verify | 16 | 2 | payment_or_data_request, urgency_pressure | — | 3208 |
| phish-0014 | phishing | needs_verification | pay | 24 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 3749 |
| phish-0015 | phishing | needs_verification | pay | 16 | 2 | manipulation_cue, risky_attachment | — | 3693 |
| phish-0016 | phishing | needs_verification | verify | 46 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 3740 |
| phish-0017 | phishing | needs_verification | pay | 16 | 2 | manipulation_cue, risky_attachment | — | 3507 |
| phish-0018 | phishing | needs_verification | pay | 16 | 3 | authority_impersonation, deceptive_link, urgency_pressure | — | 3722 |
| phish-0019 | phishing | needs_verification | pay | 16 | 2 | sender_impersonation, urgency_pressure | — | 3569 |
| phish-0020 | phishing | needs_verification | pay | 24 | 3 | authority_impersonation, risky_attachment, urgency_pressure | — | 3777 |
| phish-0021 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, manipulation_cue | — | 3431 |
| phish-0022 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 3279 |
| phish-0023 | phishing | needs_verification | pay | 16 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 4192 |
| phish-0024 | phishing | needs_verification | pay | 24 | 3 | deceptive_link, manipulation_cue, urgency_pressure | — | 3469 |
| phish-0025 | phishing | needs_verification | pay | 16 | 3 | manipulation_cue, risky_attachment, urgency_pressure | — | 3980 |
| phish-0026 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, manipulation_cue | — | 3005 |
| phish-0027 | phishing | needs_verification | verify | 16 | 3 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 4079 |
| phish-0028 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, manipulation_cue | — | 2997 |
| phish-0029 | phishing | needs_verification | pay | 24 | 3 | risky_attachment, sender_impersonation, urgency_pressure | — | 4116 |
| phish-0030 | phishing | needs_verification | verify | 36 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 4068 |
| phish-0031 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, manipulation_cue | — | 3441 |
| phish-0032 | phishing | needs_verification | verify | 16 | 3 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 4331 |
| phish-0033 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 3727 |
| phish-0034 | phishing | needs_verification | pay | 8 | 1 | urgency_pressure | — | 2655 |
| phish-0035 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, sender_impersonation | — | 3490 |
| phish-0036 | phishing | needs_verification | pay | 16 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 3779 |
| phish-0037 | phishing | needs_verification | verify | 16 | 2 | deceptive_link, payment_or_data_request | — | 3472 |
| phish-0038 | phishing | needs_verification | pay | 16 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 4037 |
| phish-0039 | phishing | needs_verification | pay | 16 | 2 | manipulation_cue, risky_attachment | — | 3581 |
| phish-0040 | phishing | needs_verification | pay | 16 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 4667 |
| phish-0041 | phishing | needs_verification | verify | 16 | 3 | authority_impersonation, payment_or_data_request, urgency_pressure | — | 4175 |
| phish-0042 | phishing | needs_verification | verify | 16 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 3320 |
| phish-0043 | phishing | needs_verification | pay | 16 | 2 | authority_impersonation, risky_attachment | — | 3900 |
| phish-0044 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, manipulation_cue | — | 3538 |
| phish-0045 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 3275 |
| phish-0046 | phishing | needs_verification | verify | 16 | 3 | deceptive_link, payment_or_data_request, sender_impersonation | — | 4053 |
| phish-0047 | phishing | needs_verification | pay | 16 | 2 | manipulation_cue, urgency_pressure | — | 3552 |
| phish-0048 | phishing | needs_verification | pay | 16 | 3 | risky_attachment, sender_impersonation, urgency_pressure | — | 4458 |
| phish-0049 | phishing | needs_verification | pay | 8 | 1 | urgency_pressure | — | 2693 |
| phish-0050 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, manipulation_cue | — | 3598 |
| phish-0051 | phishing | needs_verification | verify | 36 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 3719 |
| phish-0052 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 2771 |
| phish-0053 | phishing | needs_verification | verify | 16 | 3 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 4470 |
| phish-0054 | phishing | needs_verification | pay | 16 | 3 | authority_impersonation, deceptive_link, urgency_pressure | — | 4148 |
| phish-0055 | phishing | needs_verification | verify | 16 | 3 | payment_or_data_request, risky_attachment, sender_impersonation | — | 4484 |
| phish-0056 | phishing | needs_verification | pay | 16 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 4263 |
| phish-0057 | phishing | needs_verification | verify | 36 | 5 | deceptive_link, payment_or_data_request, sender_impersonation, urgency_pressure | — | 4722 |
| phish-0058 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, urgency_pressure | — | 2823 |
| phish-0059 | phishing | needs_verification | verify | 24 | 3 | payment_or_data_request, risky_attachment, urgency_pressure | — | 3234 |
| phish-0060 | phishing | needs_verification | verify | 16 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 3924 |
| phish-0061 | phishing | needs_verification | pay | 16 | 3 | risky_attachment, sender_impersonation, urgency_pressure | — | 4699 |
| phish-0062 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, urgency_pressure | — | 3296 |
| phish-0063 | phishing | needs_verification | verify | 16 | 2 | payment_or_data_request, urgency_pressure | — | 2419 |
| phish-0064 | phishing | needs_verification | verify | 16 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 4093 |
| phish-0065 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 3195 |
| phish-0066 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, sender_impersonation | — | 3390 |
| phish-0067 | phishing | needs_verification | pay | 16 | 2 | manipulation_cue, risky_attachment | — | 3376 |
| phish-0068 | phishing | needs_verification | pay | 8 | 1 | authority_impersonation | — | 2691 |
| phish-0069 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, urgency_pressure | — | 2946 |
| phish-0070 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2403 |
| phish-0071 | phishing | needs_verification | verify | 16 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 4100 |
| phish-0072 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2871 |
| phish-0073 | phishing | needs_verification | pay | 16 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 4185 |
| phish-0074 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, urgency_pressure | — | 3494 |
| phish-0075 | phishing | needs_verification | pay | 16 | 2 | manipulation_cue, risky_attachment | — | 3750 |
| phish-0076 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, manipulation_cue | — | 3594 |
| phish-0077 | phishing | needs_verification | verify | 16 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 4193 |
| phish-0078 | phishing | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2671 |
| phish-0079 | phishing | needs_verification | pay | 24 | 3 | manipulation_cue, risky_attachment, urgency_pressure | — | 3921 |
| phish-0080 | phishing | needs_verification | verify | 28 | 2 | deceptive_link, payment_or_data_request | — | 2931 |
| phish-0081 | phishing | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2799 |
| phish-0082 | phishing | needs_verification | verify | 16 | 3 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 4095 |
| phish-0083 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 3460 |
| phish-0084 | phishing | needs_verification | pay | 8 | 1 | urgency_pressure | — | 2737 |
| phish-0085 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2535 |
| phish-0086 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, urgency_pressure | — | 3581 |
| phish-0087 | phishing | needs_verification | verify | 16 | 2 | manipulation_cue, payment_or_data_request | — | 3618 |
| phish-0088 | phishing | needs_verification | pay | 16 | 2 | sender_impersonation, urgency_pressure | — | 4005 |
| phish-0089 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2826 |
| phish-0090 | phishing | needs_verification | pay | 16 | 3 | deceptive_link, sender_impersonation, urgency_pressure | — | 4135 |
| phish-0091 | phishing | needs_verification | verify | 16 | 2 | authority_impersonation, payment_or_data_request | — | 3277 |
| phish-0092 | phishing | needs_verification | verify | 8 | 1 | payment_or_data_request | — | 2615 |
| phish-0093 | phishing | needs_verification | pay | 16 | 2 | authority_impersonation, risky_attachment | — | 3835 |
| phish-0094 | phishing | needs_verification | pay | 8 | 1 | sender_impersonation | — | 2251 |
| phish-0095 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 3211 |
| phish-0096 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, sender_impersonation | — | 3048 |
| phish-0097 | phishing | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2099 |
| phish-0098 | phishing | needs_verification | pay | 16 | 2 | authority_impersonation, risky_attachment | — | 3348 |
| phish-0099 | phishing | needs_verification | pay | 8 | 1 | urgency_pressure | — | 2969 |
| phish-0100 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, manipulation_cue | — | 2955 |
