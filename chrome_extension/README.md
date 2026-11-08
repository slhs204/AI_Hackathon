# Dobby’s Catch 0.3.6: private Cloud Run AI demo

## One-window Windows demo

Double-click `Start-Demo.cmd` at the repository root. Keep that one window open; no separate proxy is needed. In **Connect demo backend**, choose **One-click backend · 8081**, check the Tinker permission notice, paste the temporary loopback token from the window and click Connect. The launcher connects to private Cloud Run by default; `-Local` retains the local fallback. Reload the unpacked extension and refresh Gmail after updating. Use synthetic emails only. Normal startup makes no model calls; Analyze/Challenge can incur inference charges. Provider keys and Google identity tokens stay outside the extension. See [startup prerequisites](../scripts/README.md).

The connection selector retains legacy private staging on 8080 with the rules-only guard. Tinker permission is off by default and is stored with the temporary loopback token only in browser-session storage; Disconnect clears it. Reconnecting revokes the previous session even if the new connection fails. Each request validates the selected mode server-side and rechecks the model before sending email. Cloud connector results and connection status say **CLOUD RUN · TINKER**; local Tinker results retain **TINKER AI**. Model failure is an error, never an all-clear. Cloud Run remains private.

## Existing rules-only and offline behavior

Version 0.3.4 waits for both the backend response and the visual scan to finish before showing a result. Fast responses finish the current sweep; slow responses do not start another sweep or add a fresh delay. **Cancel check** clears the pending view and discards its eventual response, but cannot recall a backend request already sent.

The display name is now exactly **Dobby’s Catch**. The cat-and-fish artwork introduced in 0.3.3 remains in the toolbar, extension list and side-panel header. The packaged PNG icons preserve the full artwork at 16, 32, 48 and 128 pixels. The header wraps its controls on narrow panels. Internal message, session-storage and DOM identifiers remain unchanged. Chrome may clear session storage when reloading or updating an extension; reconnect if needed.

The retained offline and legacy staging modes are:

- **Try demo:** local pattern demonstration. No email leaves the browser and no AI runs.
- **Analyze open email with legacy staging selected:** sends the selected Gmail message through the historical local authenticated proxy. The badge says **BACKEND RULES ONLY**. This legacy selection rejects paid-model mode; the current one-click 8081 cloud/local connection requires separate explicit Tinker permission.

Neither mode authenticates a sender or authorizes payment. Missing information stays unknown. Gmail extraction is explicitly partial: last visible expanded message only, no raw authentication headers, Reply-To or attachment content. Messages over 20,000 characters are rejected; more than 50 links are explicitly reported as partial.

## Simple interface

Simple is on by default. After Analyze or Try demo, the shield gives a short result:

- Red: **Don't pay yet** for a stop verdict.
- Amber: **Check first** when warning signs need review.
- Gray: **Can't tell yet** when there is not enough verified information.
- Green: **No warning signs**, only for a complete explicit all-clear response with all four dimensions checked, no findings and no limitations. It never says "OK to pay" or authorizes payment. The current partial Gmail rules-only checks do not establish sender authenticity and should not become green.

**Why?** or unchecking Simple opens the existing evidence, dimensions, challenge and practice view. **Back** returns from details or guidance to Simple; Back from Simple clears the result so you can analyze another message. Message subject and the displayed (not authenticated) sender remain visible in both result views. Switching messages or tabs still clears stale results.

**Call to check**, **Reply: wait** and **Tell IT** open local guidance and optional editable wording. They do not place calls, open links, create mailbox drafts, send email or report anything. Use existing trusted contact information, never details supplied by the suspect email. Local wording is discarded when closed or when the selected message changes. **Mark as reviewed**, when available, is only an ephemeral screen acknowledgment, not sender verification or payment approval.

## Body scan and suspicious-title list

When you choose **Analyze open email**, a pointer-transparent scan line makes one 1.6-second pass over the visible message body while the backend runs concurrently. The line then stops; a static border and the side-panel status remain while waiting for the backend. Results stay hidden until both are ready, and the overlay is removed before the result appears. It is an activity indicator, not proof that every word or attachment was checked. The overlay stays outside the email DOM and is removed after success, failure, navigation, panel closure or a 46-second fallback timeout. Reduced-motion settings disable the moving line and skip the visual wait. If the animation event is suppressed, a 1.9-second fallback explicitly ends the visual; a lost completion acknowledgment fails visibly after 2.5 seconds rather than hanging. Errors and cancellation do not wait for an animation. Changing the email or active tab discards pending results, and the selected message is checked again just before completion. Selecting an exact body-evidence clue highlights it temporarily for eight seconds without rewriting the message.

On the home screen, **Check inbox titles** checks up to the first 100 visible Gmail rows locally. English and Traditional Chinese rules look for time pressure, account/password requests and payment/bank-change wording. Matching subjects receive amber **Check title** marks and appear in the side panel. The title check does not send email content to the backend or read previews, senders or message bodies. It is a narrow keyword check, not a phishing classification, and an unmarked message is not an all-clear.

**Selected email** and the **Suspicious titles** list remain visible above the analysis result. Select a listed title, review its body in Gmail, and choose **Analyze open email** separately. Then select another title and repeat without rerunning the title check. Selecting a title clears the previous body result and cancels any pending display, but does not send a body to the backend. **Connect demo backend** is now at the bottom of the panel; legacy staging remains available; the one-click 8081 cloud/local option is described above.

The list is a captured, local snapshot, not a live inbox or a safety verdict. Opening messages, returning to the inbox, or reordering rows does not erase it. Captured Gmail thread identifiers open only a hash route in the same account. If a row has no supported identifier, it can only be opened while the original captured row is still visible and unchanged; otherwise the panel asks for another title check without discarding the other titles. **Clear marks**, a new title check, switching tabs/accounts, or closing/reloading the panel discards the snapshot. Late responses cannot restore an old list. Titles and optional local guidance are not saved.

While Gmail loads a selected title, extraction rejects the previous body. Readiness prefers Gmail-owned thread metadata, and otherwise requires a newly loaded body/message identity or the exact previously resolved target view; heading-only and text-only changes are not enough. The fallback is still a DOM heuristic, not an authoritative Gmail API identity check. Unsupported or changing Gmail markup can require refreshing Gmail and checking titles again. Actual-account browser acceptance remains required.

To update an existing unpacked installation, replace the files in the same existing extension folder, reload the extension at `chrome://extensions` (it may still show the old Hookline name until reloaded), then refresh Gmail. Confirm the name is **Dobby’s Catch**, the cat icon appears, and the version is **0.3.6**. Do not remove and reinstall it just to update the branding. Reconnect the temporary loopback token if the session was cleared. Version 0.3.6 identifies Cloud Run execution through the one-click connector while retaining the local fallback, explicit Tinker permission and existing host permissions. This version still targets Gmail DOM selectors; Outlook or other email clients are not implemented.

## Optional legacy rules-only connection

The following manual proxy instructions apply only to the optional 8080 rules-only selection. For the default one-window Cloud Run AI connection, follow the opening section instead. Use the `rules-only` tag, never the service's base URL, so promoting AI cannot silently change this legacy connection. The rules-only tag is retained and the independently reviewed AI revision serves 100% base-service traffic; see [deployment status](../docs/PRIVATE_STAGING.md).

1. Confirm the `rules-only` tag points to the retained mock revision `phish-staging-fix-313b174`, with Cloud Run IAM authentication enabled. Do not redeploy the base service as mock to use this optional connection. If the tag is unavailable, stop rather than falling back to the base service.
2. On the **same computer as Chrome**, use an already signed-in Google Cloud CLI account with existing invoker permission. Start:

   ```bash
   gcloud run services proxy phish-staging --project=lateral-nomad-514001-c7 --region=us-central1 --tag=rules-only --port=8080
   ```

   Cloud Shell is a different computer: its localhost is not your laptop's localhost. Leave the local proxy running. Do not change IAM, expose the service publicly, or copy Google identity tokens into the extension. If Google Cloud CLI is not installed or the account lacks access, stop and resolve that setup separately.
3. Load this `chrome_extension` folder in `chrome://extensions` using **Load unpacked**, or reload the existing installation. The only backend host permission is `http://127.0.0.1/*`; legacy staging fixes port 8080 and the one-click cloud/local connection fixes port 8081; both reject redirects. Refresh Gmail after reloading.
4. The remaining legacy 8080 steps are historical compatibility information, not the current demo setup. Use the one-window 8081 flow above. Never paste the cloud app token into the extension; the current flow accepts only the launcher’s temporary loopback token.

## Verification

```bash
node --test chrome_extension/tests/*.test.cjs
node --check chrome_extension/background.js
node --check chrome_extension/content.js
node --check chrome_extension/sidepanel.js
node --check chrome_extension/inbox-panel.js
```

Automated tests cover branding, PNG icon dimensions, transport, token and mode guards, original-finding challenges, failure handling, interrupted/late results, limitations, extraction, finite body-scan completion, fast/slow backend responses, reduced motion, cancellation/retry, lost animation events/acknowledgments, late results, retained title selection, rapid A→B→A switching, heading-only loading guards, account/tab invalidation and stale-response suppression. They use API/Chrome/DOM stubs, **not real Chrome/Gmail E2E**.

Current verification: 238 backend tests passed with 1 skipped. Passing evidence for the unchanged 99 extension tests and Windows PowerShell 5.1 launcher checks is reused. Real Chrome with version 0.3.6 passed synthetic T23 Analyze and Challenge through the cloud connector, flagged partial extraction, and blocked analysis after AI consent was revoked. This covers those specific browser paths; the broader checklist below is not claimed complete.

Broader manual acceptance checklist (proxy/rules-only items apply only to legacy staging):

- Local demo works offline and is labeled LOCAL DEMO.
- Wrong app token is rejected; valid token connects through IAM proxy.
- Synthetic Gmail Analyze shows BACKEND RULES ONLY and missing-information notes.
- Exact body quote highlights correctly; metadata/link-only evidence is not fabricated as body text.
- Full-finding challenge retains unresolved procedure and never clears a finding.
- Switching messages/tabs while extracting or analyzing clears stale results and leaves controls usable.
- Disconnect clears the token; Gmail analysis then fails until reconnecting.
- Stop the proxy: request fails visibly, not as a clean assessment.
- Check titles in a synthetic inbox: only matching visible subjects are marked and listed, and no backend request occurs. Repeat the check, clear marks, change tabs and change the inbox list; old results must not reopen the wrong message.
- Open a listed message, then Analyze separately. Confirm the title list remains below Selected email on the result screen. Select a second title and analyze it, then return to the first; repeat rapidly and while a check is pending. The old result must disappear, and no old body may be sent during loading. Confirm Connect demo backend is last in the panel. With a fast backend, the one-pass animation must finish and disappear before the result appears. With a slow backend, it must stop after one pass while the text status keeps waiting; backend completion must not restart a delay.
- Enable reduced motion: no sweep and no artificial visual wait. Cancel during the sweep, retry, switch messages/tabs, disconnect, and close the panel: no late result or leftover overlay should appear. Errors must appear promptly and re-enable controls.
- The scan remains pointer-transparent and only indicates activity, never scan coverage or an all-clear.

Gmail DOM selectors are unstable and require actual-browser validation. Sender matching and a low risk score are not proof of authenticity. Do not test with sensitive real inbox data in public demos.


P1 Qwen-assisted evaluation is complete: the frozen test run warned on 49/50 phishing-labelled and 2/50 legitimate-labelled public inputs. All 100 analyses remained incomplete under Gmail extraction limits. Known routine-content errors were repaired on development cases; remaining errors and historical test exposure are disclosed in the [evaluation report](../docs/QWEN_EVALUATION.md). The [P0 acceptance record](../docs/P0_ACCEPTANCE.md) remains historical integration evidence.


The cloud app token is used only by the connector and is never pasted into the extension. Paste only the temporary loopback token displayed by the launcher.
