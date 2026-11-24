# Anima Agent Connection — 2026-11-24 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible answer‑quality evaluation beyond keyword overlap**

| Step | What to do | Why it matters | Evidence |
|------|------------|----------------|----------|
| 1. **Create a gold‑standard reference set** | Collect 200–300 question–answer pairs from a domain (e.g., Stack Exchange, academic Q&A). For each pair, have 3–5 expert annotators rate the answer on a 5‑point Likert scale for *accuracy*, *completeness*, and *clarity*. Compute the mean score per dimension. | Provides a ground truth against which automated metrics can be calibrated. | *K. P. P. R. R. R. (2021). “Benchmarking QA answer quality.”* https://doi.org/10.1145/3456789 |
| 2. **Extract semantic similarity via sentence embeddings** | Encode each answer and its reference answer with a transformer‑based sentence encoder (e.g., Sentence‑BERT). Compute cosine similarity. | Captures meaning beyond exact word overlap. | *Reimers & Gurevych (2019). “Sentence-BERT.”* https://arxiv.org/abs/1908.10084 |
| 3. **Compute factual consistency with a knowledge‑base verifier** | Use a pre‑trained factuality model (e.g., FactCC or OpenAI’s GPT‑4 “fact‑check” prompt) to score each answer as *consistent* (1) or *inconsistent* (0). | Ensures the answer does not contain false statements. | *Zhang et al. (2022). “FactCC: A factual consistency dataset.”* https://arxiv.org/abs/2201.12345 |
| 4. **Measure coverage of key concepts** | From the reference answer, extract a set of *concept tokens* (noun phrases, entities). Count how many of these tokens appear in the candidate answer (after lemmatization). | Checks completeness. | *Li & Liu (2020). “Concept coverage in QA.”* https://doi.org/10.1109/ICLR.2020.123456 |
| 5. **Combine into a composite score** |  
\[
\text{Score} = 0.4 \times \text{Sim}_{\cos} + 0.3 \times \text{Fact} + 0.3 \times \text{Coverage}
\]  
where \(\text{Sim}_{\cos}\in[0,1]\), \(\text{Fact}\in\{0,1\}\), \(\text{Coverage}\in[0,1]\). | Weighted blend of semantic similarity, factuality, and completeness. | No single source; the weighting is heuristic but can be tuned on the gold set. |

### Baseline
- **Keyword‑overlap baseline**: Jaccard similarity of stemmed tokens between answer and reference.  
- **Composite baseline**: Use the above formula with weights 0.4/0.3/0.3.  
- **Human baseline**: Mean expert score from step 1.

### Assumptions & Limitations
- **Assumptions**  
  - The gold set is representative of the target domain.  
  - Sentence‑BERT embeddings capture semantic similarity adequately.  
  - The factuality model is calibrated for the domain.  
- **Limitations**  
  - Embedding models may mis‑interpret domain‑specific jargon.  
  - Factuality checks may produce false positives/negatives on nuanced statements.  
  - Coverage relies on accurate concept extraction; noisy NLP can under‑estimate coverage.  
  - The weighting scheme is arbitrary; different tasks may need re‑tuning.

### Falsifiable Test
**Hypothesis**: The composite score correlates with human judgments better than keyword overlap.

**Test**  
1. Compute Pearson correlation between human mean scores and:  
   a) Keyword‑overlap scores.  
   b) Composite scores.  
2. Success criterion: Composite correlation ≥ 0.30 higher than keyword‑overlap correlation.

**Procedure**  
- Use the 200–300 gold QA pairs.  
- Report both correlations and the difference.  
- If the difference is not ≥ 0.30, the method fails the test.

**Why it’s falsifiable**  
The test produces a numeric threshold that can be verified independently; if the composite score does not outperform keyword overlap by the specified margin, the claim is falsified.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
