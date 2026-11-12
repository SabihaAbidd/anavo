# ANAVO live task tracker

## Current backend status

**Local backend validation passed.** The tested environment is the project .venv, with Streamlit absent. React remains deferred pending the design reference. Publication of the latest changes is tracked separately from local correctness.

| Done | Task | Evidence / status |
|---|---|---|
| [x] | Preserve existing project, plan and history | Existing public SabihaAbidd/anavo on main; no project restart or force operations |
| [x] | Separate final application from optional demo | React/TypeScript/Vite -> FastAPI -> Qiskit/classical; requirements-demo.txt and legacy_demo/ are opt-in |
| [x] | Install and verify backend dependencies | User completed backend install; imports pass, pip check passes, Streamlit absent |
| [x] | Pin tested environment | requirements-lock.txt records 27 packages; Python 3.13.5, Qiskit 2.6.2, Aer 0.18.2 |
| [x] | Validate physical model and exact solver | Battery/power/mandatory constraints, zero/infeasible cases and deterministic optima pass |
| [x] | Validate QUBO/Ising and numerical safeguards | Exhaustive consistency, tiny-priority guard, small-cost normalization and exact auxiliary residual checks pass |
| [x] | Execute real Qiskit circuits | Aer expectation, circuit phase, shots, bit decoding, candidate feasibility and seeded reproducibility tests pass |
| [x] | Verify all FastAPI routes | Actual TestClient requests and 12 real Uvicorn HTTP checks pass, including measured quantum optimize/compare and CORS |
| [x] | Execute all required tests | 72 passed, zero skips/failures/errors; historical Streamlit tests excluded |
| [x] | Run actual quantum benchmarks | Three scenarios; 2,048 shots, p=2, seed 42; best measured utilities 30 and 15, both gap 0; mandatory-infeasible case has no feasible sample |
| [x] | Verify repeatability | Actual repeated benchmark counts and optimized parameters match in the installed environment; see benchmark_reproducibility.json |
| [x] | Pass strict release gate | results/release_check.json: ready=true, exit_code=0, matching runtime-source fingerprint |
| [x] | Prepare API/math/report/pitch/demo/deployment docs | Current measured evidence replaces prior dependency-blocked status; no quantum advantage claim |
| [x] | Configure backend-only CI | Fresh venv, tested lock, no Streamlit, actual runtime experiments and strict gate; read-only repository token |
| [ ] | Publish latest validated source and measured evidence | Latest git add denied .git/index.lock; dependency-lock blob API returned 403. Remote main remains verified at 1f2e86d076ddac27d3e1f2c08ab2dea2767aeac6; these new changes are local. |
| [ ] | Verify CI on newly published commit | Workflow definition/local syntax checks are not a completed CI run |
| [ ] | React frontend | Explicitly deferred until user provides design reference; no React implementation started |

## Evidence files

- results/validation.json: all 72 required tests executed successfully.
- results/api_startup_check.json: all 12 real HTTP checks passed; temporary Uvicorn process stopped after verification.
- results/benchmark_results.json: actual simulator counts, physical/full-encoding probabilities, best candidates, objective gaps, parameters, optimizer flags, runtimes and versions.
- results/benchmark_reproducibility.json: measured count digests and optimized-parameter comparisons across repeated actual runs.
- results/backend_dependency_check.json: current verified installed backend, pip consistency and absence of Streamlit.
- results/release_check.json: successful strict local release verification.
- results/github_verification.json: independently verified remote baseline and latest publication outcome, kept separate from runtime readiness.

## Scientific limitations

Both feasible benchmark best-sample gaps were zero, but COBYLA reached the 80-evaluation budget in each restart rather than reporting convergence. The limited-battery run had about 24.3% physically feasible outcomes and about 0.73% full-encoding feasible outcomes. Exact classical enumeration was much faster. No hardware, speedup, household savings or production safety claim is supported.

## Resolved blockers and history

Earlier managed-session package installs failed, and the backend/quantum tests were skipped. The user's successful ordinary-PowerShell install resolved missing dependencies; subsequent agent execution verified real API requests, Qiskit circuits and all required tests. Older skipped-test totals are historical and no longer the current status.

The user previously published d9c24703603b8f833b140cdd76338cd42d697b4e and later 1f2e86d076ddac27d3e1f2c08ab2dea2767aeac6. These published commits are preserved. Runtime success does not by itself change Git metadata permissions or integration write scopes. Do not mark the latest milestone published until a new remote commit is verified.
