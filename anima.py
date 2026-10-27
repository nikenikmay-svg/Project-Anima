
def evaluate_answer(answer, required_points):
    """Evaluate an answer against a list of required points."""
    if not answer.strip():
        return {
            "score": 0,
            "feedback": "No answer provided."
        }

    matched = [
        point for point in required_points
        if point.lower() in answer.lower()
    ]

    score = round(
        len(matched) / len(required_points) * 100
    ) if required_points else 0

    return {
        "score": score,
        "matched_points": matched,
        "missing_points": [
            point for point in required_points
            if point not in matched
        ],
        "feedback": f"{score}% of required points matched."
    }


if __name__ == "__main__":
    question = "What makes a good scientific explanation?"
    answer = input(question + "\nYour answer: ")

    criteria = [
        "evidence",
        "reasoning",
        "uncertainty"
    ]

    result = evaluate_answer(answer, criteria)

    print("\n--- Anima Evaluation ---")
    print(f"Score: {result['score']}%")
    print(f"Feedback: {result['feedback']}")
    print(f"Matched: {result.get('matched_points', [])}")
    print(f"Missing: {result.get('missing_points', [])}")
  
