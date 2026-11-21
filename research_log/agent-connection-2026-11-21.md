# Anima Agent Connection — 2026-11-21 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method (RAQ‑Eval)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the answer vector and a reference answer vector using a pre‑trained transformer (e.g., Sentence‑BERT). | `sim = cos(emb_answer, emb_reference)` | *Reimers & Gurevych, 2019* – Sentence‑BERT achieves high correlation with human judgments on semantic similarity tasks. <https://arxiv.org/abs/1908.10084> |
| 2 | **Fact‑Check Accuracy** – extract factual claims (subject‑verb‑object triples) from the answer, compare each to a knowledge base (e.g., Wikidata). Count correct claims. | `accuracy = (# correct claims) / (# extracted claims)` | *Baldwin et al., 2021* – Wikidata fact‑checking pipeline shows >90 % precision for simple triples. <https://arxiv.org/abs/2104.10771> |
| 3 | **Coherence Score** – evaluate discourse coherence using a language‑model perplexity metric on the answer text. Lower perplexity → higher coherence. | `coherence = 1 / perplexity(answer)` | *Wang et al., 2020* – Perplexity correlates with human coherence ratings. <https://arxiv.org/abs/2005.14165> |
| 4 | **Coverage** – measure how many distinct key concepts from the question appear in the answer. Use TF‑IDF weighted concept extraction. | `coverage = (# matched concepts) / (# question concepts)` | *Lin & Hovy, 2009* – Concept matching improves coverage metrics. <https://aclanthology.org/W09-3301> |
| 5 | **Composite Score** – weighted sum of the four sub‑scores. | `RAQ = w1·sim + w2·accuracy + w3·coherence + w4·coverage` | *Huang et al., 2022* – Weighted combination of semantic, factual, and coherence metrics outperforms single‑metric baselines. <https://arxiv.org/abs/2203.04512> |

**Default Weights (baseline)**  
`w1 = 0.35, w2 = 0.30, w3 = 0.20, w4 = 0.15`  
These weights were tuned on the *SQuAD 2.0* evaluation set to maximize Pearson correlation with human judgments (r = 0.78).

---

### Assumptions & Limitations  

1. **Reference Answers** – Requires a high‑quality reference answer for each question. If none exists, the method defaults to a *human‑annotated* gold standard.  
2. **Knowledge Base Coverage** – Fact‑check accuracy depends on the KB’s completeness; rare or domain‑specific facts may be missed, inflating error rates.  
3. **Language Model Bias** – Perplexity is language‑model dependent; different models yield different coherence scores.  
4. **Concept Extraction** – TF‑IDF may miss synonyms; manual curation improves coverage but reduces reproducibility.  
5. **Weight Sensitivity** – The chosen weights are dataset‑specific; cross‑domain transfer may require re‑tuning.

---

### Falsifiable Test  

**Hypothesis**: *RAQ‑Eval correlates with human quality ratings better than keyword‑overlap (BLEU) alone.*

**Test Design**  
1. Collect 200 QA pairs from a public benchmark (e.g., *Natural Questions*).  
2. Obtain human quality ratings (1–5) from 5 annotators per answer.  
3. Compute RAQ scores and BLEU scores for each answer.  
4. Calculate Pearson correlation coefficients: `r_RAQ` vs. human ratings, `r_BLEU` vs. human ratings.

**Success Criterion**  
`r_RAQ - r_BLEU ≥ 0.10` (i.e., RAQ‑Eval improves correlation by at least 0.10).  

If the criterion is not met, the method’s weighting or components must be re‑examined.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
