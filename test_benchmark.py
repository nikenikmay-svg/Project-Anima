"""Tests for Anima's deterministic benchmark."""
import unittest

from benchmark import CASES, run_benchmark


class BenchmarkTests(unittest.TestCase):
    def test_all_baseline_cases_match_expected_labels(self):
        report = run_benchmark()
        self.assertEqual(report["passed"], report["total"], report["results"])

    def test_report_discloses_limitations(self):
        report = run_benchmark()
        self.assertTrue(report["limitations"])

    def test_benchmark_covers_input_and_phrase_edge_cases(self):
        case_ids = {case["id"] for case in CASES}
        self.assertGreaterEqual(len(CASES), 19)
        self.assertTrue({
            "multiword_criterion_phrase",
            "duplicate_criterion_is_counted_once",
            "empty_criteria_list",
            "without_marker_flags_criterion",
        }.issubset(case_ids))

    def test_case_ids_are_unique_and_categories_are_known(self):
        case_ids = [case["id"] for case in CASES]
        self.assertEqual(len(case_ids), len(set(case_ids)), "benchmark case IDs must be unique")
        allowed_categories = {
            "baseline",
            "negation",
            "phrase_matching",
            "input_edges",
            "context",
            "clause_scope",
            "repeated_mentions",
        }
        self.assertTrue(all(case.get("category") in allowed_categories for case in CASES))

    def test_category_metrics_cover_every_case(self):
        report = run_benchmark()
        self.assertTrue(all(case.get("category") for case in CASES))
        self.assertEqual(
            sum(item["total"] for item in report["category_metrics"].values()),
            report["total"],
        )
        self.assertEqual(
            set(report["category_metrics"]),
            {case["category"] for case in CASES},
        )
        for metrics in report["category_metrics"].values():
            self.assertEqual(metrics["passed"] + sum(
                metrics["error_counts"][kind]
                for kind in ("false_positive", "false_negative", "mixed_contradiction_errors", "score_mismatch")
            ), metrics["total"])
            self.assertEqual(
                sum(len(ids) for ids in metrics["case_ids_by_error_type"].values()),
                metrics["total"],
            )
            for kind, ids in metrics["case_ids_by_error_type"].items():
                self.assertEqual(len(ids), metrics["error_counts"][kind])

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
        for criterion, counts in report["criterion_error_counts"].items():
            confusion_total = sum(
                counts[key]
                for key in ("true_positive", "false_positive", "false_negative", "true_negative")
            )
            self.assertEqual(confusion_total, counts["evaluated_cases"])
            expected_cases = sum(criterion in case["criteria"] for case in CASES)
            self.assertEqual(counts["evaluated_cases"], expected_cases)

    def test_per_criterion_rates_are_bounded_or_undefined(self):
        report = run_benchmark()
        self.assertEqual(set(report["criterion_metrics"]), set(report["criterion_error_counts"]))
        for metrics in report["criterion_metrics"].values():
            for name in ("precision", "recall", "f1", "specificity"):
                value = metrics[name]
                self.assertTrue(value is None or 0 <= value <= 1, (name, value))


if __name__ == "__main__":
    unittest.main()
