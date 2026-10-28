"""Create a conservative, auditable duplicate-cleanup preview for Anima memory.

The original store is never modified. Only web observations with the same
normalized source URL, normalized extracted-text SHA-256, outcome, confidence,
and review status are eligible for consolidation. The raw response-body hash is
recorded for audit but is not used as the primary duplicate fingerprint because
page HTML can change between fetches while extracted text stays the same.
Records without extractable text remain separate. A report preserves the IDs
and metadata of every collapsed record.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path

from experience_store import read_records
from web_roamer import canonical_source_url

PAGE_HASH = re.compile(r"(?m)^Page SHA-256: ([0-9a-f]{64})$")
TEXT_MARKER = "Extracted page text (untrusted; not independently verified):\\n"


def _page_hash(record: dict) -> str | None:
    """Return the original response-body hash for audit/debug purposes."""
    match = PAGE_HASH.search(record.get("content", ""))
    return match.group(1) if match else None


def _extracted_text_hash(record: dict) -> str | None:
    """Fingerprint normalized extracted text, excluding volatile response metadata."""
    content = record.get("content", "")
    if TEXT_MARKER not in content:
        return None
    text = content.split(TEXT_MARKER, 1)[1]
    normalized = " ".join(text.split()).casefold()
    if not normalized:
        return None
    import hashlib
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def cleanup_preview(records: list[dict]) -> tuple[list[dict], str]:
    """Return a cleaned copy and an audit report; input records are not mutated."""
    groups: OrderedDict[tuple, list[dict]] = OrderedDict()
    passthrough = []
    for record in records:
        digest = _extracted_text_hash(record)
        if record.get("record_type") != "observation" or not digest:
            passthrough.append(record)
            continue
        key = (
            canonical_source_url(record["source"]),
            digest,
            record["outcome"],
            record["confidence"],
            record["review_status"],
        )
        groups.setdefault(key, []).append(record)

    cleaned = list(passthrough)
    clusters = []
    for (canonical_url, digest, outcome, confidence, review_status), members in groups.items():
        primary = dict(members[0])
        if len(members) > 1:
            # Combine tags deterministically without changing the stored source text.
            primary["tags"] = list(dict.fromkeys(
                tag for member in members for tag in member["tags"]
            ))
            clusters.append({
                "canonical_url": canonical_url,
                "extracted_text_sha256": digest,
                "original_page_sha256s": list(dict.fromkeys(
                    value for member in members if (value := _page_hash(member))
                )),
                "retained_id": primary["id"],
                "collapsed_ids": [member["id"] for member in members[1:]],
                "members": [
                    {
                        "id": member["id"],
                        "recorded_at": member["recorded_at"],
                        "source": member["source"],
                        "review_status": member["review_status"],
                        "outcome": member["outcome"],
                        "confidence": member["confidence"],
                        "tags": member["tags"],
                    }
                    for member in members
                ],
            })
        cleaned.append(primary)

    # Preserve original relative order as much as possible: primary records and
    # passthrough records are sorted by the original input order.
    positions = {record["id"]: index for index, record in enumerate(records)}
    cleaned.sort(key=lambda record: positions[record["id"]])

    removed = sum(len(cluster["collapsed_ids"]) for cluster in clusters)
    lines = [
        "# Anima memory cleanup preview", "",
        f"- Input records: **{len(records)}**",
        f"- Preview records: **{len(cleaned)}**",
        f"- Records consolidated in this preview: **{removed}**",
        f"- Duplicate clusters: **{len(clusters)}**",
        "",
        "> This is a preview only. The original memory file is not changed. Consolidation is limited to web observations with matching normalized source URL, page-body SHA-256, outcome, confidence, and review status. Records without a recognized page hash, changed page content, or different review status are preserved separately. This is not fact-checking and does not promote any observation to verified knowledge.",
        "",
    ]
    if not clusters:
        lines.append("No eligible exact-duplicate clusters were found.")
    for index, cluster in enumerate(clusters, start=1):
        lines.extend([
            f"## Duplicate cluster {index}", "",
            f"- Normalized source: {cluster['canonical_url']}",
            f"- Normalized extracted-text SHA-256: {cluster['extracted_text_sha256']}",
            f"- Original response-body SHA-256 values (may vary across identical fetches): {', '.join(cluster['original_page_sha256s']) or '(not available)'}",
            f"- Retained record ID: {cluster['retained_id']}",
            f"- Consolidated duplicate IDs: {', '.join(cluster['collapsed_ids'])}",
            "",
            "| Record ID | Recorded at | Original source | Review status |",
            "|---|---|---|---|",
        ])
        for member in cluster["members"]:
            source = member["source"].replace("|", "%7C")
            lines.append(
                f"| {member['id']} | {member['recorded_at']} | {source} | {member['review_status']} |"
            )
        lines.append("")
    return cleaned, "\n".join(lines) + "\n"


def write_preview(store_path: str | Path, output_path: str | Path,
                  report_path: str | Path) -> dict:
    """Read the original store and write separate cleaned-copy and audit files."""
    records = read_records(store_path)
    cleaned, report = cleanup_preview(records)
    output = Path(output_path)
    audit = Path(report_path)
    if output.resolve() == Path(store_path).resolve():
        raise ValueError("cleanup output must not overwrite the original memory store")
    if audit.resolve() in {Path(store_path).resolve(), output.resolve()}:
        raise ValueError("audit report must be a separate file")
    output.parent.mkdir(parents=True, exist_ok=True)
    audit.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in cleaned),
        encoding="utf-8",
    )
    audit.write_text(report, encoding="utf-8")
    return {"input_records": len(records), "preview_records": len(cleaned),
            "collapsed_records": len(records) - len(cleaned), "output": str(output),
            "report": str(audit)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", default="anima-memory.jsonl")
    parser.add_argument("--output", default="anima-memory-cleaned.jsonl")
    parser.add_argument("--report", default="anima-memory-cleanup-report.md")
    args = parser.parse_args(argv)
    try:
        result = write_preview(args.store, args.output, args.report)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
