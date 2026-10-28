"""Tests for the reasoning-indicator benchmark and its diagnostic report."""
import unittest

from reasoning_indicator_benchmark import CASES, CATEGORIES, run_benchmark


class ReasoningIndicatorBenchmarkTests(unittest.TestCase):
    def test_case_ids_are_unique_and_expected_categories_are_valid(self):
        ids = [case["id"] for case in CASES]
        self.assertEqual(len(ids), len(set(ids)))
        for case in CASES:
            self.assertTrue(set(case["expected_detected"]).issubset(CATEGORIES))

    def test_report_covers_every_case(self):
        report = run_benchmark()
        self.assertEqual(report["total"], len(CASES))
        self.assertEqual(len(report["results"]), len(CASES))
        self.assertEqual(report["passed"] + sum(
            not item["passed"] for item in report["results"]
        ), report["total"])

    def test_error_case_ids_match_reported_errors(self):
        report = run_benchmark()
        for error_type, ids in report["error_case_ids"].items():
            if error_type == "false_positive":
                expected_ids = [item["id"] for item in report["results"] if item["false_positive_categories"]]
            else:
                expected_ids = [item["id"] for item in report["results"] if item["false_negative_categories"]]
            self.assertEqual(ids, expected_ids)

    def test_category_metrics_have_consistent_confusion_counts_and_rates(self):
        report = run_benchmark()
        self.assertEqual(set(report["category_metrics"]), set(CATEGORIES))
        for category, metrics in report["category_metrics"].items():
            confusion_total = sum(metrics[key] for key in (
                "true_positive", "false_positive", "false_negative", "true_negative"
            ))
            self.assertEqual(confusion_total, len(CASES), category)
            self.assertEqual(metrics["evaluated_cases"], len(CASES), category)
            for rate in ("precision", "recall", "f1"):
                value = metrics[rate]
                self.assertTrue(value is None or 0 <= value <= 1, (category, rate, value))

    def test_benchmark_discloses_lexical_limitations(self):
        self.assertTrue(run_benchmark()["limitations"])


if __name__ == "__main__":
    unittest.main()
