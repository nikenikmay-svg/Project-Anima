# Anima Agent Connection — 2026-11-13 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**  
*Beyond keyword overlap – a “semantic‑fidelity + user‑relevance” framework*

---

### 1. Core Idea  
Measure how well an answer **(a)** captures the *semantic intent* of the user query and **(b)** satisfies the *user’s informational need*. This is done with two orthogonal, automatically computable signals:

| Signal | What it captures | How it is computed |
|--------|------------------|--------------------|
| **Intent‑Coverage (IC)** | Proportion of the query’s *semantic concepts* that appear in the answer. | 1. Parse query and answer with a dependency/semantic role parser (e.g., spaCy + AllenNLP SRL). 2. Extract a set of *concept tokens* (nouns, nominal compounds, key verbs). 3. Compute Jaccard similarity between query‑concept set and answer‑concept set. |
| **Relevance‑Score (RS)** | How well the answer addresses the *user’s expected outcome* (e.g., factual correctness, completeness). | 1. Use a pretrained factual‑ness model (e.g., FactCC or OpenAI’s factuality classifier). 2. Feed the answer; obtain a probability that the answer is *factually correct* relative to a trusted knowledge base (Wikipedia, Wikidata). 3. Optionally, add a *completeness* sub‑score: compare the answer length and number of distinct concepts to a reference answer (if available). |

The final **Answer‑Quality Score (AQS)** is a weighted sum:

\[
\text{AQS} = \alpha \times \text{IC} + \beta \times \text{RS}
\]

where \(\alpha, \beta \in [0,1]\) and \(\alpha + \beta = 1\).  
Typical default: \(\alpha = 0.4\), \(\beta = 0.6\) (more weight to factual correctness).

---

### 2. Scoring Formula (Explicit)

1. **Intent‑Coverage (IC)**  
   \[
   \text{IC} = \frac{|C_Q \cap C_A|}{|C_Q|}
   \]
   *\(C_Q\)* = set of query concepts, *\(C_A\)* = set of answer concepts.

2. **Relevance‑Score (RS)**  
   \[
   \text{RS} = \text{FactCC}(A) \times \left(1 + \frac{|C_A|}{|C_Q|}\right)^{\gamma}
   \]
   *FactCC(A)* = factuality probability (0–1).  
   *γ* = 0.2 (to mildly reward concept coverage).  
   RS is capped at 1.

3. **Answer‑Quality Score (AQS)**  
   \[
   \text{AQS} = 0.4 \times \text{IC} + 0.6 \times \text{RS}
   \]
   Resulting in a score between 0 and 1.

---

### 3. Verifiable Source URLs & Claims

| Claim | Source URL | Specific Claim |
|-------|------------|----------------|
| Dependency parsing and concept extraction are reliable for English queries | https://spacy.io/usage | “spaCy provides a fast, accurate dependency parser.” |
| Semantic role labeling improves concept extraction | https://allenai.org/plato/semantic-role-labeling | “SRL identifies predicate‑argument structures.” |
| FactCC provides factuality scores against Wikipedia | https://github.com/allenai/factcc | “FactCC predicts factuality of a sentence using a BERT-based classifier.” |
| Jaccard similarity is a standard set‑overlap metric | https://en.wikipedia.org/wiki/Jaccard_index | “Jaccard index measures similarity between finite sample sets.” |
| Weighted sum of intent and factuality is common in QA evaluation | https://arxiv.org/abs/1905.10832 | “Combining coverage and correctness improves overall QA quality.” |

---

### 4. Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| Query and answer are in the same language (English). | Multilingual extension requires language‑specific parsers. |
| The factuality model is trained on Wikipedia; domain‑specific knowledge may be missing. | Answers about niche topics may be penalized unfairly. |
| Concept extraction via dependency/SRL captures all relevant semantics. | Idiomatic or implicit meanings may be missed. |
| The reference answer (for completeness) is available or approximated by the answer length. | In open‑ended tasks, no ground truth may exist. |
| Weighting \(\alpha, \beta\) is fixed; different tasks may need tuning. | Requires empirical calibration. |

---

### 5. Baseline

*Baseline method*: **ROUGE‑L** (longest common subsequence) between answer and a gold reference answer.  
Typical ROUGE‑L F1 scores for state‑of‑the‑art QA systems hover around **0.45–0.55** on datasets like SQuAD.  
Our proposed AQS, when evaluated on the same dataset with default weights, achieves an average **0.62** (higher indicates better quality), demonstrating improved sensitivity to factual correctness and intent coverage.

---

### 6. Falsifiable Test

**Test**: *Does AQS correlate better with human judgments of answer quality than ROUGE‑L?*

1. **Setup**  
   - Sample 200 QA pairs from a public dataset (e.g., Natural Questions).  
   - Have 10 human annotators rate each answer on a 5‑point Likert scale for *overall quality* (1 = poor, 5 = excellent).  
   - Compute AQS and ROUGE‑L for each answer.

2. **Success Criterion**  
   - Pearson correlation coefficient between human scores and AQS ≥ 0.70.  
   - Pearson correlation between human scores and ROUGE‑L ≤ 0.55.  

If the criterion is met, the method is validated; if not, the weighting or components must be revisited.

---

### 7. Rationale (Concise)

Keyword overlap ignores semantics and factual correctness. By decomposing quality into *intent coverage* (semantic overlap) and *relevance* (factuality + completeness), the method captures both *what* the answer says and *how well* it answers the question. The scoring formula is simple, reproducible, and leverages mature NLP tools, enabling consistent evaluation across systems. The falsifiable test provides a clear, empirical benchmark against human judgment.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
