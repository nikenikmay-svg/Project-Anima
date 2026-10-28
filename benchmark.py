"""Run a small, deterministic benchmark against Anima's evaluator.

The benchmark measures agreement with hand-written expected labels. It does not
measure general intelligence, semantic understanding, or scientific truth.
"""
import json
from pathlib import Path

from anima import evaluate_answer


CASES_PATH = Path(__file__).with_name("benchmark_cases.json")
CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))



def run_benchmark():
    results = []
    for case in CASES:
        actual = evaluate_answer(case["answer"], case["criteria"])
        actual_contradicted = actual["contradicted_points"]
        expected_contradicted = case["expected_contradicted"]
        false_positive_points = [
            point for point in actual_contradicted if point not in expected_contradicted
        ]
        false_negative_points = [
            point for point in expected_contradicted if point not in actual_contradicted
        ]
        score_mismatch = actual["score"] != case["expected_score"]
        passed = not false_positive_points and not false_negative_points and not score_mismatch

        if false_positive_points and false_negative_points:
            error_type = "mixed_contradiction_errors"
        elif false_positive_points:
            error_type = "false_positive"
        elif false_negative_points:
            error_type = "false_negative"
        elif score_mismatch:
            error_type = "score_mismatch"
        else:
            error_type = "correct"

        results.append({
            "id": case["id"],
            "passed": passed,
            "expected_score": case["expected_score"],
            "actual_score": actual["score"],
            "expected_contradicted": expected_contradicted,
            "actual_contradicted": actual_contradicted,
            "error_analysis": {
                "type": error_type,
                "false_positive_points": false_positive_points,
                "false_negative_points": false_negative_points,
                "score_mismatch": score_mismatch,
            },
            "criterion_analysis": actual["criterion_analysis"],
        })

    passed_count = sum(item["passed"] for item in results)
    error_counts = {
        kind: sum(item["error_analysis"]["type"] == kind for item in results)
        for kind in ("correct", "false_positive", "false_negative", "mixed_contradiction_errors", "score_mismatch")
    }

    criterion_names = sorted({
        point
        for case in CASES
        for point in case["criteria"]
    })
    criterion_error_counts = {}
    criterion_metrics = {}
    for criterion in criterion_names:
        true_positive = false_positive = false_negative = true_negative = 0
        for case, item in zip(CASES, results):
            # Only score a criterion in cases where it was requested.
            if criterion not in case["criteria"]:
                continue
            expected = criterion in case["expected_contradicted"]
            predicted = criterion in item["actual_contradicted"]
            if expected and predicted:
                true_positive += 1
            elif predicted and not expected:
                false_positive += 1
            elif expected and not predicted:
                false_negative += 1
            else:
                true_negative += 1
        criterion_error_counts[criterion] = {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "true_negative": true_negative,
            "evaluated_cases": true_positive + false_positive + false_negative + true_negative,
        }
        precision_denominator = true_positive + false_positive
        recall_denominator = true_positive + false_negative
        specificity_denominator = true_negative + false_positive
        precision = true_positive / precision_denominator if precision_denominator else None
        recall = true_positive / recall_denominator if recall_denominator else None
        specificity = true_negative / specificity_denominator if specificity_denominator else None
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision is not None and recall is not None and precision + recall
            else (0.0 if precision == 0 or recall == 0 else None)
        )
        criterion_metrics[criterion] = {
            "precision": round(precision, 4) if precision is not None else None,
            "recall": round(recall, 4) if recall is not None else None,
            "f1": round(f1, 4) if f1 is not None else None,
            "specificity": round(specificity, 4) if specificity is not None else None,
        }

    report = {
        "benchmark": "Anima lexical evaluator baseline",
        "passed": passed_count,
        "total": len(results),
        "pass_rate_percent": round(passed_count / len(results) * 100) if results else 0,
        "error_counts": error_counts,
        "criterion_error_counts": criterion_error_counts,
        "criterion_metrics": criterion_metrics,
        "results": results,
        "limitations": [
            "Cases are hand-written and small; they are not a representative language dataset.",
            "Passing means matching expected labels, not understanding meaning.",
            "Negation and contradiction detection is heuristic and can make false positives or false negatives.",
            "Contrast splitting handles a few common patterns only and does not resolve general linguistic scope.",
        ],
    }
    return report


if __name__ == "__main__":
    report = run_benchmark()
    print(json.dumps(report, indent=2))
    output_path = Path("benchmark-results.json")
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Saved report to {output_path}")
    raise SystemExit(0 if report["passed"] == report["total"] else 1)
