# ANAVO

**When power is limited, intelligence shouldn't be.**

Quantum-Assisted Energy Resilience Optimization for Pakistan | Energy & Smart Infrastructure

ANAVO helps a household choose which appliances to run during a power outage. It maximizes user-stated utility under usable battery-energy and simultaneous inverter-power limits, with explicit mandatory-load requirements. **Final architecture: React + TypeScript + Vite -> FastAPI/Python -> Qiskit or the classical solver.** React development awaits a separate design reference. Streamlit is optional archived demo code only and is not installed or tested by the backend release workflow.

## Backend-first architecture update

The primary application is a FastAPI/Pydantic backend that reuses the existing independent optimization engine. React + TypeScript + Vite + Tailwind CSS + Motion is deferred until a separate design brief; no React frontend is implemented. The Streamlit app is preserved without feature development. Public **[SabihaAbidd/anavo](https://github.com/SabihaAbidd/anavo)** is connected as origin/main. The initial project was successfully published by the user; the latest published local/remote baseline was verified as `1f2e86d076ddac27d3e1f2c08ab2dea2767aeac6`. Newer changes remain local while agent Git metadata writes are denied and the integration denies content writes. Do not confuse the successful initial push with permission to publish from this managed agent session.

Backend implementation and executed validation are tracked in TASKS.md and results/. Use the project .venv interpreter, which now has the verified API and quantum dependencies.

## Current verified status

The installed project .venv has passed **72 required backend tests with zero skips, failures or errors**, including actual FastAPI requests and Qiskit Aer circuits. An actual Uvicorn server passed **12 real HTTP checks**, covering all five routes, measured quantum optimize/compare requests, constraints, validation and CORS. Streamlit is absent and pip check found no broken requirements. requirements-lock.txt pins the 27 tested backend packages.

Actual QAOA benchmarks used p=2, 2,048 shots and seed 42. The best feasible samples matched exact utilities 30 and 15 with zero best-sample gaps; the mandatory-infeasible case produced no feasible sample. Repeated executions with identical source fingerprints reproduced counts and optimized parameters. The strict local release gate passed. See results/validation.json, api_startup_check.json, benchmark_results.json, benchmark_reproducibility.json and release_check.json.

These are ideal simulator results, not quantum speedup or hardware evidence. COBYLA reached its evaluation budgets, and the limited scenario had only about 24.3% physically feasible shots. Publication and CI status are separate from local readiness; React remains deferred pending the design reference.

## Start the FastAPI backend

From this project folder in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Health: http://127.0.0.1:8000/health Â· Swagger UI: http://127.0.0.1:8000/docs Â· ReDoc: http://127.0.0.1:8000/redoc Â· OpenAPI: http://127.0.0.1:8000/openapi.json

| Method / route | Behavior |
|---|---|
| `GET /health` | Service liveness and quantum dependency presence; does not claim circuit validation |
| `GET /api/scenarios` | Four validated editable example scenarios |
| `POST /api/optimize` | Explicit classical or quantum selection; structured allocation or error |
| `POST /api/compare` | Same scenario, both solvers; clearly labeled partial result if quantum unavailable |
| `GET /api/algorithm-info` | Objective, units, assumptions, algorithm and compute limits |

Full request/response contracts and error semantics are in [docs/API.md](docs/API.md). The API limits inputs to 16 appliances and quantum encodings to 14 qubits; the underlying engine's existing 20-appliance classical limit is unchanged. One heavy request per process is admitted at a time; busy requests get 429. Restrict local CORS with `ANAVO_CORS_ORIGINS` (default `http://localhost:5173,http://127.0.0.1:5173`). This is an unauthenticated local research API, not a public hosted service.

Example classical request using a shipped JSON fixture:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/optimize -ContentType application/json -Body (Get-Content -Raw docs/examples/optimize-request.json)
```

## Optional legacy prototype (not the application frontend)

Python 3.13 is available in the development environment; use Python 3.11â€“3.13 with compatible package wheels.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-demo.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

These commands are optional. The original app.py and .streamlit/config.toml are preserved, with historical tests and the old startup probe in legacy_demo/. Backend setup, CI and strict release checks use requirements.txt and tests/ only. See [legacy_demo/README.md](legacy_demo/README.md) for opt-in historical test commands. Installing the optional file includes the backend requirements plus Streamlit; installing the backend file alone never requests Streamlit.

## Reproduce and verify

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m scripts.validate
.\.venv\Scripts\python.exe -m scripts.api_startup_check
.\.venv\Scripts\python.exe -m scripts.benchmark --require-quantum
.\.venv\Scripts\python.exe -m scripts.verify_release
```

Tests use the standard library unittest runner. FastAPI HTTP tests are skipped when FastAPI is absent; circuit/quantum API tests are skipped when dependencies are absent. Green tests with skips establish neither HTTP nor quantum validity. `scripts.validate` saves actual outcomes with separate completeness flags. `verify_release` rejects skips, failed API health probes, unavailable quantum benchmarks, and absent measured comparisons. Requirements declare compatibility ranges; benchmark/validation records list actual installed versions. requirements-lock.txt pins the now-tested backend environment.

The HTTP script now exercises all five routes, actual small QAOA optimize/compare requests, infeasibility, invalid input, zero capacity, quantum limits and CORS. A health-only response is insufficient. The gate checks runtime source fingerprints, benchmark scenario coverage, positive shot counts, measured best selections, exact classical allocations, probabilities and gaps. Source fingerprints detect stale records, not cryptographic proof of quantum execution. Synthetic consistency fixtures exist only in tests and are never published as measured benchmarks.

`.github/workflows/backend-ci.yml` installs real dependencies on a hosted Python 3.13 runner, performs HTTP and quantum experiments, runs the strict gate, and retains result artifacts. Its repository token is read-only; it neither pushes source nor changes permissions. The CI workflow itself has been syntax checked locally; a passing CI run requires publication and actual execution.

To publish this continuation without waiting for dependency installation, run `.\scripts\publish_now.ps1` from ordinary Windows PowerShell. Then inspect https://github.com/SabihaAbidd/anavo/actions. The user's initial publish works outside this managed agent session; current agent staging and GitHub Git-tree writes remain denied. If a CI job fails, its logs/artifactsâ€”not the existence of the workflowâ€”determine the next defect or blocker.

For a Windows terminal with ordinary network and Git write access, run `.\scripts\finish_setup.ps1`. It first invokes the verified GitHub setup workflow, preserving implemented work and its honest blocked-status documentation in a commit, then installs dependencies, runs actual API/quantum validation and benchmarks, and publishes the next milestone. GitHub CLI must be installed and authenticated. It creates only **public `anavo`**, refuses unrelated remotes/history/private repositories, and verifies GitHub and remote commit hashes. See [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md). No passwords or tokens are requested in chat.

## Backend demonstration

1. Start Uvicorn using the backend command above and open http://127.0.0.1:8000/docs.
2. Call health, scenarios and algorithm-info; inspect their actual JSON responses.
3. Submit docs/examples/optimize-request.json to POST /api/optimize. The evening exact recommendation is fan, lights and router: 180 Wh, 60 W, utility 24.
4. Submit docs/examples/compare-request.json to POST /api/compare. Quantum measurements appear only when real Qiskit execution succeeds; unavailable results stay explicit.
5. Try the mandatory-infeasible preset and negative values to demonstrate hard constraints and validation. No React UI has been built yet.

## Architecture

`backend/main.py` -> strict Pydantic request -> `backend/service.py` -> existing `src/` engine -> physical feasibility check -> typed JSON response. The legacy `app.py` continues to call the same engine independently. No FastAPI imports were introduced into optimization code.

| Path | Purpose |
|---|---|
| `PLAN.md`, `TASKS.md` | Decisions, milestones, validation evidence and blockers |
| `backend/` | FastAPI routes, strict contracts, independent service adapter, restricted CORS settings |
| `requirements-demo.txt`, `legacy_demo/` | Optional Streamlit dependency and preserved historical checks; excluded from backend release |
| `src/classical_solver.py` | Exact baseline with deterministic tie handling |
| `src/optimization.py` | Exact decimal normalization, bounded slack QUBO, Ising mapping |
| `src/quantum_solver.py` | H/RZ/RZZ/RX circuit, COBYLA, statevector expectation, measured counts |
| `src/evaluation.py` | Identical-input comparison, versions, explicit unavailable state |
| `results/benchmark_results.json` | Actual executed benchmarks; inspect completeness flag |
| `results/validation.json` | Actual test pass/fail/skip evidence, API and quantum completeness flags |
| `docs/` | Derivation, research, architecture, report, pitch, demo, submission checklist |

## Limitations and future work

This is decision support, not an electrical controller. Appliance power ratings are illustrative, not measured Pakistan household data. Battery input is usable AC-side energy. Selected appliances run for fixed durations; power is conservatively reserved simultaneously. Essential is an explanatory label; utility expresses priority; mandatory is a hard constraint. No surge/duty-cycle, stochastic outage, solar forecast, or battery-degradation model exists. Exact enumeration is capped at 20 appliances, and simulator encodings at 14 qubits. Decimal precision can expand the encoding. The simulator is noiseless and uses exact statevector expectations for tuning; the final distribution is shot-sampled. No quantum advantage is claimed. Expand later to MILP baselines, time-slot schedules, realistic device measurements, and hardware/noise experiments.
