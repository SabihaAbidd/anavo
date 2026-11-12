# Architecture and decisions

```mermaid
flowchart TD
    Future["Future React frontend"] --> API["FastAPI routes"]
    API --> Schemas["Strict Pydantic contracts"]
    Schemas --> Service["Framework-independent service"]
    Service --> Model["Validated physical scenario"]
    Legacy["Preserved Streamlit demo"] --> Model
    Model --> Exact["Exact enumeration"]
    Model --> Qubo["Integer QUBO and Ising"]
    Qubo --> Circuit["Qiskit QAOA circuit"]
    Circuit --> Aer["Aer expectations and shots"]
    Aer --> Check["Decode and check feasibility"]
    Exact --> Compare["Typed allocation and comparison"]
    Check --> Compare
```

`backend/main.py` defines the five HTTP endpoints, structured errors, OpenAPI, CORS and per-process job admission. `backend/schemas.py` owns schema 1.0 requests/responses; cross-field validation delegates to the existing physical model. `backend/service.py` has no HTTP-framework imports: it calls the existing solvers, independently rechecks returned allocations, maps failures without hidden fallback and preserves actual measured metadata. `backend/settings.py` validates the explicit CORS allowlist.

`models.py` owns inputs/physical constraints. `classical_solver.py` enumerates independently of quantum mapping. `optimization.py` handles rational normalization, bounded auxiliary bits, penalty expansion and basis energies. `quantum_solver.py` builds the cost/mixer circuit, optimizes angles, measures, and evaluates all sampled candidates. `evaluation.py` preserves the legacy comparison path and records installed package versions. Existing `app.py` remains unchanged as a legacy demo. `scripts/benchmark.py` persists the existing three reproducible scenarios. Future React consumes these API contracts after a separate design brief; no React code is being developed.

## Significant choices

| What / why | How | Alternatives / tradeoffs | Validation |
|---|---|---|---|
| Fixed-duration selection makes the five-hour MVP auditable | Two resource bounds and mandatory bits | A time-slot MILP models flexibility more accurately, with more variables | Independent enumeration and boundary tests |
| Explicit circuit avoids version-sensitive optimizer wrappers | H, RZ, RZZ, RX; Aer; SciPy COBYLA | Built-in qaoa_ansatz is convenient; manual gates expose signs/scaling | Basis energies and conditional circuit phase/measurement tests |
| Exact decimal normalization prevents hidden discretization | Fraction, LCM, GCD, integer floor capacity | Coarse energy buckets would use fewer qubits but change feasibility | Decimal boundary and QUBO checks |
| Separate physical and auxiliary feasibility aids interpretation | Evaluate appliance bits; also check full penalty | Requiring valid auxiliary bits can discard safe measured decisions | Two measured probabilities and row-level flags |
| Separate backend from future React | Strict Pydantic -> framework-independent service -> existing engine | Embedding HTTP models in mathematics would couple future clients to solver internals | Executed service/schema checks; real FastAPI tests conditional on installation |
| Preserve validated Streamlit work | Existing app unchanged; new API is the primary interface | Rewriting the old UI would spend time ahead of the user's design brief | Original AppTest checks still run |
| Explicit local CORS and compute limits | Two Vite origins, no credentials, one heavy job per process, API limits | This is not a production authentication/job-isolation system | Settings checks run; CORS/busy HTTP tests await FastAPI |
| Explicit blocked state preserves scientific honesty | Import failures/resource limits show classical result labeled | A fabricated quantum fallback is unacceptable | Missing-dependency benchmark records and release gate |

No private repository or external account is needed to run locally. A configured authorized GitHub remote is required for the separate submission/push milestone.

## Route semantics and validation boundaries

Classical infeasibility is a successful domain response with no allocation. Direct quantum optimization returns 413 for excessive encoding, 503 for missing/failed quantum execution. Comparison returns an explicit partial 200 response preserving the exact baseline; unknown gaps remain null. Allocation feasibility and physical resource usage are re-evaluated even if an upstream candidate includes cached values. Mandatory constraints are never relaxed.

The API permits 16 appliances while the independent core retains its prior 20-appliance cap. Quantum request bounds cannot exceed 14 qubits, 4 layers, 8,192 shots, 200 evaluations per restart and 3 restarts. Synchronous handlers run in FastAPI's threadpool, so CPU-bound solvers are not run directly in async event-loop handlers. A semaphore admits one heavy request per server process; it does not provide multi-process/global quotas or cancellation. Do not expose the unauthenticated prototype outside localhost without a deployment design.

Actual execution status is separate from code presence: Pydantic/service checks have run; FastAPI and Qiskit/Aer installs remain blocked by network access. Conditional HTTP/circuit tests are recorded as skipped, not validated endpoints or quantum execution. See docs/API.md and results/validation.json.
