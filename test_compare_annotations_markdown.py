"""Tests for the reviewer comparison Markdown renderer."""
import csv
import tempfile
import unittest
from pathlib import Path

from compare_annotations import compare_annotations
from compare_annotations_markdown import render_comparison_markdown

FIELDS = [
    "case_id", "contextual_evidence", "contextual_reasoning",
    "contextual_uncertainty", "evidence_support", "inference_quality", "confidence",
]


class CompareAnnotationsMarkdownTests(unittest.TestCase):
    def test_report_includes_overview_disagreements_missingness_and_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            rows_a = [
                {"case_id": "case|one", "contextual_evidence": "present"},
                {"case_id": "two", "contextual_evidence": ""},
            ]
            rows_b = [
                {"case_id": "case|one", "contextual_evidence": "absent"},
                {"case_id": "two", "contextual_evidence": "present"},
            ]
            for path, rows in ((a, rows_a), (b, rows_b)):
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=FIELDS)
                    writer.writeheader()
                    writer.writerows(rows)

            rendered = render_comparison_markdown(compare_annotations(a, b))
            self.assertIn("# Reviewer Worksheet Comparison", rendered)
            self.assertIn("## Field-by-field metrics", rendered)
            self.assertIn("## Disagreements requiring human review", rendered)
            self.assertIn("## Missing annotations", rendered)
            self.assertIn("Raw agreement", rendered)
            self.assertIn("not chance-corrected inter-rater reliability", rendered)
            self.assertIn("case\\|one", rendered)
            self.assertIn("semantic reasoning quality", rendered)

    def test_empty_metrics_render_as_na(self):
        report = {
            "worksheet_comparison_overview": {
                "fields_compared": 1, "completed_pairs_compared": 0,
                "agreements": 0, "disagreements_requiring_human_review": 0,
                "missing_pairs": 1, "raw_agreement": None,
            },
            "total_case_ids": 1,
            "field_metrics": {"confidence": {
                "compared_cases": 0, "agreements": 0, "disagreements": 0,
                "missing_from_at_least_one_reviewer": 1, "raw_agreement": None,
            }},
            "disagreements": [],
            "missing_annotations": [],
            "missing_value_counts": {"reviewer_a": 1, "reviewer_b": 0},
            "limitations": ["Test limitation."],
        }
        rendered = render_comparison_markdown(report)
        self.assertIn("Raw agreement: N/A", rendered)
        self.assertIn("No disagreements among nonblank paired labels.", rendered)
        self.assertIn("No missing annotations.", rendered)


if __name__ == "__main__":
    unittest.main()
