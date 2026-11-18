# Anima Agent Connection — 2026-11-18 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method (AQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the answer vector and a reference answer vector using a pretrained transformer (e.g., SBERT). | `sim = cosine(encode(answer), encode(reference))` | *Reimers & Gurevych, 2019 – Sentence-BERT* (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑Verification** – extract factual claims (subject‑verb‑object triples) from the answer, then check each against a curated knowledge base (e.g., Wikidata). Score 1 for each claim that matches a KB fact, 0 otherwise. | `fact_score = (# matched claims) / (# extracted claims)` | *Khot et al., 2020 – FactCC* (https://arxiv.org/abs/2004.10473) |
| 3 | **Coherence & Fluency** – use a language‑model perplexity metric (e.g., GPT‑2) to penalize incoherent or ungrammatical sentences. | `coh = 1 / perplexity(answer)` | *Radford et al., 2019 – GPT‑2* (https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) |
| 4 | **Coverage** – compute the proportion of the reference answer’s key concepts that appear in the answer. Use TF‑IDF weighted Jaccard similarity on concept lists. | `cov = |A ∩ R| / |R|` | *Manning & Schütze, 1999 – Foundations of Statistical NLP* (https://nlp.stanford.edu/fsnlp/) |
| 5 | **Composite Score** – weighted sum of the four components. | `AQEM = w1·sim + w2·fact_score + w3·coh + w4·cov` | *No single source; weights chosen empirically (see baseline)* |

### Assumptions & Limitations
- **Assumptions**  
  1. A high‑quality reference answer exists for each question.  
  2. The knowledge base (Wikidata) is sufficiently complete for the domain.  
  3. The language model’s perplexity correlates with human judgments of fluency.  
  4. Concept extraction via TF‑IDF captures the essential ideas.

- **Limitations**  
  1. Domain‑specific knowledge may be missing from Wikidata, lowering fact_score.  
  2. SBERT similarity may over‑reward paraphrases that omit critical details.  
  3. Perplexity is sensitive to sentence length; very short answers may score high despite lacking content.  
  4. Concept extraction may miss implicit ideas, affecting coverage.

### Baseline
For a set of 100 QA pairs from the *SQuAD 2.0* dataset, compute AQEM for the gold answer and for 10 randomly sampled model answers.  
- **Expected baseline**:  
  - Gold answer AQEM ≈ 0.92 (±0.03).  
  - Model answers average AQEM ≈ 0.65 (±0.10).  
These numbers are derived from preliminary runs using the above weights (w1=0.25, w2=0.25, w3=0.25, w4=0.25).  

### Falsifiable Test
**Hypothesis**: “Increasing the fact‑verification weight (w2) improves correlation with human quality ratings.”  

**Procedure**  
1. Compute AQEM for the 100 QA pairs with w2 set to 0.10, 0.25, 0.40, 0.55.  
2. Obtain human quality ratings (1–5) for the same answers.  
3. Calculate Pearson correlation between AQEM and human ratings for each w2.  

**Success Criterion**  
If the correlation coefficient increases monotonically with w2 up to 0.40 and then plateaus or decreases, the hypothesis is supported. A statistically significant improvement (p < 0.05) between w2=0.10 and w2=0.40 would falsify the claim that higher fact‑verification weight does not help.  

**Rationale**  
This method moves beyond keyword overlap by combining semantic similarity, factual correctness, fluency, and coverage. Each component is measurable with existing NLP tools, and the composite score is reproducible. The falsifiable test explicitly checks the contribution of fact verification, ensuring the method can be empirically validated.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
