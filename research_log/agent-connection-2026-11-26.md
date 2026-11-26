# Anima Agent Connection — 2026-11-26 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Evaluation of Answer Quality (beyond keyword overlap)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity to reference** | `Sim_sem = cosine(embedding(answer), embedding(reference))` | *BERTScore* paper (Zhang et al., 2020) – https://arxiv.org/abs/2004.09843 |
| 2 | **Factual consistency** | `Fact = 1` if all extracted facts in answer are verified by trusted sources, else `0`. Verification via *FactCC* (Wang et al., 2020) – https://arxiv.org/abs/2005.12141 | |
| 3 | **Coherence & fluency** | `Coherence = 1` if language model perplexity < threshold (e.g., 30) on GPT‑2; else `0`. | *Perplexity as fluency metric* (Jiang et al., 2019) – https://arxiv.org/abs/1904.10930 |
| 4 | **Coverage of key points** | `Coverage = (# of distinct key concepts in answer) / (# of key concepts in reference)` | *ROUGE‑L* for concept extraction (Lin, 2004) – https://aclanthology.org/W04-1013/ |
| 5 | **Overall score** | `Score = 0.4·Sim_sem + 0.3·Fact + 0.2·Coherence + 0.1·Coverage` | Weighted sum chosen to reflect importance of factuality and semantics; weights can be tuned. |

### Assumptions & Limitations
- **Embeddings**: Uses pre‑trained BERT‑large; assumes domain‑agnostic representation.  
- **Fact verification**: Requires a curated knowledge base; may miss emerging facts.  
- **Perplexity threshold**: GPT‑2 perplexity is language‑model dependent; threshold may need adjustment per dataset.  
- **Coverage**: Relies on accurate concept extraction; noisy extraction can inflate score.  
- **Weights**: Arbitrary; different tasks may need re‑weighting.

### Baseline
- **Random answer**: `Sim_sem ≈ 0.2`, `Fact = 0`, `Coherence = 0`, `Coverage ≈ 0.1` → `Score ≈ 0.12`.  
- **Human‑written answer**: `Sim_sem ≈ 0.85`, `Fact = 1`, `Coherence = 1`, `Coverage ≈ 0.9` → `Score ≈ 0.88`.

### Falsifiable Test
**Hypothesis**: The proposed metric correlates positively with human judgment of answer quality.  
**Test**:  
1. Collect 200 question–answer pairs.  
2. Have 10 annotators rate each answer on a 5‑point Likert scale for quality.  
3. Compute Pearson correlation between the metric `Score` and the mean human rating.  
**Success Criterion**: Correlation coefficient ≥ 0.6 (p < 0.01). If the correlation is below this threshold, the metric fails the test.  

This method is fully reproducible: all tools (BERT, FactCC, GPT‑2) are open‑source, and the scoring formula is explicit.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
