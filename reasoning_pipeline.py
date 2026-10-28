"""Combine Anima's existing criterion evaluator and indicator checklist."""
from anima import evaluate_answer
from reasoning import analyze_reasoning_indicators


def evaluate_reasoning(answer, required_points):
    """Return one report containing criterion coverage and lexical indicators.

    This composes existing transparent heuristics; it does not infer meaning or
    validate evidence, factual accuracy, or logical soundness.
    """
    criteria_report = evaluate_answer(answer, required_points)
    indicator_report = analyze_reasoning_indicators(answer)
    return {
        "criterion_evaluation": criteria_report,
        "reasoning_indicators": indicator_report,
        "overall_notice": (
            "Combined heuristic report only. Scores and detected terms do not "
            "establish that an answer is correct or logically sound."
        ),
    }
