"""Contextual stress tests document observed lexical behavior, not semantic truth."""
import json
import unittest
from pathlib import Path

from anima import evaluate_answer

CASES_PATH = Path(__file__).with_name("contextual_stress_cases.json")
CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))


class ContextualStressTests(unittest.TestCase):
    def test_dataset_has_unique_ids_and_pending_human_review(self):
        ids = [case["id"] for case in CASES]
        self.assertEqual(len(ids), len(set(ids)))
        for case in CASES:
            self.assertEqual(case["review_status"], "pending_human_review")
            self.assertTrue(case["review_question"].strip())

    def test_observed_detector_statuses_are_reproducible(self):
        for case in CASES:
            with self.subTest(case_id=case["id"]):
                result = evaluate_answer(case["answer"], case["criteria"])
                actual = {item["criterion"]: item["status"] for item in result["criterion_analysis"]}
                expected = case.get("observed_statuses")
                if expected is None:
                    expected = {case["criteria"][0]: case["observed_status"]}
                self.assertEqual(actual, expected)

    def test_double_negation_case_has_updated_observed_status(self):
        case = next(item for item in CASES if item["id"] == "double_negation_not_irrelevant")
        result = evaluate_answer(case["answer"], case["criteria"])
        self.assertEqual(result["criterion_analysis"][0]["status"], "matched")
        self.assertEqual(case["review_status"], "pending_human_review")

    def test_dataset_explicitly_does_not_claim_semantic_validation(self):
        for case in CASES:
            self.assertIn("review_question", case)
            self.assertEqual(case["review_status"], "pending_human_review")
            self.assertNotIn("semantic_correctness", case)


if __name__ == "__main__":
    unittest.main()
