"""Optional historical UI tests; install requirements-demo.txt to run explicitly."""
import unittest
from streamlit.testing.v1 import AppTest


class DashboardTests(unittest.TestCase):
    def test_launch_optimize_and_stale_result_invalidation(self):
        at=AppTest.from_file("app.py",default_timeout=60).run()
        self.assertFalse(at.exception)
        self.assertEqual(at.title[0].value,"ANAVO")
        at.button(key="optimize").click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any("Exact classical recommendation" in x.value for x in at.success))
        at.number_input(key="battery_Evening backup").set_value(0.0).run()
        self.assertFalse(at.exception)
        self.assertFalse(at.success)
        at.button(key="optimize").click().run()
        self.assertTrue(any("No feasible allocation" in x.value for x in at.error))

    def test_invalid_duration(self):
        at=AppTest.from_file("app.py",default_timeout=30).run()
        at.number_input(key="outage_Evening backup").set_value(.5).run()
        self.assertFalse(at.exception)
        self.assertTrue(any("duration cannot exceed" in x.value for x in at.error))

    def test_presets_change_capacity(self):
        at=AppTest.from_file("app.py",default_timeout=30).run()
        at.selectbox(key="preset").select("Limited battery").run()
        self.assertEqual(at.number_input(key="battery_Limited battery").value,90)
        self.assertFalse(at.exception)


if __name__ == "__main__":
    unittest.main()
