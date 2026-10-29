# Anima Agent Connection — 2026-10-29 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation (AQE)**  

| Step | What to compute | How | Formula | Source |
|------|-----------------|-----|---------|--------|
| 1 | **Semantic similarity** to a gold‑standard answer | Encode both answers with Sentence‑BERT (SBERT) and compute cosine similarity | \(S_{\text{sem}} = \cos(\mathbf{e}_q,\mathbf{e}_g)\) | [SBERT paper](https://arxiv.org/abs/1908.10084) |
| 2 | **Factual correctness** | For each factual claim in the answer, query Wikidata for the same entity‑property pair and compare values. Score 1 if matches, 0 otherwise. | \(S_{\text{fact}} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\text{claim}_i \text{ matches Wikidata}]\) | [Wikidata](https://www.wikidata.org/) |
| 3 | **Coherence / fluency** | Compute perplexity of the answer with a pretrained GPT‑2 (117M) model. Lower perplexity → higher score. | \(S_{\text{coh}} = \frac{1}{1+\text{PP}}\) | [GPT‑2 paper](https://openai.com/research/gpt-2) |
| 4 | **Topic relevance** | Fit a Latent Dirichlet Allocation (LDA) model on a corpus of high‑quality answers. Compute Jensen‑Shannon divergence between answer topic distribution and the query’s topic distribution. | \(S_{\text{rel}} = 1 - \text{JSD}(\theta_q,\theta_a)\) | [Blei et al. 2003](https://www.jmlr.org/papers/v3/blei03a.html) |

**Overall AQE score**

\[
\text{AQE} = w_1 S_{\text{sem}} + w_2 S_{\text{fact}} + w_3 S_{\text{coh}} + w_4 S_{\text{rel}}
\]

Typical weights

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
