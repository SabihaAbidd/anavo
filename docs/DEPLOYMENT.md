# Backend installation and startup

Final application architecture: **React + TypeScript + Vite -> FastAPI/Python -> Qiskit/classical solver**. The separate React frontend is implemented in frontend/; see frontend/README.md for local startup and production reverse-proxy requirements. Streamlit has no role in the active application or required backend validation.

From the project directory in ordinary Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -c "import fastapi, qiskit, qiskit_aer, numpy, scipy; print('Backend imports OK')"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs for interactive API requests. Health is http://127.0.0.1:8000/health and OpenAPI is http://127.0.0.1:8000/openapi.json. These URLs become available only after the actual server starts. Cloud deployment configuration is described at the end of this document.

Required backend/quantum checks, with no Streamlit tests:

```powershell
.\.venv\Scripts\python.exe -m scripts.api_startup_check
.\.venv\Scripts\python.exe -m scripts.benchmark --require-quantum
.\.venv\Scripts\python.exe -m scripts.verify_release
```

The release gate discovers tests/ only. Historical UI tests are outside that directory in legacy_demo/tests. For optional prototype instructions, see legacy_demo/README.md and requirements-demo.txt; neither is needed for the commands above.

CI installs requirements-lock.txt into a fresh venv, verifies Streamlit is absent, and then runs actual HTTP/quantum checks and backend release verification. A successful CI run is distinct from a syntax-checked workflow file. Existing user environments may still contain Streamlit from older installs; it is no longer requested or imported by this backend. For strict dependency isolation, use a fresh venv rather than assuming an already-populated environment contains only current requirements.

Default CORS allows only http://localhost:5173 and http://127.0.0.1:5173 for the Vite frontend. Set ANAVO_CORS_ORIGINS to explicit origins when deployment is later configured. This research backend has no production authentication, quotas or external-control functionality; bind localhost for the current demonstration.

Current verified environment: the user installed the backend dependencies successfully in .venv; pip check passed and Streamlit is absent. All 72 tests, 12 real HTTP checks, actual QAOA benchmarks and the strict local release gate passed. Backend setup is no longer blocked by missing packages in this environment. New downloads can still be restricted inside the managed agent session; Git publication permissions are a separate concern.

Frontend: run `npm ci` and `npm run dev` from frontend/ while FastAPI runs on port 8000. Open http://127.0.0.1:5173. Build with `npm run build`. Static hosting must separately route /api and /health to FastAPI; never expose this unauthenticated research API without a deployment security design. See "Cloud deployment" below for Vercel hosting.

## Cloud deployment (Vercel frontend + Render backend)

Configuration added 13 November 2026. Not yet deployed: the accounts and clicks below are done by the project owner.

Vercel serverless functions cannot host this backend: Qiskit, Qiskit Aer, SciPy and NumPy exceed the Python function size limit, and the in-memory job queue (`/api/jobs`) needs one long-lived process. The backend therefore runs as a Docker web service, and Vercel serves only the static React build.

1. **Backend on Render.** New → Blueprint → select this GitHub repository. Render reads `render.yaml` and builds `Dockerfile` (Python 3.13-slim, `requirements-lock.txt`, one Uvicorn worker on `$PORT`, health check `/health`). Keep the service name `anavo-api` so its URL is `https://anavo-api.onrender.com`; if Render assigns a different URL, update both destinations in `frontend/vercel.json`. Optionally set `ANAVO_CORS_ORIGINS` to the Vercel URL (for example `https://anavo.vercel.app`).
2. **Frontend on Vercel.** Add New → Project → import this repository, set **Root Directory** to `frontend`. `frontend/vercel.json` builds with `npm run build`, serves `dist/`, and rewrites `/api/*` and `/health` to the Render backend, so `src/api.ts` keeps same-origin relative paths and no CORS preflight is needed.
3. **Before a demo**, open `https://anavo-api.onrender.com/health` once. The free Render plan sleeps after about 15 minutes idle and takes roughly a minute to wake.

Local evidence for this configuration: `npm run build` succeeded; the exact container start command (`uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1`) served `/health`, `/api/scenarios` and a measured `/api/compare` request carrying a non-allowlisted `Origin`, confirming that proxied requests are not blocked. The Docker image itself was not built locally (Docker daemon not running); the Linux install of `requirements-lock.txt` on Python 3.13 is exercised by `backend-ci.yml` on ubuntu-latest.

Security: the API is still an unauthenticated research API with a single optimization slot. A public URL lets anyone submit jobs; keep it up only for the judging period, or add authentication and rate limiting first.
