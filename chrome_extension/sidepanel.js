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
  requestNumber++;
  currentEmail = null;
  currentFindings = [];
  selectedFindingId = null;
  currentMode = null;
  setEmail(null);
  resetHook();
  $("results").hidden = true;
  $("challenge-section").hidden = true;
  $("practice").hidden = true;
  $("challenge-result").textContent = "";
  $("practice-feedback").textContent = "";
  setStatus(status);
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
  await clearGmailHighlight();
  const myRequest = ++requestNumber;
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
  setStatus("Analyzing selected message…");
  $("analyze").disabled = true;
  try {
    const response = await chrome.runtime.sendMessage({ type: "ANALYZE", email });
    if (myRequest !== requestNumber) return;
    if (!response?.ok) throw new Error(response?.error || "No analysis returned.");
    const analysis = response.data;
    if (analysis.email_id !== email.email_id) throw new Error("Backend response email ID does not match the selected email.");
    currentFindings = Array.isArray(analysis.findings) ? analysis.findings : [];
    renderResults(analysis, response.mocked);
    setStatus(response.mocked ? "Mock analysis complete. No AI was called." : "Analysis complete.");
  } catch (error) {
    if (myRequest === requestNumber) setStatus(`Analysis failed: ${error.message}`, true);
  } finally {
    if (myRequest === requestNumber) $("analyze").disabled = false;
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
    ? "Selected clue. Hookline is locating its exact text in Gmail."
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
  renderVerdictBox(analysis);
  $("warning-total").textContent = String(count);
  $("count").textContent = `warning sign${count === 1 ? "" : "s"}`;
  $("summary").textContent = analysis.summary || "Review the findings and evidence below.";
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
  $("mode").textContent = mocked ? "MOCK AI" : "LIVE AI";
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
  try {
    const tab = await activeTab();
    if (!tab?.id) throw new Error("No active browser tab was found.");
    // Do not depend on tab.url: Chrome can hide that field without explicit grants.
    // Only the Gmail content script responds to EXTRACT_EMAIL.
    const response = await chrome.tabs.sendMessage(tab.id, { type: "EXTRACT_EMAIL" });
    if (!response?.ok) throw new Error(response?.error || "Could not read email.");
    await analyzeEmail(response.email, "gmail", tab.id);
  } catch (error) {
    // Prevent a previously displayed demo from looking like an analysis of Gmail.
    await clearGmailHighlight();
    clearResults();
    const missingReceiver = /Receiving end does not exist|Could not establish connection/i.test(String(error?.message || ""));
    setStatus(missingReceiver
      ? "Hookline could not connect to Gmail. Make sure Gmail is active, refresh the Gmail tab, and try again."
      : `Could not read the message: ${error.message}`, true);
  }
});

$("demo").addEventListener("click", () => analyzeEmail(DEMO_EMAIL, "demo"));

$("challenge").addEventListener("click", async () => {
  const context = $("challenge-text").value.trim();
  if (!context) {
    $("challenge-result").textContent = "Please enter the context you want the model to consider.";
    return;
  }
  const selectedFinding = currentFindings.find((item) => item.id === selectedFindingId)
    || currentFindings[0];
  if (!currentEmail || !selectedFinding) return;
  const myRequest = requestNumber;
  $("challenge-result").textContent = "Reconsidering…";
  try {
    const response = await chrome.runtime.sendMessage({
      type: "CHALLENGE", email: currentEmail, finding_id: selectedFinding.id, context
    });
    if (myRequest !== requestNumber || selectedFindingId !== selectedFinding.id && selectedFindingId !== null) return;
    if (!response?.ok) throw new Error(response?.error || "No response.");
    $("challenge-result").textContent = `${response.mocked ? "Mock response: " : ""}${response.data.explanation}\nNext step: ${response.data.next_action}`;
  } catch (error) {
    if (myRequest === requestNumber) $("challenge-result").textContent = `Challenge failed: ${error.message}`;
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
  if (currentMode === "gmail" && currentTabId === sender.tab?.id && message.email_id !== currentEmail?.email_id) {
    clearResults("Different email opened. Click Analyze open email for fresh results.");
  }
});
chrome.tabs.onActivated.addListener(({ tabId }) => {
  if (currentMode === "gmail" && currentTabId !== tabId) {
    clearResults("Tab changed. Analyze the email in your active tab.");
  }
});

setStatus("Open Gmail, select one message, and click Analyze open email. Or try the demo.");
