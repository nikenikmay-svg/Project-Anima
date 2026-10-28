"""Small, transparent evaluator for checking required concepts in an answer.

This is a keyword-based heuristic, not a semantic or scientific-truth judge.
It reports likely contradictions separately so keyword presence is not mistaken
for endorsement. Review the source answer when a contradiction is flagged.
"""
import re


# Conservative sentence-level markers. If one appears in a clause, criteria
# found in that clause are flagged for review rather than counted as affirmed.
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
            "feedback": "No answer provided.",
        }

    if not points:
        return {
            "score": 0,
            "matched_points": [],
            "missing_points": [],
            "contradicted_points": [],
            "feedback": "No evaluation criteria provided; score is 0%.",
        }

    clauses = _split_clauses(answer)
    mentioned = []
    contradicted = []
    for point in points:
        matching_clauses = [clause for clause in clauses if _contains_phrase(clause, point)]
        if not matching_clauses:
            continue
        if any(_CONTRADICTION_MARKERS.search(clause) for clause in matching_clauses):
            contradicted.append(point)
        else:
            mentioned.append(point)

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
