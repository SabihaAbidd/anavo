# ANAVO live task tracker

## Current backend status

**Local backend validation passed.** The tested environment is the project .venv, with Streamlit absent. The supplied design reference authorizes the new separate React frontend. Publication of the latest changes is tracked separately from local correctness.

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
| [ ] | Publish latest validated source and measured evidence | Latest git add denied .git/index.lock; dependency-lock blob API returned 403. Remote main remains verified at 6f471887303118e3206c8e648de2bfbcce48f58b; these new changes are local. |
| [ ] | Verify CI on newly published commit | Workflow definition/local syntax checks are not a completed CI run |
| [x] | Separate React frontend | React/TypeScript/Vite, original GSAP intro, animated pixel planet, lime/purple responsive UI, editable manifest and real classical/QAOA comparison |

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

The user previously published d9c24703603b8f833b140cdd76338cd42d697b4e and later 6f471887303118e3206c8e648de2bfbcce48f58b. These published commits are preserved. Runtime success does not by itself change Git metadata permissions or integration write scopes. Do not mark the latest milestone published until a new remote commit is verified.

## Frontend validation

- npm install completed; npm run build passed TypeScript and Vite production bundling.
- Live browser classical request returned utility 24, 180 Wh, 60 W for the evening preset.
- Live browser quantum comparison returned measured utility 24, 12 qubits, 2,048 shots, seed 42, depth 33, 45.9% physically feasible shots and zero best-sample gap; runtime about 17 seconds. No speedup claim.
- Frontend source remains independent of Python; no optimization logic was rewritten.

- Two live frontend proxy integration tests passed: entry/health, scenarios, exact optimum, actual measured quantum optimum, mandatory infeasibility and 422 validation.
- Phone viewport (390px) and intro replay verified in the browser. Production build rerun after final visual changes passed.
- Publishing helper includes frontend/ and excludes node_modules, build output and unrelated untracked recordings. The agent staging attempt still failed with .git/index.lock permission denied. Latest independently verified remote baseline is 6f471887303118e3206c8e648de2bfbcce48f58b.

## Recorded-reference opening milestone

- Visually inspected the supplied 45.77-second MP4, including binary title and later explanatory scenes.
- Replaced the earlier generic intro with a separate SequenceIntro component: live binary territories, large pixel type, binary text substitutions, purple inversion, symbol controls, pause/play, pointer interaction and stepped reveal.
- Added pixel typography to the main hero, brand and closing. Preserved the energy lab and API contracts.
- Temporary video viewer and copied footage removed; the original recording stays untracked and is not shipped.
- Build and browser validation outcomes are recorded in results/frontend_validation.json.

- Recorded opening checks passed: pause/play, symbol switching while paused, automatic reveal, Escape skip, replay and 390px phone layout. Main hero uses verified Pixelify Sans.
- Live proxy tests: 2 passed after restarting the stopped local backend; real quantum execution included. TypeScript/Vite production build passed. Backend scientific source was unchanged.
- Intro session marker versioned so existing visitors see the new sequence once after refreshing.
- Agent git add still denied .git/index.lock. Changes remain local; published baseline is 158378ea6bc64092df07db5e7b60f3aa3056cb8a.

## Opening refresh correction
Removed the sessionStorage gate: the recorded-style intro now mounts on every page load/refresh, including /#lab. Footer replay remains available and reduced-motion preference still skips animation. This supersedes the earlier once-per-session behavior.

## Header logo placement correction
Replaced the rotated text glyph with a bounded SVG pixel mark (30px desktop / 26px mobile), separated the wordmark, and aligned the registration mark. Production TypeScript/Vite build passed; desktop preview visually verified without logo overlap. Fresh page load also visibly showed the opening before revealing the app. Backend checks were not rerun for this presentation-only change.
