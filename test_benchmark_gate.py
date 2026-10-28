"""Tests for the saved-report benchmark regression gate."""
import unittest

from benchmark_gate import compare_reports


def report(*rows):
    return {"results": list(rows)}


def row(case_id, passed, score=50):
    return {"id": case_id, "passed": passed, "actual_score": score}


class BenchmarkGateTests(unittest.TestCase):
    def test_passes_when_outcomes_are_unchanged(self):
        result = compare_reports(report(row("a", True)), report(row("a", True)))
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["delta"]["passed_cases"], 0)

    def test_blocks_pass_to_fail_regression(self):
        result = compare_reports(
            report(row("a", True), row("b", False)),
            report(row("a", False), row("b", True)),
        )
        self.assertFalse(result["gate_passed"])
        self.assertEqual([item["id"] for item in result["regressions"]], ["a"])
        self.assertEqual([item["id"] for item in result["improvements"]], ["b"])

    def test_allows_improvement_without_regression(self):
        result = compare_reports(
            report(row("a", True), row("b", False)),
            report(row("a", True), row("b", True)),
        )
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["candidate"]["passed"], 2)

    def test_reports_actual_score_changes_even_if_pass_state_is_same(self):
        result = compare_reports(report(row("a", True, 40)), report(row("a", True, 70)))
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["actual_score_changes"][0]["delta"], 30)

    def test_rejects_changed_case_set(self):
        with self.assertRaisesRegex(ValueError, "exactly the same case IDs"):
            compare_reports(report(row("a", True)), report(row("b", True)))

    def test_rejects_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicate case ID"):
            compare_reports(report(row("a", True), row("a", False)), report(row("a", True)))

    def test_rejects_empty_or_malformed_results(self):
        with self.assertRaisesRegex(ValueError, "no benchmark results"):
            compare_reports(report(), report(row("a", True)))
        with self.assertRaisesRegex(ValueError, "boolean passed"):
            compare_reports(report({"id": "a", "passed": 1}), report(row("a", True)))

    def test_discloses_limits(self):
        result = compare_reports(report(row("a", True)), report(row("a", True)))
        self.assertTrue(result["limitations"])


if __name__ == "__main__":
    unittest.main()
