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

    def test_ignores_malformed_evidence_values_safely(self):
        report = review_argument(self.argument, {"1": "not a list", "2": ["", None, "Evidence B"]})
        self.assertEqual(report["premise_evidence"][0]["evidence_items"], [])
        self.assertEqual(report["premise_evidence"][1]["evidence_items"], ["Evidence B"])

    def test_does_not_invent_assumptions_or_counterexamples(self):
        report = review_argument(self.argument)
        self.assertEqual(report["unstated_assumptions"], [])
        self.assertEqual(report["counterexamples"], [])
        self.assertEqual(report["conclusion_evidence_status"], "not_assessed")


if __name__ == "__main__":
    unittest.main()
