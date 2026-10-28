"""Tests for JSON and Markdown review report output."""
import hashlib
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

    def test_cli_writes_json_and_markdown_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.json"
            prefix = Path(temp) / "review-bundle"
            input_path.write_text(json.dumps(self.payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "argument_review_cli.py", str(input_path),
                 "--format", "bundle", "--output", str(prefix)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            json_report = json.loads(Path(str(prefix) + ".json").read_text(encoding="utf-8"))
            markdown_path = Path(str(prefix) + ".md")
            markdown_report = markdown_path.read_text(encoding="utf-8")
            manifest_path = Path(str(prefix) + ".manifest.json")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(json_report["schema_version"], "1.0")
            self.assertIn("# Argument Review Report", markdown_report)
            self.assertIn("not_assessed", markdown_report)
            self.assertEqual(manifest["manifest_version"], "1.0")
            self.assertEqual(manifest["files"][Path(str(prefix) + ".json").name],
                             hashlib.sha256(Path(str(prefix) + ".json").read_bytes()).hexdigest())
            self.assertEqual(manifest["files"][markdown_path.name],
                             hashlib.sha256(markdown_path.read_bytes()).hexdigest())
            self.assertIn("do not validate", manifest["notice"])

    def test_exported_bundle_passes_verifier_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.json"
            prefix = Path(temp) / "review-bundle"
            input_path.write_text(json.dumps(self.payload), encoding="utf-8")
            export_result = subprocess.run(
                [sys.executable, "argument_review_cli.py", str(input_path),
                 "--format", "bundle", "--output", str(prefix)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(export_result.returncode, 0, export_result.stderr)

            verify_command = [sys.executable, "verify_review_bundle.py", str(prefix)]
            verify_result = subprocess.run(
                verify_command, capture_output=True, text=True, check=False,
            )
            self.assertEqual(verify_result.returncode, 0, verify_result.stdout + verify_result.stderr)
            self.assertIn("Integrity check passed", verify_result.stdout)

            Path(str(prefix) + ".md").write_text("# altered after export\\n", encoding="utf-8")
            tampered_result = subprocess.run(
                verify_command, capture_output=True, text=True, check=False,
            )
            self.assertEqual(tampered_result.returncode, 1)
            self.assertIn("hash mismatch", tampered_result.stdout)

    def test_bundle_requires_output_prefix(self):
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.json"
            input_path.write_text(json.dumps(self.payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "argument_review_cli.py", str(input_path), "--format", "bundle"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("--format bundle requires --output", result.stderr)
    def test_strict_input_bundle_writes_both_reports_before_returning_three(self):
        payload = dict(self.payload)
        payload["evidence_by_premise"] = {"9": ["Unmatched item"]}
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.json"
            prefix = Path(temp) / "bundle"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "argument_review_cli.py", str(input_path),
                 "--format", "bundle", "--strict-input", "--output", str(prefix)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 3, result.stderr)
            json_path = Path(str(prefix) + ".json")
            markdown_path = Path(str(prefix) + ".md")
            self.assertTrue(json_path.is_file())
            self.assertTrue(markdown_path.is_file())
            report = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertTrue(report["review"]["input_warnings"])
            self.assertIn("input", markdown_path.read_text(encoding="utf-8").lower())
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
