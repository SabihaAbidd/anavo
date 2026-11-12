"""Synthetic consistency fixtures only; no fixture is published as quantum evidence."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
import unittest
import numpy as np
from scripts.evidence import check_benchmark_evidence,check_http_evidence,load_record,REQUIRED_HTTP_CHECKS
from scripts.provenance import source_fingerprint
from scripts.http_checks import measured_quantum
from src.scenarios import presets
from src.optimization import build_qubo
from src.models import evaluate
from src.classical_solver import solve_exact


def synthetic_benchmarks():
    """Classically constructed test data, never an actual QAOA experiment."""
    records=[]
    for name in ("Ample backup","Limited battery","Mandatory infeasible"):
        s=presets()[name];q=build_qubo(s)
        index=int(np.argmin(q.basis_energies()))
        bits=tuple((index>>i)&1 for i in range(q.n_qubits))
        candidate=evaluate(s,bits[:q.n_appliances])
        best=candidate if candidate["feasible"] else None
        classical=solve_exact(s)
        measured=format(index,f"0{q.n_qubits}b")
        metadata=dict(status="sampled" if best else "no feasible sample",best=best,
            counts={measured:8},shots=8,qubits=q.n_qubits,seed=42,qaoa_depth=1,circuit_depth=1,
            optimizer="COBYLA",optimizer_runs=[dict(message="synthetic unit-test fixture")],
            optimizer_evaluations=1,parameters=[.1,.2],runtime_s=.001,
            feasible_selection_probability=float(candidate["feasible"]),
            feasible_encoding_probability=float(candidate["feasible"] and q.encoding_feasible(bits)))
        gap=classical["best"]["utility"]-best["utility"] if classical["best"] and best else None
        records.append(dict(scenario=asdict(s),classical=classical,quantum=metadata,
            environment={"qiskit":"synthetic-test-fixture","qiskit-aer":"synthetic-test-fixture"},
            objective_gap=gap,relative_gap=0.0 if gap==0 else None))
    return dict(source_fingerprint="test-source",complete_quantum_execution=True,results=records)


class BenchmarkEvidenceTests(unittest.TestCase):
    def test_consistent_synthetic_fixture(self):
        self.assertEqual(check_benchmark_evidence(synthetic_benchmarks(),"test-source"),[])

    def test_stale_source_rejected(self):
        self.assertTrue(any("stale" in issue for issue in check_benchmark_evidence(synthetic_benchmarks(),"changed-source")))

    def test_counts_shots_probabilities_and_width_rejected(self):
        for defect in ("count","boolean","shots","probability","width"):
            data=synthetic_benchmarks();q=data["results"][0]["quantum"]
            key=next(iter(q["counts"]))
            if defect=="count": q["counts"][key]=-8
            if defect=="boolean": q["counts"][key]=True
            if defect=="shots": q["shots"]=9
            if defect=="probability": q["feasible_selection_probability"]=.25
            if defect=="width": q["counts"]={"0":8}
            with self.subTest(defect=defect): self.assertTrue(check_benchmark_evidence(data,"test-source"))

    def test_best_selection_and_gap_rejected(self):
        for defect in ("selection","utility","gap","classical"):
            data=synthetic_benchmarks();record=data["results"][0]
            if defect=="selection": record["quantum"]["best"]["selection"]=[0,0,0,0]
            if defect=="utility": record["quantum"]["best"]["utility"]=-1
            if defect=="gap": record["objective_gap"]=100
            if defect=="classical": record["classical"]["status"]="infeasible"
            with self.subTest(defect=defect): self.assertTrue(check_benchmark_evidence(data,"test-source"))

    def test_required_scenarios_cannot_be_duplicates(self):
        data=synthetic_benchmarks()
        data["results"]=[deepcopy(data["results"][0]) for _ in range(3)]
        self.assertTrue(check_benchmark_evidence(data,"test-source"))

    def test_unavailable_not_measured_and_missing_versions(self):
        for defect in ("unavailable","versions","nan"):
            data=synthetic_benchmarks();record=data["results"][0]
            if defect=="unavailable": record["quantum"]["status"]="unavailable"
            if defect=="versions": record["environment"]["qiskit"]=None
            if defect=="nan": record["quantum"]["parameters"][0]=float("nan")
            with self.subTest(defect=defect): self.assertTrue(check_benchmark_evidence(data,"test-source"))


class HTTPEvidenceTests(unittest.TestCase):
    def fixture(self):
        return dict(source_fingerprint="test-source",healthy=True,
                    checks=[dict(name=name,passed=True) for name in REQUIRED_HTTP_CHECKS])

    def test_all_checks_required(self):
        self.assertEqual(check_http_evidence(self.fixture(),"test-source"),[])
        data=self.fixture();data["checks"].pop()
        self.assertTrue(check_http_evidence(data,"test-source"))

    def test_health_only_is_insufficient(self):
        self.assertTrue(check_http_evidence(dict(healthy=True,source_fingerprint="test-source"),"test-source"))

    def test_failed_duplicate_and_stale_checks(self):
        for defect in ("failed","duplicate","stale"):
            data=self.fixture()
            if defect=="failed": data["checks"][0]["passed"]=False
            if defect=="duplicate": data["checks"].append(data["checks"][0])
            if defect=="stale": data["source_fingerprint"]="older-source"
            with self.subTest(defect=defect): self.assertTrue(check_http_evidence(data,"test-source"))

    def test_measured_quantum_requires_actual_positive_counts_and_allocation(self):
        result=dict(status="sampled",allocation=dict(feasible=True),quantum_metadata=dict(shots=256,counts={"01":256}))
        self.assertTrue(measured_quantum(result))
        result["quantum_metadata"]["counts"]={"01":True}
        self.assertFalse(measured_quantum(result))
        self.assertFalse(measured_quantum(dict(status="unavailable")))


class ProvenanceTests(unittest.TestCase):
    def test_stable_fingerprint_and_runtime_change_detection(self):
        before=source_fingerprint()
        self.assertEqual(len(before),64)
        self.assertEqual(before,source_fingerprint())
        original=Path.read_bytes
        def changed(path):
            content=original(path)
            return content+b"\n# synthetic source change\n" if path.name=="models.py" else content
        with patch.object(Path,"read_bytes",changed): self.assertNotEqual(before,source_fingerprint())

    def test_bad_record_is_an_issue_not_an_uncaught_error(self):
        for body in ("{", "[]"):
            with patch.object(Path,"read_text",return_value=body):
                data,error=load_record("synthetic-record.json")
            self.assertIsNone(data)
            self.assertIsNotNone(error)


if __name__=="__main__": unittest.main()
