"""Smoke-test the claim audit rules; results are not semantic accuracy metrics."""
import json
from pathlib import Path

from reasoning_audit import audit_claim

CASES_PATH = Path(__file__).with_name("reasoning_audit_cases.json")
DEFAULT_OUTPUT = Path("reasoning-audit-report.json")


def run_benchmark(output_path=DEFAULT_OUTPUT):
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    results = []
    passed = 0
    rule_counts = {}
    for case in cases:
        report = audit_claim(case["prompt"], case["claim"], case["context"])
        observed = sorted(item["rule"] for item in report["review_flags"])
        expected = sorted(case["expected_review_flags"])
        matches = observed == expected
        passed += int(matches)
        for rule in observed:
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
        results.append({
            "id": case["id"],
            "expected_review_flags": expected,
            "observed_review_flags": observed,
            "smoke_test_passed": matches,
            "semantic_assessment": report["semantic_assessment"],
        })
    report = {
        "report": "Anima claim-audit prototype smoke tests",
        "passed": passed,
        "total": len(cases),
        "pass_rate_percent": round(100 * passed / len(cases), 2) if cases else 0,
        "rule_trigger_counts": rule_counts,
        "results": results,
        "interpretation": "Pass rate measures agreement with this small rule-smoke-test set, not semantic reasoning quality.",
        "semantic_validation": "not_established",
    }
    Path(output_path).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    report = run_benchmark()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Saved report to {DEFAULT_OUTPUT}")
    raise SystemExit(0 if report["passed"] == report["total"] else 1)
