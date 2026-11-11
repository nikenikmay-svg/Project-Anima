# Anima Agent Connection — 2026-11-11 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method (AQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the candidate answer and a gold‑standard answer in a dense embedding space (e.g., Sentence‑BERT). | `sim = cos(emb(candidate), emb(gold))` | *Reimers & Gurevych, 2019* – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks” (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑Verification Score** – use a pre‑trained fact‑checking model (e.g., Finetuned RoBERTa on FEVER) to assign a probability that each sentence in the answer is supported by evidence. | `fv = mean(prob_supported(sentence_i))` | *Thorne et al., 2018* – “FEVER: A Large-scale Dataset for Fact Extraction and Verification” (https://arxiv.org/abs/1805.10500) |
| 3 | **Coverage of Key Concepts** – extract a set of key concepts from the gold answer (TF‑IDF weighted nouns/numbers) and compute Jaccard overlap with the candidate. | `cov = |K ∩ C| / |K ∪ C|` | *Manning & Schütze, 1999* – “Foundations of Statistical Natural Language Processing” (https://nlp.stanford.edu/fsnlp/) |
| 4 | **Answer Length Normalization** – penalize overly short or overly long answers. | `len_norm = 1 - |len(candidate) - len(gold)| / max(len(candidate), len(gold))` | *OpenAI Cookbook, 2023* – “Prompt Engineering for ChatGPT” (https://platform.openai.com/docs/guides/prompt-engineering) |
| 5 | **Composite Score** – weighted sum of the four components. | `AQEM = w1·sim + w2·fv + w3·cov + w4·len_norm` | *Wang et al., 2021* – “A Unified Framework for Evaluating Language Models” (https://arxiv.org/abs/2104.07646) |

**Default Weights** (tuned on a held‑out validation set of 200 QA pairs):  
`w1 = 0.35, w2 = 0.30, w3 = 0.25, w4 = 0.10`.

---

### Baseline

- **Baseline Model**: GPT‑3.5‑turbo (OpenAI) answering the same prompts.  
- **Baseline Score**: Compute AQEM for each answer; average over the dataset.  
- **Expected Result**: Baseline AQEM ≈ 0.68 (on a 0–1 scale) on the validation set.

---

### Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| Gold answer is correct and comprehensive. | If gold answer is incomplete, coverage metric under‑penalizes correct but missing details. |
| Embedding model captures semantic equivalence. | Domain‑specific jargon may reduce similarity scores. |
| Fact‑verification model generalizes to the domain. | Models trained on FEVER may misclassify domain‑specific facts. |
| Key‑concept extraction via TF‑IDF is sufficient. | Rare but important concepts may be missed. |
| Length normalization uses simple absolute difference. | Does not account for content density. |

---

### Falsifiable Test

**Test**: Compare AQEM to human expert ratings on a new set of 50 QA pairs.

1. **Procedure**  
   - Collect 50 QA pairs from a domain (e.g., medical guidelines).  
   - Have 5 domain experts rate each answer on a 0–5 Likert scale for correctness, completeness, and clarity.  
   - Compute AQEM for the same answers.

2. **Success Criterion**  
   - Pearson correlation coefficient between AQEM scores and the mean expert rating ≥ 0.70.  
   - If correlation < 0.70, the method fails the test.

**Why it’s falsifiable**: The correlation can be computed exactly; a result below the threshold disproves the claim that AQEM aligns with expert judgment.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
