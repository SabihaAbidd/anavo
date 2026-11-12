# ANAVO technical report

## Backend continuation and latest evidence

The primary delivery is now a FastAPI/Pydantic backend exposing health, scenario listing, explicit optimization, comparison and algorithm-information routes, with restricted CORS, bounded fields, per-process heavy-job admission, structured errors and OpenAPI contracts. Existing solvers and mathematical mappings are reused; installed-version reporting in the legacy evaluation helper was extended. Streamlit remains preserved without feature development; React/TypeScript/Vite/Tailwind/Motion is deferred pending design references.

Latest full validation: 55 tests discovered, **40 passed, 15 skipped, zero failures/errors**. The skips comprise 12 FastAPI endpoint tests, one real quantum API test, and two core quantum circuit tests. Eighteen new Pydantic/service/CORS-configuration tests ran successfully, including exact resource/objective output, rechecking candidates, hard infeasibility, zero capacity, and explicit dependency/resource/runtime failure handling. No skipped test is counted as HTTP or quantum validation. The direct classical service example is saved with an explicit non-HTTP label in results/api_service_example.json; Pydantic schemas and input fixtures are shipped for integration.

FastAPI is not installed, and pip retries plus a direct PyPI DNS lookup confirmed network resolution failure. Uvicorn startup was not attempted after the script detected the missing dependency; results/api_startup_check.json records this blocked outcome. The legacy localhost socket restriction remains unresolved. Qiskit/Aer still have not executed; refreshed classical benchmarks retain quantum=unavailable with no invented gaps/counts.

GitHub integration authentication is verified as SabihaAbidd. A later lookup confirmed public https://github.com/SabihaAbidd/anavo, default branch main, with no branches/commits yet. The exposed integration has no repository-creation operation; repository existence was observed, not attributed to an agent creation action. Attempting the first file commit was denied with 403 Resource not accessible by integration. Local main remains unborn, origin absent, and both .git/config and .git/index.lock writes are denied. No stale lock or running Git process explains this session restriction. No commit or push success is claimed. A safe CLI recovery script targets only public owner/anavo and checks existing content/history/remote/visibility before writing. See docs/GITHUB_SETUP.md.

## Executive summary and release status

ANAVO implements a household backup-energy allocation prototype for the Energy & Smart Infrastructure theme. It combines an independently exact binary optimizer, an explicit constrained QUBO/Ising mapping, a Qiskit QAOA implementation, and a working Streamlit dashboard. The consumer-facing problem is motivated by electricity reliability concerns in Pakistan; the scenarios are illustrative rather than measured household data.

**This is an implementation with partially validated execution, not a complete quantum hackathon release.** The development environment cannot resolve `pypi.org`, Qiskit/Aer are absent, and writes to Git's index are denied. A real localhost health probe also received socket access denial (WinError 10013), although Streamlit AppTest interactions pass. Actual HTTP startup, circuit execution, quantum benchmark comparison, commits, and remote push remain blocked. These requirements are not marked complete.

## Methodology and implementation

Each appliance request has a fixed duration, power, utility, essential label, and mandatory flag. Exact enumeration checks every hard constraint and maximizes utility with deterministic lexicographic ties. A separate conversion uses exact rational normalization, bounded slack variables, and penalty A=1+total utility. QUBO minima and Ising energies are validated exhaustively. Mandatory requirements remain hard even when infeasible.

The quantum implementation prepares |+> on every qubit, alternates Ising cost rotations and X mixing, uses seeded COBYLA restarts to minimize noiseless Aer expectations, then measures an optimized Qiskit circuit through Aer. Bitstrings are decoded in logical order and checked against the physical model. Both physical-selection and full-encoding feasibility probabilities are defined. No classical repair or exact-answer substitution is used.

## Executed results

Run: `python -m scripts.benchmark`, seed 42 requested; actual package versions are stored in `results/benchmark_results.json`. Quantum depth/shots are requested settings only until execution succeeds. Classical runtimes are measured in that JSON; there is no quantum runtime to compare. All physical bitstrings below use appliance input order: fan, lights, router, laptop.

| Scenario | Battery Wh | Inverter W | Exact selection | Exact utility | Energy Wh | Power W | Quantum |
|---|---:|---:|---|---:|---:|---:|---|
| Ample backup | 400 | 150 | 1111 | 30 | 300 | 120 | Unavailable; dependency import failed |
| Limited battery | 90 | 60 | 0110 | 15 | 60 | 20 | Unavailable; dependency import failed |
| Mandatory infeasible | 15 | 100 | None | Undefined | Undefined | Undefined | Unavailable; dependency import failed |

The ample case serves every load because all fit. The limited case favors lights and the mandatory router; adding the 120 Wh fan or laptop would exceed the 90 Wh budget. The impossible case has only 15 Wh available for a mandatory router needing 30 Wh, so no feasible allocation exists. The dashboard's additional evening example selects fan/lights/router for utility 24 at 180 Wh and 60 W.

The benchmark's `complete_quantum_execution` flag is false. Objective gaps, measured feasible probabilities, quantum counts and quantum runtimes are absent/undefined. No conclusion about QAOA quality can be drawn from these classical results.

## Verification

The standard-library unittest suite executes model, classical, QUBO, Ising, bit-order, encoding-limit, and Streamlit interaction checks. The initial run completed 24 tests: 22 passed and two conditional real-circuit tests skipped. A final validation record is maintained in `results/validation.json` and TASKS.md. Streamlit's AppTest validated initial render, optimization, preset capacities, invalid duration rejection, and stale-result clearing. Exact QUBO ground states were verified for all four presets, including explicit detection of physical infeasibility. An initial test incorrectly assumed a single fine-decimal weight must create a large encoding; GCD reduction correctly eliminated that scale. The test was corrected to use two incommensurate weights and passed.

`scripts.verify_release` rejects skipped circuit tests and incomplete measured benchmarks. Passing algebra tests is not a substitute for executing a quantum circuit. Requirements use declared compatibility ranges and need a fully validated lock after installation succeeds.

## Limitations and impact

No quantum advantage is established. A small classical exact solver is appropriate here, and simulation includes exponential state storage and basis-energy evaluation; its runtime is not a hardware resource estimate. Ideal statevector expectation optimization omits measurement noise during training, calibration drift, hardware connectivity, and gate errors. Multi-start tuning and best-of-many shots can help observed candidates but offer no guaranteed optimum. Utility is subjective, and mandatory is not equivalent to a medically safe supply plan. The simultaneous model excludes actual start times, surge currents, duty cycles, switching, degradation, uncertain solar and outages. Ratings are editable illustrative assumptions.

The intended contribution is transparent decision support: explain what fits, which services are served, when hard requirements cannot be satisfied, and how an auditable quantum formulation compares with an exact reference. Future work should add measured household data, time-slot MILP, realistic battery conversion, noise studies, parameter/seed sweeps, and carefully controlled hardware experiments.

## Required completion before submission

Restore normal package-network and Git write access. Run `scripts/finish_setup.ps1`; inspect actual QAOA counts, feasibility, gaps and versions; update this report and pitch with measured quantum outcomes; complete the submission checklist and verify the authorized GitHub push. Do not present this report's pending quantum results as executed.
