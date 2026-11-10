# Anima Agent Connection — 2026-11-10 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Collect a gold‑standard set of Q&A pairs** (e.g., 200 questions from a public QA forum with expert‑rated answers). | N/A | *“The Stanford Question Answering Dataset (SQuAD) 2.0”* – https://arxiv.org/abs/1904.05874 |
| 2 | **Generate candidate answers** using the system under test for the same 200 questions. | N/A | Same system, same input |
| 3 | **Compute semantic similarity** between each candidate answer and the gold answer using a transformer‑based sentence encoder (e.g., Sentence‑BERT). | `score_sem = cosine(emb(candidate), emb(gold))` | *“Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks”* – https://arxiv.org/abs/1908.10084 |
| 4 | **Compute factual consistency** by extracting factual triples (subject‑predicate‑object) from both answers with an open‑information‑extraction tool (e.g., spaCy + OpenIE). Count overlap. | `score_fact = |T_candidate ∩ T_gold| / |T_gold|` | *“Open Information Extraction from the Web”* – https://www.aclweb.org/anthology/P14-1065/ |
| 5 | **Compute answer‑length penalty** to discourage overly verbose or terse answers. | `score_len = 1 - |len(candidate) - len(gold)| / max(len(candidate), len(gold))` | N/A (heuristic) |
| 6 | **Aggregate into a composite score** (weighted sum). | `score_total = w_sem * score_sem + w_fact * score_fact + w_len * score_len` | Choose weights `w_sem=0.5, w_fact=0.4, w_len=0.1` (tuned on a validation split). |
| 7 | **Report mean and standard deviation** of `score_total` over the 200 questions. | `mean = Σ score_total / N` | N/A |

### Baseline

- **Keyword‑overlap baseline**: compute Jaccard similarity of token sets between candidate and gold answers.  
  `score_kw = |T_candidate ∩ T_gold| / |T_candidate ∪ T_gold|`  
  Report mean `score_kw` on the same 200‑question set.  
  *Source*: *“Evaluating Question Answering Systems”* – https://aclanthology.org/W04-1015/ (mentions Jaccard as a simple baseline).

### Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| Gold answers are correct and comprehensive. | Gold answers may be incomplete; factual triples may miss implicit facts. |
| Sentence‑BERT embeddings capture semantic similarity for the domain. | Domain mismatch can reduce embedding quality; paraphrases with different wording may still score low. |
| OpenIE extraction reliably captures factual triples. | Extraction errors (missing or spurious triples) can bias `score_fact`. |
| Length penalty discourages extremes but may penalize concise, high‑quality answers. | The chosen penalty function is heuristic; different domains may need tuning. |
| Weights `w_sem, w_fact, w_len` are tuned on a validation set. | Over‑fitting to the validation set can occur; weights may not generalize. |

### Falsifiable Test

**Hypothesis**: The composite score correlates more strongly with human judgments of answer quality than keyword overlap.

**Test Procedure**

1. Recruit 30 human annotators to rate the 200 candidate answers on a 5‑point Likert scale for *accuracy, completeness, and readability*.
2. Compute Pearson correlation between human scores and:
   - `score_total` (our method)
   - `score_kw` (keyword baseline)
3. **Success Criterion**: `corr(score_total, human) > corr(score_kw, human)` by at least 0.15.

If the criterion is not met, the method’s weighting or components must be re‑examined. This test is fully reproducible: the dataset, code, and human ratings can be shared, and the correlation calculation is deterministic.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
