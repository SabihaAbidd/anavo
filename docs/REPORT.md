# ANAVO technical report

## Executive summary

ANAVO is a Pakistan-focused household backup-energy decision-support prototype for Energy & Smart Infrastructure. Final architecture: React + TypeScript + Vite -> FastAPI/Python -> Qiskit Aer or an independent exact classical solver. React is deferred until the user supplies the design. Streamlit is optional historical code only and is absent from the tested backend environment.

The local backend passed all 72 required tests with zero skips/failures/errors, 12 real Uvicorn HTTP checks, actual QAOA experiments and strict release verification. Repeated seeded benchmarks reproduced counts and optimized parameters. Publication of the latest evidence and its CI run remain separate tasks. There has been no hardware execution, quantum speedup demonstration or production electrical-control validation.

## Methodology and implementation

Each appliance request has power W, duration h, energy Wh, utility and explicit essential/mandatory flags. Binary decisions maximize stated utility subject to usable AC-side battery energy and simultaneous inverter power. Mandatory requirements are never automatically relaxed. Essential is a label, not a hidden utility bonus. The presets are illustrative, not measured household data.

An independent exact enumerator checks every small-instance selection and resolves ties deterministically. Rational decimal normalization and bounded binary slack convert resource inequalities into QUBO equalities. A penalty exceeding the objective range enforces constraints in exact arithmetic, with numerical guards rejecting unsafe floating-point representations. The substitution x=(1-Z)/2 gives the Ising Hamiltonian. Tests exhaustively check energies/minima, bit order, tiny-priority loss and integer auxiliary residuals. See MATHEMATICAL_MODEL.md for the full derivation and worked example.

Actual Qiskit QAOA uses H initialization, cost RZ/RZZ gates and X mixing. Seeded SciPy COBYLA restarts minimize actual noiseless Aer statevector expectations; a separate Aer shot circuit supplies measured counts. Candidates are decoded and physically checked. Full auxiliary encoding feasibility is also reported, independently of physical appliance feasibility. No repair or exact-answer injection is used.

## Actual measured benchmarks

Every benchmark uses p=2, 2,048 shots, seed 42, COBYLA and two restarts with 80 evaluations each (160 evaluations total). Circuit depth below is transpiled depth and differs from p. Raw counts, parameters, optimizer messages/flags, seeds, versions and runtimes are in results/benchmark_results.json.

| Scenario | Qubits | Circuit depth | Exact utility | Quantum best | Physical feasible | Full encoding feasible | Utility gap | Quantum seconds | Classical seconds |
|---|---:|---:|---|---|---:|---:|---|---:|---:|
| Ample backup | 4 | 2 | 30 | 30 | 100.0000% | 100.0000% | 0 | 2.8995 | 0.000529 |
| Limited battery | 9 | 26 | 15 | 15 | 24.3164% | 0.7324% | 0 | 1.9369 | 0.001264 |
| Mandatory infeasible | 8 | 25 | Infeasible | None | 0.0000% | 0.0000% | Undefined | 1.8999 | 0.001291 |

Ample backup selects all four appliances: utility 30, energy 300 Wh, power 120 W. Limited battery selects LED lights and the mandatory router: utility 15, energy 60 Wh, power 20 W. The mandatory-infeasible case has 15 Wh for a router needing 30 Wh: enumeration proves infeasibility, no measured candidate is physically feasible, and its gap is undefined rather than zero.

The zero gaps describe best feasible sampled selections only. About 24.3% of limited-battery shots are physically feasible and about 0.73% satisfy the complete auxiliary encoding. All optimizer runs hit MAXFUN and report success=false; a capped evaluation budget is not parameter convergence. Exact classical enumeration was much faster on these small problems. These results do not demonstrate quantum advantage.

Two actual benchmark executions with identical runtime-source fingerprints and installed versions produced identical measurement counts and optimized parameters across all three scenarios. results/benchmark_reproducibility.json records the comparison and count digests. Wall times and timestamps differ naturally. This verifies repeatability in this environment, not across all hardware/platforms/seeds.

## API and release verification

All 72 backend tests executed successfully, including real Qiskit circuit phase/measurement/reproducibility checks and actual FastAPI TestClient requests. Optional historical Streamlit tests were excluded. An additional Uvicorn process passed 12 real HTTP cases: health, scenarios, algorithm information, classical optimize, measured quantum optimize, measured comparison, mandatory infeasibility, invalid requests, quantum limits, zero capacity and allowed/rejected CORS. The temporary probe server stops after checking; use the documented Uvicorn command for an ongoing demo.

The strict release gate returned exit 0. Test, HTTP and benchmark records share the current runtime-source fingerprint. The gate independently checks scenario coverage, decoded counts, probabilities, best samples, exact baseline and objective gaps. Synthetic consistency fixtures are confined to tests; published benchmark records come from real Aer execution. See results/validation.json, api_startup_check.json and release_check.json.

## Tested environment and reproducibility

Python 3.13.5 on Windows; Qiskit 2.6.2, Aer 0.18.2, NumPy 2.5.4, SciPy 1.18.1, FastAPI 0.162.5 and Pydantic 2.14.3 were verified. pip check passed. Streamlit is not installed. requirements-lock.txt pins all 27 resolved backend packages; requirements.txt retains backend-only compatibility ranges, and requirements-demo.txt is opt-in.

Earlier package installation attempts were blocked in the managed session. The user completed installation in ordinary PowerShell, after which actual imports/API/circuit execution resolved those runtime blockers. The configured CI workflow uses a fresh venv and the tested lock to repeat checks after publication. No CI success for unpublished changes is claimed.

## Limitations and next phase

This is an ideal/noiseless simulator demonstration. Statevector training is not a noisy hardware estimator, and simulation includes exponential memory/cost. Subjective utilities, fixed durations and conservative simultaneous power omit switching schedules, surge currents, duty cycles, battery degradation, uncertain solar/outages and actual battery conversion losses. No household energy-saving or safety outcome has been measured.

Publish the current validated source and measured evidence, verify the remote commit and CI run, then wait for the user's React design reference. The backend is an unauthenticated localhost research API. Future work can add real household measurements, time-slot MILP, noise studies and carefully controlled hardware experiments.
