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
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (RAQEM)**  

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
Apply RAQEM to a baseline retrieval‑augment
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
