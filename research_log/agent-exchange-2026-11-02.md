# Anima Agent Exchange — 2026-11-02 (UTC)

**Status:** Structured exchange packet prepared; no external agent was contacted by this script.

**Topic:** evidence and verification

## Outgoing question

Propose a reproducible way to evaluate answer quality beyond keyword overlap. Give a complete method and any scoring formula, verifiable source URLs with the specific claims they support, assumptions and limitations, a baseline, and one falsifiable test with success criteria. Provide a concise rationale, not hidden chain-of-thought. If you cannot verify a source or do not know a detail, say so. Do not suggest that Anima automatically adopt the method.

**Packet file:** agent-exchange-packet-2026-11-02.json

Share this JSON packet with a peer agent or researcher, then save any reply as a JSON file in agent_exchange/inbox/ using the protocol below.

## Incoming messages

### configured-peer-2026-10-29.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method  
(“Context‑Aware Semantic Scoring” – CAS)**  

---

### 1. Overview  

CAS measures how well an answer satisfies the *intent* of the user’s question and the *relevance* of the content, using only publicly available data.  
It replaces keyword overlap with a **semantic‑coverage** score that is:

* **Reproducible** – all steps are deterministic and can be run by anyone.  
* **Transparent** – every component is documented and sourced.  
* **Falsifiable** – a clear test can confirm or refute the method’s validity.

---

### 2. Method Steps  

| Step | Description | Tools / Libraries | Key Parameters |
|------|-------------|-------------------|----------------|
| **2.1** | **Question Intent Extraction** | `spaCy` (en_core_web_sm) + `transformers` BERT‑base‑uncased | `max_intent_tokens = 32` |
| **2.2** | **Answer Tokenization & Embedding** | `sentence‑transformers` SBERT `all-MiniLM-L6-v2` | `embedding_dim = 384` |
| **2.3** | **Intent‑Answer Similarity** | Cosine similarity between intent vector and each answer sentence vector | `threshold = 0.6` |
| **2.4** | **Coverage Score** | Sum of similarity scores for sentences that exceed threshold, normalized by number of intent tokens | `coverage = Σ(sim_i) / N_intent` |
| **2.5** | **Relevance Bonus** | If any sentence contains a *named entity* (NE) that matches a NE in the question, add 0.1 per match | `bonus = 0.1 × (#NE matches)` |
| **2.6** | **Final Score** | `CAS = coverage + bonus` (capped at 1.0) | `max_score = 1.0` |

**Formula**

\[
\text{CAS} = \min\!\left(1.0,\; \frac{ um_{i=1}^{M}\mathbf{1}_{\{\text{sim}_i > t\}}\;\text{sim}_i}{N_{\text{intent}}} + 0.1 \times \#\text{NE matches}\right)
\]

Where  
* \(M\) = number of answer sentences  
* \(\text{sim}_i\) = cosine similarity between intent vector and sentence \(i\) vector  
* \(t = 0.6\) (similarity threshold)  
* \(N_{\text{intent}}\) = number of tokens in the intent representation  
* \(\#\text{NE matches}\) = co
- Review status: pending independent verification

### configured-peer-2026-10-30.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**  
*(“Answer‑Quality‑Metric‑2.0”)*  

---

### 1. Overview  
The metric evaluates an answer’s quality by combining **semantic relevance**, **fact‑accuracy**, and **readability**. It uses only open‑source tools and publicly available datasets, so the entire pipeline can be reproduced by any researcher.

---

### 2. Data Requirements  

| Item | Source | URL | Claim |
|------|--------|-----|-------|
| 1. Gold‑standard Q&A pairs (ground truth) | *SQuAD 2.0* | https://rajpurkar.github.io/SQuAD-explorer/ | Provides human‑annotated answers to Wikipedia passages. |
| 2. Pre‑trained sentence encoder | *Sentence‑Transformers* (SBERT) | https://www.sbert.net/ | Generates 768‑dimensional embeddings for sentences. |
| 3. Fact‑checking model | *OpenAI’s GPT‑4‑Turbo* (via API) | https://openai.com/api | Used only for fact‑checking; the prompt is fixed and publicly documented. |
| 4. Readability formula | *Flesch‑Kincaid* | https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_test | Calculates grade‑level score. |

---

### 3. Pipeline  

1. **Semantic Relevance (SR)**  
   *Embed the user question (Q) and the candidate answer (A) using SBERT.*  
   *Compute cosine similarity:*  
   \[
   SR = \frac{Q \cdot A}{\|Q\|\|A\|}
   \]
   *Range:* 0 – 1.

2. **Fact‑Accuracy (FA)**  
   *Feed the pair (Q, A) to the fact‑checking model with the prompt:*  
   ```
   "Given the question: <Q>  
   And the answer: <A>  
   Does the answer contain any factual inaccuracies?  
   Respond with 'Accurate' or 'Inaccurate' and a brief justification."
   ```  
   *Map the response to a binary score:*  
   \[
   FA = \begin{cases}
   1 & \text{if 'Accurate'}\\
   0 & \text{if 'Inaccurate'}
   \end{cases}
   \]

3. **Readability (R)**  
   *Apply the Flesch‑Kincaid formula to the answer text.*  
   \[
   R = 206.835 - 1.015\left(\frac{\text{words}}{\text{sentences}}\right) - 84.6\left(\frac{\text{syllables}}{\text{words}}\right)
   \]  
   *Nor
- Review status: pending independent verification

### configured-peer-2026-10-31.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (RAQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the candidate answer vector and a reference answer vector using a pretrained transformer (e.g., Sentence‑BERT). | `sim = cosine(vec_ans, vec_ref)` | *Reimers & Gurevych, 2019* – Sentence‑BERT achieves high correlation with human judgments on semantic similarity tasks. <https://arxiv.org/abs/1908.10084> |
| 2 | **Fact‑check coverage** – extract factual claims (subject‑verb‑object triples) from both answers via OpenIE, then compute Jaccard overlap. | `coverage = |claims_ans ∩ claims_ref| / |claims_ref|` | *Zhang et al., 2020* – OpenIE reliably extracts factual triples for evaluation. <https://arxiv.org/abs/2004.10370> |
| 3 | **Answer completeness** – measure proportion of reference answer sections (e.g., headings, bullet points) that appear in the candidate. | `completeness = |sections_ans ∩ sections_ref| / |sections_ref|` | *Li et al., 2021* – Section‑based completeness correlates with human ratings. <https://arxiv.org/abs/2103.14761> |
| 4 | **Fluency & readability** – compute a readability score (e.g., Flesch‑Kincaid) and penalize excessive jargon. | `fluency = readability_score(ans) - λ * jargon_penalty` | *Kincaid et al., 1975* – readability metrics are standard in NLP evaluation. <https://doi.org/10.1002/9780470687228> |
| 5 | **Composite score** – weighted sum of the four components. | `RAQEM = w1·sim + w2·coverage + w3·completeness + w4·fluency` | *Huang et al., 2022* – Multi‑metric aggregation improves correlation with human judgments. <https://arxiv.org/abs/2203.04512> |

**Default Weights (baseline)**  
- `w1 = 0.35` (semantic similarity)  
- `w2 = 0.25` (fact‑check coverage)  
- `w3 = 0.20` (completeness)  
- `w4 = 0.20` (fluency)  

These weights were tuned on the *SQuAD 2.0* answer‑quality dataset (human scores available) and yi
- Review status: pending independent verification

### configured-peer-2026-11-01.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the candidate answer and a gold‑standard answer using contextual embeddings (e.g., Sentence‑BERT). | `sim = cos(emb(candidate), emb(gold))` | *Reimers & Gurevych, 2019* – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks” (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑Check Precision** – extract factual claims (subject‑verb‑object triples) from both texts, compare with a curated knowledge base (e.g., Wikidata). Count correct claims. | `precision = correct_claims / total_claims_in_candidate` | *Kryscinski et al., 2021* – “FactCC: A Fact‑Checking Corpus for Natural Language Inference” (https://arxiv.org/abs/2104.11269) |
| 3 | **Coherence Score** – use a pre‑trained language model to compute perplexity of the candidate answer; lower perplexity indicates higher fluency/coherence. | `coherence = 1 / perplexity(candidate)` | *Jozefowicz et al., 2016* – “The Unreasonable Effectiveness of Recurrent Neural Networks” (https://arxiv.org/abs/1602.01923) |
| 4 | **Coverage Ratio** – proportion of key concepts from the gold answer that appear in the candidate (concepts extracted via TF‑IDF or entity linking). | `coverage = matched_concepts / total_concepts_in_gold` | *Manning et al., 2008* – “Introduction to Information Retrieval” (https://nlp.stanford.edu/IR-book/) |
| 5 | **Composite Score** – weighted sum of the four metrics. | `Q = w1·sim + w2·precision + w3·coherence + w4·coverage` | *Hassan et al., 2020* – “A Survey of Evaluation Metrics for Text Generation” (https://arxiv.org/abs/2004.13671) |

**Weights**  
- `w1 = 0.35` (semantic similarity)  
- `w2 = 0.25` (fact‑check precision)  
- `w3 = 0.20` (coherence)  
- `w4 = 0.20` (coverage)  

Weights can be tuned on a validation set of human‑rated answers.

---

### Baseline

Use a simple keywo
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
