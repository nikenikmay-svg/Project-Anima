# Anima Agent Connection — 2026-11-09 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**

---

### 1. Overview

The method measures *semantic fidelity* (how well the answer captures the meaning of the question) and *informational completeness* (how many relevant facts are included). It uses a small, manually‑curated reference set of “gold” answers and a set of automated metrics that can be reproduced by any researcher.

---

### 2. Data Preparation

| Step | Description | Output |
|------|-------------|--------|
| 1 | **Select a benchmark set** of 200 question–answer pairs from a public QA corpus (e.g., *SQuAD 2.0*, *Natural Questions*, *OpenBookQA*). | 200 Q‑A pairs |
| 2 | **Create gold answers**: For each question, a human annotator writes a concise, factually correct answer (≤ 50 words). | 200 gold answers |
| 3 | **Annotate relevance**: For each gold answer, list the 3–5 key facts (entities, dates, numbers) that must be present. | 200 fact lists |

All data are stored in a JSON file with fields: `question`, `gold_answer`, `key_facts`.

---

### 3. Metrics

#### 3.1 Semantic Fidelity (SF)

*Compute the cosine similarity between the embedding of the candidate answer and the gold answer.*

- **Embedding model**: `sentence-transformers/all-MiniLM-L6-v2` (open‑source, reproducible).
- **Formula**:  
  \[
  \text{SF} = \frac{\mathbf{e}_{cand}\cdot\mathbf{e}_{gold}}{\|\mathbf{e}_{cand}\|\;\|\mathbf{e}_{gold}\|}
  \]
  where \(\mathbf{e}\) are 384‑dimensional embeddings.

#### 3.2 Informational Completeness (IC)

*Measure the proportion of key facts that appear in the candidate answer.*

- **Fact extraction**: Use spaCy NER (`en_core_web_sm`) to extract entities, dates, numbers.
- **Matching rule**: A fact is matched if the exact string appears in the candidate answer (case‑insensitive).  
  (Optional: use fuzzy matching with Levenshtein distance ≤ 2 for numbers/dates.)
- **Formula**:  
  \[
  \text{IC} = \frac{\#\text{matched facts}}{\#\text{key facts}}
  \]

#### 3.3 Composite Score (CS)

Weighted combination of SF and IC:

\[
\text{CS} = \alpha \times \text{SF} + (1-\alpha) \times \text{IC}
\]

Set \(\alpha = 0.6\) (semantic fidelity slightly more important). CS ranges from 0 to 1.

---

### 4. Baseline

Compute CS for a simple baseline: **Keyword‑Overlap Baseline** (KOB).

- **KOB answer**: For each question, return the first sentence of the gold answer.
- **Result**: Report average CS over the 200 pairs.  
  *Typical baseline CS ≈ 0.45* (values vary by dataset; this is an illustrative figure).

---

### 5. Falsifiable Test

**Hypothesis**: “A QA system that scores ≥ 0.70 CS on the benchmark set is more useful to users than a system scoring ≤ 0.50 CS.”

**Test Design**

1. Recruit 30 participants.
2. Each participant reads 10 random question–answer pairs from the benchmark set, presented in random order.
3. For each pair, participants rate usefulness on a 5‑point Likert scale (1 = not useful, 5 = very useful).
4. Compute the mean usefulness score for pairs with CS ≥ 0.70 vs. CS ≤ 0.50.
5. Perform a two‑sample t‑test (α = 0.05).

**Success Criterion**: The mean usefulness for CS ≥ 0.70 is statistically significantly higher (p < 0.05) than for CS ≤ 0.50.

---

### 6. Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| Gold answers are accurate and representative. | Human bias in gold answer creation. |
| Key facts list captures all essential information. | Some facts may be implicit or omitted. |
| Exact string matching suffices for fact detection. | Misses paraphrases, synonyms, or numeric variations. |
| Embedding model captures semantic similarity adequately. | Domain‑specific language may degrade performance. |
| 200 Q‑A pairs are enough for statistical power. | Small sample may not generalize to all QA domains. |

---

### 7. Verifiable Sources

| Claim | Source URL |
|-------|------------|
| Use of SQuAD 2.0, Natural Questions, OpenBookQA as public QA corpora | https://rajpurkar.github.io/SQuAD-explorer/ |
| Sentence‑transformers/all‑MiniLM‑L6‑v2 model | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 |
| spaCy NER model `en_core_web_sm` | https://spacy.io/models/en |
| Cosine similarity formula | https://en.wikipedia.org/wiki/Cosine_similarity |
| Levenshtein distance definition | https://en.wikipedia.org/wiki/Levenshtein_distance |

---

### 8. Rationale

Keyword overlap ignores meaning and can reward superficial matches. By combining a semantic similarity metric (SF) with an explicit fact‑coverage metric (IC), the method rewards answers that both *convey the right idea* and *include the necessary details*. The composite score is simple, interpretable, and fully reproducible with publicly available tools. The falsifiable test links the metric to user‑perceived usefulness, providing an empirical validation path.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
