"""Exact time-slot scheduling (MILP via SciPy/HiGHS) with optional rooftop solar.

Each selected appliance runs one contiguous block of its requested duration inside the
outage window. Inverter power is limited per slot (not reserved for the whole outage), and
battery state of charge is tracked slot by slot, so loads can be sequenced instead of being
deferred. Results are re-verified independently of the solver.
"""
from math import pi, sin, isclose
from time import perf_counter
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

MAX_SLOTS = 96
SOLAR_PERFORMANCE_RATIO = 0.75  # Assumed system losses (inverter, temperature, soiling).


def choose_slot(scenario):
    values = [scenario.outage_h] + [a.duration_h for a in scenario.appliances]
    for slot in (1.0, 0.5, 0.25):
        if all(isclose(v / slot, round(v / slot), abs_tol=1e-9) for v in values):
            return slot
    raise ValueError("Durations and outage window must be multiples of 15 minutes for scheduling")


def clock(hour):
    hour %= 24
    return f"{int(hour):02d}:{int(round((hour - int(hour)) * 60)) % 60:02d}"


def solar_profile(slots, slot_h, start_hour, solar_kwp, peak_sun_hours):
    """Half-sine daylight curve 06:00-18:00 scaled to kWp x peak-sun-hours x performance ratio."""
    daily_wh = solar_kwp * 1000 * peak_sun_hours * SOLAR_PERFORMANCE_RATIO
    peak_w = daily_wh * pi / 24  # integral of peak*sin over 12 h = peak*24/pi
    result = []
    for t in range(slots):
        mid = (start_hour + (t + 0.5) * slot_h) % 24
        result.append(peak_w * sin(pi * (mid - 6) / 12) * slot_h if 6 < mid < 18 else 0.0)
    return result


def solve_schedule(scenario, start_hour=18.0, solar_kwp=0.0, peak_sun_hours=5.67, time_limit=10.0):
    started = perf_counter()
    slot_h = choose_slot(scenario)
    slots = int(round(scenario.outage_h / slot_h))
    if slots > MAX_SLOTS:
        raise ValueError(f"Scheduling supports at most {MAX_SLOTS} slots; shorten the outage window")
    apps = scenario.appliances
    durations = [int(round(a.duration_h / slot_h)) for a in apps]
    solar = solar_profile(slots, slot_h, start_hour, solar_kwp, peak_sun_hours)

    # Variables: x[i,s] start choices, then battery level L[t], then curtailed solar c[t].
    starts = []
    for i, d in enumerate(durations):
        starts.extend((i, s) for s in range(slots - d + 1))
    nx = len(starts)
    L0, C0 = nx, nx + slots
    nvar = nx + 2 * slots
    battery = float(scenario.battery_wh)

    utility_scale = max([a.utility for a in apps] + [1.0])
    epsilon = 1e-4 * utility_scale / (battery + 1.0)  # tie-break: keep more energy in reserve
    c = np.zeros(nvar)
    for k, (i, _) in enumerate(starts):
        c[k] = -apps[i].utility
    c[L0 + slots - 1] = -epsilon

    rows, lower, upper = [], [], []

    def add(row, lo, hi):
        rows.append(row); lower.append(lo); upper.append(hi)

    for i, a in enumerate(apps):
        row = np.zeros(nvar)
        for k, (j, _) in enumerate(starts):
            if j == i:
                row[k] = 1
        add(row, 1.0 if a.mandatory else 0.0, 1.0)
    load_rows = []
    for t in range(slots):
        row = np.zeros(nvar)
        for k, (i, s) in enumerate(starts):
            if s <= t < s + durations[i]:
                row[k] = apps[i].power_w
        load_rows.append(row)
        add(row, -np.inf, float(scenario.inverter_w))
    for t in range(slots):
        # L[t] - L[t-1] + load_t*slot_h + c[t] = solar_t ; L[-1] = battery (full at outage start)
        row = load_rows[t] * slot_h
        row[L0 + t] = 1
        row[C0 + t] = 1
        if t:
            row[L0 + t - 1] = -1
        rhs = solar[t] + (battery if t == 0 else 0.0)
        add(row, rhs, rhs)

    integrality = np.concatenate([np.ones(nx), np.zeros(2 * slots)])
    lb = np.zeros(nvar)
    ub = np.concatenate([np.ones(nx), np.full(slots, battery), np.full(slots, np.inf)])
    result = milp(c, integrality=integrality, bounds=Bounds(lb, ub),
                  constraints=LinearConstraint(np.array(rows), lower, upper) if rows else None,
                  options={"time_limit": time_limit, "disp": False})
    runtime = perf_counter() - started
    base = dict(method="Exact MILP time-slot schedule (SciPy HiGHS)", slot_h=slot_h, slots=slots,
                start_hour=start_hour, solar_kwp=solar_kwp, peak_sun_hours=peak_sun_hours,
                solar_performance_ratio=SOLAR_PERFORMANCE_RATIO, runtime_s=runtime)
    if result.x is None:
        status = "infeasible" if result.status == 2 else "failed"
        return dict(base, status=status, feasible=False, utility=None, appliances=[], timeline=[],
                    message="No schedule satisfies every hard constraint; mandatory loads were not relaxed."
                    if status == "infeasible" else f"Solver stopped: {result.message}")

    x = np.round(result.x[:nx]).astype(int)
    chosen = {}
    for k, (i, s) in enumerate(starts):
        if x[k]:
            chosen[i] = s
    # Independent verification: recompute loads and battery from the chosen starts.
    load = [0.0] * slots
    for i, s in chosen.items():
        for t in range(s, s + durations[i]):
            load[t] += apps[i].power_w
    level, timeline, curtailed_total = battery, [], 0.0
    for t in range(slots):
        level = level + solar[t] - load[t] * slot_h
        curtailed = max(0.0, level - battery)
        level = min(level, battery)
        curtailed_total += curtailed
        if load[t] > scenario.inverter_w + 1e-6 or level < -1e-6:
            raise ValueError("Schedule verification failed; refusing to return an infeasible plan")
        timeline.append(dict(slot=t, start=clock(start_hour + t * slot_h),
                             end=clock(start_hour + (t + 1) * slot_h), load_w=load[t],
                             solar_wh=solar[t], battery_wh=max(level, 0.0), curtailed_wh=curtailed,
                             inverter_headroom_w=scenario.inverter_w - load[t],
                             running=[apps[i].name for i, s in chosen.items() if s <= t < s + durations[i]]))
    plan = []
    for i, a in enumerate(apps):
        s = chosen.get(i)
        plan.append(dict(name=a.name, power_w=a.power_w, duration_h=a.duration_h, utility=a.utility,
                         mandatory=a.mandatory, selected=s is not None, start_slot=s,
                         start=clock(start_hour + s * slot_h) if s is not None else None,
                         end=clock(start_hour + (s + durations[i]) * slot_h) if s is not None else None,
                         energy_wh=a.energy_wh if s is not None else 0.0))
    used = sum(p["energy_wh"] for p in plan)
    return dict(base, status="optimal" if result.status == 0 else "time_limit", feasible=True,
                utility=sum(p["utility"] for p in plan if p["selected"]), energy_used_wh=used,
                solar_generated_wh=sum(solar), solar_curtailed_wh=curtailed_total,
                final_battery_wh=timeline[-1]["battery_wh"] if timeline else battery,
                peak_load_w=max(load) if load else 0.0, appliances=plan, timeline=timeline,
                message=None)
