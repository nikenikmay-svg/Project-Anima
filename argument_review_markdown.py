"""Render argument-review documents as readable Markdown.

This is a presentation layer over supplied review data, not a semantic evaluator.
"""
from __future__ import annotations

from typing import Any


def _text(value: Any, fallback: str = "Not supplied") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _bullets(values: Any) -> list[str]:
    if not isinstance(values, list):
        return ["- None supplied"]
    cleaned = [item.strip() for item in values if isinstance(item, str) and item.strip()]
    return [f"- {item}" for item in cleaned] or ["- None supplied"]


def render_review_markdown(document: Any) -> str:
    """Render a review document into Markdown, preserving unknown statuses."""
    if not isinstance(document, dict):
        raise ValueError("review document must be an object")
    review = document.get("review")
    summary = document.get("summary")
    if not isinstance(review, dict) or not isinstance(summary, dict):
        raise ValueError("review document must contain object fields 'review' and 'summary'")

    validation = review.get("argument_validation")
    validation = validation if isinstance(validation, dict) else {}
    premise_rows = review.get("premise_evidence")
    premise_rows = premise_rows if isinstance(premise_rows, list) else []

    lines = [
        "# Argument Review Report",
        "",
        f"- **Schema version:** {_text(document.get('schema_version'), 'Unknown')}",
        f"- **Argument ID:** {_text(validation.get('argument_id'))}",
        f"- **Structure valid:** {'Yes' if validation.get('valid') is True else 'No / not validated'}",
        f"- **Review status:** {_text(review.get('review_status'), 'pending_human_review')}",
        f"- **Inference quality:** {_text(review.get('inference_quality'), 'not_assessed')}",
        f"- **Conclusion evidence status:** {_text(review.get('conclusion_evidence_status'), 'not_assessed')}",
        "",
        "## Premises and supplied evidence",
        "",
    ]

    if not premise_rows:
        lines.append("No premise evidence rows were supplied.")
    for row in premise_rows:
        if not isinstance(row, dict):
            continue
        index = row.get("premise_index", "?")
        premise = _text(row.get("premise"))
        lines.extend([f"### Premise {index}", "", premise, "", "**Evidence items supplied:**"])
        lines.extend(_bullets(row.get("evidence_items")))
        lines.extend(["", f"**Support assessment:** {_text(row.get('support_assessment'), 'not_assessed')}", ""])

    lines.extend(["## Unstated assumptions supplied", ""])
    lines.extend(_bullets(review.get("unstated_assumptions")))
    lines.extend(["", "## Counterexamples supplied", ""])
    lines.extend(_bullets(review.get("counterexamples")))
    lines.extend(["", "## Summary counts", ""])
    for key, label in (
        ("premise_count", "Premises"),
        ("premises_with_evidence_supplied", "Premises with evidence items supplied"),
        ("evidence_items_supplied", "Evidence items supplied"),
        ("assumption_count", "Assumptions supplied"),
        ("counterexample_count", "Counterexamples supplied"),
    ):
        value = summary.get(key, 0)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            value = 0
        lines.append(f"- **{label}:** {value}")
    lines.extend([
        "",
        "## Limitations",
        "",
        _text(
            document.get("notice"),
            "This report organizes supplied information only and does not establish truth or logical validity.",
        ),
        "",
        "**Human review is required.** Counts describe supplied material, not evidence quality. "
        "A missing item does not prove that no evidence exists. Inference quality remains unassessed.",
        "",
    ])
    return "\n".join(lines)
