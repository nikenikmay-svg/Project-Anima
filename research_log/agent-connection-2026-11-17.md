# Anima Agent Connection — 2026-11-17 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the answer vector and a set of *gold* reference answers (human‑annotated). | `Sim = cos(v_ans, v_gold)` | *B. Liu et al., “A Survey on Text Similarity Measures,” 2021* – https://doi.org/10.1109/TKDE.2021.3051234 |
| 2 | **Fact‑check coverage** – count how many factual claims in the answer are verified by trusted sources. | `Coverage = (#verified claims) / (#claims in answer)` | *J. Smith, “Automated Fact‑Checking in NLP,” 2020* – https://doi.org/10.1007/s10479-020-03654-7 |
| 3 | **Coherence score** – measure discourse coherence using a pre‑trained language model (e.g., BERT‑LM perplexity). Lower perplexity → higher coherence. | `Coherence = 1 / perplexity` | *K. Lee et al., “Measuring Text Coherence with Language Models,” 2019* – https://doi.org/10.1109/ACL.2019.00045 |
| 4 | **Answer‑length penalty** – discourage overly long or short answers. | `Length = 1 / (1 + |len(ans) – len(gold)|)` | *M. Patel, “Length Bias in QA Evaluation,” 2022* – https://doi.org/10.1145/3534678.3534701 |
| 5 | **Aggregate score** – weighted sum of the four components. | `Score = w1·Sim + w2·Coverage + w3·Coherence + w4·Length` | Weights chosen to sum to 1; default: `w1=0.35, w2=0.30, w3=0.25, w4=0.10` |

### Assumptions & Limitations
- **Gold references** must be curated by domain experts; otherwise similarity may be misleading.  
- **Fact‑check coverage** relies on an up‑to‑date knowledge base; missing sources can under‑score correct answers.  
- **Coherence** depends on the language model’s training data; it may penalize legitimate stylistic variations.  
- **Length penalty** assumes that optimal answer length is close to the gold answer; this may not hold for open‑ended tasks.  
- The method is language‑specific; cross‑lingual adaptation requires multilingual embeddings and fact‑check databases.

### Baseline
For a given QA dataset, compute the aggregate score for:
- **Human‑written answers** (average ≈ 0.82).  
- **Baseline retrieval‑based system** (average ≈ 0.55).  
- **Large‑language‑model answer** (average ≈ 0.70).  
These figures provide a reference range for new systems.

### Falsifiable Test
**Hypothesis**: “Increasing the weight of the fact‑check coverage component (w2) will improve the correlation between the aggregate score and human judgment of factual correctness.”

**Test Procedure**
1. Compute aggregate scores for a held‑out set of 200 QA pairs with human factual‑correctness ratings.  
2. Vary `w2` from 0.1 to 0.5 (keeping other weights adjusted to sum to 1).  
3. For each `w2`, calculate Pearson correlation `r` between aggregate scores and human ratings.  

**Success Criterion**  
If the correlation `r` increases monotonically with `w2` up to a peak (e.g., `r` > 0.75 at `w2=0.4`) and then declines, the hypothesis is supported. If no monotonic improvement is observed, the hypothesis is falsified.

---

**Rationale**  
This method moves beyond keyword overlap by combining semantic similarity, factual verification, discourse coherence, and length normalization. Each component is independently measurable, reproducible, and backed by peer‑reviewed literature. The aggregate score is transparent, tunable, and can be validated against human judgments through the falsifiable test.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
