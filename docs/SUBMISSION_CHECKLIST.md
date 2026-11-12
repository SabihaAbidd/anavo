# Submission checklist

## Verified local backend

- [x] Final architecture: React + TypeScript + Vite -> FastAPI -> Qiskit/classical solver.
- [x] Streamlit excluded from backend requirements, imports, CI and required tests; optional legacy source/tests preserved.
- [x] Backend environment installed; imports and pip consistency pass; Streamlit absent.
- [x] Tested versions pinned in requirements-lock.txt (27 packages).
- [x] Physical input, hard constraints, mandatory semantics and exact baseline validated.
- [x] QUBO/Ising formulation, numerical safeguards and bit decoding validated.
- [x] Actual Qiskit Aer QAOA circuits and measurements executed successfully.
- [x] All five FastAPI routes verified by actual requests and 12 Uvicorn HTTP cases.
- [x] Required suite: 72 passed, zero skipped/failed/errors.
- [x] Three actual quantum benchmarks recorded with shots/seeds/depth/counts/feasibility/gaps/runtime/versions.
- [x] Repeated seeded benchmark counts and optimized parameters match.
- [x] Strict local release verification passes; code-dependent evidence matches source fingerprint.
- [x] API, mathematics, research, architecture, report, pitch, demo and setup documentation prepared.
- [x] Existing public anavo repository and initial publications preserved.

## Outstanding publication and frontend

- [ ] Commit/push the latest validated source, dependency lock and measured evidence; verify the new remote SHA/files.
- [ ] Inspect the CI run for that published commit; do not claim an unexecuted CI workflow passed.
- [ ] Obtain the user's design reference before implementing React. No React frontend has been built.
- [ ] Rehearse the submitted demo and ensure the submission links the intended published commit.

Status: **LOCAL BACKEND CHECKS PASSED; LATEST PUBLICATION AND FRONTEND ARE SEPARATE.** No quantum advantage or production-control claim is made.
