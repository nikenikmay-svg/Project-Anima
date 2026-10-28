"""Tests for Anima's public-web research boundary and memory integration."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import web_roamer
from experience_store import read_records


class WebRoamerTests(unittest.TestCase):
    def test_rejects_non_http_schemes(self):
        with self.assertRaisesRegex(ValueError, "http"):
            web_roamer.validate_public_url("file:///etc/passwd")

    def test_rejects_localhost(self):
        with self.assertRaisesRegex(ValueError, "local"):
            web_roamer.validate_public_url("http://localhost/private")

    def test_rejects_private_ip(self):
        with self.assertRaisesRegex(ValueError, "non-public"):
            web_roamer.validate_public_url("http://127.0.0.1/admin")

    def test_rejects_credentials_and_nonstandard_port(self):
        with self.assertRaisesRegex(ValueError, "credentials"):
            web_roamer.validate_public_url("https://user:pass@example.com")
        with self.assertRaisesRegex(ValueError, "ports"):
            web_roamer.validate_public_url("https://example.com:8443")

    def test_extractor_ignores_script_and_style(self):
        parser = web_roamer.TextExtractor()
        parser.feed("<html><title>Example</title><style>bad css</style><script>secret()</script><p>Hello world</p></html>")
        title, text = parser.result()
        self.assertEqual(title, "Example")
        self.assertIn("Hello world", text)
        self.assertNotIn("secret", text)
        self.assertNotIn("bad css", text)

    def test_search_parser_collects_result_title(self):
        parser = web_roamer.SearchExtractor()
        parser.feed('<a class="result__a" href="https://example.com">Example result</a>')
        self.assertEqual(parser.results[0]["title"], "Example result")
        self.assertEqual(parser.results[0]["url"], "https://example.com")

    def test_search_parser_accepts_alternate_result_link_class(self):
        parser = web_roamer.SearchExtractor()
        parser.feed('<a class="result-link" href="https://example.com">Alternate result</a>')
        self.assertEqual(parser.results[0]["title"], "Alternate result")
        self.assertEqual(parser.results[0]["url"], "https://example.com")

    def test_query_with_no_search_results_reports_search_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "memory.jsonl"
            with patch.object(web_roamer, "search_web", return_value=[]):
                with self.assertRaisesRegex(ValueError, "search returned no usable results"):
                    web_roamer.research("test query", [], store)

    def test_research_saves_unreviewed_source_linked_record(self):
        page = {"url": "https://example.com/", "title": "Example", "text": "Observed text",
                "content_sha256": "abc123"}
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "memory.jsonl"
            with patch.object(web_roamer, "read_page", return_value=page):
                result = web_roamer.research(None, ["https://example.com/"], store)
            self.assertEqual(len(result["saved"]), 1)
            records = read_records(store)
            self.assertEqual(records[0]["source"], "https://example.com/")
            self.assertEqual(records[0]["review_status"], "unreviewed")
            self.assertIn("not independently verified", records[0]["content"])

    def test_research_skips_unchanged_page(self):
        page = {"url": "https://example.com/", "title": "Example", "text": "Observed text",
                "content_sha256": "abc123"}
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "memory.jsonl"
            with patch.object(web_roamer, "read_page", return_value=page):
                web_roamer.research(None, ["https://example.com/"], store)
                result = web_roamer.research(None, ["https://example.com/"], store)
            self.assertEqual(len(result["saved"]), 0)
            self.assertEqual(len(result["skipped"]), 1)

    def test_invalid_limit_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 10"):
            web_roamer.search_web("anima", limit=20)


if __name__ == "__main__":
    unittest.main()
