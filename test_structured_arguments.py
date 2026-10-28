"""Regression tests for explicit argument structure validation."""
import unittest

from structured_arguments import validate_argument, validate_arguments


class StructuredArgumentTests(unittest.TestCase):
    def test_valid_shape_does_not_claim_logical_validity(self):
        result = validate_argument({
            "id": "a1",
            "premises": ["All mammals are animals.", "Whales are mammals."],
            "conclusion": "Whales are animals.",
        })
        self.assertTrue(result["valid"])
        self.assertEqual(result["premise_count"], 2)
        self.assertEqual(result["logical_validity"], "not_assessed")

    def test_rejects_missing_fields(self):
        result = validate_argument({"id": "a1", "premises": ["P"]})
        self.assertFalse(result["valid"])
        self.assertTrue(any("conclusion" in error for error in result["errors"]))

    def test_rejects_empty_premises_and_conclusion(self):
        result = validate_argument({"id": "a1", "premises": [" "], "conclusion": ""})
        self.assertFalse(result["valid"])
        self.assertGreaterEqual(len(result["errors"]), 2)

    def test_rejects_wrong_top_level_types(self):
        self.assertFalse(validate_argument(["not", "an", "object"])["valid"])
        self.assertFalse(validate_arguments({"not": "a list"})["valid"])

    def test_duplicate_ids_are_reported(self):
        result = validate_arguments([
            {"id": "same", "premises": ["P"], "conclusion": "C"},
            {"id": "same", "premises": ["Q"], "conclusion": "D"},
        ])
        self.assertFalse(result["valid"])
        self.assertIn("duplicate argument ids: same", result["errors"])

    def test_empty_premise_list_is_invalid(self):
        result = validate_argument({"id": "a1", "premises": [], "conclusion": "C"})
        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
