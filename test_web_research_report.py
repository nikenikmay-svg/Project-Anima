"""Tests for Anima's deterministic source inventory report."""
import unittest

from experience_store import make_record
from web_research_report import build_report, source_indicators


class WebResearchReportTests(unittest.TestCase):
    def setUp(self):
        self.record = make_record(
            record_id="web-001", record_type="observation",
            source="https://en.wikipedia.org/wiki/Science",
            content=(
                "Title: Science\nURL: https://en.wikipedia.org/wiki/Science\n"
                "Page SHA-256: " + "a" * 64 + "\n"
                "Extracted page text (untrusted; not independently verified):\n"
                "Evidence and methods."
            ),
            outcome="observed", confidence="low", review_status="unreviewed",
            tags=["web", "unverified"],
        )

    def test_wikipedia_is_only_classified_as_reference_indicator(self):
        indicators = source_indicators(self.record["source"], self.record["content"])
        self.assertEqual(indicators["domain_category"], "reference-encyclopedia indicator")
        self.assertEqual(indicators["transport"], "HTTPS")
        self.assertEqual(indicators["extracted_text_characters"], len("Evidence and methods."))
        self.assertIn("human review", indicators["review_status"])

    def test_report_preserves_source_and_unverified_caveat(self):
        report = build_report([self.record])
        self.assertIn(self.record["source"], report)
        self.assertIn("not a semantic summary or fact-check", report)
        self.assertIn("review_status", report)
        self.assertIn("Source inventory", report)

    def test_report_counts_repeated_normalized_source_urls(self):
        second = dict(self.record, id="web-002", source=self.record["source"] + "#section")
        report = build_report([self.record, second])
        self.assertIn("Distinct source URLs (fragment/trailing-slash normalized): **1**", report)
        self.assertIn("URLs appearing more than once: **1**", report)

    def test_empty_report_is_explicit(self):
        self.assertIn("No source-linked web observations", build_report([]))


if __name__ == "__main__":
    unittest.main()
