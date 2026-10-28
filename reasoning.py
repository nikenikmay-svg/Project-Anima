"""Transparent checklist-style indicators for evidence, reasoning, and uncertainty.

These lexical indicators help inspect an answer; they do not validate logic,
evidence quality, factual accuracy, or the author's intended meaning.
"""
import re


_INDICATORS = {
    "evidence": re.compile(
        r"\b(?:evidence|data|observations?|sources?|stud(?:y|ies)|experiments?|measurements?)\b",
        re.IGNORECASE,
    ),
    "reasoning": re.compile(
        r"\b(?:because|therefore|since|implies?|suggests?|consequently|reason(?:ing)?|logic|inference|thus)\b",
        re.IGNORECASE,
    ),
    "uncertainty": re.compile(
        r"\b(?:uncertain(?:ty)?|may|might|could|likely|unlikely|estimate(?:d)?|confidence|limitation|unknown|possibly|perhaps)\b",
        re.IGNORECASE,
    ),
}


def analyze_reasoning_indicators(answer):
    """Return category-by-category lexical indicators found in an answer.

    A category is 'detected' when one of its configured terms occurs in a
    sentence-like clause. 'not_detected' means no configured term was found,
    not that the answer lacks the underlying reasoning concept.
    """
    if not isinstance(answer, str):
        raise TypeError("answer must be a string")

    clauses = [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+|\n+", answer)
        if part.strip()
    ]
    categories = {}
    for category, pattern in _INDICATORS.items():
        evidence_clauses = [clause for clause in clauses if pattern.search(clause)]
        categories[category] = {
            "status": "detected" if evidence_clauses else "not_detected",
            "evidence_clauses": evidence_clauses,
        }

    detected = [name for name, item in categories.items() if item["status"] == "detected"]
    missing = [name for name, item in categories.items() if item["status"] == "not_detected"]
    return {
        "categories": categories,
        "detected_categories": detected,
        "not_detected_categories": missing,
        "notice": (
            "Lexical indicators only: detection does not establish sound reasoning, "
            "reliable evidence, or appropriate uncertainty."
        ),
    }
