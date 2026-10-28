"""Tests for the experiment ledger validator."""
import unittest

from experiment_ledger import validate_ledger, render_markdown


def valid_record():
    return {
        "experiment_id": "exp-001",
        "hypothesis": "A narrower clause boundary rule may reduce false positives.",
        "target_case_ids": ["case-1"],
        "baseline_report": "baseline-results.json",
        "candidate_report": "candidate-results.json",
        "test_summary": "Unit tests passed; benchmark gate passed.",
        "gate_passed": True,
        "reviewer_decision": {
            "status": "proposed",
            "reviewed_by": "pending",
            "rationale": "Awaiting independent review.",
            "human_verified": False,
        },
    }


class ExperimentLedgerTests(unittest.TestCase):
    def test_accepts_valid_record(self):
        self.assertEqual(len(validate_ledger([valid_record()])), 1)

    def test_accepted_requires_human_verification(self):
        record = valid_record()
        record["reviewer_decision"].update({
            "status": "accepted",
            "reviewed_by": "reviewer",
            "rationale": "Reviewed test evidence.",
            "human_verified": False,
        })
        with self.assertRaisesRegex(ValueError, "human_verified=true"):
            validate_ledger([record])

    def test_accepts_human_verified_decision(self):
        record = valid_record()
        record["reviewer_decision"].update({
            "status": "accepted",
            "reviewed_by": "reviewer",
            "rationale": "Reviewed test evidence.",
            "human_verified": True,
        })
        self.assertEqual(len(validate_ledger([record])), 1)

    def test_rejects_duplicate_experiment_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicate experiment_id"):
            validate_ledger([valid_record(), valid_record()])

    def test_rejects_duplicate_target_case_ids(self):
        record = valid_record()
        record["target_case_ids"] = ["case-1", "case-1"]
        with self.assertRaisesRegex(ValueError, "target_case_ids must be unique"):
            validate_ledger([record])

    def test_rejects_missing_fields(self):
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            validate_ledger([{"experiment_id": "exp-001"}])

    def test_markdown_mentions_human_review(self):
        rendered = render_markdown([valid_record()])
        self.assertIn("pending", rendered)
        self.assertIn("traceability aid", rendered)


if __name__ == "__main__":
    unittest.main()
