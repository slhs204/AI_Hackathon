const $ = (id) => document.getElementById(id);
const DEMO_EMAIL = {
  email_id: "demo-001",
  sender: { name: "Payroll Support", address: "support@example.test" },
  subject: "Urgent account update",
  blocks: [{ id: "b1", text: "Hello, Please change my salary account today. This is urgent. Do not tell anyone until it is complete." }],
  links: []
};

let currentEmail = null;
let currentMode = null; // "gmail" or "demo"
let currentTabId = null;
let currentFindings = [];
let selectedFindingId = null;
let requestNumber = 0;
let challengeNumber = 0;
let connected = false;
let pendingExtractionTab = null;
let currentAnalysis = null;
let simpleMode = true;
let activeAction = null;
let actionOpener = null;
let activeBodyScan = null;
const scanSession = globalThis.crypto?.randomUUID?.() || Math.random().toString(36).slice(2);

async function endBodyScan(target = activeBodyScan) {
  if (!target) return;
  target.cancelFinish?.();
  if (activeBodyScan === target) activeBodyScan = null;
  await chrome.tabs.sendMessage(target.tabId, { type: "STOP_BODY_SCAN", scan_id: target.id }).catch(() => {});
}

async function beginBodyScan(email, tabId, request) {
  const target = { tabId, id: `${scanSession}-${request}`, request };
  activeBodyScan = target;
  const response = await chrome.tabs.sendMessage(tabId, { type: "START_BODY_SCAN", email_id: email.email_id, scan_id: target.id });
  if (!response?.ok) throw new Error(response?.error || "Could not confirm the selected Gmail message. Refresh Gmail and try again.");
  return target;
}

async function finishBodyScan(target, email) {
  // Content owns actual animation completion. A lost response must not leave the
  // panel waiting forever or allow results alongside an unfinished overlay.
  let timer;
  const interrupted = new Promise((_, reject) => {
    target.cancelFinish = () => reject(new Error("Check canceled."));
    timer = setTimeout(() => reject(new Error("Could not finish the scan display. Refresh Gmail and try again.")), 2500);
  });
  try {
    const response = await Promise.race([
      chrome.tabs.sendMessage(target.tabId, { type: "FINISH_BODY_SCAN", email_id: email.email_id, scan_id: target.id }),
      interrupted
    ]);
    if (!response?.ok || response.completed !== true || response.scan_id !== target.id || response.email_id !== email.email_id) {
      throw new Error(response?.error || "The scan was interrupted. Refresh Gmail and analyze again.");
    }
    if (activeBodyScan === target) activeBodyScan = null;
  } finally {
    clearTimeout(timer);
    target.cancelFinish = null;
  }
}

function setBusy(busy) {
  $("analyze").disabled = busy;
  $("demo").disabled = busy;
  $("analyze").setAttribute("aria-busy", String(busy));
  $("cancel-check").hidden = !busy;
}

function modeLabel(analysis, mocked) {
  if (mocked) return "LOCAL DEMO";
  if (analysis?.model === "rules-only") return "BACKEND RULES ONLY";
  return "MODE UNVERIFIED";
}


function setStatus(text, error = false) {
  $("status").textContent = text;
  $("status").classList.toggle("error", error);
}

function setEmail(email) {
  $("subject").textContent = email?.subject || "No message selected";
  $("sender").textContent = email
    ? `${email.sender?.name || "Unknown sender"} · ${email.sender?.address || "unknown"}`
    : "Open an email in Gmail to get started.";
}

function clearResults(status = "Open a Gmail message and analyze it.") {
  const hadResult = currentAnalysis !== null;
  void endBodyScan();
  requestNumber++;
  challengeNumber++;
  setBusy(false);
  $("challenge").disabled = false;
  $("mode").textContent = connected ? "STAGING CONNECTED" : "NOT CONNECTED";
  currentEmail = null;
  currentAnalysis = null;
  closeAction(false);
  currentFindings = [];
  selectedFindingId = null;
  currentMode = null;
  currentTabId = null;
  pendingExtractionTab = null;
  setEmail(null);
  resetHook();
  $("results").hidden = true;
  $("challenge-section").hidden = true;
  $("practice").hidden = true;
  $("challenge-result").textContent = "";
  $("practice-feedback").textContent = "";
  setStatus(status);
  updateView();
  if (hadResult) $("analyze").focus?.();
}

async function activeTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function clearGmailHighlight() {
  if (currentMode === "gmail" && currentTabId) {
    await chrome.tabs.sendMessage(currentTabId, { type: "CLEAR_HIGHLIGHTS" }).catch(() => {});
  }
}

async function analyzeEmail(email, mode, tabId = null) {
  const myRequest = ++requestNumber;
  challengeNumber++;
  setBusy(true);
  await clearGmailHighlight();
  if (myRequest !== requestNumber) return;
  currentAnalysis = null;
  closeAction(false);
  updateView();
  currentEmail = email;
  currentMode = mode;
  currentTabId = tabId;
  currentFindings = [];
  selectedFindingId = null;
  resetHook();
  setEmail(email);
  $("results").hidden = true;
  $("challenge-section").hidden = true;
  $("practice").hidden = true;
  $("challenge-result").textContent = "";
  $("practice-feedback").textContent = "";
  setStatus("Checking the selected message body… Animation shows activity, not proof of a complete check.");
  setBusy(true);
  let scanTarget = null;
  try {
    if (mode === "gmail") {
      scanTarget = await beginBodyScan(email, tabId, myRequest);
      if (myRequest !== requestNumber) return;
    }
    const response = await chrome.runtime.sendMessage({ type: "ANALYZE", email, demo: mode === "demo" });
    if (myRequest !== requestNumber) return;
    if (!response?.ok) throw new Error(response?.error || "No analysis returned.");
    const analysis = response.data;
    if (analysis.email_id !== email.email_id) throw new Error("Backend response email ID does not match the selected email.");
    if (scanTarget) {
      const tab = await activeTab();
      if (myRequest !== requestNumber) return;
      if (tab?.id !== tabId) {
        clearResults("Tab changed. Analyze the email in your active tab.");
        return;
      }
      setStatus("Backend response received. Finishing the visual indicator before showing results…");
      await finishBodyScan(scanTarget, email);
      if (myRequest !== requestNumber) return;
    }
    currentFindings = Array.isArray(analysis.findings) ? analysis.findings : [];
    renderResults(analysis, response.mocked);
    setStatus(response.mocked ? "Local demo complete. No email was sent and no AI was called." :
      analysis.analysis_complete ? "Backend rules-only check complete. No AI was called; this is not payment approval." :
      "Partial backend rules-only check. Review the missing-information notes before acting.");
  } catch (error) {
    if (myRequest === requestNumber) setStatus(`Analysis failed: ${error.message}`, true);
  } finally {
    await endBodyScan(scanTarget || (activeBodyScan?.request === myRequest ? activeBodyScan : null));
    if (myRequest === requestNumber) setBusy(false);
  }
}

function appendParagraph(parent, text, className) {
  const paragraph = document.createElement("p");
  if (className) paragraph.className = className;
  paragraph.textContent = text;
  parent.append(paragraph);
}

function resetHook() {
  $("warning-total").textContent = "0";
  $("count").textContent = "warning signs";
  $("bait-list").replaceChildren();
  $("hook-detail").hidden = true;
  $("hook-instruction").textContent = "Select a clue to learn why it matters and highlight the evidence in Gmail.";
}

function renderBait() {
  const list = $("bait-list");
  list.replaceChildren();
  if (!currentFindings.length) {
    const placeholder = document.createElement("div");
    placeholder.className = "bait-empty";
    placeholder.textContent = "No clues found by this analysis. That does not mean the message is safe.";
    list.append(placeholder);
    return;
  }
  for (const [index, finding] of currentFindings.entries()) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "bait";
    button.dataset.findingId = finding.id;
    button.style.setProperty("--bait-index", String(Math.min(index, 8)));
    button.setAttribute("aria-pressed", "false");
    button.setAttribute("aria-label", `Clue ${index + 1}: ${finding.title || finding.category || "Warning"}. ${currentMode === "gmail" ? "Select and highlight in Gmail." : "Preview this clue."}`);

    const bead = document.createElement("span");
    bead.className = "bait-bead";
    bead.setAttribute("aria-hidden", "true");
    bead.textContent = String(index + 1);
    const content = document.createElement("span");
    content.className = "bait-text";
    const title = document.createElement("span");
    title.className = "bait-title";
    title.textContent = finding.title || finding.category || "Warning sign";
    const quote = document.createElement("span");
    quote.className = "bait-quote";
    quote.textContent = finding.evidence?.quote ? `“${finding.evidence.quote}”` : "Evidence not available";
    content.append(title, quote);
    const arrow = document.createElement("span");
    arrow.className = "bait-arrow";
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "↗";
    button.append(bead, content, arrow);
    button.addEventListener("click", () => selectFinding(finding));
    list.append(button);
  }
}

async function selectFinding(finding) {
  // Selecting a clue also determines which finding the challenge feature discusses.
  selectedFindingId = finding.id;
  challengeNumber++;
  $("challenge").disabled = false;
  for (const button of $("bait-list").querySelectorAll(".bait")) {
    button.setAttribute("aria-pressed", String(button.dataset.findingId === finding.id));
  }
  for (const card of $("findings").querySelectorAll(".finding")) {
    card.classList.toggle("selected", card.dataset.findingId === finding.id);
  }
  const index = currentFindings.indexOf(finding) + 1;
  $("hook-detail-number").textContent = `#${index}`;
  $("hook-detail-title").textContent = finding.title || finding.category || "Warning sign";
  $("hook-detail-quote").textContent = finding.evidence?.quote ? `“${finding.evidence.quote}”` : "No exact quote available";
  $("hook-detail-why").textContent = `Why it matters: ${finding.explanation || "Review the request carefully."}`;
  $("hook-detail-check").textContent = `How to check: ${finding.next_action || "Use a trusted, separate channel."}`;
  $("hook-detail").hidden = false;
  $("hook-instruction").textContent = currentMode === "gmail"
    ? "Selected clue. dobby’s catch is locating its exact text in Gmail."
    : "Demo clue selected. Analyze an email in Gmail to see the exact highlight.";
  $("challenge-result").textContent = "";
  await highlightFinding(finding);
}

const DIM_MARK = { ok: ["✓", "no warning"], warn: ["⚠", "warning"], unknown: ["?", "can't tell"] };

// Rubric v2 from /analyze: the answer plus four questions, each ✓ / ⚠ / ? (can't tell). Hidden in mock mode.
function renderVerdictBox(analysis) {
  const dims = Array.isArray(analysis.dimensions) ? analysis.dimensions : [];
  $("verdict-box").hidden = !analysis.verdict || !dims.length;
  if ($("verdict-box").hidden) return;
  const state = analysis.verdict.state === "unknown" ? "unknown" : analysis.verdict.key;
  $("verdict-box").dataset.state = state;
  $("verdict-line").textContent = analysis.verdict.label || analysis.verdict.key;
  $("dim-list").replaceChildren(...dims.map((d) => {
    const [mark, spoken] = DIM_MARK[d.status] || DIM_MARK.unknown;
    const li = document.createElement("li");
    li.className = `dim ${d.status}`;
    const m = document.createElement("span");
    m.className = "dim-mark";
    m.textContent = mark;
    m.setAttribute("aria-label", spoken);
    const text = document.createElement("span");
    const q = document.createElement("strong");
    q.textContent = d.question;
    text.append(q, document.createElement("br"), d.answer);
    li.append(m, text);
    return li;
  }));
  $("dim-rule").textContent = analysis.verdict.rule || "";
}

function renderResults(analysis, mocked) {
  const count = currentFindings.length;
  currentAnalysis = analysis;
  renderVerdictBox(analysis);
  renderSimple(analysis);
  $("warning-total").textContent = String(count);
  $("count").textContent = `warning sign${count === 1 ? "" : "s"}`;
  $("summary").textContent = analysis.summary || "Review the findings and evidence below.";
  $("completeness").textContent = analysis.analysis_complete
    ? "Checked the supplied text only. Sender identity and payment approval are not established."
    : "Incomplete assessment. Missing information or failed checks must not be treated as clearance.";
  $("limitations").replaceChildren(...(analysis.limitations || []).map(text => {
    const item = document.createElement("li");
    item.textContent = text;
    return item;
  }));
  $("analysis-notes").replaceChildren();
  for (const note of analysis.notes || []) {
    appendParagraph($("analysis-notes"), `Context note: ${note.explanation || note.title || note.category}`);
  }
  $("findings").replaceChildren();
  for (const finding of currentFindings) {
    const card = document.createElement("div");
    card.className = "finding";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "finding-title";
    const heading = document.createElement("strong");
    heading.textContent = `⚠ ${finding.title || finding.category || "Warning sign"}`;
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = currentMode === "gmail" ? "Highlight ↗" : "Demo finding";
    button.append(heading, tag);
    button.addEventListener("click", () => selectFinding(finding));
    card.append(button);
    if (finding.evidence?.quote) appendParagraph(card, `“${finding.evidence.quote}”`, "quote");
    appendParagraph(card, `Why: ${finding.explanation || "Review this request carefully."}`);
    appendParagraph(card, `How to check: ${finding.next_action || "Use a trusted, separate communication channel."}`, "next-action");
    card.dataset.findingId = finding.id;
    $("findings").append(card);
  }
  if (!count) appendParagraph($("findings"), "No specific findings from this analysis. Do not treat that as proof the email is safe.");
  renderBait();
  $("results").hidden = false;
  $("challenge-section").hidden = count === 0;
  $("practice").hidden = count === 0;
  $("mode").textContent = modeLabel(analysis, mocked);
  updateView();
  $(simpleMode ? "simple-title" : "results").focus?.();
}

async function highlightFinding(finding) {
  const emailIdAtRequest = currentEmail?.email_id;
  const tabAtRequest = currentTabId;
  if (currentMode !== "gmail") {
    setStatus("Demo mode has no Gmail text to highlight. Analyze a matching message in Gmail to test highlighting.");
    return;
  }
  try {
    const response = await chrome.tabs.sendMessage(currentTabId, {
      type: "HIGHLIGHT_EVIDENCE",
      email_id: currentEmail.email_id,
      evidence: finding.evidence
    });
    if (currentEmail?.email_id !== emailIdAtRequest || currentTabId !== tabAtRequest) return;
    setStatus(response?.success ? "Matching evidence highlighted in Gmail." : (response?.reason || "Evidence could not be highlighted."), !response?.success);
  } catch (error) {
    if (currentEmail?.email_id === emailIdAtRequest && currentTabId === tabAtRequest) {
      setStatus(`Could not reach the Gmail tab: ${error.message}. Reload Gmail and try again.`, true);
    }
  }
}

$("analyze").addEventListener("click", async () => {
  const extractionRequest = ++requestNumber;
  setBusy(true);
  try {
    const tab = await activeTab();
    if (extractionRequest !== requestNumber) return;
    if (!tab?.id) throw new Error("No active browser tab was found.");
    pendingExtractionTab = tab.id;
    // Do not depend on tab.url: Chrome can hide that field without explicit grants.
    // Only the Gmail content script responds to EXTRACT_EMAIL.
    const response = await chrome.tabs.sendMessage(tab.id, { type: "EXTRACT_EMAIL" });
    if (extractionRequest !== requestNumber) return;
    if (!response?.ok) throw new Error(response?.error || "Could not read email.");
    const stillActive = await activeTab();
    const latest = await chrome.tabs.sendMessage(tab.id, { type: "EXTRACT_EMAIL" });
    if (extractionRequest !== requestNumber) return;
    if (stillActive?.id !== tab.id || !latest?.ok || latest.email.email_id !== response.email.email_id) {
      clearResults("Selected email changed during extraction. Click Analyze again.");
      return;
    }
    pendingExtractionTab = null;
    await analyzeEmail(response.email, "gmail", tab.id);
  } catch (error) {
    // Prevent a previously displayed demo from looking like an analysis of Gmail.
    if (extractionRequest !== requestNumber) return;
    await clearGmailHighlight();
    if (extractionRequest !== requestNumber) return;
    clearResults();
    const missingReceiver = /Receiving end does not exist|Could not establish connection/i.test(String(error?.message || ""));
    setStatus(missingReceiver
      ? "dobby’s catch could not connect to Gmail. Make sure Gmail is active, refresh the Gmail tab, and try again."
      : `Could not read the message: ${error.message}`, true);
  }
});

$("cancel-check").addEventListener("click", () => {
  clearResults("Check canceled. A request already sent may still finish; its result will not be shown.");
  $("analyze").focus?.();
});

$("demo").addEventListener("click", () => analyzeEmail(DEMO_EMAIL, "demo"));

$("challenge").addEventListener("click", async () => {
  const context = $("challenge-text").value.trim();
  if (!context) {
    $("challenge-result").textContent = "Please enter context for the selected finding. Rules-only mode does not call AI.";
    return;
  }
  const selectedFinding = currentFindings.find((item) => item.id === selectedFindingId)
    || currentFindings[0];
  if (!currentEmail || !selectedFinding) return;
  const myRequest = requestNumber;
  const myChallenge = ++challengeNumber;
  $("challenge").disabled = true;
  $("challenge-result").textContent = "Reconsidering…";
  try {
    const response = await chrome.runtime.sendMessage({
      type: "CHALLENGE", email: currentEmail, finding: selectedFinding, context, demo: currentMode === "demo"
    });
    if (myRequest !== requestNumber || myChallenge !== challengeNumber) return;
    if (!response?.ok) throw new Error(response?.error || "No response.");
    const data = response.data;
    $("challenge-result").textContent = response.mocked
      ? `Local demo response: ${data.explanation}\nNext step: ${data.next_action}`
      : `Backend rules-only: ${data.assessment === "less_concerning" ? "Less concerning, not cleared" : "Still concerning"}. ${data.message}\nStill unresolved: ${data.still_unresolved}\nNext step: ${data.next_action}`;
  } catch (error) {
    if (myRequest === requestNumber && myChallenge === challengeNumber) $("challenge-result").textContent = `Challenge failed: ${error.message}`;
  } finally {
    if (myRequest === requestNumber && myChallenge === challengeNumber) $("challenge").disabled = false;
  }
});

$("unsafe-answer").addEventListener("click", () => {
  $("practice-feedback").textContent = "Not quite. An email's urgency is not a reason to skip established approval procedures.";
});
$("safe-answer").addEventListener("click", () => {
  $("practice-feedback").textContent = "Correct. Verify through your existing payroll or payment approval process.";
});

chrome.runtime.onMessage.addListener((message, sender) => {
  if (message?.type !== "EMAIL_CHANGED") return;
  if (pendingExtractionTab === sender.tab?.id ||
      currentMode === "gmail" && currentTabId === sender.tab?.id && message.email_id !== currentEmail?.email_id) {
    clearResults("Different email opened. Click Analyze open email for fresh results.");
  }
});
chrome.tabs.onActivated.addListener(({ tabId }) => {
  if (pendingExtractionTab !== null && pendingExtractionTab !== tabId ||
      currentMode === "gmail" && currentTabId !== tabId) {
    clearResults("Tab changed. Analyze the email in your active tab.");
  }
});

async function refreshConnection() {
  const response = await chrome.runtime.sendMessage({ type: "CONNECTION_STATUS" });
  connected = response?.ok && response.connected;
  $("connection-status").textContent = connected
    ? "Session configured for 127.0.0.1:8080. Each analysis rechecks rules-only mode."
    : "Not connected. Try demo stays local. Connect before analyzing Gmail.";
  if (!currentEmail) $("mode").textContent = connected ? "STAGING CONNECTED" : "NOT CONNECTED";
}

$("connect").addEventListener("click", async () => {
  $("connect").disabled = true;
  const token = $("demo-token").value;
  $("demo-token").value = "";
  try {
    const response = await chrome.runtime.sendMessage({ type: "CONNECT", token });
    if (!response?.ok) throw new Error(response?.error || "Connection failed.");
    await refreshConnection();
    clearResults("Connected to rules-only staging. Only a click on Analyze sends the selected email.");
  } catch (error) {
    $("connection-status").textContent = `Connection failed: ${error.message}`;
  } finally { $("connect").disabled = false; }
});
$("disconnect").addEventListener("click", async () => {
  requestNumber++;
  challengeNumber++;
  await chrome.runtime.sendMessage({ type: "DISCONNECT" });
  await clearGmailHighlight();
  connected = false;
  clearResults("Disconnected. Session token cleared; Try demo stays local.");
  await refreshConnection();
});
refreshConnection().catch(() => { $("connection-status").textContent = "Could not read connection state. Reload the extension."; });
setStatus("Use synthetic email only. Connect to private staging before analyzing Gmail, or choose Try demo.");


// Simple is a presentation of the same assessment, never an override or payment authorization.
function simpleAssessment(analysis) {
  const verdict = analysis?.verdict;
  const dims = Array.isArray(analysis?.dimensions) ? analysis.dimensions : [];
  const findings = Array.isArray(analysis?.findings) ? analysis.findings : [];
  if (verdict?.key === "stop") return { state: "stop", title: "Don't pay yet" };
  if (findings.length || dims.some(d => d.status === "warn")) return { state: "verify", title: "Check first" };
  const allChecked = ["sender", "money", "pressure", "links"].every(key =>
    dims.filter(d => d.key === key).length === 1 && dims.find(d => d.key === key).status === "ok");
  if (verdict?.key === "pay" && verdict.state !== "unknown" && analysis.analysis_complete === true &&
      allChecked && dims.length === 4 && !(analysis.limitations || []).length) {
    return { state: "clear", title: "No warning signs" };
  }
  if (verdict?.key === "verify" && verdict.state !== "unknown" && analysis.analysis_complete === true) {
    return { state: "verify", title: "Check first" };
  }
  return { state: "unknown", title: "Can't tell yet" };
}

function renderSimple(analysis) {
  const assessment = simpleAssessment(analysis);
  $("simple-verdict").dataset.state = assessment.state;
  $("simple-title").textContent = assessment.title;
  $("result-subject").textContent = currentEmail?.subject || "Selected message";
  $("result-sender").textContent = currentEmail
    ? `${currentEmail.sender?.name || "Unknown sender"} · ${currentEmail.sender?.address || "address unavailable"}`
    : "Sender unavailable";
  const count = currentFindings.length;
  $("simple-scope").textContent = count
    ? `${count} warning sign${count === 1 ? "" : "s"}. Check through a channel you already trust.`
    : analysis.analysis_complete !== true || assessment.state === "unknown"
      ? "Not enough information to assess this message. Verify through a channel you already trust."
      : "No warning signs found is not proof of safety. Verify independently before acting.";
  $("simple-warning").textContent = analysis.analysis_complete === true
    ? "Sender identity and payment approval are not established by this tool."
    : "Incomplete check. Sender, headers or other information could not be verified. This is not payment approval.";
  $("simple-reviewed").hidden = assessment.state !== "clear";
  $("simple-call").hidden = false;
  $("reviewed-note").textContent = "";
}

function updateView() {
  const hasResult = currentAnalysis !== null;
  $("home-view").hidden = hasResult;
  $("result-context").hidden = !hasResult;
  $("simple-view").hidden = !hasResult || !simpleMode || activeAction !== null;
  $("details-view").hidden = !hasResult || simpleMode || activeAction !== null;
  $("action-panel").hidden = !hasResult || activeAction === null;
  $("back").hidden = !hasResult;
  $("simple-toggle").checked = simpleMode;
}

const SIMPLE_ACTIONS = {
  call: {
    title: "Call to check",
    guidance: "Use a number from your saved contacts or your organization's trusted directory. Do not use a phone number or link from this email. Confirm the request and follow the normal approval process. This button does not place a call."
  },
  reply: {
    title: "Reply: wait",
    guidance: "You do not need to reply to a suspicious sender. If appropriate, contact the person separately using a known address. The wording below is only a local draft; review it before you use it.",
    template: "I will hold this request while I verify it through our usual process."
  },
  report: {
    title: "Tell IT",
    guidance: "Use your organization's established phishing-reporting button or known IT/security contact. Do not use contact details in the suspicious email. Nothing is reported automatically, and email contents are not copied into this draft.",
    template: "Please review a potentially suspicious email. I have paused the request pending verification. What is the approved way to report it?"
  }
};

function openAction(kind, opener) {
  if (!currentAnalysis || !SIMPLE_ACTIONS[kind]) return;
  const action = SIMPLE_ACTIONS[kind];
  activeAction = kind;
  actionOpener = opener;
  $("action-title").textContent = action.title;
  $("action-guidance").textContent = action.guidance;
  $("action-template").value = action.template || "";
  $("action-template").hidden = !action.template;
  $("action-template-label").hidden = !action.template;
  updateView();
  $("action-title").focus?.();
}

function closeAction(restoreFocus = true) {
  const opener = actionOpener;
  activeAction = null;
  actionOpener = null;
  $("action-template").value = "";
  $("action-panel").hidden = true;
  if (restoreFocus) {
    updateView();
    $(opener || "simple-title").focus?.();
  }
}

$("simple-toggle").addEventListener("change", () => {
  simpleMode = $("simple-toggle").checked;
  closeAction(false);
  updateView();
});
$("simple-why").addEventListener("click", () => {
  simpleMode = false;
  updateView();
  $("results").focus?.();
});
$("back").addEventListener("click", async () => {
  if (activeAction) return closeAction();
  if (!simpleMode && currentAnalysis) {
    simpleMode = true;
    updateView();
    $("simple-title").focus?.();
    return;
  }
  const backRequest = ++requestNumber;
  challengeNumber++;
  await clearGmailHighlight();
  if (backRequest !== requestNumber) return;
  clearResults("Choose another message, then click Analyze open email. Try demo stays local.");
  $("analyze").focus?.();
});
$("action-close").addEventListener("click", () => closeAction());
for (const [kind, id] of [["call", "simple-call"], ["reply", "simple-reply"], ["report", "simple-report"]]) {
  $(id).addEventListener("click", () => openAction(kind, id));
}
$("simple-reviewed").addEventListener("click", () => {
  if (!currentAnalysis || simpleAssessment(currentAnalysis).state !== "clear") return;
  $("reviewed-note").textContent = "Reviewed locally for this screen only. This does not verify the sender or approve payment.";
});
updateView();

// Closing the panel should not leave an activity overlay in Gmail. The content script also has a timeout.
globalThis.window?.addEventListener("pagehide", () => {
  requestNumber++;
  challengeNumber++;
  void endBodyScan();
});
