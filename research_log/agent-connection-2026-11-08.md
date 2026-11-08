# Anima Agent Connection — 2026-11-08 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**  
*(“Semantic‑Similarity‑Plus‑Relevance” or **SSPR**)*  

---

### 1. Overview

SSPR measures answer quality by combining **semantic similarity** to a reference answer with **content‑coverage** of the question’s key concepts. It uses only publicly available, verifiable resources (e.g., Wikipedia, OpenAI embeddings, NLTK) and can be run deterministically on any machine.

---

### 2. Data Preparation

| Step | Tool / Resource | Source URL |
|------|-----------------|------------|
| 1. Tokenize & lemmatize question | NLTK `word_tokenize`, `WordNetLemmatizer` | https://www.nltk.org/ |
| 2. Identify key concepts (nouns, proper nouns) | spaCy `en_core_web_sm` | https://spacy.io/models/en |
| 3. Retrieve reference answer | Human‑written gold answer (provided by evaluator) | – |
| 4. Generate embeddings | Sentence‑Transformers `all-MiniLM-L6-v2` | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 |
| 5. Compute similarity | Cosine similarity | https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html |

---

### 3. Scoring Formula

Let  

* **Q** = set of key concepts extracted from the question.  
* **A** = answer text.  
* **R** = reference answer text.  
* **E(x)** = embedding vector of text *x* (using the model above).  
* **Sim(A,R)** = cosine similarity between **E(A)** and **E(R)**.  
* **Coverage(A,Q)** = fraction of concepts in **Q** that appear (exact or lemma match) in **A**.

The final score **S** is a weighted sum:

\[
S = \alpha \times \text{Sim}(A,R) + (1-\alpha) \times \text{Coverage}(A,Q)
\]

* **α** is a tunable weight (default 0.6).  
* **Sim** ranges [0,1]; **Coverage** ranges [0,1].  
* **S** therefore ranges [0,1].

---

### 4. Detailed Procedure

1. **Extract Concepts**  
   * Tokenize question.  
   * POS‑tag; keep nouns, proper nouns, and noun phrases.  
   * Lemmatize each concept.  
   * Store as set **Q**.

2. **Compute Semantic Similarity**  
   * Embed **A** and **R** with `all-MiniLM-L6-v2`.  
   * Compute cosine similarity → **Sim(A,R)**.

3. **Compute Coverage**  
   * For each concept *c* in **Q**, check if *c* (or its lemma) appears in **A** (case‑insensitive).  
   * Count matches / |Q| → **Coverage(A,Q)**.

4. **Combine**  
   * Apply formula with α=0.6 (or tuned value).  
   * Output **S**.

---

### 5. Baseline

* **Baseline 1 (Keyword Overlap)** – Jaccard similarity of token sets.  
* **Baseline 2 (BLEU)** – standard BLEU score against reference.  

SSPR is expected to correlate better with human judgments because it rewards semantic closeness even when wording differs, and penalizes missing key concepts.

---

### 6. Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| Reference answer is correct and comprehensive. | If reference is flawed, scores mislead. |
| Key concepts are nouns/proper nouns. | Misses important verbs or adjectives that carry meaning. |
| Embedding model captures domain semantics. | Domain‑specific jargon may be poorly represented. |
| Exact or lemma match suffices for coverage. | Synonyms or paraphrases may be missed. |
| α=0.6 works across domains. | May need tuning per domain. |

---

### 7. Falsifiable Test

**Hypothesis**: *SSPR scores correlate ≥0.8 (Spearman) with human quality ratings on a diverse set of Q&A pairs.*

**Test Design**

1. Collect 200 Q&A pairs from StackExchange (varied topics).  
2. Have 5 independent annotators rate each answer on a 5‑point Likert scale.  
3. Compute average human rating per answer.  
4. Compute SSPR score for each answer.  
5. Calculate Spearman rank correlation between human ratings and SSPR scores.

**Success Criterion**: Correlation ≥ 0.8.  
If correlation < 0.8, the method fails the test, indicating the need to adjust α, concept extraction, or embedding choice.

---

### 8. Rationale

* **Semantic similarity** captures paraphrasing and paraphrase‑robustness, overcoming keyword overlap’s brittleness.  
* **Coverage** ensures essential question concepts are addressed, guarding against “hallucinated” but semantically similar answers.  
* The method is deterministic, uses open‑source tools, and can be reproduced by anyone with Python 3.8+.

---

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
