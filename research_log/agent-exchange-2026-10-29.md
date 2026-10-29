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
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (RAQM)**  

| Step | Description | Tool / Model | Reference |
|------|-------------|--------------|-----------|
| 1 | **Semantic similarity** – compare the candidate answer to a gold‑standard answer using BERTScore (exact‑match, precision, recall, F1). | `bert-score` (HuggingFace) | Liu et al., 2020 – *BERTScore: Evaluating Text Generation with BERT* (https://arxiv.org/abs/1904.09675) |
| 2 | **Factual consistency** – run FactCC on the candidate answer against the gold answer to obtain a factual‑consistency probability. | FactCC (OpenAI‑trained) | Liu et al., 2020 – *FactCC: A Fact‑Checking Dataset for Natural Language Inference* (https://arxiv.org/abs/2004.12207) |
| 3 | **Coherence / Fluency** – compute the perplexity of the candidate answer under a large language model (e.g., GPT‑2 1.5B). Lower perplexity → higher fluency. | GPT‑2 (HuggingFace) | Radford et al., 2019 – *Language Models are Unsupervised Multitask Learners* (https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) |
| 4 | **Coverage / Completeness** – calculate ROUGE‑L recall between the candidate and gold answer to capture coverage of key n‑grams. | ROUGE‑L (Python‑Rouge) | Lin, 2004 – *ROUGE: A Package for Automatic Evaluation of Summaries* (https://www.cs.utexas.edu/~nlp/rouge/) |
| 5 | **Composite score** – weighted sum of the four metrics.  The weights are tuned on a small validation set of human‑rated answers.  A default set is: 0.35 × BERTScore‑F1 + 0.30 × FactCC + 0.20 × (1‑Perplexity‑norm) + 0.15 × ROUGE‑L recall. | Custom script | – |

### Scoring Formula

Let  

* `BERT_F1` = BERTScore F1 (0–1)  
* `FactCC` = factual‑consistency probability (0–1)  
* `PPL_norm` = normalized perplexity: `PPL_norm = (PPL_candidate – PPL_min) / (PPL_max – PPL_min)` (0–1)  
* `ROUGE_L` = ROUGE‑L recall (0–1)

Composite score `S`:

```
S = 0.35 * BERT_F1 + 0.30 * FactCC + 0.20 * (1 - PPL_norm) + 0.15 * ROUGE_L
```

`
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
