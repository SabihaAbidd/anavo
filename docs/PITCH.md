# ANAVO three-minute pitch

Use the measured local backend results below. Demonstrate the React frontend at localhost:5173, with FastAPI running on port 8000. Swagger remains available at localhost:8000/docs. Publish the latest source/results before presenting a repository link as the completed milestone.

## 0:00-0:30 - The problem

Imagine a three-hour power outage. Your household has a battery, a fan, lights, a router and a laptop. There is enough electricity for some services, but running everything could exceed the energy budget or inverter rating. Which appliances should get that limited backup? ANAVO makes that decision explicit and explainable, motivated by household energy resilience in Pakistan.

## 0:30-1:00 - Introducing ANAVO

Our tagline is: when power is limited, intelligence shouldn't be. ANAVO takes usable battery energy, inverter power and appliance requests. Users assign utility scores and can mark mandatory loads. Mandatory really means mandatory: if the available energy cannot support those requirements, the system reports infeasibility. The application architecture is React, FastAPI and a reusable optimization engine. The verified backend is ready; the custom React design is the next separately authorized phase.

## 1:00-1:45 - The quantum method

Each appliance is a binary on-or-off decision. We maximize total stated utility within energy and power limits. An independent exact solver checks every subset on these small examples. The quantum path encodes the same constraints using binary slack and squared penalties, producing a QUBO and then an Ising Hamiltonian. QAOA alternates cost and mixing gates while a classical optimizer tunes the angles. We execute actual Qiskit circuits on the Aer simulator and check the measured bitstrings against the original physical constraints. We do not inject the exact answer into the quantum result.

## 1:45-2:30 - Live demonstration and measured results

In the API documentation, submit the evening example: 240 watt-hours and a 100-watt inverter. The exact allocation selects the fan, lights and router, using 180 watt-hours and 60 watts for utility 24. Then show the recorded quantum benchmark comparison. With ample backup, the best quantum sample serves all appliances for utility 30. With limited battery, it serves lights and the mandatory router for utility 15. Both match the exact optima. Each run uses two QAOA layers, 2,048 shots and seed 42. The impossible mandatory case returns no feasible allocation; it never quietly drops the requirement.

## 2:30-3:00 - Evidence, limitations and impact

All 72 backend tests pass, and an actual Uvicorn server passed 12 HTTP checks. Repeating the seeded benchmarks reproduced counts and optimized parameters. These are noiseless simulator results, not a quantum speedup claim: classical enumeration is much faster here. Only about a quarter of limited-battery shots were physically feasible, and parameter optimization reached its evaluation budget. ANAVO's value is transparent decision support and a verifiable quantum formulation. Next come the custom React interface, measured household profiles and more realistic scheduling, while keeping every result auditable.
