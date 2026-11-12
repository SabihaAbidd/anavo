"""Real Qiskit circuits: noiseless Aer expectations, then Aer shot measurement."""
from time import perf_counter
import numpy as np
from scipy.optimize import minimize
from .models import evaluate
from .optimization import build_qubo, decode_counts_key


def hamiltonian_scale(fields,pairs):
    largest=max(float(np.max(np.abs(fields))),float(np.max(np.abs(pairs))))
    return largest if largest>0 else 1.0


def build_qaoa_circuit(qubo, depth=2):
    if type(depth) is not int or not 1 <= depth <= 4:
        raise ValueError("QAOA depth must be between 1 and 4")
    from qiskit import QuantumCircuit
    from qiskit.circuit import ParameterVector
    offset, fields, pairs = qubo.ising()
    scale = hamiltonian_scale(fields,pairs)
    params = ParameterVector("theta", 2*depth)
    circuit = QuantumCircuit(qubo.n_qubits)
    circuit.h(range(qubo.n_qubits))
    for layer in range(depth):
        gamma, beta = params[2*layer], params[2*layer+1]
        for i, value in enumerate(fields):
            if value != 0:
                circuit.rz(2*gamma*float(value)/scale, i)
        for i in range(qubo.n_qubits):
            for j in range(i+1, qubo.n_qubits):
                if pairs[i, j] != 0:
                    circuit.rzz(2*gamma*float(pairs[i, j])/scale, i, j)
        circuit.rx(2*beta, range(qubo.n_qubits))
    return circuit, params, scale, offset


def solve_quantum(scenario, depth=2, shots=2048, maxiter=80, seed=42, restarts=2, max_qubits=14):
    start = perf_counter()
    for name, value, lower, upper in (("shots", shots, 1, 100000),
         ("maxiter", maxiter, 10, 1000), ("restarts", restarts, 1, 5),
         ("depth", depth, 1, 4), ("seed", seed, 0, 2**31-1)):
        if type(value) is not int or not lower <= value <= upper:
            raise ValueError(f"{name} must be an integer between {lower} and {upper}")
    qubo = build_qubo(scenario, max_qubits=max_qubits)
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    backend = AerSimulator(method="statevector", max_parallel_threads=1, seed_simulator=seed)
    circuit, params, scale, offset = build_qaoa_circuit(qubo, depth)
    state_circuit = circuit.copy()
    state_circuit.save_statevector()
    compiled = transpile(state_circuit, backend, seed_transpiler=seed, optimization_level=1)
    energies = qubo.basis_energies()
    normalized_energies = (energies-offset)/scale
    history = []
    optimizer_runs = []

    def expectation(theta):
        bound = compiled.assign_parameters(dict(zip(params, theta)))
        state = backend.run(bound).result().get_statevector()
        value = float(np.dot(np.abs(np.asarray(state))**2, normalized_energies))
        history.append(value*scale+offset)
        return value

    rng = np.random.default_rng(seed)
    best_run = None
    for _ in range(restarts):
        initial = rng.uniform(0, np.pi, 2*depth)
        result = minimize(expectation, initial, method="COBYLA", options={"maxiter":maxiter, "tol":1e-5})
        optimizer_runs.append(dict(nfev=int(result.nfev), success=bool(result.success),
                                   message=str(result.message), objective=float(result.fun)))
        if best_run is None or result.fun < best_run.fun:
            best_run = result
    measured = circuit.assign_parameters(dict(zip(params, best_run.x)))
    measured.measure_all()
    compiled_measurement = transpile(measured, backend, seed_transpiler=seed, optimization_level=1)
    counts = backend.run(compiled_measurement, shots=shots, seed_simulator=seed).result().get_counts()
    best = None
    selection_feasible = 0
    encoding_feasible = 0
    distribution = []
    for key, count in sorted(counts.items()):
        bits = decode_counts_key(key, qubo.n_qubits)
        candidate = evaluate(scenario, bits[:qubo.n_appliances])
        full_feasible = candidate["feasible"] and qubo.encoding_feasible(bits)
        selection_feasible += count*int(candidate["feasible"])
        encoding_feasible += count*int(full_feasible)
        distribution.append(dict(measured_bitstring=key, appliance_bitstring=candidate["bitstring"],
                                 count=int(count), feasible=candidate["feasible"],
                                 encoding_feasible=bool(full_feasible), utility=candidate["utility"],
                                 qubo_energy=qubo.energy(bits)))
        if candidate["feasible"] and (best is None or (-candidate["utility"], candidate["selection"]) < (-best["utility"], best["selection"])):
            best = candidate
    return dict(method="QAOA / Qiskit Aer noiseless simulator", status="sampled" if best else "no feasible sample",
                best=best, runtime_s=perf_counter()-start, qubits=qubo.n_qubits,
                appliance_qubits=qubo.n_appliances, slack_qubits=qubo.n_qubits-qubo.n_appliances,
                qaoa_depth=depth, circuit_depth=compiled_measurement.depth(), shots=shots, seed=seed,
                optimizer="COBYLA", max_evaluations_per_restart=maxiter, restarts=restarts,
                optimizer_evaluations=sum(r["nfev"] for r in optimizer_runs), optimizer_runs=optimizer_runs,
                optimizer_iterations=None, iteration_note="SciPy COBYLA reports nfev, not a separate iteration count",
                parameters=best_run.x.tolist(), penalty=qubo.penalty, hamiltonian_scale=scale,
                expected_qubo_energy=float(best_run.fun*scale+offset), objective_history=history,
                feasible_selection_probability=selection_feasible/shots,
                feasible_encoding_probability=encoding_feasible/shots,
                counts={k:int(v) for k,v in counts.items()}, distribution=distribution)
