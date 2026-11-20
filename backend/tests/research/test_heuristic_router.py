import unittest
from research.baseline.heuristic_router import Calibration, select_model


class HeuristicRouterTests(unittest.TestCase):
    def test_selects_highest_weighted_candidate_deterministically(self):
        candidates = [
            {"model_id": "provider/fast", "fit_score": 80, "carbon_g": 999},
            {"model_id": "provider/fit", "fit_score": 95, "carbon_g": 0},
        ]
        calibration = {
            "provider/fast": Calibration(100, 100, 40),
            "provider/fit": Calibration(90, 500, 40),
        }
        result = select_model(candidates, calibration)
        self.assertEqual(result["selected_model"], "provider/fast")
        # Carbon fields are intentionally ignored by CHR scoring.
        self.assertEqual(result["selection_method"], "CHR-0.1")

    def test_excludes_insufficient_calibration(self):
        with self.assertRaises(ValueError):
            select_model([{"model_id": "x", "fit_score": 90}], {"x": Calibration(99, 10, 2)})


if __name__ == "__main__":
    unittest.main()
