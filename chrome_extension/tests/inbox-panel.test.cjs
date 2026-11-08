const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class El {
  constructor() { this.children = []; this.handlers = {}; this.attrs = {}; this.hidden = false; this.disabled = false; this.textContent = ''; this.classList = { toggle() {} }; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(key, value) { this.attrs[key] = value; }
  addEventListener(name, fn) { this.handlers[name] = fn; }
  focus() { this.focused = true; }
}
const result = {
  ok: true, snapshot_id: 'inbox-1', checked: 3, visible_total: 3, missing_subjects: 0,
  flagged: [{ row_id: 'inbox-1-0', subject: '<img src=x> Urgent', signals: ['Time pressure'] }]
};
const tick = () => new Promise(resolve => setImmediate(resolve));
function panel(send = async () => result) {
  const elements = {}, calls = [], events = {};
  let tabId = 1;
  const get = id => elements[id] ||= new El();
  const ctx = {
    document: { getElementById: get, createElement: () => new El() },
    window: { addEventListener: (name, fn) => events[name] = fn },
    chrome: {
      tabs: {
        query: async () => [{ id: tabId }],
        sendMessage: async (id, message) => { calls.push({ id, ...message }); return send(message); },
        onActivated: { addListener: fn => events.tab = fn }
      },
      runtime: { onMessage: { addListener: fn => events.message = fn } }
    }
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'inbox-panel.js'), 'utf8'), ctx);
  return { get, calls, events, changeTab: id => { tabId = id; events.tab({ tabId: id }); } };
}

test('title list is explicit, text-only, local and separately opens a captured row', async () => {
  const p = panel(async message => message.type === 'PRECHECK_INBOX' ? result : { ok: true });
  assert.equal(p.calls.length, 0);
  await p.get('inbox-check').handlers.click();
  const button = p.get('inbox-list').children[0].children[0];
  assert.equal(button.children[0].textContent, '<img src=x> Urgent');
  assert.match(p.get('inbox-status').textContent, /not a safety determination/);
  await button.handlers.click();
  const open = p.calls.find(call => call.type === 'OPEN_INBOX_ROW');
  assert.equal(open.snapshot_id, 'inbox-1');
  assert.equal(open.row_id, 'inbox-1-0');
  assert.equal(p.get('inbox-list').children.length, 0);
  assert.equal(p.get('analyze').focused, true);
  assert.ok(p.calls.every(call => ['PRECHECK_INBOX', 'OPEN_INBOX_ROW', 'CLEAR_INBOX_MARKS'].includes(call.type)));
});

test('zero matches and incomplete visible coverage never claim safety', async () => {
  const p = panel(async () => ({ ...result, flagged: [], checked: 100, visible_total: 104, missing_subjects: 2 }));
  await p.get('inbox-check').handlers.click();
  assert.match(p.get('inbox-status').textContent, /0 titles flagged/);
  assert.match(p.get('inbox-status').textContent, /first 100 of 104/);
  assert.match(p.get('inbox-status').textContent, /2 row\(s\) had no readable subject/);
  assert.match(p.get('inbox-status').textContent, /not a safety determination/);
});

test('tab change discards a pending title response and clears only its marks', async () => {
  let finish;
  const p = panel(message => message.type === 'PRECHECK_INBOX' ? new Promise(resolve => finish = resolve) : { ok: true });
  const pending = p.get('inbox-check').handlers.click();
  await tick(); p.changeTab(2); finish(result); await pending;
  assert.equal(p.get('inbox-list').children.length, 0);
  assert.equal(p.get('inbox-check').disabled, false);
  const clear = p.calls.find(call => call.type === 'CLEAR_INBOX_MARKS');
  assert.equal(clear.id, 1); assert.equal(clear.snapshot_id, 'inbox-1');
});

test('navigation invalidates a pending title response', async () => {
  let finish;
  const p = panel(message => message.type === 'PRECHECK_INBOX' ? new Promise(resolve => finish = resolve) : { ok: true });
  const pending = p.get('inbox-check').handlers.click();
  await tick(); p.events.message({ type: 'INBOX_CHANGED', snapshot_id: 'inbox-1' }, { tab: { id: 1 } });
  finish(result); await pending;
  assert.equal(p.get('inbox-list').children.length, 0);
  assert.equal(p.get('inbox-check').disabled, false);
  assert.match(p.get('inbox-status').textContent, /view changed/);
});

test('Clear and newer checks cannot open a stale captured subject', async () => {
  let count = 0;
  const p = panel(async message => message.type === 'PRECHECK_INBOX' ? { ...result, snapshot_id: `inbox-${++count}` } : { ok: true });
  await p.get('inbox-check').handlers.click();
  const old = p.get('inbox-list').children[0].children[0];
  p.get('inbox-clear').handlers.click();
  await p.get('inbox-check').handlers.click();
  await old.handlers.click();
  assert.equal(p.calls.filter(call => call.type === 'OPEN_INBOX_ROW').length, 0);
  assert.equal(p.get('inbox-list').children.length, 1);
});

test('failed row opening clears stale list and reports the need to check again', async () => {
  const p = panel(async message => message.type === 'PRECHECK_INBOX' ? result : { ok: false, error: 'The list changed. Check again.' });
  await p.get('inbox-check').handlers.click();
  await p.get('inbox-list').children[0].children[0].handlers.click();
  assert.equal(p.get('inbox-list').children.length, 0);
  assert.match(p.get('inbox-status').textContent, /list changed/);
  assert.equal(p.get('analyze').focused, undefined);
});

test('failed or malformed responses re-enable the title check without results', async () => {
  for (const response of [{ ok: false, error: 'Unavailable' }, { ok: true, snapshot_id: 'bad' }]) {
    const p = panel(async () => response);
    await p.get('inbox-check').handlers.click();
    assert.equal(p.get('inbox-check').disabled, false);
    assert.equal(p.get('inbox-list').children.length, 0);
    assert.match(p.get('inbox-status').textContent, /Title check unavailable/);
  }
});
