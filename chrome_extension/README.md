# Hookline 0.3: private rules-only staging

This unpacked Chrome extension has two distinct modes:

- **Try demo:** local pattern demonstration. No email leaves the browser and no AI runs.
- **Analyze open email:** sends the selected Gmail message to the private staging backend through a local authenticated proxy. The badge says **BACKEND RULES ONLY**. This build rejects paid-model mode.

Neither mode authenticates a sender or authorizes payment. Missing information stays unknown. Gmail extraction is explicitly partial: last visible expanded message only, no raw authentication headers, Reply-To or attachment content. Messages over 20,000 characters are rejected; more than 50 links are explicitly reported as partial.

## Connect securely

1. Update the private staging backend to this same commit using [the staging guide](../docs/PRIVATE_STAGING.md). Keep Cloud Run IAM authentication enabled and MODEL_PROVIDER=mock.
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
```

Automated tests cover transport, token and mode guards, original-finding challenges, failure handling, interrupted/late results, limitations and extraction. They use API/Chrome/DOM stubs, **not real Chrome/Gmail E2E**.

Manual acceptance checklist, still required:

- Local demo works offline and is labeled LOCAL DEMO.
- Wrong app token is rejected; valid token connects through IAM proxy.
- Synthetic Gmail Analyze shows BACKEND RULES ONLY and missing-information notes.
- Exact body quote highlights correctly; metadata/link-only evidence is not fabricated as body text.
- Full-finding challenge retains unresolved procedure and never clears a finding.
- Switching messages/tabs while extracting or analyzing clears stale results and leaves controls usable.
- Disconnect clears the token; Gmail analysis then fails until reconnecting.
- Stop the proxy: request fails visibly, not as a clean assessment.

Gmail DOM selectors are unstable and require actual-browser validation. Sender matching and a low risk score are not proof of authenticity. Do not test with sensitive real inbox data in public demos.
