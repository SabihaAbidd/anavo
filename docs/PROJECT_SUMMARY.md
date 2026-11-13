# ANAVO: the complete project summary (no quantum background needed)

> **When power is limited, intelligence shouldn't be.**

This document explains the whole project in plain language: what problem it solves, how it works, how quantum computing fits in, what was actually proven, and what was not. You do not need to know any physics or quantum computing to follow it. Technical words get explained the first time they show up, and there is a glossary at the end.

---

## 1. ANAVO in one paragraph

Pakistan has long, frequent power outages (load-shedding). Many homes get through them with a battery and an inverter (a UPS). The battery holds a limited amount of energy, and the inverter can only supply a limited amount of power at once, so during an outage people have to choose what to keep on: fan, lights, Wi-Fi, laptop, fridge, a medical device. ANAVO makes that choice for them. It finds the combination of appliances that gives the most value without draining the battery or overloading the inverter, and it never drops an appliance the user marked as must-have. It solves the problem two ways: with an exact classical method that is guaranteed correct, and with a quantum algorithm (QAOA) running on a quantum computer simulator. Then it compares the two answers side by side and is honest about the result.

---

## 2. The real-world problem

During an outage, a household with a UPS faces two separate limits:

| Limit | Unit | Plain meaning | Everyday analogy |
|---|---|---|---|
| **Battery energy** | watt-hours (Wh) | How much electricity is stored in total | How much water is in the tank |
| **Inverter power** | watts (W) | How much can be drawn *at the same moment* | How wide the tap is |

A 40 W fan running for 3 hours uses 40 × 3 = **120 Wh** of energy. You can run out of energy (tank empty) or exceed power (too much through the tap at once, and the inverter trips). Both have to be respected.

The user also gives every appliance:
- a **utility score**: how much they care about it (Fan = 9, Laptop = 6, and so on). Higher means more important.
- an optional **mandatory** flag: "this must stay on no matter what", such as a router for work or an oxygen concentrator. ANAVO treats this as a hard rule. If the mandatory loads cannot fit, ANAVO says so plainly. It never quietly drops one.
- an **essential** label, which is only for reporting ("3 of 3 essential services served") and does not change the maths.

**The goal:** pick the set of appliances with the **highest total utility** that stays within battery energy and inverter power and includes every mandatory appliance.

Computer scientists call this a **knapsack problem**: you have a bag with limited room and want to pack the most valuable items. It looks simple, but the number of possible combinations doubles with every appliance added. 4 appliances give 16 combinations, 10 give 1,024, 20 give over a million, and 50 give more than a quadrillion. This kind of rapidly exploding search is exactly the kind of problem people hope quantum computers will one day help with.

---

## 3. What the app does (the four features)

| Feature | Who it's for | What it does | How it's solved |
|---|---|---|---|
| **Energy Lab** (household optimizer) | One home (B2C) | Chooses which appliances to run within battery and inverter limits | Exact classical search, plus quantum QAOA for comparison |
| **Quantum Insights** | Anyone curious / judges | Shows what the quantum run actually did: measured results, the chance of hitting the best answer, how the tuning converged, which qubit means what, the circuit's gate counts | Real measurements from the quantum simulator |
| **Timeline** (hour-by-hour planner) | One home | Decides *when* each appliance runs, so loads can take turns instead of all running at once; tracks battery level over time; can include rooftop solar | Exact classical method (MILP, explained below) |
| **Society Grid** (B2B) | Housing societies / microgrids with one shared battery bank | Shares one big battery and inverter across up to 500 homes, keeps every home's mandatory loads on, can guarantee each home a minimum fair share, and compares against "just split it equally" | Exact classical MILP; any single home can be re-checked with QAOA |
| **Pakistan data** | Everyone | Real outage hours (NEPRA), solar data (ESMAP), fan ratings (NEECA) and an appliance library, each with its source or marked as an estimate | `data/pakistan_energy.json` |

**Example results** (all reproducible with the project's tests):
- A typical Pakistani house scores **47** when ANAVO schedules appliances hour by hour, compared with **42** when everything has to run at once.
- A 24-home society sharing 40 kWh / 6 kW gets **871** priority points with ANAVO versus **740** for an equal split, and keeps every home's oxygen concentrator running. The equal split leaves 2 homes without one.
- 500 homes (3,076 on/off decisions) solve in about **3 seconds**.

---

## 4. The classical solver (the "answer key")

Before getting to quantum, here's the simple, reliable method.

**Exact enumeration** (`src/classical_solver.py`) tries every possible combination. Each appliance is either ON (1) or OFF (0), so a choice for 4 appliances looks like `1110` (Fan on, Lights on, Router on, Laptop off). The program checks all 16 strings, throws away any that break a rule, and keeps the one with the highest utility. It is guaranteed to find the true best answer, and for household-sized problems (up to 20 appliances) it is very fast.

This is ANAVO's **ground truth**. The quantum answer is always checked against it.

For the bigger features (timeline and housing society), trying every combination is impossible, so ANAVO uses **MILP** (Mixed-Integer Linear Programming) through SciPy's HiGHS solver. MILP is a mature, industrial-strength classical technique that finds proven-optimal answers to large problems of this kind. Every plan it returns is re-checked independently before being shown to the user.

---

## 5. Quantum computing from zero

### 5.1 Bits vs qubits
A normal computer stores information in **bits**, each either 0 or 1. A **qubit** (quantum bit) can be in a **superposition**, a blend of 0 and 1 at the same time, with some "weight" on each. With several qubits, the system can be in a blend of **all possible combinations at once**. Four qubits can hold a blend of all 16 appliance choices simultaneously.

### 5.2 Measurement
You can't read a blend directly. When you **measure** qubits, the blend "collapses" to one ordinary answer such as `1110`, chosen at random. Combinations with more weight come up more often. So you run the circuit many times (ANAVO uses **2,048 runs, called "shots"**) and count how often each answer appears. The result is a histogram.

### 5.3 Quantum gates and circuits
You change qubits' weights with **gates**: small operations like rotations. A sequence of gates is a **circuit**. The skill is in designing a circuit that piles weight onto good answers and drains it from bad ones, so that when you measure, the best answer shows up often.

### 5.4 Simulator, not hardware
Real quantum computers exist but are small, noisy, and expensive to access. ANAVO runs its circuits on **Qiskit Aer**, IBM's quantum-computer **simulator**, which runs on a normal computer and behaves exactly like an ideal, noise-free quantum computer would. The circuits are real Qiskit quantum circuits and could be sent to IBM hardware later. Today's results are simulator results, and the project says so everywhere.

---

## 6. How ANAVO uses quantum, step by step

The quantum algorithm is **QAOA** (Quantum Approximate Optimization Algorithm). In one sentence: QAOA is a tunable quantum circuit that is repeatedly adjusted by a normal computer until measuring it tends to give low-cost (good) answers.

To use it, the household problem has to be translated into the language a quantum computer understands. Here is the full pipeline, with the code file for each step:

```
 Household problem ──► QUBO ──► Ising ──► QAOA circuit ──► tune (COBYLA) ──► measure 2,048 times ──► decode & check ──► compare with exact answer
 (models.py)        (optimization.py)        (quantum_solver.py)                                         (evaluation.py)
```

### Step 1: Turn rules into a single "cost" number (the QUBO)
Quantum optimizers can't follow "if/then" rules. They only know how to make one number, the **cost** (also called **energy**), as low as possible. So ANAVO rewrites the whole problem as one cost formula:

```
cost = − (total utility of chosen appliances)
       + BIG PENALTY × (how badly the battery limit is broken)²
       + BIG PENALTY × (how badly the inverter limit is broken)²
       + BIG PENALTY × (number of mandatory appliances left off)
```

- More utility makes the cost go down, which is good.
- Breaking any rule adds a huge penalty, which is bad.

The penalty is set to `1 + (sum of all utilities)`, so breaking a rule always costs more than any utility could earn back. This is proven mathematically in [MATHEMATICAL_MODEL.md](MATHEMATICAL_MODEL.md): if a valid answer exists, the lowest-cost answer is always the valid one with the highest utility.

This kind of formula, built only from 0/1 variables multiplied in pairs, is called a **QUBO** (Quadratic Unconstrained Binary Optimization). It's the standard input format for quantum optimizers.

### Step 2: Slack qubits (handling "≤")
The rule "energy used ≤ battery" is an inequality, and a QUBO can only express "equals". The trick is to add **slack**: an extra amount that fills the gap.

> energy used + slack = battery capacity

If you use 180 Wh of a 240 Wh battery, the slack is 60 Wh worth. The slack is stored in **extra qubits** (slack qubits) using binary counting (1, 2, 4, 8 …). So some qubits represent appliances and some represent "leftover room".

ANAVO also converts decimals into exact whole numbers first (using fractions), so no rounding ever changes whether something fits. If an encoding would need too many qubits (more than 14 in this project), or the numbers get too fine for reliable computer arithmetic, ANAVO refuses and says so instead of guessing.

**Worked example (the "Evening backup" scenario):**

| Appliance | Power | Hours | Energy | Utility | Mandatory |
|---|---:|---:|---:|---:|---|
| Fan | 40 W | 3 | 120 Wh | 9 | No |
| LED lights | 10 W | 3 | 30 Wh | 7 | No |
| Wi-Fi router | 10 W | 3 | 30 Wh | 8 | **Yes** |
| Laptop | 60 W | 2 | 120 Wh | 6 | No |

Battery 240 Wh, inverter 100 W. This needs **12 qubits**: 4 for the appliances and 8 slack qubits (4 for the battery rule, 4 for the inverter rule). The best answer is **Fan + Lights + Router** (`1110`): utility 24, 180 Wh, 60 W. The laptop doesn't fit alongside the fan.

### Step 3: Ising form
Physicists describe qubits as tiny magnets pointing up or down, written +1 and −1 instead of 0 and 1. ANAVO converts the QUBO into this **Ising** form, which tells it directly which gates to apply and how strongly. It's a change of notation, like converting °C to °F. The tests check that every one of the 2ⁿ answers gets exactly the same cost in both forms.

### Step 4: Build the QAOA circuit
The circuit (`build_qaoa_circuit` in `src/quantum_solver.py`) is built by hand from four gate types:

1. **H (Hadamard) on every qubit**: starts in an equal blend of every possible combination, so nothing is favoured yet.
2. **RZ and RZZ gates (the "cost layer")**: nudge each combination according to its cost. RZ handles single-appliance terms; RZZ handles pairs (for example, "fan and laptop together use too much power").
3. **RX gates (the "mixer layer")**: shuffle weight between neighbouring combinations so the search doesn't get stuck.
4. Repeat cost + mixer **p** times. ANAVO uses **p = 2** layers.

Each layer has two dials: **γ (gamma)**, how strongly the cost is applied, and **β (beta)**, how strongly to mix. With p = 2 there are four dials in total.

### Step 5: Tune the dials (the hybrid loop)
Nobody knows the best dial settings in advance, so a normal computer searches for them:

1. Pick dial settings.
2. Run the circuit on the simulator and compute the average cost of the answers it would produce.
3. **COBYLA**, a classical optimisation routine from SciPy, chooses better dial settings.
4. Repeat (up to 80 tries per attempt, with 2 attempts from different random starting points), and keep the best.

That's why QAOA is called a **hybrid quantum–classical** algorithm. The quantum circuit evaluates, and the classical computer steers. The app shows this convergence as a chart in Quantum Insights.

### Step 6: Measure 2,048 times
With the best dials, the circuit is run with real measurement **2,048 times** (seeded, so it's reproducible). Each shot gives a string of 0s and 1s for all qubits.

### Step 7: Decode and check every answer honestly
- Qiskit prints qubits in reverse order, so ANAVO flips each string, then reads the first bits as appliance choices (the slack bits are just helpers).
- **Every measured answer is re-checked** against the real battery, inverter and mandatory rules using the same independent checker the classical solver uses.
- The **best answer that actually passes the rules** is reported as the quantum result.
- If none of the 2,048 shots is valid, ANAVO reports **"no feasible sample"**. It never fills in the classical answer and labels it quantum.

### Step 8: Compare with the exact answer
`src/evaluation.py` runs both solvers on the identical input and reports:
- both recommendations side by side,
- the **gap** (how much utility the quantum answer missed; 0 means it matched),
- what fraction of the 2,048 shots were valid,
- the chance of measuring the exact best answer,
- qubit count, circuit depth, gate counts, runtime, and the software versions used.

---

## 7. What the quantum results actually showed

From the saved benchmark run (`results/benchmark_results.json`: p = 2, 2,048 shots, seed 42):

| Scenario | Exact best utility | QAOA best utility | Gap | Qubits (slack) | Valid shots |
|---|---:|---:|---:|---:|---:|
| Ample backup (everything fits) | 30 | 30 | 0 | 4 (0) | 100% |
| Limited battery | 15 | 15 | 0 | 9 (5) | about 24% |
| Mandatory infeasible (router can't fit) | none | no feasible sample | n/a | 8 (4) | 0%, correctly |

What this means:
- In both solvable cases, the quantum method **found the true best answer** among its measurements.
- In the impossible case, it **correctly found nothing valid**, and ANAVO didn't pretend otherwise.
- With tighter limits, only about a quarter of the shots were valid, which is why every answer gets checked.
- Running the benchmark again with the same code reproduced the same counts and dial settings.

### What ANAVO does **not** claim
This matters, and judges will ask about it:
- **No quantum speedup.** On these small problems, the classical solver is faster, at well under a millisecond against about 1–2 seconds for QAOA. Today's quantum hardware and simulators don't beat classical methods for this.
- **No real hardware.** All runs are on a noise-free simulator.
- **No fake results.** If the quantum side is unavailable, too large, or finds nothing valid, the app says exactly that.

### So why use quantum at all?
- Knapsack-style problems are a leading candidate for future quantum optimisation. ANAVO builds the full, correct pipeline (problem → QUBO → circuit → measurement → verification) now, so it's ready to test on real quantum hardware as that hardware improves.
- It's a working, transparent demonstration that a real Pakistani energy problem can be encoded and solved on a quantum circuit, with every step checked against a guaranteed-correct baseline.
- The Quantum Insights panel turns the quantum run into something people can actually see: which qubit means what, how the dials converged, and how often the best answer appeared.

---

## 8. Architecture (how the pieces connect)

```
 Browser (React + TypeScript + Vite)          ← what the user sees: frontend/
        │  HTTP / JSON
        ▼
 FastAPI backend (Python, Pydantic checks)    ← backend/
        │
        ▼
 Optimization engine (pure Python)            ← src/
   ├─ exact classical solver   (classical_solver.py)
   ├─ QUBO / Ising builder     (optimization.py)
   ├─ QAOA on Qiskit Aer       (quantum_solver.py)
   ├─ hour-by-hour MILP        (scheduler.py)
   └─ housing-society MILP     (fleet.py)
```

- **Frontend** (`frontend/`): React with a pixel/cyberpunk design, an animated opening, and the Energy Lab, Timeline, Society Grid, Pakistan Data and Architecture sections.
- **Backend** (`backend/`): FastAPI web server. It validates every input strictly (no negative watts, unique names, and so on), calls the engine, re-checks every answer, and returns clear errors. Slow quantum jobs can run in a background job queue. Only one heavy job runs at a time; others get a "busy, try again" (HTTP 429).
- **Engine** (`src/`): all the maths, with no web code mixed in, so it can be tested on its own.
- **Main API routes:** `/health`, `/api/scenarios`, `/api/optimize`, `/api/compare`, `/api/schedule`, `/api/fleet/optimize`, `/api/jobs`, `/api/data/pakistan`. Full details are in [API.md](API.md).
- **Deployment config:** Docker + Render for the backend, Vercel for the frontend ([DEPLOYMENT.md](DEPLOYMENT.md)). These are configured but not deployed yet.
- **Legacy:** the original Streamlit prototype (`app.py`) is kept for history only and isn't part of the final app.

**Tech stack:** React, TypeScript, Vite, GSAP (animation) · Python 3.13, FastAPI, Pydantic, Uvicorn · Qiskit, Qiskit Aer · NumPy, SciPy (COBYLA, HiGHS MILP).

---

## 9. How we know it works (testing and evidence)

- **91 automated backend tests**, all passing with zero skipped, covering the solvers, the QUBO maths, real quantum circuits, the API, scheduling, housing societies, jobs and the dataset (`python -m scripts.validate`).
- **Real HTTP checks**: a live server is started and actually called, including real quantum requests (`scripts.api_startup_check`).
- **Quantum benchmarks** on the simulator, with saved results and a reproducibility check (`scripts.benchmark --require-quantum`).
- **Strict release gate** (`scripts.verify_release`): fails if any test was skipped, any quantum benchmark is missing, or the saved evidence is out of date with the code (checked with source-file fingerprints).
- **Frontend**: production build passes; live integration tests through the proxy pass, including a quantum job.
- **GitHub Actions CI** runs the backend checks on every push.

All evidence is saved in `results/`, and the history of what was checked and when is in [TASKS.md](../TASKS.md).

---

## 10. Limitations and future work

- **Decision support, not a controller.** ANAVO recommends; it doesn't switch appliances on or off.
- **Appliance figures** are published ratings or typed estimates, not measurements from real homes.
- **Simple models:** no motor start-up surges, no fridge on/off cycling, no battery ageing, no outage forecasting. Solar uses an average daily curve, not a weather forecast.
- **Size limits:** quantum encodings up to 14 qubits (simulating more gets very slow on a laptop), classical enumeration up to 20 appliances (MILP features scale to 500 homes).
- **Simulator only,** noise-free, so no hardware or speedup evidence.
- **Future:** real household metering data, outage and solar forecasting, runs on real (noisy) IBM quantum hardware, smarter qubit encodings, and a production-grade job queue.

---

## 11. Likely questions and short answers

**"Is this actually quantum?"**
Yes. The quantum part is a real Qiskit circuit (H, RZ, RZZ and RX gates) built from the problem and measured 2,048 times on IBM's Aer simulator. It's simulated quantum, not hardware, and we say so.

**"Is the quantum version faster?"**
No, and we don't claim it is. At this size, classical is faster. The value is a correct, verified quantum pipeline that's ready for better hardware.

**"How do you know the quantum answer is right?"**
Every measured answer is re-checked against the real limits, and the best valid one is compared with the guaranteed-correct classical answer. In our benchmarks the gap was zero.

**"What are slack qubits?"**
Helper qubits that store "leftover battery" and "leftover inverter room", so a "must not exceed" rule can be written as an exact equation the quantum circuit can handle.

**"What happens if the must-have appliances don't fit?"**
ANAVO reports that the plan is infeasible. It never drops a mandatory load to force an answer.

**"Why 14 qubits?"**
Simulating qubits on a normal computer doubles in cost with each one added. 14 keeps demo runs to seconds.

**"What's new for Pakistan specifically?"**
Real NEPRA outage data, ESMAP solar data, NEECA fan ratings, and a shared-battery planner for housing societies, where common UPS and solar systems are increasingly used.

---

## 12. Glossary

| Term | Meaning |
|---|---|
| **Wh (watt-hour)** | Amount of energy; a battery's "tank size" |
| **W (watt)** | Rate of power; what the inverter can supply at one moment |
| **Inverter / UPS** | Device that turns battery power into household electricity |
| **Utility** | The user's importance score for an appliance |
| **Mandatory** | Must stay on; a hard rule |
| **Feasible** | Obeys every rule (battery, inverter, mandatory) |
| **Knapsack problem** | Choosing the most valuable items that fit a limited capacity |
| **Exact enumeration** | Trying every combination; guaranteed best |
| **MILP** | Mixed-Integer Linear Programming; a powerful classical method for exact large-scale planning |
| **Bit / qubit** | Classical 0-or-1 / quantum unit that can be a blend of 0 and 1 |
| **Superposition** | A qubit (or group of qubits) holding a blend of possibilities at once |
| **Measurement / shot** | Reading the qubits, which gives one ordinary answer; one run = one shot |
| **Gate / circuit** | An operation on qubits / a sequence of operations |
| **Qiskit / Aer** | IBM's quantum programming toolkit / its quantum simulator |
| **QUBO** | The whole problem rewritten as one cost formula over 0/1 variables |
| **Penalty** | A huge extra cost added when a rule is broken |
| **Slack qubit** | Helper qubit storing leftover capacity so "≤" becomes "=" |
| **Ising** | The same cost written in physics notation (+1/−1 instead of 0/1) |
| **QAOA** | Quantum Approximate Optimization Algorithm; a tunable circuit that favours low-cost answers |
| **Depth p** | How many cost + mixer layers the QAOA circuit has (ANAVO: 2) |
| **γ, β (gamma, beta)** | The tuning dials of each QAOA layer |
| **COBYLA** | The classical routine that tunes the dials |
| **Hybrid quantum–classical** | Quantum circuit evaluates, classical computer steers |
| **Gap** | Exact best utility minus quantum best utility (0 = matched) |
| **Quantum speedup / advantage** | Being faster or better than the best classical method; **not claimed** by ANAVO |
