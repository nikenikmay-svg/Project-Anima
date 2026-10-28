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


if __name__ == "__main__":
    unittest.main()
