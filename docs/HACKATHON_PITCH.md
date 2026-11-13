# ANAVO: hackathon pitch, mapped to the rubric

Challenge: **The Quantum Optimization Challenge** (IBM Qiskit). Domain: **6. Energy & Smart Infrastructure**.
Judging: 100 points across A–E. This guide has five parts:

1. How ANAVO earns each rubric point, in simple words
2. The 3-minute pitch script, word for word, with the rubric item each part earns
3. Slides for a live presentation
4. Judges' questions with short answers
5. Things to keep in mind

All numbers here come from the project's saved results or from a fresh run on 2026-11-13 (Evening scenario: 12 qubits, best answer `1110`, utility 24, valid shots 45.9%, exact best answer measured in 9.0% of shots, circuit depth 33).

---

## Part 1: The rubric, explained simply

### What the hackathon asks for (the 6 steps)
| Step | What it means in plain words | ANAVO's answer |
|---|---|---|
| 01 Identify | Pick a real problem and say who it helps | Families in Pakistan choosing what to power from a small UPS during load-shedding; housing societies sharing one battery |
| 02 Formulate | Write down the choices, the goal, the rules, and one small example | Choices: each appliance ON/OFF. Goal: highest total priority. Rules: battery Wh, inverter W, must-have loads. Example: "Evening backup" (4 appliances) |
| 03 Justify | Say which quantum algorithm and why | QAOA, because the problem is "pick the best ON/OFF combination", which is exactly what QAOA is designed for |
| 04 Implement | Actually run a quantum part in Qiskit | Hand-built QAOA circuit, run on Qiskit Aer, 2,048 measurements |
| 05 Evaluate | Compare with an answer known to be correct | An exact solver tries every combination; the quantum answer is compared with it |
| 06 Reflect | Be honest about limits | Simulator only, no speedup, only 46% of shots valid, 14-qubit limit |

### Required deliverables checklist
- [ ] **Problem statement** (objective, constraints, motivation): Part 2, sections 1–2 below, and [REPORT.md](REPORT.md)
- [x] **Working Qiskit code + GitHub link**: https://github.com/SabihaAbidd/anavo
- [x] **Report with architecture diagram, results, classical comparison, limitations**: [REPORT.md](REPORT.md), [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md), architecture figure `frontend/src/assets/anavo-architecture.svg`
- [ ] **3-minute demo video link** (Google Drive): upload the final video and **set sharing to "Anyone with the link can view"**. Test the link in a private/incognito window.

### Point by point

#### A. Problem validity: 20 points
| Sub-point | Pts | What judges want | What you show / say |
|---|---:|---|---|
| Relevance in the domain | 5 | Is this a real energy problem? | NEPRA: high-loss Karachi feeders average more than 10.5 hours of outage a day, and some areas up to 16. Families really do have to choose what to keep on. |
| Clear optimization formulation | 5 | Can you write the problem as maths? | "Maximise total priority, subject to: energy used ≤ battery, power used ≤ inverter, must-have loads = ON." |
| Scope & feasibility | 5 | Small enough to actually solve? | Small test case: 4 appliances, 12 qubits. Fits the simulator, solves in seconds. |
| Measurable objectives & constraints | 5 | Real units, real numbers? | Watt-hours, watts, priority points. Evening example: 240 Wh battery, 100 W inverter. |

**Say it simply:** "Every appliance is a yes or no. We want the most useful set that the battery and inverter can actually handle."

#### B. Meaningful quantum utilization: 25 points (the biggest section)
| Sub-point | Pts | What judges want | What you show / say |
|---|---:|---|---|
| Correct mapping to quantum | 10 | Did you turn the problem into a quantum form properly? | Problem → **QUBO** (one cost formula with penalties) → **slack qubits** turn "≤" into "=" → **Ising Hamiltonian** → circuit. The penalty is large enough that breaking a rule never pays off, and tests check that every possible state gives the same cost in QUBO and Ising form. |
| Algorithm suitability & justification | 10 | Why QAOA? | QAOA is built for yes/no combination problems. Our problem is exactly that: a knapsack. It's shallow (2 layers), which suits today's small quantum machines. Its dials are tuned by a classical optimiser (COBYLA): hybrid. |
| Quantum materially used + aware of limits | 5 | Is quantum doing real work, not decoration? Do you know its limits? | The quantum answer comes **only** from measured shots; we never copy in the classical answer. Limits: noise-free simulator, no speedup, 14-qubit cap, only 46% of shots valid. |

**Say it simply:** "We rewrote the rules as one score, where lower is better and breaking a rule is very expensive. QAOA is a quantum circuit with dials. A normal computer turns the dials until the circuit mostly gives low-score answers. Then we measure it 2,048 times."

#### C. Implementation & validation: 25 points
| Sub-point | Pts | What judges want | What you show / say |
|---|---:|---|---|
| Working Qiskit implementation | 10 | Does it run? | Live demo: press "Classical + Quantum" and show real results. Code: `src/quantum_solver.py` (H, RZ, RZZ, RX gates, Aer simulator). |
| Interpretable outputs | 5 | Can a normal person understand the result? | Quantum Insights panel: histogram of measured answers, which qubit means what, convergence chart, gate counts, appliances on and off in plain words. |
| Valid classical baseline | 5 | Something to compare against | Exact solver tries all 16 combinations, so its answer is guaranteed best. Quantum best = 24, exact best = 24, **gap 0**. |
| Reproducibility | 5 | Can someone else get the same result? | Fixed seed 42, pinned package versions (`requirements-lock.txt`), 91 automated tests, re-running gives identical counts. Anyone can clone the repo and run it. |

**Say it simply:** "We check the quantum answer against a method that tries every option. They agree. And anyone can rerun it and get the same numbers."

#### D. Innovation & originality: 15 points
| Sub-point | Pts | What judges want | What you show / say |
|---|---:|---|---|
| Originality of the problem | 10 | Not the usual textbook example | Not a generic "EV charging" demo. It's about Pakistani load-shedding and home UPS systems, with a **must-have** rule for things like an oxygen concentrator. It uses real NEPRA, ESMAP and NEECA data. |
| Thoughtful extension | 5 | Did you go beyond the minimum? | Two separate limits (energy *and* power), exact decimal handling, an hour-by-hour planner with solar, a housing-society version for 500 homes (B2B), and single-home QAOA verification inside the society. |

**Say it simply:** "This is a problem we live with every day in Pakistan, and we didn't stop at one house."

#### E. Presentation & defense: 15 points
| Sub-point | Pts | What judges want | What you do |
|---|---:|---|---|
| Clarity of explanation | 10 | Easy to follow | Follow the story: problem → formulation → quantum → results → limits. Use one example (Evening) the whole way through. |
| Demo quality & answers | 5 | Smooth demo, confident answers | Practise the demo 3 times. Learn Part 4 (Q&A). |

---

## Part 2: The 3-minute pitch script

Speak slowly. About 130–150 words per minute. The tag in brackets shows which rubric points each part earns.

### 1. The problem: 0:00–0:30  [A: relevance]
> "In Pakistan, load-shedding is daily life. NEPRA reports that high-loss feeders in Karachi average over ten and a half hours of outage a day, and some areas face up to sixteen.
> Most families have a small UPS. But it can't run everything, so every outage, someone has to guess: fan, lights, Wi-Fi, or the laptop? Guess wrong and the battery dies at 2 a.m.
> ANAVO replaces that guess with an optimal plan."

### 2. The formulation: 0:30–0:55  [A: formulation, measurable constraints]
> "Each appliance is a yes-or-no decision. Each has a priority score set by the family.
> We maximise total priority under two limits: the battery's energy in watt-hours, and the inverter's power in watts. Some loads, like a router for work or an oxygen concentrator, are marked mandatory. They are never dropped. If they can't fit, ANAVO says so honestly.
> Our test case: four appliances, a 240 watt-hour battery and a 100 watt inverter."

### 3. The quantum approach: 0:55–1:35  [B: mapping, justification]
> "This is a classic yes-or-no combination problem, and that's exactly what QAOA, the Quantum Approximate Optimization Algorithm, is designed for.
> First we rewrite the rules as one cost formula, a QUBO. Good choices lower the cost. Breaking a rule adds a penalty so large it can never pay off.
> Limits like 'don't exceed the battery' are inequalities, so we add slack qubits that store the leftover capacity. That gives us 12 qubits: four for the appliances and eight for slack.
> We convert this to an Ising Hamiltonian and build the QAOA circuit in Qiskit by hand: Hadamard gates to start from every possibility at once, then cost and mixer layers. A classical optimiser, COBYLA, tunes the circuit's angles. It's a hybrid quantum-classical loop."

### 4. Live demo: 1:35–2:20  [C: working, interpretable, baseline]
**On screen:** Energy Lab → Evening backup → Classical + Quantum → Optimize → Quantum Insights.
> "Here's the Evening scenario. The exact classical solver tries all sixteen combinations: fan, lights and router, utility 24. The laptop is deferred.
> Now the quantum run on IBM's Aer simulator: 2,048 shots. This histogram is what the circuit actually measured. Every measured answer is checked against the real limits, and the best valid one is also fan, lights and router, utility 24. A gap of zero.
> The exact best answer shows up in about 9% of shots, and about 46% of shots are valid. We show these numbers openly instead of hiding them."

### 5. Beyond one house: 2:20–2:40  [D: originality, extension]
> "Real homes don't run everything at once, so our timeline planner decides *when* each appliance runs, with optional rooftop solar. That raises a typical house from 42 to 47 points.
> And for housing societies sharing one battery, ANAVO plans for up to 500 homes. With 24 homes, an equal split leaves two families without their oxygen concentrator. ANAVO keeps every mandatory load on and serves 18% more priority. Any single home can be double-checked with QAOA."

### 6. Honesty and close: 2:40–3:00  [B: limits, C: reproducibility, E]
> "To be clear, this runs on a noise-free simulator, not quantum hardware, and on problems this small, classical is faster. We don't claim a speedup.
> What we built is a correct, tested quantum pipeline: 91 automated tests, a fixed seed, reproducible results, and a real Pakistani problem ready for better quantum hardware.
> When power is limited, intelligence shouldn't be. This is ANAVO."

*(If you're using the candle-story video from [VIDEO_SCRIPT.md](VIDEO_SCRIPT.md), it covers the same content. Make sure sections 3 and 6 above are fully in it, because they carry 25 + points.)*

---

## Part 3: Slides (if presenting live)

Keep slides light: one idea per slide, few words, big numbers.

| # | Slide | On the slide | Rubric |
|---|---|---|---|
| 1 | Title | ANAVO logo · "When power is limited, intelligence shouldn't be." · Domain 6: Energy & Smart Infrastructure · team names | E |
| 2 | The problem | "10.5+ hours/day of outage (NEPRA)" · photo/illustration of a candle and UPS · "What do we keep on?" | A |
| 3 | Formulation | Choices: xᵢ ∈ {0,1} · Goal: maximise Σ priority · Rules: energy ≤ battery, power ≤ inverter, mandatory = 1 · Evening table (4 appliances) | A |
| 4 | Why QAOA | "Yes/no combination problem → QAOA" · hybrid loop picture: circuit ⇄ COBYLA | B |
| 5 | Quantum mapping | Problem → QUBO → slack qubits → Ising → circuit · "12 qubits = 4 appliances + 8 slack" · small circuit drawing | B |
| 6 | Architecture | The architecture figure (React → FastAPI → classical + QAOA → checker) | C |
| 7 | Results | Table: Ample 30 = 30, Limited 15 = 15, Evening 24 = 24, Impossible: correctly nothing · "Gap 0" · histogram screenshot | C |
| 8 | Live demo | (switch to app) | C, E |
| 9 | Beyond one home | Timeline 42 → 47 · Society: 871 vs 740, 0 vs 2 homes losing oxygen · 500 homes in ~3 s | D |
| 10 | Honest limits | Simulator only · no speedup · 46% valid shots · 14-qubit cap · next steps: real hardware, real meter data | B, C |
| 11 | Close | Tagline · GitHub link · QR code to the demo video | E |

---

## Part 4: Judges' questions with short answers

**Quantum basics**
- **"Why QAOA and not VQE or Grover?"**
  QAOA is made for combinatorial (yes/no combination) problems and has a fixed, problem-based structure. VQE is mainly for chemistry and energy levels. Grover needs a much deeper circuit, which isn't practical today.
- **"What is a QUBO?"**
  The whole problem written as one cost formula using only 0/1 variables and pairs of them. Lowest cost = best valid answer.
- **"What are slack qubits and why do you need them?"**
  A QUBO can only say "equals", but our rules are "no more than". Slack qubits hold the leftover room, so *used + leftover = capacity*.
- **"How did you choose the penalty?"**
  Penalty = 1 + sum of all priorities. Breaking any rule costs at least that much, which is more than any set of appliances can earn. So the lowest-cost answer is always valid if a valid answer exists. The proof is in MATHEMATICAL_MODEL.md.
- **"What does p = 2 mean?"**
  Two layers of cost + mixer gates. More layers can mean better answers but deeper circuits and more tuning.
- **"Why 2,048 shots?"**
  Enough measurements to see a clear pattern in the histogram while keeping the run to seconds.

**Correctness**
- **"How do you know the quantum answer is right?"**
  Every measured answer goes through the same independent rule checker, and the best valid one is compared with the exact solver. Gap = 0 in all solvable benchmarks.
- **"Do you ever use the classical answer as the quantum answer?"**
  Never. If no shot is valid, the app shows "no feasible sample".
- **"Only 46% of shots are valid. Isn't that bad?"**
  It's normal for penalty-based QAOA at low depth. That's why we check every shot. More layers, better tuning, or constraint-preserving mixers could raise it. Those are future work.
- **"What if the must-have appliances don't fit?"**
  ANAVO reports infeasible. It never drops a mandatory load. Our "Mandatory infeasible" benchmark shows exactly that.

**Limits and value**
- **"Is quantum faster here?"**
  No. Classical takes under a millisecond, QAOA a few seconds. We don't claim speedup. The rubric says speedup isn't required.
- **"Then why quantum?"**
  These knapsack-type problems are a leading candidate for future quantum optimisation. We built the full, verified pipeline now, so it can move to real hardware as it improves.
- **"Why only 14 qubits?"**
  Simulating qubits on a laptop doubles the cost for each extra qubit. 14 keeps the demo fast.
- **"Could this run on real IBM hardware?"**
  Yes, it's a standard Qiskit circuit. On real hardware, noise would lower the valid-shot rate. Testing that is our next step.
- **"How does it scale to 500 homes if quantum is limited to 14 qubits?"**
  The society plan uses an exact classical method (MILP). Quantum verifies individual homes. That's a hybrid design, and we're upfront about which part does what.

**Data**
- **"Where do your numbers come from?"**
  NEPRA (outages), ESMAP/World Bank (solar), NEECA (fan ratings). Each value in our dataset has a source or is marked as an estimate.

---

## Part 5: Things to keep in mind

### Do
1. **Use one example the whole way through**: the Evening scenario (240 Wh, 100 W → fan, lights, router, utility 24). Repetition makes it easy to follow.
2. **Spend the most time on quantum (section B, 25 pts) and validation (section C, 25 pts).** Together they're half the score.
3. **Say the honest limits yourself, before anyone asks.** The rubric awards points for "awareness of limitations". Saying "no speedup, simulator only" earns points; it doesn't cost them.
4. **Say "simulator" every time** you talk about quantum results.
5. **Point at the screen** when you say "this histogram is what the circuit measured". Judges should see that quantum is really running.
6. **Keep to 3:00.** Practise with a timer. If you run long, cut the society section, not the quantum or results.
7. **Know the 5 key numbers by heart:** 12 qubits (4 + 8 slack) · 2,048 shots · gap 0 · ~46% valid shots · 91 tests.

### Don't
1. Don't say "quantum is faster", "quantum advantage" or "runs on a quantum computer". Say "runs on a quantum simulator".
2. Don't say "the quantum computer tries all answers at once and picks the best". That's a common myth. Say "QAOA shifts the odds toward good answers, then we measure".
3. Don't read the slides aloud. Slides show numbers; you tell the story.
4. Don't use jargon without a one-line explanation (QUBO, slack, Ising, COBYLA).
5. Don't make up numbers if asked something you don't know. Say "we haven't measured that; it's in our future work".

### Before the demo (technical checklist)
- [ ] Start the backend first (`uvicorn` on port 8000), then the frontend (port 5173). Check that "BACKEND OFFLINE" is not showing.
- [ ] Do one quantum run before presenting, so everything is warmed up. A quantum run takes about 7–20 seconds, so **keep talking while it runs** (script section 4 is written for that).
- [ ] Have a **backup**: a screen recording of the demo and screenshots of the Quantum Insights panel, in case Wi-Fi or the laptop fails.
- [ ] Close other heavy programs. Turn off notifications. Charge the laptop.
- [ ] Zoom the browser so judges can read the numbers.
- [ ] Open the GitHub repo in a tab, and check that the demo video link works in incognito.
- [ ] Only one quantum job runs at a time. If you click twice you'll see "Another optimization is running". Just wait.

### Simple words cheat sheet (if you get nervous)
| Technical word | Say it like this |
|---|---|
| Optimization | Finding the best choice within the limits |
| Constraint | A rule that can't be broken |
| Objective | What we're trying to make as big (or small) as possible |
| Qubit | A quantum bit that can be a mix of 0 and 1 |
| Superposition | Holding many possibilities at once before measuring |
| QUBO | The whole problem written as one score to minimise |
| Penalty | A huge cost for breaking a rule |
| Slack qubit | A helper qubit that stores leftover capacity |
| Ising Hamiltonian | The same score written in the physics form the circuit uses |
| QAOA | A quantum circuit with dials that's tuned to favour good answers |
| COBYLA | The normal-computer method that turns the dials |
| Shot | One run and measurement of the circuit |
| Baseline | An answer we know is correct, used to check the quantum one |
| Feasible | Follows every rule |
| Reproducible | Anyone running it again gets the same result |
