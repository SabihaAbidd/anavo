import {Plus,ArrowUpRight} from 'lucide-react';
import type {Dataset,DataAppliance} from '../api';

/** Cited Pakistan context: outage bands, solar resource and an appliance library that feeds the control room. */
export default function PakistanData({data,onAdd,outage}:{data:Dataset|null;onAdd:(a:DataAppliance)=>void;outage:number}){
 if(!data)return null;
 const maxH=Math.max(...data.outage_profiles.map(p=>p.daily_outage_h),1);
 const cite=(basis:string)=>basis==='estimate'?<span className="badge est">ESTIMATE</span>:<a className="badge" href={data.sources[basis]?.url} target="_blank" rel="noreferrer">SOURCE ↗</a>;
 return <section className="pakdata section" id="data">
  <div className="feature-heading"><div><div className="section-label">[ 05 / PAKISTAN DATA ]</div><h2>GROUNDED IN<br/><span>PAKISTAN.</span></h2></div>
   <p>{data.disclaimer}</p></div>
  <div className="insight-grid">
   <article className="insight-card"><header><span>DAILY LOAD-SHEDDING BY FEEDER</span><small>NEPRA BANDS & REPORTED AVERAGES</small></header>
    <div className="compare-bars">{data.outage_profiles.map(p=><div key={p.id}><span>{p.label}</span><div className="bar"><i style={{width:`${p.daily_outage_h/maxH*100}%`}}/></div><b>{p.daily_outage_h} h</b></div>)}</div>
    <p className="note">{data.outage_profiles.map(p=>p.note).join(' ')} The society planner can use these as one continuous worst-case block.</p>
    <div className="cites">{[...new Set(data.outage_profiles.map(p=>p.basis))].map(b=><a key={b} href={data.sources[b].url} target="_blank" rel="noreferrer">{data.sources[b].title} <ArrowUpRight size={11}/></a>)}</div></article>
   <article className="insight-card"><header><span>SOLAR RESOURCE</span><small>WORLD BANK ESMAP ESTIMATE</small></header>
    <div className="big-number">{data.solar.ghi_kwh_m2_day}<span>kWh/m²/day</span></div>
    <p className="note">{data.solar.note} Used by the hour-by-hour planner when you add rooftop solar.</p>
    <div className="cites"><a href={data.sources[data.solar.basis].url} target="_blank" rel="noreferrer">{data.sources[data.solar.basis].title} <ArrowUpRight size={11}/></a></div></article>
  </div>
  <article className="insight-card wide"><header><span>APPLIANCE LIBRARY</span><small>CLICK + TO ADD TO YOUR CONTROL-ROOM MANIFEST</small></header>
   <div className="table-scroll"><table className="data-table"><thead><tr><th>APPLIANCE</th><th>W</th><th>HOURS</th><th>PRIORITY</th><th>BASIS</th><th><span className="sr-only">Add</span></th></tr></thead>
    <tbody>{data.appliances.map(a=><tr key={a.name}><td>{a.mandatory?'★ ':''}{a.name}</td><td>{a.power_w}</td><td>{Math.min(a.hours,outage)}</td><td>{a.priority}</td><td>{cite(a.basis)}</td><td><button className="remove" aria-label={`Add ${a.name}`} onClick={()=>onAdd(a)}><Plus size={14}/></button></td></tr>)}</tbody></table></div>
   <p className="note">Fan wattages follow NEECA-related reporting (conventional ≈80–130 W, 3-star ≈50–65 W, marketed inverter fans ≈30 W). Other ratings are typical nameplate estimates — edit them to match your own appliances.</p></article>
 </section>;
}
