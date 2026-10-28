"""Build a layered summary without conflating lexical and human-review results."""
import argparse
import json
from pathlib import Path

from benchmark import run_benchmark as run_criterion_benchmark
from reasoning_indicator_benchmark import run_benchmark as run_indicator_benchmark
from compare_annotations import compare_annotations


def build_summary(reviewer_a=None, reviewer_b=None):
    criterion = run_criterion_benchmark()
    indicators = run_indicator_benchmark()
    human_review = None
    review_status = "not_provided"
    if bool(reviewer_a) != bool(reviewer_b):
        raise ValueError("provide both reviewer CSV paths, or neither")
    if reviewer_a and reviewer_b:
        human_review = compare_annotations(reviewer_a, reviewer_b)
        review_status = "comparison_generated"

    return {
        "report": "Project Anima layered evaluation summary",
        "summary_version": 1,
        "evaluation_layers": {
            "criterion_lexical_benchmark": {
                "status": "computed",
                "passed": criterion["passed"],
                "total": criterion["total"],
                "pass_rate_percent": criterion["pass_rate_percent"],
                "error_counts": criterion["error_counts"],
                "meaning": "Agreement with hand-written expected labels for criterion and contradiction heuristics.",
            },
            "reasoning_indicator_lexical_benchmark": {
                "status": "computed",
                "passed": indicators["passed"],
                "total": indicators["total"],
                "pass_rate_percent": indicators["pass_rate_percent"],
                "category_metrics": indicators["category_metrics"],
                "error_case_ids": indicators["error_case_ids"],
                "meaning": "Agreement with hand-written expected labels for configured indicator words.",
            },
            "human_review_comparison": {
                "status": review_status,
                "report": human_review,
                "meaning": (
                    "Descriptive raw agreement between two supplied reviewer worksheets; "
                    "not semantic truth, not chance-corrected reliability, and not adjudication."
                ),
            },
            "reasoning_quality_validation": {
                "status": "not_established",
                "meaning": "No automated semantic validation or independent reasoning-quality gold labels are claimed.",
            },
        },
        "limitations": [
            "The lexical datasets are small, hand-written, and not representative of general language.",
            "Lexical benchmark pass rates measure agreement with expected labels, not semantic understanding or factual correctness.",
            "Human review comparison appears only when two reviewer worksheets are supplied.",
            "Raw reviewer agreement is descriptive; it is not chance-corrected reliability and does not resolve disagreements.",
            "Human reasoning-quality validation remains unestablished unless a separate, documented study is completed.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-a", help="Optional completed worksheet from reviewer A")
    parser.add_argument("--reviewer-b", help="Optional completed worksheet from reviewer B")
    parser.add_argument("--output", default="anima-evaluation-summary.json",
                        help="Output JSON path (default: anima-evaluation-summary.json)")
    args = parser.parse_args()
    report = build_summary(args.reviewer_a, args.reviewer_b)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    Path(args.output).write_text(rendered + "\\n", encoding="utf-8")
    print(rendered)
    print(f"Saved summary to {args.output}")


if __name__ == "__main__":
    main()
