import unittest
from research.evaluation.metrics import summarise_attempts


class MetricsTests(unittest.TestCase):
    def test_failed_attempt_is_included_in_reliability_and_per_attempt_resources(self):
        result = summarise_attempts([
            {"success": True, "latency_ms": 100, "energy_wh": .2, "carbon_g": .1, "quality_score": 4},
            {"success": False, "energy_wh": .1, "carbon_g": .05},
        ])
        self.assertEqual(result["reliability_percent"], 50)
        self.assertEqual(result["energy_wh_per_attempt"], .15)
        self.assertEqual(result["energy_wh_per_success"], .2)


if __name__ == "__main__":
    unittest.main()
