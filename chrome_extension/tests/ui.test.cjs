const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
class El {
  constructor(){this.children=[];this.dataset={};this.attrs={};this.hidden=false;this.textContent='';this.value='';this.disabled=false;this.handlers={};this.classList={toggle:()=>{}};this.style={setProperty:()=>{}};}
  append(...x){this.children.push(...x)} replaceChildren(...x){this.children=x} setAttribute(k,v){this.attrs[k]=v} addEventListener(k,fn){this.handlers[k]=fn} querySelectorAll(){return []}
}
const finding={id:'f1',category:'payment_or_data_request',evidence:{kind:'text',block_id:'b1',quote:'Transfer'},explanation:'Money request',next_action:'Verify through existing process'};
const email={email_id:'synthetic',sender:{address:'unknown'},subject:'Test',blocks:[{id:'b1',text:'Transfer money today.'}],links:[]};
const result={email_id:'synthetic',model:'rules-only',findings:[finding],analysis_complete:false,limitations:['Missing headers'],notes:[],verdict:{key:'verify',state:'unknown',label:'Verify'},dimensions:[{key:'sender',status:'unknown',question:'Sender?',answer:'Cannot tell'}]};
const scanReply = m => ({success:true,ok:true,...(m.type==='FINISH_BODY_SCAN'?{completed:true,scan_id:m.scan_id,email_id:m.email_id}:{})});
function panel(send) {
  const els={};let focused=null;const get=id=>{if(!els[id]) {els[id]=new El();els[id].focus=()=>{focused=id};}return els[id]};const messages=[];const events={};
  const ctx={setTimeout,clearTimeout,window:{addEventListener:(type,fn)=>events[type]=fn},document:{getElementById:get,createElement:()=>new El()},chrome:{runtime:{sendMessage:async m=>{messages.push(m);return m.type==='CONNECTION_STATUS'?{ok:true,connected:true}:send(m)},onMessage:{addListener:fn=>events.email=fn}},tabs:{query:async()=>[{id:1}],sendMessage:async(_,m)=>scanReply(m),onActivated:{addListener:fn=>events.tab=fn}}}};
  vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'..','sidepanel.js'),'utf8'),ctx);
  ctx.email=email;ctx.result=result;ctx.finding=finding;return {els,get,ctx,messages,events,focused:()=>focused};
}
test('UI labels backend rules-only and shows incomplete limitations, not LIVE AI',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));await p.ctx.analyzeEmail(email,'gmail',1);
  assert.equal(p.get('mode').textContent,'BACKEND RULES ONLY');assert.match(p.get('completeness').textContent,/Incomplete/);assert.equal(p.get('limitations').children[0].textContent,'Missing headers');assert.equal(p.get('verdict-box').dataset.state,'unknown');
});
test('demo label and transport remain explicitly local',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:true}));await p.ctx.analyzeEmail(email,'demo');
  assert.equal(p.get('mode').textContent,'LOCAL DEMO');assert.equal(p.messages.at(-1).demo,true);
});
test('navigation invalidation drops late analysis and re-enables controls',async()=>{
  let finish;const p=panel(()=>new Promise(r=>finish=r));const pending=p.ctx.analyzeEmail(email,'gmail',1);await new Promise(r=>setImmediate(r));
  p.ctx.clearResults('New email');finish({ok:true,data:result,mocked:false});await pending;
  assert.equal(p.get('results').hidden,true);assert.equal(p.get('analyze').disabled,false);assert.equal(p.get('demo').disabled,false);
});
test('challenge preserves the exact finding and unresolved procedure',async()=>{
  const p=panel(async m=>m.type==='ANALYZE'?{ok:true,data:result,mocked:false}:{ok:true,mocked:false,data:{assessment:'less_concerning',message:'Context noted',still_unresolved:'Procedure: verify first',next_action:'Call known contact'}});
  await p.ctx.analyzeEmail(email,'gmail',1);p.get('challenge-text').value='I called the known number.';await p.get('challenge').handlers.click();
  const m=p.messages.at(-1);assert.deepEqual(m.finding,finding);assert.equal(m.finding_id,undefined);assert.match(p.get('challenge-result').textContent,/Less concerning, not cleared/);assert.match(p.get('challenge-result').textContent,/Procedure: verify first/);
});
test('selection changes invalidate pending challenge without leaving button disabled',async()=>{
  let finish;const p=panel(async m=>m.type==='ANALYZE'?{ok:true,data:result,mocked:false}:new Promise(r=>finish=r));await p.ctx.analyzeEmail(email,'demo');
  p.get('challenge-text').value='Context';const pending=p.get('challenge').handlers.click();await new Promise(r=>setImmediate(r));await p.ctx.selectFinding(finding);finish({ok:true,mocked:true,data:{explanation:'OLD',next_action:'OLD'}});await pending;
  assert.equal(p.get('challenge-result').textContent,'');assert.equal(p.get('challenge').disabled,false);
});
test('repeated analyses accept only latest result',async()=>{
  const pending=[];const p=panel(()=>new Promise(r=>pending.push(r)));
  const a=p.ctx.analyzeEmail(email,'demo');await new Promise(r=>setImmediate(r));const b=p.ctx.analyzeEmail(email,'demo');await new Promise(r=>setImmediate(r));
  pending[1]({ok:true,mocked:true,data:{...result,summary:'Latest'}});await b;pending[0]({ok:true,mocked:true,data:{...result,summary:'Old'}});await a;assert.equal(p.get('summary').textContent,'Latest');
});
function extract(bodyText,linkCount=0,from=null){
  const body={innerText:bodyText,getClientRects:()=>[1],closest:()=>({querySelector:()=>from}),querySelectorAll:()=>Array.from({length:linkCount},(_,i)=>({innerText:`Link ${i}`,href:`https://example.test/${i}`}))};
  const ctx={document:{querySelectorAll:()=>[body],querySelector:()=>({textContent:'Test'}),documentElement:{}},chrome:{runtime:{onMessage:{addListener:()=>{}},sendMessage:async()=>{}}},window:{addEventListener:()=>{}},location:{hash:'#synthetic'},MutationObserver:class{observe(){}},setTimeout,clearTimeout};
  vm.createContext(ctx);let src=fs.readFileSync(path.join(__dirname,'..','content.js'),'utf8').replace('  checkEmailChange();\n})();','  globalThis.testExtract = extractEmail;\n})();');vm.runInContext(src,ctx);return ctx.testExtract();
}
test('extraction does not invent unknown address or borrow another message sender',()=>{
  const e=extract('Message');assert.equal(e.sender.address,'');assert.equal(e.extraction_complete,false);assert.ok(e.extraction_limitations.length>=2);
});
test('body over limit fails rather than silent truncation',()=>{assert.throws(()=>extract('x'.repeat(20000)),/20,000/)});
test('link truncation is explicit in incomplete extraction',()=>{const e=extract('Message',55);assert.equal(e.links.length,50);assert.match(e.extraction_limitations.at(-1),/first 50/)});

test('tab change during first extraction prevents any backend request',async()=>{
  let finish;const p=panel(async()=>({ok:true,data:result,mocked:false}));p.ctx.chrome.tabs.sendMessage=()=>new Promise(r=>finish=r);
  const pending=p.get('analyze').handlers.click();await new Promise(r=>setImmediate(r));p.events.tab({tabId:2});finish({ok:true,email});await pending;
  assert.equal(p.messages.filter(x=>x.type==='ANALYZE').length,0);assert.equal(p.get('analyze').disabled,false);
});
test('message change during first extraction prevents any backend request',async()=>{
  let finish;const p=panel(async()=>({ok:true,data:result,mocked:false}));p.ctx.chrome.tabs.sendMessage=()=>new Promise(r=>finish=r);
  const pending=p.get('analyze').handlers.click();await new Promise(r=>setImmediate(r));p.events.email({type:'EMAIL_CHANGED',email_id:'new'},{tab:{id:1}});finish({ok:true,email});await pending;
  assert.equal(p.messages.filter(x=>x.type==='ANALYZE').length,0);assert.equal(p.get('analyze').disabled,false);
});

test('Simple is the default, with truthful mode and incomplete warning visible',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));await p.ctx.analyzeEmail(email,'gmail',1);
  assert.equal(p.get('simple-view').hidden,false);assert.equal(p.get('details-view').hidden,true);
  assert.equal(p.get('home-view').hidden,true);assert.equal(p.get('simple-toggle').checked,true);
  assert.equal(p.get('simple-title').textContent,'Check first');assert.match(p.get('simple-warning').textContent,/Incomplete/);
  assert.equal(p.get('simple-reviewed').hidden,true);
});
test('stop always stays red even if the assessment is incomplete',()=>{
  const p=panel();const a=p.ctx.simpleAssessment({...result,verdict:{key:'stop',state:'unknown'}});
  assert.equal(a.state,'stop');assert.equal(a.title,"Don't pay yet");
});
test('missing or malformed verdict, incomplete and unknown never become green',()=>{
  const p=panel();const dims=['sender','money','pressure','links'].map(key=>({key,status:'ok'}));
  const clear={findings:[],analysis_complete:true,dimensions:dims,limitations:[],verdict:{key:'pay'}};
  assert.equal(p.ctx.simpleAssessment(clear).state,'clear');
  for(const changed of [
    {verdict:undefined},{verdict:{}},{verdict:{key:'pay',state:'unknown'}},{analysis_complete:false},
    {analysis_complete:undefined},{limitations:['Unverified']},{dimensions:[]},
    {dimensions:dims.slice(1)},{dimensions:[...dims,{key:'sender',status:'ok'}]},
    {dimensions:dims.map(d=>d.key==='sender'?{...d,status:'unknown'}:d)},
  ]) assert.notEqual(p.ctx.simpleAssessment({...clear,...changed}).state,'clear');
  assert.equal(p.ctx.simpleAssessment({...clear,findings:[finding]}).state,'verify');
  assert.equal(p.ctx.simpleAssessment({...clear,dimensions:dims.map(d=>({...d,status:'warn'}))}).state,'verify');
});
test('zero findings is unknown, not a guarantee or payment authorization',async()=>{
  const p=panel(async()=>({ok:true,data:{...result,findings:[],verdict:{key:'verify',state:'unknown'}},mocked:false}));
  await p.ctx.analyzeEmail(email,'gmail',1);assert.equal(p.get('simple-title').textContent,"Can't tell yet");
  assert.match(p.get('simple-scope').textContent,/Not enough information/);assert.equal(p.get('simple-verdict').dataset.state,'unknown');
});
test('Why and repeated toggles preserve results, then Back returns to Simple',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));await p.ctx.analyzeEmail(email,'gmail',1);
  const n=p.messages.length;p.get('simple-why').handlers.click();assert.equal(p.get('details-view').hidden,false);
  assert.equal(p.get('simple-toggle').checked,false);await p.get('back').handlers.click();
  assert.equal(p.get('simple-view').hidden,false);
  for(const checked of [false,true,false,true]) {p.get('simple-toggle').checked=checked;p.get('simple-toggle').handlers.change();assert.equal(p.get('simple-view').hidden,!checked);}
  assert.equal(p.messages.length,n);assert.equal(p.get('summary').textContent,'Review the findings and evidence below.');
});
test('Call, Reply and Tell IT are local-only guidance with no email data copied',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));await p.ctx.analyzeEmail(email,'gmail',1);
  const n=p.messages.length;
  for(const id of ['simple-call','simple-reply','simple-report']) {
    p.get(id).handlers.click();assert.equal(p.get('action-panel').hidden,false);assert.equal(p.get('simple-view').hidden,true);
    assert.doesNotMatch(p.get('action-template').value,/Transfer money|unknown/);
    p.get('action-template').value='Local edits';p.get('action-close').handlers.click();
    assert.equal(p.get('action-template').value,'');assert.equal(p.get('action-panel').hidden,true);
    assert.equal(p.get('simple-view').hidden,false);
  }
  assert.equal(p.messages.length,n);
});
test('Back closes guidance first, then clears result and Gmail highlight',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));const tabCalls=[];
  p.ctx.chrome.tabs.sendMessage=async(id,m)=>{tabCalls.push(m);return scanReply(m)};
  await p.ctx.analyzeEmail(email,'gmail',1);p.get('simple-reply').handlers.click();
  await p.get('back').handlers.click();assert.equal(p.get('simple-view').hidden,false);
  await p.get('back').handlers.click();assert.equal(p.get('home-view').hidden,false);assert.equal(p.get('simple-view').hidden,true);
  assert.equal(p.get('back').hidden,true);assert.equal(tabCalls.at(-1).type,'CLEAR_HIGHLIGHTS');
});
test('navigation clears open local drafts and late analysis cannot restore Simple',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));await p.ctx.analyzeEmail(email,'gmail',1);
  p.get('simple-report').handlers.click();p.get('action-template').value='Edited';
  p.events.email({type:'EMAIL_CHANGED',email_id:'new'},{tab:{id:1}});
  assert.equal(p.get('action-panel').hidden,true);assert.equal(p.get('action-template').value,'');assert.equal(p.get('simple-view').hidden,true);
  let finish;p.ctx.chrome.runtime.sendMessage=()=>new Promise(r=>finish=r);
  const pending=p.ctx.analyzeEmail(email,'gmail',1);await new Promise(r=>setImmediate(r));
  p.ctx.clearResults('Changed');finish({ok:true,data:result,mocked:false});await pending;
  assert.equal(p.get('simple-view').hidden,true);assert.equal(p.get('home-view').hidden,false);
});
test('analysis failure after a result does not leave a stale shield visible',async()=>{
  let fail=false;const p=panel(async()=>fail?{ok:false,error:'Proxy stopped'}:{ok:true,data:result,mocked:false});
  await p.ctx.analyzeEmail(email,'gmail',1);fail=true;await p.ctx.analyzeEmail(email,'gmail',1);
  assert.equal(p.get('simple-view').hidden,true);assert.equal(p.get('details-view').hidden,true);assert.match(p.get('status').textContent,/Proxy stopped/);
});
test('disconnect clears result, open guidance, token request and mode',async()=>{
  const p=panel(async m=>m.type==='ANALYZE'?{ok:true,data:result,mocked:false}:{ok:true});
  await p.ctx.analyzeEmail(email,'gmail',1);p.get('simple-call').handlers.click();
  p.ctx.chrome.runtime.sendMessage=async m=>{p.messages.push(m);return m.type==='CONNECTION_STATUS'?{ok:true,connected:false}:{ok:true}};
  await p.get('disconnect').handlers.click();assert.ok(p.messages.some(m=>m.type==='DISCONNECT'));
  assert.equal(p.get('simple-view').hidden,true);assert.equal(p.get('action-panel').hidden,true);assert.equal(p.get('mode').textContent,'NOT CONNECTED');
});
test('mark reviewed never changes the verdict or transmits anything',async()=>{
  const clear={...result,analysis_complete:true,findings:[],limitations:[],verdict:{key:'pay'},dimensions:['sender','money','pressure','links'].map(key=>({key,status:'ok'}))};
  const p=panel(async()=>({ok:true,data:clear,mocked:false}));await p.ctx.analyzeEmail(email,'demo');
  const n=p.messages.length;assert.equal(p.get('simple-title').textContent,'No warning signs');
  p.get('simple-reviewed').handlers.click();assert.match(p.get('reviewed-note').textContent,/does not verify/);
  assert.equal(p.messages.length,n);assert.equal(p.get('simple-verdict').dataset.state,'clear');
  p.ctx.clearResults();p.get('simple-reviewed').handlers.click();assert.equal(p.get('simple-view').hidden,true);
});


test('result transitions move focus and retain subject and displayed sender',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));await p.ctx.analyzeEmail(email,'gmail',1);
  assert.equal(p.focused(),'simple-title');assert.equal(p.get('result-context').hidden,false);
  assert.equal(p.get('result-subject').textContent,'Test');assert.match(p.get('result-sender').textContent,/unknown/);
  p.get('simple-why').handlers.click();assert.equal(p.focused(),'results');assert.equal(p.get('result-context').hidden,false);
  p.ctx.clearResults();assert.equal(p.focused(),'analyze');assert.equal(p.get('result-context').hidden,true);
});
test('Back cannot erase a newer result while clearing old Gmail highlights',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));await p.ctx.analyzeEmail(email,'gmail',1);
  let finish;p.ctx.chrome.tabs.sendMessage=()=>new Promise(r=>finish=r);
  const back=p.get('back').handlers.click();await new Promise(r=>setImmediate(r));
  p.ctx.clearResults();await p.ctx.analyzeEmail(email,'demo');finish({success:true,ok:true});await back;
  assert.equal(p.get('simple-view').hidden,false);assert.equal(p.get('home-view').hidden,true);
});

test('failed body-scan identity check prevents backend transmission',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));const calls=[];
  p.ctx.chrome.tabs.sendMessage=async(_,m)=>{calls.push(m);return {ok:false,error:'Selected message changed'}};
  await p.ctx.analyzeEmail(email,'gmail',1);
  assert.equal(p.messages.filter(m=>m.type==='ANALYZE').length,0);
  assert.match(p.get('status').textContent,/Selected message changed/);
  assert.equal(p.get('analyze').disabled,false);
  assert.equal(calls.at(-1).type,'STOP_BODY_SCAN');
});
test('navigation while starting a body scan prevents transmission and removes overlay',async()=>{
  let finish;const calls=[];const p=panel(async()=>({ok:true,data:result,mocked:false}));
  p.ctx.chrome.tabs.sendMessage=async(_,m)=>{calls.push(m);return m.type==='START_BODY_SCAN'?new Promise(r=>finish=r):{ok:true}};
  const pending=p.ctx.analyzeEmail(email,'gmail',1);await new Promise(r=>setImmediate(r));
  p.ctx.clearResults('New message');finish({ok:true});await pending;
  assert.equal(p.messages.filter(m=>m.type==='ANALYZE').length,0);
  assert.equal(p.get('analyze').disabled,false);
  assert.equal(calls.at(-1).type,'STOP_BODY_SCAN');
});
test('backend failures always stop the matching body scan and restore controls',async()=>{
  const calls=[];const p=panel(async()=>({ok:false,error:'Backend unavailable'}));
  p.ctx.chrome.tabs.sendMessage=async(_,m)=>{calls.push(m);return {ok:true}};
  await p.ctx.analyzeEmail(email,'gmail',1);
  assert.equal(calls[0].type,'START_BODY_SCAN');assert.equal(calls.at(-1).type,'STOP_BODY_SCAN');
  assert.equal(calls[0].scan_id,calls.at(-1).scan_id);
  assert.equal(p.get('analyze').disabled,false);assert.match(p.get('status').textContent,/Backend unavailable/);
});


test('fast backend response stays hidden and busy until the scan completion acknowledgment',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));let finish;const calls=[];
  p.ctx.chrome.tabs.sendMessage=async(_,m)=>{calls.push(m);return m.type==='FINISH_BODY_SCAN'?new Promise(r=>finish=()=>r(scanReply(m))):scanReply(m)};
  const pending=p.ctx.analyzeEmail(email,'gmail',1);await new Promise(r=>setImmediate(r));
  assert.equal(p.messages.filter(m=>m.type==='ANALYZE').length,1);
  assert.equal(p.get('simple-view').hidden,true);assert.equal(p.get('results').hidden,true);
  assert.equal(p.get('analyze').disabled,true);assert.equal(p.get('analyze').attrs['aria-busy'],'true');assert.equal(p.get('cancel-check').hidden,false);
  assert.match(p.get('status').textContent,/Backend response received/);assert.notEqual(p.focused(),'simple-title');
  finish();await pending;
  assert.equal(p.get('simple-view').hidden,false);assert.equal(p.focused(),'simple-title');
  assert.equal(p.get('analyze').attrs['aria-busy'],'false');assert.equal(p.get('cancel-check').hidden,true);
});
test('animation readiness alone cannot reveal a result while the backend is pending',async()=>{
  let finish;const p=panel(()=>new Promise(r=>finish=r));const calls=[];
  p.ctx.chrome.tabs.sendMessage=async(_,m)=>{calls.push(m);return scanReply(m)};
  const pending=p.ctx.analyzeEmail(email,'gmail',1);await new Promise(r=>setImmediate(r));
  assert.equal(p.get('results').hidden,true);assert.equal(calls.some(m=>m.type==='FINISH_BODY_SCAN'),false);
  finish({ok:true,data:result,mocked:false});await pending;assert.equal(p.get('simple-view').hidden,false);
});
test('navigation, cancel, disconnect and panel closure during finish discard late completion',async()=>{
  for(const cancel of [
    p=>p.events.email({type:'EMAIL_CHANGED',email_id:'new'},{tab:{id:1}}),
    p=>p.events.tab({tabId:2}),
    p=>p.get('cancel-check').handlers.click(),
    p=>p.get('disconnect').handlers.click(),
    p=>p.events.pagehide()
  ]) {
    const p=panel(async()=>({ok:true,data:result,mocked:false}));let finish;
    p.ctx.chrome.tabs.sendMessage=async(_,m)=>m.type==='FINISH_BODY_SCAN'?new Promise(r=>finish=()=>r(scanReply(m))):scanReply(m);
    const pending=p.ctx.analyzeEmail(email,'gmail',1);await new Promise(r=>setImmediate(r));
    await cancel(p);finish();await pending;
    assert.equal(p.get('simple-view').hidden,true);assert.equal(p.get('results').hidden,true);
  }
});
test('missing or mismatched completion acknowledgment fails closed and restores controls',async()=>{
  for(const response of [{ok:true},{ok:false,error:'Message changed'}, {ok:true,completed:true,scan_id:'old',email_id:email.email_id}]) {
    const p=panel(async()=>({ok:true,data:result,mocked:false}));
    p.ctx.chrome.tabs.sendMessage=async(_,m)=>m.type==='FINISH_BODY_SCAN'?response:scanReply(m);
    await p.ctx.analyzeEmail(email,'gmail',1);
    assert.equal(p.get('simple-view').hidden,true);assert.equal(p.get('analyze').disabled,false);assert.match(p.get('status').textContent,/Analysis failed/);
  }
});
test('lost completion response has a bounded timeout, clears the scan and permits retry',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));let timeout;const calls=[];
  p.ctx.setTimeout=(fn,ms)=>{assert.equal(ms,2500);timeout=fn;return 1};p.ctx.clearTimeout=()=>{};
  p.ctx.chrome.tabs.sendMessage=async(_,m)=>{calls.push(m);return m.type==='FINISH_BODY_SCAN'?new Promise(()=>{}):scanReply(m)};
  const pending=p.ctx.analyzeEmail(email,'gmail',1);await new Promise(r=>setImmediate(r));timeout();await pending;
  assert.equal(p.get('simple-view').hidden,true);assert.equal(p.get('analyze').disabled,false);
  assert.equal(calls.at(-1).type,'STOP_BODY_SCAN');assert.match(p.get('status').textContent,/Refresh Gmail/);
});
test('an old canceled scan cannot stop or overwrite a newer scan result',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));const completions=[],calls=[];
  p.ctx.chrome.tabs.sendMessage=async(_,m)=>{calls.push(m);return m.type==='FINISH_BODY_SCAN'?new Promise(r=>completions.push(()=>r(scanReply(m)))):scanReply(m)};
  const old=p.ctx.analyzeEmail(email,'gmail',1);await new Promise(r=>setImmediate(r));p.get('cancel-check').handlers.click();
  const newer=p.ctx.analyzeEmail(email,'gmail',1);await new Promise(r=>setImmediate(r));
  completions[1]();await newer;completions[0]();await old;
  assert.equal(p.get('simple-view').hidden,false);assert.equal(p.get('analyze').disabled,false);
  const starts=calls.filter(m=>m.type==='START_BODY_SCAN');assert.notEqual(starts[0].scan_id,starts[1].scan_id);
});
test('final active-tab validation rejects a switch even before the tab event arrives',async()=>{
  const p=panel(async()=>({ok:true,data:result,mocked:false}));p.ctx.chrome.tabs.query=async()=>[{id:2}];
  await p.ctx.analyzeEmail(email,'gmail',1);assert.equal(p.get('simple-view').hidden,true);assert.match(p.get('status').textContent,/Tab changed/);
});


test('selecting another retained title immediately clears the previous result and local guidance', async () => {
  const p=panel(async()=>({ok:true,data:result,mocked:false})); await p.ctx.analyzeEmail(email,'gmail',1);
  p.get('simple-reply').handlers.click();
  p.events['hookline:inbox-opening']({detail:{subject:'Next suspicious title'}});
  assert.equal(p.get('simple-view').hidden,true); assert.equal(p.get('action-panel').hidden,true);
  assert.equal(p.get('subject').textContent,'Next suspicious title');
  assert.match(p.get('sender').textContent,/not been checked/);
  assert.equal(p.get('analyze').disabled,false);
});

test('selecting a retained title discards an in-flight body analysis before Gmail finishes opening', async () => {
  let finish; const p=panel(()=>new Promise(resolve=>finish=resolve));
  const pending=p.ctx.analyzeEmail(email,'gmail',1); await new Promise(resolve=>setImmediate(resolve));
  p.events['hookline:inbox-opening']({detail:{subject:'Next title'}});
  finish({ok:true,data:result,mocked:false}); await pending;
  assert.equal(p.get('simple-view').hidden,true); assert.equal(p.get('results').hidden,true);
  assert.equal(p.get('subject').textContent,'Next title'); assert.equal(p.get('analyze').disabled,false);
});
