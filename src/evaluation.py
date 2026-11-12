"""Comparable results without silently substituting an exact solution for QAOA."""
from dataclasses import asdict
import platform
from importlib.metadata import version, PackageNotFoundError
from .classical_solver import solve_exact
from .quantum_solver import solve_quantum
from .optimization import QuantumLimitError


def environment_versions():
    result = {"python": platform.python_version()}
    for package in ("qiskit", "qiskit-aer", "numpy", "scipy", "streamlit", "fastapi", "pydantic", "uvicorn", "httpx"):
        try:
            result[package] = version(package)
        except PackageNotFoundError:
            result[package] = None
    return result


def compare(scenario, **quantum_options):
    exact = solve_exact(scenario)
    try:
        quantum = solve_quantum(scenario, **quantum_options)
    except (ImportError, QuantumLimitError) as exc:
        quantum = dict(status="unavailable", best=None, reason=str(exc))
    gap = None
    relative_gap = None
    if exact["best"] is not None and quantum["best"] is not None:
        gap = exact["best"]["utility"] - quantum["best"]["utility"]
        relative_gap = gap/exact["best"]["utility"] if exact["best"]["utility"] else 0.0
    return dict(scenario=asdict(scenario), classical=exact, quantum=quantum,
                objective_gap=gap, relative_gap=relative_gap,
                environment=environment_versions(),
                bit_order="Appliance strings use input order x0..xn-1; measured strings use Qiskit q[n-1]..q[0]",
                interpretation="Noiseless simulator demonstration; no quantum speedup or hardware claim.")
