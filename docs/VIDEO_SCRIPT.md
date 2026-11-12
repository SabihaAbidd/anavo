# ANAVO — demo video script and full test checklist

Target length: about 3:00. Spoken lines are written word for word; adjust names freely.

---

## PART A — Full video script

### Scene 1 · Lights on (0:00–0:15)
**Setup:** You at your desk, room lights on, fan running, laptop open. Candle and matches on the desk, out of focus.

> "Assalam-o-alaikum. I'm ___, and this is ANAVO.
> Tonight I was finishing this project — the fan's on, my phone is charging, the Wi-Fi is working, my family is in the next room watching TV. A completely normal evening in Pakistan…"

### Scene 2 · The outage (0:15–0:22)
**Action:** Lights go OFF (someone flips the switch / you switch the main). Fan sound stops. Hold 2 seconds of darkness and silence.

> (sigh, frustrated) "…Oh. The light went off. Again."

### Scene 3 · The candle (0:22–0:30)
**Action:** Strike the match, light the candle. Let the flame settle on your face. Speak slower and quieter.

> "Third time this week. No warning. No idea when it comes back."

### Scene 4 · The emotional plea (0:30–0:58)
**Action:** Look straight into the camera, candle in front of you.

> "For millions of us, this is daily life. According to NEPRA, high-loss feeders in Karachi average more than ten and a half hours of load-shedding every single day. In some areas it can go up to sixteen hours.
>
> Sixteen hours. Children doing homework by candlelight. Shopkeepers losing customers. A grandmother whose oxygen concentrator depends on one small UPS battery.
>
> Most families have some backup — a UPS, a battery, maybe solar. But it's small. And every outage, in the dark, we're forced to make the same decision: *what do we keep on?* The fan? The lights? The router so the kids can study? Guess wrong, and the battery dies at 2 a.m. — in the heat, in the dark.
>
> Electricity isn't a luxury. It's dignity, it's education, it's health. And nobody should have to guess."

### Scene 5 · The turn (0:58–1:05)
**Action:** Blow out the candle. Cut to screen recording (or lights come back on, then cut).

> "So we built ANAVO — a quantum-assisted energy planner that decides, mathematically, what your backup should power."

### Scene 6 · Opening + mission (1:05–1:12)
**Screen:** Refresh → opening animation → hero.
> "ANAVO turns every outage into an optimisation problem — with real constraints and real quantum circuits."

### Scene 7 · Energy Lab (1:12–1:30)
**Screen:** Energy Lab → Evening backup → CLASSICAL → Optimize.
> "Each appliance is a yes-or-no decision. We maximise the family's priorities under two hard limits: battery energy — 240 watt-hours — and inverter power — 100 watts. The Wi-Fi router is mandatory; it can never be dropped. The exact solver keeps the fan, lights and router — utility 24, using 180 watt-hours — and defers the laptop."

### Scene 8 · Quantum (1:30–2:00)
**Screen:** CLASSICAL + QUANTUM → Optimize → scroll to Quantum Insights. (Keep talking during the ~20 s run.)
> "Now the same problem in IBM Qiskit. We encode it as a QUBO — slack qubits turn the battery and inverter limits into equations — convert it to an Ising Hamiltonian, and run QAOA on the Aer simulator: 12 qubits, 2,048 shots, tuned by COBYLA.
> The best valid quantum answer matches the exact optimum: 24.
> This histogram is what the circuit actually measured. The optimum appears in about 9% of shots, and an independent checker rejects every sample that breaks a limit — so ANAVO never recommends an unsafe plan."

### Scene 9 · Timeline (2:00–2:15)
**Screen:** Timeline → Load Pakistani house example → Plan hour by hour.
> "Real homes don't run everything at once. Our scheduler decides *when* each appliance runs. The water pump and washing machine take turns instead of one being cut — 47 points instead of 42, with the battery tracked every half hour."

### Scene 10 · Society — B2B (2:15–2:40)
**Screen:** Society grid → Optimize society → click a dim home → Verify with QAOA.
> "ANAVO also scales to businesses. Here, one shared battery serves a 24-home housing society. If you split power equally, two homes lose their oxygen concentrator. ANAVO keeps every mandatory load on and serves 18% more of everyone's priorities.
> Each home's share is small enough to verify with QAOA — a hybrid classical-quantum design."

### Scene 11 · Data + architecture (2:40–2:50)
**Screen:** Pakistan data → Architecture figure.
> "Every number is grounded in NEPRA, World Bank and NEECA sources. React, FastAPI, Qiskit and exact optimisation — 91 automated tests, seeded and reproducible."

### Scene 12 · Close (2:50–3:00)
**Camera:** Back to you, lights on (or candle relit).
> "We run on a simulator, not quantum hardware, and we don't claim a speedup. But the next time the lights go out, nobody should have to guess. ANAVO — power through uncertainty."

### Filming tips
- Record the candle scenes first, separately, then the screen recording. Edit together.
- Practise lighting the match once off camera.
- Put the phone/camera on a stand; candlelight needs a steady shot.
- If the narration runs long, trim Scene 4, not the demo.

---

## PART B — Full test checklist (do this before recording)

Start both servers, open http://127.0.0.1:5173/ in Chrome. Tick each row.

### 1. Opening and navigation
| # | Do this | Expected | ✓ |
|---|---|---|---|
| 1.1 | Refresh the page | Binary "anavo / power" animation plays ~7 s, then slides into the site | |
| 1.2 | Refresh, press **Escape** | Skips straight to the site | |
| 1.3 | Refresh, click **ENTER ANAVO** | Skips straight to the site | |
| 1.4 | Footer → **REPLAY INTRO** | Animation plays again | |
| 1.5 | Click each top menu link (Energy Lab, Timeline, Society, Data, System) | Scrolls to that section | |
| 1.6 | Look at the Energy Lab header | Shows **BACKEND CONNECTED** and **QISKIT AER AVAILABLE** | |

### 2. Energy Lab — classical (mode: CLASSICAL)
| # | Preset / input | Expected | ✓ |
|---|---|---|---|
| 2.1 | Evening backup (240 Wh, 100 W, 3 h) | Fan, lights, router POWERED; laptop DEFERRED; **utility 24, 180 Wh, 60 W** | |
| 2.2 | Ample backup (400 Wh, 150 W) | All four powered; **utility 30** | |
| 2.3 | Limited battery (90 Wh, 60 W) | Lights + router; **utility 15** | |
| 2.4 | Mandatory infeasible (15 Wh) | Clear "no feasible allocation" message (router needs 30 Wh) | |
| 2.5 | Evening, change battery to **1000**, inverter to **50** | Fan + router; **utility 17**, 150 Wh, 50 W (inverter is the limit) | |
| 2.6 | Evening, battery **200**, inverter **200** | Fan, lights, router; **utility 24** (battery is the limit) | |
| 2.7 | Evening, tick **MUST RUN** on Laptop | Lights, router, laptop; **utility 21** (fan dropped) | |
| 2.8 | Evening, battery **1000**, inverter **5** | **Infeasible** (router needs 10 W) | |
| 2.9 | Evening, battery **0** | **Infeasible** | |
| 2.10 | Change any input after a result | Old result disappears | |
| 2.11 | **ADD APPLIANCE**, then remove one | Row added/removed; can't go below 1 or above 16 | |
| 2.12 | **RESET** | Back to Evening backup | |

### 3. Energy Lab — the "surprise" custom case
Set battery **100**, inverter **60**, outage **2**, appliances:
Fan 40 W 2 h priority 9 · LED lights 10/2/7 · Wi-Fi router 10/2/8 **must run** · Phone charger 10/2/6 · TV 40/2/4.

| # | Mode | Expected | ✓ |
|---|---|---|---|
| 3.1 | CLASSICAL | Lights, router, charger; **utility 21**, 60 Wh, 30 W — **fan deferred despite highest priority** | |
| 3.2 | CLASSICAL + QUANTUM | Quantum also **21**, **11 qubits** | |

### 4. Energy Lab — quantum (mode: CLASSICAL + QUANTUM, ~20 s)
| # | Preset | Expected | ✓ |
|---|---|---|---|
| 4.1 | Evening backup | Both cards **24**, gap 0; **12 qubits**, 2,048 shots, seed 42, ~**46% feasible** | |
| 4.2 | (same run) Quantum Insights panel | KPIs: optimum in ~**9.0%** of shots, **45.9%** feasible, 4 + 8 qubits, 160 evaluations | |
| 4.3 | Histogram | 10 bars; row **1110 ★ EXACT OPTIMUM** highlighted | |
| 4.4 | Convergence chart, Qubit map, Circuit, Landscape | All four cards drawn; 12 qubit tiles; RZZ/RX counts; 16 dots | |
| 4.5 | Limited battery | Both **15**; **9 qubits**; ~24% feasible | |
| 4.6 | Mandatory infeasible | Classical infeasible; quantum "no feasible sample measured" | |
| 4.7 | Evening + add TV (100 W, 2 h, priority 4), battery 600, inverter 200 | Classical solves; quantum **oversized** (needs 21 qubits, limit 14) — honest limit, not a bug | |

### 5. Input validation (should show a clear error, never crash)
| # | Enter | Expected message mentions | ✓ |
|---|---|---|---|
| 5.1 | Appliance watts **-40** | power must be ≥ 0 | |
| 5.2 | Appliance duration **5** with outage **3** | duration cannot exceed outage | |
| 5.3 | Outage **0** | outage must be > 0 | |

### 6. Timeline (hour-by-hour)
| # | Do this | Expected | ✓ |
|---|---|---|---|
| 6.1 | **LOAD PAKISTANI HOUSE EXAMPLE** | Energy Lab now shows 7 appliances, 2000 Wh, 1100 W, 4 h | |
| 6.2 | Start **18:00**, solar **0**, **PLAN HOUR BY HOUR** | **47** with scheduling vs **42** at once, **+5**, peak **1007 W**, **122 Wh** left | |
| 6.3 | Gantt chart | Pump and washing machine at different times; iron deferred | |
| 6.4 | Load vs inverter chart | All purple bars under the dashed inverter line | |
| 6.5 | Start-time dropdown | Only 00:00–23:30; daytime marked "daylight" | |
| 6.6 | Type **110** in solar | Changes to **50** (max) | |
| 6.7 | Evening preset, start **10:00**, solar **1** | Plan solves; yellow solar bars appear; still 24 (inverter is the limit) | |
| 6.8 | Mandatory infeasible preset → Plan | "No schedule satisfies every hard constraint" | |

### 7. Society grid (B2B)
| # | Do this | Expected | ✓ |
|---|---|---|---|
| 7.1 | Defaults (10/8/2/4 homes, 40 kWh, **6 kW**, evening 4 h, fairness 30%) → **OPTIMIZE SOCIETY** | Button shows job status, then **+131** vs equal split (871 vs 740, ~18% more) | |
| 7.2 | KPI: mandatory | **24/24** (equal split **22**) | |
| 7.3 | KPI: fairness | ~**0.96** (equal split ~**0.86**) | |
| 7.4 | Change inverter to **8 kW**, run again | **+90** (932 vs 842) | |
| 7.5 | Click a home tile | Detail shows powered / deferred and equal-split comparison | |
| 7.6 | **VERIFY THIS HOME WITH QAOA** | Job runs; QAOA utility equals exact; qubits and feasible % shown | |
| 7.7 | Change any setting | Old result clears | |

### 8. Pakistan data
| # | Do this | Expected | ✓ |
|---|---|---|---|
| 8.1 | Scroll to Data | Load-shedding bars (0, 10.65, 12.23, 16 h); solar **5.67 kWh/m²/day** | |
| 8.2 | Click a **SOURCE ↗** badge | Opens the cited article / NEPRA document | |
| 8.3 | Click **+** on "Inverter fan" | Jumps to Energy Lab; new row added | |

### 9. Architecture
| # | Do this | Expected | ✓ |
|---|---|---|---|
| 9.1 | Scroll to System | Full figure with animated arrows | |
| 9.2 | **FULL SIZE** / **DOWNLOAD SVG** | Opens / downloads the figure | |

### 10. Phone layout
| # | Do this | Expected | ✓ |
|---|---|---|---|
| 10.1 | F12 → Ctrl+Shift+M → iPhone → refresh | Opening fits; logo small; no sideways page scroll | |
| 10.2 | Scroll every section | Readable; architecture figure scrolls inside its own box | |

### 11. Error handling
| # | Do this | Expected | ✓ |
|---|---|---|---|
| 11.1 | Stop the backend, reload, click Optimize | **BACKEND OFFLINE** + "Start FastAPI on port 8000" | |
| 11.2 | Restart backend, reload | Connected again | |

### 12. Automated checks (optional, terminal)
| Command | Expected |
|---|---|
| `.\.venv\Scripts\python.exe -m scripts.validate` | **91 passed**, 0 failed |
| `cd frontend` → `npm run build` | Build succeeds |
| `npm run test:integration` (both servers running) | **3 pass**, 0 fail |

---

## PART C — Judge Q&A
- **Why quantum if classical is faster?** At this size it isn't faster, and we say so. We show a correct, verifiable quantum formulation and a hybrid design where QAOA handles small sub-problems.
- **Why 12 qubits for 4 appliances?** 4 decision qubits + 8 slack qubits that encode unused battery and inverter capacity.
- **Why aren't all shots valid?** QAOA outputs a probability distribution; we check every sample against the real limits.
- **Did it converge?** COBYLA used its full 80-evaluation budget; we report the best valid sample, not convergence.
- **Is the data yours?** No — cited public figures (NEPRA, World Bank ESMAP, NEECA reporting) and clearly labelled estimates.
- **Is it reproducible?** Seed 42, pinned versions, 91 tests, saved benchmark files in `results/`.
