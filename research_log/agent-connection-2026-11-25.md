# Anima Agent Connection — 2026-11-25 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the answer vector and a set of reference answer vectors (human‑graded gold answers) using a transformer encoder (e.g., SBERT). | `Sim = cos(Enc(answer), Enc(gold))` | *Reimers & Gurevych, 2019* – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks” (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑check coverage** – extract factual claims (subject‑verb‑object triples) from the answer, compare against a curated knowledge base (e.g., Wikidata). Count matched claims. | `Coverage = |Claims_matched| / |Claims_total|` | *Kryscinski et al., 2020* – “FactCC: A Fact‑Checking Corpus for Natural Language Inference” (https://arxiv.org/abs/2004.07671) |
| 3 | **Coherence & fluency** – use a language‑model perplexity score (GPT‑2 or similar) to penalize incoherent sentences. | `Coherence = 1 / Perplexity(answer)` | *Radford et al., 2019* – “Language Models are Unsupervised Multitask Learners” (https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) |
| 4 | **Answer‑question alignment** – compute question‑answer relevance via a supervised QA model (e.g., BERT‑QA). | `Relevance = QA_model.score(question, answer)` | *Rajpurkar et al., 2018* – “SQuAD: 100,000+ Questions for Machine Comprehension of Text” (https://arxiv.org/abs/1606.05250) |
| 5 | **Composite score** – weighted sum of the four components. | `Score = w1·Sim + w2·Coverage + w3·Coherence + w4·Relevance` | *Henderson et al., 2021* – “A Survey of Automatic Evaluation Metrics for NLP” (https://arxiv.org/abs/2104.07148) |

**Weights**  
- `w1 = 0.35` (semantic similarity)  
- `w2 = 0.25` (fact coverage)  
- `w3 = 0.20` (coherence)  
- `w4 = 0.20` (relevance)  

Weights can be tuned on a held‑out validation set of human‑rated answers.

---

### Baseline

Use the **ROUGE‑L** overlap metric (standard in many NLP benchmarks) as a baseline. Compute the average ROUGE‑L F1 score over the same test set. Report the baseline alongside the composite score to illustrate improvement.

---

### Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| Reference gold answers are representative of high‑quality responses. | If gold answers are sparse or biased, similarity may be misleading. |
| Knowledge base (Wikidata) contains all factual claims needed. | Out‑of‑knowledge claims cannot be verified, lowering coverage unfairly. |
| Language‑model perplexity correlates with human fluency. | Perplexity is sensitive to tokenization and model size; may penalize creative phrasing. |
| QA relevance model is trained on a domain similar to the test data. | Domain mismatch reduces relevance scores. |
| Linear combination of components is sufficient. | Interactions between components are ignored; non‑linear models could capture more nuance. |

---

### Falsifiable Test

**Test Statement**  
> “The composite score will be statistically significantly higher (p < 0.01) than the ROUGE‑L baseline on a held‑out set of 500 QA pairs.”

**Procedure**  
1. Collect 500 QA pairs with human‑rated quality scores.  
2. Compute both the composite score and ROUGE‑L for each pair.  
3. Perform a paired t‑test on the two score distributions.  
4. If the p‑value < 0.01, the test passes; otherwise, the method fails.

**Success Criterion**  
A p‑value < 0.01 indicates that the proposed method consistently outperforms the ROUGE‑L baseline, demonstrating that it captures aspects of answer quality beyond keyword overlap. If the test fails, revisit component weights or add additional signals (e.g., discourse structure).

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
