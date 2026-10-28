"""Run a small, deterministic benchmark against Anima's evaluator.

The benchmark measures agreement with hand-written expected labels. It does not
measure general intelligence, semantic understanding, or scientific truth.
"""
import json
from pathlib import Path

from anima import evaluate_answer


CASES = [
    {
        "id": "all_criteria_present",
        "answer": "A good explanation uses evidence, reasoning, and uncertainty.",
        "criteria": ["evidence", "reasoning", "uncertainty"],
        "expected_score": 100,
        "expected_contradicted": [],
    },
    {
        "id": "one_criterion_missing",
        "answer": "Use evidence and reasoning to explain the result.",
        "criteria": ["evidence", "reasoning", "uncertainty"],
        "expected_score": 67,
        "expected_contradicted": [],
    },
    {
        "id": "all_criteria_explicitly_rejected",
        "answer": "Evidence, reasoning, and uncertainty are irrelevant to science.",
        "criteria": ["evidence", "reasoning", "uncertainty"],
        "expected_score": 0,
        "expected_contradicted": ["evidence", "reasoning", "uncertainty"],
    },
    {
        "id": "case_insensitive_match",
        "answer": "EVIDENCE matters.",
        "criteria": ["evidence"],
        "expected_score": 100,
        "expected_contradicted": [],
    },
    {
        "id": "substring_false_positive",
        "answer": "Partial results were reported.",
        "criteria": ["art"],
        "expected_score": 0,
        "expected_contradicted": [],
    },
    {
        "id": "empty_answer",
        "answer": "",
        "criteria": ["evidence"],
        "expected_score": 0,
        "expected_contradicted": [],
    },
    {
        "id": "contradiction_marker_flags_criterion",
        "answer": "There is no evidence for this claim.",
        "criteria": ["evidence"],
        "expected_score": 0,
        "expected_contradicted": ["evidence"],
    },
    {
        "id": "unrelated_sentence_does_not_flag",
        "answer": "Evidence supports the claim. Uncertainty remains about the timing.",
        "criteria": ["evidence", "uncertainty"],
        "expected_score": 100,
        "expected_contradicted": [],
    },
    {
        "id": "repeated_criterion_mixed_mentions",
        "answer": "Evidence is not available yet. Later evidence supports the conclusion.",
        "criteria": ["evidence"],
        "expected_score": 100,
        "expected_contradicted": [],
    },
    {
        "id": "contrast_clause_scope",
        "answer": "There is no evidence for the claim, but reasoning supports the conclusion.",
        "criteria": ["evidence", "reasoning"],
        "expected_score": 50,
        "expected_contradicted": ["evidence"],
    },
    {
        "id": "negation_marker_in_same_clause",
        "answer": "Evidence is not irrelevant to the conclusion.",
        "criteria": ["evidence"],
        "expected_score": 0,
        "expected_contradicted": ["evidence"],
    },
    {
        "id": "clean_repeat_offsets_flagged_repeat",
        "answer": "Evidence is unavailable. New evidence supports the conclusion.",
        "criteria": ["evidence"],
        "expected_score": 100,
        "expected_contradicted": [],
    },
    {
        "id": "semicolon_does_not_scope_marker",
        "answer": "The claim is not established; evidence supports the result.",
        "criteria": ["evidence"],
        "expected_score": 0,
        "expected_contradicted": ["evidence"],
    },
    {
        "id": "multiple_criteria_with_mixed_polarity",
        "answer": "Evidence is absent, but reasoning supports the conclusion.",
        "criteria": ["evidence", "reasoning", "uncertainty"],
        "expected_score": 33,
        "expected_contradicted": ["evidence"],
    },
    {
        "id": "word_boundary_prevents_embedded_match",
        "answer": "The artwork was discussed without scientific support.",
        "criteria": ["art", "evidence"],
        "expected_score": 0,
        "expected_contradicted": [],
    },
]


def run_benchmark():
    results = []
    for case in CASES:
        actual = evaluate_answer(case["answer"], case["criteria"])
        actual_contradicted = actual["contradicted_points"]
        passed = (
            actual["score"] == case["expected_score"]
            and actual_contradicted == case["expected_contradicted"]
        )
        results.append({
            "id": case["id"],
            "passed": passed,
            "expected_score": case["expected_score"],
            "actual_score": actual["score"],
            "expected_contradicted": case["expected_contradicted"],
            "actual_contradicted": actual_contradicted,
            "criterion_analysis": actual["criterion_analysis"],
        })

    passed_count = sum(item["passed"] for item in results)
    report = {
        "benchmark": "Anima lexical evaluator baseline",
        "passed": passed_count,
        "total": len(results),
        "pass_rate_percent": round(passed_count / len(results) * 100) if results else 0,
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
