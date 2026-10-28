"""Turn benchmark failures into a human-reviewable improvement queue.

This tool suggests investigation areas only. It never edits source code or labels
a proposed change as correct without testing and human review.
"""
import argparse
import json
from pathlib import Path


def build_proposals(report):
    if not isinstance(report, dict) or not isinstance(report.get("results"), list):
        raise ValueError("benchmark report must be an object containing a results list")

    seen = set()
    proposals = []
    for row in report["results"]:
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
        focus_by_type = {
            "false_positive": "Inspect why the evaluator flagged a criterion not present in the expected contradiction labels.",
            "false_negative": "Inspect why an expected contradicted criterion was not flagged.",
            "mixed_contradiction_errors": "Review both extra and missed contradiction flags; isolate one behavior at a time.",
            "score_mismatch": "Compare the expected score with criterion coverage and scoring rules.",
        }
        proposals.append({
            "case_id": case_id,
            "category": row.get("category", "unknown"),
            "error_type": error_type,
            "priority": "high" if error_type in {"mixed_contradiction_errors", "false_positive", "false_negative"} else "normal",
            "actual_score": row.get("actual_score"),
            "expected_score": row.get("expected_score"),
            "false_positive_points": analysis.get("false_positive_points", []),
            "false_negative_points": analysis.get("false_negative_points", []),
            "proposed_investigation": focus_by_type.get(
                error_type,
                "Inspect the case inputs, expected labels, and evaluator trace to identify the smallest reproducible issue.",
            ),
            "required_human_review": True,
            "source_code_changed": False,
        })

    return {
        "report_type": "human-reviewable improvement proposal queue",
        "proposal_count": len(proposals),
        "proposals": proposals,
        "limitations": [
            "Proposals are debugging suggestions derived from recorded benchmark errors, not verified fixes.",
            "No source code is generated, modified, or applied by this tool.",
            "Expected labels are hand-written and do not establish semantic truth.",
            "A reviewer should reproduce the case, assess the label, add a focused regression test, and run the full suite before proposing a change.",
        ],
    }


def render_markdown(queue):
    lines = [
        "# Anima improvement proposal queue",
        "",
        f"Proposals requiring human review: **{queue['proposal_count']}**",
        "",
        "These are investigation suggestions, not verified fixes. No source code was changed.",
        "",
    ]
    if not queue["proposals"]:
        lines.extend([
            "No failing cases were found in this benchmark report.",
            "",
            "This means the current evaluator matched this small set of hand-written labels; it does not prove semantic reasoning quality.",
        ])
    for item in queue["proposals"]:
        lines.extend([
            f"## {item['case_id']} — {item['error_type']}",
            "",
            f"- Category: {item['category']}",
            f"- Priority: {item['priority']}",
            f"- Expected score: {item['expected_score']}; actual score: {item['actual_score']}",
            f"- Investigation: {item['proposed_investigation']}",
            f"- Extra contradiction flags: {item['false_positive_points']}",
            f"- Missed contradiction flags: {item['false_negative_points']}",
            "- Human review required: yes",
            "",
        ])
    lines.extend(["## Limitations", ""])
    lines.extend(f"- {item}" for item in queue["limitations"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="benchmark JSON report path")
    parser.add_argument("--json-output", default="improvement-proposals.json")
    parser.add_argument("--markdown-output", default="improvement-proposals.md")
    args = parser.parse_args(argv)
    try:
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
        queue = build_proposals(report)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    Path(args.json_output).write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown_output).write_text(render_markdown(queue), encoding="utf-8")
    print(f"Created {queue['proposal_count']} human-reviewable proposal(s).")
    print(f"JSON: {args.json_output}")
    print(f"Markdown: {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
