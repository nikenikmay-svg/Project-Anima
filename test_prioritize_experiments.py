"""Tests for deterministic candidate prioritization."""
import unittest

from prioritize_experiments import prioritize_candidates, render_markdown


class PrioritizeExperimentsTests(unittest.TestCase):
    def test_ranks_mixed_errors_above_false_positive(self):
        report = {"results": [
            {"id": "a", "category": "negation", "passed": False,
             "error_analysis": {"type": "false_positive"}},
            {"id": "b", "category": "scope", "passed": False,
             "error_analysis": {"type": "mixed_contradiction_errors"}},
        ]}
        queue = prioritize_candidates(report)
        self.assertEqual(queue["candidates"][0]["case_id"], "b")
        self.assertEqual(queue["candidates"][0]["rank"], 1)

    def test_tie_breaks_are_deterministic(self):
        report = {"results": [
            {"id": "z-case", "category": "negation", "passed": False,
             "error_analysis": {"type": "false_negative"}},
            {"id": "a-case", "category": "negation", "passed": False,
             "error_analysis": {"type": "false_negative"}},
        ]}
        first = prioritize_candidates(report)
        second = prioritize_candidates(report)
        self.assertEqual(first, second)
        self.assertEqual(first["candidates"][0]["case_id"], "a-case")
        self.assertEqual(first["candidates"][0]["category_failure_count"], 2)

    def test_passed_cases_are_excluded_and_limit_applies(self):
        report = {"results": [
            {"id": "pass", "passed": True},
            {"id": "fail1", "passed": False, "error_analysis": {"type": "false_positive"}},
            {"id": "fail2", "passed": False, "error_analysis": {"type": "false_negative"}},
        ]}
        queue = prioritize_candidates(report, limit=1)
        self.assertEqual(queue["candidate_count"], 1)
        self.assertEqual(queue["candidates"][0]["case_id"], "fail1")

    def test_rejects_duplicate_ids_and_invalid_limit(self):
        row = {"id": "dup", "passed": False}
        with self.assertRaisesRegex(ValueError, "duplicate benchmark case ID"):
            prioritize_candidates({"results": [row, row]})
        with self.assertRaisesRegex(ValueError, "limit must be positive"):
            prioritize_candidates({"results": []}, limit=0)

    def test_empty_queue_markdown_explains_limitations(self):
        markdown = render_markdown(prioritize_candidates({"results": []}))
        self.assertIn("No failing cases", markdown)
        self.assertIn("do not establish semantic correctness", markdown)


if __name__ == "__main__":
    unittest.main()
