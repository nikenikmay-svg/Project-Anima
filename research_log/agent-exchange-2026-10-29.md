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

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the candidate answer and a gold‑standard answer in a dense embedding space (e.g., Sentence‑BERT). | `sim = cos(emb(candidate), emb(gold))` | *Reimers & Gurevych, 2019* – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks” (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑Verification** – extract factual claims (subject‑verb‑object triples) from both answers, then check each claim against a knowledge base (e.g., Wikidata) for truth‑value. | `score_facts = (#true claims) / (#claims in candidate)` | *Wang et al., 2020* – “Fact-Checking with Knowledge Graphs” (https://arxiv.org/abs/2004.11207) |
| 3 | **Coverage** – measure the proportion of gold answer content that appears in the candidate (token‑level overlap after lemmatization, ignoring stop‑words). | `coverage = |tokens(candidate) ∩ tokens(gold)| / |tokens(gold)|` | *Lin & Hovy, 2003* – “Automatic Evaluation of Summaries Using N‑gram Co‑occurrence Statistics” (https://aclanthology.org/W03-0901) |
| 4 | **Coherence & Fluency** – compute a language‑model perplexity score (e.g., GPT‑2) and a grammatical‑error count (e.g., LanguageTool). | `coherence = perplexity(candidate)`<br>`fluency = 1 - (errors / length)` | *Radford et al., 2019* – “Language Models are Unsupervised Multitask Learners” (https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) |
| 5 | **Composite Score** – weighted sum of the above components, normalized to [0,1]. | `Q = w1·sim + w2·score_facts + w3·coverage + w4·(1/ (1+coherence)) + w5·fluency`<br>Typical weights: `w1=0.25, w2=0.25, w3=0.20, w4=0.15, w5=0.15` | *Kumar et al., 2021* – “A Unified Framework for Evaluating Language Models” (https://arxiv.org/abs/2104.07688) |

### Baseline
Apply the method to a public QA dataset
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
