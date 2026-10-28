"""Tests for evidence mapping and counterexample review scaffolding."""
import unittest

from argument_review import review_argument


class ArgumentReviewTests(unittest.TestCase):
    def setUp(self):
        self.argument = {
            "id": "arg-1",
            "premises": ["All mammals are animals.", "Whales are mammals."],
            "conclusion": "Whales are animals.",
        }

    def test_records_supplied_evidence_without_claiming_support(self):
        report = review_argument(self.argument, {"1": ["Source A, section 2"]})
        self.assertEqual(len(report["premise_evidence"]), 2)
        self.assertTrue(report["premise_evidence"][0]["evidence_supplied"])
        self.assertFalse(report["premise_evidence"][1]["evidence_supplied"])
        self.assertEqual(report["premise_evidence"][0]["support_assessment"], "not_assessed")
        self.assertEqual(report["inference_quality"], "not_assessed")
        self.assertEqual(report["input_warnings"], [])

    def test_records_assumptions_and_counterexamples_as_supplied(self):
        report = review_argument(
            self.argument,
            unstated_assumptions=["The category definitions are used consistently."],
            counterexamples=["Check whether the premise definitions admit an exception."],
        )
        self.assertEqual(len(report["unstated_assumptions"]), 1)
        self.assertEqual(len(report["counterexamples"]), 1)
        self.assertEqual(report["review_status"], "pending_human_review")

    def test_invalid_argument_does_not_generate_review_content(self):
        report = review_argument({"id": "bad", "premises": [], "conclusion": ""})
        self.assertEqual(report["report_status"], "invalid_argument_structure")
        self.assertEqual(report["premise_evidence"], [])
        self.assertEqual(report["inference_quality"], "not_assessed")

    def test_malformed_evidence_values_are_reported(self):
        report = review_argument(self.argument, {"1": "not a list", "2": ["", None, "Evidence B"]})
        self.assertEqual(report["premise_evidence"][0]["evidence_items"], [])
        self.assertEqual(report["premise_evidence"][1]["evidence_items"], ["Evidence B"])
        self.assertEqual(len(report["input_warnings"]), 3)
        self.assertIn("must be a list", report["input_warnings"][0])
        self.assertTrue(any("empty or non-text" in warning for warning in report["input_warnings"]))

    def test_unknown_and_malformed_evidence_keys_are_reported(self):
        report = review_argument(self.argument, {"1": ["Source A"], "3": ["Orphan source"], 2: ["Numeric key"]})
        self.assertEqual(report["premise_evidence"][0]["evidence_items"], ["Source A"])
        self.assertEqual(report["premise_evidence"][1]["evidence_items"], [])
        self.assertEqual(len(report["input_warnings"]), 2)
        self.assertTrue(any("does not match" in warning for warning in report["input_warnings"]))

    def test_wrong_top_level_input_and_optional_fields_are_reported(self):
        report = review_argument(
            self.argument,
            evidence_by_premise=["not", "an", "object"],
            unstated_assumptions="not a list",
            counterexamples={"wrong": "shape"},
        )
        self.assertEqual(len(report["input_warnings"]), 3)
        self.assertEqual(report["unstated_assumptions"], [])
        self.assertEqual(report["counterexamples"], [])

    def test_does_not_invent_assumptions_or_counterexamples(self):
        report = review_argument(self.argument)
        self.assertEqual(report["unstated_assumptions"], [])
        self.assertEqual(report["counterexamples"], [])
        self.assertEqual(report["conclusion_evidence_status"], "not_assessed")


if __name__ == "__main__":
    unittest.main()
