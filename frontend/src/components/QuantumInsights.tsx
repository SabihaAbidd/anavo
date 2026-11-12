import type {Comparison,Scenario} from '../api';

const pct=(v:number)=>`${(v*100).toFixed(1)}%`;

function names(bits:string,scenario:Scenario){return scenario.appliances.filter((_,i)=>bits[i]==='1').map(a=>a.name).join(' + ')||'Nothing on';}

/** Every number here is read from the actual Aer measurement and COBYLA trace returned by the API. */
export default function QuantumInsights({comparison,scenario}:{comparison:Comparison;scenario:Scenario}){
 const q=comparison.quantum.quantum_metadata;if(!q)return null;
 const optimum=comparison.classical.allocation?.bitstring;
 const top=q.selection_distribution.slice(0,10);const maxP=Math.max(...top.map(t=>t.probability),0.01);
 const hist=q.objective_history;const lo=Math.min(...hist),hi=Math.max(...hist);const span=hi-lo||1;
 const path=hist.map((v,i)=>`${i?'L':'M'}${(i/(Math.max(hist.length-1,1)))*560+20},${170-((v-lo)/span)*150}`).join(' ');
 const land=q.landscape;const maxE=Math.max(...land.map(p=>p.energy_wh),scenario.battery_wh,1);const maxU=Math.max(...land.map(p=>p.utility),1);
 const ops=Object.entries(q.circuit_operations).filter(([k])=>k!=='barrier').sort((a,b)=>b[1]-a[1]);
 return <section className="insights" aria-label="Quantum execution insights">
  <div className="insights-head"><span className="section-label">[ QUANTUM INSIGHTS / FROM REAL AER MEASUREMENTS ]</span><h3>INSIDE THE <span>QAOA RUN</span></h3>
   <p>The quantum circuit does not output one answer. It outputs a probability distribution over all {2**q.appliance_qubits} appliance decisions. Below is what the simulator actually measured in {q.shots.toLocaleString()} shots.</p></div>
  <div className="kpi-row">
   <div><strong>{comparison.optimal_selection_probability!=null?pct(comparison.optimal_selection_probability):'—'}</strong><label>of shots measured the exact optimum</label></div>
   <div><strong>{pct(q.feasible_selection_probability)}</strong><label>of shots were physically feasible</label></div>
   <div><strong>{q.qubits}</strong><label>{q.appliance_qubits} decision + {q.slack_qubits} slack qubits</label></div>
   <div><strong>{q.optimizer_evaluations}</strong><label>COBYLA circuit evaluations</label></div>
  </div>
  <div className="insight-grid">
   <article className="insight-card wide"><header><span>01 / MEASUREMENT HISTOGRAM</span><small>TOP {top.length} APPLIANCE DECISIONS (SLACK QUBITS MARGINALISED)</small></header>
    <div className="histogram">{top.map(t=><div key={t.appliance_bitstring} className={'bar-row '+(t.feasible?'ok':'bad')+(t.appliance_bitstring===optimum?' best':'')}>
     <code>{t.appliance_bitstring}</code><span className="bar-label">{names(t.appliance_bitstring,scenario)}{t.appliance_bitstring===optimum&&<b> ★ EXACT OPTIMUM</b>}</span>
     <div className="bar"><i style={{width:`${t.probability/maxP*100}%`}}/></div><span className="bar-value">{pct(t.probability)} · U{t.utility}</span></div>)}</div>
    <p className="legend"><i className="ok"/>feasible <i className="bad"/>breaks a limit <i className="best"/>exact optimum. Infeasible samples are filtered out by ANAVO's independent checker — never recommended.</p></article>
   <article className="insight-card"><header><span>02 / OPTIMIZER CONVERGENCE</span><small>EXPECTED QUBO ENERGY PER EVALUATION</small></header>
    <svg viewBox="0 0 600 190" className="chart" role="img" aria-label="COBYLA objective history"><path d={path} className="line"/><line x1="20" x2="580" y1="170" y2="170" className="axis"/><text x="20" y="186">eval 1</text><text x="540" y="186">eval {hist.length}</text><text x="24" y="16">{hi.toFixed(0)}</text><text x="24" y="166">{lo.toFixed(0)}</text></svg>
    <p className="note">Lower is better. COBYLA tunes {q.parameters.length} angles (γ, β per layer, depth {q.qaoa_depth}) with {q.optimizer_evaluations} evaluations across restarts; it hit its evaluation budget, so we report best samples rather than claim convergence.</p></article>
   <article className="insight-card"><header><span>03 / QUBIT MAP</span><small>HOW THE PROBLEM IS ENCODED</small></header>
    <div className="qubits">{q.qubit_roles.map((r,i)=><div key={r} className={i<q.appliance_qubits?'q-dec':'q-slack'}><b>q{i}</b><span>{r.replace('_slack_',' slack ')}</span></div>)}</div>
    <p className="note">Decision qubits: 1 = appliance on. Slack qubits turn "≤ battery" and "≤ inverter" into exact equations the QUBO can penalise (penalty A = {q.penalty}).</p></article>
   <article className="insight-card"><header><span>04 / CIRCUIT</span><small>TRANSPILED FOR AER</small></header>
    <div className="ops">{ops.map(([k,v])=><div key={k}><b>{v}</b><span>{k.toUpperCase()}</span></div>)}<div><b>{q.circuit_depth}</b><span>DEPTH</span></div></div>
    <p className="note">RZZ gates carry the pairwise QUBO couplings (cost layer); RX gates are the mixer. {q.qaoa_depth} alternating layers, then measurement.</p></article>
   {land.length>0&&<article className="insight-card"><header><span>05 / SOLUTION LANDSCAPE</span><small>ALL {land.length} DECISIONS · DOT SIZE = MEASURED PROBABILITY</small></header>
    <svg viewBox="0 0 600 230" className="chart" role="img" aria-label="Energy versus utility for all appliance decisions">
     <line x1={40+scenario.battery_wh/maxE*540} x2={40+scenario.battery_wh/maxE*540} y1="10" y2="200" className="limit"/><text x={44+scenario.battery_wh/maxE*540} y="22">battery {scenario.battery_wh} Wh</text>
     <line x1="40" x2="580" y1="200" y2="200" className="axis"/><text x="40" y="222">0 Wh</text><text x="520" y="222">{maxE.toFixed(0)} Wh</text>
     {land.map(p=><circle key={p.appliance_bitstring} cx={40+p.energy_wh/maxE*540} cy={200-p.utility/maxU*180} r={3+Math.sqrt(p.probability)*28} className={p.appliance_bitstring===optimum?'pt best':p.feasible?'pt ok':'pt bad'}><title>{`${p.appliance_bitstring}: U${p.utility}, ${p.energy_wh} Wh, ${p.power_w} W, ${pct(p.probability)}`}</title></circle>)}
    </svg><p className="note">Up = more value, right = more energy. The best answer is the highest feasible dot; QAOA should put its biggest dots near it.</p></article>}
  </div>
 </section>;
}
