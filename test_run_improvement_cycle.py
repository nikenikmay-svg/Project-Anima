"""Tests for the integrated improvement cycle."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from run_improvement_cycle import run_cycle


class ImprovementCycleTests(unittest.TestCase):
    def test_cycle_records_tested_but_unapproved_result(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps({"results": [{"id": "case-1", "passed": True}]}), encoding="utf-8")
            fake_report = {
                "gate_passed": True,
                "status": "completed",
                "execution": {"exit_code": 0, "timed_out": False},
            }
            with patch("run_improvement_cycle.run_experiment", return_value=fake_report):
                result = run_cycle(
                    baseline, "exp-123", "Test a narrow change",
                    ["case-1"], "python benchmark.py", root / "out",
                )
            self.assertTrue(result["gate_passed"])
            ledger = json.loads(Path(result["ledger_json"]).read_text(encoding="utf-8"))
            record = ledger[0]
            self.assertEqual(record["reviewer_decision"]["status"], "tested")
            self.assertFalse(record["reviewer_decision"]["human_verified"])
            self.assertEqual(record["target_case_ids"], ["case-1"])

    def test_failed_gate_records_needs_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps({"results": [{"id": "case-1", "passed": True}]}), encoding="utf-8")
            with patch("run_improvement_cycle.run_experiment", return_value={
                "gate_passed": False, "status": "completed",
                "execution": {"exit_code": 1, "timed_out": False},
            }):
                result = run_cycle(
                    baseline, "exp-124", "Test a failing change",
                    ["case-1"], "python benchmark.py", root / "out",
                )
            self.assertFalse(result["gate_passed"])
            ledger = json.loads(Path(result["ledger_json"]).read_text(encoding="utf-8"))
            self.assertEqual(ledger[0]["reviewer_decision"]["status"], "needs_revision")

    def test_writes_both_ledger_formats(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps({"results": [{"id": "case-1", "passed": True}]}), encoding="utf-8")
            with patch("run_improvement_cycle.run_experiment", return_value={
                "gate_passed": True, "status": "completed",
                "execution": {"exit_code": 0, "timed_out": False},
            }):
                result = run_cycle(baseline, "exp-125", "Hypothesis",
                                   ["case-1"], "python benchmark.py", root / "out")
            self.assertTrue(Path(result["ledger_json"]).is_file())
            self.assertTrue(Path(result["ledger_markdown"]).is_file())


if __name__ == "__main__":
    unittest.main()
