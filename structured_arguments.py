"""Small schema validator for explicitly supplied argument structures.

This module checks structure only. It does not judge whether premises are true,
relevant, sufficient, or whether the conclusion follows logically.
"""
from __future__ import annotations

from typing import Any

_REQUIRED_KEYS = {"id", "premises", "conclusion"}


def validate_argument(argument: Any) -> dict[str, Any]:
    """Return a stable validation report for one argument mapping."""
    errors: list[str] = []
    if not isinstance(argument, dict):
        return {
            "valid": False,
            "errors": ["argument must be a JSON object / Python dict"],
            "premise_count": 0,
            "conclusion_present": False,
            "logical_validity": "not_assessed",
        }

    missing = sorted(_REQUIRED_KEYS - set(argument))
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))

    identifier = argument.get("id")
    if not isinstance(identifier, str) or not identifier.strip():
        errors.append("id must be a non-empty string")

    premises = argument.get("premises")
    if not isinstance(premises, list):
        errors.append("premises must be a list of non-empty strings")
        premise_count = 0
    else:
        premise_count = len(premises)
        if not premises:
            errors.append("premises must contain at least one premise")
        for index, premise in enumerate(premises):
            if not isinstance(premise, str) or not premise.strip():
                errors.append(f"premises[{index}] must be a non-empty string")

    conclusion = argument.get("conclusion")
    conclusion_present = isinstance(conclusion, str) and bool(conclusion.strip())
    if not conclusion_present:
        errors.append("conclusion must be a non-empty string")

    return {
        "valid": not errors,
        "errors": errors,
        "argument_id": identifier.strip() if isinstance(identifier, str) else None,
        "premise_count": premise_count,
        "conclusion_present": conclusion_present,
        "logical_validity": "not_assessed",
    }


def validate_arguments(arguments: Any) -> dict[str, Any]:
    """Validate a collection and reject malformed top-level input."""
    if not isinstance(arguments, list):
        return {
            "valid": False,
            "errors": ["arguments must be a list"],
            "results": [],
            "logical_validity": "not_assessed",
        }
    results = [validate_argument(item) for item in arguments]
    ids = [r.get("argument_id") for r in results if r.get("argument_id")]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    errors = []
    if duplicates:
        errors.append("duplicate argument ids: " + ", ".join(duplicates))
    return {
        "valid": not errors and all(item["valid"] for item in results),
        "errors": errors,
        "results": results,
        "logical_validity": "not_assessed",
    }
