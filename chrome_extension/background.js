// The one-click backend is direct on 8081; legacy private staging stays on 8080.
// No Cloud Run identity token, service-account key, or provider key belongs here.
const API_BASE_URL = "http://127.0.0.1:8080";
const LOCAL_API_URL = "http://127.0.0.1:8081";
const SESSION_KEY = "hooklineConnection";
const TIMEOUT_MS = 45000;
let connectionRevision = 0;

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true })
  .catch(() => console.error("Cannot enable side panel."));

function trustedPanel(sender) {
  return sender?.id === chrome.runtime.id && !sender.tab &&
    sender.url === chrome.runtime.getURL("sidepanel.html");
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message || !["ANALYZE", "CHALLENGE", "CONNECT", "DISCONNECT", "CONNECTION_STATUS"].includes(message.type)) return;
  // Gmail content scripts only extract/highlight. They cannot initiate backend calls.
  if (!trustedPanel(sender)) {
    sendResponse({ ok: false, error: "Open the Dobby’s Catch side panel to run this action." });
    return;
  }
  (async () => {
    try {
      if (message.type === "CONNECT") {
        const revision = ++connectionRevision;
        await chrome.storage.session.remove(SESSION_KEY);
        const token = typeof message.token === "string" ? message.token.trim() : "";
        if (!token || token.length > 512 || /[\r\n]/.test(token)) throw new Error("Enter the demo token privately in this panel.");
        if (message.endpoint && !["local", "staging"].includes(message.endpoint)) throw new Error("Choose a supported local connection.");
        const endpoint = message.endpoint === "local" ? LOCAL_API_URL : API_BASE_URL;
        const allowAI = message.allowAI === true;
        if (allowAI && endpoint !== LOCAL_API_URL) throw new Error("Tinker permission applies only to the one-click local backend.");
        const connection = { token, endpoint, allowAI };
        const health = await checkHealth(connection);
        connection.model = health.model.analyze;
        if (revision !== connectionRevision) throw new Error("Connection was cancelled.");
        await chrome.storage.session.set({ [SESSION_KEY]: connection });
        sendResponse({ ok: true, connected: true, endpoint, allowAI });
        return;
      }
      if (message.type === "DISCONNECT") {
        connectionRevision++;
        await chrome.storage.session.remove(SESSION_KEY);
        sendResponse({ ok: true, connected: false });
        return;
      }
      const connection = (await chrome.storage.session.get(SESSION_KEY))[SESSION_KEY];
      if (message.type === "CONNECTION_STATUS") {
        sendResponse({ ok: true, connected: Boolean(connection?.token), endpoint: connection?.endpoint || API_BASE_URL, allowAI: connection?.allowAI === true });
        return;
      }
      const mocked = message.demo === true;
      if (!mocked && !connection?.token) throw new Error("Connect the demo backend first, or choose Try demo for local pattern rules.");
      const result = mocked
        ? message.type === "ANALYZE" ? mockAnalyze(message.email) : mockChallenge(message)
        : await callBackend(message, connection);
      sendResponse({ ok: true, data: result, mocked });
    } catch (error) {
      sendResponse({ ok: false, error: String(error?.message || error) });
    }
  })();
  return true;
});

async function request(path, connection, payload) {
  const endpoint = connection.endpoint || API_BASE_URL;
  if (![API_BASE_URL, LOCAL_API_URL].includes(endpoint) || connection.allowAI && endpoint !== LOCAL_API_URL) throw new Error("Unsupported connection. Reconnect in the panel.");
  let response;
  try {
    response = await fetch(`${endpoint}${path}`, {
      method: payload ? "POST" : "GET",
      headers: { "Content-Type": "application/json", "X-Demo-Token": connection.token,
        ...(connection.allowAI ? { "X-Require-Tinker": "1" } : { "X-Require-Rules-Only": "1" }) },
      ...(payload ? { body: JSON.stringify(payload) } : {}),
      credentials: "omit",
      redirect: "error", // Never forward the token or email to another destination.
      cache: "no-store",
      signal: AbortSignal.timeout(TIMEOUT_MS)
    });
  } catch (error) {
    if (error?.name === "TimeoutError" || error?.name === "AbortError") throw new Error("Backend request timed out. No result was accepted; check the demo window before retrying.");
    throw new Error("Cannot reach the backend. Run Start-Demo for local mode, or start the legacy staging proxy; check Chrome's local-network permission if prompted.");
  }
  if (!response.ok) {
    const detail = {
      401: "The demo token is missing or incorrect.",
      403: "Cloud Run access was denied. Check the proxy's signed-in account and existing invoker access.",
      409: "Backend mode does not match your permission. Reconnect with the intended mode; no email was analyzed.",
      422: "The backend rejected the email or finding. No assessment was accepted.",
      503: "The backend is not ready or its demo token is not configured."
    }[response.status];
    throw new Error(detail || `Backend returned HTTP ${response.status}.`);
  }
  try { return await response.json(); }
  catch { throw new Error("The backend returned invalid JSON. No assessment was accepted."); }
}

async function checkHealth(connection) {
  const data = await request("/session", connection);
  const model = data?.model?.analyze;
  const expected = connection.allowAI ? typeof model === "string" && model.startsWith("tinker:") && model.length > 7 : model === "rules-only";
  if (data?.status !== "ok" || data?.service !== "phishing-coach" ||
      !expected || data?.model?.challenge !== model || connection.model && connection.model !== model) {
    throw new Error("Backend model changed or does not match your permission. No email was sent; reconnect.");
  }
  return data;
}

async function callBackend(message, connection) {
  const revision = connectionRevision;
  await checkHealth(connection);
  if (revision !== connectionRevision) throw new Error("Connection changed. No email was sent.");
  const isAnalyze = message.type === "ANALYZE";
  if (!isAnalyze && (!message.finding?.id || !message.finding?.evidence)) throw new Error("Select the original finding before challenging it.");
  const data = await request(isAnalyze ? "/analyze" : "/challenge", connection,
    isAnalyze ? message.email : { email: message.email, finding: message.finding, user_context: message.context });
  if (data?.model !== (connection.model || "rules-only")) throw new Error("Unexpected or unavailable backend model. No result was accepted.");
  if (isAnalyze) {
    if (data.email_id !== message.email?.email_id || !Array.isArray(data.findings) ||
        typeof data.analysis_complete !== "boolean" || !Array.isArray(data.limitations) ||
        !data.findings.every(f => f && typeof f.id === "string" && f.evidence && typeof f.explanation === "string")) {
      throw new Error("Incomplete or mismatched analysis response. No assessment was accepted.");
    }
  } else if (data.finding_id !== message.finding.id ||
      !["still_concerning", "less_concerning"].includes(data.assessment) ||
      typeof data.still_unresolved !== "string" || typeof data.next_action !== "string" ||
      typeof data.message !== "string") {
    throw new Error("Incomplete or mismatched challenge response. No reassessment was accepted.");
  }
  return data;
}

function mockAnalyze(email) {
  if (!email?.blocks?.length) throw new Error("No email text available to analyze.");
  const findings = [];
  const rules = [
    {
      pattern: /\b(?:change|update|replace)\s+(?:my|our|the)?\s*(?:salary|payroll|direct deposit|bank|payment)\s+(?:account|details|information)\b(?:\s+(?:today|immediately))?/i,
      category: "payment_change",
      title: "Payment details change",
      explanation: "The message asks to alter financial or payroll details. Attackers may impersonate employees or vendors to redirect payments.",
      next_action: "Confirm the request through your company's existing payroll or payment approval process."
    },
    {
      pattern: /\b(?:urgent|immediately|right away|within 24 hours|by end of day)\b/i,
      category: "urgency",
      title: "Time pressure",
      explanation: "Urgency can pressure you to act before checking the request. Urgent language alone does not prove phishing.",
      next_action: "Take time to verify the request through a trusted, separate channel."
    },
    {
      pattern: /\b(?:password|verification code|one-time code|security code)\b/i,
      category: "credentials",
      title: "Sensitive credential reference",
      explanation: "The message mentions information that attackers may try to obtain. Its presence is a signal to examine the context.",
      next_action: "Do not share passwords or sign-in codes in response to an unverified email."
    }
  ];

  for (const block of email.blocks) {
    for (const rule of rules) {
      const match = String(block.text || "").match(rule.pattern);
      if (!match) continue;
      if (findings.some((finding) => finding.category === rule.category)) continue;
      findings.push({
        id: `f${findings.length + 1}`,
        category: rule.category,
        title: rule.title,
        evidence: { block_id: block.id, quote: match[0] },
        explanation: rule.explanation,
        next_action: rule.next_action
      });
    }
  }

  return {
    email_id: email.email_id,
    model: "local-demo",
    analysis_complete: false,
    limitations: ["Local demonstration patterns only. Sender identity, headers, attachments and link destinations are not verified."],
    findings,
    summary: findings.length
      ? `${findings.length} warning sign${findings.length === 1 ? "" : "s"} identified for your review.`
      : "No warning signs matched the demo rules. This is not a safety determination.",
    disclaimer: "No warning signs found does not mean the email is safe."
  };
}

function mockChallenge(message) {
  if (!String(message.context || "").trim()) throw new Error("Enter additional context.");
  return {
    finding_id: message.finding?.id,
    explanation: "Your context may make the request less unexpected. It does not independently verify the sender or authorize changing payment details.",
    next_action: "Confirm the request through your organization's existing approval procedure."
  };
}
