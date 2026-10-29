"""Run a fixed AQE benchmark against a lexical-overlap baseline.

This is diagnostic, not a validated answer-quality evaluator. Preferences are
hand-authored for synthetic examples. No external AI response is executed and
this script never changes evaluator code or labels.
"""
from datetime import datetime, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "research_log"
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "but", "by",
    "can", "does", "for", "from", "in", "is", "it", "may", "not", "of",
    "on", "or", "that", "the", "their", "this", "to", "was", "what",
    "with", "without", "would", "you", "your", "we", "our", "they"
}

CASES = [
    {
        "id": "A_causal_overclaim",
        "question": "Does the evidence establish that the intervention caused the improvement?",
        "reference": "The results show improvement after the intervention, but without a suitable comparison or controls they do not establish causation.",
        "preferred": "cautious",
        "candidates": {
            "cautious": "The report shows improvement after the intervention, but without a comparison group or other controls it does not establish causation.",
            "overclaim": "The intervention definitely caused the improvement, and the evidence proves the causal effect."
        },
        "lesson": "Lexical similarity can reward topic words while missing an unsupported causal claim."
    },
    {
        "id": "B_paraphrase",
        "question": "What can an observational study conclude?",
        "reference": "The variables were associated in the observed sample, but the study does not establish that one caused the other.",
        "preferred": "paraphrase",
        "candidates": {
            "reference_like": "The variables were associated in the observed sample, but the study does not establish that one caused the other.",
            "paraphrase": "The two measures moved together among participants; this design cannot show that either one produced the change in the other."
        },
        "lesson": "A sound paraphrase may receive a lower lexical score despite preserving the key limitation."
    },
    {
        "id": "C_sample_scope",
        "question": "A survey of 40 volunteers finds that 70% prefer option A. What can be concluded?",
        "reference": "In this volunteer sample, 70% preferred option A; the result may not represent the wider population.",
        "preferred": "scoped",
        "candidates": {
            "scoped": "In this volunteer sample, 70% preferred option A. The result may not represent the wider population because the sample may be biased.",
            "population_overclaim": "The survey conclusively proves that 70% of the entire population prefers option A."
        },
        "lesson": "Repeating the statistic does not justify generalizing from volunteers to the whole population."
    },
    {
        "id": "D_missing_current_source",
        "question": "What is the current policy of a named organization?",
        "reference": "The current policy cannot be verified from the information given; consult the organization's official current source.",
        "preferred": "uncertain",
        "candidates": {
            "uncertain": "I cannot verify the current policy from the information provided; check the organization's current official source.",
            "unsupported": "The current policy is definitely X."
        },
        "lesson": "When current evidence is absent, a confident unsupported answer should not be treated as correct."
    }
]

def tokens(text):
    return {
        word for word in re.findall(r"[a-z0-9]+", text.lower())
        if word not in STOPWORDS
    }

def jaccard(a, b):
    left, right = tokens(a), tokens(b)
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)

def main():
    LOG_DIR.mkdir(exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = LOG_DIR / f"aqe-benchmark-{date}.md"
    lines = [
        f"# AQE Benchmark Diagnostic — {date} (UTC)", "",
        "**Status:** Fixed synthetic benchmark executed. This is not a validated evaluator or a human study.", "",
        "**Baseline:** Jaccard overlap between each candidate answer and a human-authored reference answer.",
        "Expected preferences are explicitly hand-authored for these four examples; they are not learned labels.",
        "The baseline measures word overlap only and cannot establish truth or factual correctness.", "",
        "## Results", ""
    ]
    failures = 0
    for case in CASES:
        scored = [(name, jaccard(answer, case["reference"])) for name, answer in case["candidates"].items()]
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)
        winner = ranked[0][0]
        expected = case["preferred"]
        mismatch = winner != expected
        failures += int(mismatch)
        lines += [
            f"### {case['id']}", f"- Question: {case['question']}",
            f"- Reference: {case['reference']}",
            f"- Hand-authored preferred answer: {expected}",
        ]
        for name, score in scored:
            lines.append(f"- Candidate {name} lexical similarity: {score:.3f}")
        lines += [
            f"- Lexical baseline top-ranked candidate: {winner}",
            f"- Ranking agrees with hand-authored preference: {'NO — baseline failure' if mismatch else 'yes'}",
            f"- Diagnostic lesson: {case['lesson']}", ""
        ]
    lines += [
        "## Summary", "",
        f"- Cases run: {len(CASES)}",
        f"- Baseline ranking mismatches: {failures}",
        "- This small synthetic set is designed to expose known lexical-overlap failure modes, not estimate real-world accuracy.",
        "- No semantic embedding, fact checker, external service, or human rater was used.",
        "- A zero-mismatch result would still not validate the method; these cases are small and hand-authored.", "",
        "## Safety and next steps", "",
        "- Peer-agent output remains untrusted data and is never executed.",
        "- Do not change production evaluator rules based on this report alone.",
        "- Next validation: independent human ratings on a larger held-out set, plus verified sources and documented implementations.", ""
    ]
    output.write_text("\\n".join(lines), encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)}; cases={len(CASES)}; baseline_mismatches={failures}")

if __name__ == "__main__":
    main()
