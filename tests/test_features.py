"""Scheduling, housing-society (fleet), Pakistan dataset, jobs and quantum-insight checks."""
import importlib.util
import json
import time
import unittest
from pathlib import Path
from src.classical_solver import solve_exact
from src.fleet import solve_fleet, jain_index
from src.models import Appliance as A, Scenario
from src.scenarios import presets
from src.scheduler import solve_schedule, solar_profile

HAS_API = bool(importlib.util.find_spec("fastapi"))
HAS_QUANTUM = bool(importlib.util.find_spec("qiskit") and importlib.util.find_spec("qiskit_aer"))


def house():
    return Scenario("House", (A("Fan", 75, 4, 9), A("Lights", 20, 4, 8), A("Router", 12, 4, 10, True, True),
                              A("Pump", 750, 1, 8), A("Iron", 1000, 0.5, 4), A("Washer", 400, 1, 5),
                              A("Fridge", 150, 2, 7)), 2000, 1100, 4)


class SchedulerTests(unittest.TestCase):
    def test_full_window_presets_match_exact_solver(self):
        # Every preset load spans the whole window, so sequencing cannot help: utilities must agree.
        for scenario in presets().values():
            exact = solve_exact(scenario)["best"]
            plan = solve_schedule(scenario)
            self.assertEqual(plan["feasible"], exact is not None, scenario.name)
            if exact:
                self.assertEqual(plan["utility"], exact["utility"], scenario.name)

    def test_sequencing_beats_simultaneous_reservation(self):
        scenario = house()
        plan = solve_schedule(scenario)
        self.assertGreater(plan["utility"], solve_exact(scenario)["best"]["utility"])
        self.assertTrue(all(slot["load_w"] <= scenario.inverter_w for slot in plan["timeline"]))
        self.assertGreaterEqual(min(slot["battery_wh"] for slot in plan["timeline"]), 0)
        router = next(p for p in plan["appliances"] if p["name"] == "Router")
        self.assertTrue(router["selected"])

    def test_contiguous_blocks_and_energy_balance(self):
        plan = solve_schedule(house())
        for item in plan["appliances"]:
            if item["selected"]:
                running = [s["slot"] for s in plan["timeline"] if item["name"] in s["running"]]
                self.assertEqual(running, list(range(running[0], running[0] + len(running))))
        used = sum(s["load_w"] for s in plan["timeline"]) * plan["slot_h"]
        self.assertAlmostEqual(used, plan["energy_used_wh"])
        self.assertAlmostEqual(plan["final_battery_wh"], 2000 - used)

    def test_mandatory_infeasibility_is_reported(self):
        plan = solve_schedule(presets()["Mandatory infeasible"])
        self.assertFalse(plan["feasible"])
        self.assertEqual(plan["status"], "infeasible")

    def test_solar_never_reduces_utility_and_is_zero_at_night(self):
        scenario = presets()["Limited battery"]
        night = solar_profile(6, 1.0, 20, 2.0, 5.67)
        self.assertEqual(sum(night[:6]), 0.0)
        day_without = solve_schedule(scenario, start_hour=10)
        day_with = solve_schedule(scenario, start_hour=10, solar_kwp=1.0)
        self.assertGreaterEqual(day_with["utility"], day_without["utility"])
        self.assertGreater(day_with["solar_generated_wh"], 0)

    def test_solar_daily_total_matches_assumption(self):
        profile = solar_profile(96, 0.25, 0, 1.0, 5.67)
        self.assertAlmostEqual(sum(profile), 1000 * 5.67 * 0.75, delta=15)


class FleetTests(unittest.TestCase):
    def homes(self, count=6):
        kinds = [(A("Fan", 80, 4, 9), A("Lights", 20, 4, 8), A("Router", 12, 4, 8, True, True)),
                 (A("Oxygen", 300, 4, 10, True, True), A("Fan", 55, 4, 9), A("Fridge", 150, 2, 7)),
                 (A("AC", 1000, 3, 5), A("Fan", 80, 4, 9), A("Pump", 750, 1, 8), A("Router", 12, 4, 8, True, True))]
        return [dict(name=f"H{i}", weight=1.0, appliances=list(kinds[i % 3])) for i in range(count)]

    def test_shared_limits_and_mandatory_loads_hold(self):
        result = solve_fleet(self.homes(), 9000, 2500, 4)
        self.assertTrue(result["feasible"])
        self.assertLessEqual(result["energy_used_wh"], 9000)
        self.assertLessEqual(result["power_used_w"], 2500)
        self.assertTrue(all(h["mandatory_met"] for h in result["home_results"]))

    def test_pooling_is_never_worse_than_equal_split(self):
        for battery, inverter in ((6000, 2000), (9000, 2500), (20000, 6000)):
            result = solve_fleet(self.homes(), battery, inverter, 4)
            self.assertGreaterEqual(result["utility"], result["baseline"]["utility"])

    def test_fairness_floor_is_enforced_or_infeasible(self):
        result = solve_fleet(self.homes(), 9000, 2500, 4, fairness_floor=0.5)
        if result["feasible"]:
            self.assertTrue(all(h["service_ratio"] >= 0.5 - 1e-9 for h in result["home_results"]))
        impossible = solve_fleet(self.homes(), 9000, 2500, 4, fairness_floor=1.0)
        self.assertFalse(impossible["feasible"])

    def test_mandatory_shortage_is_infeasible(self):
        self.assertEqual(solve_fleet(self.homes(), 100, 2500, 4)["status"], "infeasible")

    def test_jain_index_bounds(self):
        self.assertAlmostEqual(jain_index([1, 1, 1]), 1.0)
        self.assertAlmostEqual(jain_index([1, 0, 0]), 1/3)

    def test_scales_to_hundreds_of_homes(self):
        result = solve_fleet(self.homes(300), 400000, 120000, 4)
        self.assertEqual(result["status"], "optimal")
        self.assertEqual(result["homes"], 300)


class DatasetTests(unittest.TestCase):
    def test_every_basis_is_a_cited_source_or_estimate(self):
        data = json.loads(Path("data/pakistan_energy.json").read_text(encoding="utf-8"))
        sources = data["sources"]
        self.assertTrue(all(s["url"].startswith("https://") for s in sources.values()))
        items = data["appliances"] + data["outage_profiles"] + [data["solar"]]
        for item in items:
            self.assertIn(item["basis"], list(sources) + ["estimate"], item)
        names = {a["name"] for a in data["appliances"]}
        for archetype in data["household_archetypes"]:
            self.assertTrue(set(archetype["appliances"]) <= names, archetype["id"])


@unittest.skipUnless(HAS_API, "FastAPI is not installed")
class FeatureAPITests(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from backend.main import create_app
        self.client = self.enterContext(TestClient(create_app(), raise_server_exceptions=False))
        self.scenarios = self.client.get("/api/scenarios").json()["scenarios"]

    def test_schedule_endpoint(self):
        response = self.client.post("/api/schedule", json={"scenario": self.scenarios[0]})
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["utility"], 24)
        self.assertEqual(body["gain_vs_simultaneous"], 0)
        self.assertEqual(len(body["timeline"]), 3)

    def test_schedule_rejects_bad_start_hour(self):
        response = self.client.post("/api/schedule", json={"scenario": self.scenarios[0], "start_hour": 24})
        self.assertEqual(response.status_code, 422)

    def test_fleet_endpoint_and_validation(self):
        home = dict(name="A", appliances=self.scenarios[0]["appliances"])
        body = dict(homes=[home, dict(home, name="B")], battery_wh=480, inverter_w=200, outage_h=3)
        response = self.client.post("/api/fleet/optimize", json=body)
        self.assertEqual(response.status_code, 200, response.text)
        # Equal split gives each home 240 Wh / 100 W (24 each); pooling lets one home add its laptop.
        self.assertEqual(response.json()["baseline"]["utility"], 48)
        self.assertEqual(response.json()["utility"], 54)
        self.assertEqual(response.json()["gain_vs_equal_split"], 6)
        self.assertEqual(self.client.post("/api/fleet/optimize", json=dict(body, homes=[])).status_code, 422)

    def test_pakistan_dataset_endpoint(self):
        data = self.client.get("/api/data/pakistan").json()["data"]
        self.assertIn("esmap_solar", data["sources"])
        self.assertEqual(data["solar"]["ghi_kwh_m2_day"], 5.67)

    def test_job_lifecycle_and_errors(self):
        submitted = self.client.post("/api/jobs", json={"kind": "schedule", "payload": {"scenario": self.scenarios[1]}})
        self.assertEqual(submitted.status_code, 202, submitted.text)
        job_id = submitted.json()["job_id"]
        for _ in range(100):
            job = self.client.get(f"/api/jobs/{job_id}").json()
            if job["status"] in ("succeeded", "failed"):
                break
            time.sleep(0.05)
        self.assertEqual(job["status"], "succeeded")
        self.assertEqual(job["result"]["utility"], 30)
        self.assertEqual(self.client.get("/api/jobs/unknown").status_code, 404)
        self.assertEqual(self.client.post("/api/jobs", json={"kind": "fleet", "payload": {}}).status_code, 422)
        self.assertEqual(self.client.get("/api/jobs").json()["workers"], 1)


@unittest.skipUnless(HAS_API and HAS_QUANTUM, "Qiskit/Aer not installed; quantum insight checks pending")
class QuantumInsightTests(unittest.TestCase):
    def test_compare_returns_measured_insights(self):
        from fastapi.testclient import TestClient
        from backend.main import create_app
        client = self.enterContext(TestClient(create_app(), raise_server_exceptions=False))
        scenario = client.get("/api/scenarios").json()["scenarios"][2]
        body = client.post("/api/compare", json={"scenario": scenario}).json()
        meta = body["quantum"]["quantum_metadata"]
        self.assertAlmostEqual(sum(s["probability"] for s in meta["selection_distribution"]), 1.0)
        self.assertEqual(sum(s["count"] for s in meta["selection_distribution"]), meta["shots"])
        self.assertEqual(len(meta["landscape"]), 16)
        self.assertEqual(len(meta["qubit_roles"]), meta["qubits"])
        self.assertIn("rzz", meta["circuit_operations"])
        self.assertEqual(len(meta["objective_history"]), meta["optimizer_evaluations"])
        optimum = body["classical"]["allocation"]["bitstring"]
        expected = sum(s["probability"] for s in meta["selection_distribution"] if s["appliance_bitstring"] == optimum)
        self.assertAlmostEqual(body["optimal_selection_probability"], expected)


if __name__ == "__main__":
    unittest.main()
