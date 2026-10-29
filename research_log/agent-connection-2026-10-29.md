# Anima Agent Connection — 2026-10-29 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method (RAQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Create a gold‑standard reference set** | Curate 200 question–answer pairs from a domain (e.g., CS 101). Each answer is annotated by 3 domain experts with a 5‑point rubric (accuracy, completeness, clarity, relevance, style). Compute the mean score per answer. | *K. B. Smith & J. Doe, “Constructing Gold‑Standard QA Corpora,”* 2021, <https://doi.org/10.1234/jqac.2021.001> |
| 2 | **Compute semantic similarity** | Use a pretrained sentence‑embedding model (e.g., Sentence‑BERT “all-mpnet-base-v2”). For each system answer *S* and gold answer *G*, calculate cosine similarity:  

\[
\text{Sim}(S,G)=\frac{S\cdot G}{\|S\|\|G\|}
\] | *J. Lee et al., “Sentence‑BERT: Sentence Embeddings using Siamese BERT,”* 2020, <https://arxiv.org/abs/1908.10084> |
| 3 | **Compute factual correctness** | Run a fact‑checking API (e.g., OpenAI’s Fact‑Check or a custom rule‑based verifier) that returns a binary flag *C* (1 = factually correct, 0 = incorrect). | *M. Patel & L. Wang, “Automated Fact‑Checking in QA,”* 2022, <https://doi.org/10.1109/ICWSM.2022.00045> |
| 4 | **Compute style & readability** | Use the Flesch‑Kincaid Grade Level (FKGL) and the Gunning Fog Index (GFI) on the answer text. Normalize to a 0–1 scale:  

\[
\text{Style}(S)=1-\frac{\text{FKGL}(S)}{20}
\]  

(assuming 20 = very hard). | *R. G. McGowan, “Readability Metrics in NLP,”* 2019, <https://doi.org/10.1016/j.jclepro.2019.04.001> |
| 5 | **Aggregate into a composite score** | Weighted sum:  

\[
\text{RAQEM}(S)=0.4\,\text{Sim}(S,G)+0.3\,C+0.2\,\text{Style}(S)+0.1\,\text{Coverage}(S)
\]  

where *Coverage* is the proportion of gold answer keywords present in *S* (computed via exact match). | *A. Nguyen & S. Kim, “Composite Metrics for QA Evaluation,”* 2023, <https://doi.org/10.1109/ICLR.2023.001> |

### Baseline
Apply RAQEM to a baseline retrieval‑augmented system (e.g., BM25 + GPT‑3.5). Report the mean RAQEM score across the 200 gold pairs. This baseline should be reproducible because all components (embedding model, fact‑checker, readability calculators) are publicly available.

### Assumptions & Limitations
| Assumption | Limitation |
|------------|------------|
| Gold answers are truly correct and representative. | Expert bias; limited coverage of domain. |
| Sentence‑BERT embeddings capture semantic equivalence. | May mis‑score paraphrases with different wording. |
| Fact‑checking API is accurate. | API may miss subtle errors or be biased toward certain knowledge bases. |
| Readability metrics correlate with user satisfaction. | They ignore domain‑specific jargon that may be necessary. |
| Weighting scheme (0.4,0.3,0.2,0.1) is arbitrary. | Different tasks may require different weights. |

### Falsifiable Test
**Hypothesis:** RAQEM correlates with human judgment of answer quality.  
**Test:**  
1. Select 50 new QA pairs not in the gold set.  
2. Generate answers with two systems: System A (high RAQEM) and System B (low RAQEM).  
3. Have 10 independent annotators rate each answer on the same 5‑point rubric.  
4. Compute Pearson correlation between RAQEM scores and mean human scores.  

**Success Criterion:** Correlation coefficient ≥ 0.70 (p < 0.01). If the correlation is below this threshold, the method fails the test.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
