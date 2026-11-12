"""Executed contract/service checks; these do not pretend to be HTTP tests."""
import json
import os
import unittest
from unittest.mock import patch
from pydantic import ValidationError
from backend.schemas import ScenarioInput, OptimizeRequest, CompareRequest, QuantumOptions, OptimizeResponse
from backend import service
from backend.settings import cors_origins
from src.scenarios import presets


def payload(name="Evening backup"):
    return dict(scenario=ScenarioInput.from_domain(presets()[name]).model_dump(mode="json"))


class ContractTests(unittest.TestCase):
    def test_domain_roundtrip(self):
        for original in presets().values():
            schema = ScenarioInput.from_domain(original)
            self.assertEqual(schema.to_domain(), original)

    def test_strict_numeric_and_boolean_fields(self):
        for key,value in (("power_w","40"),("power_w",True),("utility",-1),
                          ("duration_h",float("nan")),("essential","true")):
            data = payload()
            data["scenario"]["appliances"][0][key] = value
            with self.subTest(key=key,value=value), self.assertRaises(ValidationError):
                OptimizeRequest(**data)

    def test_cross_field_validation(self):
        for edit in ("duration","duplicate","empty","count"):
            data = payload()
            if edit=="duration": data["scenario"]["outage_h"] = 1
            if edit=="duplicate": data["scenario"]["appliances"][1]["name"] = " FAN "
            if edit=="empty": data["scenario"]["appliances"] = []
            if edit=="count": data["scenario"]["appliances"] *= 5
            with self.subTest(edit=edit), self.assertRaises(ValidationError):
                OptimizeRequest(**data)

    def test_forbid_unknown_fields_and_modes(self):
        for changes in (dict(algorithm="fake_quantum"),dict(unexpected=True)):
            with self.assertRaises(ValidationError):
                OptimizeRequest(**payload(),**changes)

    def test_quantum_limits(self):
        for field,value in (("depth",0),("shots",8193),("maxiter",201),
                            ("seed",-1),("restarts",4),("max_qubits",15),("shots",True)):
            with self.subTest(field=field),self.assertRaises(ValidationError):
                QuantumOptions(**{field:value})

    def test_infinite_battery_rejected(self):
        data=payload()
        data["scenario"]["battery_wh"]=float("inf")
        with self.assertRaises(ValidationError): OptimizeRequest(**data)

    def test_defaults_and_json_schema(self):
        request=OptimizeRequest(**payload())
        self.assertEqual(request.algorithm,"classical")
        self.assertEqual(request.quantum_options.shots,2048)
        self.assertIn("QuantumOptions",OptimizeRequest.model_json_schema()["$defs"])


class ServiceTests(unittest.TestCase):
    def test_exact_allocation_contract(self):
        result=service.optimize(OptimizeRequest(**payload()))
        best=result.result.allocation
        self.assertEqual(best.objective_value,24)
        self.assertEqual([a.name for a in best.selected_appliances],["Fan","LED lights","Wi-Fi router"])
        self.assertEqual([a.name for a in best.deferred_appliances],["Laptop"])
        self.assertEqual((best.energy_used_wh,best.power_used_w),(180,60))
        self.assertEqual((best.energy_remaining_wh,best.inverter_remaining_w),(60,40))
        self.assertEqual(result.result.feasibility,"feasible")
        self.assertFalse(result.fallback_used)
        encoded=result.model_dump_json()
        self.assertEqual(OptimizeResponse.model_validate_json(encoded),result)
        self.assertEqual(json.loads(encoded)["schema_version"],"1.0")

    def test_infeasible_preserves_requirements(self):
        result=service.optimize(OptimizeRequest(**payload("Mandatory infeasible")))
        self.assertEqual(result.result.status,"infeasible")
        self.assertEqual(result.result.feasibility,"infeasible")
        self.assertIsNone(result.result.allocation)
        self.assertTrue(result.scenario.appliances[2].mandatory)

    def test_zero_budget_safe_empty_allocation(self):
        data=payload()
        data["scenario"]["battery_wh"]=0
        data["scenario"]["inverter_w"]=0
        for a in data["scenario"]["appliances"]: a["mandatory"]=False
        best=service.optimize(OptimizeRequest(**data)).result.allocation
        self.assertEqual(best.energy_utilization,0)
        self.assertEqual(best.selection,[0,0,0,0])

    def test_compare_dependency_unavailable_is_explicit(self):
        with patch("backend.service.solve_quantum",side_effect=ImportError("not installed")):
            result=service.compare(CompareRequest(**payload()))
        self.assertEqual(result.comparison_status,"quantum_unavailable")
        self.assertEqual(result.classical.allocation.objective_value,24)
        self.assertIsNone(result.quantum.allocation)
        self.assertIsNone(result.quantum.quantum_metadata)
        self.assertIsNone(result.objective_gap)

    def test_quantum_mode_never_uses_classical_fallback(self):
        with patch("backend.service.solve_exact",side_effect=AssertionError("unexpected baseline")), \
             patch("backend.service.solve_quantum",side_effect=ImportError("not installed")):
            result=service.optimize(OptimizeRequest(**payload(),algorithm="quantum"))
        self.assertEqual(result.result.status,"unavailable")
        self.assertFalse(result.fallback_used)

    def test_actual_oversized_preflight(self):
        result=service.compare(CompareRequest(**payload(),quantum_options=QuantumOptions(max_qubits=1)))
        self.assertEqual(result.comparison_status,"quantum_oversized")
        self.assertEqual(result.quantum.error_code,"quantum_resource_limit")
        self.assertIsNone(result.objective_gap)

    def test_failure_preserves_classical_and_hides_exception_details(self):
        with patch("backend.service.solve_quantum",side_effect=RuntimeError("internal private detail")), \
             self.assertLogs("backend.service",level="ERROR"):
            result=service.compare(CompareRequest(**payload()))
        self.assertEqual(result.comparison_status,"quantum_failed")
        self.assertEqual(result.classical.allocation.objective_value,24)
        self.assertNotIn("internal private detail",result.model_dump_json())

    def test_candidate_resources_are_rechecked(self):
        scenario=presets()["Evening backup"]
        checked=service.allocation(scenario,dict(selection=[1,1,1,0],utility=999,energy_wh=0))
        self.assertEqual(checked.objective_value,24)
        self.assertEqual(checked.energy_used_wh,180)
        with self.assertRaises(ValueError):
            service.allocation(scenario,dict(selection=[1,1,1,1],feasible=True))


class SettingsTests(unittest.TestCase):
    def test_default_local_cors(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertEqual(cors_origins(),["http://localhost:5173","http://127.0.0.1:5173"])

    def test_explicit_cors(self):
        with patch.dict(os.environ,{"ANAVO_CORS_ORIGINS":"https://anavo.example,https://anavo.example"}):
            self.assertEqual(cors_origins(),["https://anavo.example"])

    def test_reject_cors_wildcards_credentials_and_paths(self):
        for value in ("*","https://*.example","https://x.example/path","https://user:pass@x.example","file://x","https://x:bad"):
            with patch.dict(os.environ,{"ANAVO_CORS_ORIGINS":value}), self.subTest(value=value), self.assertRaises(ValueError):
                cors_origins()
