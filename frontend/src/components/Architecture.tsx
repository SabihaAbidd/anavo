/** Static system map so judges can see how each feature flows through the stack. */
const layers=[
 {label:'CLIENT',items:[['React + TypeScript + Vite','Control room, timeline, society grid, insights'],['GSAP + Canvas + SVG','Opening sequence and live charts — no chart library']]},
 {label:'API',items:[['FastAPI + Pydantic (strict)','/api/optimize · /api/compare · /api/schedule · /api/fleet/optimize · /api/data/pakistan'],['Async job queue','/api/jobs — QAOA and large fleets run off the request path; poll by job id'],['Admission control','One heavy solve per process; extra requests get HTTP 429 instead of overloading']]},
 {label:'ENGINES',items:[['Exact enumeration','Household reference optimum (≤20 appliances)'],['MILP scheduler (HiGHS)','Time slots, per-slot inverter limit, battery state of charge, solar'],['Society MILP (HiGHS)','500 homes · 8,000 decisions · fairness floor · equal-split baseline'],['QUBO → Ising → QAOA','Slack-qubit encoding, Qiskit circuit, COBYLA, Aer shots, independent feasibility check']]},
 {label:'EVIDENCE',items:[['Automated tests','Physics, QUBO consistency, schedules, fleets, API contracts, real circuits'],['Reproducible runs','Seed 42, pinned versions, saved benchmark JSON in results/']]},
];
export default function Architecture(){
 return <section className="architecture section" id="architecture">
  <div className="feature-heading"><div><div className="section-label">[ 06 / ARCHITECTURE ]</div><h2>BUILT TO<br/><span>SCALE.</span></h2></div>
   <p>Households (B2C) and housing societies (B2B) share one engine. Small decisions go to QAOA where a 14-qubit simulator can verify them; large decisions use exact MILP; every answer is re-checked against the physical limits before it is shown.</p></div>
  <div className="arch">{layers.map((l,i)=><div key={l.label} className="arch-layer"><span className="arch-label">{String(i+1).padStart(2,'0')} / {l.label}</span><div className="arch-items">{l.items.map(([t,d])=><div key={t}><b>{t}</b><small>{d}</small></div>)}</div>{i<layers.length-1&&<i className="arch-arrow">↓</i>}</div>)}</div>
  <p className="note honest">Honest limits: Aer is a noiseless simulator, not quantum hardware; at these sizes the classical solvers are faster; COBYLA hits its evaluation budget; appliance ratings are editable estimates. No quantum speedup is claimed.</p>
 </section>;
}
