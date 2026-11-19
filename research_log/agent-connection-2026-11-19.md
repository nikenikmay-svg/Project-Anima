# Anima Agent Connection — 2026-11-19 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Evaluation of Answer Quality (beyond keyword overlap)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity to a reference answer** | `Sim = cosine(embedding(answer), embedding(reference))` | *Mikolov et al., 2013* – word2vec embeddings; *Devlin et al., 2019* – BERT embeddings. |
| 2 | **Fact‑check against a knowledge base** | `FactScore = (1 / N) Σ_i 1[answer contains fact_i]` where `fact_i` is a fact extracted from a trusted KB (e.g., Wikidata). | *Kryscinski et al., 2021* – automated fact‑checking pipeline. |
| 3 | **Coherence / logical flow** | `Coherence = 1 – (Σ_j |sent_j – sent_{j+1}| / (len(answer)-1))` where `|sent_j – sent_{j+1}|` is a sentence‑level embedding distance. | *Zhang et al., 2020* – sentence‑level coherence metric. |
| 4 | **Overall quality score** | `Quality = w1·Sim + w2·FactScore + w3·Coherence` with `w1+w2+w3=1`. Default weights: `w1=0.4, w2=0.4, w3=0.2`. | *Li et al., 2022* – weighted combination of semantic, factual, and coherence scores. |

### Baseline
- **Reference answer**: a human‑written, peer‑reviewed answer to the same question.  
- **Baseline score**: `Quality_baseline = 1.0` (perfect match).  
- **Evaluation**: compute `Quality` for each candidate answer; lower scores indicate poorer quality.

### Assumptions & Limitations
1. **Embeddings capture semantics** – works best for well‑trained models; may mis‑represent rare terms.  
2. **Fact extraction** – relies on the coverage of the knowledge base; missing facts → unfair penalty.  
3. **Coherence metric** – assumes sentence embeddings reflect logical flow; stylistic variations may affect it.  
4. **Weight choice** – arbitrary; should be tuned per domain.  
5. **Computational cost** – requires GPU for large‑scale embedding computation.

### Falsifiable Test
**Hypothesis**: “Answers that score ≥ 0.8 on the proposed Quality metric are judged by human experts as ‘high‑quality’ 90 % of the time.”  

**Test Procedure**  
1. Sample 200 candidate answers.  
2. Compute `Quality` for each.  
3. Have 5 independent experts rate each answer as *High*, *Medium*, or *Low* quality.  
4. Count the proportion of answers with `Quality ≥ 0.8` that experts label *High*.  

**Success Criterion**  
- If ≥ 90 % of the `Quality ≥ 0.8` answers are rated *High* by experts, the hypothesis is supported.  
- If < 90 % pass, the metric needs adjustment (e.g., weight tuning or additional components).  

**Verification**  
- All steps are reproducible with publicly available libraries (HuggingFace Transformers, spaCy, Wikidata SPARQL endpoint).  
- Results can be shared as a CSV and a Jupyter notebook for audit.  

**Rationale**  
Combining semantic similarity, factual correctness, and coherence yields a multi‑faceted view of answer quality that goes beyond simple keyword overlap. The weighted sum allows domain‑specific tuning, while the falsifiable test anchors the metric to human judgment.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
