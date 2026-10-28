"""Compare saved benchmark reports and block pass/fail regressions.

This gate compares recorded outcomes for the same case IDs. It does not assess
semantic correctness or prove that a candidate evaluator is better in general.
"""
import argparse
import json
from pathlib import Path


def _index_report(report, label):
    if not isinstance(report, dict) or not isinstance(report.get("results"), list):
        raise ValueError(f"{label} report must be an object with a results list")

    indexed = {}
    for row in report["results"]:
        if not isinstance(row, dict):
            raise ValueError(f"{label} report contains a non-object result")
        case_id = row.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{label} report contains a blank or invalid case ID")
        if case_id in indexed:
            raise ValueError(f"{label} report contains duplicate case ID: {case_id}")
        if not isinstance(row.get("passed"), bool):
            raise ValueError(f"{label} result {case_id!r} must have a boolean passed field")
        indexed[case_id] = row

    if not indexed:
        raise ValueError(f"{label} report contains no benchmark results")
    return indexed


def compare_reports(baseline, candidate):
    """Return a deterministic comparison report or raise ValueError on invalid inputs."""
    before = _index_report(baseline, "baseline")
    after = _index_report(candidate, "candidate")
    baseline_ids, candidate_ids = set(before), set(after)
    if baseline_ids != candidate_ids:
        missing = sorted(baseline_ids - candidate_ids)
        added = sorted(candidate_ids - baseline_ids)
        raise ValueError(
            "baseline and candidate must contain exactly the same case IDs; "
            f"missing from candidate: {missing}; added in candidate: {added}"
        )

    regressions = []
    improvements = []
    unchanged = []
    score_changes = []
    for case_id in sorted(baseline_ids):
        old, new = before[case_id], after[case_id]
        detail = {
            "id": case_id,
            "baseline_passed": old["passed"],
            "candidate_passed": new["passed"],
        }
        if old["passed"] and not new["passed"]:
            regressions.append(detail)
        elif not old["passed"] and new["passed"]:
            improvements.append(detail)
        else:
            unchanged.append(detail)

        old_score, new_score = old.get("actual_score"), new.get("actual_score")
        if isinstance(old_score, (int, float)) and not isinstance(old_score, bool) and isinstance(new_score, (int, float)) and not isinstance(new_score, bool):
            if old_score != new_score:
                score_changes.append({
                    "id": case_id,
                    "baseline_actual_score": old_score,
                    "candidate_actual_score": new_score,
                    "delta": new_score - old_score,
                })

    baseline_passed = sum(row["passed"] for row in before.values())
    candidate_passed = sum(row["passed"] for row in after.values())
    total = len(before)
    gate_passed = not regressions and candidate_passed >= baseline_passed
    return {
        "comparison": "saved benchmark report outcomes",
        "gate_passed": gate_passed,
        "baseline": {
            "passed": baseline_passed,
            "total": total,
            "pass_rate_percent": round(baseline_passed / total * 100, 2),
        },
        "candidate": {
            "passed": candidate_passed,
            "total": total,
            "pass_rate_percent": round(candidate_passed / total * 100, 2),
        },
        "delta": {
            "passed_cases": candidate_passed - baseline_passed,
            "pass_rate_percentage_points": round((candidate_passed - baseline_passed) / total * 100, 2),
        },
        "regressions": regressions,
        "improvements": improvements,
        "unchanged_cases": len(unchanged),
        "actual_score_changes": score_changes,
        "limitations": [
            "Case-level pass/fail outcomes are comparisons against hand-written expected labels, not semantic truth.",
            "A passing gate only means no existing case regressed and the number of passing cases did not decrease.",
            "Both reports must use the same benchmark case IDs; changes to the case set need separate review.",
            "This utility compares saved reports; it does not run two evaluator versions or create a baseline automatically.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", help="path to the saved baseline benchmark JSON report")
    parser.add_argument("candidate", help="path to the candidate benchmark JSON report")
    parser.add_argument("--output", help="optional path to write the comparison JSON")
    args = parser.parse_args(argv)

    try:
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
        report = compare_reports(baseline, candidate)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
