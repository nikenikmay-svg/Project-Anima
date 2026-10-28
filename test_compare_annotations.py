"""Regression tests for independent reviewer annotation comparison."""
import csv
import tempfile
import unittest
from pathlib import Path

from compare_annotations import compare_annotations

FIELDS = [
    "case_id", "contextual_evidence", "contextual_reasoning",
    "contextual_uncertainty", "evidence_support", "inference_quality", "confidence",
]

class CompareAnnotationsTests(unittest.TestCase):
    def write_csv(self, path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def test_reports_raw_agreement_and_preserves_disagreements(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            self.write_csv(a, [
                {"case_id": "one", "contextual_evidence": "present", "confidence": "high"},
                {"case_id": "two", "contextual_evidence": "absent", "confidence": "medium"},
            ])
            self.write_csv(b, [
                {"case_id": "one", "contextual_evidence": "present", "confidence": "high"},
                {"case_id": "two", "contextual_evidence": "ambiguous", "confidence": "low"},
            ])
            report = compare_annotations(a, b)
            evidence = report["field_metrics"]["contextual_evidence"]
            self.assertEqual(evidence["compared_cases"], 2)
            self.assertEqual(evidence["agreements"], 1)
            self.assertEqual(evidence["disagreements"], 1)
            self.assertEqual(evidence["raw_agreement"], 0.5)
            self.assertEqual(len(report["disagreements"]), 2)
            self.assertTrue(any("chance-corrected" in item for item in report["limitations"]))

    def test_blank_values_are_excluded_not_treated_as_agreement(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            self.write_csv(a, [{"case_id": "one", "contextual_evidence": ""}])
            self.write_csv(b, [{"case_id": "one", "contextual_evidence": "present"}])
            metric = compare_annotations(a, b)["field_metrics"]["contextual_evidence"]
            self.assertEqual(metric["compared_cases"], 0)
            self.assertEqual(metric["missing_from_at_least_one_reviewer"], 1)
            self.assertIsNone(metric["raw_agreement"])

    def test_missing_annotation_report_identifies_case_field_and_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            self.write_csv(a, [{"case_id": "one", "contextual_evidence": ""}])
            self.write_csv(b, [{"case_id": "one", "contextual_evidence": "present"}])
            report = compare_annotations(a, b)
            self.assertIn({
                "case_id": "one",
                "field": "contextual_evidence",
                "reviewer_a_missing": True,
                "reviewer_b_missing": False,
            }, report["missing_annotations"])

    def test_missing_value_counts_are_reported_per_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            self.write_csv(a, [{"case_id": "one", "contextual_evidence": ""}])
            self.write_csv(b, [{"case_id": "one", "contextual_evidence": "present", "confidence": ""}])
            counts = compare_annotations(a, b)["missing_value_counts"]
            self.assertEqual(counts["reviewer_a"], 6)
            self.assertEqual(counts["reviewer_b"], 5)
            self.assertEqual(counts["total_missing_values"], 11)
            self.assertEqual(counts["possible_values"], 12)

    def test_mismatched_case_ids_raise_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            self.write_csv(a, [{"case_id": "one"}])
            self.write_csv(b, [{"case_id": "two"}])
            with self.assertRaisesRegex(ValueError, "case IDs differ"):
                compare_annotations(a, b)

    def test_missing_required_annotation_columns_raise_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            for path in (a, b):
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["case_id", "confidence"])
                    writer.writeheader()
                    writer.writerow({"case_id": "one", "confidence": "high"})
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                compare_annotations(a, b)

    def test_invalid_annotation_value_raises_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            self.write_csv(a, [{"case_id": "one", "contextual_evidence": "probably"}])
            self.write_csv(b, [{"case_id": "one", "contextual_evidence": "present"}])
            with self.assertRaisesRegex(ValueError, "invalid contextual_evidence value"):
                compare_annotations(a, b)

    def test_allowed_values_and_blank_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            self.write_csv(a, [{"case_id": "one", "contextual_evidence": "", "evidence_support": "not_applicable"}])
            self.write_csv(b, [{"case_id": "one", "contextual_evidence": "", "evidence_support": "not_applicable"}])
            report = compare_annotations(a, b)
            self.assertEqual(report["field_metrics"]["evidence_support"]["raw_agreement"], 1.0)
            self.assertIsNone(report["field_metrics"]["contextual_evidence"]["raw_agreement"])

    def test_duplicate_column_names_raise_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            header = ",".join(FIELDS + ["confidence"]) + chr(10)
            for path in (a, b):
                path.write_text(header, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate column names"):
                compare_annotations(a, b)

    def test_blank_column_name_raises_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            header = ",".join(FIELDS) + "," + chr(10)
            for path in (a, b):
                path.write_text(header, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "blank column name"):
                compare_annotations(a, b)

    def test_duplicate_case_ids_raise_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.csv"
            b = Path(tmp) / "b.csv"
            self.write_csv(a, [{"case_id": "one"}, {"case_id": "one"}])
            self.write_csv(b, [{"case_id": "one"}])
            with self.assertRaisesRegex(ValueError, "duplicate case_id"):
                compare_annotations(a, b)

if __name__ == "__main__":
    unittest.main()
