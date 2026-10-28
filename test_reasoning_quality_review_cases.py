"""Checks the separate, unlabelled reasoning-quality review set."""
import json
from pathlib import Path
import unittest


PATH = Path(__file__).with_name("reasoning_quality_review_cases.json")


class ReasoningQualityReviewCasesTests(unittest.TestCase):
    def test_cases_have_unique_ids_and_required_fields(self):
        cases = json.loads(PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 10)
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        required = {
            "id", "prompt", "claim", "context", "review_focus",
            "review_question", "review_status",
        }
        for case in cases:
            with self.subTest(case=case.get("id")):
                self.assertTrue(required.issubset(case))
                for field in required - {"review_status"}:
                    self.assertTrue(str(case[field]).strip(), field)
                self.assertEqual(case["review_status"], "pending_human_review")

    def test_review_set_covers_multiple_reasoning_failure_modes(self):
        cases = json.loads(PATH.read_text(encoding="utf-8"))
        focuses = {case["review_focus"] for case in cases}
        for focus in (
            "causal_inference", "correlation_causation", "overgeneralization",
            "confounding", "unsupported_motive", "uncertainty_calibration",
            "attribution", "scope_mismatch", "insufficient_context",
        ):
            self.assertIn(focus, focuses)

    def test_no_semantic_gold_labels_are_prepopulated(self):
        cases = json.loads(PATH.read_text(encoding="utf-8"))
        forbidden_fields = {
            "gold_label", "correctness_label", "inference_quality",
            "evidence_support", "adjudicated_label",
        }
        for case in cases:
            self.assertTrue(forbidden_fields.isdisjoint(case), case["id"])
            self.assertEqual(case["review_status"], "pending_human_review")


if __name__ == "__main__":
    unittest.main()
