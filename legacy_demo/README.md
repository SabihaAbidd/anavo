# Optional historical Streamlit demonstration

ANAVO's final architecture is **React + TypeScript + Vite -> FastAPI -> Qiskit / classical solver**. React implementation awaits the user's design reference. Streamlit is not an application frontend or backend requirement.

The original `app.py`, `.streamlit/config.toml`, historical UI tests and startup probe are preserved for reference. To explicitly install and run the old demonstration from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-demo.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Optional historical checks (not part of backend CI/release):

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s legacy_demo/tests -v
.\.venv\Scripts\python.exe -m legacy_demo.startup_check
```

Installing `requirements.txt` alone does not install Streamlit. The required backend suite discovers only `tests/`; this directory deliberately has no unittest package initializer, so root discovery also leaves the archived tests alone. An existing environment may still contain Streamlit from an earlier install; no automatic uninstall is performed.
