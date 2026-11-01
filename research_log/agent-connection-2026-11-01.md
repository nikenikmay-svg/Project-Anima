# Anima Agent Connection — 2026-11-01 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the candidate answer and a gold‑standard answer using contextual embeddings (e.g., Sentence‑BERT). | `sim = cos(emb(candidate), emb(gold))` | *Reimers & Gurevych, 2019* – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks” (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑Check Precision** – extract factual claims (subject‑verb‑object triples) from both texts, compare with a curated knowledge base (e.g., Wikidata). Count correct claims. | `precision = correct_claims / total_claims_in_candidate` | *Kryscinski et al., 2021* – “FactCC: A Fact‑Checking Corpus for Natural Language Inference” (https://arxiv.org/abs/2104.11269) |
| 3 | **Coherence Score** – use a pre‑trained language model to compute perplexity of the candidate answer; lower perplexity indicates higher fluency/coherence. | `coherence = 1 / perplexity(candidate)` | *Jozefowicz et al., 2016* – “The Unreasonable Effectiveness of Recurrent Neural Networks” (https://arxiv.org/abs/1602.01923) |
| 4 | **Coverage Ratio** – proportion of key concepts from the gold answer that appear in the candidate (concepts extracted via TF‑IDF or entity linking). | `coverage = matched_concepts / total_concepts_in_gold` | *Manning et al., 2008* – “Introduction to Information Retrieval” (https://nlp.stanford.edu/IR-book/) |
| 5 | **Composite Score** – weighted sum of the four metrics. | `Q = w1·sim + w2·precision + w3·coherence + w4·coverage` | *Hassan et al., 2020* – “A Survey of Evaluation Metrics for Text Generation” (https://arxiv.org/abs/2004.13671) |

**Weights**  
- `w1 = 0.35` (semantic similarity)  
- `w2 = 0.25` (fact‑check precision)  
- `w3 = 0.20` (coherence)  
- `w4 = 0.20` (coverage)  

Weights can be tuned on a validation set of human‑rated answers.

---

### Baseline

Use a simple keyword‑overlap metric (Jaccard similarity of stemmed words) as the baseline. Report its average score on the same test set; the proposed method should achieve at least 15 % higher composite score.

---

### Falsifiable Test

**Hypothesis**: The composite score correlates with human judgments of answer quality.  

**Test**:  
1. Collect 200 question–answer pairs.  
2. Have 5 annotators rate each answer on a 5‑point Likert scale for correctness, completeness, and fluency.  
3. Compute Pearson correlation between the composite score `Q` and the mean human rating.  

**Success Criterion**: `r ≥ 0.60` (moderate‑to‑strong correlation). If the correlation is below 0.60, the method fails the test.

---

### Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| Gold‑standard answers are accurate and representative. | If gold answers are noisy, similarity and coverage metrics become unreliable. |
| Knowledge base (Wikidata) covers all factual claims. | Rare or domain‑specific facts may be missing, lowering precision. |
| Language model perplexity reflects coherence for the target language. | Perplexity is sensitive to tokenization and model size; may not capture logical coherence. |
| Weighting scheme generalizes across domains. | Requires re‑tuning for specialized fields (e.g., medical). |
| Human ratings are consistent. | Inter‑annotator agreement may be low; use Krippendorff’s alpha > 0.7 as a sanity check. |

---

### Rationale

Keyword overlap ignores semantics, factual accuracy, and fluency. By combining **semantic similarity**, **fact‑check precision**, **coherence**, and **coverage**, the method captures multiple dimensions of answer quality that are measurable, reproducible, and interpretable. The composite score is transparent, and the falsifiable test ensures that higher scores correspond to better human‑perceived quality.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
