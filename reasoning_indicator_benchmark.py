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
        "results": results,
        "limitations": [
            "Expected labels are hand-written and the dataset is small.",
            "Indicators are lexical matches, not evidence of valid reasoning or factual correctness.",
            "Negated statements may still trigger an indicator by design.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run_benchmark(), indent=2))
