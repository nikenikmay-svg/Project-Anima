"""Transparent evidence mapping and counterexample prompts for argument review.

These helpers organize reviewer-supplied information. They do not infer semantic
support, discover hidden premises, or prove/disprove an argument.
"""
from __future__ import annotations

from typing import Any


def review_argument(
    argument: Any,
    evidence_by_premise: Any = None,
    unstated_assumptions: Any = None,
    counterexamples: Any = None,
) -> dict[str, Any]:
    """Build a review report without inventing evidence or human judgments.

    evidence_by_premise maps 1-based premise positions as strings (for example,
    "1" for the first premise) to lists of evidence descriptions/identifiers.
    Assumptions and counterexamples are reviewer-supplied text, not generated claims.
    """
    from structured_arguments import validate_argument

    validation = validate_argument(argument)
    report: dict[str, Any] = {
        "argument_validation": validation,
        "premise_evidence": [],
        "unstated_assumptions": [],
        "counterexamples": [],
        "input_warnings": [],
        "conclusion_evidence_status": "not_assessed",
        "inference_quality": "not_assessed",
        "review_status": "pending_human_review",
        "limitations": [
            "Evidence entries are supplied by the caller; this tool does not verify sources or entailment.",
            "An absent evidence entry means none was supplied here, not that no evidence exists.",
            "Assumptions and counterexamples are recorded, not automatically discovered or judged.",
            "Inference quality and conclusion truth remain not_assessed.",
        ],
    }
    if not validation["valid"]:
        report["report_status"] = "invalid_argument_structure"
        return report

    premises = argument["premises"]
    if evidence_by_premise is None:
        evidence_map = {}
    elif isinstance(evidence_by_premise, dict):
        evidence_map = evidence_by_premise
    else:
        evidence_map = {}
        report["input_warnings"].append(
            "evidence_by_premise must be an object keyed by 1-based premise positions; no evidence entries were read."
        )

    valid_keys = {str(index) for index in range(1, len(premises) + 1)}
    for key in evidence_map:
        if not isinstance(key, str) or key not in valid_keys:
            report["input_warnings"].append(
                f"Evidence key {key!r} does not match a 1-based premise position; its entries were not used."
            )

    for index, premise in enumerate(premises, start=1):
        premise_id = str(index)
        supplied = evidence_map.get(premise_id, [])
        if not isinstance(supplied, list):
            report["input_warnings"].append(
                f"Evidence for premise {index} must be a list; its entries were not used."
            )
            supplied = []
        cleaned = []
        for item in supplied:
            if isinstance(item, str) and item.strip():
                cleaned.append(item.strip())
            else:
                report["input_warnings"].append(
                    f"Premise {index} contains an empty or non-text evidence item; that item was ignored."
                )
        report["premise_evidence"].append({
            "premise_index": index,
            "premise": premise,
            "evidence_items": cleaned,
            "evidence_supplied": bool(cleaned),
            "support_assessment": "not_assessed",
        })

    if isinstance(unstated_assumptions, list):
        report["unstated_assumptions"] = [
            item.strip() for item in unstated_assumptions
            if isinstance(item, str) and item.strip()
        ]
    elif unstated_assumptions is not None:
        report["input_warnings"].append("unstated_assumptions must be a list of non-empty text items.")

    if isinstance(counterexamples, list):
        report["counterexamples"] = [
            item.strip() for item in counterexamples
            if isinstance(item, str) and item.strip()
        ]
    elif counterexamples is not None:
        report["input_warnings"].append("counterexamples must be a list of non-empty text items.")

    report["report_status"] = "ready_for_human_review"
    report["review_prompts"] = [
        "For each premise, do the cited items actually support that premise?",
        "Are the sources reliable, relevant, current, and accurately represented?",
        "What assumptions connect the premises to the conclusion?",
        "Can the premises be true while the conclusion is false?",
        "What alternative explanations or counterexamples should be considered?",
    ]
    return report
