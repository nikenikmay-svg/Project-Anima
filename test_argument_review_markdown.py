"""Tests for readable Markdown review report export."""
import unittest

from argument_review import review_argument
from argument_review_markdown import render_review_markdown
from argument_review_summary import summarize_review


class ArgumentReviewMarkdownTests(unittest.TestCase):
    def setUp(self):
        review = review_argument(
            {
                "id": "markdown-1",
                "premises": ["Premise one.", "Premise two."],
                "conclusion": "Conclusion.",
            },
            evidence_by_premise={"1": ["Source A"]},
            unstated_assumptions=["Assumption A"],
            counterexamples=["Counterexample A"],
        )
        self.document = {
            "schema_version": "1.0",
            "review": review,
            "summary": summarize_review(review),
            "notice": "Supplied material only; no logical validation.",
        }

    def test_renders_key_sections_and_unknown_statuses(self):
        output = render_review_markdown(self.document)
        self.assertIn("# Argument Review Report", output)
        self.assertIn("## Premises and supplied evidence", output)
        self.assertIn("Source A", output)
        self.assertIn("Assumption A", output)
        self.assertIn("Counterexample A", output)
        self.assertIn("not_assessed", output)
        self.assertIn("Human review is required", output)

    def test_empty_lists_are_explicit(self):
        self.document["review"]["unstated_assumptions"] = []
        self.document["review"]["counterexamples"] = []
        output = render_review_markdown(self.document)
        self.assertIn("## Unstated assumptions supplied", output)
        self.assertIn("- None supplied", output)

    def test_rejects_malformed_document(self):
        with self.assertRaises(ValueError):
            render_review_markdown([])
        with self.assertRaises(ValueError):
            render_review_markdown({"review": []})

    def test_does_not_turn_bad_count_into_claim(self):
        self.document["summary"]["evidence_items_supplied"] = -100
        output = render_review_markdown(self.document)
        self.assertIn("Evidence items supplied: 0", output)


if __name__ == "__main__":
    unittest.main()
