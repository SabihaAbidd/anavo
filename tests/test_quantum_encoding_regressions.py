import itertools
import unittest
from src.models import Appliance, Scenario, evaluate
from src.optimization import build_qubo, QuantumLimitError
from src.quantum_solver import solve_quantum, build_qaoa_circuit,hamiltonian_scale
from src.classical_solver import solve_exact
from src.scenarios import presets


class EncodingRegressions(unittest.TestCase):
    def test_tiny_utilities_are_rejected_instead_of_erased(self):
        s=Scenario("tiny",(Appliance("a",1,1,1e-20),Appliance("b",1,1,2e-20)),1,1,1)
        self.assertEqual(solve_exact(s)["best"]["bitstring"],"01")
        with self.assertRaisesRegex(QuantumLimitError,"Utility precision"):
            build_qubo(s)

    def test_reasonable_fractional_utility_preserves_optimum(self):
        s=Scenario("decimal",(Appliance("a",1,1,.1),Appliance("b",1,1,.2)),1,1,1)
        q=build_qubo(s)
        self.assertAlmostEqual(float(q.basis_energies().min()),-.2)

    def test_integer_residuals_match_full_feasibility(self):
        s=presets()["Limited battery"]
        q=build_qubo(s)
        for bits in itertools.product((0,1),repeat=q.n_qubits):
            expected=evaluate(s,bits[:q.n_appliances])["feasible"] and abs(q.energy(bits)+evaluate(s,bits[:q.n_appliances])["utility"])<1e-7
            self.assertEqual(q.encoding_feasible(bits),expected)

    def test_wrong_slack_is_not_physically_infeasible(self):
        s=Scenario("slack",(Appliance("a",1,1,1),Appliance("b",1,1,2)),1,1,1)
        q=build_qubo(s)
        self.assertTrue(evaluate(s,(0,0))["feasible"])
        self.assertFalse(q.encoding_feasible((0,)*q.n_qubits))

    def test_mandatory_without_auxiliary_bits(self):
        s=Scenario("mandatory",(Appliance("a",1,1,1,True,True),),5,5,1)
        q=build_qubo(s)
        self.assertFalse(q.encoding_feasible((0,)))
        self.assertTrue(q.encoding_feasible((1,)))
        with self.assertRaises(ValueError): q.encoding_feasible((2,))

    def test_options_validate_before_optional_quantum_imports(self):
        s=presets()["Ample backup"]
        for options in (dict(seed=-1),dict(shots=True),dict(depth=0),dict(restarts=False),dict(max_qubits=15)):
            with self.subTest(options=options),self.assertRaises(ValueError):
                solve_quantum(s,**options)
        with self.assertRaises(ValueError): build_qaoa_circuit(build_qubo(s),depth=True)

    def test_small_unconstrained_cost_is_normalized_not_dropped(self):
        s=Scenario("tiny no penalties",(Appliance("a",1,1,1e-20),),2,2,1)
        q=build_qubo(s)
        _,h,j=q.ising()
        scale=hamiltonian_scale(h,j)
        self.assertGreater(scale,0)
        self.assertLess(scale,1)
        self.assertAlmostEqual(float(h[0]/scale),1.0)


if __name__=="__main__": unittest.main()
