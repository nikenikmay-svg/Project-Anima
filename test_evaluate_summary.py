"""Tests for the layered evaluation summary."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluate_summary import build_summary

class EvaluationSummaryTests(unittest.TestCase):
    def test_separates_lexical_results_from_unvalidated_reasoning_quality(self):
        with patch("evaluate_summary.run_criterion_benchmark", return_value={
            "passed": 18, "total": 19, "pass_rate_percent": 95,
            "error_counts": {"correct": 18, "false_positive": 1},
        }), patch("evaluate_summary.run_indicator_benchmark", return_value={
            "passed": 32, "total": 32, "pass_rate_percent": 100,
            "category_metrics": {"evidence": {"f1": 1.0}},
            "error_case_ids": {"false_positive": [], "false_negative": []},
        }):
            report = build_summary()
        layers = report["evaluation_layers"]
        self.assertEqual(layers["criterion_lexical_benchmark"]["pass_rate_percent"], 95)
        self.assertEqual(layers["reasoning_indicator_lexical_benchmark"]["pass_rate_percent"], 100)
        self.assertEqual(layers["human_review_comparison"]["status"], "not_provided")
        self.assertEqual(layers["reasoning_quality_validation"]["status"], "not_established")

    def test_optional_reviewer_comparison_is_separate_and_labeled_raw(self):
        fields = ["case_id", "contextual_evidence", "contextual_reasoning",
                  "contextual_uncertainty", "evidence_support", "inference_quality", "confidence"]
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.csv", Path(tmp) / "b.csv"
            for path, label in ((a, "present"), (b, "absent")):
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=fields)
                    writer.writeheader()
                    writer.writerow({"case_id": "one", "contextual_evidence": label})
            with patch("evaluate_summary.run_criterion_benchmark", return_value={
                "passed": 1, "total": 1, "pass_rate_percent": 100, "error_counts": {},
            }), patch("evaluate_summary.run_indicator_benchmark", return_value={
                "passed": 1, "total": 1, "pass_rate_percent": 100,
                "category_metrics": {}, "error_case_ids": {},
            }):
                report = build_summary(str(a), str(b))
        layers = report["evaluation_layers"]
        self.assertEqual(layers["human_review_comparison"]["status"], "comparison_generated")
        metric = layers["human_review_comparison"]["report"]["field_metrics"]["contextual_evidence"]
        self.assertEqual(metric["raw_agreement"], 0.0)
        self.assertIn("not chance-corrected", layers["human_review_comparison"]["meaning"])
        self.assertEqual(layers["reasoning_quality_validation"]["status"], "not_established")

    def test_requires_both_reviewer_files(self):
        with self.assertRaisesRegex(ValueError, "provide both"):
            build_summary("reviewer.csv", None)

if __name__ == "__main__":
    unittest.main()
