"""Regression tests for the argument-review summary."""
import unittest

from argument_review import review_argument
from argument_review_summary import summarize_review


class ArgumentReviewSummaryTests(unittest.TestCase):
    def setUp(self):
        self.argument = {
            "id": "arg-summary",
            "premises": ["Premise one.", "Premise two."],
            "conclusion": "Conclusion.",
        }

    def test_summary_counts_only_supplied_items(self):
        report = review_argument(
            self.argument,
            evidence_by_premise={"1": ["Source A", "Source B"], "2": ["Source C"]},
            unstated_assumptions=["Assumption A"],
            counterexamples=["Counterexample A", "Counterexample B"],
        )
        summary = summarize_review(report)
        self.assertTrue(summary["valid_report"])
        self.assertEqual(summary["premise_count"], 2)
        self.assertEqual(summary["premises_with_evidence_supplied"], 2)
        self.assertEqual(summary["evidence_items_supplied"], 3)
        self.assertEqual(summary["assumption_count"], 1)
        self.assertEqual(summary["counterexample_count"], 2)

    def test_summary_never_claims_semantic_validation(self):
        summary = summarize_review(review_argument(self.argument))
        self.assertEqual(summary["conclusion_evidence_status"], "not_assessed")
        self.assertEqual(summary["inference_quality"], "not_assessed")
        self.assertEqual(summary["review_status"], "pending_human_review")

    def test_non_mapping_report_is_handled(self):
        summary = summarize_review(None)
        self.assertFalse(summary["valid_report"])
        self.assertEqual(summary["inference_quality"], "not_assessed")

    def test_malformed_entries_are_ignored_in_counts(self):
        summary = summarize_review({
            "argument_validation": {"valid": True, "argument_id": "x"},
            "premise_evidence": [{"evidence_items": ["A", "", None]}, "bad"],
            "unstated_assumptions": ["A", None],
            "counterexamples": ["B", ""],
            "review_status": "pending_human_review",
        })
        self.assertEqual(summary["evidence_items_supplied"], 1)
        self.assertEqual(summary["assumption_count"], 1)
        self.assertEqual(summary["counterexample_count"], 1)


if __name__ == "__main__":
    unittest.main()
