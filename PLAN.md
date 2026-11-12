# ANAVO execution plan

## 1. Problem and objectives
During a Pakistan household outage, choose a subset of requested appliance operations that maximizes stated utility within usable battery energy (Wh) and inverter power (W). Deliver an explainable decision-support prototype, a real simulated QAOA experiment, and an independent exact baseline. Theme: Energy & Smart Infrastructure. Users: households, students, and resilience researchers. This is not an appliance controller.

## 2. Solution and formulation
Binary x_i selects appliance i for its fixed requested duration t_i hours, with energy E_i=P_i*t_i. Maximize sum(u_i*x_i), subject to energy <= battery Wh, simultaneous power <= inverter W, and x_i=1 for mandatory loads. A separate essential flag is a preference/critical-service label; mandatory is a hard constraint. All requested durations must lie within the outage. Simultaneous operation is a conservative assumption even when durations differ. Battery input is usable AC-side energy, not nameplate battery capacity.

## 3. Algorithm decisions
**What:** exhaustive classical enumeration and QAOA over the same instance. **Why:** an exact reference establishes correctness on small examples. **How:** enumerate selections; encode integer resource inequalities with bounded binary slack; penalize squared equality residuals; convert x=(1-Z)/2; use H, RZ, RZZ, RX layers and SciPy COBYLA with Qiskit Aer. **Alternatives:** MILP is better for larger classical instances; time-slot models are beyond this MVP; hardware execution needs credentials and funding. **Tradeoffs:** slack increases qubits, so enforce explicit resource limits rather than truncate user inputs or claim larger quantum runs. **Validation:** exhaustive QUBO and Ising energy checks plus measured circuit outputs.

Penalty A=1+sum utilities exceeds the entire objective range when normalized residuals are integers. Exact decimal-to-rational conversion and GCD normalization avoid silent rounding. Omit redundant constraints; cap slack and simulator size explicitly. A mandatory-infeasible scenario is reported as infeasible; do not relax it silently.

## 4. Stack, architecture, and data flow
Primary backend: Python, FastAPI, Pydantic v2, NumPy, SciPy, Qiskit and Qiskit Aer. Uvicorn serves HTTP; HTTPX/TestClient and standard-library unittest validate endpoints. The existing Streamlit app is preserved as a legacy demonstration and receives no feature development. Future frontend: React, TypeScript, Vite, Tailwind CSS and Motion, deferred until the user supplies design references. No React implementation is authorized yet.

Request -> strict Pydantic contract -> framework-independent application service -> existing Scenario and optimization engine -> structured response model. Optimize selects classical or quantum explicitly; compare returns both with no hidden fallback. Synchronous FastAPI handlers run CPU work outside the event loop; bounded job admission rejects concurrent heavy requests. Restrict request sizes, quantum evaluations/shots/qubits, and CORS to explicitly configured local Vite origins. Do not expose this unauthenticated research service publicly without a separate deployment design.

## 5. UI/UX
Preserve the validated Streamlit UI unchanged. Define stable, documented JSON schemas for future React consumption, including selected/deferred appliance details, resource usage, infeasibility, measured metadata, and explicit unavailable states. Build GET /health, GET /api/scenarios, POST /api/optimize, POST /api/compare, and GET /api/algorithm-info. Provide OpenAPI /docs and /redoc; no frontend changes yet.

## 6. Milestones and time allocation (five-hour target)
1. Environment, Git, plan, architecture: 20 minutes.
2. Model and independently tested exact solver: 40 minutes.
3. QUBO, Ising, actual QAOA execution and validation: 80 minutes.
4. Streamlit UI and explanations: 60 minutes.
5. Tests, three benchmark scenarios, fixes: 45 minutes.
6. Report, research, pitch, demo guide: 30 minutes.
7. Repository verification and submission checklist: 25 minutes.
Proceed immediately after writing this plan. Commit each validated milestone; update TASKS.md with evidence.

## 7. Testing and evaluation
Test units, invalid/nonfinite input, energy/power boundaries, zero energy, essential vs mandatory semantics, deterministic ties, infeasibility, QUBO minima, Ising energies, bit order, real measured quantum results, quantum limits, and Streamlit AppTest/startup. Benchmark feasible, energy-constrained, and impossible mandatory cases using identical solver inputs. Record seeds, versions, shots, qubits, depth, optimizer evaluations/iterations, parameters, measured feasibility, gap, counts, and wall time. Distinguish selection feasibility from full slack-register feasibility. No fabricated results or quantum-speedup claims.

## 8. Research and documentation
Consult primary Qiskit/Aer docs, original QAOA research, energy optimization research, and NEPRA. Record source URLs, dates where available, relevance, and limits. Deliver README, architecture Mermaid diagram, mathematical derivation and worked example, research notes, measured technical report, three-minute pitch, demo guide, and submission checklist. Document what/why/how/alternatives/tradeoffs/validation for major decisions.

## 9. Git and GitHub
Preserve main and existing files/history. Verify authenticated GitHub identity, then inspect owner/anavo before creating exactly `anavo`, public, description "Quantum-Assisted Energy Resilience Optimization for Pakistan". Never create the previous proposed repository name. If anavo exists, inspect ownership/content/history and refuse to overwrite unrelated work or change private visibility silently. Confirm origin matches the authenticated account, stage only intended files, commit validated milestones and verify pushed HEAD through GitHub and git ls-remote. No force pushes, destructive locks/ACL repairs or credential disclosure. GitHub integration authorization is user-interactive when missing. Current session metadata restrictions may prevent commits even after GitHub connects; document those independently.

## 10. Risks, limitations, and scope
Risks: dependency installation, simulator exponential cost, poor shallow-QAOA performance, GitHub auth absence. Mitigate with supported low-level circuit APIs, small explicit instances, honest best-feasible measured candidates, and local commits. Classical fallback must always be labeled. No quantum advantage, hardware validation, measured Pakistan consumption dataset, battery degradation, surge-current guarantees, load switching, or actual time-slot scheduling. Device powers are illustrative; refrigerator/pump duty cycles need a richer model.

## 11. Definition of done and stretch goals
Done: app starts, editable inputs validate, independent exact solution and actual Qiskit measurements compare on identical scenarios, automated checks pass, measured benchmarks and complete documentation exist, commits exist, and remote pushed if authenticated access is available. Remaining blockers must be stated explicitly. Priority 1: scenarios, editable loads, export, charts. Stretch only after core: solar, community batteries, time slots, additional classical algorithms.

## 12. Immediate backend milestones
1. Recheck GitHub/authentication, locks/processes and Git writes; notify user of missing authorization immediately.
2. Update architecture, repo naming/visibility, tracker and README before backend implementation.
3. Implement strict Pydantic schemas and a framework-independent service adapter; preserve existing mathematical code.
4. Implement/document all five FastAPI endpoints, restricted CORS, explicit errors and bounded local compute.
5. Test contracts/services immediately even if FastAPI cannot install; execute HTTP endpoint tests only with actual FastAPI, never a mock framework.
6. Retry quantum dependency installation, run actual circuits/tests/benchmarks where possible, record unavailable states honestly otherwise.
7. Commit/push each validated milestone if metadata permissions/authentication allow. Supply safe local recovery commands when blocked. React remains deferred.

## 13. Autonomous continuation after latest attached brief

Read Pasted text(3).txt in full (494 lines). Preserve the published main history and the existing unpublished workflow changes. Current runtime still lacks FastAPI/Qiskit/Aer; the project venv lacks the numerical/API packages, and the approved network allowlist does not include PyPI. A fresh supported pip attempt failed; Git metadata staging is still denied. Do not repeat unchanged installation attempts or bypass these restrictions.

Execute unblocked correctness work next: (1) reject numerically unsafe QUBO encodings after reproducing tiny-utility loss, (2) validate auxiliary assignments through integer residuals rather than cancellation-sensitive energy tolerance, (3) validate solver options before missing imports, (4) implement a real HTTP probe for all five API routes and negative/CORS cases, (5) strengthen release evidence validation and add regression tests, (6) add CI that can perform genuine dependency installation and runtime validation when published, (7) refresh documentation/status records and attempt authorized publication. The CI definition itself is not a successful CI run. React and Streamlit feature work remain deferred.
