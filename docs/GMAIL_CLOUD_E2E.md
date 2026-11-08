# Gmail / Cloud Run replay progress

This is a partial technical end-to-end check, not a new accuracy benchmark.

Twenty sanitized copies of the previously frozen public-source messages were sent once to the owner-authorized test account. All twenty were observed delivered: five in Inbox and fifteen in Spam. Original sender authentication, recipient headers and attachments were not reproduced. Subjects were prefixed; three display-link mappings were omitted. These transformations prevent direct accuracy comparison with the earlier local test.

Three messages (R20, R19 and R18) completed explicit Gmail extension analysis through Cloud Run and Tinker. All three returned partial assessments; their warning counts were two, one and two. Cloud Run recorded three successful POST /analyze requests at 13:18:34Z, 13:21:48Z and 13:24:35Z on 2026-11-08. The extension discarded one unsupported AI quote per result.

Seventeen messages remain untested. R17 has an attempt reservation but was never analyzed: Gmail navigation failed its heading check before Analyze. Do not resend delivered copies or repeat the three completed paid calls.

Desktop testing was paused because the tool's Chrome accessibility tree and screenshot showed different foreground applications. The owner then prioritized GitHub publication and a flagged-only title list. Version 0.3.8 implements that filter and passes 111 extension tests; its real-Chrome behavior has not yet been checked. Backend checks: 238 passed, one skipped. No new backend deployment or inference was needed for this filter.

Reload the existing unpacked extension and refresh Gmail to activate 0.3.8. This can clear the connection; reconnect using the launcher's temporary token. A title absent from the suspicious list has not had its body checked and is not declared safe.
