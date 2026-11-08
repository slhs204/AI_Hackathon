const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'background.js'), 'utf8');
const health = {status:'ok', service:'phishing-coach', model:{analyze:'rules-only',challenge:'rules-only'}};
const email = {email_id:'synthetic', sender:{address:'test@example.test'},subject:'Example',blocks:[{id:'b1',text:'Please change my salary account today.'}],links:[]};
const finding = {id:'model-f7',category:'manipulation_cue',evidence:{kind:'text',block_id:'b1',quote:'Please'},explanation:'Verify',next_action:'Call on known number',source:'model'};
const analysis = {email_id:email.email_id, model:'rules-only', findings:[finding], analysis_complete:false, limitations:['Missing headers']};
function harness(fetcher) {
  let listener; const storage = {}; const calls=[];
  const sender={id:'extension-id',url:'chrome-extension://extension-id/sidepanel.html'};
  const chrome={runtime:{id:sender.id,getURL:p=>`chrome-extension://extension-id/${p}`,onMessage:{addListener:fn=>listener=fn}},
    sidePanel:{setPanelBehavior:async()=>{}}, storage:{session:{get:async key=>({[key]:storage[key]}),set:async x=>Object.assign(storage,x),remove:async k=>delete storage[k]}}};
  const context={chrome,console,AbortSignal,fetch:async (url,opts)=>{calls.push({url,opts}); return fetcher?.(url,opts,calls.length) || {ok:true,json:async()=>health}}};
  vm.createContext(context);vm.runInContext(source,context);
  return {calls,storage,context,send:(message,source=sender)=>new Promise(resolve=>listener(message,source,resolve))};
}
test('rejects content-script initiated backend calls', async()=>{
  const h=harness();const r=await h.send({type:'ANALYZE',email},{id:'extension-id',tab:{id:1},url:'https://mail.google.com/'});
  assert.equal(r.ok,false);assert.equal(h.calls.length,0);
});
test('Gmail analysis requires explicit session connection; demo stays local',async()=>{
  const h=harness();assert.equal((await h.send({type:'ANALYZE',email})).ok,false);
  const r=await h.send({type:'ANALYZE',email,demo:true});assert.equal(r.mocked,true);assert.equal(r.data.model,'local-demo');assert.equal(h.calls.length,0);
});
test('connect checks authenticated rules-only session, stores token in session, not reply',async()=>{
  const h=harness();const r=await h.send({type:'CONNECT',token:'synthetic-demo-token'});
  assert.equal(r.ok,true);assert.equal(h.calls[0].url,'http://127.0.0.1:8080/session');
  assert.equal(h.calls[0].opts.headers['X-Demo-Token'],'synthetic-demo-token');
  assert.equal(h.calls[0].opts.headers['X-Require-Rules-Only'],'1');assert.equal(h.calls[0].opts.redirect,'error');
  assert.equal(h.calls[0].opts.credentials,'omit');assert.equal(JSON.stringify(r).includes('synthetic-demo-token'),false);
  await h.send({type:'DISCONNECT'});assert.deepEqual(h.storage,{});
});
test('paid backend refuses connection and sends no email',async()=>{
  const h=harness(()=>({ok:true,json:async()=>({...health,model:{analyze:'paid',challenge:'paid'}})}));
  assert.equal((await h.send({type:'CONNECT',token:'x'})).ok,false);assert.equal(h.calls.length,1);assert.deepEqual(h.storage,{});
});
test('wrong token is reported at connection, not silently stored',async()=>{
  const h=harness(()=>({ok:false,status:401}));const r=await h.send({type:'CONNECT',token:'wrong'});
  assert.equal(r.ok,false);assert.match(r.error,/token/);assert.deepEqual(h.storage,{});
});
test('backend analyze validates response and uses full payload with rules-only guard',async()=>{
  const h=harness(url=>({ok:true,json:async()=>url.endsWith('/analyze')?analysis:health}));
  await h.send({type:'CONNECT',token:'x'});const r=await h.send({type:'ANALYZE',email});
  assert.equal(r.ok,true);assert.equal(r.mocked,false);assert.deepEqual(JSON.parse(h.calls.at(-1).opts.body),email);
  assert.equal(h.calls.at(-1).opts.headers['X-Require-Rules-Only'],'1');
});
test('challenge sends complete original finding and context, not a volatile id',async()=>{
  const h=harness(url=>({ok:true,json:async()=>url.endsWith('/challenge')?{model:'rules-only',finding_id:finding.id,assessment:'less_concerning',message:'Context noted',still_unresolved:'Procedure remains',next_action:'Call'}:health}));
  await h.send({type:'CONNECT',token:'x'});const r=await h.send({type:'CHALLENGE',email,finding,context:'I called.'});
  assert.equal(r.ok,true);assert.deepEqual(JSON.parse(h.calls.at(-1).opts.body),{email,finding,user_context:'I called.'});
});
test('malformed/mismatched response and unexpected AI result fail closed',async()=>{
  for (const result of [{}, {...analysis,email_id:'other'}, {...analysis,model:'paid'}, {...analysis,findings:[null]}]) {
    const h=harness(url=>({ok:true,json:async()=>url.endsWith('/analyze')?result:health}));
    await h.send({type:'CONNECT',token:'x'});assert.equal((await h.send({type:'ANALYZE',email})).ok,false);
  }
});
test('HTTP auth/validation/server errors, timeout and malformed JSON remain errors',async()=>{
  for (const status of [403,409,422,502,503,504,500]) {
    const h=harness(()=>({ok:false,status}));assert.equal((await h.send({type:'CONNECT',token:'x'})).ok,false);
  }
  for (const fetcher of [()=>{throw {name:'TimeoutError'}},()=>({ok:true,json:async()=>{throw Error('invalid')}})]) {
    const h=harness(fetcher);assert.equal((await h.send({type:'CONNECT',token:'x'})).ok,false);
  }
});
test('disconnect during connection check prevents late token save',async()=>{
  let finish; const h=harness(()=>new Promise(r=>finish=()=>r({ok:true,json:async()=>health})));
  const pending=h.send({type:'CONNECT',token:'x'});await new Promise(r=>setImmediate(r));
  await h.send({type:'DISCONNECT'});finish();assert.equal((await pending).ok,false);assert.deepEqual(h.storage,{});
});
test('disconnect during preflight prevents the subsequent email POST',async()=>{
  let finish; const h=harness((url,opts,n)=>n===2?new Promise(r=>finish=()=>r({ok:true,json:async()=>health})):null);
  await h.send({type:'CONNECT',token:'x'});const pending=h.send({type:'ANALYZE',email});await new Promise(r=>setImmediate(r));
  await h.send({type:'DISCONNECT'});finish();assert.equal((await pending).ok,false);assert.equal(h.calls.length,2);
});

test('local Tinker needs explicit permission and keeps a server-enforced provider guard',async()=>{
  const model='tinker:test-sampler'; const liveHealth={...health,model:{analyze:model,challenge:model}};
  const h=harness(url=>({ok:true,json:async()=>url.endsWith('/analyze')?{...analysis,model}:liveHealth}));
  assert.equal((await h.send({type:'CONNECT',token:'x',endpoint:'local'})).ok,false);
  assert.equal(h.calls.length,1);assert.equal(h.calls[0].opts.headers['X-Require-Rules-Only'],'1');
  assert.equal((await h.send({type:'CONNECT',token:'x',endpoint:'local',allowAI:true})).ok,true);
  const result=await h.send({type:'ANALYZE',email});assert.equal(result.ok,true);
  assert.equal(h.calls.at(-1).url,'http://127.0.0.1:8081/analyze');
  assert.equal(h.calls.at(-1).opts.headers['X-Require-Tinker'],'1');
  assert.equal(h.calls.at(-1).opts.headers['X-Require-Rules-Only'],undefined);
  await h.send({type:'DISCONNECT'});assert.deepEqual(h.storage,{});
});

test('rejects arbitrary destinations and AI permission on legacy staging',async()=>{
  for(const endpoint of ['https://example.test','other','staging']) {
    const h=harness();const r=await h.send({type:'CONNECT',token:'x',endpoint,allowAI:true});
    assert.equal(r.ok,false);assert.equal(h.calls.length,0);
  }
});

test('changing provider after Tinker connection prevents email POST',async()=>{
  const model='tinker:test-sampler';let changed=false;
  const h=harness(()=>({ok:true,json:async()=>({...health,model:{analyze:changed?'anthropic:other':model,challenge:changed?'anthropic:other':model}})}));
  assert.equal((await h.send({type:'CONNECT',token:'x',endpoint:'local',allowAI:true})).ok,true);
  changed=true;assert.equal((await h.send({type:'ANALYZE',email})).ok,false);
  assert.ok(h.calls.every(c=>c.opts.method==='GET'));
});

test('failed reconnect revokes the previous AI session rather than retaining permission',async()=>{
  const model='tinker:test-sampler';let invalid=false;
  const h=harness(()=>invalid?{ok:false,status:401}:{ok:true,json:async()=>({...health,model:{analyze:model,challenge:model}})});
  assert.equal((await h.send({type:'CONNECT',token:'x',endpoint:'local',allowAI:true})).ok,true);
  invalid=true;assert.equal((await h.send({type:'CONNECT',token:'wrong',endpoint:'local'})).ok,false);
  const before=h.calls.length;assert.equal((await h.send({type:'ANALYZE',email})).ok,false);assert.equal(h.calls.length,before);assert.deepEqual(h.storage,{});
});

test('cloud execution survives connection storage and status restoration without exposing tokens',async()=>{
  const model='tinker:Qwen/Qwen3-8B';
  const h=harness(()=>({ok:true,json:async()=>({...health,execution:'cloud-run',model:{analyze:model,challenge:model}})}));
  const connected=await h.send({type:'CONNECT',token:'private-token',endpoint:'local',allowAI:true});
  assert.equal(connected.execution,'cloud-run');
  assert.equal(h.storage.hooklineConnection.execution,'cloud-run');
  const restored=await h.send({type:'CONNECTION_STATUS'});
  assert.equal(restored.execution,'cloud-run');
  assert.equal(restored.allowAI,true);
  assert.equal(JSON.stringify(restored).includes('private-token'),false);
});
