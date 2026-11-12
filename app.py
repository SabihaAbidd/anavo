"""ANAVO Streamlit decision-support dashboard."""
from dataclasses import asdict
import hashlib
import json
import pandas as pd
import streamlit as st
from src.models import Appliance, Scenario
from src.scenarios import presets
from src.evaluation import compare
from src.optimization import build_qubo, QuantumLimitError

st.set_page_config(page_title="ANAVO | Energy resilience", page_icon="💡", layout="wide")
st.markdown("""<style>
.block-container{max-width:1280px;padding-top:2.2rem}
h1{letter-spacing:.16em;font-weight:800!important}
.eyebrow{color:#F8BE62;letter-spacing:.2em;font-size:.75rem;font-weight:700}
.hero{color:#a9b8cc;font-size:1.2rem;max-width:780px;margin-bottom:1.5rem}
[data-testid="stMetric"]{background:#141d2b;border:1px solid #243044;padding:18px;border-radius:12px}
div.stButton>button[kind="primary"]{border-radius:8px;font-weight:700}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="eyebrow">ENERGY & SMART INFRASTRUCTURE · PAKISTAN</div>',unsafe_allow_html=True)
st.title("ANAVO")
st.markdown('<div class="hero">When power is limited, intelligence shouldn’t be.</div>',unsafe_allow_html=True)
st.write("Make limited backup energy go further. Configure your outage, protect mandatory loads, and compare an exact allocation with simulated quantum optimization.")

with st.sidebar:
    st.subheader("Your backup system")
    preset_name=st.selectbox("Example scenario",list(presets()),key="preset")
    preset=presets()[preset_name]
    battery=st.number_input("Usable battery energy (Wh)",min_value=0.0,value=float(preset.battery_wh),step=30.0,key=f"battery_{preset_name}")
    inverter=st.number_input("Inverter limit (W)",min_value=0.0,value=float(preset.inverter_w),step=10.0,key=f"inverter_{preset_name}")
    outage=st.number_input("Outage duration (hours)",min_value=0.25,value=float(preset.outage_h),step=.25,key=f"outage_{preset_name}")
    st.caption("Enter energy available to appliances after battery/inverter losses. 1 kWh = 1,000 Wh.")
    st.divider()
    st.subheader("Quantum experiment")
    depth=st.slider("QAOA layers (p)",1,4,2)
    shots=st.select_slider("Measurement shots",options=[256,512,1024,2048,4096],value=2048)
    evaluations=st.slider("Evaluations per restart",20,200,80,20)
    seed=st.number_input("Reproducible seed",min_value=0,max_value=2**31-1,value=42,step=1)
    st.caption("Qiskit Aer · noiseless simulator · 2 restarts · 14-qubit limit. No hardware or quantum speedup claim.")

st.subheader("01 / Choose what matters")
st.caption("Utility is your priority score. Essential labels critical services; mandatory enforces operation as a hard requirement. Each load runs for its requested duration, with simultaneous power reserved conservatively.")
table=st.data_editor(pd.DataFrame([asdict(a) for a in preset.appliances]),num_rows="dynamic",hide_index=True,
    key=f"loads_{preset_name}",width="stretch",column_config={
        "name":st.column_config.TextColumn("Appliance",required=True),
        "power_w":st.column_config.NumberColumn("Power (W)",min_value=0.0,required=True),
        "duration_h":st.column_config.NumberColumn("Duration (h)",min_value=0.0,required=True),
        "utility":st.column_config.NumberColumn("Utility",min_value=0.0,required=True),
        "essential":st.column_config.CheckboxColumn("Essential"),
        "mandatory":st.column_config.CheckboxColumn("Mandatory")})
try:
    loads=[]
    for row in table.to_dict("records"):
        # Blank added rows must be completed, never silently dropped.
        loads.append(Appliance(str(row["name"]) if pd.notna(row["name"]) else "",
            float(row["power_w"]),float(row["duration_h"]),float(row["utility"]),
            bool(row["essential"]) if pd.notna(row["essential"]) else False,
            bool(row["mandatory"]) if pd.notna(row["mandatory"]) else False))
    scenario=Scenario(preset_name,tuple(loads),float(battery),float(inverter),float(outage))
except (ValueError,TypeError) as exc:
    st.error(f"Please correct your inputs: {exc}")
    st.stop()

requested=sum(a.energy_wh for a in loads)
cols=st.columns(4)
for col,label,value in zip(cols,["Outage","Available energy","Requested energy","Inverter capacity"],
        [f"{outage:g} h",f"{battery:g} Wh",f"{requested:g} Wh",f"{inverter:g} W"]):
    col.metric(label,value)
try:
    qubo=build_qubo(scenario)
    st.caption(f"Quantum encoding: {qubo.n_appliances} appliance qubits + {qubo.n_qubits-qubo.n_appliances} slack qubits = {qubo.n_qubits} total.")
except QuantumLimitError as exc:
    st.warning(str(exc)+" The exact solver remains available.")

fingerprint=hashlib.sha256(json.dumps(dict(scenario=asdict(scenario),depth=depth,shots=shots,evaluations=evaluations,seed=seed),sort_keys=True).encode()).hexdigest()
if st.session_state.get("fingerprint") != fingerprint:
    st.session_state.pop("result",None)
if st.button("Optimize backup allocation",type="primary",key="optimize"):
    with st.spinner("Solving the exact baseline and running the Qiskit experiment…"):
        try:
            st.session_state.result=compare(scenario,depth=depth,shots=shots,maxiter=evaluations,seed=int(seed))
            st.session_state.fingerprint=fingerprint
        except Exception as exc:
            st.error(f"Optimization failed: {type(exc).__name__}: {exc}")

if "result" in st.session_state:
    result=st.session_state.result
    classical=result["classical"]
    quantum=result["quantum"]
    st.subheader("02 / Your energy allocation")
    if classical["best"] is None:
        st.error("No feasible allocation can satisfy every mandatory load. Increase capacity, reduce requested durations, or explicitly change the mandatory requirements.")
    else:
        best=classical["best"]
        st.success("Exact classical recommendation: "+(", ".join(best["selected"]) or "No appliances selected"))
        cols=st.columns(4)
        for col,label,value in zip(cols,["Utility served","Essential loads","Energy utilization","Energy remaining"],
            [f"{best['utility']:g}",f"{best['essential_served']} / {best['essential_total']}",
             f"{100*best['energy_wh']/battery:.1f}%" if battery else "0%",f"{best['remaining_wh']:g} Wh"]):
            col.metric(label,value)
        st.dataframe(pd.DataFrame([dict(Appliance=a.name,Status="Selected" if x else "Unselected",
            Energy_Wh=a.energy_wh,Power_W=a.power_w,Utility=a.utility,Mandatory=a.mandatory)
            for a,x in zip(loads,best["selection"])]),hide_index=True,width="stretch")
        st.write(f"This allocation maximizes your stated utility while using {best['energy_wh']:g} of {battery:g} Wh and reserving {best['power_w']:g} of {inverter:g} W. All mandatory loads are served.")
        if best["unselected"]:
            st.caption("Unselected: "+", ".join(best["unselected"])+". No alternative feasible selection has higher total utility; equal-utility ties use input-order bitstrings.")

    st.subheader("03 / Quantum vs classical")
    if quantum["status"] == "unavailable":
        st.warning("Quantum execution unavailable: "+quantum["reason"])
        st.info("The recommendation above is the exact classical baseline. Install requirements and rerun to obtain real Qiskit measurements.")
    else:
        qbest=quantum["best"]
        st.dataframe(pd.DataFrame([
            dict(Method="Exact classical",Utility=classical["best"]["utility"] if classical["best"] else None,
                Feasible=classical["best"] is not None,Seconds=classical["runtime_s"],
                Bits=classical["best"]["bitstring"] if classical["best"] else "—"),
            dict(Method="QAOA · simulated",Utility=qbest["utility"] if qbest else None,
                Feasible=qbest is not None,Seconds=quantum["runtime_s"],Bits=qbest["bitstring"] if qbest else "—")]),hide_index=True,width="stretch")
        st.write(f"{quantum['qubits']} qubits · p={quantum['qaoa_depth']} · {quantum['shots']:,} shots · COBYLA · {quantum['optimizer_evaluations']} objective evaluations")
        st.write(f"Measured feasible selections: {quantum['feasible_selection_probability']:.1%}. Full QUBO encoding feasibility: {quantum['feasible_encoding_probability']:.1%}.")
        if result["objective_gap"] is not None:
            st.write(f"Best sampled feasible utility gap: {result['objective_gap']:g} ({result['relative_gap']:.1%}).")
        else:
            st.warning("No comparable feasible pair; the objective gap is undefined.")
        if qbest:
            st.write("Best quantum-sampled feasible selection: "+(", ".join(qbest["selected"]) or "No appliances"))
        st.caption("Physical appliance selections are checked independently of slack-register validity. No candidate repair or classical optimum injection is performed.")
        distribution=pd.DataFrame(quantum["distribution"])
        top=distribution.sort_values("count",ascending=False).head(20)
        st.bar_chart(top.set_index("measured_bitstring")["count"],color="#F8BE62")
        with st.expander("Measurement details and optimizer diagnostics"):
            st.dataframe(distribution,hide_index=True)
            st.json({k:quantum[k] for k in ("parameters","optimizer_runs","hamiltonian_scale","penalty","seed","iteration_note")})
            st.line_chart(pd.DataFrame({"Expected QUBO energy":quantum["objective_history"]}))
    st.download_button("Download experiment JSON",json.dumps(result,indent=2,allow_nan=False),
                       "anavo_experiment.json","application/json")

with st.expander("04 / How ANAVO works",expanded="result" not in st.session_state):
    st.markdown("""**1. Model the request.** Each appliance has one on/off decision. Energy is power × hours; W and Wh constrain different resources.

**2. Establish the exact answer.** Enumerate every selection and reject energy, power, or mandatory-load violations.

**3. Encode a quantum optimization problem.** Binary slack variables turn inequalities into equalities. Squared penalties enforce these equalities in a QUBO. The substitution x=(1−Z)/2 produces the Ising cost Hamiltonian.

**4. Run hybrid QAOA.** Qiskit prepares a superposition and alternates cost and mixing gates. SciPy tunes the angles using noiseless Aer statevector expectations, then Aer measures the optimized circuit for the reported shots.

**5. Check what was measured.** Decode Qiskit's reversed display order, check physical constraints, and compare the best feasible sampled utility with the independent exact optimum.

**Limits.** This is a small, noiseless simulator experiment. It establishes neither quantum speedup nor household safety. Illustrative device powers, fixed durations, and conservative simultaneous operation omit switching schedules, surge currents, battery degradation, solar forecasts, and appliance duty cycles. Essential labels do not create hidden utility bonuses. Mandatory requests are never automatically relaxed.""")
st.caption("ANAVO · Quantum-assisted energy resilience · Decision support, not electrical control")
