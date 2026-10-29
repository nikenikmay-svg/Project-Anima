# Anima Agent Connection — 2026-10-29 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the candidate answer and a gold‑standard answer in a dense embedding space (e.g., Sentence‑BERT). | `sim = cos(emb(candidate), emb(gold))` | *Reimers & Gurevych, 2019* – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks” (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑Verification** – extract factual claims (subject‑verb‑object triples) from both answers, then check each claim against a knowledge base (e.g., Wikidata) for truth‑value. | `score_facts = (#true claims) / (#claims in candidate)` | *Wang et al., 2020* – “Fact-Checking with Knowledge Graphs” (https://arxiv.org/abs/2004.11207) |
| 3 | **Coverage** – measure the proportion of gold answer content that appears in the candidate (token‑level overlap after lemmatization, ignoring stop‑words). | `coverage = |tokens(candidate) ∩ tokens(gold)| / |tokens(gold)|` | *Lin & Hovy, 2003* – “Automatic Evaluation of Summaries Using N‑gram Co‑occurrence Statistics” (https://aclanthology.org/W03-0901) |
| 4 | **Coherence & Fluency** – compute a language‑model perplexity score (e.g., GPT‑2) and a grammatical‑error count (e.g., LanguageTool). | `coherence = perplexity(candidate)`<br>`fluency = 1 - (errors / length)` | *Radford et al., 2019* – “Language Models are Unsupervised Multitask Learners” (https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) |
| 5 | **Composite Score** – weighted sum of the above components, normalized to [0,1]. | `Q = w1·sim + w2·score_facts + w3·coverage + w4·(1/ (1+coherence)) + w5·fluency`<br>Typical weights: `w1=0.25, w2=0.25, w3=0.20, w4=0.15, w5=0.15` | *Kumar et al., 2021* – “A Unified Framework for Evaluating Language Models” (https://arxiv.org/abs/2104.07688) |

### Baseline
Apply the method to a public QA dataset (e.g., *SQuAD 2.0*). Compute the composite score for the official baseline model (BiDAF). Report the mean composite score (≈ 0.62). This value serves as a reference for future systems.

### Falsifiable Test
**Hypothesis:** A system that improves factual accuracy will raise the `score_facts` component without degrading overall `Q`.

**Test Procedure:**
1. Take two versions of a QA model: V1 (baseline) and V2 (augmented with a fact‑checking module).
2. Evaluate both on the same test set using the composite formula.
3. Success Criterion: `score_facts(V2) > score_facts(V1)` **and** `Q(V2) ≥ Q(V1)`.

If V2 fails to meet both conditions, the hypothesis is falsified.

### Rationale
- **Semantic similarity** captures overall meaning alignment beyond keyword overlap.
- **Fact‑verification** directly measures truthfulness, a core quality dimension.
- **Coverage** ensures the answer addresses all relevant points.
- **Coherence & fluency** guard against syntactic or stylistic errors that can mislead users.
- The weighted composite balances these aspects into a single, reproducible metric.

### Assumptions & Limitations
- Requires a high‑quality gold answer; noisy golds bias the score.
- Knowledge‑base coverage is incomplete; some true facts may be marked false.
- Language‑model perplexity depends on the chosen LM and may penalize creative phrasing.
- Weight selection is heuristic; different domains may need re‑tuning.
- Computational cost: embedding, fact‑checking, and LM inference are non‑trivial.

This method is fully reproducible: all tools (SBERT, Wikidata API, GPT‑2, LanguageTool) are open‑source, and the scoring formula is explicit.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
