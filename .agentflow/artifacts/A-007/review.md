# Review: 0.3.8 flagged-only title list

**Verdict: the patch is functionally correct and minimal.** I found no blocking code defect. One demo-flow risk is material and should be fixed or verified before you rely on the script. The remaining items are small hardening and documentation fixes.

## What the patch gets right

- **Flagged only after acknowledgment:** `render()` still runs only after `FINISH_INBOX_SCAN` returns `completed` with the same `snapshot_id`. It now iterates `result.flagged`.
- **Guards unchanged:** the stale-revision, tab-change, timeout and mismatch guards are untouched, and so are the mark-clearing paths. `Array.isArray(response.flagged)` was already being checked.
- **Empty case:** with no flags, the list is empty and the status reads "0 titles flagged among N visible rows… Subjects only, not a safety determination." Nothing says "safe" or "clear."
- **Local only:** there are no backend, provider or permission changes, and nothing sends data automatically.
- **Version:** the manifest and the branding test both say 0.3.8.

## Material issue

**1. The demo script's direct Gmail open of T23 may clear the flagged list.** The script now has the presenter click T23 directly in Gmail. That path does not go through `OPEN_INBOX_ROW`.

- If the content script sends `INBOX_CHANGED` on Gmail navigation, the listener at the end of `inbox-panel.js` resets the panel. The flagged list and marks disappear, and the status reads "The Gmail view changed…".
- That contradicts the README sentence "Then select another title and repeat without rerunning the title check."
- It may also break later demo segments that pick a flagged title from the list.

Whether this happens depends on content-script logic that wasn't supplied, and real Chrome hasn't been verified, so treat it as a likely risk. Fix it one of two ways:
- Reorder the script so the flagged titles are used from the list first and T23 is opened from Gmail last, with a rerun of Check inbox titles afterwards if needed.
- Or confirm that a direct open does not reset the list, and record that as unverified until it has been checked in real Chrome.

## Minor issues

2. **Hidden assumption that every flagged item has signals.** `render` assumes every `flagged` item has a non-empty `signals` array. An empty or missing array would show a bare "⚠ " or throw. A cheap guard is `item.signals?.length ? … : "Subject-only warning clue"`. This is optional if the content script guarantees the invariant.
3. **The first regression test can pass vacuously.** The `every(...)` check holds even if nothing renders. Add `assert.ok(result.flagged.length > 0)` or assert the expected row ids.
4. **The empty-case test could pin more of the contract.** It could also assert that `inbox-clear` is visible and that the status contains no wording like "safe" or "clear". Use a word-boundary regex so "safety" still matches.
5. **The status line doesn't mention Gmail.** The README says unlisted messages remain available directly in Gmail, but the status line doesn't. Consider appending "Unlisted messages can still be opened in Gmail; their bodies were not checked."
6. **README wording:**
   - The appended 0.3.8 note sits after the P2 operations section, far from the title-check docs. It also refers to "historical 0.3.7 all-title browser observations above," and I couldn't find any such observations in the visible context. Move it next to the title-check paragraph, or point to where the proof is recorded.
   - "Version 0.3.8 keeps the finite title sweep … and identifies Cloud Run execution…" reads as if Cloud Run identification is new in 0.3.8. Consider "continues to identify."
7. **Possible leftover all-title wording.** Search for stale strings outside this diff: `No local title clue`, `Body not checked`, `all checked titles`, `all-title`, `所有標題`, `從清單選`. Check the rest of `DEMO_SCRIPT_ZH_TW.md`, the docs and the fixtures.

## Before the GitHub update

- **Commit first.** The patch is uncommitted, and the worktree is on a **detached HEAD**. A fast-forward-only push needs an explicit refspec such as `git push origin HEAD:main`, with no force. Confirm `origin/main` is still an ancestor right before pushing.
- **Check the agentflow files.** `.agentflow/artifacts/A-007/` (untracked) and the modified `.agentflow/…devlog.md` must be checked for private email content, tokens, loopback or app tokens, and account identifiers before they go into the commit. If they can't be cleared, leave them out of the commit.
- **Keep the commit message limited to what's proven.** It should not claim real-Chrome verification of the filter or full 20-mail E2E completion. The current state is 3 of 20 UI completions, with 17 untested and R17 reserved but not analyzed.


## Host disposition

No blocking code defect. Direct Gmail navigation is documented as invalidating the snapshot; the demo continues with the open T23 and does not depend on the old list. The producer guarantees nonempty signals through items.filter(item => item.signals.length). The regression asserts list length equals the nonempty fixture length, so it cannot pass with an empty list. No extra fallback, status text or behavior was added. Current extension count corrected to 111. New 0.3.8 Chrome behavior remains unverified.
