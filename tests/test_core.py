import importlib.util
import itertools
import unittest
import numpy as np
from src.models import Appliance, Scenario, evaluate
from src.classical_solver import solve_exact
from src.scenarios import presets
from src.optimization import build_qubo, decode_counts_key, integer_constraint, slack_weights, QuantumLimitError


class ModelTests(unittest.TestCase):
    def test_energy_units_and_boundary(self):
        a = Appliance("Fan", 40, 3, 9)
        self.assertEqual(a.energy_wh, 120)
        self.assertTrue(evaluate(Scenario("s", (a,), 120, 40, 3), (1,))["feasible"])

    def test_reject_invalid_appliance(self):
        for field, value in [("power_w", -1), ("utility", float("nan")),
             ("duration_h", float("inf")), ("power_w", True), ("utility", "9"),
             ("name", "  "), ("mandatory", "False")]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                values = dict(name="a", power_w=1, duration_h=1, utility=1)
                values[field] = value
                Appliance(**values)

    def test_reject_invalid_scenario(self):
        a = Appliance("a", 1, 2, 1)
        for loads, battery, inverter, outage in [((a,), 1, 1, 1), ((a,a), 1, 1, 2),
             ((a,), -1, 1, 2), ((a,), 1, float("nan"), 2), ((), 1, 1, 2), ((a,),1,1,0)]:
            with self.subTest(loads=loads), self.assertRaises(ValueError):
                Scenario("s", loads, battery, inverter, outage)

    def test_constraints_and_mandatory(self):
        s = Scenario("s", (Appliance("a", 10, 2, 5, True, True),), 19, 9, 2)
        self.assertEqual(len(evaluate(s, (1,))["violations"]), 2)
        self.assertEqual(evaluate(s, (0,))["violations"], ["mandatory load omitted"])

    def test_selection_validation(self):
        s = presets()["Evening backup"]
        for bits in [(1,), (0,0,0,2)]:
            with self.assertRaises(ValueError):
                evaluate(s, bits)

    def test_decimal_boundary(self):
        s = Scenario("decimal", (Appliance("a", .1, 1, 1), Appliance("b", .2, 1, 1)), .3, .3, 1)
        self.assertTrue(evaluate(s, (1,1))["feasible"])


class ClassicalTests(unittest.TestCase):
    def test_known_optimum(self):
        r = solve_exact(presets()["Evening backup"])
        self.assertEqual(r["best"]["selection"], [1,1,1,0])
        self.assertEqual(r["best"]["utility"], 24)
        self.assertEqual(r["best"]["energy_wh"], 180)

    def test_zero_energy_optional_essential(self):
        s = Scenario("s", (Appliance("a",1,1,5,True),),0,10,1)
        self.assertEqual(solve_exact(s)["best"]["selection"], [0])

    def test_infeasible(self):
        self.assertIsNone(solve_exact(presets()["Mandatory infeasible"])["best"])

    def test_tie_and_power(self):
        s = Scenario("s", (Appliance("a",1,1,1),Appliance("b",1,1,1)),2,1,1)
        r = solve_exact(s)
        self.assertEqual(r["best"]["selection"], [0,1])
        self.assertEqual(r["feasible_selections"], 3)

    def test_zero_utility(self):
        s = Scenario("s", (Appliance("a",0,0,0),),0,0,1)
        self.assertEqual(solve_exact(s)["best"]["selection"], [0])


class QuboTests(unittest.TestCase):
    def test_integer_normalization_no_rounding(self):
        self.assertEqual(integer_constraint([.1,.2], .29), ([1,2],2))

    def test_bounded_slack_coverage(self):
        for bound in range(20):
            weights = slack_weights(bound)
            sums = {sum(w*x for w,x in zip(weights,bits)) for bits in itertools.product((0,1),repeat=len(weights))}
            self.assertEqual(sums, set(range(bound+1)))

    def test_qubo_ground_states(self):
        for name, s in presets().items():
            q = build_qubo(s)
            energies = q.basis_energies()
            minimum = float(energies.min())
            exact = solve_exact(s)["best"]
            if exact is not None:
                self.assertAlmostEqual(minimum, -exact["utility"])
                for index in np.flatnonzero(np.isclose(energies,minimum)):
                    bits = [(int(index)>>i)&1 for i in range(len(s.appliances))]
                    candidate = evaluate(s,bits)
                    self.assertTrue(candidate["feasible"], name)
                    self.assertEqual(candidate["utility"], exact["utility"])
            else:
                self.assertTrue(all(not evaluate(s,b)["feasible"] for b in itertools.product((0,1),repeat=len(s.appliances))))

    def test_all_ising_and_qubo_energies(self):
        s = presets()["Limited battery"]
        q = build_qubo(s)
        offset,h,j = q.ising()
        energies = q.basis_energies()
        for index in range(2**q.n_qubits):
            bits = np.array([(index>>i)&1 for i in range(q.n_qubits)])
            z = 1-2*bits
            self.assertAlmostEqual(q.energy(bits), offset+h@z+z@j@z, places=6)
            self.assertAlmostEqual(q.energy(bits), energies[index], places=6)

    def test_each_selection_has_correct_minimized_penalty(self):
        s = Scenario("s", (Appliance("a",2,1,3),Appliance("b",3,1,4,True,True)),3,4,1)
        q = build_qubo(s)
        for bits in itertools.product((0,1),repeat=2):
            minimum = min(q.energy(bits+slack) for slack in itertools.product((0,1),repeat=q.n_qubits-2))
            e = evaluate(s,bits)
            if e["feasible"]:
                self.assertAlmostEqual(minimum,-e["utility"])
            else:
                self.assertGreaterEqual(minimum+e["utility"],q.penalty)

    def test_quantum_limit_before_simulation(self):
        with self.assertRaises(QuantumLimitError):
            build_qubo(presets()["Evening backup"], max_qubits=2)

    def test_measurement_bit_order(self):
        self.assertEqual(decode_counts_key("1010",4),(0,1,0,1))
        with self.assertRaises(ValueError):
            decode_counts_key("12",2)

    def test_input_precision_limit(self):
        s=Scenario("s",(Appliance("a",1.123456789,1,1),Appliance("b",1,1,1)),.5,3,1)
        with self.assertRaises(QuantumLimitError):
            build_qubo(s)


HAS_QUANTUM = bool(importlib.util.find_spec("qiskit") and importlib.util.find_spec("qiskit_aer"))


@unittest.skipUnless(HAS_QUANTUM, "Qiskit and Aer not installed; actual quantum execution remains unverified")
class QuantumTests(unittest.TestCase):
    def test_actual_circuit_counts_and_feasibility(self):
        from src.quantum_solver import solve_quantum
        s=Scenario("small",(Appliance("a",1,1,3),Appliance("b",1,1,2)),1,1,1)
        r=solve_quantum(s,depth=1,shots=256,maxiter=15,restarts=1)
        self.assertEqual(sum(r["counts"].values()),256)
        self.assertEqual(r["qubits"],4)
        self.assertGreater(r["optimizer_evaluations"],0)
        self.assertIsNotNone(r["best"])
        self.assertTrue(r["best"]["feasible"])
        self.assertLessEqual(r["best"]["utility"],solve_exact(s)["best"]["utility"])
        self.assertTrue(0 <= r["feasible_encoding_probability"] <= r["feasible_selection_probability"] <= 1)
        again=solve_quantum(s,depth=1,shots=256,maxiter=15,restarts=1)
        self.assertEqual(r["counts"],again["counts"])

    def test_circuit_phase_matches_ising(self):
        from qiskit.quantum_info import Statevector
        from src.quantum_solver import build_qaoa_circuit
        q=build_qubo(Scenario("s",(Appliance("a",1,1,2),Appliance("b",1,1,3)),2,2,1))
        circuit,params,scale,offset=build_qaoa_circuit(q,depth=1)
        gamma=.17
        circuit=circuit.assign_parameters({params[0]:gamma,params[1]:0.0})
        actual=np.asarray(Statevector.from_instruction(circuit))
        expected=np.exp(-1j*gamma*(q.basis_energies()-offset)/scale)/np.sqrt(2**q.n_qubits)
        np.testing.assert_allclose(actual,expected,atol=1e-10)


if __name__ == "__main__":
    unittest.main()
