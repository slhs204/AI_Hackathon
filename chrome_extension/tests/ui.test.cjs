const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
class El {
  constructor(){this.children=[];this.dataset={};this.attrs={};this.hidden=false;this.textContent='';this.value='';this.disabled=false;this.handlers={};this.classList={toggle:()=>{}};this.style={setProperty:()=>{}};}
  append(...x){this.children.push(...x)} replaceChildren(...x){this.children=x} setAttribute(k,v){this.attrs[k]=v} addEventListener(k,fn){this.handlers[k]=fn} querySelectorAll(){return []}
}
const finding={id:'f1',category:'payment_or_data_request',evidence:{kind:'text',block_id:'b1',quote:'Transfer'},explanation:'Money request',next_action:'Verify through existing process'};
const email={email_id:'synthetic',sender:{address:'unknown'},subject:'Test',blocks:[{id:'b1',text:'Transfer money today.'}],links:[]};
const result={email_id:'synthetic',model:'rules-only',findings:[finding],analysis_complete:false,limitations:['Missing headers'],notes:[],verdict:{key:'verify',state:'unknown',label:'Verify'},dimensions:[{key:'sender',status:'unknown',question:'Sender?',answer:'Cannot tell'}]};
function panel(send) {
  const els={};const get=id=>els[id] ||=new El();const messages=[];const events={};
  const ctx={document:{getElementById:get,createElement:()=>new El()},chrome:{runtime:{sendMessage:async m=>{messages.push(m);return m.type==='CONNECTION_STATUS'?{ok:true,connected:true}:send(m)},onMessage:{addListener:fn=>events.email=fn}},tabs:{query:async()=>[{id:1}],sendMessage:async()=>({success:true}),onActivated:{addListener:fn=>events.tab=fn}}}};
  vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'..','sidepanel.js'),'utf8'),ctx);
  ctx.email=email;ctx.result=result;ctx.finding=finding;return {els,get,ctx,messages,events};
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
