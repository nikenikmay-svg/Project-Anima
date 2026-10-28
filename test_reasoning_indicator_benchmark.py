"""Tests for the reasoning-indicator benchmark and its diagnostic report."""
import json
import unittest
from pathlib import Path

from reasoning import analyze_reasoning_indicators

from reasoning_indicator_benchmark import CASES, CATEGORIES, run_benchmark


class ReasoningIndicatorBenchmarkTests(unittest.TestCase):
    def test_case_ids_are_unique_and_expected_categories_are_valid(self):
        ids = [case["id"] for case in CASES]
        self.assertEqual(len(ids), len(set(ids)))
        for case in CASES:
            self.assertTrue(set(case["expected_detected"]).issubset(CATEGORIES))
            self.assertIsInstance(case.get("label_rationale"), str)
            self.assertTrue(case["label_rationale"].strip(), case["id"])

    def test_dataset_has_diverse_regression_examples(self):
        self.assertGreaterEqual(len(CASES), 30)
        answers = {case["answer"] for case in CASES}
        self.assertEqual(len(answers), len(CASES))
        for category in CATEGORIES:
            self.assertTrue(
                any(category in case["expected_detected"] for case in CASES),
                f"no positive examples for {category}",
            )
            self.assertTrue(
                any(category not in case["expected_detected"] for case in CASES),
                f"no negative examples for {category}",
            )

    def test_report_covers_every_case(self):
        report = run_benchmark()
        self.assertEqual(report["total"], len(CASES))
        self.assertEqual(len(report["results"]), len(CASES))
        self.assertEqual(report["passed"] + sum(
            not item["passed"] for item in report["results"]
        ), report["total"])

    def test_error_case_ids_match_reported_errors(self):
        report = run_benchmark()
        for error_type, ids in report["error_case_ids"].items():
            if error_type == "false_positive":
                expected_ids = [item["id"] for item in report["results"] if item["false_positive_categories"]]
            else:
                expected_ids = [item["id"] for item in report["results"] if item["false_negative_categories"]]
            self.assertEqual(ids, expected_ids)

    def test_category_metrics_have_consistent_confusion_counts_and_rates(self):
        report = run_benchmark()
        self.assertEqual(set(report["category_metrics"]), set(CATEGORIES))
        for category, metrics in report["category_metrics"].items():
            confusion_total = sum(metrics[key] for key in (
                "true_positive", "false_positive", "false_negative", "true_negative"
            ))
            self.assertEqual(confusion_total, len(CASES), category)
            self.assertEqual(metrics["evaluated_cases"], len(CASES), category)
            for rate in ("precision", "recall", "f1"):
                value = metrics[rate]
                self.assertTrue(value is None or 0 <= value <= 1, (category, rate, value))

    def test_benchmark_discloses_lexical_limitations(self):
        self.assertTrue(run_benchmark()["limitations"])

    def test_all_expanded_cases_match_expected_lexical_labels(self):
        report = run_benchmark()
        self.assertEqual(report["passed"], report["total"], report["results"])


    def test_review_set_has_explicit_questions_and_pending_status(self):
        review_path = Path(__file__).with_name("reasoning_indicator_review_cases.json")
        cases = json.loads(review_path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 8)
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        valid_focuses = {"negation", "context", "ambiguous_modal", "ambiguous_connector",
                         "invalid_inference", "ambiguous_term", "implicit_reasoning",
                         "ambiguous_context"}
        for case in cases:
            self.assertTrue(case["answer"].strip(), case["id"])
            self.assertTrue(case["review_question"].strip(), case["id"])
            self.assertTrue(case["interpretation_note"].strip(), case["id"])
            self.assertEqual(case["review_status"], "pending_human_review", case["id"])
            self.assertIn(case["review_focus"], valid_focuses, case["id"])
            self.assertTrue(set(case["lexical_expected_detected"]).issubset(CATEGORIES))
            actual = analyze_reasoning_indicators(case["answer"])["detected_categories"]
            self.assertEqual(actual, case["lexical_expected_detected"], case["id"])

    def test_review_set_covers_negation_context_and_ambiguity(self):
        review_path = Path(__file__).with_name("reasoning_indicator_review_cases.json")
        cases = json.loads(review_path.read_text(encoding="utf-8"))
        focuses = {case["review_focus"] for case in cases}
        self.assertIn("negation", focuses)
        self.assertIn("context", focuses)
        self.assertTrue(any(focus.startswith("ambiguous") for focus in focuses))

    def test_human_review_protocol_separates_evaluation_questions(self):
        protocol_path = Path(__file__).with_name("HUMAN_REVIEW_PROTOCOL.md")
        protocol = protocol_path.read_text(encoding="utf-8")
        for required_phrase in ("Lexical detection", "Contextual interpretation",
                                "Reasoning quality", "reviewer_id",
                                "adjudication_status", "pending_human_review"):
            self.assertIn(required_phrase, protocol)
        self.assertIn("At least two reviewers", protocol)
        self.assertIn("No human review", protocol)

if __name__ == "__main__":
    unittest.main()
