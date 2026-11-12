"""Actual FastAPI TestClient endpoint checks, conditionally skipped if absent."""
import importlib.util
import unittest
from unittest.mock import patch
from tests.test_backend_service import payload

HAS_API=bool(importlib.util.find_spec("fastapi"))
HAS_QUANTUM=bool(importlib.util.find_spec("qiskit") and importlib.util.find_spec("qiskit_aer"))


@unittest.skipUnless(HAS_API,"FastAPI is not installed; actual HTTP endpoint verification remains pending")
class APITests(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from backend.main import create_app
        self.app=create_app()
        self.client=self.enterContext(TestClient(self.app,raise_server_exceptions=False))

    def test_health(self):
        response=self.client.get("/health")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["service"],"ANAVO API")
        self.assertIn("quantum_dependencies_available",response.json())

    def test_scenarios(self):
        response=self.client.get("/api/scenarios")
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json()["scenarios"]),4)
        self.assertEqual(response.json()["scenarios"][0]["name"],"Evening backup")

    def test_algorithm_info(self):
        response=self.client.get("/api/algorithm-info")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["quantum"]["algorithm"],"QAOA")
        self.assertFalse(response.json()["quantum"]["speedup_claim"])

    def test_classical_optimize(self):
        response=self.client.post("/api/optimize",json=payload())
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["result"]["allocation"]["objective_value"],24)
        self.assertEqual(response.json()["result"]["allocation"]["energy_used_wh"],180)

    def test_infeasible_is_valid_domain_response(self):
        response=self.client.post("/api/optimize",json=payload("Mandatory infeasible"))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["result"]["status"],"infeasible")
        self.assertIsNone(response.json()["result"]["allocation"])

    def test_compare_unavailable_is_partial_success(self):
        with patch("backend.service.solve_quantum",side_effect=ImportError("missing")):
            response=self.client.post("/api/compare",json=payload())
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["comparison_status"],"quantum_unavailable")
        self.assertEqual(response.json()["classical"]["allocation"]["objective_value"],24)
        self.assertIsNone(response.json()["objective_gap"])

    def test_quantum_unavailable_error(self):
        with patch("backend.service.solve_quantum",side_effect=ImportError("missing")):
            response=self.client.post("/api/optimize",json={**payload(),"algorithm":"quantum"})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json()["error"]["code"],"quantum_dependency_unavailable")

    def test_quantum_oversized_error(self):
        response=self.client.post("/api/optimize",json={**payload(),"algorithm":"quantum","quantum_options":{"max_qubits":1}})
        self.assertEqual(response.status_code,413)
        self.assertEqual(response.json()["error"]["code"],"quantum_resource_limit")

    def test_validation_errors(self):
        data=payload()
        data["scenario"]["battery_wh"]=-1
        response=self.client.post("/api/optimize",json=data)
        self.assertEqual(response.status_code,422)
        self.assertEqual(response.json()["error"]["code"],"validation_error")
        response=self.client.post("/api/compare",content='{"scenario":',headers={"Content-Type":"application/json"})
        self.assertEqual(response.status_code,422)

    def test_restricted_cors(self):
        for origin,expected in (("http://localhost:5173",200),("https://untrusted.example",400)):
            response=self.client.options("/api/optimize",headers={"Origin":origin,
                "Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"Content-Type"})
            self.assertEqual(response.status_code,expected)
            if expected==200: self.assertEqual(response.headers["access-control-allow-origin"],origin)
            else: self.assertNotIn("access-control-allow-origin",response.headers)

    def test_busy_response_releases_slot(self):
        self.app.state.optimization_slots.acquire()
        try:
            response=self.client.post("/api/optimize",json=payload())
            self.assertEqual(response.status_code,429)
            self.assertEqual(response.json()["error"]["code"],"optimizer_busy")
        finally:
            self.app.state.optimization_slots.release()
        self.assertEqual(self.client.post("/api/optimize",json=payload()).status_code,200)

    def test_openapi_contract(self):
        response=self.client.get("/openapi.json")
        self.assertEqual(response.status_code,200)
        schema=response.json()
        for path in ("/health","/api/scenarios","/api/optimize","/api/compare","/api/algorithm-info"):
            self.assertIn(path,schema["paths"])
        self.assertIn("OptimizeResponse",schema["components"]["schemas"])
        self.assertEqual(self.client.get("/docs").status_code,200)


@unittest.skipUnless(HAS_API and HAS_QUANTUM,"FastAPI and Qiskit/Aer required for actual measured quantum API validation")
class RealQuantumAPITests(unittest.TestCase):
    def test_real_quantum_compare(self):
        from fastapi.testclient import TestClient
        from backend.main import create_app
        data=payload("Ample backup")
        data["quantum_options"]={"depth":1,"shots":128,"maxiter":15,"restarts":1,"seed":42}
        with TestClient(create_app()) as client:
            response=client.post("/api/compare",json=data)
        self.assertEqual(response.status_code,200)
        result=response.json()
        metadata=result["quantum"]["quantum_metadata"]
        self.assertIsNotNone(metadata,result)
        self.assertEqual(sum(metadata["counts"].values()),128)
        self.assertTrue(result["quantum"]["allocation"]["feasible"])
        self.assertGreaterEqual(result["objective_gap"],0)
