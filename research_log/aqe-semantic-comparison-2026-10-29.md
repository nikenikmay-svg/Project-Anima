# AQE Semantic Similarity Comparison — 2026-10-29 (UTC)

**Purpose:** Compare a lexical Jaccard baseline with sentence-embedding cosine similarity.
**Important:** Semantic similarity is not factual verification and cannot decide whether a claim is supported by evidence.

**Model:** BAAI/bge-small-en-v1.5 via fastembed.
**Expected preferences:** Hand-authored for four synthetic examples; not validated labels.

## Results

### A_causal_overclaim
- Hand-authored preferred candidate: cautious
- Candidate cautious: lexical=0.467; embedding_cosine=0.921
- Candidate overclaim: lexical=0.118; embedding_cosine=0.643
- Lexical top-ranked: cautious (matches preference)
- Embedding top-ranked: cautious (matches preference)

### B_paraphrase
- Hand-authored preferred candidate: paraphrase
- Candidate reference_like: lexical=1.000; embedding_cosine=1.000
- Candidate paraphrase: lexical=0.091; embedding_cosine=0.742
- Lexical top-ranked: reference_like (mismatch)
- Embedding top-ranked: reference_like (mismatch)

### C_sample_scope
- Hand-authored preferred candidate: scoped
- Candidate scoped: lexical=0.900; embedding_cosine=0.962
- Candidate population_overclaim: lexical=0.214; embedding_cosine=0.717
- Lexical top-ranked: scoped (matches preference)
- Embedding top-ranked: scoped (matches preference)

### D_missing_current_source
- Hand-authored preferred candidate: uncertain
- Candidate uncertain: lexical=0.533; embedding_cosine=0.886
- Candidate unsupported: lexical=0.154; embedding_cosine=0.549
- Lexical top-ranked: uncertain (matches preference)
- Embedding top-ranked: uncertain (matches preference)

## Summary

- Cases: 4
- Lexical ranking mismatches: 1
- Embedding ranking mismatches: 1
- Four hand-authored examples are too few to establish general performance or statistical significance.
- Embedding cosine may rate an unsupported answer as semantically close to a reference; factual support needs evidence-aware checks.
- No production evaluator settings or labels were modified.

## Decision gate

Treat this as an exploratory comparison only. Before adoption, use a larger held-out set, independently reviewed labels, source-grounded factual checks, and documented error analysis.
