"""A small, append-only store for Anima's observations and lessons.

Records preserve provenance and review status. Storing a record does not make
its claim true, and unreviewed records must not be treated as verified facts.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
ALLOWED_TYPES = {"observation", "experiment", "lesson"}
ALLOWED_OUTCOMES = {"observed", "confirmed", "refuted", "unknown"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_REVIEW_STATUS = {"unreviewed", "reviewed", "rejected"}


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_record(record: object) -> dict:
    """Validate a memory record and return it without silently changing it."""
    if not isinstance(record, dict):
        raise ValueError("memory record must be a JSON object")
    required = {
        "schema_version", "id", "recorded_at", "record_type", "source",
        "content", "outcome", "confidence", "review_status", "tags",
    }
    missing = sorted(required - set(record))
    if missing:
        raise ValueError(f"missing required fields: {missing}")
    if record["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    for key in ("id", "recorded_at", "source", "content"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValueError(f"{key} must be a nonblank string")
    if record["record_type"] not in ALLOWED_TYPES:
        raise ValueError(f"record_type must be one of {sorted(ALLOWED_TYPES)}")
    if record["outcome"] not in ALLOWED_OUTCOMES:
        raise ValueError(f"outcome must be one of {sorted(ALLOWED_OUTCOMES)}")
    if record["confidence"] not in ALLOWED_CONFIDENCE:
        raise ValueError(f"confidence must be one of {sorted(ALLOWED_CONFIDENCE)}")
    if record["review_status"] not in ALLOWED_REVIEW_STATUS:
        raise ValueError(f"review_status must be one of {sorted(ALLOWED_REVIEW_STATUS)}")
    if not isinstance(record["tags"], list) or any(
        not isinstance(tag, str) or not tag.strip() for tag in record["tags"]
    ):
        raise ValueError("tags must be a list of nonblank strings")
    if len(record["tags"]) != len(set(record["tags"])):
        raise ValueError("tags must not contain duplicates")
    return record


def read_records(store_path: str | Path) -> list[dict]:
    """Read and validate every JSONL record, reporting malformed line numbers."""
    path = Path(store_path)
    if not path.exists():
        return []
    records = []
    seen_ids = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise ValueError(f"blank line in memory store at line {line_number}")
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at memory store line {line_number}: {exc.msg}") from exc
            validate_record(record)
            if record["id"] in seen_ids:
                raise ValueError(f"duplicate memory ID {record['id']!r} at line {line_number}")
            seen_ids.add(record["id"])
            records.append(record)
    return records


def make_record(*, record_id: str, record_type: str, source: str, content: str,
                outcome: str = "unknown", confidence: str = "low",
                review_status: str = "unreviewed", tags: list[str] | None = None,
                recorded_at: str | None = None) -> dict:
    """Build a validated memory record; timestamps can be supplied for tests/imports."""
    record = {
        "schema_version": SCHEMA_VERSION,
        "id": record_id,
        "recorded_at": recorded_at or utc_now(),
        "record_type": record_type,
        "source": source,
        "content": content,
        "outcome": outcome,
        "confidence": confidence,
        "review_status": review_status,
        "tags": list(tags or []),
    }
    return validate_record(record)


def append_record(store_path: str | Path, record: dict) -> dict:
    """Append one validated record; duplicate IDs and malformed stores fail closed."""
    validate_record(record)
    path = Path(store_path)
    existing = read_records(path)
    if any(item["id"] == record["id"] for item in existing):
        raise ValueError(f"memory ID already exists: {record['id']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def render_markdown(records: list[dict]) -> str:
    """Render a human-readable inventory without implying records are verified."""
    lines = ["# Anima experience memory", "", f"Records: **{len(records)}**", "",
             "Stored records preserve their declared status; storage is not verification.", ""]
    if not records:
        lines.append("No records stored yet.")
    for item in records:
        lines.extend([
            f"## {item['id']} — {item['record_type']}", "",
            f"- Recorded: {item['recorded_at']}",
            f"- Source: {item['source']}",
            f"- Outcome: {item['outcome']}",
            f"- Confidence: {item['confidence']}",
            f"- Review status: {item['review_status']}",
            f"- Tags: {', '.join(item['tags']) if item['tags'] else '(none)' }", "",
            item["content"], "",
        ])
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    add = subparsers.add_parser("add", help="append an observation, experiment, or lesson")
    add.add_argument("--store", default="anima-memory.jsonl")
    add.add_argument("--id", required=True, dest="record_id")
    add.add_argument("--type", required=True, choices=sorted(ALLOWED_TYPES), dest="record_type")
    add.add_argument("--source", required=True, help="where this record came from")
    add.add_argument("--content", required=True, help="observation or lesson; do not include secrets")
    add.add_argument("--outcome", choices=sorted(ALLOWED_OUTCOMES), default="unknown")
    add.add_argument("--confidence", choices=sorted(ALLOWED_CONFIDENCE), default="low")
    add.add_argument("--tag", action="append", default=[], dest="tags")

    show = subparsers.add_parser("list", help="list stored records")
    show.add_argument("--store", default="anima-memory.jsonl")
    show.add_argument("--format", choices=["json", "markdown"], default="markdown")

    args = parser.parse_args(argv)
    try:
        if args.action == "add":
            record = make_record(
                record_id=args.record_id, record_type=args.record_type,
                source=args.source, content=args.content, outcome=args.outcome,
                confidence=args.confidence, tags=args.tags,
            )
            append_record(args.store, record)
            print(f"Stored {record['id']} with review status '{record['review_status']}'.")
        else:
            records = read_records(args.store)
            if args.format == "json":
                print(json.dumps(records, indent=2, ensure_ascii=False))
            else:
                print(render_markdown(records))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
