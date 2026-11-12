# Demonstration guide

The final application architecture is React + TypeScript + Vite -> FastAPI -> Qiskit/classical solver. The React frontend in frontend/ is built and is the main demo: start the backend (`uvicorn backend.main:app --host 127.0.0.1 --port 8000`), then `npm run dev` in frontend/, and open http://127.0.0.1:5173/. Swagger at /docs is a secondary view. Streamlit is not required. The optional historical UI commands below require requirements-demo.txt and are outside the backend release.

## Launch from the project root

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m scripts.benchmark --require-quantum
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs after the actual server starts. Exercise all five routes; use docs/examples/optimize-request.json and compare-request.json for the POST bodies. API documentation and raw JSON are the current backend demonstration. Do not describe a dependency-blocked server or unexecuted quantum circuit as verified.

## Optional historical Streamlit walkthrough

This archived walkthrough is not the final frontend or a required demonstration. Install requirements-demo.txt and run `python -m streamlit run app.py` only if explicitly choosing the old prototype. Historical tests live in legacy_demo/tests and are excluded from backend release checks.

1. Choose **Evening backup**. Keep 240 Wh, 100 W, three hours, and default four appliance rows. Explain Wh versus W and the mandatory router.
2. Click **Optimize backup allocation**. Expect exact selection fan/lights/router, utility 24, energy 180 Wh, power 60 W. The laptop is optional; no utility hidden bonuses are added for essential flags.
3. Inspect **Quantum vs classical**. A completed Qiskit run shows actual circuit depth, qubit count, shots, optimizer evaluations, measured feasibility probabilities, decoded best sample, and gap. Explain the top-20 distribution chart's reversed Qiskit bit order and separate physical/auxiliary feasibility. The chart is a subset of outcomes; the downloadable JSON contains every outcome.
4. Download JSON. Confirm recorded versions, parameters, seed and counts. Expected p=2, 2,048 shots, COBYLA, two seeded restarts; these are experiment settings, not a promise of zero gap.
5. Select **Limited battery**: exact lights/router, 60 Wh, utility 15. Then **Mandatory infeasible**: show the hard-constraint message, not a false recommendation.
6. Change capacity after a run. Old results disappear until Optimize is clicked again.

## Questions judges may ask

| Question | Answer |
|---|---|
| Why quantum? | It is a verifiable QAOA research demonstration on a real resilience-motivated objective; classical exact optimization is the practical reference at this scale. |
| Does it outperform classical? | No speedup is claimed. We report actual measured quality/gap and both runtimes when available. |
| Is the quantum result real? | Only an actual Aer count distribution is a measured simulated quantum result. Dependency-unavailable states do not count. There has been no hardware run. |
| What if all samples are invalid? | Report no feasible quantum sample; retain the exact classical result with its label. If mandatory requirements are impossible, report infeasibility. |
| Why slack qubits? | They encode resource inequalities as zero-penalty equalities. Their overhead limits this small simulator demo. |
| Is this an actual schedule? | It selects fixed requested operations and reserves simultaneous power; start-time optimization is future work. |
| Does essential mean mandatory? | No. Essential labels critical services; utility encodes preferences; mandatory is separately enforced. |
| Are powers realistic measurements? | They are illustrative and editable, not a measured Pakistan household dataset. |

## Backup demonstration

If network/package restrictions persist, show the saved classical service/benchmark JSON and tested algebra, clearly labeling it as prior recorded output rather than a live API/quantum run. Streamlit is not a required fallback. Its historical prototype may be used only as an explicit optional demonstration after installing requirements-demo.txt. Once real quantum benchmarks succeed, retain their JSON for an offline walkthrough labeled with timestamp and seed. Do not invent screenshots or measurements.

## Verified local execution and publication

The project .venv now has all backend dependencies and no Streamlit. All 72 required tests and 12 actual Uvicorn HTTP checks passed. Actual QAOA benchmarks use p=2, 2,048 shots and seed 42; both feasible examples reached a zero best-sample utility gap, while the mandatory-infeasible case has no feasible selection. See the raw JSON and REPORT.md for the measured feasibility probabilities and optimizer budget limitations.

The verification probe stops its temporary server; run the Uvicorn command above to keep http://127.0.0.1:8000/docs available during the demo. The React frontend runs separately: in another terminal run cd frontend, npm ci, then npm run dev. Open http://127.0.0.1:5173, select a preset and run Classical or Classical + Quantum. Replay the intro from the footer. Publishing new results and verifying remote CI remain separate tasks; use scripts/publish_now.ps1 in ordinary PowerShell if agent Git permissions remain blocked. Never paste credentials into chat.
