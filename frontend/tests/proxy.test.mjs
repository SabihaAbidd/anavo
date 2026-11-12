import test from 'node:test';
import assert from 'node:assert/strict';
const base='http://127.0.0.1:5173';
async function post(path,body){return fetch(base+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});}
test('Vite serves the React entry and proxies healthy backend',async()=>{
 const page=await fetch(base);assert.equal(page.status,200);assert.match(await page.text(),/src\/main.tsx/);
 const health=await (await fetch(base+'/health')).json();assert.equal(health.status,'ok');
});
test('scenario, exact solution, quantum measurement and validation contracts traverse proxy',async()=>{
 const {scenarios}=await (await fetch(base+'/api/scenarios')).json();assert.equal(scenarios.length,4);
 const scenario=scenarios.find(s=>s.name==='Ample backup');assert.ok(scenario);
 const exact=await post('/api/optimize',{scenario,algorithm:'classical'});assert.equal(exact.status,200);
 const {result}=await exact.json();assert.equal(result.allocation.objective_value,30);assert.ok(result.allocation.energy_used_wh<=scenario.battery_wh);
 const compared=await post('/api/compare',{scenario,quantum_options:{depth:2,shots:2048,maxiter:80,restarts:2,seed:42,max_qubits:14}});assert.equal(compared.status,200);
 const pair=await compared.json();assert.equal(pair.comparison_status,'complete');assert.equal(pair.quantum.quantum_metadata.shots,2048);assert.equal(pair.quantum.allocation.objective_value,30);assert.equal(pair.objective_gap,0);
 const impossible=await post('/api/optimize',{scenario:scenarios.find(s=>s.name==='Mandatory infeasible'),algorithm:'classical'});const bad=await impossible.json();assert.equal(bad.result.status,'infeasible');assert.equal(bad.result.allocation,null);
 const invalid=await post('/api/optimize',{scenario:{...scenario,battery_wh:-1},algorithm:'classical'});assert.equal(invalid.status,422);assert.ok((await invalid.json()).error.message);
});
test('schedule, society MILP, async job queue and Pakistan dataset traverse proxy',async()=>{
 const {scenarios}=await (await fetch(base+'/api/scenarios')).json();const evening=scenarios[0];
 const plan=await (await post('/api/schedule',{scenario:evening})).json();assert.equal(plan.utility,24);assert.equal(plan.timeline.length,3);
 const {data}=await (await fetch(base+'/api/data/pakistan')).json();assert.ok(Object.keys(data.sources).length>=5);
 const home={name:'A',appliances:evening.appliances};
 const fleet=await (await post('/api/fleet/optimize',{homes:[home,{...home,name:'B'}],battery_wh:480,inverter_w:200,outage_h:3})).json();
 assert.equal(fleet.utility,54);assert.equal(fleet.baseline.utility,48);
 let job=await (await post('/api/jobs',{kind:'compare',payload:{scenario:scenarios[2]}})).json();
 while(job.status==='queued'||job.status==='running'){await new Promise(r=>setTimeout(r,500));job=await (await fetch(`${base}/api/jobs/${job.job_id}`)).json();}
 assert.equal(job.status,'succeeded');const meta=job.result.quantum.quantum_metadata;
 assert.equal(meta.selection_distribution.reduce((s,x)=>s+x.count,0),meta.shots);assert.equal(meta.landscape.length,16);
});
