import {Download,Maximize2} from 'lucide-react';
import figure from '../assets/anavo-architecture.svg?raw';

const href='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(figure);

const reading=[
 ['I · CLIENT','Households (B2C) and housing societies (B2B) send one strict JSON contract.'],
 ['II · ORCHESTRATION','FastAPI validates physics, admits one heavy solve at a time and queues slow QAOA jobs.'],
 ['III · SOLVER PLANE','One formulation (P) feeds an exact classical branch and a QUBO → Ising → QAOA branch with a COBYLA feedback loop.'],
 ['IV · VERIFICATION','Every quantum sample and MILP plan passes an exact feasibility oracle before it is compared and shown.'],
];

/** Paper-style system figure; the same SVG file is embedded in the README. */
export default function Architecture(){
 return <section className="architecture section" id="architecture">
  <div className="feature-heading"><div><div className="section-label">[ 06 / ARCHITECTURE ]</div><h2>BUILT TO<br/><span>SCALE.</span></h2></div>
   <p>Households (B2C) and housing societies (B2B) share one engine. Small decisions go to QAOA where a 14-qubit simulator can verify them; large decisions use exact MILP; every answer is re-checked against the physical limits before it is shown.</p></div>
  <figure className="arch-figure">
   <div className="arch-scroll" tabIndex={0} aria-label="Architecture diagram, scroll horizontally on small screens" dangerouslySetInnerHTML={{__html:figure}}/>
   <figcaption><span>FIG. 1 — HYBRID CLASSICAL–QUANTUM ARCHITECTURE. ANIMATED EDGES SHOW LIVE DATA FLOW; NUMBERS ARE MEASURED.</span>
    <span className="arch-actions"><a href={href} target="_blank" rel="noreferrer"><Maximize2 size={13}/> FULL SIZE</a><a href={href} download="anavo-architecture.svg"><Download size={13}/> DOWNLOAD SVG</a></span></figcaption>
  </figure>
  <div className="arch-reading">{reading.map(([t,d])=><div key={t}><b>{t}</b><small>{d}</small></div>)}</div>
  <p className="note honest">Honest limits: Aer is a noiseless simulator, not quantum hardware; at these sizes the classical solvers are faster; COBYLA hits its evaluation budget; appliance ratings are cited figures or labelled estimates. No quantum speedup is claimed.</p>
 </section>;
}
