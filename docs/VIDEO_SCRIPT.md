# ANAVO — 3-minute demo video script

## Before you press record (5 minutes)
1. Start the backend: `.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
2. Start the frontend: `cd frontend` then `npm run dev`
3. Open http://127.0.0.1:5173/ in Chrome, full screen, zoom 90–100%. Close other tabs.
4. Warm-up (so nothing is slow on camera): run the Evening **CLASSICAL + QUANTUM** compare once, run **Optimize society** once.
5. Refresh the page right before recording so the opening animation plays.

## Shot list and narration

| Time | On screen | Say |
|---|---|---|
| 0:00–0:12 | **You, lights on**, talking to camera | "Hi, I'm ___. Tonight I was working on my laptop, the fan was on, my family was —" |
| 0:12–0:18 | **Lights cut. Darkness.** Pause 2 seconds. Strike a match, light the candle. | (silence, then quietly) "…and there it is again." |
| 0:18–0:40 | **Candle-lit face** | "In Pakistan this isn't rare. NEPRA's own data shows high-loss feeders averaging over ten hours of load-shedding a day — some areas up to sixteen. Children study by candlelight. A grandmother's oxygen concentrator runs on a small battery. And every family faces the same question in the dark: *what do I keep on?* A wrong guess and the UPS dies in the middle of the night." |
| 0:40–0:45 | Blow out the candle / cut to screen | "We built ANAVO so nobody has to guess." |
| 0:45–0:55 | **Opening animation** plays, then hero | "ANAVO is quantum-assisted energy resilience for Pakistan." |
| 0:55–1:15 | **Energy Lab**, Evening backup, CLASSICAL | "Each appliance is a yes-or-no decision. We maximise priority under two hard limits: battery energy and inverter power. The Wi-Fi router is mandatory — it can never be dropped. With 240 watt-hours, the exact answer keeps fan, lights and router: utility 24." |
| 1:15–1:45 | Switch to **CLASSICAL + QUANTUM**, run, scroll to **Quantum Insights** | "Now the same problem in Qiskit. We encode it as a QUBO — slack qubits turn the limits into equations — map it to an Ising Hamiltonian and run QAOA on the Aer simulator: 12 qubits, 2,048 shots. Its best valid answer matches the exact optimum. This histogram is what the circuit actually measured — the optimum appears in about 9% of shots, and our independent checker filters every invalid sample." |
| 1:45–2:05 | **Timeline**: Load Pakistani house example → Plan hour by hour | "Real homes don't run everything at once. Our MILP scheduler decides *when* each appliance runs — the pump and washing machine take turns. Score 47 instead of 42, battery tracked every half hour." |
| 2:05–2:35 | **Society grid**: 6 kW default → Optimize society; click a dim home → Verify with QAOA | "And for businesses: one shared battery for a whole housing society. Split power equally and two homes lose their oxygen concentrator. ANAVO keeps every mandatory load on and serves 18% more. Each home's share is small enough to re-verify with QAOA — a hybrid classical-quantum decomposition." |
| 2:35–2:48 | **Pakistan data** then **Architecture** figure | "Every number is grounded in NEPRA, World Bank and NEECA sources. React, FastAPI, Qiskit Aer and exact MILP — 91 automated tests, seeded and reproducible." |
| 2:48–3:00 | Back to camera (lights on) or closing section | "This runs on a simulator, not quantum hardware, and we claim no speedup. But the next time the lights go out, no one should have to guess. ANAVO — power through uncertainty." |

**Tip:** QAOA takes ~20 s. Keep talking over it, or cut the wait in editing.

## Values to use (all verified)

| Where | Input | Expected |
|---|---|---|
| Energy Lab | Evening backup (240 Wh, 100 W, 3 h) | Fan + lights + router, **24**, 180 Wh, 60 W |
| Energy Lab | Limited battery | Lights + router, **15** |
| Energy Lab | Mandatory infeasible | Infeasible (router needs 30 Wh, only 15) |
| Compare | Evening | Quantum **24**, 12 qubits, ~46% feasible, optimum ~9% of shots |
| Timeline | Load Pakistani house example, 18:00, 0 solar | **47 vs 42**, +5 |
| Society | defaults (10/8/2/4 homes, 40 kWh, 6 kW, 4 h, 30%) | **871 vs 740**, 24/24 vs 22 mandatory met |

## Quick pre-recording test (2 minutes)
- [ ] Refresh → opening plays → Escape skips
- [ ] Evening classical = 24
- [ ] Evening compare = 24 / 24, insights panel appears
- [ ] Pakistani house schedule = 47
- [ ] Society = +131, 24/24
- [ ] Architecture figure visible

## Judge Q&A (short answers)
- **Why quantum if classical is faster?** At this size it isn't faster and we say so. We show a correct, verifiable quantum formulation and a hybrid design where QAOA handles small sub-problems.
- **Why 12 qubits for 4 appliances?** 4 decision qubits + 8 slack qubits encoding unused battery and inverter capacity.
- **Why aren't all shots valid?** QAOA gives a probability distribution; we check every sample against the real limits.
- **Did it converge?** COBYLA used its full 80-evaluation budget; we report the best valid sample, not convergence.
- **Is the data yours?** No — cited public figures (NEPRA, World Bank ESMAP, NEECA reporting) and labelled estimates.
- **Reproducible?** Seed 42, pinned versions, 91 tests, saved benchmark JSON.
