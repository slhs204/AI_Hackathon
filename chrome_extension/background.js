// CHANGEME for backend integration: Albert should supply the deployed Cloud Run URL.
// Leave MOCK_MODE=true until the /analyze and /challenge contracts are finalized.
const MOCK_MODE = true;
const API_BASE_URL = ""; // e.g. "https://your-cloud-run-service.a.run.app"

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error("Cannot enable side panel:", error));

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!message || !["ANALYZE", "CHALLENGE"].includes(message.type)) return;

  (async () => {
    try {
      const result = MOCK_MODE
        ? message.type === "ANALYZE"
          ? mockAnalyze(message.email)
          : mockChallenge(message)
        : await callBackend(message);
      sendResponse({ ok: true, data: result, mocked: MOCK_MODE });
    } catch (error) {
      sendResponse({ ok: false, error: String(error?.message || error) });
    }
  })();
  return true; // Keep messaging alive for asynchronous replies.
});

async function callBackend(message) {
  if (!API_BASE_URL) throw new Error("Set API_BASE_URL in background.js.");
  const endpoint = message.type === "ANALYZE" ? "/analyze" : "/challenge";
  // Add the EXACT API host to manifest.json > host_permissions before enabling live mode.
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(message.type === "ANALYZE"
      ? message.email
      : { email: message.email, finding_id: message.finding_id, context: message.context })
  });
  if (!response.ok) throw new Error(`Backend returned HTTP ${response.status}`);
  return await response.json();
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
    finding_id: message.finding_id,
    explanation: "Your context may make the request less unexpected. It does not independently verify the sender or authorize changing payment details.",
    next_action: "Confirm the request through your organization's existing approval procedure."
  };
}
