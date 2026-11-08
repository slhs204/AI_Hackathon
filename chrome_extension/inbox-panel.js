// Subject-only checks are initiated here, run in the Gmail tab, and never use the backend.
(() => {
  const get = id => document.getElementById(id);
  let revision = 0;
  let pendingTab = null;
  let snapshot = null;
  let pendingId = null;
  let openRequest = 0;

  const status = (text, error = false) => {
    get("inbox-status").textContent = text;
    get("inbox-status").classList.toggle("error", error);
  };
  const eraseMarks = (target) => target
    ? chrome.tabs.sendMessage(target.tabId, { type: "CLEAR_INBOX_MARKS", snapshot_id: target.id }).catch(() => {})
    : Promise.resolve();

  function reset(text) {
    revision++;
    openRequest++;
    const old = snapshot || (pendingTab !== null ? {tabId:pendingTab, id:pendingId} : null);
    snapshot = null;
    pendingTab = null;
    pendingId = null;
    get("inbox-check").disabled = false;
    get("inbox-clear").hidden = true;
    get("inbox-list").replaceChildren();
    status(text);
    void eraseMarks(old);
  }

  async function finishScan(tabId, id) {
    let timer;
    try {
      return await Promise.race([
        chrome.tabs.sendMessage(tabId, {type:"FINISH_INBOX_SCAN", snapshot_id:id}),
        new Promise((_, reject) => { timer = setTimeout(() => reject(new Error("Could not finish the title scan display. Refresh Gmail and try again.")), 2500); })
      ]);
    } finally { clearTimeout(timer); }
  }

  async function currentTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab?.id;
  }

  async function openItem(item, owner) {
    if (snapshot !== owner) return;
    const request = revision;
    const opening = ++openRequest;
    try {
      if (await currentTab() !== owner.tabId || request !== revision || opening !== openRequest) return;
      window.dispatchEvent(new CustomEvent("hookline:inbox-opening", { detail: { subject: item.subject } }));
      const result = await chrome.tabs.sendMessage(owner.tabId, {
        type: "OPEN_INBOX_ROW", snapshot_id: owner.id, row_id: item.row_id
      });
      if (request !== revision || opening !== openRequest) return;
      if (!result?.ok) throw new Error(result?.error || "The list changed. Check inbox titles again.");
      for (const li of get("inbox-list").children) {
        const button = li.children[0];
        button.setAttribute("aria-current", String(button.dataset.rowId === item.row_id));
      }
      status("Message selected. Wait for Gmail to show its body, then choose Analyze open email. This title list stays available; no body was sent by selecting it.");
      get("analyze").focus?.();
    } catch (error) {
      if (request !== revision || opening !== openRequest) return;
      status(error.message, true);
    }
  }

  function render(result, owner) {
    get("inbox-list").replaceChildren();
    for (const item of result.flagged) {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "inbox-item";
      button.dataset.rowId = item.row_id;
      button.setAttribute("aria-label", `Open message: ${item.subject || "(No readable subject)"}. Subject-only warning clue.`);
      const subject = document.createElement("strong");
      subject.textContent = item.subject || "(No readable subject)";
      const signals = document.createElement("span");
      signals.textContent = `⚠ ${item.signals.join(" · ")}`;
      const action = document.createElement("span");
      action.textContent = "Open message →";
      button.append(subject, signals, action);
      button.addEventListener("click", () => openItem(item, owner));
      li.append(button);
      get("inbox-list").append(li);
    }
    const count = result.flagged.length;
    status(`${count} title${count === 1 ? "" : "s"} flagged among ${result.checked} visible rows checked locally.` +
      (result.visible_total > result.checked ? ` Only the first ${result.checked} of ${result.visible_total} visible rows were checked.` : "") +
      (result.missing_subjects ? ` ${result.missing_subjects} row(s) had no readable subject.` : "") +
      " Subjects only, not a safety determination.");
    get("inbox-clear").hidden = false;
  }

  get("inbox-check").addEventListener("click", async () => {
    const previous = snapshot;
    reset("Checking visible subject lines locally…");
    const request = revision;
    get("inbox-check").disabled = true;
    get("inbox-clear").hidden = false;
    let tabId = null;
    let response = null;
    try {
      await eraseMarks(previous);
      tabId = await currentTab();
      if (request !== revision) return;
      if (!tabId) throw new Error("Open Gmail in the active tab first.");
      pendingTab = tabId;
      response = await chrome.tabs.sendMessage(tabId, { type: "PRECHECK_INBOX" });
      if (request !== revision) { if (response?.ok) await eraseMarks({tabId, id:response.snapshot_id}); return; }
      if (response?.ok && response.snapshot_id) {
        pendingId = response.snapshot_id;
        response = await finishScan(tabId, pendingId);
      }
      const stillActive = await currentTab();
      if (request !== revision || stillActive !== tabId) {
        if (response?.ok) await eraseMarks({ tabId, id: response.snapshot_id });
        return;
      }
      if (!response?.ok) throw new Error(response?.error || "Could not check the visible Gmail list.");
      if (!response.completed || response.snapshot_id !== pendingId) throw new Error("The title scan acknowledgement did not match. Check again.");
      if (!Array.isArray(response.items) || !Array.isArray(response.flagged) || !response.snapshot_id) throw new Error("The title-check response was incomplete. Refresh Gmail and try again.");
      snapshot = { tabId, id: response.snapshot_id };
      pendingTab = null;
      render(response, snapshot);
    } catch (error) {
      if (request !== revision) return;
      if (response?.ok) await eraseMarks({ tabId, id: response.snapshot_id });
      status(`Title check unavailable: ${error.message}. Make sure Gmail is active and refreshed.`, true);
    } finally {
      if (request === revision) { pendingTab = null; pendingId = null; get("inbox-check").disabled = false; }
    }
  });

  get("inbox-clear").addEventListener("click", () => reset("Local title results and row marks cleared."));
  chrome.runtime.onMessage.addListener((message, sender) => {
    if (message?.type !== "INBOX_CHANGED") return;
    if (snapshot?.tabId === sender.tab?.id && snapshot.id === message.snapshot_id || pendingTab === sender.tab?.id) {
      reset("The Gmail view changed. Return to the inbox and check titles again. No body was analyzed.");
    }
  });
  chrome.tabs.onActivated.addListener(({ tabId }) => {
    if (snapshot && snapshot.tabId !== tabId || pendingTab !== null && pendingTab !== tabId) {
      reset("Tab changed. Local title results were cleared; check the active Gmail inbox again.");
    }
  });
  window.addEventListener("pagehide", () => reset("Title check closed."));
})();
