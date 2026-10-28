"""Tests for the reviewer-friendly CSV annotation worksheet."""
import csv
import unittest
from pathlib import Path

class AnnotationWorksheetTests(unittest.TestCase):
    def test_worksheet_has_all_review_cases_and_blank_annotation_fields(self):
        root = Path(__file__).parent
        with (root / "reasoning_indicator_review_cases.json").open(encoding="utf-8") as handle:
            cases = __import__("json").load(handle)
        with (root / "reasoning_indicator_annotation_template.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["case_id"] for row in rows], [case["id"] for case in cases])
        self.assertEqual(len(rows), len(cases))
        required_columns = {
            "reviewer_id", "review_date", "lexical_output_observed",
            "contextual_evidence", "contextual_reasoning", "contextual_uncertainty",
            "evidence_support", "evidence_quote", "inference_quality",
            "inference_rationale", "rationale", "confidence", "adjudication_status",
        }
        self.assertTrue(required_columns.issubset(rows[0]))
        for row, case in zip(rows, cases):
            self.assertEqual(row["answer"], case["answer"])
            self.assertEqual(row["review_focus"], case["review_focus"])
            self.assertEqual(row["lexical_expected_detected"], ",".join(case["lexical_expected_detected"]) or "none")
            for column in required_columns:
                self.assertEqual(row[column], "", f"{row['case_id']}:{column}")

    def test_worksheet_does_not_present_unreviewed_labels_as_human_annotations(self):
        path = Path(__file__).with_name("reasoning_indicator_annotation_template.csv")
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(all(row["reviewer_id"] == "" for row in rows))
        self.assertTrue(all(row["adjudication_status"] == "" for row in rows))

if __name__ == "__main__":
    unittest.main()
