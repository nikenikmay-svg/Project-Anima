"""Small, transparent evaluator for checking required concepts in an answer.

This is a keyword-based heuristic, not a semantic or scientific-truth judge.
It reports likely contradictions separately so keyword presence is not mistaken
for endorsement. Review the source answer when a contradiction is flagged.
"""
import re


# Conservative lexical markers. A criterion is flagged only when every clause
# mentioning it contains a marker; one clean mention prevents an automatic flag.
_CONTRADICTION_MARKERS = re.compile(
    r"\b(?:not|no|never|without|irrelevant|unnecessary|false|reject(?:s|ed)?|"
    r"disregard(?:s|ed)?|unsupported|lacks?|lack of|cannot|can't|isn't|aren't|"
    r"doesn't|don't|shouldn't)\b",
    re.IGNORECASE,
)

# Split at common contrast transitions so a marker in one clause is less likely
# to contaminate a separate claim in the same sentence.
_CONTRAST_BOUNDARY = re.compile(
    r",\s*(?=(?:but|however|yet|nevertheless)\b)|"
    r"\b(?:however|nevertheless)\b",
    re.IGNORECASE,
)


def _contains_phrase(text, phrase):
    """Match a criterion as a phrase, ignoring case and punctuation boundaries."""
    escaped = re.escape(phrase.strip())
    if not escaped:
        return False
    # Treat spaces in criteria as flexible whitespace and enforce word boundaries
    # so, for example, 'art' does not match inside 'partial'.
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.search(r"(?<!\w)" + escaped + r"(?!\w)", text, re.IGNORECASE) is not None


def _has_contradiction_marker(clause):
    """Detect configured markers while exempting the narrow phrase 'not irrelevant'.

    This exception is intentionally narrow; other forms of negation and double
    negation remain heuristic and may require contextual human review.
    """
    normalized = re.sub(r"\bnot\s+irrelevant\b", "relevant", clause, flags=re.IGNORECASE)
    return _CONTRADICTION_MARKERS.search(normalized) is not None


def _split_clauses(answer):
    """Split sentences, then conservatively separate common contrast clauses."""
    sentences = re.split(r"(?<=[.!?])\s+|\n+", answer)
    clauses = []
    for sentence in sentences:
        clauses.extend(part.strip() for part in _CONTRAST_BOUNDARY.split(sentence) if part.strip())
    return clauses


def evaluate_answer(answer, required_points):
    """Return keyword coverage plus conservative contradiction flags.

    Score is the percentage of unique required points mentioned in a clause
    without a detected contradiction marker. This remains a lexical heuristic;
    it does not assess whether the answer's reasoning is valid.
    """
    if not isinstance(answer, str):
        raise TypeError("answer must be a string")
    if not isinstance(required_points, (list, tuple)):
        raise TypeError("required_points must be a list or tuple of strings")
    if any(not isinstance(point, str) or not point.strip() for point in required_points):
        raise ValueError("required_points must contain non-empty strings")

    # Keep input order while removing duplicate criteria (case-insensitive).
    points = []
    seen = set()
    for point in required_points:
        key = point.strip().casefold()
        if key not in seen:
            seen.add(key)
            points.append(point.strip())

    if not answer.strip():
        return {
            "score": 0,
            "matched_points": [],
            "missing_points": points.copy(),
            "contradicted_points": [],
            "criterion_analysis": [
                {"criterion": point, "status": "missing", "evidence_clauses": [], "flagged_clauses": []}
                for point in points
            ],
            "feedback": "No answer provided.",
        }

    if not points:
        return {
            "score": 0,
            "matched_points": [],
            "missing_points": [],
            "contradicted_points": [],
            "criterion_analysis": [],
            "feedback": "No evaluation criteria provided; score is 0%.",
        }

    clauses = _split_clauses(answer)
    mentioned = []
    contradicted = []
    criterion_analysis = []
    for point in points:
        matching_clauses = [clause for clause in clauses if _contains_phrase(clause, point)]
        flagged_clauses = [
            clause for clause in matching_clauses if _has_contradiction_marker(clause)
        ]
        # Repeated mentions may differ: do not let one flagged mention override
        # another mention in a clause without a contradiction marker.
        if not matching_clauses:
            status = "missing"
        elif len(flagged_clauses) == len(matching_clauses):
            contradicted.append(point)
            status = "contradicted"
        else:
            mentioned.append(point)
            status = "matched"
        criterion_analysis.append({
            "criterion": point,
            "status": status,
            "evidence_clauses": matching_clauses,
            "flagged_clauses": flagged_clauses,
        })

    matched_set = {p.casefold() for p in mentioned}
    contradicted_set = {p.casefold() for p in contradicted}
    missing = [
        p for p in points
        if p.casefold() not in matched_set and p.casefold() not in contradicted_set
    ]
    score = round(len(mentioned) / len(points) * 100)

    return {
        "score": score,
        "matched_points": mentioned,
        "missing_points": missing,
        "contradicted_points": contradicted,
        "criterion_analysis": criterion_analysis,
        "feedback": (
            f"{score}% affirmed keyword coverage. "
            f"{len(contradicted)} criterion/criteria flagged for possible contradiction. "
            "This heuristic does not determine whether the answer is scientifically correct."
        ),
    }


if __name__ == "__main__":
    question = "What makes a good scientific explanation?"
    answer = input(question + "\nYour answer: ")
    criteria = ["evidence", "reasoning", "uncertainty"]
    result = evaluate_answer(answer, criteria)

    print("\n--- Anima Evaluation ---")
    print(f"Score: {result['score']}%")
    print(f"Feedback: {result['feedback']}")
    print(f"Matched: {result['matched_points']}")
    print(f"Missing: {result['missing_points']}")
    print(f"Flagged for contradiction review: {result['contradicted_points']}")
    print("\\n--- Criterion Evidence ---")
    for item in result["criterion_analysis"]:
        print(f"- {item['criterion']}: {item['status']}")
        for clause in item["evidence_clauses"]:
            print(f"    Evidence: {clause}")
        for clause in item["flagged_clauses"]:
            print(f"    Review marker detected: {clause}")
