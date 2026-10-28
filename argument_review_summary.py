"""Build a compact summary from an argument_review report.

Counts describe what was supplied to the report, not evidence quality or logic.
"""
from __future__ import annotations

from typing import Any


def summarize_review(report: Any) -> dict[str, Any]:
    """Summarize review inventory while preserving unknowns and review status."""
    if not isinstance(report, dict):
        return {
            "valid_report": False,
            "errors": ["report must be a mapping"],
            "review_status": "not_available",
            "evidence_items_supplied": 0,
            "premises_with_evidence_supplied": 0,
            "premise_count": 0,
            "assumption_count": 0,
            "counterexample_count": 0,
            "conclusion_evidence_status": "not_assessed",
            "inference_quality": "not_assessed",
        }

    validation = report.get("argument_validation")
    if not isinstance(validation, dict):
        validation = {}
    premise_evidence = report.get("premise_evidence")
    if not isinstance(premise_evidence, list):
        premise_evidence = []
    evidence_count = 0
    premises_with_evidence = 0
    for item in premise_evidence:
        if not isinstance(item, dict):
            continue
        evidence_items = item.get("evidence_items")
        if isinstance(evidence_items, list):
            cleaned_count = sum(
                1 for entry in evidence_items
                if isinstance(entry, str) and entry.strip()
            )
            evidence_count += cleaned_count
            if cleaned_count:
                premises_with_evidence += 1

    assumptions = report.get("unstated_assumptions")
    counterexamples = report.get("counterexamples")
    assumptions = assumptions if isinstance(assumptions, list) else []
    counterexamples = counterexamples if isinstance(counterexamples, list) else []

    return {
        "valid_report": True,
        "argument_id": validation.get("argument_id"),
        "argument_structure_valid": validation.get("valid", False) is True,
        "premise_count": len(premise_evidence),
        "premises_with_evidence_supplied": premises_with_evidence,
        "evidence_items_supplied": evidence_count,
        "assumption_count": sum(1 for x in assumptions if isinstance(x, str) and x.strip()),
        "counterexample_count": sum(1 for x in counterexamples if isinstance(x, str) and x.strip()),
        "conclusion_evidence_status": "not_assessed",
        "inference_quality": "not_assessed",
        "review_status": report.get("review_status", "pending_human_review"),
        "report_status": report.get("report_status", "unknown"),
        "next_step": "Human review is required; counts do not establish evidence quality or logical validity.",
    }
