const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class El {
  constructor(text = '') { this.textContent = text; this.children = []; this.attrs = {}; this.style = {setProperty(k,v){this[k]=v}}; this.isConnected = true; this.hidden = false; this.events = {}; }
  addEventListener(type, fn) { (this.events[type] ||= new Set()).add(fn); }
  removeEventListener(type, fn) { this.events[type]?.delete(fn); }
  emit(type, extra = {}) { for (const fn of this.events[type] || []) fn({target:this, ...extra}); }
  append(...nodes) { for (const node of nodes) { this.children.push(node); node.parent = this; } }
  after(node) { this.parent.append(node); }
  remove() { if (this.parent) this.parent.children = this.parent.children.filter(x => x !== this); this.isConnected = false; }
  getClientRects() { return this.hidden || !this.isConnected ? [] : [1]; }
  setAttribute(k,v) { this.attrs[k] = v; }
  getAttribute(k) { return this.attrs[k] || null; }
  getBoundingClientRect() { return {left:30,top:60,right:630,bottom:1000}; }
}
function fixture(subjects = [], reducedMotion = false, stableIds = false) {
  const rows = subjects.map((text, index) => {
    const row = new El(); if (stableIds) row.setAttribute('data-legacy-thread-id', (0x123456789abcdef0n + BigInt(index)).toString(16)); const subject = new El(text); row.append(subject);
    row.querySelector = s => s === 'span.bog' ? subject : null;
    row.click = () => row.clicked = true;
    return row;
  });
  const body = new El('Please update our bank details.'); body.innerText = body.textContent;
  body.closest = () => ({querySelector:()=>null}); body.querySelectorAll = () => [];
  const root = new El(), head = new El(); let bodyVisible = false; let messageListener;
  const sent = [], timers = new Map(), events = {}; let clock = 0;
  const motion = {matches:reducedMotion, events:new Set(), addEventListener:(_, fn)=>motion.events.add(fn), removeEventListener:(_, fn)=>motion.events.delete(fn)};
  const document = {
    visibilityState:'visible', addEventListener:(type,fn)=>{(events[type] ||= new Set()).add(fn)},
    head, body:root, documentElement:root,
    getElementById:id=>head.children.find(x=>x.id===id), createElement:()=>new El(),
    querySelectorAll:s=>s === 'tr.zA' ? rows : s === '.a3s' && bodyVisible ? [body] : [],
    querySelector:()=>({textContent:'Test subject'})
  };
  const ctx = {document,location:{hash:'#inbox'},window:{innerWidth:900,innerHeight:700,getSelection:()=>null,matchMedia:()=>motion,
    addEventListener:(type,fn)=>{(events[type] ||= new Set()).add(fn)},removeEventListener:(type,fn)=>events[type]?.delete(fn)},
    chrome:{runtime:{id:'hookline',getURL:p=>'chrome-extension://hookline/'+p,
      onMessage:{addListener:fn=>messageListener=fn},sendMessage:async m=>sent.push(m)}},
    MutationObserver:class{observe(){}},setTimeout:(fn,ms)=>{const id=++clock;timers.set(id,{fn,ms});return id},clearTimeout:id=>timers.delete(id)};
  vm.createContext(ctx);
  const code = fs.readFileSync(path.join(__dirname,'..','content.js'),'utf8').replace(/  checkEmailChange\(\);\r?\n\}\)\(\);/, '  globalThis.testAPI = { extractEmail, subjectSignals, checkEmailChange };\n})();');
  vm.runInContext(code, ctx);
  const trusted = {id:'hookline',url:'chrome-extension://hookline/sidepanel.html'};
  const message = (m,sender=trusted) => { let result;messageListener(m,sender,r=>result=r);return result };
  const messageAsync = m => new Promise(resolve => { assert.equal(messageListener(m,trusted,resolve),true); });
  const check = async () => { const start=message({type:'PRECHECK_INBOX'}); if(!start.ok) return start; const pending=messageAsync({type:'FINISH_INBOX_SCAN',snapshot_id:start.snapshot_id}); for(const overlay of [...root.children]) if(overlay.className==='hookline-body-scan') overlay.children[0].emit('animationend',{animationName:'hookline-body-sweep'}); return pending; };
  return {ctx,rows,body,head,root,sent,timers,events,motion,message,messageAsync,check,showBody:()=>bodyVisible=true};
}
test('subject precheck runs only on request, flags English and Chinese clues, sends no data out',async()=>{
  const f=fixture(['Team lunch','URGENT: verify your account','變更銀行帳戶通知']);
  assert.equal(f.sent.length,0); assert.equal(f.rows[1].children.length,1);
  const r=await f.check();
  assert.equal(r.checked,3);assert.equal(r.flagged.length,2);assert.equal(r.flagged[0].signals.length,2);
  assert.deepEqual(Object.keys(r.flagged[0]).sort(),['row_id','signals','subject']);
  assert.equal(f.rows[0].children.length,1);assert.equal(f.rows[1].children.length,2);assert.equal(f.sent.length,0);
});
test('no matched subject never means safe and produces no green marker',async()=>{
  const f=fixture(['Project update']); const r=await f.check();
  assert.equal(r.flagged.length,0);assert.equal(f.rows[0].children.length,1);
  assert.equal('safe' in r,false);assert.equal('verdict' in r,false);
});
test('repeated title checks replace markers and reject previous row tokens',async()=>{
  const f=fixture(['Urgent']); const a=await f.check(),b=await f.check();
  assert.equal(f.rows[0].children.length,2);assert.notEqual(a.snapshot_id,b.snapshot_id);
  assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:a.snapshot_id,row_id:a.flagged[0].row_id}).ok,false);
  assert.equal(f.rows[0].clicked,undefined);
});
test('only a current flagged row opens, with no backend request',async()=>{
  const f=fixture(['Urgent']); const r=await f.check();
  assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id}).ok,true);
  assert.equal(f.rows[0].clicked,true);assert.equal(f.sent.length,0);
});
test('rows without stable IDs reject changed subject, order or route without guessing',async()=>{
  for (const change of [f=>f.rows[0].children[0].textContent='Other', f=>f.rows.reverse(),f=>f.ctx.location.hash='#sent']) {
    const f=fixture(['Urgent','Normal']);const r=await f.check();change(f);
    assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id}).ok,false);
    assert.ok(f.rows.every(row=>!row.clicked && row.children.length===2 || !row.clicked && row.children.length===1));
    assert.equal(f.sent.some(m=>m.type==='INBOX_CHANGED'),false);
  }
});
test('subject content stays text and limits/missing subjects are explicit',async()=>{
  const f=fixture(['<img src=x onerror=alert(1)> urgent','',...Array(100).fill('Normal')]);const r=await f.check();
  assert.equal(r.checked,100);assert.equal(r.visible_total,102);assert.equal(r.missing_subjects,1);
  assert.match(r.flagged[0].subject,/<img/);assert.equal(f.rows[0].children[0].textContent,r.flagged[0].subject);
});
test('title check excludes hidden rows and refuses the open-message view',async()=>{
  const f=fixture(['Urgent','Password']);f.rows[1].hidden=true;
  assert.equal((await f.check()).checked,1);f.showBody();
  assert.equal((await f.check()).ok,false);assert.equal(f.rows[0].children.length,1);
});
test('clear is snapshot-bound so a late old cleanup cannot erase newer markers',async()=>{
  const f=fixture(['Urgent']);const a=await f.check(),b=await f.check();
  f.message({type:'CLEAR_INBOX_MARKS',snapshot_id:a.snapshot_id});assert.equal(f.rows[0].children.length,2);
  f.message({type:'CLEAR_INBOX_MARKS',snapshot_id:b.snapshot_id});assert.equal(f.rows[0].children.length,1);
});
test('page-script or content-script callers cannot start scans or local inbox actions',async()=>{
  const f=fixture(['Urgent']);for(const sender of [{},{id:'hookline',tab:{id:1},url:'https://mail.google.com'}]) {
    assert.equal(f.message({type:'PRECHECK_INBOX'},sender).ok,false);
  } assert.equal(f.rows[0].children.length,1);
});
test('body animation is separate from email DOM, viewport-clipped and reduced-motion aware',async()=>{
  const f=fixture();f.showBody();const email=f.ctx.testAPI.extractEmail();const before=f.body.textContent;
  assert.equal(f.message({type:'START_BODY_SCAN',email_id:email.email_id,scan_id:'a'}).ok,true);
  assert.equal(f.root.children.length,1);assert.equal(f.body.textContent,before);assert.equal(f.body.children.length,0);
  assert.equal(f.root.children[0].style.height,'640px');assert.equal(f.root.children[0].attrs['aria-hidden'],'true');
  assert.match(f.head.children[0].textContent,/prefers-reduced-motion:reduce/);
  assert.match(f.head.children[0].textContent,/pointer-events:none/);
  assert.ok([...f.timers.values()].some(x=>x.ms===46000));
});
test('wrong email cannot start scan; late stop cannot remove newer scan; matching stop cleans up',async()=>{
  const f=fixture();f.showBody();const email=f.ctx.testAPI.extractEmail();
  assert.equal(f.message({type:'START_BODY_SCAN',email_id:'wrong',scan_id:'a'}).ok,false);assert.equal(f.root.children.length,0);
  f.message({type:'START_BODY_SCAN',email_id:email.email_id,scan_id:'a'});f.message({type:'START_BODY_SCAN',email_id:email.email_id,scan_id:'b'});
  f.message({type:'STOP_BODY_SCAN',scan_id:'a'});assert.equal(f.root.children.length,1);
  f.message({type:'STOP_BODY_SCAN',scan_id:'b'});assert.equal(f.root.children.length,0);assert.equal(f.events.scroll.size,0);assert.equal(f.timers.size,0);
});
test('navigation and animation timeout remove overlays without retaining message data',async()=>{
  const f=fixture();f.showBody();const email=f.ctx.testAPI.extractEmail();
  f.message({type:'START_BODY_SCAN',email_id:email.email_id,scan_id:'a'});
  [...f.events.hashchange][0]();assert.equal(f.root.children.length,0);
  f.message({type:'START_BODY_SCAN',email_id:f.ctx.testAPI.extractEmail().email_id,scan_id:'b'});
  [...f.timers.values()].find(x=>x.ms===46000).fn();assert.equal(f.root.children.length,0);
});

const start = f => {
  f.showBody();const email = f.ctx.testAPI.extractEmail();
  assert.equal(f.message({type:'START_BODY_SCAN',email_id:email.email_id,scan_id:'a'}).ok,true);
  return {type:'FINISH_BODY_SCAN',email_id:email.email_id,scan_id:'a'};
};
const tick = () => new Promise(resolve => setImmediate(resolve));
const endSweep = f => f.root.children[0].children[0].emit('animationend',{animationName:'hookline-body-sweep'});
test('fast backend completion waits for the actual finite sweep before removing overlay',async()=>{
  const f=fixture(),request=start(f);let done=false;
  const pending=f.messageAsync(request).then(r=>{done=true;return r});await tick();
  assert.equal(done,false);assert.equal(f.root.children.length,1);
  // Unrelated/bubbled animation events must not complete the sweep.
  f.root.children[0].children[0].emit('animationend',{animationName:'other'});await tick();assert.equal(done,false);
  endSweep(f);const r=await pending;
  assert.equal(r.completed,true);assert.equal(r.email_id,request.email_id);assert.equal(r.scan_id,'a');
  assert.equal(f.root.children.length,0);assert.equal(f.timers.size,0);assert.equal(f.motion.events.size,0);
  assert.match(f.head.children[0].textContent,/1600ms linear 1 forwards/);
  assert.doesNotMatch(f.head.children[0].textContent,/linear infinite/);
});
test('slow backend keeps a static indicator after one sweep and completes without another delay',async()=>{
  const f=fixture(),request=start(f);endSweep(f);
  assert.equal(f.root.children.length,1);assert.equal(f.root.children[0].children[0].hidden,true);
  assert.equal((await f.messageAsync(request)).completed,true);assert.equal(f.root.children.length,0);
});
test('missing animation event terminates the visual at the 1900ms fallback before success',async()=>{
  const f=fixture(),request=start(f);const line=f.root.children[0].children[0];const pending=f.messageAsync(request);
  [...f.timers.values()].find(x=>x.ms===1900).fn();assert.equal(line.hidden,true);assert.equal(line.style.animation,'none');
  assert.equal((await pending).completed,true);assert.equal(f.timers.size,0);
});
test('reduced motion skips the presentation delay and preference changes end it immediately',async()=>{
  for(const initiallyReduced of [true,false]) {
    const f=fixture([],initiallyReduced),request=start(f);const pending=f.messageAsync(request);
    if(!initiallyReduced) for(const fn of [...f.motion.events]) fn({matches:true});
    assert.equal((await pending).completed,true);assert.equal(f.root.children.length,0);assert.equal(f.timers.size,0);
  }
});
test('cancel, replacement, pagehide, hidden tab and timeout settle pending finish without a result',async()=>{
  for(const cancel of [
    f=>f.message({type:'STOP_BODY_SCAN',scan_id:'a'}),
    f=>f.message({type:'START_BODY_SCAN',email_id:f.ctx.testAPI.extractEmail().email_id,scan_id:'b'}),
    f=>[...f.events.pagehide][0](),
    f=>{f.ctx.document.visibilityState='hidden';[...f.events.visibilitychange][0]()},
    f=>[...f.timers.values()].find(x=>x.ms===46000).fn()
  ]) {
    const f=fixture(),request=start(f);const pending=f.messageAsync(request);cancel(f);
    assert.equal((await pending).ok,false);
    f.message({type:'STOP_BODY_SCAN'});assert.equal(f.root.children.length,0);assert.equal(f.timers.size,0);
  }
});
test('same-route body changes are rejected before the debounced EMAIL_CHANGED notification',async()=>{
  const f=fixture(),request=start(f);const pending=f.messageAsync(request);
  f.body.innerText='A different message';endSweep(f);
  assert.equal((await pending).ok,false);assert.equal(f.root.children.length,0);
});
test('finish is scoped to the scan and email and requires a trusted side panel sender',async()=>{
  const f=fixture(),request=start(f);
  assert.equal((await f.messageAsync({...request,scan_id:'wrong'})).ok,false);
  assert.equal((await f.messageAsync({...request,email_id:'wrong'})).ok,false);
  assert.equal(f.message(request,{}).ok,false);assert.equal(f.root.children.length,1);
  f.message({type:'STOP_BODY_SCAN'});
});


test('stable captured thread IDs survive navigation, detached rows and reordered inboxes', async () => {
  const f = fixture(['Urgent: first', 'Password: second'], false, true);
  const r = await f.check();
  const open = index => f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[index].row_id});
  assert.equal(open(0).ok, true);
  assert.equal(f.ctx.location.hash, '#all/123456789abcdef0');
  [...f.events.hashchange][0]();
  f.rows.forEach(row => row.isConnected = false); f.rows.reverse();
  f.ctx.testAPI.checkEmailChange();
  assert.equal(open(1).ok, true);
  assert.equal(f.ctx.location.hash, '#all/123456789abcdef1');
  [...f.events.hashchange][0]();
  assert.equal(open(0).ok, true);
  assert.equal(f.ctx.location.hash, '#all/123456789abcdef0');
  assert.equal(f.sent.some(m => m.type === 'INBOX_CHANGED'), false);
  assert.ok(f.rows.every(row => !row.clicked));
});

test('Gmail account scope changes clear retained snapshots instead of opening another account', async () => {
  const f = fixture(['Urgent'], false, true); f.ctx.location.pathname = '/mail/u/0/';
  const r = await f.check(); f.ctx.location.pathname = '/mail/u/1/';
  assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id}).ok, false);
  assert.equal(f.ctx.location.hash, '#inbox');
  assert.equal(f.sent.at(-1).type, 'INBOX_CHANGED');
});

test('modern decimal Gmail thread metadata is converted without precision loss', async () => {
  const f = fixture(['Urgent']); f.rows[0].setAttribute('data-thread-id', '#thread-f:1781234567890123456');
  const r = await f.check();
  assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id}).ok, true);
  assert.equal(f.ctx.location.hash, '#all/' + BigInt('1781234567890123456').toString(16));
});

test('untrusted thread IDs are not interpreted as URLs or script', async () => {
  for (const id of ['https://evil.test/', 'javascript:alert(1)', '../other', 'abc#sent', '123456789abcdef0?x=1']) {
    const f = fixture(['Urgent']); f.rows[0].setAttribute('data-legacy-thread-id', id);
    const r = await f.check(); f.rows[0].isConnected = false;
    assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id}).ok, false);
    assert.equal(f.ctx.location.hash, '#inbox');
  }
});

test('selecting a new title blocks extraction of the previous body during Gmail navigation', async () => {
  const f = fixture(['Urgent: new'], false, true);
  const r = await f.check(); f.showBody();
  f.ctx.document.querySelector = () => ({textContent:'Previous message'});
  assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id}).ok, true);
  assert.match(f.message({type:'EXTRACT_EMAIL'}).error, /still opening/);
  f.ctx.document.querySelector = () => ({textContent:'Urgent: new'});
  f.body.innerText = 'New message body';
  f.body.closest = () => ({querySelector:()=>null,getAttribute:key=>key==='data-message-id'?'new-message':null});
  assert.equal(f.message({type:'EXTRACT_EMAIL'}).ok, true);
  assert.equal(f.message({type:'EXTRACT_EMAIL'}).email.subject, 'Urgent: new');
});

test('clear marks invalidates retained row tokens even while a message is open', async () => {
  const f = fixture(['Urgent'], false, true); const r = await f.check();
  f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id});
  f.message({type:'CLEAR_INBOX_MARKS',snapshot_id:r.snapshot_id});
  assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id}).ok, false);
});


test('heading-only and text-only rendering changes cannot release the previous body', async () => {
  const f = fixture(['Urgent: new'], false, true); const r = await f.check(); f.showBody();
  f.ctx.document.querySelector = () => ({textContent:'Previous message'});
  f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id});
  f.ctx.document.querySelector = () => ({textContent:'Urgent: new'});
  assert.match(f.message({type:'EXTRACT_EMAIL'}).error, /still opening/);
  f.body.innerText += ' An unrelated mutation in the previous body.';
  assert.match(f.message({type:'EXTRACT_EMAIL'}).error, /still opening/);
});

test('rapid A to B to A reselect accepts the already loaded A without a body mutation', async () => {
  const f = fixture(['Urgent A', 'Urgent B'], false, true); const r = await f.check(); f.showBody();
  f.ctx.location.hash = '#all/123456789abcdef0';
  f.ctx.document.querySelector = () => ({textContent:'Urgent A'});
  const open = i => f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[i].row_id});
  open(1); assert.match(f.message({type:'EXTRACT_EMAIL'}).error, /still opening/);
  open(0); assert.equal(f.message({type:'EXTRACT_EMAIL'}).ok, true);
  assert.equal(f.message({type:'EXTRACT_EMAIL'}).email.subject, 'Urgent A');
});

test('available Gmail thread identity must match even when duplicate subjects and body metadata change', async () => {
  const f = fixture(['Urgent same', 'Urgent same'], false, true); const r = await f.check(); f.showBody();
  f.ctx.document.querySelector = () => ({textContent:'Urgent same'});
  const container = new El(); container.querySelector = () => null;
  container.setAttribute('data-legacy-thread-id', '123456789abcdef0');
  container.setAttribute('data-message-id', 'message-A'); f.body.closest = () => container;
  f.ctx.location.hash = '#all/123456789abcdef0';
  f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[1].row_id});
  container.setAttribute('data-message-id', 'another-message-in-A');
  assert.match(f.message({type:'EXTRACT_EMAIL'}).error, /still opening/);
  container.setAttribute('data-legacy-thread-id', '123456789abcdef1');
  assert.equal(f.message({type:'EXTRACT_EMAIL'}).ok, true);
});

test('title sweep gates marks and releases all checked rows only after animation', async()=>{
 const f=fixture(['Urgent','Team lunch']); const start=f.message({type:'PRECHECK_INBOX'});
 assert.equal(f.rows[0].children.length,1);
 let done=false; const finish=f.messageAsync({type:'FINISH_INBOX_SCAN',snapshot_id:start.snapshot_id}).then(r=>{done=true;return r});
 await Promise.resolve(); assert.equal(done,false);
 f.root.children[0].children[0].emit('animationend',{animationName:'hookline-body-sweep'});
 await Promise.resolve();assert.equal(done,false);
 f.root.children[0].children[0].emit('animationend',{animationName:'wrong'});
 for(const overlay of [...f.root.children]) overlay.children[0].emit('animationend',{animationName:'hookline-body-sweep'});
 const result=await finish; assert.equal(result.items.length,2); assert.equal(result.items[1].signals.length,0);
 assert.equal(f.rows[0].children.length,2);
 assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:result.snapshot_id,row_id:result.items[1].row_id}).ok,true);
});

test('title sweeps cancel stale snapshots and clear overlays on interruption', async()=>{
 for(const cancel of [f=>f.message({type:'CLEAR_INBOX_MARKS'}), f=>{f.ctx.location.hash='#sent';[...f.events.hashchange][0]()}, f=>{f.ctx.document.visibilityState='hidden';[...f.events.visibilitychange][0]()}, f=>[...f.events.pagehide][0]()]) {
 const f=fixture(['Urgent']);const start=f.message({type:'PRECHECK_INBOX'});const pending=f.messageAsync({type:'FINISH_INBOX_SCAN',snapshot_id:start.snapshot_id});cancel(f);
 assert.equal((await pending).ok,false);assert.equal(f.root.children.length,0);assert.equal(f.rows[0].children.length,1);
 }
});
test('title watchdog revalidates subjects and account before release', async()=>{
 for(const change of [f=>f.rows[0].children[0].textContent='Changed',f=>f.ctx.location.pathname='/mail/u/1/']) {
 const f=fixture(['Urgent']);const start=f.message({type:'PRECHECK_INBOX'});const pending=f.messageAsync({type:'FINISH_INBOX_SCAN',snapshot_id:start.snapshot_id});change(f);
 [...f.timers.values()].find(t=>t.ms===1900).fn();assert.equal((await pending).ok,false);assert.equal(f.root.children.length,0);
 }
});
test('reduced motion title sweep is immediate and watchdog ends lost events', async()=>{
 for(const reduced of [true,false]) {const f=fixture(['Normal'],reduced);const start=f.message({type:'PRECHECK_INBOX'});const pending=f.messageAsync({type:'FINISH_INBOX_SCAN',snapshot_id:start.snapshot_id});
 if(!reduced) [...f.timers.values()].find(t=>t.ms===1900).fn();
 assert.equal((await pending).ok,true);assert.equal(f.root.children.length,0);}
});

test('new title check cancels old sweep and never releases its marks', async()=>{
 const f=fixture(['Urgent']);const a=f.message({type:'PRECHECK_INBOX'});const old=f.messageAsync({type:'FINISH_INBOX_SCAN',snapshot_id:a.snapshot_id});
 const b=f.message({type:'PRECHECK_INBOX'});assert.equal((await old).ok,false);assert.equal(f.root.children.length,1);assert.equal(f.rows[0].children.length,1);
 const next=f.messageAsync({type:'FINISH_INBOX_SCAN',snapshot_id:b.snapshot_id});f.root.children[0].children[0].emit('animationend',{animationName:'hookline-body-sweep'});assert.equal((await next).ok,true);
});

test('empty captured subject opens only with stable identity and waits for a new body', async()=>{
 const f=fixture([''],false,true);const r=await f.check();f.showBody();
 f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.items[0].row_id});
 assert.match(f.message({type:'EXTRACT_EMAIL'}).error,/still opening/);
 const container=new El();container.querySelector=()=>null;container.setAttribute('data-message-id','new-body');f.body.closest=()=>container;
 assert.equal(f.message({type:'EXTRACT_EMAIL'}).ok,true);
 const g=fixture(['']);const q=await g.check();assert.match(g.message({type:'OPEN_INBOX_ROW',snapshot_id:q.snapshot_id,row_id:q.items[0].row_id}).error,/subject|identifier/i);
});
test('ready snapshot loses stale row marks without losing stable navigation', async()=>{
 for(const change of [f=>f.rows[0].children[0].textContent='New subject',f=>f.rows[0].isConnected=false,f=>f.rows[0].setAttribute('data-legacy-thread-id','123456789abcdef1')]){
 const f=fixture(['Urgent'],false,true);const r=await f.check();change(f);f.ctx.testAPI.checkEmailChange();
 assert.equal(f.rows[0].children.length,1);assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.items[0].row_id}).ok,true);
 }
});

test('empty subject accepts only matching available thread identity, never changed metadata in another thread', async()=>{
 const f=fixture([''],false,true);const r=await f.check();f.showBody();
 const container=new El();container.querySelector=()=>null;container.setAttribute('data-legacy-thread-id','123456789abcdef1');container.setAttribute('data-message-id','old');f.body.closest=()=>container;
 f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.items[0].row_id});
 container.setAttribute('data-message-id','changed-in-wrong-thread');assert.match(f.message({type:'EXTRACT_EMAIL'}).error,/still opening/);
 container.setAttribute('data-legacy-thread-id','123456789abcdef0');assert.equal(f.message({type:'EXTRACT_EMAIL'}).ok,true);
});
