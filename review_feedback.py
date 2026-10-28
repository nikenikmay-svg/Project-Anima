"""Validate human-reviewed feedback and export proposed regression cases.

This tool never edits benchmark_cases.json or changes evaluator behavior. It only
exports approved, explicitly human-verified feedback as a separate JSON file.
"""
import argparse
import json
from pathlib import Path

ALLOWED_STATUSES = {"pending", "approved", "rejected"}


def load_feedback(path):
    """Load and validate a feedback JSON list."""
    try:
        items = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read feedback JSON: {exc}") from exc
    if not isinstance(items, list):
        raise ValueError("feedback document must be a JSON list")
    seen = set()
    for index, item in enumerate(items):
        prefix = f"feedback item {index}"
        if not isinstance(item, dict):
            raise ValueError(f"{prefix} must be an object")
        required = {
            "id", "answer", "criteria", "expected_score",
            "expected_contradicted", "category", "status",
            "human_verified", "reviewer_rationale",
        }
        missing = sorted(required - set(item))
        if missing:
            raise ValueError(f"{prefix} is missing required fields: {missing}")
        case_id = item["id"]
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{prefix} id must be a nonblank string")
        if case_id in seen:
            raise ValueError(f"duplicate feedback id: {case_id}")
        seen.add(case_id)
        if not isinstance(item["answer"], str):
            raise ValueError(f"{prefix} answer must be a string")
        if not isinstance(item["criteria"], list) or not all(
            isinstance(value, str) and value.strip() for value in item["criteria"]
        ):
            raise ValueError(f"{prefix} criteria must be a list of nonblank strings")
        score = item["expected_score"]
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
            raise ValueError(f"{prefix} expected_score must be an integer from 0 to 100")
        contradicted = item["expected_contradicted"]
        if not isinstance(contradicted, list) or not all(
            isinstance(value, str) and value in item["criteria"] for value in contradicted
        ):
            raise ValueError(f"{prefix} expected_contradicted must contain only requested criteria")
        if len(contradicted) != len(set(contradicted)):
            raise ValueError(f"{prefix} expected_contradicted must not contain duplicates")
        if item["category"] != "human_reviewed":
            raise ValueError(f"{prefix} category must be 'human_reviewed'")
        if item["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"{prefix} status must be one of {sorted(ALLOWED_STATUSES)}")
        if not isinstance(item["human_verified"], bool):
            raise ValueError(f"{prefix} human_verified must be a boolean")
        if not isinstance(item["reviewer_rationale"], str) or not item["reviewer_rationale"].strip():
            raise ValueError(f"{prefix} reviewer_rationale must be nonblank")
    return items


def approved_feedback_to_cases(items, existing_ids=()):
    """Return benchmark-shaped cases only for approved, human-verified feedback."""
    existing = set(existing_ids)
    exported = []
    for item in items:
        if item["status"] != "approved" or item["human_verified"] is not True:
            continue
        if item["id"] in existing:
            raise ValueError(f"feedback id already exists in baseline benchmark: {item['id']}")
        existing.add(item["id"])
        exported.append({
            "id": item["id"],
            "answer": item["answer"],
            "criteria": list(item["criteria"]),
            "expected_score": item["expected_score"],
            "expected_contradicted": list(item["expected_contradicted"]),
            "category": "human_reviewed",
        })
    return exported


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feedback_json", help="JSON list of human feedback records")
    parser.add_argument("--output", required=True, help="Path for exported candidate cases")
    parser.add_argument(
        "--existing-benchmark", default="benchmark_cases.json",
        help="Baseline benchmark used to prevent duplicate case IDs",
    )
    args = parser.parse_args()
    try:
        feedback = load_feedback(args.feedback_json)
        baseline = json.loads(Path(args.existing_benchmark).read_text(encoding="utf-8"))
        if not isinstance(baseline, list):
            raise ValueError("existing benchmark must be a JSON list")
        existing_ids = [item.get("id") for item in baseline if isinstance(item, dict)]
        candidates = approved_feedback_to_cases(feedback, existing_ids)
        Path(args.output).write_text(
            json.dumps(candidates, indent=2, ensure_ascii=False) + "\\n",
            encoding="utf-8",
        )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"Exported {len(candidates)} approved candidate case(s) to {args.output}.")
    print("Review the output and merge cases into the baseline only through a separate reviewed change.")


if __name__ == "__main__":
    main()
