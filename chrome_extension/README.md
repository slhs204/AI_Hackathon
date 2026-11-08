# Hookline 0.3.2: Simple interface, body scan and local subject list

This unpacked Chrome extension has two distinct modes:

- **Try demo:** local pattern demonstration. No email leaves the browser and no AI runs.
- **Analyze open email:** sends the selected Gmail message to the private staging backend through a local authenticated proxy. The badge says **BACKEND RULES ONLY**. This build rejects paid-model mode.

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

When you choose **Analyze open email**, a pointer-transparent scan line moves over the visible message body while the check is pending. It is an activity indicator, not proof that every word or attachment was checked. The overlay stays outside the email DOM and is removed after success, failure, navigation, panel closure or a 46-second fallback timeout. Reduced-motion settings disable the moving line. Selecting an exact body-evidence clue highlights it temporarily for eight seconds without rewriting the message.

On the home screen, **Check inbox titles** checks up to the first 100 visible Gmail rows locally. English and Traditional Chinese rules look for time pressure, account/password requests and payment/bank-change wording. Matching subjects receive amber **Check title** marks and appear in the side panel. The title check does not send email content to the backend or read previews, senders or message bodies. It is a narrow keyword check, not a phishing classification, and an unmarked message is not an all-clear.

Select a listed subject to open that captured Gmail row. Body analysis is still a separate **Analyze open email** action. **Clear marks**, changing tabs, navigating, or changing the list clears the results. Stale rows are checked before opening, and late responses cannot restore an old list. Titles and optional local guidance are not saved.

To update an existing unpacked installation, replace the extension files, reload Hookline at `chrome://extensions`, and refresh Gmail. Reconnect the staging demo token if the session was cleared. Version 0.3.2 does not change backend transport, host permissions or rules-only safeguards. An already-working PR #5 staging backend does not need to be redeployed for this UI update. This version still targets Gmail DOM selectors; Outlook or other email clients are not implemented.

## Connect securely

1. For initial setup, update the private staging backend to the compatible PR #5 backend using [the staging guide](../docs/PRIVATE_STAGING.md). Keep Cloud Run IAM authentication enabled and MODEL_PROVIDER=mock.
2. On the **same computer as Chrome**, use an already signed-in Google Cloud CLI account with existing invoker permission. Start:

   ```bash
   gcloud run services proxy phish-staging --project=lateral-nomad-514001-c7 --region=us-central1 --port=8080
   ```

   Cloud Shell is a different computer: its localhost is not your laptop's localhost. Leave the local proxy running. Do not change IAM, expose the service publicly, or copy Google identity tokens into the extension. If Google Cloud CLI is not installed or the account lacks access, stop and resolve that setup separately.
3. Load this `chrome_extension` folder in `chrome://extensions` using **Load unpacked**, or reload the existing installation. The only backend host permission is `http://127.0.0.1/*`; the code fixes its destination to port 8080 and rejects redirects. Refresh Gmail after reloading.
4. Open **Connect to private staging**. Enter the existing staging **demo token** directly into the password field and click Connect. Never put it in source code, chat, screenshots or Git. It is kept only in `chrome.storage.session`, not sync/local storage, and cleared on Disconnect or browser-session end. This is demo access control, not production authentication. If Chrome prompts for local-network access, review and allow it yourself only for this intended connection.
5. Connection checks `/session`, validating both the app token and rules-only mode before any email is sent. An invalid token fails here. No provider key, service-account key or Cloud Run identity token is used by the extension.
6. Open a **synthetic** Gmail message and click Analyze. The extension sends `X-Demo-Token` and `X-Require-Rules-Only: 1`; the backend refuses non-mock providers before calling a model. Challenge sends the original full finding and displays unresolved checks. A less-concerning response is never clearance.

The proxy uses the local user's existing Google credentials to reach IAM-private Cloud Run. The app token is a separate second gate. A Cloud Run URL plus the app token alone is insufficient. Official references: [authenticate developers](https://docs.cloud.google.com/run/docs/authenticating/developers), [gcloud proxy](https://docs.cloud.google.com/sdk/gcloud/reference/run/services/proxy).

## Verification

```bash
node --test chrome_extension/tests/*.test.cjs
node --check chrome_extension/background.js
node --check chrome_extension/content.js
node --check chrome_extension/sidepanel.js
node --check chrome_extension/inbox-panel.js
```

Automated tests cover transport, token and mode guards, original-finding challenges, failure handling, interrupted/late results, limitations, extraction, body-scan lifecycle and subject-list invalidation. They use API/Chrome/DOM stubs, **not real Chrome/Gmail E2E**.

Manual acceptance checklist, still required:

- Local demo works offline and is labeled LOCAL DEMO.
- Wrong app token is rejected; valid token connects through IAM proxy.
- Synthetic Gmail Analyze shows BACKEND RULES ONLY and missing-information notes.
- Exact body quote highlights correctly; metadata/link-only evidence is not fabricated as body text.
- Full-finding challenge retains unresolved procedure and never clears a finding.
- Switching messages/tabs while extracting or analyzing clears stale results and leaves controls usable.
- Disconnect clears the token; Gmail analysis then fails until reconnecting.
- Stop the proxy: request fails visibly, not as a clean assessment.
- Check titles in a synthetic inbox: only matching visible subjects are marked and listed, and no backend request occurs. Repeat the check, clear marks, change tabs and change the inbox list; old results must not reopen the wrong message.
- Open a listed message, then Analyze separately: the body scan ends on result, error or navigation, does not capture clicks, and honors reduced motion.

Gmail DOM selectors are unstable and require actual-browser validation. Sender matching and a low risk score are not proof of authenticity. Do not test with sensitive real inbox data in public demos.
