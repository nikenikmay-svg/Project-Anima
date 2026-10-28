"""Tests for Anima's modular lexical reasoning-indicator checklist."""
import unittest

from reasoning import analyze_reasoning_indicators


class ReasoningIndicatorTests(unittest.TestCase):
    def test_detects_each_category_and_preserves_source_clauses(self):
        answer = (
            "Evidence from the study supports the claim. "
            "Therefore, the conclusion follows. "
            "The estimate may still be uncertain."
        )
        result = analyze_reasoning_indicators(answer)
        self.assertEqual(result["detected_categories"], ["evidence", "reasoning", "uncertainty"])
        self.assertEqual(result["not_detected_categories"], [])
        self.assertEqual(
            result["categories"]["evidence"]["evidence_clauses"],
            ["Evidence from the study supports the claim."],
        )

    def test_reports_categories_without_indicators_as_not_detected(self):
        result = analyze_reasoning_indicators("The sky is blue.")
        self.assertEqual(result["detected_categories"], [])
        self.assertEqual(result["not_detected_categories"], ["evidence", "reasoning", "uncertainty"])

    def test_empty_answer(self):
        result = analyze_reasoning_indicators("  ")
        self.assertEqual(result["detected_categories"], [])
        self.assertEqual(len(result["not_detected_categories"]), 3)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            analyze_reasoning_indicators(None)

    def test_notice_does_not_claim_semantic_validation(self):
        result = analyze_reasoning_indicators("Evidence is irrelevant.")
        self.assertIn("does not establish sound reasoning", result["notice"])


if __name__ == "__main__":
    unittest.main()
