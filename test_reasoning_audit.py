"""Tests for the lexical claim-audit prototype."""
import json
import tempfile
import unittest
from pathlib import Path

from reasoning_audit import audit_claim
from reasoning_audit_benchmark import run_benchmark


class ReasoningAuditTests(unittest.TestCase):
    def test_flags_causal_and_generalization_language(self):
        result = audit_claim("A study ran.", "The study caused improvement for everyone.", "No comparison group.")
        self.assertEqual(
            {item["rule"] for item in result["review_flags"]},
            {"causal_language", "broad_generalization"},
        )

    def test_leaves_semantic_validity_unassessed(self):
        result = audit_claim("Prompt", "The result may be meaningful.", "Small sample.")
        self.assertEqual(result["semantic_assessment"]["evidence_support"], "not_assessed")
        self.assertEqual(result["semantic_assessment"]["inference_validity"], "not_assessed")
        self.assertIn("not a verdict", result["notice"])

    def test_rejects_bad_input_and_empty_claim(self):
        with self.assertRaises(TypeError):
            audit_claim(None, "claim")
        with self.assertRaises(ValueError):
            audit_claim("", "  ")

    def test_smoke_cases_match_rule_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_benchmark(Path(tmp) / "report.json")
        self.assertEqual(report["passed"], report["total"])
        self.assertEqual(report["semantic_validation"], "not_established")
        self.assertTrue(all(
            result["semantic_assessment"]["inference_validity"] == "not_assessed"
            for result in report["results"]
        ))

    def test_case_schema_and_unique_ids(self):
        path = Path(__file__).with_name("reasoning_audit_cases.json")
        cases = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 10)
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        for case in cases:
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["claim"].strip())
            self.assertTrue(case["context"].strip())
            self.assertEqual(case["expected_review_flags"], sorted(set(case["expected_review_flags"])))


if __name__ == "__main__":
    unittest.main()
