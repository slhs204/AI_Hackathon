// Gmail is a single-page app. These selectors are practical hackathon heuristics,
// NOT a supported Gmail API. Test against your actual Gmail account before demoing.
(() => {
  const HIGHLIGHT_NAME = "hookline-evidence";
  const STYLE_ID = "hookline-highlight-style";
  let lastEmailId = null;
  let checkTimer;
  let fallbackRange = null;
  let highlightTimer;
  let scan = null;
  let inboxSnapshot = null;
  let inboxRevision = 0;
  const ROW_LIMIT = 100;
  const BODY_SWEEP_MS = 1600;
  const BODY_SWEEP_FALLBACK_MS = BODY_SWEEP_MS + 300;
  const ATTENTION_STYLE_ID = "hookline-attention-style";

  function ensureAttentionStyle() {
    if (document.getElementById(ATTENTION_STYLE_ID)) return;
    const style = document.createElement("style");
    style.id = ATTENTION_STYLE_ID;
    style.textContent = `
      .hookline-body-scan { position:fixed; z-index:2147483645; pointer-events:none; overflow:hidden; border:1px solid #1a73e866; border-radius:4px; box-sizing:border-box; }
      .hookline-body-scan-line { position:absolute; left:0; right:0; height:55px; top:-55px; border-bottom:2px solid #1a73e8; background:linear-gradient(180deg,transparent,#1a73e830); animation:hookline-body-sweep ${BODY_SWEEP_MS}ms linear 1 forwards; }
      @keyframes hookline-body-sweep { from { transform:translateY(0); } to { transform:translateY(var(--hookline-scan-height)); } }
      .hookline-title-flag { display:inline-block; margin-left:6px; padding:1px 5px; border:1px solid #b75e0a; border-radius:8px; color:#7a3d00; background:#fff4d5; font:11px/1.5 sans-serif; vertical-align:middle; }
      @media (prefers-reduced-motion:reduce) { .hookline-body-scan-line { animation:none; display:none; } }
    `;
    document.head.append(style);
  }

  function stopBodyScan(scanId) {
    if (!scan || (scanId && scan.id !== scanId)) return;
    clearTimeout(scan.timer);
    scan.settleSweep(false);
    scan.overlay.remove();
    window.removeEventListener("scroll", scan.position, true);
    window.removeEventListener("resize", scan.position);
    scan = null;
  }

  function startBodyScan(emailId, scanId) {
    const email = extractEmail();
    if (!email || email.email_id !== emailId || typeof scanId !== "string" || scanId.length > 100) {
      return { ok: false, error: "The selected message changed. Click Analyze again." };
    }
    if (document.visibilityState === "hidden") return { ok: false, error: "Return to the Gmail tab and analyze again." };
    stopBodyScan();
    ensureAttentionStyle();
    const body = findMessageBody();
    const overlay = document.createElement("div");
    overlay.className = "hookline-body-scan";
    overlay.setAttribute("aria-hidden", "true");
    const line = document.createElement("div");
    line.className = "hookline-body-scan-line";
    overlay.append(line);
    // An independent, pointer-transparent overlay: never rewrite the email's DOM.
    const position = () => {
      if (!body.isConnected || !visible(body)) { stopBodyScan(scanId); return; }
      const rect = body.getBoundingClientRect();
      const left = Math.max(0, rect.left), top = Math.max(0, rect.top);
      const width = Math.max(0, Math.min(window.innerWidth, rect.right) - left);
      const height = Math.max(0, Math.min(window.innerHeight, rect.bottom) - top);
      overlay.hidden = !width || !height;
      overlay.style.left = `${left}px`;
      overlay.style.top = `${top}px`;
      overlay.style.width = `${width}px`;
      overlay.style.height = `${height}px`;
      overlay.style.setProperty("--hookline-scan-height", `${height + 55}px`);
    };
    // One finite sweep, concurrent with the real check. Its end is presentation only,
    // never a claim that the backend checked every word or that the message is safe.
    const motion = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    let settled = false, fallbackTimer, resolveSweep;
    const sweepDone = new Promise(resolve => { resolveSweep = resolve; });
    const settleSweep = (completed) => {
      if (settled) return;
      settled = true;
      clearTimeout(fallbackTimer);
      line.removeEventListener("animationend", onAnimationEnd);
      motion?.removeEventListener("change", onMotionChange);
      // Also terminate a suppressed or stalled animation before acknowledging it.
      line.style.animation = "none";
      line.hidden = true;
      resolveSweep(completed);
    };
    const onAnimationEnd = event => {
      if (event.target === line && event.animationName === "hookline-body-sweep") settleSweep(true);
    };
    const onMotionChange = event => { if (event.matches) settleSweep(true); };
    line.addEventListener("animationend", onAnimationEnd);
    motion?.addEventListener("change", onMotionChange);
    scan = { id: scanId, emailId, overlay, position, sweepDone, settleSweep,
      timer: setTimeout(() => stopBodyScan(scanId), 46000) };
    document.body.append(overlay);
    if (motion?.matches) settleSweep(true);
    else fallbackTimer = setTimeout(() => settleSweep(true), BODY_SWEEP_FALLBACK_MS);
    window.addEventListener("scroll", position, true);
    window.addEventListener("resize", position);
    position();
    return { ok: true };
  }

  async function finishBodyScan(emailId, scanId) {
    const target = scan;
    if (!target || target.id !== scanId || target.emailId !== emailId) {
      return { ok: false, error: "The scan was canceled or replaced. Analyze the current message again." };
    }
    const completed = await target.sweepDone;
    // Re-extract here, not only in the debounced observer: Gmail may have changed
    // during the final sweep, before EMAIL_CHANGED reaches the side panel.
    let matches = false;
    try { matches = extractEmail()?.email_id === emailId; } catch { /* fail closed */ }
    if (!completed || scan !== target || !matches || document.visibilityState === "hidden") {
      stopBodyScan(scanId);
      return { ok: false, error: "The selected message changed or the scan was canceled. Analyze again." };
    }
    stopBodyScan(scanId);
    return { ok: true, completed: true, scan_id: scanId, email_id: emailId };
  }

  function visibleInboxRows() {
    // Never read bodies, previews, sender addresses or off-page messages for this check.
    return [...document.querySelectorAll("tr.zA")].filter(visible);
  }

  function rowSubject(row) {
    return row.querySelector("span.bog")?.textContent?.trim() || "";
  }

  function subjectSignals(subject) {
    const rules = [
      [/\b(?:urgent|immediately|final notice|action required|account suspended|within 24 hours)\b|緊急|立即|最後通知|帳[戶號].{0,4}(?:停用|凍結)/i, "Time pressure or account warning"],
      [/\b(?:password|verification code|one[- ]time (?:code|password)|verify (?:your )?account|reset (?:your )?password)\b|密碼|驗證碼|驗證.{0,3}帳[戶號]/i, "Password or account verification"],
      [/\b(?:(?:change|update|new|revised).{0,30}(?:bank|payroll|payment|account)|wire transfer|gift cards?|unpaid invoice|overdue payment)\b|(?:變更|更改|更新|新).{0,10}(?:銀行|收款|匯款|帳[戶號])|禮品卡|轉帳|匯款/i, "Payment or bank-detail request"]
    ];
    return rules.filter(([pattern]) => pattern.test(subject)).map(([, label]) => label);
  }

  function clearInbox(notify = false) {
    const previous = inboxSnapshot;
    if (!previous) return;
    inboxSnapshot = null;
    previous.rows.forEach(item => item.mark?.remove());
    if (notify) chrome.runtime.sendMessage({ type: "INBOX_CHANGED", snapshot_id: previous.id }).catch(() => {});
  }

  function inboxUnchanged() {
    if (!inboxSnapshot || location.hash !== inboxSnapshot.hash) return false;
    const rows = visibleInboxRows();
    return rows.length === inboxSnapshot.total && inboxSnapshot.rows.every((item, index) =>
      rows[index] === item.element && rowSubject(item.element) === item.subject);
  }

  function precheckInbox() {
    clearInbox();
    if (findMessageBody()) return { ok: false, error: "Return to the Gmail inbox or a message list first." };
    const allRows = visibleInboxRows();
    if (!allRows.length) return { ok: false, error: "No visible Gmail inbox rows were found. Open the inbox and try again." };
    ensureAttentionStyle();
    const id = `inbox-${++inboxRevision}`;
    const rows = allRows.slice(0, ROW_LIMIT).map((element, index) => {
      const subject = rowSubject(element);
      return { id: `${id}-${index}`, element, subject, signals: subjectSignals(subject) };
    });
    for (const item of rows) {
      if (!item.signals.length) continue;
      const title = item.element.querySelector("span.bog");
      const mark = document.createElement("span");
      mark.className = "hookline-title-flag";
      mark.textContent = "⚠ Check title";
      mark.title = `Local subject-only clue: ${item.signals.join("; ")}. Not a phishing verdict or safety check.`;
      mark.setAttribute("aria-label", mark.title);
      title.after(mark);
      item.mark = mark;
    }
    inboxSnapshot = { id, hash: location.hash, rows, total: allRows.length };
    return {
      ok: true, snapshot_id: id, checked: rows.length, visible_total: allRows.length,
      missing_subjects: rows.filter(item => !item.subject).length,
      flagged: rows.filter(item => item.signals.length).map(({ id: row_id, subject, signals }) => ({ row_id, subject, signals }))
    };
  }

  function openInboxRow(snapshotId, rowId) {
    if (!inboxSnapshot || inboxSnapshot.id !== snapshotId) {
      return { ok: false, error: "This title-check result expired. Run the check again." };
    }
    if (!inboxUnchanged()) {
      clearInbox(true);
      return { ok: false, error: "The Gmail list changed. Run the title check again." };
    }
    const item = inboxSnapshot.rows.find(row => row.id === rowId && row.signals.length);
    if (!item) return { ok: false, error: "This row is not part of the current title check." };
    // Click only the captured Gmail row after checking its identity. Never follow an email URL.
    item.element.click();
    return { ok: true };
  }


  function visible(element) {
    return Boolean(element && element.getClientRects().length > 0);
  }

  function findMessageBody() {
    const bodies = [...document.querySelectorAll(".a3s")]
      .filter((element) => visible(element) && element.innerText?.trim());
    return bodies.at(-1) || null; // The last expanded message in a thread.
  }

  function shortHash(value) {
    let hash = 2166136261;
    for (let i = 0; i < value.length; i++) {
      hash ^= value.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16);
  }

  function extractEmail() {
    const body = findMessageBody();
    if (!body) return null;

    const container = body.closest(".adn") || body.closest("[data-message-id]") || body.parentElement;
    const from = container?.querySelector(".gD[email]");
    const senderAddress = from?.getAttribute("email") || "";
    const senderName = from?.textContent?.trim() || senderAddress;
    const subject = document.querySelector("h2.hP")?.textContent?.trim() || "(No subject found)";
    const content = body.innerText.trim();
    // Never silently drop body text or over-limit links and call it a complete check.
    if (content.length + subject.length > 20000) throw new Error("This message exceeds the 20,000-character analysis limit. No text was sent.");
    const allLinks = [...body.querySelectorAll("a[href]")];
    const links = allLinks.slice(0, 50).map((link, index) => ({
      id: `l${index + 1}`,
      text: link.innerText?.trim() || link.textContent?.trim() || "(link)",
      url: link.href
    }));
    return {
      email_id: `gmail-${shortHash(`${location.hash}|${senderAddress}|${subject}|${content}|${JSON.stringify(links)}`)}`,
      sender: { name: senderName, address: senderAddress },
      subject,
      blocks: [{ id: "b1", text: content }],
      extraction_complete: false,
      extraction_limitations: [
        "Gmail DOM view only: the last visible expanded message, not the full thread.",
        "Raw authentication headers, Reply-To and attachment contents are unavailable.",
        ...(allLinks.length > 50 ? ["Only the first 50 links were extracted."] : [])
      ],
      links
    };
  }

  function clearHighlight() {
    stopBodyScan();
    clearTimeout(highlightTimer);
    if (globalThis.CSS?.highlights) CSS.highlights.delete(HIGHLIGHT_NAME);
    const selection = window.getSelection();
    if (fallbackRange && selection?.rangeCount === 1) {
      const range = selection.getRangeAt(0);
      if (range.startContainer === fallbackRange.startContainer && range.startOffset === fallbackRange.startOffset &&
          range.endContainer === fallbackRange.endContainer && range.endOffset === fallbackRange.endOffset) selection.removeAllRanges();
    }
    fallbackRange = null;
  }

  function buildRange(root, quote) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    let node;
    while ((node = walker.nextNode())) {
      if (node.textContent) nodes.push(node);
    }
    const combined = nodes.map((item) => item.textContent).join("");
    const from = combined.indexOf(quote);
    if (from === -1) return null;
    const to = from + quote.length;
    let seen = 0;
    let startNode, startOffset, endNode, endOffset;
    for (const item of nodes) {
      const end = seen + item.textContent.length;
      if (!startNode && from < end) {
        startNode = item;
        startOffset = from - seen;
      }
      if (startNode && to <= end) {
        endNode = item;
        endOffset = to - seen;
        break;
      }
      seen = end;
    }
    if (!startNode || !endNode) return null;
    const range = document.createRange();
    range.setStart(startNode, startOffset);
    range.setEnd(endNode, endOffset);
    return range;
  }

  function highlightEvidence(evidence, requestedEmailId) {
    const email = extractEmail();
    if (!email || email.email_id !== requestedEmailId) {
      return { success: false, reason: "You switched emails. Analyze the new message first." };
    }
    if (evidence?.block_id !== "b1" || !evidence?.quote) {
      return { success: false, reason: "No valid block and quote were provided." };
    }
    const body = findMessageBody();
    if (!email.blocks[0].text.includes(evidence.quote)) {
      return { success: false, reason: "Evidence quote is not present in this message." };
    }
    const range = buildRange(body, evidence.quote);
    if (!range) {
      return { success: false, reason: "Evidence is valid, but the Gmail formatting prevented an exact DOM highlight." };
    }
    clearHighlight();
    if (globalThis.CSS?.highlights && typeof Highlight !== "undefined") {
      if (!document.getElementById(STYLE_ID)) {
        const style = document.createElement("style");
        style.id = STYLE_ID;
        style.textContent = `::highlight(${HIGHLIGHT_NAME}) { background: #ffe082; color: #30220d; text-decoration: underline; }`;
        document.head.append(style);
      }
      CSS.highlights.set(HIGHLIGHT_NAME, new Highlight(range));
    } else {
      // Selection is a transient fallback. Do not wrap, replace or flatten email nodes.
      const selection = window.getSelection();
      selection?.removeAllRanges();
      selection?.addRange(range);
      fallbackRange = range;
    }
    highlightTimer = setTimeout(clearHighlight, 8000);
    range.startContainer.parentElement?.scrollIntoView({ behavior: "smooth", block: "center" });
    return { success: true };
  }

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (["START_BODY_SCAN", "FINISH_BODY_SCAN", "STOP_BODY_SCAN", "PRECHECK_INBOX", "CLEAR_INBOX_MARKS", "OPEN_INBOX_ROW"].includes(message?.type)) {
      if (sender?.id !== chrome.runtime.id || sender.tab || sender.url !== chrome.runtime.getURL("sidepanel.html")) {
        sendResponse({ ok: false, error: "Use the dobby’s catch side panel for this action." });
        return;
      }
      try {
        if (message.type === "FINISH_BODY_SCAN") {
          finishBodyScan(message.email_id, message.scan_id).then(sendResponse, () => sendResponse({ ok: false, error: "Could not finish the message scan. Analyze again." }));
          return true; // Keep this Chrome response channel open until the sweep ends.
        }
        if (message.type === "START_BODY_SCAN") sendResponse(startBodyScan(message.email_id, message.scan_id));
        if (message.type === "STOP_BODY_SCAN") { stopBodyScan(message.scan_id); sendResponse({ ok: true }); }
        if (message.type === "PRECHECK_INBOX") sendResponse(precheckInbox());
        if (message.type === "CLEAR_INBOX_MARKS") { if (!message.snapshot_id || inboxSnapshot?.id === message.snapshot_id) clearInbox(); sendResponse({ ok: true }); }
        if (message.type === "OPEN_INBOX_ROW") sendResponse(openInboxRow(message.snapshot_id, message.row_id));
      } catch { sendResponse({ ok: false, error: "The Gmail view changed. Refresh the view and try again." }); }
      return;
    }
    if (message.type === "EXTRACT_EMAIL") {
      try {
        const email = extractEmail();
        lastEmailId = email?.email_id || null;
        sendResponse(email ? { ok: true, email } : { ok: false, error: "Open a Gmail message first (not just your inbox)." });
      } catch (error) { sendResponse({ ok: false, error: error.message }); }
    } else if (message.type === "HIGHLIGHT_EVIDENCE") {
      try { sendResponse(highlightEvidence(message.evidence, message.email_id)); }
      catch { sendResponse({ success: false, reason: "Message extraction changed. Analyze again before highlighting." }); }
    } else if (message.type === "CLEAR_HIGHLIGHTS") {
      clearHighlight();
      sendResponse({ success: true });
    }
  });

  function checkEmailChange() {
    if (inboxSnapshot && !inboxUnchanged()) clearInbox(true);
    let now;
    try { now = extractEmail()?.email_id || null; }
    catch { now = null; }
    if (now === lastEmailId) return;
    clearHighlight();
    lastEmailId = now;
    chrome.runtime.sendMessage({ type: "EMAIL_CHANGED", email_id: now }).catch(() => {});
  }

  const observer = new MutationObserver(() => {
    clearTimeout(checkTimer);
    checkTimer = setTimeout(checkEmailChange, 300);
  });
  observer.observe(document.documentElement, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ["href", "email"] });
  window.addEventListener("hashchange", () => {
    stopBodyScan();
    clearInbox(true);
    checkEmailChange();
  });
  document.addEventListener?.("visibilitychange", () => { if (document.visibilityState === "hidden") stopBodyScan(); });
  window.addEventListener("pagehide", () => { stopBodyScan(); clearInbox(); });
  checkEmailChange();
})();
