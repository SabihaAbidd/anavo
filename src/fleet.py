"""Shared-backup allocation for a housing society or microgrid (B2B).

Many homes share one battery bank and one inverter. An exact MILP (SciPy/HiGHS) chooses
which appliances run in which home, subject to shared energy and power limits, every home's
mandatory loads, and an optional fairness floor. The result is compared with the common
operating rule of splitting capacity equally between homes and solving each home alone.
"""
from time import perf_counter
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from .classical_solver import solve_exact
from .models import Scenario

MAX_HOMES = 500
MAX_VARIABLES = 8000


def jain_index(values):
    values = [v for v in values]
    if not values or not any(values):
        return 0.0
    return sum(values) ** 2 / (len(values) * sum(v * v for v in values))


def solve_fleet(homes, battery_wh, inverter_w, outage_h, fairness_floor=0.0, time_limit=20.0):
    """homes: list of dicts {name, weight, appliances: [Appliance, ...]}"""
    started = perf_counter()
    if not homes or len(homes) > MAX_HOMES:
        raise ValueError(f"Use between 1 and {MAX_HOMES} homes")
    if not 0 <= fairness_floor <= 1:
        raise ValueError("fairness_floor must be between 0 and 1")
    index = [(h, i) for h, home in enumerate(homes) for i in range(len(home["appliances"]))]
    if len(index) > MAX_VARIABLES:
        raise ValueError(f"Fleet has {len(index)} appliance decisions; limit is {MAX_VARIABLES}")
    for home in homes:
        Scenario(home["name"], tuple(home["appliances"]), battery_wh, inverter_w, outage_h)  # validate
    n = len(index)
    app = lambda h, i: homes[h]["appliances"][i]
    c = np.array([-homes[h]["weight"] * app(h, i).utility for h, i in index])
    rows, lower, upper = [], [], []
    rows.append([app(h, i).energy_wh for h, i in index]); lower.append(-np.inf); upper.append(battery_wh)
    rows.append([app(h, i).power_w for h, i in index]); lower.append(-np.inf); upper.append(inverter_w)
    for h, home in enumerate(homes):
        total = sum(a.utility for a in home["appliances"])
        if fairness_floor and total:
            rows.append([app(k, i).utility if k == h else 0.0 for k, i in index])
            lower.append(fairness_floor * total); upper.append(np.inf)
    lb = np.array([1.0 if app(h, i).mandatory else 0.0 for h, i in index])
    result = milp(c, integrality=np.ones(n), bounds=Bounds(lb, np.ones(n)),
                  constraints=LinearConstraint(np.array(rows), lower, upper),
                  options={"time_limit": time_limit, "disp": False})
    runtime = perf_counter() - started
    baseline = equal_split(homes, battery_wh, inverter_w, outage_h)
    base = dict(method="Exact shared-capacity MILP (SciPy HiGHS)", homes=len(homes), decisions=n,
                battery_wh=battery_wh, inverter_w=inverter_w, outage_h=outage_h,
                fairness_floor=fairness_floor, runtime_s=runtime, baseline=baseline)
    if result.x is None:
        return dict(base, status="infeasible" if result.status == 2 else "failed", feasible=False,
                    home_results=[], message="No society-wide plan satisfies every mandatory load and fairness floor."
                    if result.status == 2 else f"Solver stopped: {result.message}")
    x = np.round(result.x).astype(int)
    per_home = []
    for h, home in enumerate(homes):
        picks = [bool(x[k]) for k, (hh, _) in enumerate(index) if hh == h]
        apps = home["appliances"]
        served = sum(a.utility for a, p in zip(apps, picks) if p)
        total = sum(a.utility for a in apps)
        per_home.append(dict(name=home["name"], weight=home["weight"], selection=[int(p) for p in picks],
                             selected=[a.name for a, p in zip(apps, picks) if p],
                             deferred=[a.name for a, p in zip(apps, picks) if not p],
                             utility=served, max_utility=total,
                             service_ratio=served / total if total else 1.0,
                             energy_wh=sum(a.energy_wh for a, p in zip(apps, picks) if p),
                             power_w=sum(a.power_w for a, p in zip(apps, picks) if p),
                             mandatory_met=all(p for a, p in zip(apps, picks) if a.mandatory),
                             baseline_utility=baseline["home_utilities"][h]))
    energy = sum(r["energy_wh"] for r in per_home)
    power = sum(r["power_w"] for r in per_home)
    if energy > battery_wh + 1e-6 or power > inverter_w + 1e-6 or not all(r["mandatory_met"] for r in per_home):
        raise ValueError("Fleet verification failed; refusing to return an infeasible plan")
    utility = sum(r["utility"] for r in per_home)
    return dict(base, status="optimal" if result.status == 0 else "time_limit", feasible=True,
                utility=utility, weighted_utility=float(-result.fun), energy_used_wh=energy, power_used_w=power,
                homes_fully_mandatory=sum(r["mandatory_met"] for r in per_home),
                fairness_index=jain_index([r["service_ratio"] for r in per_home]),
                gain_vs_equal_split=utility - baseline["utility"],
                mip_gap=getattr(result, "mip_gap", None), home_results=per_home, message=None)


def home_knapsack(apps, energy_wh, power_w):
    """Exact single-home optimum by MILP; None when mandatory loads cannot fit."""
    n = len(apps)
    result = milp(-np.array([a.utility for a in apps]), integrality=np.ones(n),
                  bounds=Bounds([1.0 if a.mandatory else 0.0 for a in apps], np.ones(n)),
                  constraints=LinearConstraint(np.array([[a.energy_wh for a in apps], [a.power_w for a in apps]]),
                                               [-np.inf, -np.inf], [energy_wh, power_w]))
    return None if result.x is None else float(sum(a.utility for a, v in zip(apps, np.round(result.x)) if v))


def equal_split(homes, battery_wh, inverter_w, outage_h):
    """Baseline: each home gets 1/N of the battery and inverter and optimizes alone (exact)."""
    share_e, share_p = battery_wh / len(homes), inverter_w / len(homes)
    utilities, ratios, mandatory_ok = [], [], 0
    for home in homes:
        apps = home["appliances"]
        if len(apps) <= 10:
            best = solve_exact(Scenario(home["name"], tuple(apps), share_e, share_p, outage_h))["best"]
            u = best["utility"] if best else None
        else:
            u = home_knapsack(apps, share_e, share_p)
        total = sum(a.utility for a in apps)
        utilities.append(u or 0.0)
        ratios.append((u or 0.0) / total if total else 1.0)
        mandatory_ok += u is not None
    return dict(method="Equal split: each home gets 1/N of capacity, solved exactly", utility=sum(utilities),
                home_utilities=utilities, homes_with_mandatory_met=mandatory_ok,
                fairness_index=jain_index(ratios))
