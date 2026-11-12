"""Framework-independent use cases; no FastAPI imports or solver rewrites."""
import logging
from src.classical_solver import solve_exact
from src.evaluation import environment_versions
from src.models import evaluate
from src.optimization import QuantumLimitError
from src.quantum_solver import solve_quantum
from .schemas import (Allocation, ApplianceDecision, CompareRequest, CompareResponse,
                      OptimizeRequest, OptimizeResponse, QuantumMetadata, SolverResult)

logger = logging.getLogger(__name__)


def allocation(scenario, best):
    if best is None:
        return None
    # Do not trust an upstream candidate's cached feasibility or resource values.
    checked = evaluate(scenario, best["selection"])
    if not checked["feasible"]:
        raise ValueError("Solver returned an infeasible recommendation")
    decisions = [ApplianceDecision(**vars(a), selected=bool(bit), energy_wh=a.energy_wh)
                 for a, bit in zip(scenario.appliances, checked["selection"])]
    return Allocation(feasible=True, objective_value=checked["utility"],
        bitstring=checked["bitstring"], selection=checked["selection"],
        selected_appliances=[a for a in decisions if a.selected],
        deferred_appliances=[a for a in decisions if not a.selected],
        energy_used_wh=checked["energy_wh"], energy_remaining_wh=checked["remaining_wh"],
        power_used_w=checked["power_w"], inverter_remaining_w=scenario.inverter_w-checked["power_w"],
        energy_utilization=checked["energy_wh"]/scenario.battery_wh if scenario.battery_wh else 0.0,
        essential_served=checked["essential_served"], essential_total=checked["essential_total"],
        violations=checked["violations"])


def classical_result(scenario):
    raw = solve_exact(scenario)
    return SolverResult(algorithm="classical", method=raw["method"], status=raw["status"],
        feasibility="feasible" if raw["best"] is not None else "infeasible",
        allocation=allocation(scenario, raw["best"]), runtime_s=raw["runtime_s"],
        enumerated=raw["enumerated"], feasible_selections=raw["feasible_selections"],
        message="No allocation satisfies every hard constraint; mandatory requirements were not relaxed."
                if raw["best"] is None else None)


def quantum_result(scenario, options):
    method = "QAOA / Qiskit Aer noiseless simulator"
    try:
        raw = solve_quantum(scenario, **options.model_dump())
        metadata = {key: raw[key] for key in QuantumMetadata.model_fields}
        return SolverResult(algorithm="quantum", method=raw["method"],
            feasibility="feasible" if raw["best"] is not None else "unknown",
            status=raw["status"].replace(" ", "_"), allocation=allocation(scenario, raw["best"]),
            runtime_s=raw["runtime_s"], quantum_metadata=QuantumMetadata(**metadata),
            message="No feasible selection was measured; this alone does not prove physical infeasibility."
                    if raw["best"] is None else None)
    except QuantumLimitError as exc:
        return SolverResult(algorithm="quantum", method=method, status="oversized",
            error_code="quantum_resource_limit", message=str(exc))
    except ImportError:
        return SolverResult(algorithm="quantum", method=method, status="unavailable",
            error_code="quantum_dependency_unavailable",
            message="Qiskit/Aer could not be imported. Install requirements.txt and run actual quantum validation.")
    except Exception:
        logger.exception("Quantum execution failed")
        return SolverResult(algorithm="quantum", method=method, status="failed",
            error_code="quantum_execution_failed", message="Quantum execution failed; consult backend logs. No quantum recommendation is available.")


def optimize(request: OptimizeRequest) -> OptimizeResponse:
    scenario = request.scenario.to_domain()
    result = classical_result(scenario) if request.algorithm == "classical" else quantum_result(scenario, request.quantum_options)
    return OptimizeResponse(scenario=request.scenario, result=result, environment=environment_versions())


def compare(request: CompareRequest) -> CompareResponse:
    scenario = request.scenario.to_domain()
    classical = classical_result(scenario)
    quantum = quantum_result(scenario, request.quantum_options)
    gap = relative = optimum_probability = None
    if classical.allocation is not None and quantum.quantum_metadata is not None:
        # Share of all shots that measured the exact optimum's appliance decision.
        optimum_probability = sum(item.probability for item in quantum.quantum_metadata.selection_distribution
                                  if item.appliance_bitstring == classical.allocation.bitstring)
    if classical.allocation is not None and quantum.allocation is not None:
        gap = classical.allocation.objective_value - quantum.allocation.objective_value
        relative = gap/classical.allocation.objective_value if classical.allocation.objective_value else 0.0
        status = "complete"
    else:
        status = {"unavailable":"quantum_unavailable", "oversized":"quantum_oversized",
                  "failed":"quantum_failed"}.get(quantum.status, "no_feasible_pair")
    return CompareResponse(scenario=request.scenario, classical=classical, quantum=quantum,
        comparison_status=status, objective_gap=gap, relative_gap=relative,
        optimal_selection_probability=optimum_probability,
        environment=environment_versions(),
        bit_order="Allocation bitstrings use input order x0..xn-1; measured strings use Qiskit q[n-1]..q[0].",
        interpretation="Ideal simulated quantum execution only when metadata/counts are present. No quantum advantage is claimed.")


def schedule(request):
    from src.scheduler import solve_schedule
    from .schemas import ScheduleResponse
    scenario = request.scenario.to_domain()
    raw = solve_schedule(scenario, start_hour=request.start_hour, solar_kwp=request.solar_kwp,
                         peak_sun_hours=request.peak_sun_hours)
    simultaneous = solve_exact(scenario)["best"]
    simultaneous_utility = simultaneous["utility"] if simultaneous else None
    gain = None
    if raw["feasible"] and simultaneous_utility is not None:
        gain = raw["utility"] - simultaneous_utility
    return ScheduleResponse(**raw, simultaneous_utility=simultaneous_utility, gain_vs_simultaneous=gain)


def fleet(request):
    from src.fleet import solve_fleet
    from src.models import Appliance
    from .schemas import FleetResponse
    homes = [dict(name=h.name, weight=h.weight,
                  appliances=[Appliance(**a.model_dump()) for a in h.appliances]) for h in request.homes]
    raw = solve_fleet(homes, request.battery_wh, request.inverter_w, request.outage_h,
                      fairness_floor=request.fairness_floor)
    return FleetResponse(name=request.name, **raw)


def pakistan_dataset():
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parent.parent / "data" / "pakistan_energy.json"
    return json.loads(path.read_text(encoding="utf-8"))
