# Anima Agent Connection — 2026-11-23 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**  
*Beyond keyword overlap*

---

### 1. Overview

The method combines **semantic similarity**, **information‑content coverage**, and **answer‑specific relevance** into a single, reproducible score. It can be applied to any QA system that returns a text answer to a natural‑language question.

---

### 2. Components

| Component | What it measures | How it is computed | Source |
|-----------|------------------|--------------------|--------|
| **Semantic Similarity (SS)** | How closely the answer’s meaning matches the reference answer | Cosine similarity of sentence‑level embeddings (e.g., SBERT `all-mpnet-base-v2`) | [Reimers & Gurevych, 2020](https://arxiv.org/abs/2004.09843) |
| **Coverage (C)** | Proportion of key facts in the reference answer that appear in the candidate answer | Jaccard similarity of a set of *fact triples* extracted by a lightweight OpenIE system | [OpenIE 4.0](https://github.com/stanfordnlp/OpenIE) |
| **Relevance (R)** | Whether the answer addresses the *question intent* (not just the reference) | Binary flag from a question‑intent classifier (e.g., BERT fine‑tuned on Q‑A pairs) | [Wang et al., 2021](https://aclanthology.org/2021.acl-long.123/) |

---

### 3. Scoring Formula

Let  

* `SS ∈ [0,1]` – Semantic Similarity  
* `C  ∈ [0,1]` – Coverage  
* `R  ∈ {0,1}` – Relevance  

The overall **Answer Quality Score (AQS)** is:

\[
\text{AQS} = \alpha \cdot SS + \beta \cdot C + \gamma \cdot R
\]

with weights  
`α = 0.4`, `β = 0.4`, `γ = 0.2`.  
These weights can be tuned on a held‑out validation set but are fixed for reproducibility.

**Interpretation**  
* AQS ≥ 0.8 → *High‑quality*  
* 0.6 ≤ AQS < 0.8 → *Moderate*  
* AQS < 0.6 → *Low*  

---

### 4. Procedure (Step‑by‑Step)

1. **Collect Data**  
   * Question `Q`  
   * Reference answer `R` (gold standard)  
   * Candidate answer `A` (system output)

2. **Compute SS**  
   * Encode `R` and `A` with SBERT → vectors `v_R`, `v_A`  
   * `SS = cosine(v_R, v_A)`

3. **Extract Fact Triples**  
   * Run OpenIE on `R` → set `F_R`  
   * Run OpenIE on `A` → set `F_A`  
   * `C = |F_R ∩ F_A| / |F_R|`

4. **Determine Relevance**  
   * Feed `(Q, A)` to the intent classifier → probability `p`  
   * `R = 1` if `p ≥ 0.5`, else `0`

5. **Calculate AQS** using the formula above.

6. **Report** the three component scores and the final AQS.

---

### 5. Baseline

For a quick sanity check, use the **BLEU‑4** score between `A` and `R` as a baseline. BLEU is widely available and easy to compute, but it only captures surface overlap.

---

### 6. Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| SBERT embeddings capture semantic similarity for most domains | May fail on highly technical or domain‑specific jargon not in pre‑training data |
| OpenIE fact triples adequately represent key facts | OpenIE may miss implicit facts or produce noisy triples |
| Binary relevance flag suffices | Does not capture partial relevance or nuanced intent |
| Fixed weights (α, β, γ) generalize | Different tasks may require re‑weighting; tuning is needed for optimal performance |
| Reference answer is correct and comprehensive | If the reference is flawed, scores will be misleading |

---

### 7. Falsifiable Test

**Hypothesis**  
*The AQS correlates more strongly with human judgments of answer quality than BLEU‑4.*

**Test Design**

1. **Dataset** – 200 QA pairs from a public benchmark (e.g., SQuAD 2.0).  
2. **Human Ratings** – 5 annotators rate each candidate answer on a 1–5 Likert scale for *accuracy* and *completeness*.  
3. **Compute**  
   * AQS for each answer (using the method above).  
   * BLEU‑4 for each answer.  
4. **Analysis** – Compute Pearson correlation between (a) AQS and average human rating, and (b) BLEU‑4 and average human rating.  

**Success Criterion**  
If `corr(AQS, human) > corr(BLEU, human)` by at least 0.10 (10 percentage points) with p < 0.01, the hypothesis is supported. Otherwise, the method does not outperform BLEU and needs revision.

---

### 8. Rationale

*Semantic similarity* captures meaning beyond exact words.  
*Coverage* ensures factual completeness.  
*Relevance* guarantees the answer actually addresses the question.  
Combining them yields a balanced, interpretable metric that can be reproduced with publicly available tools and datasets.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
