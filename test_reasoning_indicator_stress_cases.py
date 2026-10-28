"""Schema and reproducibility checks for contextual stress-review cases.

Observed matches document current lexical behavior; they are not gold labels.
"""
import json
import unittest
from pathlib import Path

from reasoning import analyze_reasoning_indicators


CASES_PATH = Path(__file__).with_name("reasoning_indicator_stress_cases.json")
CATEGORIES = {"evidence", "reasoning", "uncertainty"}


class ReasoningIndicatorStressCasesTests(unittest.TestCase):
    def test_cases_have_valid_unique_ids_and_review_fields(self):
        cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 8)
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        required = {
            "id", "answer", "review_focus", "observed_lexical_matches",
            "review_question", "interpretation_note", "review_status",
        }
        for case in cases:
            self.assertTrue(required.issubset(case))
            self.assertTrue(case["id"])
            self.assertTrue(case["answer"])
            self.assertTrue(case["review_question"])
            self.assertTrue(case["interpretation_note"])
            self.assertEqual(case["review_status"], "pending_human_review")
            self.assertTrue(set(case["observed_lexical_matches"]).issubset(CATEGORIES))

    def test_recorded_matches_reproduce_current_detector_output(self):
        cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["id"]):
                actual = analyze_reasoning_indicators(case["answer"])["detected_categories"]
                self.assertEqual(actual, case["observed_lexical_matches"])


if __name__ == "__main__":
    unittest.main()
