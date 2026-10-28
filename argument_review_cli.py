"""JSON command-line interface for transparent argument review.

Input JSON fields: argument (required), evidence_by_premise, unstated_assumptions,
counterexamples (optional). Output contains the review report and inventory summary.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from argument_review import review_argument
from argument_review_summary import summarize_review


def build_review_document(payload: Any) -> dict[str, Any]:
    """Create a review document from a parsed JSON payload."""
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    if "argument" not in payload:
        raise ValueError("input JSON must include an 'argument' field")
    review = review_argument(
        payload["argument"],
        evidence_by_premise=payload.get("evidence_by_premise"),
        unstated_assumptions=payload.get("unstated_assumptions"),
        counterexamples=payload.get("counterexamples"),
    )
    return {
        "schema_version": "1.0",
        "review": review,
        "summary": summarize_review(review),
        "notice": (
            "This report organizes supplied information only. It does not verify "
            "sources or establish premise support, conclusion truth, or logical validity."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a JSON argument-review report without claiming semantic validation."
    )
    parser.add_argument("input", help="path to a UTF-8 JSON input file")
    parser.add_argument("-o", "--output", help="output path; defaults to stdout")
    args = parser.parse_args(argv)

    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        document = build_review_document(payload)
        rendered = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"argument-review: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
