"""Compare semantic embedding similarity with the lexical AQE baseline.

Uses fastembed's BAAI/bge-small-en-v1.5 sentence embeddings when available.
Embedding similarity measures textual semantic proximity; it does NOT establish
factual correctness. Hand-authored preferences are diagnostic only.
"""
from datetime import datetime, timezone
from pathlib import Path
import math
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
        "reference": "The results show improvement after the intervention, but without a suitable comparison or controls they do not establish causation.",
        "preferred": "cautious",
        "candidates": {
            "cautious": "The report shows improvement after the intervention, but without a comparison group or other controls it does not establish causation.",
            "overclaim": "The intervention definitely caused the improvement, and the evidence proves the causal effect."
        }
    },
    {
        "id": "B_paraphrase",
        "reference": "The variables were associated in the observed sample, but the study does not establish that one caused the other.",
        "preferred": "paraphrase",
        "candidates": {
            "reference_like": "The variables were associated in the observed sample, but the study does not establish that one caused the other.",
            "paraphrase": "The two measures moved together among participants; this design cannot show that either one produced the change in the other."
        }
    },
    {
        "id": "C_sample_scope",
        "reference": "In this volunteer sample, 70% preferred option A; the result may not represent the wider population.",
        "preferred": "scoped",
        "candidates": {
            "scoped": "In this volunteer sample, 70% preferred option A. The result may not represent the wider population because the sample may be biased.",
            "population_overclaim": "The survey conclusively proves that 70% of the entire population prefers option A."
        }
    },
    {
        "id": "D_missing_current_source",
        "reference": "The current policy cannot be verified from the information given; consult the organization's official current source.",
        "preferred": "uncertain",
        "candidates": {
            "uncertain": "I cannot verify the current policy from the information provided; check the organization's current official source.",
            "unsupported": "The current policy is definitely X."
        }
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

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0

def main():
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = LOG_DIR / f"aqe-semantic-comparison-{date}.md"
    LOG_DIR.mkdir(exist_ok=True)
    lines = [
        f"# AQE Semantic Similarity Comparison — {date} (UTC)", "",
        "**Purpose:** Compare a lexical Jaccard baseline with sentence-embedding cosine similarity.",
        "**Important:** Semantic similarity is not factual verification and cannot decide whether a claim is supported by evidence.", ""
    ]
    try:
        from fastembed import TextEmbedding
        model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        all_texts = []
        for case in CASES:
            all_texts.append(case["reference"])
            all_texts.extend(case["candidates"].values())
        vectors = list(model.embed(all_texts))
    except Exception as exc:
        lines += [
            "**Status:** Embedding model unavailable; no semantic scores were produced.",
            f"**Diagnostic:** {type(exc).__name__}: {str(exc)[:240]}",
            "The workflow records this limitation rather than substituting lexical scores for semantic ones.", ""
        ]
        output.write_text("\n".join(lines), encoding="utf-8")
        print(f"Semantic comparison skipped safely: {type(exc).__name__}")
        return

    lines += [
        "**Model:** BAAI/bge-small-en-v1.5 via fastembed.",
        "**Expected preferences:** Hand-authored for four synthetic examples; not validated labels.", "",
        "## Results", ""
    ]
    cursor = 0
    lexical_mismatches = 0
    semantic_mismatches = 0
    for case in CASES:
        ref_vector = vectors[cursor]
        cursor += 1
        scores = []
        for name, answer in case["candidates"].items():
            vector = vectors[cursor]
            cursor += 1
            scores.append({
                "name": name,
                "lexical": jaccard(answer, case["reference"]),
                "semantic": cosine(ref_vector, vector)
            })
        lex_winner = max(scores, key=lambda row: row["lexical"])["name"]
        sem_winner = max(scores, key=lambda row: row["semantic"])["name"]
        expected = case["preferred"]
        lexical_mismatches += int(lex_winner != expected)
        semantic_mismatches += int(sem_winner != expected)
        lines += [
            f"### {case['id']}",
            f"- Hand-authored preferred candidate: {expected}",
        ]
        for row in scores:
            lines.append(f"- Candidate {row['name']}: lexical={row['lexical']:.3f}; embedding_cosine={row['semantic']:.3f}")
        lines += [
            f"- Lexical top-ranked: {lex_winner} ({'mismatch' if lex_winner != expected else 'matches preference'})",
            f"- Embedding top-ranked: {sem_winner} ({'mismatch' if sem_winner != expected else 'matches preference'})", ""
        ]
    lines += [
        "## Summary", "",
        f"- Cases: {len(CASES)}",
        f"- Lexical ranking mismatches: {lexical_mismatches}",
        f"- Embedding ranking mismatches: {semantic_mismatches}",
        "- Four hand-authored examples are too few to establish general performance or statistical significance.",
        "- Embedding cosine may rate an unsupported answer as semantically close to a reference; factual support needs evidence-aware checks.",
        "- No production evaluator settings or labels were modified.", "",
        "## Decision gate", "",
        "Treat this as an exploratory comparison only. Before adoption, use a larger held-out set, independently reviewed labels, source-grounded factual checks, and documented error analysis.", ""
    ]
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)}; cases={len(CASES)}; lexical_mismatches={lexical_mismatches}; embedding_mismatches={semantic_mismatches}")

if __name__ == "__main__":
    main()
