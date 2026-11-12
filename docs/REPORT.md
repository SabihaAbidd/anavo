# ANAVO technical report

## Backend continuation and latest evidence

The primary delivery is now a FastAPI/Pydantic backend exposing health, scenario listing, explicit optimization, comparison and algorithm-information routes, with restricted CORS, bounded fields, per-process heavy-job admission, structured errors and OpenAPI contracts. Existing solvers and mathematical mappings are reused; installed-version reporting in the legacy evaluation helper was extended. Streamlit remains preserved without feature development; React/TypeScript/Vite/Tailwind/Motion is deferred pending design references.

Latest full validation: 74 tests discovered, **59 passed, 15 skipped, zero failures/errors**. The skips comprise 12 FastAPI endpoint tests, one real quantum API test, and two core quantum circuit tests. Nineteen new regression/evidence tests cover numerical precision, integer slack residuals, direct solver option checks and rejection of stale/inconsistent runtime records. The earlier 18 Pydantic/service/CORS-configuration checks still pass. No skipped test is counted as HTTP or quantum validation. The direct classical service example is explicitly labeled non-HTTP; synthetic evidence consistency fixtures remain confined to tests.

FastAPI is not installed; the fresh supported pip attempt again failed, and the execution environment's network allowlist excludes PyPI. The project venv has pip but lacks the application dependencies; installed system packages support the remaining algebra/service/UI checks. The new HTTP script detects missing FastAPI and records a blocked outcome before launching Uvicorn. The earlier localhost socket restriction remains unresolved. Qiskit/Aer still have not executed; refreshed classical benchmarks retain quantum=unavailable with no invented gaps/counts.

The user successfully published the initial project to public https://github.com/SabihaAbidd/anavo. Local HEAD/origin and remote main were verified at d9c24703603b8f833b140cdd76338cd42d697b4e; the current GitHub comparison is identical to that commit. Newer fixes remain local until authorized publication succeeds. Local git add still cannot create .git/index.lock; the integration's prior contents writes were rejected with 403. User-run Git publication and agent-session write permission are separate. See docs/GITHUB_SETUP.md and results/github_verification.json.

## Executive summary and release status

ANAVO implements a household backup-energy allocation prototype for the Energy & Smart Infrastructure theme. It combines an independently exact binary optimizer, an explicit constrained QUBO/Ising mapping, a Qiskit QAOA implementation, and a working Streamlit dashboard. The consumer-facing problem is motivated by electricity reliability concerns in Pakistan; the scenarios are illustrative rather than measured household data.

**This is an implementation with partially validated execution, not a complete quantum hackathon release.** FastAPI/Qiskit/Aer are absent and package installation remains blocked. A prior localhost health probe received socket denial (WinError 10013); Streamlit AppTest interactions pass. Initial GitHub publication is verified, while publication of new fixes from this agent session remains blocked. Actual API/circuit execution and quantum comparison are not marked complete.

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

The autonomous continuation implemented a conservative QUBO precision guard after reproducing false tiny-utility ties, removed absolute cost-term dropping, normalized nonzero small Hamiltonians, and changed full encoding feasibility to exact integer residuals. Normal preset optima remain verified. The HTTP probe now covers all five routes and negative/CORS cases, including real small quantum requests when dependencies are present. Evidence records include runtime-source fingerprints; the gate checks benchmark identities, decoded counts, feasibility, best selections, exact baseline and gaps. A read-only CI workflow is defined to install dependencies and perform the full sequence after publication. Its YAML parsed successfully, but no CI run has occurred.

Restore normal package-network and Git write access. Run `scripts/finish_setup.ps1`; inspect actual QAOA counts, feasibility, gaps and versions; update this report and pitch with measured quantum outcomes; complete the submission checklist and verify the authorized GitHub push. Do not present this report's pending quantum results as executed.
