"""Tests for conservative, provenance-preserving memory cleanup previews."""
import json
import tempfile
import unittest
from pathlib import Path

from experience_store import make_record, read_records
from memory_cleanup import cleanup_preview, write_preview


class MemoryCleanupTests(unittest.TestCase):
    def observation(self, record_id, *, url="https://example.org/page", digest="a" * 64,
                    review_status="unreviewed", text="Same page text", tags=None):
        return make_record(
            record_id=record_id, record_type="observation", source=url,
            content=(
                f"Title: Example\nURL: {url}\nPage SHA-256: {digest}\n"
                "Extracted page text (untrusted; not independently verified):\n"
                f"{text}"
            ),
            outcome="observed", confidence="low", review_status=review_status,
            tags=tags or ["web", "unverified"],
            recorded_at=f"2026-10-28T12:00:{int(record_id[-1]) % 60:02d}Z",
        )

    def test_consolidates_only_matching_source_hash_and_status(self):
        first = self.observation("web-001", url="https://example.org/page?utm_source=one", tags=["web"])
        duplicate = self.observation("web-002", url="https://example.org/page#section", tags=["unverified"])
        cleaned, report = cleanup_preview([first, duplicate])
        self.assertEqual([record["id"] for record in cleaned], ["web-001"])
        self.assertEqual(cleaned[0]["tags"], ["web", "unverified"])
        self.assertIn("web-002", report)
        self.assertIn("Original source", report)
        self.assertIn("original memory file is not changed", report)

    def test_preserves_changed_content_as_separate_record(self):
        first = self.observation("web-001", digest="a" * 64)
        changed = self.observation("web-002", digest="b" * 64)
        cleaned, report = cleanup_preview([first, changed])
        self.assertEqual(len(cleaned), 2)
        self.assertIn("No eligible exact-duplicate clusters", report)

    def test_preserves_different_review_statuses(self):
        first = self.observation("web-001", review_status="unreviewed")
        reviewed = self.observation("web-002", review_status="reviewed")
        cleaned, _ = cleanup_preview([first, reviewed])
        self.assertEqual(len(cleaned), 2)
        self.assertEqual({record["review_status"] for record in cleaned}, {"unreviewed", "reviewed"})

    def test_preserves_records_without_page_hash_and_non_observations(self):
        no_hash = make_record(record_id="web-001", record_type="observation",
                              source="https://example.org/page", content="No hash here")
        lesson = make_record(record_id="lesson-1", record_type="lesson",
                             source="manual", content="A lesson")
        cleaned, _ = cleanup_preview([no_hash, lesson])
        self.assertEqual([record["id"] for record in cleaned], ["web-001", "lesson-1"])

    def test_preview_does_not_mutate_or_overwrite_original_store(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = root / "memory.jsonl"
            output = root / "cleaned.jsonl"
            report = root / "report.md"
            records = [
                self.observation("web-001"),
                self.observation("web-002"),
            ]
            store.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
            original_bytes = store.read_bytes()
            result = write_preview(store, output, report)
            self.assertEqual(store.read_bytes(), original_bytes)
            self.assertEqual(result["input_records"], 2)
            self.assertEqual(result["preview_records"], 1)
            self.assertEqual(len(read_records(output)), 1)
            self.assertIn("web-002", report.read_text(encoding="utf-8"))

    def test_refuses_to_overwrite_original_store(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "memory.jsonl"
            store.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must not overwrite"):
                write_preview(store, store, Path(directory) / "report.md")


if __name__ == "__main__":
    unittest.main()
