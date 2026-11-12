# Three-minute pitch

Backend update: ANAVO now exposes FastAPI/Pydantic JSON endpoints around the existing solver. The Streamlit demo below is preserved; the future React frontend awaits a separate design brief. Until FastAPI installs and actual endpoint tests run, describe the backend as implemented with tested schemas/services, not a verified live API.

**Use this script with an honest live dependency check. Quantum execution is currently blocked in the development environment. Do not announce a measured quantum result until the app actually displays one.**

## 0:00–0:30 — Problem

Imagine the power goes out for three hours. Your household has a battery, a fan, some lights, a router and a laptop. The question is not just how much electricity is left. It is which services that electricity should protect. Choosing everything can exceed the battery budget or the inverter rating. ANAVO turns that household decision into an explicit, explainable optimization problem, motivated by resilience needs in Pakistan.

## 0:30–1:00 — Product

ANAVO means to light up. Our tagline is: when power is limited, intelligence shouldn't be. Enter usable battery energy, inverter power and outage duration. Then edit the appliance requests and their priorities. You can label essential services and require mandatory loads. Those requirements are honest hard constraints: if the battery cannot serve them, the system tells you instead of quietly changing your priorities.

## 1:00–1:45 — Technical method

Each appliance becomes one binary decision. We maximize total stated utility while enforcing energy in watt-hours and power in watts. An independent exact solver checks every possible subset on these small instances. For the quantum path, integer slack variables and squared penalties turn the same constraints into a QUBO. We transform that into an Ising cost Hamiltonian. QAOA alternates cost and mixing operations while a classical optimizer adjusts the circuit angles. The implementation uses real Qiskit circuits and Aer simulation, with separate measurement and feasibility checks. We also exhaustively verify that the QUBO ground states match the constrained optimum.

## 1:45–2:30 — Demonstration

Here is our evening example: 240 watt-hours and a 100-watt inverter. The exact optimizer chooses the fan, lights and router: utility 24, using 180 watt-hours and 60 watts. Reducing energy to 90 watt-hours leaves the lights and mandatory router. Reducing it to 15 makes the request infeasible, because the router alone needs 30. The comparison section separates the exact recommendation from quantum samples. When quantum execution succeeds, it displays measured counts, qubits, feasible probability, runtime and objective gap. If dependencies are unavailable, it explicitly says so; we never relabel the classical answer as quantum.

## 2:30–3:00 — Evidence and impact

Our executed checks cover the physical constraints, exact solution, QUBO and Ising agreement, and dashboard behavior. Circuit execution and quantum comparison still require completion in the current restricted environment. We claim no quantum speedup. The contribution is a transparent Pakistan-focused prototype for exploring resilient energy allocation with both classical verification and a quantum formulation. Next come realistic battery data, time-slot scheduling and hardware experiments. ANAVO helps make every available watt-hour a deliberate choice.

After successful quantum execution, replace only the pending-status sentence with the actual benchmark's qubits, shots, feasible probability and gap. Keep the speedup limitation. Rehearse to three minutes; trim the technical paragraph if the demo takes longer.
