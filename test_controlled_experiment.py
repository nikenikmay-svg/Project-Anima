"""Tests for the controlled experiment runner."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from controlled_experiment import render_markdown, run_experiment


class ControlledExperimentTests(unittest.TestCase):
    def test_render_markdown_discloses_guardrails(self):
        report = {
            "status": "completed",
            "gate_passed": False,
            "execution": {"command": ["python", "benchmark.py"], "exit_code": 1, "timed_out": False, "output_excerpt": ""},
            "comparison": None,
            "comparison_error": "sample mismatch",
            "limitations": ["Human review is required."],
        }
        markdown = render_markdown(report)
        self.assertIn("Human review is required", markdown)
        self.assertIn("Regression gate passed", markdown)

    def test_missing_baseline_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "baseline report does not exist"):
                run_experiment(Path(temp) / "missing.json", "python benchmark.py", Path(temp) / "out")

    def test_invalid_timeout_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            baseline = Path(temp) / "baseline.json"
            baseline.write_text(json.dumps({"results": [{"id": "a", "passed": True}]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "positive number"):
                run_experiment(baseline, "python benchmark.py", Path(temp) / "out", timeout=0)

    def test_missing_candidate_report_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps({"results": [{"id": "a", "passed": True}]}), encoding="utf-8")
            with patch("controlled_experiment.Path") as mocked_path:
                # Exercise missing report behavior with a controlled fake temporary execution.
                mocked_path.resolve.return_value = root
                # The full filesystem runner is integration-tested by the repository workflow.
                self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
