"""Tests for review bundle manifest verification."""
import json
import tempfile
import unittest
from pathlib import Path

from verify_review_bundle import verify_bundle


class VerifyReviewBundleTests(unittest.TestCase):
    def create_bundle(self, root: Path) -> Path:
        prefix = root / "review"
        (root / "review.json").write_text('{"schema_version":"1.0"}\n', encoding="utf-8")
        (root / "review.md").write_text("# Review\n", encoding="utf-8")
        import hashlib
        manifest = {
            "manifest_version": "1.0",
            "files": {
                "review.json": hashlib.sha256((root / "review.json").read_bytes()).hexdigest(),
                "review.md": hashlib.sha256((root / "review.md").read_bytes()).hexdigest(),
            },
            "notice": "Hashes do not validate content.",
        }
        (root / "review.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return prefix

    def test_accepts_matching_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            valid, messages = verify_bundle(self.create_bundle(Path(temp)))
            self.assertTrue(valid, messages)

    def test_detects_modified_report(self):
        with tempfile.TemporaryDirectory() as temp:
            prefix = self.create_bundle(Path(temp))
            (Path(temp) / "review.md").write_text("# Changed\n", encoding="utf-8")
            valid, messages = verify_bundle(prefix)
            self.assertFalse(valid)
            self.assertTrue(any("hash mismatch" in item for item in messages))

    def test_rejects_manifest_with_unexpected_file_names(self):
        with tempfile.TemporaryDirectory() as temp:
            prefix = self.create_bundle(Path(temp))
            path = Path(temp) / "review.manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["files"]["../../other"] = "0" * 64
            path.write_text(json.dumps(manifest), encoding="utf-8")
            valid, messages = verify_bundle(prefix)
            self.assertFalse(valid)
            self.assertTrue(any("exactly" in item for item in messages))

    def test_missing_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            valid, messages = verify_bundle(Path(temp) / "missing")
            self.assertFalse(valid)
            self.assertTrue(messages)


if __name__ == "__main__":
    unittest.main()
