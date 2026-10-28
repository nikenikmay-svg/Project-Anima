"""Regression tests for Anima's transparent keyword evaluator."""
import unittest

from anima import evaluate_answer


CRITERIA = ["evidence", "reasoning", "uncertainty"]


class EvaluateAnswerTests(unittest.TestCase):
    def test_all_criteria_without_contradiction_score_100(self):
        result = evaluate_answer(
            "A scientific explanation uses evidence, reasoning, and uncertainty.",
            CRITERIA,
        )
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["matched_points"], CRITERIA)
        self.assertEqual(result["missing_points"], [])
        self.assertEqual(result["contradicted_points"], [])

    def test_missing_criterion_reduces_score(self):
        result = evaluate_answer("Use evidence and careful reasoning.", CRITERIA)
        self.assertEqual(result["score"], 67)
        self.assertEqual(result["missing_points"], ["uncertainty"])

    def test_contradictory_sentence_is_not_counted_as_affirmed(self):
        result = evaluate_answer(
            "Evidence, reasoning, and uncertainty are irrelevant to science.",
            CRITERIA,
        )
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["matched_points"], [])
        self.assertEqual(result["contradicted_points"], CRITERIA)

    def test_simple_not_irrelevant_double_negative_is_not_flagged(self):
        result = evaluate_answer("Evidence is not irrelevant to the conclusion.", ["evidence"])
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["matched_points"], ["evidence"])
        self.assertEqual(result["contradicted_points"], [])

    def test_irrelevant_without_negation_still_flags_criterion(self):
        result = evaluate_answer("Evidence is irrelevant to the conclusion.", ["evidence"])
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["contradicted_points"], ["evidence"])

    def test_other_contradiction_marker_still_flags_double_negative_clause(self):
        result = evaluate_answer(
            "Evidence is not irrelevant, but it is unsupported.",
            ["evidence"],
        )
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["contradicted_points"], ["evidence"])

    def test_phrase_matching_is_case_insensitive(self):
        result = evaluate_answer("EVIDENCE matters.", ["evidence"])
        self.assertEqual(result["score"], 100)

    def test_substring_does_not_count_as_match(self):
        result = evaluate_answer("Partial results are reported.", ["art"])
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["missing_points"], ["art"])

    def test_empty_answer(self):
        result = evaluate_answer("  ", CRITERIA)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["missing_points"], CRITERIA)

    def test_empty_criteria(self):
        result = evaluate_answer("Any answer", [])
        self.assertEqual(result["score"], 0)
        self.assertIn("No evaluation criteria", result["feedback"])

    def test_duplicate_criteria_are_counted_once(self):
        result = evaluate_answer("Evidence supports the claim.", ["evidence", "Evidence"])
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["matched_points"], ["evidence"])

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(TypeError):
            evaluate_answer(None, CRITERIA)
        with self.assertRaises(TypeError):
            evaluate_answer("text", "evidence")
        with self.assertRaises(ValueError):
            evaluate_answer("text", [""])

    def test_result_has_compatible_core_keys(self):
        result = evaluate_answer("Evidence matters.", ["evidence", "reasoning"])
        self.assertTrue({"score", "matched_points", "missing_points", "feedback"} <= set(result))

    def test_negation_in_contrast_clause_does_not_flag_other_criterion(self):
        result = evaluate_answer(
            "There is no evidence for the claim, but reasoning supports the conclusion.",
            ["evidence", "reasoning"],
        )
        self.assertEqual(result["contradicted_points"], ["evidence"])
        self.assertEqual(result["matched_points"], ["reasoning"])
        self.assertEqual(result["score"], 50)

    def test_positive_claim_followed_by_contrastive_uncertainty(self):
        result = evaluate_answer(
            "Evidence supports the claim, however uncertainty remains about timing.",
            ["evidence", "uncertainty"],
        )
        self.assertEqual(result["contradicted_points"], [])
        self.assertEqual(result["matched_points"], ["evidence", "uncertainty"])
        self.assertEqual(result["score"], 100)


    def test_narrow_double_negative_not_irrelevant_is_not_flagged(self):
        result = evaluate_answer("Evidence is not irrelevant to the conclusion.", ["evidence"])
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["matched_points"], ["evidence"])
        self.assertEqual(result["contradicted_points"], [])

    def test_plain_irrelevant_remains_flagged(self):
        result = evaluate_answer("Evidence is irrelevant to the conclusion.", ["evidence"])
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["contradicted_points"], ["evidence"])

    def test_clean_repeated_mention_prevents_automatic_contradiction_flag(self):
        result = evaluate_answer(
            "Evidence is not available yet. Later evidence supports the conclusion.",
            ["evidence"],
        )
        self.assertEqual(result["contradicted_points"], [])
        self.assertEqual(result["matched_points"], ["evidence"])
        self.assertEqual(result["score"], 100)


    def test_criterion_analysis_explains_each_status_with_source_clauses(self):
        result = evaluate_answer(
            "There is no evidence for the claim, but reasoning supports it.",
            ["evidence", "reasoning", "uncertainty"],
        )
        analysis = {item["criterion"]: item for item in result["criterion_analysis"]}
        self.assertEqual(analysis["evidence"]["status"], "contradicted")
        self.assertEqual(analysis["evidence"]["evidence_clauses"], ["There is no evidence for the claim"])
        self.assertEqual(analysis["reasoning"]["status"], "matched")
        self.assertEqual(analysis["reasoning"]["flagged_clauses"], [])
        self.assertEqual(analysis["uncertainty"]["status"], "missing")
        self.assertEqual(analysis["uncertainty"]["evidence_clauses"], [])




if __name__ == "__main__":
    unittest.main()
