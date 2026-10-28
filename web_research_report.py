"""Deterministic, provenance-preserving report for Anima's web memory.

Source indicators describe visible metadata and domain categories. They are not
truth scores, fact checks, or substitutes for reading and reviewing the sources.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from experience_store import read_records


INSTITUTIONAL_SUFFIXES = (".gov", ".gov.in", ".edu", ".ac.in", ".edu.in")
RESEARCH_HOSTS = (
    "doi.org", "pubmed.ncbi.nlm.nih.gov", "arxiv.org", "nature.com",
    "science.org", "journals.plos.org", "bmj.com", "thelancet.com",
)
REFERENCE_HOSTS = ("wikipedia.org",)


def source_indicators(url: str, content: str) -> dict:
    """Return transparent metadata indicators, never a claim that a source is true."""
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if any(host == suffix.lstrip(".") or host.endswith(suffix) for suffix in INSTITUTIONAL_SUFFIXES):
        domain_category = "institutional-domain indicator"
    elif any(host == item or host.endswith("." + item) for item in RESEARCH_HOSTS):
        domain_category = "research/publisher-domain indicator"
    elif any(host == item or host.endswith("." + item) for item in REFERENCE_HOSTS):
        domain_category = "reference-encyclopedia indicator"
    else:
        domain_category = "general-web domain; type not classified"

    title = ""
    for line in content.splitlines():
        if line.startswith("Title: "):
            title = line[len("Title: "):].strip()
            break
    return {
        "host": host or "(invalid or missing host)",
        "transport": "HTTPS" if parsed.scheme.lower() == "https" else "non-HTTPS",
        "domain_category": domain_category,
        "title_present": bool(title),
        "extracted_text_characters": _extract_text_length(content),
        "review_status": "metadata only; human review still required",
    }


def _extract_text_length(content: str) -> int:
    marker = "Extracted page text (untrusted; not independently verified):\n"
    if marker not in content:
        return 0
    return len(content.split(marker, 1)[1].strip())


def build_report(records: list[dict]) -> str:
    """Render source-linked inventory with duplicate counts and transparent indicators."""
    observations = [r for r in records if r.get("record_type") == "observation" and "URL: " in r.get("content", "")]
    canonical_urls = [r["source"].split("#", 1)[0].rstrip("/") for r in observations]
    counts = Counter(canonical_urls)
    lines = [
        "# Anima web research review report", "",
        f"- Memory records read: **{len(records)}**",
        f"- Source-linked web observations: **{len(observations)}**",
        f"- Distinct source URLs (fragment/trailing-slash normalized): **{len(counts)}**",
        f"- URLs appearing more than once: **{sum(1 for n in counts.values() if n > 1)}**",
        "",
        "> This is a deterministic inventory, not a semantic summary or fact-check. Domain labels are clues only; they do not establish source quality or truth. All stored observations remain unverified until reviewed.",
        "",
    ]
    if not observations:
        lines.append("No source-linked web observations were found.")
        return "\n".join(lines) + "\n"

    lines.extend(["## Source inventory", ""])
    for index, record in enumerate(observations, start=1):
        indicators = source_indicators(record["source"], record["content"])
        title = next((line[len("Title: "):].strip() for line in record["content"].splitlines()
                      if line.startswith("Title: ")), record["source"])
        lines.extend([
            f"### {index}. {title or record['source']}", "",
            f"- Source: {record['source']}",
            f"- Host: {indicators['host']}",
            f"- Indicators: {indicators['transport']}; {indicators['domain_category']}",
            f"- Extracted text characters: {indicators['extracted_text_characters']}",
            f"- Review status: {record.get('review_status', 'unknown')}",
            f"- Same normalized URL records: {counts[record['source'].split('#', 1)[0].rstrip('/')]}",
            f"- Memory record ID: {record['id']}", "",
        ])
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", default="anima-memory.jsonl", help="JSONL memory file")
    parser.add_argument("--output", default="anima-research-report.md", help="Markdown report path")
    args = parser.parse_args(argv)
    try:
        records = read_records(args.store)
        report = build_report(records)
        Path(args.output).write_text(report, encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Wrote source inventory for {len(records)} memory records to {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
