"""Independent exact baseline, without QUBO or quantum dependencies."""
from itertools import product
from time import perf_counter
from .models import evaluate


def solve_exact(scenario):
    start = perf_counter()
    best = None
    feasible_count = 0
    for bits in product((0, 1), repeat=len(scenario.appliances)):
        candidate = evaluate(scenario, bits)
        if candidate["feasible"]:
            feasible_count += 1
            # Enumeration order resolves utility ties lexicographically.
            if best is None or candidate["utility"] > best["utility"]:
                best = candidate
    return dict(method="exact enumeration", status="optimal" if best else "infeasible",
                best=best, feasible_selections=feasible_count,
                enumerated=2**len(scenario.appliances), runtime_s=perf_counter()-start)
