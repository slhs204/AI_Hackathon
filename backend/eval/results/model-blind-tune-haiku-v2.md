# Eval report (blind) — 2026-11-07 20:16 UTC

Model: `anthropic:claude-haiku-5-5`, prompt `v2`, split `tune`. 100 synthetic cases. Counts only; not a real-world accuracy claim.

| metric | gmail |
|---|---|
| phishing_flagged | 49/50 |
| legit_false_alarms | 3/50 |
| ambiguous_flagged | 0/0 |
| must_flag_misses | 0 |
| incomplete_results | 0 |
| model_findings_kept | 50 |
| model_findings_discarded | 0 |
| model_unavailable | 0 |
| latency_ms_median | 1689 |
| latency_ms_max | 4557 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| legit-001 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 4557 |
| legit-003 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 4429 |
| legit-005 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 4515 |
| legit-007 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 4427 |
| legit-009 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1277 |
| legit-011 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1357 |
| legit-013 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1190 |
| legit-015 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1166 |
| legit-017 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 978 |
| legit-019 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1224 |
| legit-021 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1067 |
| legit-023 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1098 |
| legit-025 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1128 |
| legit-027 | legit | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1142 |
| legit-029 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 975 |
| legit-031 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1223 |
| legit-033 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 960 |
| legit-035 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1100 |
| legit-037 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1198 |
| legit-039 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1078 |
| legit-041 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1124 |
| legit-043 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 939 |
| legit-045 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1040 |
| legit-047 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1143 |
| legit-049 | legit | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1430 |
| legit-051 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 920 |
| legit-053 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 872 |
| legit-055 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1091 |
| legit-057 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1125 |
| legit-059 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 934 |
| legit-061 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1004 |
| legit-063 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1398 |
| legit-065 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 980 |
| legit-067 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1080 |
| legit-069 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 909 |
| legit-071 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1005 |
| legit-073 | legit | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1221 |
| legit-075 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1159 |
| legit-077 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 811 |
| legit-079 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 968 |
| legit-081 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 982 |
| legit-083 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1026 |
| legit-085 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1102 |
| legit-087 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1078 |
| legit-089 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 936 |
| legit-091 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1273 |
| legit-093 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 830 |
| legit-095 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1144 |
| legit-097 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1022 |
| legit-099 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2440 |
| phish-0001 | phishing | needs_verification | pay | 24 | 3 | sender_impersonation, urgency_pressure | — | 2315 |
| phish-0003 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1803 |
| phish-0005 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1965 |
| phish-0007 | phishing | needs_verification | verify | 28 | 3 | deceptive_link, payment_or_data_request | — | 2979 |
| phish-0009 | phishing | needs_verification | verify | 36 | 3 | payment_or_data_request, risky_attachment, urgency_pressure | — | 2245 |
| phish-0011 | phishing | needs_verification | verify | 38 | 2 | risky_attachment, sender_impersonation | — | 2135 |
| phish-0013 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1903 |
| phish-0015 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1778 |
| phish-0017 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2144 |
| phish-0019 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 2108 |
| phish-0021 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1684 |
| phish-0023 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, sender_impersonation | — | 2753 |
| phish-0025 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2058 |
| phish-0027 | phishing | needs_verification | pay | 8 | 1 | sender_impersonation | — | 1937 |
| phish-0029 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 2200 |
| phish-0031 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 2029 |
| phish-0033 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1775 |
| phish-0035 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1929 |
| phish-0037 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1863 |
| phish-0039 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1685 |
| phish-0041 | phishing | needs_verification | pay | 8 | 1 | authority_impersonation | — | 1815 |
| phish-0043 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1857 |
| phish-0045 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2025 |
| phish-0047 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1920 |
| phish-0049 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1969 |
| phish-0051 | phishing | needs_verification | verify | 36 | 3 | payment_or_data_request, sender_impersonation, urgency_pressure | — | 2249 |
| phish-0053 | phishing | needs_verification | pay | 8 | 1 | sender_impersonation | — | 1958 |
| phish-0055 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 3017 |
| phish-0057 | phishing | needs_verification | verify | 28 | 3 | deceptive_link, payment_or_data_request | — | 1973 |
| phish-0059 | phishing | needs_verification | verify | 24 | 3 | payment_or_data_request, risky_attachment, urgency_pressure | — | 3290 |
| phish-0061 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1963 |
| phish-0063 | phishing | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1777 |
| phish-0065 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1895 |
| phish-0067 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1597 |
| phish-0069 | phishing | needs_verification | pay | 8 | 1 | sender_impersonation | — | 1887 |
| phish-0071 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1974 |
| phish-0073 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1880 |
| phish-0075 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1694 |
| phish-0077 | phishing | needs_verification | pay | 8 | 1 | sender_impersonation | — | 1955 |
| phish-0079 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 1951 |
| phish-0081 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1743 |
| phish-0083 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1477 |
| phish-0085 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1735 |
| phish-0087 | phishing | no_obvious_indicators | pay | 0 | 0 | — | — | 1870 |
| phish-0089 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1669 |
| phish-0091 | phishing | needs_verification | pay | 8 | 1 | sender_impersonation | — | 1827 |
| phish-0093 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2019 |
| phish-0095 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1695 |
| phish-0097 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1823 |
| phish-0099 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1787 |
