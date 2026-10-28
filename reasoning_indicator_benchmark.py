"""Small deterministic benchmark for lexical reasoning indicators.

Expected labels are hand-written. Passing measures agreement with this small
checklist, not semantic reasoning quality.
"""
import json
from pathlib import Path

from reasoning import analyze_reasoning_indicators


CASES_PATH = Path(__file__).with_name("reasoning_indicator_cases.json")
CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))
CATEGORIES = ("evidence", "reasoning", "uncertainty")


def run_benchmark():
    results = []
    for case in CASES:
        report = analyze_reasoning_indicators(case["answer"])
        expected = case["expected_detected"]
        actual = report["detected_categories"]
        false_positive = [name for name in actual if name not in expected]
        false_negative = [name for name in expected if name not in actual]
        results.append({
            "id": case["id"],
            "expected_detected": expected,
            "actual_detected": actual,
            "passed": not false_positive and not false_negative,
            "false_positive_categories": false_positive,
            "false_negative_categories": false_negative,
        })
    passed = sum(item["passed"] for item in results)
    category_metrics = {}
    for category in CATEGORIES:
        true_positive = false_positive = false_negative = true_negative = 0
        for case, item in zip(CASES, results):
            expected = category in case["expected_detected"]
            predicted = category in item["actual_detected"]
            if expected and predicted:
                true_positive += 1
            elif predicted and not expected:
                false_positive += 1
            elif expected and not predicted:
                false_negative += 1
            else:
                true_negative += 1
        precision_denominator = true_positive + false_positive
        recall_denominator = true_positive + false_negative
        precision = true_positive / precision_denominator if precision_denominator else None
        recall = true_positive / recall_denominator if recall_denominator else None
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision is not None and recall is not None and precision + recall
            else (0.0 if precision == 0 or recall == 0 else None)
        )
        category_metrics[category] = {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "true_negative": true_negative,
            "evaluated_cases": true_positive + false_positive + false_negative + true_negative,
            "precision": round(precision, 4) if precision is not None else None,
            "recall": round(recall, 4) if recall is not None else None,
            "f1": round(f1, 4) if f1 is not None else None,
        }
    error_case_ids = {
        "false_positive": [item["id"] for item in results if item["false_positive_categories"]],
        "false_negative": [item["id"] for item in results if item["false_negative_categories"]],
    }
    return {
        "benchmark": "Anima reasoning indicator lexical baseline",
        "passed": passed,
        "total": len(results),
        "pass_rate_percent": round(passed / len(results) * 100) if results else 0,
        "error_case_ids": error_case_ids,
        "category_metrics": category_metrics,
        "results": results,
        "limitations": [
            "Expected labels are hand-written and the dataset is small.",
            "Indicators are lexical matches, not evidence of valid reasoning or factual correctness.",
            "Negated statements may still trigger an indicator by design.",
        ],
    }


if __name__ == "__main__":
    report = run_benchmark()
    rendered = json.dumps(report, indent=2)
    print(rendered)
    output_path = Path("reasoning-indicator-benchmark-results.json")
    output_path.write_text(rendered + "\n", encoding="utf-8")
    print(f"Saved report to {output_path}")
