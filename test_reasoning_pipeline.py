"""Tests for the combined reasoning report."""
import unittest

from reasoning_pipeline import evaluate_reasoning


class CombinedReasoningReportTests(unittest.TestCase):
    def test_combines_existing_criterion_and_indicator_reports(self):
        result = evaluate_reasoning(
            "Evidence supports the claim because the study measured outcomes. "
            "The estimate may remain uncertain.",
            ["evidence", "reasoning", "uncertainty"],
        )
        self.assertEqual(result["criterion_evaluation"]["score"], 100)
        self.assertEqual(
            result["reasoning_indicators"]["detected_categories"],
            ["evidence", "reasoning", "uncertainty"],
        )
        self.assertIn("does not establish", result["overall_notice"])

    def test_reports_missing_criterion_without_hiding_detected_indicators(self):
        result = evaluate_reasoning("Evidence supports the claim.", ["evidence", "uncertainty"])
        self.assertEqual(result["criterion_evaluation"]["missing_points"], ["uncertainty"])
        self.assertEqual(result["reasoning_indicators"]["detected_categories"], ["evidence"])

    def test_invalid_answer_is_rejected_by_existing_evaluator(self):
        with self.assertRaises(TypeError):
            evaluate_reasoning(None, ["evidence"])


if __name__ == "__main__":
    unittest.main()
