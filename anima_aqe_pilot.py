"""Run a transparent, deterministic smoke test for Anima's AQE pilot.

This script measures keyword overlap only. It does not claim to judge truth,
reasoning, or general answer quality, and it does not modify evaluator rules.
Human labels and a validated semantic/factual evaluator remain future work.
"""
from datetime import datetime, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "research_log"

CASES = [
    {
        "case_id": "A_keywords_without_support",
        "question": "Does the evidence establish that the intervention caused the improvement?",
        "answer_1": "The report shows an improvement after the intervention, but without a comparison group or other controls it does not establish causation.",
        "answer_2": "Evidence, reasoning, uncertainty, and causal proof demonstrate that the intervention caused the improvement.",
        "hypothesis": "Keyword overlap may reward an unsupported causal claim.",
    },
    {
        "case_id": "B_paraphrase_consistency",
        "question": "What should we conclude from a small observational study?",
        "answer_1": "The findings show an association, but they do not prove that one variable caused the other.",
        "answer_2": "The variables were related in this sample; the study design cannot establish cause and effect.",
        "hypothesis": "Equivalent answers with different wording may receive different overlap scores.",
    },
    {
        "case_id": "C_fluency_vs_support",
        "question": "A survey of 40 volunteers finds that 70% prefer option A. What can be concluded?",
        "answer_1": "In this volunteer sample, 70% preferred option A. The result may not represent the wider population because the sample may be biased.",
        "answer_2": "A rigorous and comprehensive survey conclusively proves that 70% of the entire population prefers option A.",
        "hypothesis": "Confident language and repeated topic terms do not establish factual support.",
    },
    {
        "case_id": "D_uncertainty_and_missing_evidence",
        "question": "What is the current policy of a specific organization?",
        "answer_1": "I cannot verify the current policy from the information provided; check the organization's current official source.",
        "answer_2": "The policy is definitely X.",
        "hypothesis": "A short answer with certainty must not be treated as correct without evidence.",
    },
]

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "but", "by",
    "can", "does", "for", "from", "in", "is", "it", "may", "not", "of",
    "on", "or", "that", "the", "their", "this", "to", "was", "what",
    "with", "without", "would", "you", "your"
}

def tokens(text):
    return {
        word for word in re.findall(r"[a-z0-9]+", text.lower())
        if word not in STOPWORDS
    }

def overlap(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)

def main():
    LOG_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = LOG_DIR / f"aqe-pilot-{today}.md"
    lines = [
        f"# AQE Pilot Smoke Test — {today} (UTC)", "",
        "**Status:** Automated smoke test completed; this is not a validation of answer quality.", "",
        "**Method:** Jaccard overlap of lowercased answer tokens after removing a small fixed stopword list.",
        "No semantic model, fact checker, human labels, or validated ground-truth dataset is used.",
        "Scores are diagnostic only and must not be interpreted as truth, relevance, or reasoning scores.", "",
        "## Results", ""
    ]
    for case in CASES:
        score = overlap(case["answer_1"], case["answer_2"])
        lines += [
            f"### {case['case_id']}",
            f"- Question: {case['question']}",
            f"- Answer 1: {case['answer_1']}",
            f"- Answer 2: {case['answer_2']}",
            f"- Keyword-overlap baseline (Jaccard): {score:.3f}",
            f"- Test hypothesis: {case['hypothesis']}",
            "- Human ratings: not collected",
            ""
        ]
    lines += [
        "## Interpretation", "",
        "- This run proves only that the script ran and produced reproducible overlap scores for the fixed examples.",
        "- A low or high overlap score alone does not identify which answer is correct.",
        "- The next meaningful validation step is independent human annotation and comparison against a pre-defined rubric.",
        "- AQE components, weights, thresholds, and evaluator behavior remain unchanged.", "",
        "## Safety boundary", "",
        "No peer response is executed. This script does not change source code, benchmark labels, or evaluator rules.", ""
    ]
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)} with {len(CASES)} fixed smoke-test cases.")

if __name__ == "__main__":
    main()
