"""Consistency checks for recorded evidence; never a substitute for real execution."""
import math
from pathlib import Path
import json
from src.models import Appliance,Scenario,evaluate
from src.classical_solver import solve_exact
from src.optimization import build_qubo,decode_counts_key

REQUIRED_SCENARIOS={"Ample backup","Limited battery","Mandatory infeasible"}
REQUIRED_HTTP_CHECKS={"health","scenarios","algorithm_info","classical_optimize",
    "quantum_optimize","compare","mandatory_infeasible","invalid_request","quantum_limit",
    "zero_budget","cors_allowed","cors_rejected"}


def load_record(path):
    try:
        data=json.loads(Path(path).read_text(encoding="utf-8-sig"))
        if not isinstance(data,dict): raise ValueError("Top-level record must be an object")
        return data,None
    except (OSError,ValueError) as exc:
        return None,f"Cannot read {path}: {exc}"


def check_http_evidence(data,fingerprint):
    issues=[]
    if data.get("source_fingerprint") != fingerprint: issues.append("HTTP evidence is missing or stale for current runtime source")
    if data.get("healthy") is not True: issues.append("Real FastAPI HTTP checks are not complete")
    checks=data.get("checks",[])
    if not isinstance(checks,list): return issues+["HTTP check records must be a list"]
    names=[c.get("name") for c in checks if isinstance(c,dict)]
    if not REQUIRED_HTTP_CHECKS.issubset(names): issues.append("HTTP evidence does not cover every required endpoint/negative/CORS case")
    if len(names)!=len(set(names)): issues.append("HTTP evidence contains duplicate check names")
    if any(not isinstance(c,dict) or c.get("passed") is not True for c in checks):
        issues.append("At least one real HTTP check did not pass")
    return issues


def close(a,b):
    return type(a) in (int,float) and math.isfinite(a) and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-10)


def check_benchmark_evidence(data,fingerprint):
    issues=[]
    if data.get("source_fingerprint") != fingerprint: issues.append("Benchmark evidence is missing or stale for current runtime source")
    if data.get("complete_quantum_execution") is not True: issues.append("Benchmark quantum execution is incomplete")
    records=data.get("results",[])
    if not isinstance(records,list): return issues+["Benchmark results must be a list"]
    names=[r.get("scenario",{}).get("name") for r in records if isinstance(r,dict) and isinstance(r.get("scenario"),dict)]
    if set(names)!=REQUIRED_SCENARIOS or len(names)!=3:
        issues.append("Benchmarks must contain exactly the feasible, constrained and mandatory-infeasible scenarios")
    comparable=False
    for record in records:
        try:
            scenario_data=dict(record["scenario"])
            scenario_data["appliances"]=tuple(Appliance(**a) for a in scenario_data["appliances"])
            scenario=Scenario(**scenario_data)
            q=record["quantum"]
            if q.get("status") not in ("sampled","no feasible sample"):
                raise ValueError("actual measured quantum outcome is unavailable")
            model=build_qubo(scenario)
            if q["qubits"]!=model.n_qubits: raise ValueError("qubit count differs from the actual encoding")
            counts=q["counts"]
            shots=q["shots"]
            if type(shots) is not int or shots<=0 or not isinstance(counts,dict) or not counts:
                raise ValueError("missing positive shots/count distribution")
            if any(type(count) is not int or count<=0 for count in counts.values()) or sum(counts.values())!=shots:
                raise ValueError("counts must be positive integers summing to shots")
            if type(q["seed"]) is not int or not 0<=q["seed"]<=2**31-1:
                raise ValueError("invalid reproducibility seed")
            if type(q["qaoa_depth"]) is not int or not 1<=q["qaoa_depth"]<=4:
                raise ValueError("invalid QAOA layer count")
            if type(q["circuit_depth"]) is not int or q["circuit_depth"]<=0:
                raise ValueError("missing circuit depth")
            if q["optimizer"]!="COBYLA" or not q["optimizer_runs"] or q["optimizer_evaluations"]<=0:
                raise ValueError("missing optimizer execution metadata")
            if len(q["parameters"])!=2*q["qaoa_depth"] or not all(close(v,v) for v in q["parameters"]):
                raise ValueError("invalid optimized parameters")
            if not close(q["runtime_s"],q["runtime_s"]) or q["runtime_s"]<0:
                raise ValueError("invalid quantum runtime")
            if not all(record["environment"].get(p) for p in ("qiskit","qiskit-aer")):
                raise ValueError("missing actual Qiskit/Aer package versions")
            best=None
            physical=encoded=0
            for key,count in counts.items():
                bits=decode_counts_key(key,model.n_qubits)
                candidate=evaluate(scenario,bits[:model.n_appliances])
                physical+=count*int(candidate["feasible"])
                encoded+=count*int(candidate["feasible"] and model.encoding_feasible(bits))
                if candidate["feasible"] and (best is None or (-candidate["utility"],candidate["selection"])<(-best["utility"],best["selection"])):
                    best=candidate
            if not close(q["feasible_selection_probability"],physical/shots) or not close(q["feasible_encoding_probability"],encoded/shots):
                raise ValueError("feasibility probabilities disagree with decoded measured counts")
            reported=q.get("best")
            if (reported is None)!=(best is None): raise ValueError("reported quantum selection differs from observed candidates")
            if best is not None and (reported["selection"]!=best["selection"] or not close(reported["utility"],best["utility"])):
                raise ValueError("reported best is not the best feasible measured selection")
            exact=solve_exact(scenario)
            recorded_classical=record["classical"]
            if recorded_classical.get("status")!=exact["status"] or recorded_classical.get("best")!=exact["best"]:
                raise ValueError("recorded classical allocation differs from independent exact enumeration")
            if exact["best"] is not None and best is not None:
                comparable=True
                gap=exact["best"]["utility"]-best["utility"]
                relative=gap/exact["best"]["utility"] if exact["best"]["utility"] else 0.0
                if not close(record["objective_gap"],gap) or not close(record["relative_gap"],relative):
                    raise ValueError("recorded objective gap is inconsistent")
            elif record.get("objective_gap") is not None or record.get("relative_gap") is not None:
                raise ValueError("gap must be null when no feasible comparison exists")
        except (KeyError,TypeError,ValueError,OverflowError) as exc:
            issues.append(f"Invalid benchmark evidence: {exc}")
    if not comparable: issues.append("No measured feasible quantum/classical comparison exists")
    return issues
