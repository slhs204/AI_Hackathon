# Independent review: P2 rotation, title check, and demo script (read-only)

**Scope.** I reviewed only the supplied source. These files were not supplied, so every claim that depends on them is **unproved**:
- `sidepanel.js`, `sidepanel.css`, `background.js`
- the connector and backend
- the extension tests
- `scripts/README.md`, the root `README.md`, `PROJECT_SPEC.md`
- the T23/T06 fixtures

This is a defect report, not an endorsement.

## Actionable defects

### High

1. **A live demo would put real subject lines on screen (T-INV1, T-AC4).**
   - The title check lists every rendered row, up to 100. It shows them in the panel and marks them in Gmail (`content.js` `precheckInbox`, `inbox-panel.js` `render`).
   - The script's prep only says "確認合成郵件位於同一個可見清單" ("confirm the synthetic emails are in the same visible list"). It never requires that the inbox contain *only* synthetic mail.
   - On a normal account, real subjects would be shown on the projector.
   - **Fix:** add a prep step requiring a dedicated demo Gmail account (or inbox) holding only synthetic messages. Also recommend a dry run of Check inbox titles before going on stage.

2. **A title with no subject can be selected but can never be analyzed (T-AC1, T-INV3).**
   - `awaitingInboxMessage` requires `view.subject === pending.subject`.
   - For an empty row subject, `pending.subject` is `""`. Gmail's `h2.hP` typically shows "(no subject)", so the match never succeeds.
   - Because `inboxNavigation` has no timeout, `extractEmail` keeps throwing "still opening" until the user navigates elsewhere.
   - Any normalization difference between the row text and the heading text causes the same stall. It fails closed, but it would block the demo.
   - The thread ID used for matching comes from `body.closest("[data-legacy-thread-id], [data-thread-id]")`. Gmail may not put that attribute on an ancestor of the body, so the weaker fallback heuristics are probably what actually runs. This is unverified.
   - **Fix:**
     - Skip the subject-equality check when the captured subject is empty, and rely on thread ID or a replaced body instead.
     - If a row has neither a subject nor a thread ID, refuse navigation rather than leaving the panel stuck.
     - Verify `messageView().threadId` in real Gmail.

### Medium

3. **Gmail marks can end up beside the wrong message (T-INV3).**
   - Once the snapshot is ready, nothing re-checks the "⚠ Check title" marks against their rows.
   - If Gmail reuses or re-renders a `tr.zA` in place (for example, when new mail arrives), a mark can sit next to a different subject.
   - The panel list is safe because it is keyed by thread ID; the in-page marks are not.
   - **Fix:** in the existing debounced observer, remove a mark when its row is detached or when `rowSubject(row) !== item.subject`.

4. **Closing the panel may leave marks behind in Gmail.**
   - On `pagehide`, `reset()` sends a fire-and-forget `CLEAR_INBOX_MARKS`, which may never be delivered.
   - The content script has no way to tell that the panel is gone, so marks can stay in Gmail.
   - The README claim "closing/reloading the panel discards the snapshot" holds for the panel only.
   - **Fix:** either clear marks when a `chrome.tabs.connect` port disconnects, or narrow the README wording.

5. **The script makes claims the supplied evidence does not support (T-INV4).**
   - **"這封信甚至要求 AI 忽略指令、回報沒有警告"** ("this email even tells the AI to ignore its instructions and report no warnings"). The T23 content and the result showing the bank warning was kept are not supplied. The prior T23 pass only proves that Analyze and Challenge worked.
   - **"取得第二人核准"** ("get a second person's approval"). The UI guidance text is in `sidepanel.js`, which was not supplied.
   - **Gmail highlight on the T23 bank-change clue.** No host proof covers this.
   - **Fix:** attach fixture or browser evidence for each claim, or rephrase it conditionally.

6. **The spoken benchmark explanation leaves out the payroll mismatch (T-INV4).**
   - The pitch targets payroll and finance staff.
   - The dataset has essentially no payroll examples, and all 100 analyses were incomplete. That appears only in the unspoken "說明範圍" section.
   - **Fix:** add one spoken clause, e.g. "資料集以帳密與惡意附件為主，幾乎沒有薪資案例" ("the dataset is mostly credential and malicious-attachment cases, with almost no payroll examples").

7. **The real-Chrome check of 0.3.7 is pending, but the script does not say so (T-AC3).**
   - The script presents the 0.3.7 flow as settled. The README only says acceptance is "required".
   - **Fix:** state explicitly that the 0.3.7 title flow has not been verified in real Chrome until it has been.
   - Also add a presenter cue: by my reading of `subjectSignals`, "Updated remittance details" matches none of the rules. T23 should therefore show "No local title clue". The spoken line "即使標題沒有警告" ("even if the title has no warning") fits this; make it the explicit expectation.

8. **`PRIVATE_STAGING.md` has a stale test count.** Its "Current AI verification status" section cites "the unchanged 99 extension tests". That contradicts the 106 tests and the changed 0.3.7 extension. Relabel it as historical or update it.

9. **No public cost-method record (AC3, INV4).**
   - No supplied public file describes the cost inspection. The amounts belong in private output, but the following can be stated publicly without figures:
     - which sources were read
     - the time window and the delayed cutoff
     - that P1's later calls are excluded
     - that gross, credits and net are reported separately
     - that the balance is unknown
     - the reporting lag and the unknown final invoice
     - that the Tinker browser UI was blocked by URL policy and not bypassed
   - From the source alone, this remains **unproved**.

### Low

10. **No panel-side timeout on `FINISH_INBOX_SCAN`.** The body scan has a 2.5 s acknowledgment bound (claimed). The content script always settles within about 1.9 s, so the risk is small, but this lacks parity with the body scan under T-AC2's lost-event controls.
11. **"Completed" usually means the fallback timer fired, not that every animation ended.** Overlays for off-screen rows are `hidden`, so they never fire `animationend`. This is acceptable as presentation, but the README's "sweep runs over the subject rectangles" overstates it.
12. **Gmail's reading-pane (split) view is refused** by the check that runs when a message body is visible. This limitation is not disclosed.
13. **Result may be pushed off-screen.** Up to 100 list buttons sit above the result. Whether CSS bounds the list or JS scrolls or focuses the result is unproved.
14. **The rehearsal step incurs cost.** "先確認點選線索與 Reconsider 可用" ("first confirm clue selection and Reconsider work") makes paid calls. The script should say so.

## Status by requirement

| Item | Status from supplied source |
|---|---|
| INV1 | Launcher passes the cloud token through env, not argv. The loopback token is printed to the console by design. No token values appear in docs. Logs and bundles are unproved. |
| INV2 / INV3 | Docs agree with host proof. Atomicity, IAM and 404 results are host-only and not verifiable here. |
| INV4 / AC3 | Missing a public, amount-free record (see 9). |
| AC1 | Reads `latest`. The test asserts `latest` plus `phish-demo-token`. The PS5.1 production run is host proof only. |
| AC2 | Docs are consistent. |
| AC4 | The bundle omits `sidepanel.js`, the tests and the connector, so matching-bundle completeness is unproved. Untracked `.agentflow/.tmp` artifacts are present; cleanup is unverified. |
| T-INV1 | Holds in `content.js` (reads `span.bog` and row ID attributes only, no backend). Fails for demo privacy (see 1). Whether `sidepanel.js` keeps the `hookline:inbox-opening` subject local is unproved. |
| T-INV2 | Holds: no marks or results appear until the matched, finite sweep ends and `inboxUnchanged` passes. |
| T-INV3 | Defects 2 and 3. That `sidepanel.js` performs no auto-Analyze on opening is unproved. |
| T-INV4 / T-AC4 | Length is roughly 2:30–2:45. No own-training claim is made. Defects 5–7 remain. |
| T-AC1 | Every checked row is listed, unflagged ones included. The empty-subject case fails (see 2). |
| T-AC2 | Reduced-motion and stale-response handling look sound. The title flow has no lost-ack bound (see 10). |
| T-AC3 | Pending. Disclosure is insufficient (see 7). |

## Simplicity

- **Clean:** no new dependencies, permissions, backend routes or proxy. The body-scan CSS and message transport are reused.
- **Minor nits:**
  - The check-click handler calls `eraseMarks(previous)` twice: once via `reset()` and once directly.
  - `precheckInbox` duplicates the body-scan positioning logic instead of sharing a helper.

