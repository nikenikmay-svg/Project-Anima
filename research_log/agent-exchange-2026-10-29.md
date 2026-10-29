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
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**

---

### 1. Overview  
The method combines **semantic similarity**, **fact‑verification**, and **readability** into a single composite score. It can be run automatically on any pair of (question, answer) and is fully reproducible because every component uses publicly available models or datasets.

---

### 2. Components & Formula  

| Component | Metric | Source / Tool | Weight |
|-----------|--------|---------------|--------|
| **Semantic Relevance (SR)** | Cosine similarity between question and answer embeddings (SBERT “all-mpnet-base-v2”) | HuggingFace model hub | 0.35 |
| **Fact‑Accuracy (FA)** | Proportion of answer sentences that are verified by an external fact‑checking API (OpenAI’s Fact‑Check API or Google Fact Check Tools) | Google Fact‑Check Tools API (public) | 0.35 |
| **Readability (RD)** | Flesch‑Kincaid Grade Level (lower is better) mapped to a 0–1 score | `textstat` Python package | 0.15 |
| **Answer Length (AL)** | Normalized length (tokens) to penalize overly short or excessively long answers | Tokenizer from `transformers` | 0.15 |

Composite Score (CS):

\[
CS = 0.35 \times SR + 0.35 \times FA + 0.15 \times (1 - RD) + 0.15 \times AL
\]

*All sub‑scores are scaled to [0, 1] before weighting.*

---

### 3. Detailed Procedure  

1. **Pre‑processing**  
   * Tokenize question and answer.  
   * Split answer into sentences (e.g., `nltk.sent_tokenize`).  

2. **Semantic Relevance**  
   * Encode question and answer with SBERT.  
   * Compute cosine similarity → SR.  

3. **Fact‑Accuracy**  
   * For each answer sentence, query the Google Fact‑Check Tools API.  
   * If the API returns a claim with a “fact‑check” verdict of “True” or “Mostly True”, count it as verified.  
   * FA = (# verified sentences) / (total sentences).  

4. **Readability**  
   * Compute Flesch‑Kincaid Grade Level (FKGL).  
   * Map FKGL to RD:  
     \[
     RD = \min\left(1, \frac{FKGL}{12}\right)
     \]  
     (Assumes grade
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
