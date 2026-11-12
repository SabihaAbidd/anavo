import {useState} from 'react';
import {ArrowRight,LoaderCircle,Building2,Atom} from 'lucide-react';
import {archetypeHome,quantumOptions,runJob} from '../api';
import type {Comparison,Dataset,Fleet,HomeResult,Job} from '../api';

const pct=(v:number)=>`${(v*100).toFixed(0)}%`;

/** B2B: one shared battery bank and inverter for a whole housing society, solved as an exact MILP via the job queue. */
export default function SocietyLab({data}:{data:Dataset|null}){
 const [counts,setCounts]=useState<Record<string,number>>({apartment:10,family:8,medical:2,large:4});
 const [batteryKwh,setBatteryKwh]=useState(40);const [inverterKw,setInverterKw]=useState(6);
 const [outage,setOutage]=useState(4);const [fairness,setFairness]=useState(0.3);
 const [job,setJob]=useState<Job<Fleet>|null>(null);const [fleet,setFleet]=useState<Fleet|null>(null);
 const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [pick,setPick]=useState<number|null>(null);
 const [qJob,setQJob]=useState<Job<Comparison>|null>(null);const [qBusy,setQBusy]=useState(false);const [qError,setQError]=useState('');
 if(!data)return <section className="society section" id="society"><div className="section-label">[ 04 / SOCIETY GRID ]</div><p className="no-result">Waiting for the backend dataset…</p></section>;
 const homes=data.household_archetypes.flatMap(a=>Array.from({length:counts[a.id]||0},(_,i)=>archetypeHome(`${a.label} ${i+1}`,a,data.appliances,outage)));
 const reset=()=>{setFleet(null);setJob(null);setPick(null);setQJob(null);};
 async function run(){setBusy(true);setError('');reset();try{const done=await runJob<Fleet>('fleet',{name:'Housing society',homes,battery_wh:batteryKwh*1000,inverter_w:inverterKw*1000,outage_h:outage,fairness_floor:fairness},setJob);setFleet(done.result);}catch(e){setError(e instanceof Error?e.message:'Fleet optimisation failed.');}finally{setBusy(false);}}
 async function verify(index:number,home:HomeResult){setQBusy(true);setQError('');setQJob(null);
  const source=homes[index];
  // Decomposition: the society MILP allocates this home a share; QAOA re-solves the home inside that share.
  const scenario={name:home.name,appliances:source.appliances,battery_wh:home.energy_wh,inverter_w:home.power_w,outage_h:outage};
  try{const done=await runJob<Comparison>('compare',{scenario,quantum_options:quantumOptions},setQJob);setQJob(done);}catch(e){setQError(e instanceof Error?e.message:'Quantum job failed.');}finally{setQBusy(false);}}
 const q=qJob?.result;const sel=fleet&&pick!=null?fleet.home_results[pick]:null;
 const best=fleet?Math.max(fleet.utility||0,fleet.baseline.utility,1):1;
 return <section className="society section" id="society">
  <div className="feature-heading"><div><div className="section-label">[ 04 / SOCIETY GRID — B2B ]</div><h2>ONE BATTERY.<br/><span>EVERY HOME.</span></h2></div>
   <p>For housing societies, apartment blocks and solar microgrid operators. A shared battery bank and inverter serve many homes. ANAVO solves the <b>whole society at once</b> (exact MILP, hundreds of homes in seconds), guarantees every home's mandatory loads — like an oxygen concentrator — and enforces a fairness floor. It is benchmarked against the usual rule: split capacity equally.</p></div>
  <div className="control-panel"><div className="panel-bar"><span><Building2 size={15}/> SOCIETY CONFIGURATION — {homes.length} HOMES · {homes.reduce((s,h)=>s+h.appliances.length,0)} DECISIONS</span><span className="tag">RUNS ON ASYNC JOB QUEUE</span></div>
   <div className="archetypes">{data.household_archetypes.map(a=><label key={a.id}><span>{a.label}{a.weight>1?` · priority ×${a.weight}`:''}</span><small>{a.appliances.join(' · ')}</small><input type="number" min="0" max="200" value={counts[a.id]||0} onChange={e=>{setCounts({...counts,[a.id]:Math.max(0,Math.min(200,Number(e.target.value)))});reset();}}/></label>)}</div>
   <div className="config-top"><label>SHARED BATTERY<div className="number-field"><input type="number" min="0" step="5" value={batteryKwh} onChange={e=>{setBatteryKwh(Number(e.target.value));reset();}}/><span>kWh</span></div></label>
    <label>SHARED INVERTER<div className="number-field"><input type="number" min="0" step="1" value={inverterKw} onChange={e=>{setInverterKw(Number(e.target.value));reset();}}/><span>kW</span></div></label>
    <label>OUTAGE (PAKISTAN PROFILE)<select value={outage} onChange={e=>{setOutage(Number(e.target.value));reset();}}><option value={4}>Evening block · 4 h</option>{data.outage_profiles.filter(p=>p.daily_outage_h>0).map(p=><option key={p.id} value={p.daily_outage_h}>{p.label} · {p.daily_outage_h} h</option>)}</select></label>
    <label>FAIRNESS FLOOR · {pct(fairness)}<input className="range" type="range" min="0" max="0.8" step="0.05" value={fairness} onChange={e=>{setFairness(Number(e.target.value));reset();}}/></label></div>
   <div className="run-bar"><div className="panel-note inline">EVERY HOME GETS ≥ {pct(fairness)} OF ITS OWN PRIORITY POINTS · MANDATORY LOADS NEVER DROPPED</div><button className="primary-button run" disabled={busy||!homes.length} onClick={run}>{busy?<><LoaderCircle size={18} className="spin"/> {job?`JOB ${job.status.toUpperCase()}${job.queue_position?` #${job.queue_position}`:''}…`:'SUBMITTING…'}</>:<>OPTIMIZE SOCIETY <ArrowRight size={19}/></>}</button></div>
   {error&&<div className="error" role="alert">REQUEST NOT COMPLETED / {error}</div>}</div>
  {fleet&&!fleet.feasible&&<p className="no-result big">{fleet.message} Lower the fairness floor or add capacity.</p>}
  {fleet&&fleet.feasible&&<div className="society-result">
   <div className="kpi-row">
    <div className="gain"><strong>+{fleet.gain_vs_equal_split}</strong><label>priority points vs equal split ({fleet.baseline.utility? pct((fleet.gain_vs_equal_split||0)/fleet.baseline.utility):'—'} more)</label></div>
    <div><strong>{fleet.homes_fully_mandatory}/{fleet.homes}</strong><label>homes with mandatory loads met (equal split: {fleet.baseline.homes_with_mandatory_met})</label></div>
    <div><strong>{fleet.fairness_index?.toFixed(2)}</strong><label>Jain fairness index (equal split: {fleet.baseline.fairness_index.toFixed(2)})</label></div>
    <div><strong>{((fleet.energy_used_wh||0)/1000).toFixed(1)} kWh</strong><label>of {batteryKwh} kWh · {((fleet.power_used_w||0)/1000).toFixed(1)} of {inverterKw} kW</label></div>
    <div><strong>{fleet.runtime_s.toFixed(2)} s</strong><label>{fleet.decisions} binary decisions · {fleet.status}</label></div>
   </div>
   <article className="insight-card wide"><header><span>POOLED OPTIMISATION VS EQUAL SPLIT</span><small>TOTAL PRIORITY POINTS SERVED ACROSS THE SOCIETY</small></header>
    <div className="compare-bars"><div><span>ANAVO pooled MILP</span><div className="bar"><i style={{width:`${(fleet.utility||0)/best*100}%`}}/></div><b>{fleet.utility}</b></div><div><span>Equal split (1/N each)</span><div className="bar alt"><i style={{width:`${fleet.baseline.utility/best*100}%`}}/></div><b>{fleet.baseline.utility}</b></div></div></article>
   <article className="insight-card wide"><header><span>HOME MAP</span><small>BRIGHTER = MORE OF THE HOME'S PRIORITIES SERVED · CLICK A HOME</small></header>
    <div className="home-grid">{fleet.home_results.map((h,i)=><button key={h.name} className={'home '+(pick===i?'active':'')} style={{['--fill' as string]:h.service_ratio}} onClick={()=>{setPick(i);setQJob(null);setQError('');}} title={`${h.name}: ${pct(h.service_ratio)} served`}><i/><span>{i+1}</span></button>)}</div>
    {sel&&<div className="home-detail"><h4>{sel.name} <small>{pct(sel.service_ratio)} OF PRIORITIES · {sel.energy_wh.toFixed(0)} Wh · {sel.power_w} W{sel.weight>1?` · WEIGHT ×${sel.weight}`:''}</small></h4>
     <p><b>Powered:</b> {sel.selected.join(', ')||'—'}</p><p><b>Deferred:</b> {sel.deferred.join(', ')||'—'}</p><p className="note">Equal-split would have given this home {sel.baseline_utility} points; pooled gives {sel.utility}.</p>
     <button className="ghost-button" disabled={qBusy} onClick={()=>verify(pick!,sel)}>{qBusy?<><LoaderCircle size={14} className="spin"/> QAOA JOB {qJob?.status?.toUpperCase()||'SUBMITTED'}…</>:<><Atom size={14}/> VERIFY THIS HOME WITH QAOA</>}</button>
     {qError&&<div className="error">{qError}</div>}
     {q&&<div className="q-verify">{q.quantum.quantum_metadata?<>QAOA on this home's allocated share: best measured utility <b>{q.quantum.allocation?.objective_value??'none feasible'}</b> vs exact <b>{q.classical.allocation?.objective_value}</b> · {q.quantum.quantum_metadata.qubits} qubits · {pct(q.quantum.quantum_metadata.feasible_selection_probability)} feasible shots · optimum measured in {pct(q.optimal_selection_probability||0)} of shots.</>:<>Quantum status: {q.quantum.status} — {q.quantum.message}</>}</div>}
     <p className="note">Hybrid decomposition: the classical society solver splits capacity; each home's sub-problem is small enough for a 14-qubit QAOA circuit.</p></div>}
   </article>
  </div>}
 </section>;
}
