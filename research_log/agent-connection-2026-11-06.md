# Anima Agent Connection — 2026-11-06 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method (RAQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the answer vector and a set of high‑quality reference answers (e.g., from Stack Exchange or curated FAQ). | `sim = cos( vec(answer), mean(vec(refs)) )` | *Bengio et al., 2013* – “A neural probabilistic language model” (https://doi.org/10.1109/ICASSP.2013.6638949) |
| 2 | **Fact‑check coverage** – extract factual claims (subject‑predicate‑object triples) from the answer and from a trusted knowledge base (e.g., Wikidata). Count matched triples. | `coverage = |matches| / |claims|` | *Kwiatkowski et al., 2019* – “FEVER: a large-scale dataset for fact‑checking” (https://arxiv.org/abs/1901.08608) |
| 3 | **Coherence score** – measure discourse cohesion using a pretrained language model’s perplexity on the answer. Lower perplexity → higher coherence. | `coh = 1 / perplexity(answer)` | *Vaswani et al., 2017* – “Attention Is All You Need” (https://arxiv.org/abs/1706.03762) |
| 4 | **Answer‑length penalty** – discourage overly long or short answers. | `len_pen = exp( - (|len(answer)-L_opt| / σ)^2 )` where `L_opt=200` tokens, `σ=50`. | *Zhang et al., 2019* – “A Survey on Automatic Text Summarization” (https://doi.org/10.1109/TKDE.2019.2897495) |
| 5 | **Composite score** – weighted sum of the above components. | `RAQ = w1*sim + w2*coverage + w3*coh + w4*len_pen` with `w1=w2=w3=w4=0.25`. | *Hassan et al., 2021* – “Evaluating Language Models for Question Answering” (https://arxiv.org/abs/2104.07675) |

### Baseline
- **Reference set**: 10 high‑quality answers per question from the official Stack Exchange “accepted” answers.  
- **Knowledge base**: Wikidata (latest dump).  
- **Tokenizer**: SentencePiece (BPE) with 32k vocab.  
- **Embedding model**: Sentence‑BERT (paraphrase-MiniLM-L6-v2).  
- **Perplexity model**: GPT‑2‑small (117M parameters).  

The baseline composite score for a known good answer is ≈ 0.82 (±0.04).  

### Assumptions & Limitations
| Assumption | Limitation |
|------------|------------|
| Reference answers are truly correct and representative. | If the reference set contains errors, similarity and coverage will be misleading. |
| Claims can be reliably extracted via OpenIE. | Complex sentences or implicit facts may be missed, lowering coverage. |
| Perplexity correlates with coherence. | Perplexity is model‑dependent; different language models may give different values. |
| Length penalty uses a fixed optimal length. | Optimal length varies by domain; the penalty may unfairly penalize concise expert answers. |
| Equal weighting of components. | Different tasks may require different emphasis (e.g., factual QA vs. creative writing). |

### Falsifiable Test
**Hypothesis**: RAQEM scores correlate positively with human expert judgments of answer quality.  

**Test Procedure**  
1. Collect 50 Q&A pairs from a domain (e.g., medical FAQs).  
2. Have 5 domain experts rate each answer on a 5‑point Likert scale (1 = poor, 5 = excellent).  
3. Compute RAQEM scores for the same answers.  
4. Calculate Spearman’s rank‑correlation coefficient (ρ) between expert ratings and RAQEM scores.  

**Success Criterion**  
- ρ ≥ 0.60 with p < 0.01.  
- If ρ falls below 0.60, the method fails the test and must be revised (e.g., adjust weights, add components).  

This test is fully reproducible: the dataset, expert panel, and code can be shared, and the correlation can be recomputed by any researcher.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
