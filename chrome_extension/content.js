// Gmail is a single-page app. These selectors are practical hackathon heuristics,
// NOT a supported Gmail API. Test against your actual Gmail account before demoing.
(() => {
  const HIGHLIGHT_NAME = "hookline-evidence";
  const STYLE_ID = "hookline-highlight-style";
  let lastEmailId = null;
  let checkTimer;
  let fallbackMarks = [];

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
    const from = container?.querySelector(".gD[email]") || document.querySelector(".gD[email]");
    const senderAddress = from?.getAttribute("email") || "unknown";
    const senderName = from?.textContent?.trim() || senderAddress;
    const subject = document.querySelector("h2.hP")?.textContent?.trim() || "(No subject found)";
    const content = body.innerText.trim();
    const links = [...body.querySelectorAll("a[href]")].slice(0, 40).map((link, index) => ({
      id: `l${index + 1}`,
      text: link.innerText?.trim() || link.textContent?.trim() || "(link)",
      url: link.href
    }));
    return {
      email_id: `gmail-${shortHash(`${location.hash}|${senderAddress}|${subject}|${content}`)}`,
      sender: { name: senderName, address: senderAddress },
      subject,
      blocks: [{ id: "b1", text: content }],
      links
    };
  }

  function clearHighlight() {
    if (globalThis.CSS?.highlights) CSS.highlights.delete(HIGHLIGHT_NAME);
    for (const mark of fallbackMarks) mark.replaceWith(document.createTextNode(mark.textContent || ""));
    fallbackMarks = [];
    window.getSelection()?.removeAllRanges();
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
      try {
        const mark = document.createElement("mark");
        mark.style.cssText = "background:#ffe082;color:#30220d;text-decoration:underline";
        range.surroundContents(mark);
        fallbackMarks.push(mark);
      } catch {
        const selection = window.getSelection();
        selection?.removeAllRanges();
        selection?.addRange(range);
      }
    }
    range.startContainer.parentElement?.scrollIntoView({ behavior: "smooth", block: "center" });
    return { success: true };
  }

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type === "EXTRACT_EMAIL") {
      const email = extractEmail();
      lastEmailId = email?.email_id || null;
      sendResponse(email ? { ok: true, email } : { ok: false, error: "Open a Gmail message first (not just your inbox)." });
    } else if (message.type === "HIGHLIGHT_EVIDENCE") {
      sendResponse(highlightEvidence(message.evidence, message.email_id));
    } else if (message.type === "CLEAR_HIGHLIGHTS") {
      clearHighlight();
      sendResponse({ success: true });
    }
  });

  function checkEmailChange() {
    const now = extractEmail()?.email_id || null;
    if (now === lastEmailId) return;
    clearHighlight();
    lastEmailId = now;
    chrome.runtime.sendMessage({ type: "EMAIL_CHANGED", email_id: now }).catch(() => {});
  }

  const observer = new MutationObserver(() => {
    clearTimeout(checkTimer);
    checkTimer = setTimeout(checkEmailChange, 300);
  });
  observer.observe(document.documentElement, { subtree: true, childList: true, characterData: true });
  window.addEventListener("hashchange", checkEmailChange);
  checkEmailChange();
})();
