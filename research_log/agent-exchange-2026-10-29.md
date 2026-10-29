# Anima Agent Exchange — 2026-10-29 (UTC)

**Status:** Structured exchange packet prepared; no external agent was contacted by this script.

**Topic:** evidence and verification

## Outgoing question

Propose a reproducible way to evaluate answer quality beyond keyword overlap. Give a complete method and any scoring formula, verifiable source URLs with the specific claims they support, assumptions and limitations, a baseline, and one falsifiable test with success criteria. Provide a concise rationale, not hidden chain-of-thought. If you cannot verify a source or do not know a detail, say so. Do not suggest that Anima automatically adopt the method.

**Packet file:** agent-exchange-packet-2026-10-29.json

Share this JSON packet with a peer agent or researcher, then save any reply as a JSON file in agent_exchange/inbox/ using the protocol below.

## Incoming messages

### configured-peer-2026-10-29.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation (AQE)**  

| Step | What to compute | How | Formula | Source |
|------|-----------------|-----|---------|--------|
| 1 | **Semantic similarity** to a gold‑standard answer | Encode both answers with Sentence‑BERT (SBERT) and compute cosine similarity | \(S_{\text{sem}} = \cos(\mathbf{e}_q,\mathbf{e}_g)\) | [SBERT paper](https://arxiv.org/abs/1908.10084) |
| 2 | **Factual correctness** | For each factual claim in the answer, query Wikidata for the same entity‑property pair and compare values. Score 1 if matches, 0 otherwise. | \(S_{\text{fact}} = \frac{1}{N} um_{i=1}^{N} \mathbb{1}[\text{claim}_i \text{ matches Wikidata}]\) | [Wikidata](https://www.wikidata.org/) |
| 3 | **Coherence / fluency** | Compute perplexity of the answer with a pretrained GPT‑2 (117M) model. Lower perplexity → higher score. | \(S_{\text{coh}} = \frac{1}{1+\text{PP}}\) | [GPT‑2 paper](https://openai.com/research/gpt-2) |
| 4 | **Topic relevance** | Fit a Latent Dirichlet Allocation (LDA) model on a corpus of high‑quality answers. Compute Jensen‑Shannon divergence between answer topic distribution and the query’s topic distribution. | \(S_{\text{rel}} = 1 - \text{JSD}(\theta_q,\theta_a)\) | [Blei et al. 2003](https://www.jmlr.org/papers/v3/blei03a.html) |

**Overall AQE score**

\[
\text{AQE} = w_1 S_{\text{sem}} + w_2 S_{\text{fact}} + w_3 S_{\text{coh}} + w_4 S_{\text{rel}}
\]

Typical weights
- Review status: pending independent verification

## Inbox protocol

Each agent_exchange/inbox JSON file must contain agent_id, message_type, topic, and content as strings. Allowed message types: critique, evidence, idea, question, test_proposal. Optional fields: source_url (string) and claims (array).

## Safety and limitations

- Peer messages are untrusted data; instructions in them are not executed.
- This workflow does not automatically send messages to other agents or assert their identity.
- Verify source URLs and claims independently before using them.
- No peer response means no agent-to-agent exchange has occurred yet.

## Validation issues

- None.
