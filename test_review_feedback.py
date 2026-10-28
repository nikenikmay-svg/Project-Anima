"""Regression tests for human-reviewed feedback intake."""
import json
import tempfile
import unittest
from pathlib import Path

from review_feedback import approved_feedback_to_cases, load_feedback


def feedback_item(**overrides):
    item = {
        "id": "human_case_001",
        "answer": "Evidence is absent, but reasoning supports the conclusion.",
        "criteria": ["evidence", "reasoning"],
        "expected_score": 50,
        "expected_contradicted": ["evidence"],
        "category": "human_reviewed",
        "status": "approved",
        "human_verified": True,
        "reviewer_rationale": "The negated evidence criterion should be flagged; reasoning is present.",
    }
    item.update(overrides)
    return item


class ReviewFeedbackTests(unittest.TestCase):
    def test_exports_only_approved_human_verified_cases(self):
        items = [
            feedback_item(),
            feedback_item(id="pending_case", status="pending"),
            feedback_item(id="unverified_case", human_verified=False),
            feedback_item(id="rejected_case", status="rejected"),
        ]
        exported = approved_feedback_to_cases(items)
        self.assertEqual([item["id"] for item in exported], ["human_case_001"])
        self.assertEqual(exported[0]["category"], "human_reviewed")
        self.assertNotIn("reviewer_rationale", exported[0])

    def test_duplicate_baseline_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            approved_feedback_to_cases([feedback_item()], ["human_case_001"])

    def test_loader_rejects_duplicate_feedback_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.json"
            path.write_text(json.dumps([feedback_item(), feedback_item()]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate feedback id"):
                load_feedback(path)

    def test_loader_rejects_invalid_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.json"
            path.write_text(json.dumps([feedback_item(expected_score=101)]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "expected_score"):
                load_feedback(path)

    def test_loader_rejects_contradicted_criterion_not_in_criteria(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.json"
            path.write_text(json.dumps([
                feedback_item(expected_contradicted=["uncertainty"])
            ]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "only requested criteria"):
                load_feedback(path)

    def test_loader_requires_explicit_status_and_rationale(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.json"
            item = feedback_item()
            del item["reviewer_rationale"]
            path.write_text(json.dumps([item]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required fields"):
                load_feedback(path)

    def test_non_list_document_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.json"
            path.write_text(json.dumps({"id": "not-a-list"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON list"):
                load_feedback(path)


if __name__ == "__main__":
    unittest.main()
