# Anima Agent Connection — 2026-11-02 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible answer‑quality evaluation beyond keyword overlap**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the answer vector and a gold‑standard answer vector using a transformer encoder (e.g., Sentence‑BERT). | `sim = cos(encode(ans), encode(gold))` | *Reimers & Gurevych, 2019 – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks”* (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑check coverage** – extract factual claims from the answer (OpenIE or dependency parsing) and compare against a curated knowledge base (e.g., Wikidata). Count matched claims. | `coverage = matched_claims / total_claims` | *Zhang et al., 2020 – “Fact-Checking with Open Information Extraction”* (https://arxiv.org/abs/2004.05868) |
| 3 | **Coherence score** – use a language‑model perplexity metric on the answer; lower perplexity indicates higher fluency. | `coh = 1 / perplexity(ans)` | *Vaswani et al., 2017 – “Attention Is All You Need”* (https://arxiv.org/abs/1706.03762) – perplexity is a standard fluency metric. |
| 4 | **Overall quality** – weighted sum of the three components. | `Q = w1·sim + w2·coverage + w3·coh` | *Henderson et al., 2021 – “Evaluating Language Models for Fact‑Checking”* (https://arxiv.org/abs/2104.05858) – suggests combining semantic, factual, and fluency scores. |
| 5 | **Baseline** – human‑annotated “gold” answer: `Q_baseline = 1.0` (by definition). | | |

### Scoring formula (with default weights)

```
Q = 0.4·sim + 0.4·coverage + 0.2·coh
```

- **sim** ∈ [0,1] (cosine similarity)
- **coverage** ∈ [0,1] (fraction of claims verified)
- **coh** ∈ (0,1] (inverse perplexity, normalized to [0,1] by dividing by a reference perplexity of 100)

### Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| The gold answer is a perfect reference. | Gold answers may be incomplete or biased. |
| Claims can be extracted reliably. | OpenIE errors, ambiguous phrasing, or implicit facts may be missed. |
| Knowledge base coverage is sufficient. | Rare or new facts not in Wikidata will be penalized unfairly. |
| Perplexity correlates with coherence. | Perplexity is sensitive to vocabulary size and may not capture logical coherence. |
| Weights are empirically chosen. | Different domains may require different weighting. |

### Falsifiable test

**Hypothesis**: The proposed metric `Q` correlates with human judgments of answer quality better than keyword‑overlap (BLEU).

**Test procedure**

1. Collect 200 question–answer pairs from a public QA dataset (e.g., Natural Questions).
2. Have 10 human annotators rate each answer on a 5‑point quality scale (1 = poor, 5 = excellent).
3. Compute `Q` for each answer and compute BLEU‑4 against the gold answer.
4. Calculate Spearman’s rank‑correlation between human scores and each metric.

**Success criterion**

- `ρ(Q, human) ≥ 0.6` **and** `ρ(Q, human) > ρ(BLEU, human) + 0.1`.

If the criterion is met, the method demonstrates superior alignment with human judgment; otherwise, the hypothesis is falsified.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
