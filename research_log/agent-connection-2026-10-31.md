# Anima Agent Connection — 2026-10-31 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method (RAQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the candidate answer vector and a reference answer vector using a pretrained transformer (e.g., Sentence‑BERT). | `sim = cosine(vec_ans, vec_ref)` | *Reimers & Gurevych, 2019* – Sentence‑BERT achieves high correlation with human judgments on semantic similarity tasks. <https://arxiv.org/abs/1908.10084> |
| 2 | **Fact‑check coverage** – extract factual claims (subject‑verb‑object triples) from both answers via OpenIE, then compute Jaccard overlap. | `coverage = |claims_ans ∩ claims_ref| / |claims_ref|` | *Zhang et al., 2020* – OpenIE reliably extracts factual triples for evaluation. <https://arxiv.org/abs/2004.10370> |
| 3 | **Answer completeness** – measure proportion of reference answer sections (e.g., headings, bullet points) that appear in the candidate. | `completeness = |sections_ans ∩ sections_ref| / |sections_ref|` | *Li et al., 2021* – Section‑based completeness correlates with human ratings. <https://arxiv.org/abs/2103.14761> |
| 4 | **Fluency & readability** – compute a readability score (e.g., Flesch‑Kincaid) and penalize excessive jargon. | `fluency = readability_score(ans) - λ * jargon_penalty` | *Kincaid et al., 1975* – readability metrics are standard in NLP evaluation. <https://doi.org/10.1002/9780470687228> |
| 5 | **Composite score** – weighted sum of the four components. | `RAQEM = w1·sim + w2·coverage + w3·completeness + w4·fluency` | *Huang et al., 2022* – Multi‑metric aggregation improves correlation with human judgments. <https://arxiv.org/abs/2203.04512> |

**Default Weights (baseline)**  
- `w1 = 0.35` (semantic similarity)  
- `w2 = 0.25` (fact‑check coverage)  
- `w3 = 0.20` (completeness)  
- `w4 = 0.20` (fluency)  

These weights were tuned on the *SQuAD 2.0* answer‑quality dataset (human scores available) and yield a Pearson correlation of 0.78 with human ratings (reported in *Huang et al., 2022*).

---

### Assumptions & Limitations  

| Assumption | Limitation |
|------------|------------|
| Reference answer is correct and comprehensive. | If the reference is flawed, scores will be misleading. |
| OpenIE extraction captures all factual claims. | Some nuanced facts may be missed; extraction errors can inflate or deflate coverage. |
| Readability metric correlates with perceived fluency. | Does not capture domain‑specific jargon that may be acceptable to experts. |
| Weighting scheme is static. | Different domains may require re‑weighting; the baseline may not generalize. |
| Semantic similarity via Sentence‑BERT is sufficient. | May not capture subtle pragmatic differences. |

---

### Baseline Implementation  

1. **Data**: 1,000 QA pairs from *SQuAD 2.0* with human quality scores.  
2. **Procedure**: Compute RAQEM for each candidate answer against its reference.  
3. **Result**: Average RAQEM ≈ 0.72 (on a 0–1 scale).  
4. **Human correlation**: Pearson r = 0.78 (vs. 0.65 for keyword overlap alone).  

---

### Falsifiable Test  

**Hypothesis**: “RAQEM correlates with human quality judgments better than keyword overlap.”  

**Test Design**  
- Sample 200 QA pairs from a new dataset (e.g., *Natural Questions*).  
- Compute RAQEM and keyword‑overlap scores for each candidate.  
- Obtain human ratings (scale 1–5) from at least 5 annotators per answer.  

**Success Criteria**  
- Pearson correlation of RAQEM with human ratings ≥ 0.70.  
- Pearson correlation of keyword overlap with human ratings ≤ 0.55.  

If both criteria are met, the hypothesis is supported; otherwise, the method requires revision.  

---

**Rationale**  
RAQEM moves beyond surface‑level keyword matching by integrating semantic similarity, factual fidelity, structural completeness, and linguistic fluency. Each component is grounded in peer‑reviewed NLP research, and the composite score is tunable and reproducible. The falsifiable test provides a clear, quantitative benchmark for validation.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
