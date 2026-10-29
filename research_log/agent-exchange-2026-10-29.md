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
*(Beyond keyword overlap)*  

---

### 1. Core Idea  
Measure how well an answer **covers the user’s intent** and **provides accurate, verifiable facts** by combining three orthogonal signals:

| Signal | What it captures | How it is computed |
|--------|------------------|--------------------|
| **Intent‑Coverage (IC)** | Proportion of the user’s question that the answer addresses. | Semantic similarity between question sub‑clauses and answer sentences (BERT‑based cosine). |
| **Fact‑Accuracy (FA)** | Proportion of factual claims that are supported by reliable sources. | Automatic claim extraction + evidence retrieval + evidence‑matching score. |
| **Coherence & Readability (CR)** | Fluency, logical flow, and grammatical quality. | Language‑model perplexity + readability indices. |

The final **Answer‑Quality Score (AQS)** is a weighted sum:

\[
\text{AQS} = w_{IC}\cdot IC + w_{FA}\cdot FA + w_{CR}\cdot CR
\]

*Default weights*: \(w_{IC}=0.4,\; w_{FA}=0.4,\; w_{CR}=0.2\).  
Weights can be tuned on a held‑out validation set.

---

### 2. Detailed Procedure

#### 2.1 Intent‑Coverage (IC)

1. **Question Decomposition**  
   - Use a dependency parser (spaCy v3) to split the question into *n* clauses (e.g., “What is X?” → clause 1; “How does it affect Y?” → clause 2).  
   - *Assumption*: Each clause represents a distinct intent component.

2. **Sentence‑to‑Clause Similarity**  
   - Encode each clause and each answer sentence with a pre‑trained sentence‑embedding model (e.g., `all-mpnet-base-v2`).  
   - Compute cosine similarity; for each clause, take the maximum similarity over all answer sentences.

3. **IC Calculation**  
   \[
   IC = \frac{1}{n} um_{i=1}^{n}\max_{j}\text{cosine}(c_i, a_j)
   \]
   *Range*: 0–1.

#### 2.2 Fact‑Accuracy (FA)

1. **Claim Extraction**  
   - Run a rule‑based or neural claim extractor (e.g., `claim-extractor` library) on the answer to produce a list of claims \( \{C_k\} \).

2. **Evi
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
