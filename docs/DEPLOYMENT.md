# Backend installation and startup

Final application architecture: **React + TypeScript + Vite -> FastAPI/Python -> Qiskit/classical solver**. The React frontend is not implemented yet; its design will be supplied separately. Streamlit has no role in the active application or required backend validation.

From the project directory in ordinary Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -c "import fastapi, qiskit, qiskit_aer, numpy, scipy; print('Backend imports OK')"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs for interactive API requests. Health is http://127.0.0.1:8000/health and OpenAPI is http://127.0.0.1:8000/openapi.json. These URLs become available only after the actual server starts. No cloud deployment has been performed.

Required backend/quantum checks, with no Streamlit tests:

```powershell
.\.venv\Scripts\python.exe -m scripts.api_startup_check
.\.venv\Scripts\python.exe -m scripts.benchmark --require-quantum
.\.venv\Scripts\python.exe -m scripts.verify_release
```

The release gate discovers tests/ only. Historical UI tests are outside that directory in legacy_demo/tests. For optional prototype instructions, see legacy_demo/README.md and requirements-demo.txt; neither is needed for the commands above.

CI installs requirements-lock.txt into a fresh venv, verifies Streamlit is absent, and then runs actual HTTP/quantum checks and backend release verification. A successful CI run is distinct from a syntax-checked workflow file. Existing user environments may still contain Streamlit from older installs; it is no longer requested or imported by this backend. For strict dependency isolation, use a fresh venv rather than assuming an already-populated environment contains only current requirements.

Default CORS allows only http://localhost:5173 and http://127.0.0.1:5173 for the future Vite frontend. Set ANAVO_CORS_ORIGINS to explicit origins when deployment is later configured. This research backend has no production authentication, quotas or external-control functionality; bind localhost for the current demonstration.

Current verified environment: the user installed the backend dependencies successfully in .venv; pip check passed and Streamlit is absent. All 72 tests, 12 real HTTP checks, actual QAOA benchmarks and the strict local release gate passed. Backend setup is no longer blocked by missing packages in this environment. New downloads can still be restricted inside the managed agent session; Git publication permissions are a separate concern.
