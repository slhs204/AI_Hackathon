# Hookline v0.2.0 — interactive fishing-hook update

## What's new

- Real illustrated fishing hook with **animated, clickable numbered clue/bait tokens**.
- Click any token to see its exact quoted evidence, **why it matters**, and **how to verify**.
- Clicking a token (or a finding card) still calls the proven Gmail exact-text highlighter.
- The selected token and its corresponding finding card are visually linked.
- The Challenge form now targets the **selected finding** (or the first if none was selected).
- Respects **reduced-motion** settings and provides keyboard-accessible buttons.
- No changes to the Gmail content extraction, backend request/response contract, permissions, or mock rule logic.

## Update your Chrome extension

1. Extract this ZIP into a **new folder** (keep the `hookline-extension` folder intact).
2. Go to `chrome://extensions`.
3. If you previously installed Hookline from a different folder, **Remove** the old copy, then choose **Load unpacked** and select this new `hookline-extension` folder. If you're updating files in the original loaded folder instead, **Reload** that extension.
4. Refresh the Gmail tab. Open your synthetic phishing test email.
5. Open Hookline, click **Analyze open email**, and scroll down to **The fishing hook**. Three numbered clue tokens should appear.
6. Click the **Payment details change** token: the text `change my salary account today` should highlight yellow in Gmail. Try **Time pressure** and **Sensitive credential reference** too.
7. Click another clue. Its selected state and evidence explanation should change, and the Gmail highlight should move.
8. **Try demo** shows the interactive graphic without looking at any real email. Demo tokens cannot highlight Gmail.

**How to change things:** UI markup in `sidepanel.html`, styles/animations in `sidepanel.css`, token behavior in `sidepanel.js` (`renderBait()`, `selectFinding()`). The mock analyzer remains in `background.js` and is clearly not AI.

**Security reminder:** A token is a warning sign, not a likelihood or guarantee of phishing. Quoted evidence must exist exactly in the extracted message. Avoid public demos with private emails.

---

# Hookline extension starter — FIXED v0.1.1

**Fix for "Open Gmail in the active tab" error:** Gmail-specific `host_permissions` added to `manifest.json`; the side panel no longer assumes `tab.url` is available. Failed extraction now clears stale mock results.

**Install the fixed version:** Extract this ZIP, open `chrome://extensions`, **Remove** the old Hookline extension if it was loaded from another folder (or point it to this new extracted folder), then click **Load unpacked** and select the inner `hookline-extension` folder (it contains `manifest.json`). Refresh the Gmail tab and open an email. Click **Analyze open email**. No API key needed for mock mode.

# Hookline — Member 2 Chrome extension starter

**A load-unpacked Chrome Manifest V3 extension. No npm, React, build step, or API key needed.**

## First run (5 steps)

1. Unzip the project to a folder on your computer.
2. Visit `chrome://extensions` in Chrome.
3. Enable **Developer mode** (upper right).
4. Click **Load unpacked**, then select the folder containing `manifest.json`.
5. Pin **Hookline** (puzzle icon in the Chrome toolbar) and click it. The side panel opens. Click **Try demo** to verify the UI.

To test real Gmail extraction, open `https://mail.google.com`, click a message, then click **Analyze open email**. The mock analyzer uses simple patterns to find a payroll-change request, urgency, or password/code references. Click a warning card to highlight its exact text in Gmail.

**Important:** If Gmail was already open when you installed/reloaded the extension, refresh the Gmail tab to inject `content.js`.

## What each file does

- `manifest.json`: Chrome extension metadata, Gmail content-script access, and side-panel permission.
- `content.js`: reads the currently expanded Gmail message, gives the body `b1`, extracts links, highlights matching quotes, and clears stale evidence on email changes.
- `sidepanel.html`, `sidepanel.css`, `sidepanel.js`: user experience, evidence cards, fishing hook, demo and challenge UI, one-question practice.
- `background.js`: routes `/analyze` and `/challenge`; currently returns mock analysis. API key is **never** stored in the extension.
- `fixtures/demo-email.json`: agreed-upon sample payload.

## Backend integration with Albert and Sunday

1. Freeze the request payload and finding response contract first:

   Request: `POST /analyze` with `{ email_id, sender:{name,address}, subject, blocks:[{id,text}], links:[{id,text,url}] }`.

   Response: `{ email_id, findings:[{id, category, title, evidence:{block_id,quote}, explanation, next_action}], summary }`.

   Challenge request expected by this starter: `{ email, finding_id, context }` to `POST /challenge`.

   Challenge response: `{ explanation, next_action }`.

2. In `background.js`, set `MOCK_MODE = false` and set `API_BASE_URL` to the Cloud Run HTTPS base URL.
3. In `manifest.json`, add an **exact host permission** for the deployed backend (e.g. `"host_permissions": ["https://your-real-service.a.run.app/*"]`). Avoid broad `https://*/*` permissions.
4. Reload your unpacked extension on `chrome://extensions` and refresh the Gmail tab.
5. Check the service worker's Inspect link in `chrome://extensions` and Chrome DevTools for errors.
6. Verify that Sunday returns *actual substrings* from the specified block and that the backend validates those quotes before sending them.

If the backend returns a different response schema, coordinate one small normalization function rather than changing the UI and extraction code everywhere.

## Demo test checklist

- [ ] Chrome icon opens side panel.
- [ ] Try demo produces two warning signs (payment change and urgency).
- [ ] Gmail message extraction captures subject, sender, body, and links.
- [ ] Warning card highlights the exact phrase, never guessed text.
- [ ] If evidence does not match, no fabricated highlight is shown.
- [ ] Opening another email clears old results and evidence.
- [ ] Switching tabs clears stale results.
- [ ] Challenge input works (in mock mode the reply is explicitly labeled as such).
- [ ] Practice question works with mouse and keyboard.
- [ ] UI remains usable at narrow side-panel widths.
- [ ] No private email content is transmitted until user clicks Analyze.

## Known limits / production cautions

- This uses Gmail DOM selectors (`.a3s`, `.gD[email]`, `h2.hP`), which are not stable APIs; test on your Gmail UI. It extracts the *last visible expanded message* in a thread, not a full Gmail conversation.
- Quote highlighting is exact substring-based. Quotes containing browser-normalized whitespace or embedded formatting may not visually map to DOM text; in that case, a warning is shown rather than a made-up highlight.
- The mock analyzer is **not an AI classifier or a security guarantee**. It deliberately only demonstrates the interface and evidence workflow.
- Do not run this against sensitive real inboxes during a public demo. Use synthetic messages and avoid logging full email bodies in the backend.
- A matching domain is not proof of safety; a mismatch is not proof of phishing.
- If Cloud Run is access-restricted, coordinate browser authentication and access control with Albert; adding a URL is not sufficient.
