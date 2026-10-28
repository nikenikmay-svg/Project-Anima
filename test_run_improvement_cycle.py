"""Tests for the integrated improvement cycle."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experience_store import read_records
from run_improvement_cycle import run_cycle, resolve_candidate_inputs


class ImprovementCycleTests(unittest.TestCase):
    def test_queue_selects_top_candidate_inputs(self):
        queue = {"candidates": [
            {"case_id": "case-top", "hypothesis": "Test the highest-ranked case"},
            {"case_id": "case-next", "hypothesis": "Another hypothesis"},
        ]}
        hypothesis, case_ids = resolve_candidate_inputs(queue)
        self.assertEqual(hypothesis, "Test the highest-ranked case")
        self.assertEqual(case_ids, ["case-top"])

    def test_explicit_inputs_override_queue_defaults(self):
        queue = {"candidates": [{"case_id": "case-top", "hypothesis": "Queue hypothesis"}]}
        hypothesis, case_ids = resolve_candidate_inputs(queue, "My hypothesis", ["manual-case"])
        self.assertEqual(hypothesis, "My hypothesis")
        self.assertEqual(case_ids, ["manual-case"])

    def test_empty_queue_requires_manual_inputs(self):
        with self.assertRaisesRegex(ValueError, "candidate queue is empty"):
            resolve_candidate_inputs({"candidates": []})
        with self.assertRaisesRegex(ValueError, "provide --hypothesis"):
            resolve_candidate_inputs(None)

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
            self.assertIsNone(result["memory_record_id"])

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

    def test_memory_store_records_gate_outcome_as_unreviewed_observation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps({"results": [{"id": "case-1", "passed": True}]}), encoding="utf-8")
            memory_path = root / "memory.jsonl"
            with patch("run_improvement_cycle.run_experiment", return_value={
                "gate_passed": True, "status": "completed",
                "execution": {"exit_code": 0, "timed_out": False},
            }):
                result = run_cycle(
                    baseline, "exp-memory-1", "A focused change may fix case-1",
                    ["case-1"], "python benchmark.py", root / "out",
                    memory_store=memory_path,
                )
            records = read_records(memory_path)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["id"], "experiment-exp-memory-1")
            self.assertEqual(records[0]["record_type"], "experiment")
            self.assertEqual(records[0]["outcome"], "observed")
            self.assertEqual(records[0]["review_status"], "unreviewed")
            self.assertEqual(records[0]["confidence"], "low")
            self.assertIn("gate-passed", records[0]["tags"])
            self.assertEqual(result["memory_record_id"], records[0]["id"])

    def test_memory_store_duplicate_experiment_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps({"results": [{"id": "case-1", "passed": True}]}), encoding="utf-8")
            memory_path = root / "memory.jsonl"
            with patch("run_improvement_cycle.run_experiment", return_value={
                "gate_passed": True, "status": "completed",
                "execution": {"exit_code": 0, "timed_out": False},
            }):
                run_cycle(baseline, "exp-memory-2", "Hypothesis", ["case-1"],
                          "python benchmark.py", root / "out", memory_store=memory_path)
                with self.assertRaisesRegex(ValueError, "already exists"):
                    run_cycle(baseline, "exp-memory-2", "Hypothesis", ["case-1"],
                              "python benchmark.py", root / "out-2", memory_store=memory_path)

    def test_memory_records_failed_gate_without_calling_it_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps({"results": [{"id": "case-1", "passed": True}]}), encoding="utf-8")
            memory_path = root / "memory.jsonl"
            with patch("run_improvement_cycle.run_experiment", return_value={
                "gate_passed": False, "status": "completed",
                "execution": {"exit_code": 1, "timed_out": False},
            }):
                run_cycle(baseline, "exp-memory-3", "Hypothesis", ["case-1"],
                          "python benchmark.py", root / "out", memory_store=memory_path)
            record = read_records(memory_path)[0]
            self.assertIn("gate-failed", record["tags"])
            self.assertEqual(record["review_status"], "unreviewed")
            self.assertEqual(record["outcome"], "observed")

if __name__ == "__main__":
    unittest.main()
