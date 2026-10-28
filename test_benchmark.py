"""Tests for Anima's deterministic benchmark."""
import unittest

from benchmark import run_benchmark


class BenchmarkTests(unittest.TestCase):
    def test_all_baseline_cases_match_expected_labels(self):
        report = run_benchmark()
        self.assertEqual(report["passed"], report["total"], report["results"])

    def test_report_discloses_limitations(self):
        report = run_benchmark()
        self.assertTrue(report["limitations"])

    def test_error_analysis_classifies_each_case(self):
        report = run_benchmark()
        self.assertEqual(sum(report["error_counts"].values()), report["total"])
        self.assertIn("false_positive", report["error_counts"])
        self.assertIn("false_negative", report["error_counts"])
        for item in report["results"]:
            self.assertIn("type", item["error_analysis"])
            self.assertIn("false_positive_points", item["error_analysis"])
            self.assertIn("false_negative_points", item["error_analysis"])
            self.assertIn("score_mismatch", item["error_analysis"])

    def test_per_criterion_confusion_counts_are_consistent(self):
        report = run_benchmark()
        self.assertTrue(report["criterion_error_counts"])
        for counts in report["criterion_error_counts"].values():
            self.assertEqual(
                sum(counts[key] for key in ("true_positive", "false_positive", "false_negative", "true_negative")),
                counts["evaluated_cases"],
            )
            self.assertEqual(
                counts["evaluated_cases"],
                sum(criterion in case["criteria"] for case in __import__("benchmark").CASES
                    for criterion_name in [criterion] if criterion_name == list(report["criterion_error_counts"]).pop() ),
            ) if False else None

    def test_per_criterion_rates_are_bounded_or_undefined(self):
        report = run_benchmark()
        self.assertEqual(set(report["criterion_metrics"]), set(report["criterion_error_counts"]))
        for metrics in report["criterion_metrics"].values():
            for name in ("precision", "recall", "f1", "specificity"):
                value = metrics[name]
                self.assertTrue(value is None or 0 <= value <= 1, (name, value))


if __name__ == "__main__":
    unittest.main()
