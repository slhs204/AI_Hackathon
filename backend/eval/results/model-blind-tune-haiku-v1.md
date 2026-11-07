# Eval report (blind) — 2026-11-07 20:16 UTC

Model: `anthropic:claude-haiku-5-5`, prompt `v1`, split `tune`. 100 synthetic cases. Counts only; not a real-world accuracy claim.

| metric | gmail |
|---|---|
| phishing_flagged | 49/50 |
| legit_false_alarms | 4/50 |
| ambiguous_flagged | 0/0 |
| must_flag_misses | 0 |
| incomplete_results | 3 |
| model_findings_kept | 52 |
| model_findings_discarded | 3 |
| model_unavailable | 0 |
| latency_ms_median | 1625 |
| latency_ms_max | 4796 |

## Per case — gmail

| case | label | assessment | verdict | score | findings | categories | missing | ms |
|---|---|---|---|---|---|---|---|---|
| legit-001 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2598 |
| legit-003 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2416 |
| legit-005 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2422 |
| legit-007 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 2530 |
| legit-009 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1083 |
| legit-011 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1239 |
| legit-013 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1064 |
| legit-015 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1129 |
| legit-017 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1041 |
| legit-019 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1315 |
| legit-021 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1012 |
| legit-023 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1201 |
| legit-025 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1012 |
| legit-027 | legit | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1591 |
| legit-029 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1067 |
| legit-031 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1336 |
| legit-033 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1042 |
| legit-035 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1028 |
| legit-037 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 974 |
| legit-039 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1401 |
| legit-041 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 980 |
| legit-043 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1021 |
| legit-045 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1979 |
| legit-047 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1135 |
| legit-049 | legit | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1433 |
| legit-051 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 997 |
| legit-053 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1025 |
| legit-055 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1205 |
| legit-057 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1280 |
| legit-059 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1199 |
| legit-061 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1047 |
| legit-063 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1165 |
| legit-065 | legit | needs_verification | pay | 8 | 1 | manipulation_cue | — | 2143 |
| legit-067 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1355 |
| legit-069 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1568 |
| legit-071 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1072 |
| legit-073 | legit | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1225 |
| legit-075 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1264 |
| legit-077 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1410 |
| legit-079 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1910 |
| legit-081 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1215 |
| legit-083 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1500 |
| legit-085 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1281 |
| legit-087 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1310 |
| legit-089 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1178 |
| legit-091 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1166 |
| legit-093 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1242 |
| legit-095 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1300 |
| legit-097 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1008 |
| legit-099 | legit | no_obvious_indicators | pay | 0 | 0 | — | — | 1398 |
| phish-0001 | phishing | needs_verification | pay | 24 | 3 | deceptive_link, urgency_pressure | — | 1832 |
| phish-0003 | phishing | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1669 |
| phish-0005 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, sender_impersonation | — | 2269 |
| phish-0007 | phishing | needs_verification | verify | 20 | 2 | payment_or_data_request | — | 1352 |
| phish-0009 | phishing | needs_verification | verify | 36 | 3 | payment_or_data_request, risky_attachment, urgency_pressure | — | 2351 |
| phish-0011 | phishing | needs_verification | verify | 46 | 3 | risky_attachment, sender_impersonation, urgency_pressure | — | 2467 |
| phish-0013 | phishing | no_obvious_indicators | pay | 0 | 0 | — | — | 1150 |
| phish-0015 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1844 |
| phish-0017 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1831 |
| phish-0019 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 1843 |
| phish-0021 | phishing | needs_verification | pay | 16 | 2 | authority_impersonation, deceptive_link | — | 2408 |
| phish-0023 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1650 |
| phish-0025 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1944 |
| phish-0027 | phishing | needs_verification | pay | 8 | 1 | urgency_pressure | — | 1943 |
| phish-0029 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 1798 |
| phish-0031 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 2029 |
| phish-0033 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1674 |
| phish-0035 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1833 |
| phish-0037 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1453 |
| phish-0039 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1570 |
| phish-0041 | phishing | needs_verification | pay | 8 | 1 | authority_impersonation | — | 1757 |
| phish-0043 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1806 |
| phish-0045 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1662 |
| phish-0047 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1829 |
| phish-0049 | phishing | insufficient_evidence | verify | 8 | 1 | deceptive_link | — | 2325 |
| phish-0051 | phishing | needs_verification | verify | 36 | 3 | deceptive_link, payment_or_data_request, urgency_pressure | — | 2004 |
| phish-0053 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, urgency_pressure | — | 4796 |
| phish-0055 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2025 |
| phish-0057 | phishing | needs_verification | verify | 28 | 3 | deceptive_link, payment_or_data_request | — | 1980 |
| phish-0059 | phishing | needs_verification | verify | 24 | 3 | payment_or_data_request, risky_attachment, urgency_pressure | — | 2499 |
| phish-0061 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1663 |
| phish-0063 | phishing | needs_verification | pay | 16 | 2 | deceptive_link, urgency_pressure | — | 1854 |
| phish-0065 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1780 |
| phish-0067 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1869 |
| phish-0069 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1600 |
| phish-0071 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1810 |
| phish-0073 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 2015 |
| phish-0075 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1563 |
| phish-0077 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 2058 |
| phish-0079 | phishing | needs_verification | pay | 16 | 2 | risky_attachment, urgency_pressure | — | 2078 |
| phish-0081 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1810 |
| phish-0083 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1952 |
| phish-0085 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1816 |
| phish-0087 | phishing | needs_verification | verify | 8 | 1 | payment_or_data_request | — | 1588 |
| phish-0089 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 2311 |
| phish-0091 | phishing | needs_verification | pay | 8 | 1 | authority_impersonation | — | 1941 |
| phish-0093 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1936 |
| phish-0095 | phishing | needs_verification | pay | 8 | 1 | risky_attachment | — | 1787 |
| phish-0097 | phishing | needs_verification | pay | 8 | 1 | deceptive_link | — | 1920 |
| phish-0099 | phishing | insufficient_evidence | verify | 0 | 0 | — | — | 1840 |
