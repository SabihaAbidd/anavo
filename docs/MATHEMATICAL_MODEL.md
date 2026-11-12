# Mathematical model and derivation

## Physical problem

For appliance i, P_i is watts, t_i is requested hours, E_i=P_i*t_i is watt-hours, u_i >= 0 is stated utility, and x_i is a binary selection. Durations lie within the outage T. All selected loads reserve simultaneous inverter capacity; there is no start-time schedule.

Maximize U(x)=sum_i u_i*x_i subject to:

- sum_i E_i*x_i <= B, the usable AC-side battery energy in Wh.
- sum_i P_i*x_i <= W, the inverter rating in W.
- x_i=1 for every mandatory appliance i.

Essential labels count critical services served, but add no implicit objective weight. Users express preferences through u_i. Mandatory infeasibility is reported; no automatic relaxation occurs. Zero battery allows zero-energy operations but rejects positive-energy loads. These are selection decisions for fixed operations, not durations chosen by the optimizer.

## Exact decimal normalization

Interpret the shortest decimal representation of each validated input as a rational. For energy, multiply rational P_i by rational t_i, avoiding float-product rounding. Multiply the resource weights by their denominators' LCM D, then divide by the integer weights' GCD g. This yields integer weights a_i. Set integer capacity C=floor(B*D/g). Flooring is exact because the left side is integer; it does not discretize or approximate a feasible fractional load. Zero weights use g=1. If C >= sum a_i, the constraint is redundant and omitted.

## Bounded binary slack

Represent slack s in 0..C with weights 1, 2, 4, ..., and a final remainder when needed. For C=8, weights are [1,2,4,1]; the sums cover every integer 0..8 (some encodings are degenerate), and cannot exceed 8. C=0 requires no slack bits. Write resource equality sum a_i*x_i + sum w_k*y_k - C = 0. Maintain distinct slack registers for energy and power; no device decision is dropped.

## QUBO

Let z contain appliance decisions followed by resource slack bits. Define A=1+sum u_i and minimize:

F(z) = -sum u_i*x_i + A*sum_r (c_r dot z - C_r)^2 + A*sum_mandatory (1-x_i).

The final term equals A*(1-x_i)^2 for binary x_i. Every infeasible constraint produces an integer residual of magnitude at least one. Therefore any constraint-violating full state has F >= A-sum u_i > 0. Every feasible state with valid slack has F=-U <= 0. Thus if a feasible physical allocation exists, all global QUBO minima are feasible and maximize U. If none exists, the QUBO still has a ground state, but it is not a valid recommendation: physical feasibility is always checked independently.

For one row c dot z-C, expansion uses z_i^2=z_i:

- Constant: A*C^2.
- Linear coefficient: A*(c_i^2-2*C*c_i).
- Upper-triangle pair coefficient i<j: 2*A*c_i*c_j.
- Add -u_i for appliance variables and mandatory constant A / linear -A.

The implementation stores each quadratic pair once, not a symmetric matrix counted twice. Explicit qubit and coefficient guards reject impractical encodings rather than rounding inputs.

Double-precision storage introduces another limit. A reproduced instance with utilities 1e-20 and 2e-20 and unit penalties lost its objective coefficients, creating false ties between 00, 01 and 10 although the exact optimum was 01. The converter now derives the exact utility lattice from rational decimal utilities and compares its spacing with a conservative coefficient-roundoff bound. An unsafe encoding raises QuantumLimitError instead of silently changing preferences. Normal decimal and integer presets retain their verified optima; the exact classical solver remains available for rejected quantum encodings. This is a conservative numerical guard, not arbitrary objective rounding.

## Ising transformation

For F(z)=c+sum l_i*z_i+sum_(i<j) q_ij*z_i*z_j, substitute z_i=(1-Z_i)/2.

H_C = c' I + sum h_i*Z_i + sum_(i<j) J_ij*Z_i*Z_j,

where J_ij=q_ij/4, h_i=-l_i/2-sum_(j!=i) q_min(i,j),max(i,j)/4, and c'=c+sum l_i/2+sum q_ij/4. The basis state with bit z_i has Pauli eigenvalue 1-2*z_i. Tests compare every computational-basis energy with the QUBO, including the constant offset.

## QAOA circuit and classical loop

Initialize H on every qubit. For each layer apply RZ_i(2*gamma*h_i/S), RZZ_ij(2*gamma*J_ij/S), then RX_i(2*beta), where S=max(max|h|,max|J|), using S=1 only for an identically zero Hamiltonian. This implements exp(-i*gamma*(H_C-c'I)/S), then exp(-i*beta*sum X). The constant creates only a global phase and is omitted from gates. Positive rescaling changes angles, not ground states. Nonzero terms are retained rather than discarded by an absolute 1e-12 cutoff; scaling a small unconstrained cost keeps it meaningful in the circuit.

SciPy COBYLA minimizes the exact noiseless Aer expectation of (F-c')/S using seeded initial angles, with two restarts. A separate measured Aer circuit supplies reported shot counts. This is simulator-based hybrid optimization; circuit expectations are not noisy hardware estimates. NFEV is recorded; a separate iteration count is null because the chosen SciPy result does not expose it.

Qiskit count strings display highest qubit first. Reverse them to decode logical variables, then take appliance bits. Compare the best physically feasible measured selection with the independent exact optimum. Auxiliary-register feasibility is also reported separately; physically feasible decisions can appear alongside incorrect slack. There is no repair, no optimum injection, and no renormalization of feasible-shot probability.

Full-encoding feasibility uses integer row residuals and mandatory bits directly. It does not subtract utility from a large floating-point QUBO energy and compare against a tolerance. Physical feasibility still comes from the independent appliance model. This separates hard-constraint truth from numerical cost reporting.

## Worked evening example

| Appliance | Power W | Hours | Energy Wh | Utility | Mandatory |
|---|---:|---:|---:|---:|---|
| Fan | 40 | 3 | 120 | 9 | No |
| LED lights | 10 | 3 | 30 | 7 | No |
| Router | 10 | 3 | 30 | 8 | Yes |
| Laptop | 60 | 2 | 120 | 6 | No |

B=240 Wh, W=100 W, T=3 h. Energy row: [4,1,1,4], C=8. Power row: [4,1,1,6], C=10. Each row needs four bounded slack bits, totaling 12 qubits (four device, eight auxiliary). A=31. The exact physical optimum x=[1,1,1,0] has utility 24, energy 180 Wh, and power 60 W. Valid slack is energy 2 and power 4; its QUBO value is -24. Exhaustive enumeration verifies the QUBO minimum and independent baseline agree. This mathematical result does not establish that a finite-depth QAOA run will measure that optimum.
