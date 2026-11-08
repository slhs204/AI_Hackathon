const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class El {
  constructor(text = '') { this.textContent = text; this.children = []; this.attrs = {}; this.style = {setProperty(k,v){this[k]=v}}; this.isConnected = true; this.hidden = false; }
  append(...nodes) { for (const node of nodes) { this.children.push(node); node.parent = this; } }
  after(node) { this.parent.append(node); }
  remove() { if (this.parent) this.parent.children = this.parent.children.filter(x => x !== this); this.isConnected = false; }
  getClientRects() { return this.hidden || !this.isConnected ? [] : [1]; }
  setAttribute(k,v) { this.attrs[k] = v; }
  getBoundingClientRect() { return {left:30,top:60,right:630,bottom:1000}; }
}
function fixture(subjects = []) {
  const rows = subjects.map(text => {
    const row = new El(); const subject = new El(text); row.append(subject);
    row.querySelector = s => s === 'span.bog' ? subject : null;
    row.click = () => row.clicked = true;
    return row;
  });
  const body = new El('Please update our bank details.'); body.innerText = body.textContent;
  body.closest = () => ({querySelector:()=>null}); body.querySelectorAll = () => [];
  const root = new El(), head = new El(); let bodyVisible = false; let messageListener;
  const sent = [], timers = new Map(), events = {}; let clock = 0;
  const document = {
    head, body:root, documentElement:root,
    getElementById:id=>head.children.find(x=>x.id===id), createElement:()=>new El(),
    querySelectorAll:s=>s === 'tr.zA' ? rows : s === '.a3s' && bodyVisible ? [body] : [],
    querySelector:()=>({textContent:'Test subject'})
  };
  const ctx = {document,location:{hash:'#inbox'},window:{innerWidth:900,innerHeight:700,getSelection:()=>null,
    addEventListener:(type,fn)=>{(events[type] ||= new Set()).add(fn)},removeEventListener:(type,fn)=>events[type]?.delete(fn)},
    chrome:{runtime:{id:'hookline',getURL:p=>'chrome-extension://hookline/'+p,
      onMessage:{addListener:fn=>messageListener=fn},sendMessage:async m=>sent.push(m)}},
    MutationObserver:class{observe(){}},setTimeout:(fn,ms)=>{const id=++clock;timers.set(id,{fn,ms});return id},clearTimeout:id=>timers.delete(id)};
  vm.createContext(ctx);
  const code = fs.readFileSync(path.join(__dirname,'..','content.js'),'utf8').replace('  checkEmailChange();\n})();', '  globalThis.testAPI = { extractEmail, subjectSignals, checkEmailChange };\n})();');
  vm.runInContext(code, ctx);
  const trusted = {id:'hookline',url:'chrome-extension://hookline/sidepanel.html'};
  const message = (m,sender=trusted) => { let result;messageListener(m,sender,r=>result=r);return result };
  return {ctx,rows,body,head,root,sent,timers,events,message,showBody:()=>bodyVisible=true};
}
test('subject precheck runs only on request, flags English and Chinese clues, sends no data out',()=>{
  const f=fixture(['Team lunch','URGENT: verify your account','變更銀行帳戶通知']);
  assert.equal(f.sent.length,0); assert.equal(f.rows[1].children.length,1);
  const r=f.message({type:'PRECHECK_INBOX'});
  assert.equal(r.checked,3);assert.equal(r.flagged.length,2);assert.equal(r.flagged[0].signals.length,2);
  assert.deepEqual(Object.keys(r.flagged[0]).sort(),['row_id','signals','subject']);
  assert.equal(f.rows[0].children.length,1);assert.equal(f.rows[1].children.length,2);assert.equal(f.sent.length,0);
});
test('no matched subject never means safe and produces no green marker',()=>{
  const f=fixture(['Project update']); const r=f.message({type:'PRECHECK_INBOX'});
  assert.equal(r.flagged.length,0);assert.equal(f.rows[0].children.length,1);
  assert.equal('safe' in r,false);assert.equal('verdict' in r,false);
});
test('repeated title checks replace markers and reject previous row tokens',()=>{
  const f=fixture(['Urgent']); const a=f.message({type:'PRECHECK_INBOX'}),b=f.message({type:'PRECHECK_INBOX'});
  assert.equal(f.rows[0].children.length,2);assert.notEqual(a.snapshot_id,b.snapshot_id);
  assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:a.snapshot_id,row_id:a.flagged[0].row_id}).ok,false);
  assert.equal(f.rows[0].clicked,undefined);
});
test('only a current flagged row opens, with no backend request',()=>{
  const f=fixture(['Urgent']); const r=f.message({type:'PRECHECK_INBOX'});
  assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id}).ok,true);
  assert.equal(f.rows[0].clicked,true);assert.equal(f.sent.length,0);
});
test('changed subject, row order or route invalidates marks before opening',()=>{
  for (const change of [f=>f.rows[0].children[0].textContent='Other', f=>f.rows.reverse(),f=>f.ctx.location.hash='#sent']) {
    const f=fixture(['Urgent','Normal']);const r=f.message({type:'PRECHECK_INBOX'});change(f);
    assert.equal(f.message({type:'OPEN_INBOX_ROW',snapshot_id:r.snapshot_id,row_id:r.flagged[0].row_id}).ok,false);
    assert.ok(f.rows.every(row=>!row.clicked && row.children.length===1));
    assert.equal(f.sent.at(-1).type,'INBOX_CHANGED');
  }
});
test('subject content stays text and limits/missing subjects are explicit',()=>{
  const f=fixture(['<img src=x onerror=alert(1)> urgent','',...Array(100).fill('Normal')]);const r=f.message({type:'PRECHECK_INBOX'});
  assert.equal(r.checked,100);assert.equal(r.visible_total,102);assert.equal(r.missing_subjects,1);
  assert.match(r.flagged[0].subject,/<img/);assert.equal(f.rows[0].children[0].textContent,r.flagged[0].subject);
});
test('title check excludes hidden rows and refuses the open-message view',()=>{
  const f=fixture(['Urgent','Password']);f.rows[1].hidden=true;
  assert.equal(f.message({type:'PRECHECK_INBOX'}).checked,1);f.showBody();
  assert.equal(f.message({type:'PRECHECK_INBOX'}).ok,false);assert.equal(f.rows[0].children.length,1);
});
test('clear is snapshot-bound so a late old cleanup cannot erase newer markers',()=>{
  const f=fixture(['Urgent']);const a=f.message({type:'PRECHECK_INBOX'}),b=f.message({type:'PRECHECK_INBOX'});
  f.message({type:'CLEAR_INBOX_MARKS',snapshot_id:a.snapshot_id});assert.equal(f.rows[0].children.length,2);
  f.message({type:'CLEAR_INBOX_MARKS',snapshot_id:b.snapshot_id});assert.equal(f.rows[0].children.length,1);
});
test('page-script or content-script callers cannot start scans or local inbox actions',()=>{
  const f=fixture(['Urgent']);for(const sender of [{},{id:'hookline',tab:{id:1},url:'https://mail.google.com'}]) {
    assert.equal(f.message({type:'PRECHECK_INBOX'},sender).ok,false);
  } assert.equal(f.rows[0].children.length,1);
});
test('body animation is separate from email DOM, viewport-clipped and reduced-motion aware',()=>{
  const f=fixture();f.showBody();const email=f.ctx.testAPI.extractEmail();const before=f.body.textContent;
  assert.equal(f.message({type:'START_BODY_SCAN',email_id:email.email_id,scan_id:'a'}).ok,true);
  assert.equal(f.root.children.length,1);assert.equal(f.body.textContent,before);assert.equal(f.body.children.length,0);
  assert.equal(f.root.children[0].style.height,'640px');assert.equal(f.root.children[0].attrs['aria-hidden'],'true');
  assert.match(f.head.children[0].textContent,/prefers-reduced-motion:reduce/);
  assert.match(f.head.children[0].textContent,/pointer-events:none/);
  assert.ok([...f.timers.values()].some(x=>x.ms===46000));
});
test('wrong email cannot start scan; late stop cannot remove newer scan; matching stop cleans up',()=>{
  const f=fixture();f.showBody();const email=f.ctx.testAPI.extractEmail();
  assert.equal(f.message({type:'START_BODY_SCAN',email_id:'wrong',scan_id:'a'}).ok,false);assert.equal(f.root.children.length,0);
  f.message({type:'START_BODY_SCAN',email_id:email.email_id,scan_id:'a'});f.message({type:'START_BODY_SCAN',email_id:email.email_id,scan_id:'b'});
  f.message({type:'STOP_BODY_SCAN',scan_id:'a'});assert.equal(f.root.children.length,1);
  f.message({type:'STOP_BODY_SCAN',scan_id:'b'});assert.equal(f.root.children.length,0);assert.equal(f.events.scroll.size,0);assert.equal(f.timers.size,0);
});
test('navigation and animation timeout remove overlays without retaining message data',()=>{
  const f=fixture();f.showBody();const email=f.ctx.testAPI.extractEmail();
  f.message({type:'START_BODY_SCAN',email_id:email.email_id,scan_id:'a'});
  [...f.events.hashchange][0]();assert.equal(f.root.children.length,0);
  f.message({type:'START_BODY_SCAN',email_id:f.ctx.testAPI.extractEmail().email_id,scan_id:'b'});
  [...f.timers.values()].find(x=>x.ms===46000).fn();assert.equal(f.root.children.length,0);
});
