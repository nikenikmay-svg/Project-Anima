"""Rank benchmark failures into focused, human-reviewable experiment candidates.

Ranking is a deterministic triage heuristic, not a claim about semantic importance.
It never changes source code or edits benchmark labels.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ERROR_WEIGHT = {
    "mixed_contradiction_errors": 4,
    "false_positive": 3,
    "false_negative": 3,
    "score_mismatch": 2,
    "unspecified": 1,
}
HYPOTHESIS_BY_ERROR = {
    "mixed_contradiction_errors": "A narrowly scoped change to the identified evaluator behavior may reduce both extra and missed flags for this case without causing regressions.",
    "false_positive": "A narrower detection rule may prevent the extra contradiction flag for this case while preserving existing correct cases.",
    "false_negative": "A targeted detection rule may capture the missed contradiction signal for this case without introducing extra flags.",
    "score_mismatch": "A focused scoring-rule adjustment may align this case's score with its expected label without regressing other cases.",
    "unspecified": "Inspect this case's inputs, expected labels, and evaluator trace to form a testable, narrow hypothesis.",
}


def prioritize_candidates(report, limit=None):
    if not isinstance(report, dict) or not isinstance(report.get("results"), list):
        raise ValueError("benchmark report must be an object containing a results list")
    rows = report["results"]
    seen = set()
    failures = []
    category_counts = Counter()
    error_counts = Counter()

    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("benchmark results must contain objects")
        case_id = row.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("each benchmark result must have a nonblank string id")
        if case_id in seen:
            raise ValueError(f"duplicate benchmark case ID: {case_id}")
        seen.add(case_id)
        if not isinstance(row.get("passed"), bool):
            raise ValueError(f"result {case_id!r} must have a boolean passed field")
        if row["passed"]:
            continue
        analysis = row.get("error_analysis")
        if not isinstance(analysis, dict):
            analysis = {}
        error_type = analysis.get("type", "unspecified")
        if not isinstance(error_type, str) or not error_type.strip():
            error_type = "unspecified"
        category = row.get("category", "unknown")
        if not isinstance(category, str) or not category.strip():
            category = "unknown"
        category_counts[category] += 1
        error_counts[error_type] += 1
        failures.append({
            "case_id": case_id,
            "category": category,
            "error_type": error_type,
            "priority_weight": ERROR_WEIGHT.get(error_type, 1),
            "category_failure_count": 0,
            "error_type_failure_count": 0,
            "expected_score": row.get("expected_score"),
            "actual_score": row.get("actual_score"),
            "false_positive_points": analysis.get("false_positive_points", []),
            "false_negative_points": analysis.get("false_negative_points", []),
            "hypothesis": HYPOTHESIS_BY_ERROR.get(error_type, HYPOTHESIS_BY_ERROR["unspecified"]),
            "proposed_experiment": (
                f"Create a focused regression test for {case_id}, change one behavior at a time, "
                "then run the full benchmark and regression gate."
            ),
            "requires_human_review": True,
            "source_code_changed": False,
        })

    for item in failures:
        item["category_failure_count"] = category_counts[item["category"]]
        item["error_type_failure_count"] = error_counts[item["error_type"]]

    # Prefer severe error classes, then repeatedly failing categories, then stable ID order.
    failures.sort(key=lambda item: (
        -item["priority_weight"],
        -item["category_failure_count"],
        -item["error_type_failure_count"],
        item["case_id"],
    ))
    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be positive")
        failures = failures[:limit]

    for rank, item in enumerate(failures, start=1):
        item["rank"] = rank

    return {
        "report_type": "prioritized experiment candidate queue",
        "candidate_count": len(failures),
        "ranking_method": [
            "Higher weight for mixed contradiction errors, then false positives/negatives, then score mismatches.",
            "Tie-break by how often the category fails, then error-type frequency, then case ID.",
            "This deterministic ranking is a triage aid, not a measure of truth or semantic importance.",
        ],
        "candidates": failures,
        "group_summary": {
            "by_error_type": dict(sorted(error_counts.items())),
            "by_category": dict(sorted(category_counts.items())),
        },
        "limitations": [
            "Only failing rows present in the supplied benchmark report are considered.",
            "Benchmark labels are hand-written and do not establish semantic correctness.",
            "Hypotheses are templates for human investigation, not verified fixes.",
            "No source code, expected labels, or baselines are changed.",
        ],
    }


def render_markdown(queue):
    lines = [
        "# Anima prioritized experiment candidates",
        "",
        f"Candidates requiring review: **{queue['candidate_count']}**",
        "",
        "## Ranking method",
        "",
    ]
    lines.extend(f"- {item}" for item in queue["ranking_method"])
    lines.extend(["", "## Candidates", ""])
    if not queue["candidates"]:
        lines.extend(["No failing cases were found in the supplied report.", ""])
    for item in queue["candidates"]:
        lines.extend([
            f"### {item['rank']}. {item['case_id']}",
            "",
            f"- Priority weight: {item['priority_weight']}",
            f"- Error type: {item['error_type']}",
            f"- Category: {item['category']} ({item['category_failure_count']} failing case(s))",
            f"- Expected / actual score: {item['expected_score']} / {item['actual_score']}",
            f"- Extra flags: {item['false_positive_points']}",
            f"- Missed flags: {item['false_negative_points']}",
            f"- Hypothesis: {item['hypothesis']}",
            f"- Next experiment: {item['proposed_experiment']}",
            "- Human review required; no source code changed.",
            "",
        ])
    lines.extend(["## Group summary", ""])
    lines.append(f"- By error type: {queue['group_summary']['by_error_type']}")
    lines.append(f"- By category: {queue['group_summary']['by_category']}")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in queue["limitations"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="benchmark-results.json from a completed benchmark")
    parser.add_argument("--limit", type=int, help="optional maximum number of candidates to emit")
    parser.add_argument("--json-output", default="prioritized-candidates.json")
    parser.add_argument("--markdown-output", default="prioritized-candidates.md")
    args = parser.parse_args(argv)
    try:
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
        queue = prioritize_candidates(report, args.limit)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    Path(args.json_output).write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown_output).write_text(render_markdown(queue), encoding="utf-8")
    print(f"Created {queue['candidate_count']} prioritized candidate(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
