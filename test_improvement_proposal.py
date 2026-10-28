"""Tests for the human-reviewable improvement proposal queue."""
import unittest

from improvement_proposal import build_proposals, render_markdown


class ImprovementProposalTests(unittest.TestCase):
    def test_failed_cases_become_reviewable_proposals(self):
        queue = build_proposals({"results": [{
            "id": "case-1",
            "category": "negation",
            "passed": False,
            "expected_score": 100,
            "actual_score": 50,
            "error_analysis": {
                "type": "false_negative",
                "false_positive_points": [],
                "false_negative_points": ["evidence"],
            },
        }]})
        self.assertEqual(queue["proposal_count"], 1)
        proposal = queue["proposals"][0]
        self.assertEqual(proposal["case_id"], "case-1")
        self.assertTrue(proposal["required_human_review"])
        self.assertFalse(proposal["source_code_changed"])
        self.assertEqual(proposal["false_negative_points"], ["evidence"])

    def test_passing_cases_are_not_proposed(self):
        queue = build_proposals({"results": [{"id": "case-1", "passed": True}]})
        self.assertEqual(queue["proposal_count"], 0)
        self.assertEqual(queue["proposals"], [])

    def test_empty_queue_markdown_explains_limitations(self):
        rendered = render_markdown(build_proposals({"results": []}))
        self.assertIn("No failing cases", rendered)
        self.assertIn("does not prove semantic reasoning quality", rendered)

    def test_rejects_duplicate_ids(self):
        row = {"id": "same", "passed": False}
        with self.assertRaisesRegex(ValueError, "duplicate benchmark case ID"):
            build_proposals({"results": [row, row]})

    def test_rejects_invalid_result(self):
        with self.assertRaisesRegex(ValueError, "boolean passed"):
            build_proposals({"results": [{"id": "case-1", "passed": "false"}]})

    def test_discloses_no_automatic_code_changes(self):
        queue = build_proposals({"results": []})
        self.assertTrue(any("No source code" in item for item in queue["limitations"]))


if __name__ == "__main__":
    unittest.main()
