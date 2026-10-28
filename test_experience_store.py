"""Regression tests for Anima's append-only experience memory."""
import json
import tempfile
import unittest
from pathlib import Path

from experience_store import append_record, make_record, read_records, render_markdown, validate_record


class ExperienceStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = Path(self.temp_dir.name) / "memory.jsonl"
        self.record = make_record(
            record_id="exp-001", record_type="experiment", source="benchmark run 12",
            content="Semicolon-separated clauses should be evaluated independently.",
            outcome="observed", confidence="medium", tags=["clause-scope"],
            recorded_at="2026-10-28T12:00:00Z",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_store_is_empty(self):
        self.assertEqual(read_records(self.store), [])

    def test_append_and_read_round_trip(self):
        append_record(self.store, self.record)
        self.assertEqual(read_records(self.store), [self.record])
        self.assertEqual(len(self.store.read_text(encoding="utf-8").splitlines()), 1)

    def test_duplicate_id_is_rejected_without_appending(self):
        append_record(self.store, self.record)
        with self.assertRaisesRegex(ValueError, "already exists"):
            append_record(self.store, self.record)
        self.assertEqual(len(read_records(self.store)), 1)

    def test_invalid_record_type_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "record_type"):
            make_record(record_id="bad", record_type="guess", source="test", content="text")

    def test_empty_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "source"):
            make_record(record_id="bad", record_type="lesson", source=" ", content="text")

    def test_invalid_review_status_is_rejected(self):
        candidate = dict(self.record, review_status="verified_by_ai")
        with self.assertRaisesRegex(ValueError, "review_status"):
            validate_record(candidate)

    def test_corrupt_json_reports_line_number(self):
        self.store.write_text('{broken}\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "line 1"):
            read_records(self.store)

    def test_duplicate_ids_in_existing_file_fail_closed(self):
        row = json.dumps(self.record)
        self.store.write_text(row + "\n" + row + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate memory ID"):
            read_records(self.store)

    def test_markdown_labels_unreviewed_records(self):
        output = render_markdown([self.record])
        self.assertIn("Review status: unreviewed", output)
        self.assertIn("storage is not verification", output)

    def test_search_requires_nonblank_query(self):
        from experience_store import search_records
        with self.assertRaisesRegex(ValueError, "nonblank"):
            search_records([self.record], "  ")

    def test_search_matches_all_terms_case_insensitively(self):
        from experience_store import search_records
        second = make_record(
            record_id="exp-002", record_type="observation", source="https://example.org",
            content="Evidence supports the claim but uncertainty remains.",
            tags=["research"], recorded_at="2026-10-28T13:00:00Z",
        )
        found = search_records([self.record, second], "EVIDENCE uncertainty")
        self.assertEqual([item["id"] for item in found], ["exp-002"])

    def test_search_filters_by_review_status_and_exact_tag(self):
        from experience_store import search_records
        reviewed = make_record(
            record_id="exp-002", record_type="lesson", source="manual review",
            content="Clause scope needs careful review.", outcome="confirmed",
            confidence="medium", review_status="reviewed", tags=["clause-scope"],
        )
        found = search_records([self.record, reviewed], "review", review_status="reviewed", tag="CLAUSE-SCOPE")
        self.assertEqual([item["id"] for item in found], ["exp-002"])

    def test_search_rejects_unknown_review_status(self):
        from experience_store import search_records
        with self.assertRaisesRegex(ValueError, "review_status"):
            search_records([self.record], "evidence", review_status="verified")

    def test_tags_must_be_unique(self):
        with self.assertRaisesRegex(ValueError, "duplicates"):
            make_record(record_id="bad", record_type="lesson", source="test", content="text", tags=["x", "x"])


if __name__ == "__main__":
    unittest.main()
