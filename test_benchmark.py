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


if __name__ == "__main__":
    unittest.main()
