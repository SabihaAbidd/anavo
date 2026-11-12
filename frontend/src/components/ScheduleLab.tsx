import {useState} from 'react';
import {ArrowRight,LoaderCircle,Sun,Clock} from 'lucide-react';
import {request} from '../api';
import type {Scenario,Schedule} from '../api';

/** Hour-by-hour plan from the exact MILP scheduler, rendered as a Gantt chart plus battery/load curves. */
export default function ScheduleLab({scenario,onLoadHouse}:{scenario:Scenario;onLoadHouse:()=>void}){
 const [startHour,setStartHour]=useState(18);const [solar,setSolar]=useState(0);
 const [plan,setPlan]=useState<Schedule|null>(null);const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 async function run(){setBusy(true);setError('');setPlan(null);try{setPlan(await request<Schedule>('/api/schedule',{scenario,start_hour:startHour,solar_kwp:solar}));}catch(e){setError(e instanceof Error?e.message:'Scheduling failed.');}finally{setBusy(false);}}
 const slots=plan?.timeline||[];const n=Math.max(slots.length,1);
 const maxLoad=Math.max(scenario.inverter_w,...slots.map(s=>s.load_w),1);
 const W=640,left=150,colW=(W-left-10)/n;
 const battery=slots.map((s,i)=>`${i?'L':'M'}${left+(i+1)*colW},${150-s.battery_wh/Math.max(scenario.battery_wh,1)*130}`).join(' ');
 return <section className="schedule section" id="schedule">
  <div className="feature-heading"><div><div className="section-label">[ 03 / TIME MACHINE ]</div><h2>EVERY HOUR.<br/><span>PLANNED.</span></h2></div>
   <p>The control room above reserves inverter power for all appliances at once. Real homes don't work that way. This exact <b>MILP scheduler</b> decides <i>when</i> each appliance runs — so the pump and the washing machine can take turns instead of one being cut. It tracks battery charge every slot and can add rooftop solar.</p></div>
  <div className="control-panel"><div className="panel-bar"><span><Clock size={15}/> SCHEDULE SETTINGS — USES THE MANIFEST FROM THE CONTROL ROOM</span><button onClick={onLoadHouse}>LOAD PAKISTANI HOUSE EXAMPLE</button></div>
   <div className="config-top three"><label>OUTAGE STARTS AT<div className="number-field"><input type="number" min="0" max="23.5" step="0.5" value={startHour} onChange={e=>{setStartHour(Number(e.target.value));setPlan(null);}}/><span>H</span></div></label>
    <label><span><Sun size={12}/> ROOFTOP SOLAR</span><div className="number-field"><input type="number" min="0" max="50" step="0.5" value={solar} onChange={e=>{setSolar(Number(e.target.value));setPlan(null);}}/><span>kWp</span></div></label>
    <div className="run-cell"><button className="primary-button run" disabled={busy} onClick={run}>{busy?<><LoaderCircle size={18} className="spin"/> SOLVING MILP…</>:<>PLAN HOUR BY HOUR <ArrowRight size={19}/></>}</button></div></div>
   <div className="panel-note">{scenario.name.toUpperCase()} / {scenario.appliances.length} LOADS / {scenario.battery_wh} Wh / {scenario.inverter_w} W / {scenario.outage_h} H WINDOW · SOLAR USES ESMAP 5.67 kWh/m²/DAY × 0.75 PERFORMANCE RATIO</div>
   {error&&<div className="error" role="alert">REQUEST NOT COMPLETED / {error}</div>}</div>
  {plan&&!plan.feasible&&<p className="no-result big">{plan.message}</p>}
  {plan&&plan.feasible&&<div className="schedule-result">
   <div className="kpi-row">
    <div><strong>{plan.utility}</strong><label>utility with scheduling</label></div>
    <div><strong>{plan.simultaneous_utility??'—'}</strong><label>utility if everything ran at once</label></div>
    <div className={plan.gain_vs_simultaneous?'gain':''}><strong>{plan.gain_vs_simultaneous!=null&&plan.gain_vs_simultaneous>0?'+':''}{plan.gain_vs_simultaneous??'—'}</strong><label>gain from smart timing</label></div>
    <div><strong>{plan.peak_load_w?.toFixed(0)} W</strong><label>peak load (limit {scenario.inverter_w} W)</label></div>
    <div><strong>{plan.final_battery_wh?.toFixed(0)} Wh</strong><label>left in battery{plan.solar_generated_wh?` · ${plan.solar_generated_wh.toFixed(0)} Wh solar`:''}</label></div>
   </div>
   <article className="insight-card wide"><header><span>GANTT / WHICH APPLIANCE RUNS WHEN</span><small>{plan.slots} SLOTS × {plan.slot_h} H · {plan.status.toUpperCase()} · {plan.runtime_s.toFixed(3)} s</small></header>
    <svg viewBox={`0 0 ${W} ${plan.appliances.length*26+34}`} className="chart gantt" role="img" aria-label="Appliance schedule">
     {slots.map((s,i)=><g key={i}><line x1={left+i*colW} x2={left+i*colW} y1="0" y2={plan.appliances.length*26} className="grid"/>{(n<=16||i%Math.ceil(n/12)===0)&&<text x={left+i*colW+2} y={plan.appliances.length*26+16}>{s.start}</text>}</g>)}
     {plan.appliances.map((a,r)=><g key={a.name}><text x="0" y={r*26+17} className={a.selected?'':'muted'}>{a.mandatory?'★ ':''}{a.name.slice(0,18)}</text>
      {a.selected&&a.start_slot!=null?<rect x={left+a.start_slot*colW+1} y={r*26+4} width={a.duration_h/plan.slot_h*colW-2} height="18" className={a.mandatory?'bar-m':'bar-on'}><title>{`${a.name}: ${a.start}–${a.end}, ${a.power_w} W`}</title></rect>:<text x={left+4} y={r*26+17} className="muted">deferred</text>}</g>)}
    </svg></article>
   <article className="insight-card wide"><header><span>LOAD VS INVERTER LIMIT · BATTERY LEVEL</span><small>BARS = WATTS DRAWN · LINE = BATTERY Wh</small></header>
    <svg viewBox={`0 0 ${W} 175`} className="chart" role="img" aria-label="Load and battery timeline">
     <line x1={left} x2={W-10} y1={150-scenario.inverter_w/maxLoad*130} y2={150-scenario.inverter_w/maxLoad*130} className="limit"/><text x="0" y={154-scenario.inverter_w/maxLoad*130}>inverter {scenario.inverter_w} W</text>
     {slots.map((s,i)=><rect key={i} x={left+i*colW+2} y={150-s.load_w/maxLoad*130} width={colW-4} height={s.load_w/maxLoad*130} className="load"><title>{`${s.start}: ${s.load_w} W · ${s.running.join(', ')}`}</title></rect>)}
     {slots.some(s=>s.solar_wh>0)&&slots.map((s,i)=><rect key={'s'+i} x={left+i*colW+colW/2-3} y={150-Math.min(130,s.solar_wh/plan.slot_h/maxLoad*130)} width="6" height={Math.min(130,s.solar_wh/plan.slot_h/maxLoad*130)} className="solar"/>)}
     <path d={`M${left},${20} `+battery.replace(/^M/,'L')} className="line"/><line x1={left} x2={W-10} y1="150" y2="150" className="axis"/>
    </svg></article>
  </div>}
 </section>;
}
