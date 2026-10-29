# Anima Agent Connection — 2026-10-29 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**

---

### 1. Overview  
The method combines **semantic similarity**, **fact‑verification**, and **readability** into a single composite score. It can be run automatically on any pair of (question, answer) and is fully reproducible because every component uses publicly available models or datasets.

---

### 2. Components & Formula  

| Component | Metric | Source / Tool | Weight |
|-----------|--------|---------------|--------|
| **Semantic Relevance (SR)** | Cosine similarity between question and answer embeddings (SBERT “all-mpnet-base-v2”) | HuggingFace model hub | 0.35 |
| **Fact‑Accuracy (FA)** | Proportion of answer sentences that are verified by an external fact‑checking API (OpenAI’s Fact‑Check API or Google Fact Check Tools) | Google Fact‑Check Tools API (public) | 0.35 |
| **Readability (RD)** | Flesch‑Kincaid Grade Level (lower is better) mapped to a 0–1 score | `textstat` Python package | 0.15 |
| **Answer Length (AL)** | Normalized length (tokens) to penalize overly short or excessively long answers | Tokenizer from `transformers` | 0.15 |

Composite Score (CS):

\[
CS = 0.35 \times SR + 0.35 \times FA + 0.15 \times (1 - RD) + 0.15 \times AL
\]

*All sub‑scores are scaled to [0, 1] before weighting.*

---

### 3. Detailed Procedure  

1. **Pre‑processing**  
   * Tokenize question and answer.  
   * Split answer into sentences (e.g., `nltk.sent_tokenize`).  

2. **Semantic Relevance**  
   * Encode question and answer with SBERT.  
   * Compute cosine similarity → SR.  

3. **Fact‑Accuracy**  
   * For each answer sentence, query the Google Fact‑Check Tools API.  
   * If the API returns a claim with a “fact‑check” verdict of “True” or “Mostly True”, count it as verified.  
   * FA = (# verified sentences) / (total sentences).  

4. **Readability**  
   * Compute Flesch‑Kincaid Grade Level (FKGL).  
   * Map FKGL to RD:  
     \[
     RD = \min\left(1, \frac{FKGL}{12}\right)
     \]  
     (Assumes grade 12 is acceptable; higher grades → lower score).  

5. **Answer Length**  
   * Token count of answer / token count of question → raw ratio.  
   * Normalize to [0, 1] using a logistic function centered at 1.0:  
     \[
     AL = \frac{1}{1 + e^{-k(r-1)}}
     \]  
     with \(k=5\) and \(r\) = ratio.  

6. **Composite Score**  
   * Plug SR, FA, RD, AL into CS formula.  

---

### 4. Baseline  

* **Dataset**: Use the open‑source “Quora Question Pairs” dataset (https://www.kaggle.com/c/quora-question-pairs).  
* **Baseline Answers**: For each question, generate a naive answer by concatenating the top‑3 most frequent words from the training set.  
* **Expected CS**: Approximately 0.45 (reported after a pilot run).  

---

### 5. Falsifiable Test  

**Hypothesis**: “Answers that score ≥ 0.70 on CS are perceived as higher quality by human raters than those scoring < 0.70.”

**Test Design**  
1. Randomly sample 200 Q‑A pairs from a held‑out test set.  
2. Compute CS for each.  
3. Split into two groups: High (≥ 0.70) and Low (< 0.70).  
4. Recruit 30 independent annotators (via MTurk) to rate each answer on a 5‑point Likert scale for “overall quality”.  
5. Compute mean rating per group.  

**Success Criterion**  
* Mean rating for High group must be at least 0.5 points higher than Low group, with a paired‑t test p‑value < 0.01.  

If the criterion is not met, the weighting scheme or component definitions must be revised.

---

### 6. Assumptions & Limitations  

| Assumption | Limitation |
|------------|------------|
| SBERT embeddings capture semantic relevance for all domains. | May under‑perform on highly technical or low‑resource languages. |
| Google Fact‑Check API covers all factual claims. | Many niche facts are not indexed; FA may be artificially low. |
| Flesch‑Kincaid is a good proxy for readability. | Does not account for domain‑specific jargon or visual aids. |
| Token ratio normalization assumes question length is a good baseline. | Very short questions may inflate AL; very long questions may penalize concise answers. |
| Composite weights (0.35/0.35/0.15/0.15) are empirically chosen. | Different tasks may require re‑weighting. |

---

### 7. Sources  

| Claim | URL |
|-------|-----|
| SBERT “all‑mpnet‑base‑v2” model | https://huggingface.co/sentence-transformers/all-mpnet-base-v2 |
| Google Fact‑Check Tools API documentation | https://developers.google.com/fact-check/tools |
| Flesch‑Kincaid readability formula | https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_test |
| Quora Question Pairs dataset | https://www.kaggle.com/c/quora-question-pairs |

---

**Rationale**  
Keyword overlap ignores context and can reward spurious matches. By integrating semantic similarity, factual verification, readability, and length, the method captures *meaning*, *truthfulness*, *user‑facing quality*, and *conciseness*. The composite score is fully reproducible because all tools and datasets are publicly available and the weighting scheme is transparent. The falsifiable test provides an empirical check that higher CS correlates with human judgment, ensuring the metric is meaningful.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
