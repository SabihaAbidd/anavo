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
| [x] | Publish latest validated source and measured evidence | 2026-11-12: remote main verified at 3940efd61cdc3eaa7cba19abafe923709ff7a9b1, equal to local HEAD (frontend, opening, logo fix). Earlier index.lock/403 blockers are historical. |
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

## Pre-recording verification (2026-11-12, rerun this session)
- Remote: `git ls-remote origin main` = 3940efd61cdc3eaa7cba19abafe923709ff7a9b1 = local HEAD.
- Both servers started; /health ok with quantum dependencies available.
- Live classical /api/optimize: Evening 24 (fan/lights/router, 180 Wh, 60 W); Ample 30 (all four); Limited 15 (lights/router); Mandatory infeasible returned infeasible, 16 enumerated, 0 feasible.
- Live /api/compare (Evening, p=2, 2,048 shots, seed 42): measured best utility 24, gap 0; 12 qubits (4 appliance + 8 slack), circuit depth 33, 45.9% physically feasible shots, COBYLA hit its 80-evaluation budget per restart, ~20 s runtime. Simulator only; no speedup claimed.
- scripts.validate: 72 passed, 0 skipped/failures/errors.
- npm run build passed; npm run test:integration: 2 passed, 0 failed.
- Browser: opening mounted on load, Enter skip worked, header logo measured 30x30 px on desktop. Phone-layout check was not finished in this session because the hidden preview pane stopped responding; check it visually before recording.

## Feature expansion milestone (2026-11-12)
- Quantum insights: `/api/compare` now returns measured selection distribution (slack marginalised), full solution landscape, qubit roles, transpiled gate counts and probability of measuring the exact optimum. Existing QAOA results unchanged.
- Hour-by-hour scheduler (`src/scheduler.py`, `/api/schedule`): exact MILP with contiguous blocks, per-slot inverter limit, battery state of charge, optional solar (ESMAP 5.67 kWh/m2/day x 0.75). Independently re-verified before returning.
- Housing society B2B (`src/fleet.py`, `/api/fleet/optimize`): shared-capacity MILP for up to 500 homes, per-home mandatory loads, fairness floor, Jain index, equal-split baseline. 500 homes / 3,076 decisions solved in about 3 s.
- Async job queue (`backend/jobs.py`, `/api/jobs`): one worker sharing the optimization slot.
- Pakistan dataset (`data/pakistan_energy.json`, `/api/data/pakistan`): every value tagged with a cited source or marked estimate.
- Frontend: quantum insights panel, timeline (Gantt + load/battery chart), society grid with single-home QAOA verification, Pakistan data library, architecture section.
- Checks run this milestone: scripts.validate 91 passed / 0 skipped / 0 failed; npm run build passed; npm run test:integration 3 passed; scripts.benchmark --require-quantum regenerated (30, 15, no feasible sample); scripts.api_startup_check passed; scripts.verify_release passed.
- Browser (desktop, hidden preview pane): all sections render; society job, single-home QAOA verify, compare insights and schedule flows completed with expected values. Phone layout of new sections not visually verified.

## Architecture figure (2026-11-12)
- Added paper-style SVG figure `frontend/src/assets/anavo-architecture.svg` (lanes: client, orchestration, solver plane, verification; QUBO/Ising/QAOA circuit drawing; COBYLA loop; feasibility oracle; measured Evening numbers). Embedded in the Architecture section (scrollable on phones, full-size and download links), README, docs/ARCHITECTURE.md and docs/REPORT.md. SVG styles scoped to `#anavo-fig`.
- Checks: SVG parses as XML; npm run build passed; browser render verified at 1600 px and no page-level horizontal overflow at phone width.

## Deployment configuration (2026-11-13)
- Added `Dockerfile` + `.dockerignore` (backend only: Python 3.13-slim, requirements-lock.txt, one Uvicorn worker on `$PORT`, non-root user), `render.yaml` (Render free web service `anavo-api`, health check `/health`) and `frontend/vercel.json` (Vite build, `/api/*` and `/health` rewritten to `https://anavo-api.onrender.com`). Steps in docs/DEPLOYMENT.md.
- Checks: `npm run build` passed; the container's Uvicorn command served `/health`, `/api/scenarios` and a measured `/api/compare` from the local venv. Docker image not built locally (daemon not running). Nothing is deployed yet: Render and Vercel setup is pending on the owner's accounts.

## Beginner project summary (2026-11-13)
- Added `docs/PROJECT_SUMMARY.md`: plain-language explanation of the problem, features, classical solver, quantum basics, the full QUBO -> slack -> Ising -> QAOA -> COBYLA -> measurement -> verification pipeline, saved benchmark numbers, architecture, evidence, limitations, Q&A and glossary.
- Documentation only; figures were taken from `results/benchmark_results.json`, README and TASKS.md. No code changed and no checks rerun.
