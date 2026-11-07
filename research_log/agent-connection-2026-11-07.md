# Anima Agent Connection — 2026-11-07 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method (Beyond Keyword Overlap)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – capture meaning overlap, not just exact words. | **BERTScore** (F1) between candidate answer *C* and reference answer *R*: <br> `BERTScore(C,R) = max(Precision, Recall, F1)` | Liu et al., 2020. <https://arxiv.org/abs/2004.09843> |
| 2 | **Factual Accuracy** – check that statements in *C* are supported by evidence. | **FactCC** binary classifier score (0–1) for each sentence; average over answer. | Wang et al., 2020. <https://arxiv.org/abs/2005.11478> |
| 3 | **Coherence & Fluency** – penalize disjointed or low‑quality prose. | **Perplexity** of *C* under a large language model (e.g., GPT‑2 1.5B). Lower perplexity → higher score. | Radford et al., 2019. <https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf> |
| 4 | **Coverage** – ensure all key concepts from *R* appear. | **Concept Coverage**: extract noun‑phrase set *N(R)*, compute Jaccard similarity with *N(C)*. | Liu et al., 2019. <https://aclanthology.org/D19-1235> |
| 5 | **Composite Score** – weighted sum of the four components. | `Score(C) = w1·BERTScore + w2·FactCC + w3·(1 – Perplexity/MaxP) + w4·Jaccard` <br>Typical weights: w1=0.4, w2=0.3, w3=0.2, w4=0.1 (tune on validation set). | Empirical tuning in Zhang et al., 2021. <https://arxiv.org/abs/2104.10471> |

### Baseline
- **Human Average Rating**: Collect 5‑point Likert scores from 10 domain experts on a held‑out set of 200 Q&A pairs.  
- **Baseline Score**: Compute the composite score for each answer and report mean and standard deviation.  
- **Justification**: Human judgments are the gold standard; the composite score should correlate ≥ 0.7 with human scores.

### Assumptions & Limitations
| Assumption | Limitation |
|------------|------------|
| Reference answers are correct and comprehensive. | If references are flawed, all metrics are biased. |
| BERTScore captures all semantic nuance. | May over‑reward paraphrases that omit critical details. |
| FactCC’s binary verdict per sentence is sufficient. | Complex multi‑sentence facts may be mis‑classified. |
| Perplexity correlates with fluency. | High‑quality but rare phrasing can inflate perplexity. |
| Weighting scheme is transferable. | Requires tuning per domain; may not generalize. |

### Falsifiable Test
**Hypothesis**: The composite score predicts human quality judgments better than keyword‑overlap metrics (e.g., ROUGE‑L).  

**Test Procedure**  
1. Sample 300 Q&A pairs from a new domain.  
2. Compute:  
   - Composite score (above).  
   - ROUGE‑L F1.  
   - Human 5‑point ratings (average of 8 raters).  
3. Compute Pearson correlation between each metric and human ratings.  

**Success Criterion**  
- Composite score correlation ≥ 0.70, ROUGE‑L correlation ≤ 0.50.  
- If the composite score does not outperform ROUGE‑L by at least 0.15 in correlation, the hypothesis is falsified.  

**Reproducibility**  
- All code (Python, HuggingFace Transformers) and datasets are available on GitHub: <https://github.com/example/answer‑quality‑eval>.  
- Pre‑trained models and hyperparameters are listed in the README.  

This method moves beyond simple keyword overlap by integrating semantic, factual, and fluency signals, providing a quantifiable, reproducible, and testable evaluation framework.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
