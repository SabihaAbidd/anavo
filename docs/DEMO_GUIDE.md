# Demonstration guide

The primary application is now the FastAPI backend, documented in docs/API.md. Start it with `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000` after installing requirements, then use http://127.0.0.1:8000/docs to send the shipped JSON examples. Actual HTTP verification is pending FastAPI installation. The original Streamlit walkthrough below is preserved as an optional legacy demonstration; React remains deferred.

## Launch from the project root

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m scripts.benchmark --require-quantum
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Use the printed localhost URL. The system Python can launch the current classical dashboard with `python -m streamlit run app.py`; the incomplete .venv does not yet contain application dependencies. Do not claim that this fallback executes Qiskit.

## Click sequence

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

If network/package restrictions persist, run the working classical dashboard, show tested algebra and exact results, and explicitly state that Qiskit execution is pending. `results/benchmark_results.json` currently contains honest classical-only records, not a substitute quantum experiment. Once real quantum benchmarks succeed, retain their JSON for an offline recorded-results walkthrough, labeled as a prior simulator run with its timestamp/seed. Do not invent screenshots or numbers.

## Environment recovery

The current managed environment denies Git index writes and PyPI DNS resolution, and no GitHub CLI/remote is configured. In a terminal with normal access, `scripts/finish_setup.ps1` installs, validates, generates actual benchmarks, commits and uses an authorized remote or authenticated GitHub CLI. Re-read REPORT.md/PITCH.md/TASKS.md after it finishes and update pending claims from the new measured output. Never paste credentials into chat.
