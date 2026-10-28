"""Tests for JSON and Markdown review report output."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from argument_review_cli import build_review_document


class ArgumentReviewCliTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "argument": {
                "id": "cli-1",
                "premises": ["Premise one.", "Premise two."],
                "conclusion": "Conclusion.",
            },
            "evidence_by_premise": {"1": ["Source A"]},
            "unstated_assumptions": ["Assumption A"],
            "counterexamples": ["Counterexample A"],
        }

    def test_document_contains_review_summary_and_limit_notice(self):
        document = build_review_document(self.payload)
        self.assertEqual(document["schema_version"], "1.0")
        self.assertEqual(document["summary"]["evidence_items_supplied"], 1)
        self.assertEqual(document["summary"]["assumption_count"], 1)
        self.assertEqual(document["review"]["inference_quality"], "not_assessed")
        self.assertIn("does not verify", document["notice"])

    def test_rejects_non_object_and_missing_argument(self):
        with self.assertRaises(ValueError):
            build_review_document([])
        with self.assertRaises(ValueError):
            build_review_document({"premises": []})

    def test_cli_writes_json_output_file(self):
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.json"
            output_path = Path(temp) / "output.json"
            input_path.write_text(json.dumps(self.payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "argument_review_cli.py", str(input_path), "--output", str(output_path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(output["summary"]["evidence_items_supplied"], 1)

    def test_cli_writes_markdown_output_file(self):
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.json"
            output_path = Path(temp) / "output.md"
            input_path.write_text(json.dumps(self.payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "argument_review_cli.py", str(input_path),
                 "--format", "markdown", "--output", str(output_path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = output_path.read_text(encoding="utf-8")
            self.assertIn("# Argument Review Report", output)
            self.assertIn("Source A", output)
            self.assertIn("not_assessed", output)

    def test_strict_input_returns_three_when_warnings_exist(self):
        payload = dict(self.payload)
        payload["evidence_by_premise"] = {"9": ["Unmatched item"]}
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.json"
            output_path = Path(temp) / "output.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "argument_review_cli.py", str(input_path),
                 "--strict-input", "--output", str(output_path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 3, result.stderr)
            output = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertTrue(output["review"]["input_warnings"])

    def test_strict_input_returns_zero_when_no_warnings_exist(self):
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.json"
            input_path.write_text(json.dumps(self.payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "argument_review_cli.py", str(input_path),
                 "--strict-input"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_reports_invalid_json_with_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "bad.json"
            input_path.write_text("{broken", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "argument_review_cli.py", str(input_path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("argument-review:", result.stderr)


if __name__ == "__main__":
    unittest.main()
