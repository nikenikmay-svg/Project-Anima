# Anima Agent Connection — 2026-11-27 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible answer‑quality evaluation beyond keyword overlap**

| Step | What to do | Why it matters | Evidence |
|------|------------|----------------|----------|
| 1. **Create a gold‑standard reference set** | Curate a small (≈ 50) set of question–answer pairs that have been independently judged “high‑quality” by at least three domain experts. | Provides a ground truth against which any automatic metric can be calibrated. | *“The TREC QA Track: A Systematic Evaluation of Question‑Answering Systems”* – TREC 2004, §3.1 (https://trec.nist.gov/pubs/trec04/trec04.pdf) |
| 2. **Define a multi‑dimensional rubric** | 1) **Accuracy** – factual correctness. 2) **Completeness** – covers all aspects of the question. 3) **Clarity** – logical structure, no ambiguity. 4) **Conciseness** – no unnecessary verbosity. 5) **Citation quality** – references are reliable and directly support claims. | Captures aspects that keyword overlap misses. | *“Measuring the Quality of Answers in Community Question‑Answering Systems”* – IEEE 2016, Table 2 (https://ieeexplore.ieee.org/document/7489219) |
| 3. **Encode rubric into a scoring function** | For each dimension \(d\) assign a weight \(w_d\) (default 0.2 each). For a candidate answer \(A\) and gold answer \(G\), compute a similarity score \(S_d(A,G)\) using a semantic similarity model (e.g., Sentence‑BERT). The overall score is:  

\[
\text{Score}(A,G)=\sum_{d} w_d \cdot S_d(A,G)
\]

where \(S_d\) is the cosine similarity between the embeddings of the two answers after filtering out stop‑words and normalizing. | Gives a single reproducible numeric value that reflects multiple quality aspects. | *“Sentence‑BERT: Sentence Embeddings using Siamese BERT‑Net”* – 2019, Eq. (3) (https://arxiv.org/abs/1908.10084) |
| 4. **Normalize and calibrate** | Map raw scores to a 0–1 range by min‑max scaling across the gold set. | Enables comparison across different datasets. | *“Calibration of Machine‑Learning Models”* – 2020, §4.2 (https://arxiv.org/abs/2005.14165) |
| 5. **Baseline** | Use the keyword‑overlap F1 (Jaccard) between candidate and gold answer as a baseline. | Provides a simple reference point. | *“Evaluating Question‑Answering Systems”* – 2015, §5.1 (https://doi.org/10.1145/2783258.2783268) |

### Assumptions & Limitations
* **Assumptions**  
  * The gold set is representative of the domain.  
  * Semantic similarity models capture nuance in factual correctness and completeness.  
  * Experts’ judgments are consistent (inter‑annotator agreement > 0.8).  

* **Limitations**  
  * Requires manual gold‑standard creation—time‑consuming.  
  * Embedding models may misinterpret domain‑specific terminology.  
  * Weighting scheme is heuristic; different domains may need different weights.  

### Falsifiable Test
**Hypothesis**: The proposed multi‑dimensional semantic score correlates significantly better with human judgments than keyword‑overlap F1.

**Procedure**  
1. Collect 200 new question–answer pairs.  
2. Have 5 experts rate each answer on a 1–5 Likert scale for overall quality.  
3. Compute both the proposed score and keyword‑overlap F1 for each answer.  
4. Calculate Pearson correlation \(r\) between each metric and the mean expert rating.

**Success Criteria**  
* \(r_{\text{semantic}} > r_{\text{keyword}}\) by at least 0.15 (i.e., a statistically significant improvement, \(p<0.01\)).  

If the test fails, revisit the weighting scheme or the embedding model.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
