"""Schema and lexical-output checks for the contextual stress review set."""
import json
from pathlib import Path
import unittest

from reasoning import analyze_reasoning_indicators


class ReasoningIndicatorStressReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("reasoning_indicator_stress_review_cases.json")
        cls.cases = json.loads(path.read_text(encoding="utf-8"))

    def test_cases_have_unique_ids_and_pending_status(self):
        ids = [case["id"] for case in self.cases]
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(len(ids), len(set(ids)))
        for case in self.cases:
            self.assertEqual(case["review_status"], "pending_human_review")
            self.assertTrue(case["review_focus"])
            self.assertTrue(case["review_question"])
            self.assertTrue(case["interpretation_note"])

    def test_recorded_outputs_match_current_lexical_detector(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                actual = analyze_reasoning_indicators(case["answer"])["detected_categories"]
                self.assertEqual(case["lexical_expected_detected"], actual)

    def test_dataset_does_not_claim_completed_human_review(self):
        self.assertTrue(all(case["review_status"] == "pending_human_review" for case in self.cases))


if __name__ == "__main__":
    unittest.main()
