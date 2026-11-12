# FastAPI backend contract (schema 1.0)

Status: route implementation written; Pydantic and service tests executed. Actual FastAPI HTTP tests remain unexecuted because FastAPI cannot be installed in this environment. No React frontend exists. Stable request/response models are in `backend/schemas.py`; service code has no FastAPI imports and invokes the existing optimizer.

## Start and inspect

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Swagger: http://127.0.0.1:8000/docs · ReDoc: http://127.0.0.1:8000/redoc · OpenAPI JSON: http://127.0.0.1:8000/openapi.json. These are local URLs available after a successful install and server start, not deployed/verified URLs.

## Endpoints

| Method | Path | Success contract |
|---|---|---|
| GET | `/health` | `HealthResponse`: service/version/liveness and dependency-presence flag; no expensive circuit execution |
| GET | `/api/scenarios` | `ScenariosResponse.scenarios`: four full `ScenarioInput` objects suitable for editing |
| POST | `/api/optimize` | `OptimizeRequest` -> `OptimizeResponse`, one explicitly selected algorithm |
| POST | `/api/compare` | `CompareRequest` -> `CompareResponse`, exact and quantum outcomes for identical inputs |
| GET | `/api/algorithm-info` | `AlgorithmInfo`: units, assumptions, algorithm description and resource limits |

## Inputs

`OptimizeRequest` is `{ "scenario": {...}, "algorithm": "classical", "quantum_options": {...} }`. Algorithm defaults to classical and accepts only `classical` or `quantum`. `CompareRequest` has scenario/quantum_options and rejects an algorithm field. Send JSON numbers and real booleans, not numeric/boolean strings. Unexpected fields, duplicate trimmed case-insensitive names, NaN, infinity, negative values, durations beyond the outage, and empty loads are rejected.

| Scenario/appliance field | Units and rules |
|---|---|
| `name` | 1–120 trimmed characters; scenario name defaults to Custom outage |
| `battery_wh` | Usable AC-side Wh, 0–1,000,000,000 |
| `inverter_w` | Simultaneous W capacity, 0–10,000,000 |
| `outage_h` | Hours, positive and at most 168 |
| `appliances` | 1–16 rows at API boundary; core classical engine remains independently capped at 20 |
| `power_w` | W, 0–1,000,000 |
| `duration_h` | h, 0–168 and at most outage_h |
| `utility` | User priority score, 0–1,000,000 |
| `essential` | Boolean label, defaults false; no hidden objective bonus |
| `mandatory` | Boolean hard constraint, defaults false; never automatically relaxed |

| Quantum option | Default | Allowed |
|---|---:|---|
| `depth` | 2 | 1–4 |
| `shots` | 2048 | 1–8192 |
| `maxiter` | 80 | 10–200 objective-evaluation budget per restart |
| `restarts` | 2 | 1–3 |
| `seed` | 42 | 0–2^31−1 |
| `max_qubits` | 14 | 1–14; can lower the server cap, never raise it |

Example payloads are `docs/examples/optimize-request.json` and `compare-request.json`. The scenario uses the shipped evening example; these are input fixtures, not measurement results.

## Output allocation

`OptimizeResponse` includes schema_version, echoed validated scenario, result, fallback_used=false and actual installed environment versions. `result` includes algorithm, method, status, feasibility (`feasible`, `infeasible`, `unknown`), allocation, runtime_s and optional quantum metadata. An available allocation contains:

- selected/deferred appliance objects, preserving ratings, duration, utility, essential/mandatory and computed energy;
- objective_value, input-order bitstring and selection vector;
- energy_used_wh, energy_remaining_wh, power_used_w, inverter_remaining_w, energy_utilization as a fraction;
- essential_served/essential_total, independently rechecked feasibility and violations.

Deferred means not selected for this request; it is not a promised later operating time. Infeasible classical requests return status=infeasible, feasibility=infeasible, allocation=null and no invented objective. Empty allocations can be valid when no positive-energy service is required and zero capacity is available.

Quantum metadata is present only after actual execution. It includes qubits/device/slack counts, QAOA depth and transpiled circuit depth, shots, seed, optimizer/evaluation budgets/runs, parameters, penalty/scale, expected QUBO energy history, full count distribution and independently checked physical/full-encoding feasible probabilities. SciPy's separate iteration count is null when unavailable. Physical feasibility ignores incorrect slack-register values; full-encoding feasibility includes them. No sample repair or exact-answer substitution occurs.

`CompareResponse` provides classical, quantum, comparison_status, objective_gap, relative_gap, environment and interpretation. Gaps are defined only when both allocations exist, including a zero gap for zero-utility identical outcomes. `comparison_status=complete` means an available measured feasible pair, not quantum optimality or release readiness. `no_feasible_pair` may indicate physical infeasibility or no feasible sample; inspect each solver's status. A no-feasible-sample quantum outcome alone does not prove no physical solution exists.

## Errors and partial results

Normal API errors use `{ "error": { "code": "...", "message": "...", "details": ... } }`. Validation details contain paths/types/messages, without echoing nonfinite input values or Python exceptions. Missing/oversized/failed direct quantum optimization errors include the structured attempted result in `error.details`, with no classical fallback.

| HTTP status | Code / meaning |
|---|---|
| 200 | Valid classical/quantum domain response, including classical infeasibility |
| 200 on compare | Explicit partial comparison if quantum unavailable/oversized/failed; classical result retained and gap null |
| 413 on quantum optimize | `quantum_resource_limit`; exact encoding exceeds qubit/coefficient cap |
| 422 | `validation_error`; JSON/field/cross-field contract failure |
| 429 | `optimizer_busy`; another heavy job is running in this process; Retry-After: 1 |
| 503 on quantum optimize | `quantum_dependency_unavailable` or `quantum_execution_failed` |
| 500 | `internal_error`; logged server-side, no raw internal detail returned |

HTTP routing errors are structured. CORS preflight rejects disallowed origins with the middleware's ordinary 400 response. CORS is a browser policy, not authentication; nonbrowser clients are not blocked by it.

## Future React integration

Run Vite on localhost:5173; call the backend's localhost:8000 URL. Send Content-Type: application/json, inspect HTTP status before rendering, then consume response.status/comparison_status rather than assuming every result is complete. Distinguish an empty selection from an infeasible null allocation. Keep unavailable quantum panels explicit; do not render the classical recommendation as quantum. Retain the request alongside each result and invalidate results after input edits. JSON schema 1.0 is the contract; generated OpenAPI is available only after actual FastAPI startup. No TypeScript/components/design work is included yet.

Configure origins before starting Uvicorn:

```powershell
$env:ANAVO_CORS_ORIGINS = 'http://localhost:5173,http://127.0.0.1:5173'
```

Wildcards, URL credentials, paths, fragments and invalid ports are refused. Credentials are disabled; only GET/POST and Content-Type are allowed. Bind localhost by default. One heavy job per process bounds local concurrency; multiple workers each have their own limit. A production API would additionally need authentication, quotas, request/body limits, cancellation and isolated job workers.

## Validation commands

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_backend_service tests.test_api -v
.\.venv\Scripts\python.exe -m scripts.validate
.\.venv\Scripts\python.exe -m scripts.api_startup_check
.\.venv\Scripts\python.exe -m scripts.benchmark --require-quantum
```

Endpoint tests use actual FastAPI TestClient/HTTPX ASGI requests when installed; they never substitute a fake FastAPI implementation. Mocked missing-dependency/error tests validate transport behavior, not quantum performance. Real quantum API tests are separate conditional tests. See results/validation.json for executed evidence and skips.
