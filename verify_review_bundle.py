"""Verify the integrity of a JSON/Markdown review bundle manifest.

This verifies file hashes only. It does not authenticate authors or validate content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def verify_bundle(prefix: str | Path) -> tuple[bool, list[str]]:
    """Return whether the bundle matches its manifest and any diagnostic messages."""
    base = Path(prefix)
    manifest_path = Path(str(base) + ".manifest.json")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"cannot read manifest: {exc}"]

    if not isinstance(manifest, dict) or manifest.get("manifest_version") != "1.0":
        return False, ["unsupported or malformed manifest"]
    files = manifest.get("files")
    expected_names = {base.name + ".json", base.name + ".md"}
    if not isinstance(files, dict) or set(files) != expected_names:
        return False, ["manifest must list exactly the matching .json and .md report files"]

    errors: list[str] = []
    for name, expected_hash in files.items():
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            errors.append(f"invalid SHA-256 entry for {name}")
            continue
        path = base.parent / name
        try:
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            errors.append(f"cannot read {name}: {exc}")
            continue
        if actual_hash != expected_hash:
            errors.append(f"hash mismatch: {name}")
    return not errors, errors or ["bundle hashes match manifest"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify review-bundle file integrity (not source trust or reasoning quality)."
    )
    parser.add_argument("prefix", help="bundle output prefix used by argument_review_cli.py")
    args = parser.parse_args(argv)
    valid, messages = verify_bundle(args.prefix)
    for message in messages:
        print(message)
    print("Integrity check passed." if valid else "Integrity check failed.", file=sys.stderr if not valid else sys.stdout)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
