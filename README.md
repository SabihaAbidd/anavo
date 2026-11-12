# ANAVO

**When power is limited, intelligence shouldn't be.**

Quantum-Assisted Energy Resilience Optimization for Pakistan · Energy & Smart Infrastructure

ANAVO helps a household choose which appliances to run during a power outage. It maximizes user-stated utility under usable battery-energy and simultaneous inverter-power limits, with explicit mandatory-load requirements. Its FastAPI backend exposes the existing exact optimizer and Qiskit QAOA implementation through strict JSON contracts. The earlier Streamlit demonstration is preserved.

## Backend-first architecture update

The primary application is now a FastAPI/Pydantic backend that reuses the existing independent optimization engine. React + TypeScript + Vite + Tailwind CSS + Motion is planned only after a separate design brief; no React frontend is implemented. The existing Streamlit app is preserved without further feature development. Public **[SabihaAbidd/anavo](https://github.com/SabihaAbidd/anavo)** and its default branch `main` have now been verified through the authenticated integration. Publishing contents was denied with GitHub 403; local origin/config/index writes are separately denied. No commit/push has succeeded.

Backend implementation and verification are tracked in TASKS.md. FastAPI is currently absent in this restricted environment; Pydantic 2.12.5 is installed. Do not interpret schema/service validation as successful HTTP endpoint execution.

## Current verified status

The physical model, exact solver, QUBO/Ising math, and dashboard interactions have been executed and tested. Actual localhost health verification is blocked by socket permissions (WinError 10013). **Qiskit/Aer execution is pending:** packages are absent and this environment cannot resolve PyPI. The quantum implementation is real circuit code but has not been executed here. Saved benchmarks explicitly record `quantum.status = unavailable`; there are no invented quantum numbers. Git initialized successfully, but commits are blocked by denied writes to `.git/index.lock`. No remote is configured or verified. This is not yet a submission-ready release.

## Start the FastAPI backend

From this project folder in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Health: http://127.0.0.1:8000/health · Swagger UI: http://127.0.0.1:8000/docs · ReDoc: http://127.0.0.1:8000/redoc · OpenAPI: http://127.0.0.1:8000/openapi.json

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

## Legacy Streamlit demonstration

Python 3.13 is available in the development environment; use Python 3.11–3.13 with compatible package wheels.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If `venv` cannot bootstrap pip, repair the Python installation or install its bundled pip wheel before continuing. Do not substitute fake quantum outputs. The existing system Python has Streamlit/NumPy/SciPy, so the classical dashboard also runs now with `python -m streamlit run app.py`.

## Reproduce and verify

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m scripts.validate
.\.venv\Scripts\python.exe -m scripts.api_startup_check
.\.venv\Scripts\python.exe -m scripts.benchmark --require-quantum
.\.venv\Scripts\python.exe -m scripts.verify_release
```

Tests use the standard library unittest runner. FastAPI HTTP tests are skipped when FastAPI is absent; circuit/quantum API tests are skipped when dependencies are absent. Green tests with skips establish neither HTTP nor quantum validity. `scripts.validate` saves actual outcomes with separate completeness flags. `verify_release` rejects skips, failed API health probes, unavailable quantum benchmarks, and absent measured comparisons. Requirements declare compatibility ranges; benchmark/validation records list actual installed versions. A verified dependency lock awaits a complete install/run.

For a Windows terminal with ordinary network and Git write access, run `.\scripts\finish_setup.ps1`. It first invokes the verified GitHub setup workflow, preserving implemented work and its honest blocked-status documentation in a commit, then installs dependencies, runs actual API/quantum validation and benchmarks, and publishes the next milestone. GitHub CLI must be installed and authenticated. It creates only **public `anavo`**, refuses unrelated remotes/history/private repositories, and verifies GitHub and remote commit hashes. See [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md). No passwords or tokens are requested in chat.

## Demonstration

1. Start Streamlit and open the local URL it prints.
2. Keep **Evening backup**: 240 Wh, 100 W inverter, three-hour outage.
3. Click **Optimize backup allocation**. Exact recommendation: fan, LED lights, router; 180 Wh, 60 W, utility 24.
4. Inspect actual simulated quantum measurements if dependencies are installed. If unavailable, the UI says so explicitly.
5. Switch to **Limited battery**: exact recommendation is lights + mandatory router, utility 15, 60 Wh.
6. Switch to **Mandatory infeasible**: router needs 30 Wh but battery has 15 Wh; report infeasibility without relaxing requirements.

## Architecture

`backend/main.py` -> strict Pydantic request -> `backend/service.py` -> existing `src/` engine -> physical feasibility check -> typed JSON response. The legacy `app.py` continues to call the same engine independently. No FastAPI imports were introduced into optimization code.

| Path | Purpose |
|---|---|
| `PLAN.md`, `TASKS.md` | Decisions, milestones, validation evidence and blockers |
| `backend/` | FastAPI routes, strict contracts, independent service adapter, restricted CORS settings |
| `src/classical_solver.py` | Exact baseline with deterministic tie handling |
| `src/optimization.py` | Exact decimal normalization, bounded slack QUBO, Ising mapping |
| `src/quantum_solver.py` | H/RZ/RZZ/RX circuit, COBYLA, statevector expectation, measured counts |
| `src/evaluation.py` | Identical-input comparison, versions, explicit unavailable state |
| `results/benchmark_results.json` | Actual executed benchmarks; inspect completeness flag |
| `results/validation.json` | Actual test pass/fail/skip evidence, API and quantum completeness flags |
| `docs/` | Derivation, research, architecture, report, pitch, demo, submission checklist |

## Limitations and future work

This is decision support, not an electrical controller. Appliance power ratings are illustrative, not measured Pakistan household data. Battery input is usable AC-side energy. Selected appliances run for fixed durations; power is conservatively reserved simultaneously. Essential is an explanatory label; utility expresses priority; mandatory is a hard constraint. No surge/duty-cycle, stochastic outage, solar forecast, or battery-degradation model exists. Exact enumeration is capped at 20 appliances, and simulator encodings at 14 qubits. Decimal precision can expand the encoding. The simulator is noiseless and uses exact statevector expectations for tuning; the final distribution is shot-sampled. No quantum advantage is claimed. Expand later to MILP baselines, time-slot schedules, realistic device measurements, and hardware/noise experiments.
