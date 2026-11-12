"""Exact integer inequality encoding and explicit QUBO / Ising mapping."""
from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from math import gcd, lcm, floor
import numpy as np


class QuantumLimitError(ValueError):
    pass


def integer_constraint(weights, capacity):
    """Preserve decimal inputs exactly; residuals have integer spacing >= 1."""
    weights = [Fraction(str(w)) if not isinstance(w, Fraction) else w for w in weights]
    denominator = lcm(*(w.denominator for w in weights))
    integer_weights = [int(w * denominator) for w in weights]
    divisor = reduce(gcd, integer_weights, 0) or 1
    normalized = [w // divisor for w in integer_weights]
    bound = floor(Fraction(str(capacity)) * denominator / divisor)
    return normalized, bound


def slack_weights(bound):
    """Bounded binary encoding: all integer sums 0..bound, never above bound."""
    result = []
    remainder = bound
    weight = 1
    while remainder:
        take = min(weight, remainder)
        result.append(take)
        remainder -= take
        weight *= 2
    return result


@dataclass
class Qubo:
    linear: np.ndarray
    quadratic: np.ndarray  # upper triangle, each pair counted exactly once
    constant: float
    n_appliances: int
    penalty: float
    constraints: list
    variable_names: list
    mandatory_indices: tuple = ()

    @property
    def n_qubits(self):
        return len(self.linear)

    def energy(self, bits):
        x = np.asarray(bits, dtype=float)
        if x.shape != self.linear.shape or not np.all((x == 0) | (x == 1)):
            raise ValueError("QUBO state must have one binary bit per variable")
        return float(self.constant + self.linear @ x + x @ self.quadratic @ x)

    def ising(self):
        # x_i=(1-z_i)/2; x_i*x_j=(1-z_i-z_j+z_i*z_j)/4.
        pairs = self.quadratic / 4
        fields = -self.linear / 2 - pairs.sum(axis=0) - pairs.sum(axis=1)
        offset = self.constant + self.linear.sum()/2 + pairs.sum()
        return float(offset), fields, pairs

    def encoding_feasible(self, bits):
        """Check zero hard-constraint residuals without subtracting large float energies."""
        if len(bits) != self.n_qubits or any(bit not in (0, 1) for bit in bits):
            raise ValueError("Encoding state must have one binary bit per variable")
        if any(not bits[i] for i in self.mandatory_indices):
            return False
        for row in self.constraints:
            used = sum(weight*int(bits[i]) for i, weight in enumerate(row["weights"]))
            slack = sum(weight*int(bits[row["slack_start"]+i]) for i, weight in enumerate(row["slack"]))
            if used+slack != row["bound"]:
                return False
        return True

    def basis_energies(self):
        indexes = np.arange(2**self.n_qubits, dtype=np.uint64)
        bits = ((indexes[:, None] >> np.arange(self.n_qubits, dtype=np.uint64)) & 1).astype(float)
        return self.constant + bits @ self.linear + np.sum((bits @ self.quadratic) * bits, axis=1)


def build_qubo(scenario, max_qubits=14):
    if type(max_qubits) is not int or not 1 <= max_qubits <= 14:
        raise ValueError("max_qubits must be an integer between 1 and 14")
    n = len(scenario.appliances)
    rows = []
    energy = [Fraction(str(a.power_w))*Fraction(str(a.duration_h)) for a in scenario.appliances]
    for name, weights, capacity in (("energy", energy, scenario.battery_wh),
                                    ("power", [a.power_w for a in scenario.appliances], scenario.inverter_w)):
        normalized, bound = integer_constraint(weights, capacity)
        if bound >= sum(normalized):
            continue
        # Integer coefficients may grow for fine decimal input. Fail before allocation.
        if max(normalized + [bound], default=0) > 1_000_000:
            raise QuantumLimitError("Input precision makes the quantum encoding too large; use simpler decimal loads")
        rows.append(dict(name=name, weights=normalized, bound=bound, slack=slack_weights(bound)))
    total = n + sum(len(row["slack"]) for row in rows)
    if total > max_qubits:
        raise QuantumLimitError(f"This exact encoding needs {total} qubits; local demo limit is {max_qubits}. Reduce loads or simplify capacities.")
    penalty = 1.0 + sum(a.utility for a in scenario.appliances)
    linear = np.zeros(total)
    linear[:n] = [-a.utility for a in scenario.appliances]
    quadratic = np.zeros((total, total))
    constant = 0.0
    names = [a.name for a in scenario.appliances]
    cursor = n
    for row in rows:
        coeff = np.zeros(total)
        coeff[:n] = row["weights"]
        coeff[cursor:cursor+len(row["slack"])] = row["slack"]
        row["slack_start"] = cursor
        names.extend(f"{row['name']}_slack_{k}" for k in range(len(row["slack"])))
        cursor += len(row["slack"])
        bound = row["bound"]
        constant += penalty * bound**2
        linear += penalty * (coeff**2 - 2*bound*coeff)
        quadratic += 2*penalty * np.triu(np.outer(coeff, coeff), 1)
    for i, a in enumerate(scenario.appliances):
        if a.mandatory:
            constant += penalty
            linear[i] -= penalty  # A(1-x_i)^2 = A(1-x_i)
    if not np.isfinite(constant) or not np.all(np.isfinite(linear)) or not np.all(np.isfinite(quadratic)):
        raise QuantumLimitError("Utility or resource coefficients exceed safe numerical range")
    # Decimal utilities define an exact lattice of possible objective differences.
    # If its spacing is lost in double-precision coefficient expansion, reject the
    # quantum encoding; do not silently change priorities or claim a valid QUBO.
    utilities = [Fraction(str(a.utility)) for a in scenario.appliances]
    denominator = lcm(*(u.denominator for u in utilities))
    divisor = reduce(gcd, (int(u*denominator) for u in utilities), 0)
    spacing = min(Fraction(1), Fraction(divisor, denominator)) if divisor else Fraction(1)
    magnitude = abs(constant) + np.abs(linear).sum() + np.abs(quadratic).sum()
    roundoff_bound = (2*total**2+8*total+16)*np.finfo(float).eps*magnitude
    if not np.isfinite(roundoff_bound) or roundoff_bound >= float(spacing)/8:
        raise QuantumLimitError("Utility precision is too fine relative to QUBO penalty coefficients for reliable floating-point encoding; use simpler priority scores")
    return Qubo(linear, quadratic, constant, n, penalty, rows, names,
                tuple(i for i, a in enumerate(scenario.appliances) if a.mandatory))


def decode_counts_key(key, n_qubits):
    key = key.replace(" ", "")
    if len(key) != n_qubits or any(c not in "01" for c in key):
        raise ValueError("Invalid measured bitstring")
    # Qiskit displays q[n-1]..q[0]; physical variable i lives on qubit i.
    return tuple(int(c) for c in key[::-1])
