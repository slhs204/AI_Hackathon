# Post-demo operations

The launcher connects a local browser session to the private cloud service. Its temporary loopback token changes every launch; the separate cloud app token stays in the connector and is pinned by each cloud revision.

P2 rotated the cloud app token to Secret Manager numeric version `2` and disabled version `1`. The launcher reads `latest`, currently `2`. The AI revision `phish-staging-p2-ai-b3b3e19-a005` serves 100% traffic through the base service and `p1-ai` tag. The `rules-only` tag identifies `phish-staging-p2-rules-b3b3e19-a005`, a mock backup with no Tinker key and 0% base traffic. Obsolete P0/A002 tags are removed.

1. Stop any running connector with Ctrl+C. It may still cache the revoked cloud token.
2. Double-click `Start-Demo.cmd` and keep its window open. Existing authorized Google Cloud sign-in and secret access are required.
3. Disconnect the extension, choose the one-click 8081 connection, explicitly enable Tinker, and paste only the newly displayed temporary loopback token. Never paste the cloud app token or Google credentials.
4. Expect a successful cloud Tinker session. Restarting the launcher does not run inference; Analyze and Challenge can incur charges.

Stock Windows PowerShell 5.1 launcher verification returned session 200 after rotation, without inference. Cloud checks returned new token 200, old token 401 and anonymous 403. The P1 image, IAM and resources were unchanged; the frozen P1 evaluation and earlier paid-canary observations remain historical. Rotation did not run a new paid analysis or challenge.

For the optional rules-only connection, use its tagged route and the existing [legacy connection instructions](../chrome_extension/README.md#optional-legacy-rules-only-connection), never the AI base URL. Historical rollback revisions bound to disabled version `1` must be rebound to numeric version `2` before use; do not restore an obsolete revision as-is. Keep private IAM authentication and the existing model guard. The separate `-Local` sampler fallback still has its recorded expiry and is not renewed by token rotation.


Cost inspection used the read-only Tinker organization usage/storage API and the authenticated Google Cloud Billing project report, with currency verified separately. The requested API window was November7–9UTC; observed usage ended November8 08:00UTC and excludes later P1 evaluation calls. Tinker values are organization-wide gross estimates, not project attribution or an invoice. The Google project report used November7–8Pacific dates and separated usage, credits and net. Current-day reporting may lag; the final invoice and Tinker balance remain unknown. A Windows URL-verification policy blocked the Tinker billing-console check, which was stopped without bypassing it. Financial figures are retained only in the private local cost report.
