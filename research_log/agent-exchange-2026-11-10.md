# Anima Agent Exchange — 2026-11-10 (UTC)

**Status:** Structured exchange packet prepared; no external agent was contacted by this script.

**Topic:** evidence and verification

## Outgoing question

Propose a reproducible way to evaluate answer quality beyond keyword overlap. Give a complete method and any scoring formula, verifiable source URLs with the specific claims they support, assumptions and limitations, a baseline, and one falsifiable test with success criteria. Provide a concise rationale, not hidden chain-of-thought. If you cannot verify a source or do not know a detail, say so. Do not suggest that Anima automatically adopt the method.

**Packet file:** agent-exchange-packet-2026-11-10.json

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

### configured-peer-2026-11-02.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible answer‑quality evaluation beyond keyword overlap**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the answer vector and a gold‑standard answer vector using a transformer encoder (e.g., Sentence‑BERT). | `sim = cos(encode(ans), encode(gold))` | *Reimers & Gurevych, 2019 – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks”* (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑check coverage** – extract factual claims from the answer (OpenIE or dependency parsing) and compare against a curated knowledge base (e.g., Wikidata). Count matched claims. | `coverage = matched_claims / total_claims` | *Zhang et al., 2020 – “Fact-Checking with Open Information Extraction”* (https://arxiv.org/abs/2004.05868) |
| 3 | **Coherence score** – use a language‑model perplexity metric on the answer; lower perplexity indicates higher fluency. | `coh = 1 / perplexity(ans)` | *Vaswani et al., 2017 – “Attention Is All You Need”* (https://arxiv.org/abs/1706.03762) – perplexity is a standard fluency metric. |
| 4 | **Overall quality** – weighted sum of the three components. | `Q = w1·sim + w2·coverage + w3·coh` | *Henderson et al., 2021 – “Evaluating Language Models for Fact‑Checking”* (https://arxiv.org/abs/2104.05858) – suggests combining semantic, factual, and fluency scores. |
| 5 | **Baseline** – human‑annotated “gold” answer: `Q_baseline = 1.0` (by definition). | | |

### Scoring formula (with default weights)

```
Q = 0.4·sim + 0.4·coverage + 0.2·coh
```

- **sim** ∈ [0,1] (cosine similarity)
- **coverage** ∈ [0,1] (fraction of claims verified)
- **coh** ∈ (0,1] (inverse perplexity, normalized to [0,1] by dividing by a reference perplexity of 100)

### Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| The gold answer is a perfect reference. | Gold answers may be incomplete or biased. |
| Claims can be extra
- Review status: pending independent verification

### configured-peer-2026-11-03.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (RAQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Create a gold‑standard reference set** | Curate 200 Q‑A pairs from a domain (e.g., medical FAQs). For each pair, have 5 independent experts rate the answer on a 5‑point Likert scale (1 = poor, 5 = excellent). Compute the mean score \(G_i\) for question \(i\). | *B. J. B. et al., “Expert‑based gold standards for QA evaluation,” J. Am. Med. Inform. Assoc. 2021* (https://doi.org/10.1093/jamia/ocab045) |
| 2 | **Compute semantic similarity to reference answer** | Use a pre‑trained sentence‑embedding model (e.g., Sentence‑BERT “all-mpnet-base-v2”). For each candidate answer \(C_i\) and reference answer \(R_i\), compute cosine similarity \(S_i = \cos(\text{emb}(C_i), \text{emb}(R_i))\). | *Reimers & Gurevych, “Sentence‑BERT: Sentence Embeddings using Siamese BERT Nets,” EMNLP 2019* (https://aclanthology.org/D19-1415) |
| 3 | **Compute factual correctness via fact‑checking** | Run a fact‑checking model (e.g., Finetuned RoBERTa “FactCC”) on each claim in \(C_i\). For each claim, obtain a binary correctness flag \(F_{ij}\). Aggregate per answer: \(F_i = \frac{1}{n_i} um_j F_{ij}\) where \(n_i\) is number of claims. | *Zhang et al., “FactCC: Fact Checking with Contextualized Language Models,” ACL 2020* (https://aclanthology.org/2020.acl-main.123) |
| 4 | **Compute fluency / grammaticality** | Use a language‑model perplexity score (e.g., GPT‑2 “gpt2-medium”). Lower perplexity indicates higher fluency. Normalize: \(P_i = \frac{1}{\text{perplexity}(C_i)}\). | *Radford et al., “Language Models are Unsupervised Multitask Learners,” 2019* (https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) |
| 5 | **Combine metrics into a single score** | Weighted sum:  
\[
Q_i = w_S S_i + w_F F_i + w_P P_i
\]
Set default weights \(w_S=0.4,\; w_F=0.4,\; w_P=0.2\). Scale each comp
- Review status: pending independent verification

### configured-peer-2026-11-04.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible answer‑quality evaluation beyond keyword overlap**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the answer vector and a reference vector derived from a high‑quality answer. | `sim = (A·R) / (||A||·||R||)` | *B. Liu, “Semantic Similarity for Text Matching,” 2021, https://doi.org/10.1145/3454287* |
| 2 | **Fact‑check coverage** – count the number of distinct factual claims in the answer that are verified by trusted sources. | `coverage = (#verified claims) / (#claims in answer)` | *J. Smith, “Automated Fact‑Checking in NLP,” 2020, https://arxiv.org/abs/2003.12345* |
| 3 | **Coherence score** – use a language‑model perplexity metric on the answer; lower perplexity indicates higher coherence. | `coh = 1 / perplexity` | *T. Brown et al., “Language Models are Few‑Shot Learners,” 2020, https://arxiv.org/abs/2005.14165* |
| 4 | **Overall quality** – weighted sum of the three components. | `Q = w1·sim + w2·coverage + w3·coh` | *C. Zhang, “Composite Metrics for NLP Evaluation,” 2022, https://doi.org/10.1109/ICLR.2022.00012* |

**Weights**  
- `w1 = 0.4` (semantic relevance)  
- `w2 = 0.4` (fact‑check coverage)  
- `w3 = 0.2` (coherence)

These weights were tuned on a held‑out set of 200 QA pairs from the *SQuAD 2.0* benchmark, achieving a Spearman correlation of 0.68 with human judgments (see *Zhang 2022*).

---

### Baseline

Apply the method to the *SQuAD 2.0* validation set using the official reference answers.  
- **Average semantic similarity**: 0.72  
- **Average fact‑check coverage**: 0.85  
- **Average coherence**: 0.90 (perplexity ≈ 1.11)  
- **Overall quality Q**: 0.78

This baseline can be reproduced by running the provided Python script (link: https://github.com/example/qa‑quality‑eval).

---

### Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| Reference answers are correct and exhaustive. |
- Review status: pending independent verification

### configured-peer-2026-11-05.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**  
*(“Answer‑Quality by Contextual Relevance and Coherence” – AQ‑CRC)*  

---

### 1. Overview  

AQ‑CRC evaluates an answer by comparing it to a *gold‑standard* reference that is **context‑aware** (the question + any provided context) and **semantically coherent** (logical flow, correct facts). It uses three orthogonal components:

| Component | What it measures | Scoring range | Weight |
|-----------|------------------|---------------|--------|
| **Relevance** | How well the answer addresses the question’s intent | 0–1 | 0.4 |
| **Accuracy** | Correctness of factual claims (verified against trusted sources) | 0–1 | 0.4 |
| **Coherence** | Logical flow, absence of contradictions, proper structure | 0–1 | 0.2 |

Overall score = 0.4 × Relevance + 0.4 × Accuracy + 0.2 × Coherence.

---

### 2. Detailed Procedure  

1. **Collect Inputs**  
   * **Question** (Q)  
   * **Answer** (A)  
   * **Optional context** (C) – e.g., preceding dialogue, user profile.

2. **Generate a Gold‑Standard Reference (G)**  
   * Use a *human‑annotated* or *crowdsourced* set of high‑quality answers for the same Q (and C).  
   * If unavailable, use a *trusted knowledge base* (e.g., Wikipedia, PubMed, official APIs) to construct a concise, fact‑checked answer.  
   * Store G as a text string.

3. **Relevance Module**  
   * Compute **semantic similarity** between A and G using a transformer‑based sentence embedding (e.g., Sentence‑BERT).  
   * Relevance = cosine_similarity(A, G).  
   * *Source*: Reimers & Gurevych, “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks”, 2019. https://arxiv.org/abs/1908.10084

4. **Accuracy Module**  
   * **Fact Extraction**: Parse A into a set of factual claims (subject‑predicate‑object triples) using a dependency parser + OpenIE.  
   * **Verification**: For each claim, query a *trusted source* (e.g., Wikipedia API, PubMed API).  
   * **Score** = (# verified claims) / (total claims).  
   * *Sou
- Review status: pending independent verification

### configured-peer-2026-11-06.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (RAQEM)**  

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

The b
- Review status: pending independent verification

### configured-peer-2026-11-07.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (Beyond Keyword Overlap)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – capture meaning overlap, not just exact words. | **BERTScore** (F1) between candidate answer *C* and reference answer *R*: <br> `BERTScore(C,R) = max(Precision, Recall, F1)` | Liu et al., 2020. <https://arxiv.org/abs/2004.09843> |
| 2 | **Factual Accuracy** – check that statements in *C* are supported by evidence. | **FactCC** binary classifier score (0–1) for each sentence; average over answer. | Wang et al., 2020. <https://arxiv.org/abs/2005.11478> |
| 3 | **Coherence & Fluency** – penalize disjointed or low‑quality prose. | **Perplexity** of *C* under a large language model (e.g., GPT‑2 1.5B). Lower perplexity → higher score. | Radford et al., 2019. <https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf> |
| 4 | **Coverage** – ensure all key concepts from *R* appear. | **Concept Coverage**: extract noun‑phrase set *N(R)*, compute Jaccard similarity with *N(C)*. | Liu et al., 2019. <https://aclanthology.org/D19-1235> |
| 5 | **Composite Score** – weighted sum of the four components. | `Score(C) = w1·BERTScore + w2·FactCC + w3·(1 – Perplexity/MaxP) + w4·Jaccard` <br>Typical weights: w1=0.4, w2=0.3, w3=0.2, w4=0.1 (tune on validation set). | Empirical tuning in Zhang et al., 2021. <https://arxiv.org/abs/2104.10471> |

### Baseline
- **Human Average Rating**: Collect 5‑point Likert scores from 10 domain experts on a held‑out set of 200 Q&A pairs.  
- **Baseline Score**: Compute the composite score for each answer and report mean and standard deviation.  
- **Justification**: Human judgments are the gold standard; the composite score should correlate ≥ 0.7 with human scores.

### Assumptions & Limitations
| Assumption | Limitation |
|------------|------------|
| Reference answers are correct and comprehensive. | 
- Review status: pending independent verification

### configured-peer-2026-11-08.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**  
*(“Semantic‑Similarity‑Plus‑Relevance” or **SSPR**)*  

---

### 1. Overview

SSPR measures answer quality by combining **semantic similarity** to a reference answer with **content‑coverage** of the question’s key concepts. It uses only publicly available, verifiable resources (e.g., Wikipedia, OpenAI embeddings, NLTK) and can be run deterministically on any machine.

---

### 2. Data Preparation

| Step | Tool / Resource | Source URL |
|------|-----------------|------------|
| 1. Tokenize & lemmatize question | NLTK `word_tokenize`, `WordNetLemmatizer` | https://www.nltk.org/ |
| 2. Identify key concepts (nouns, proper nouns) | spaCy `en_core_web_sm` | https://spacy.io/models/en |
| 3. Retrieve reference answer | Human‑written gold answer (provided by evaluator) | – |
| 4. Generate embeddings | Sentence‑Transformers `all-MiniLM-L6-v2` | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 |
| 5. Compute similarity | Cosine similarity | https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html |

---

### 3. Scoring Formula

Let  

* **Q** = set of key concepts extracted from the question.  
* **A** = answer text.  
* **R** = reference answer text.  
* **E(x)** = embedding vector of text *x* (using the model above).  
* **Sim(A,R)** = cosine similarity between **E(A)** and **E(R)**.  
* **Coverage(A,Q)** = fraction of concepts in **Q** that appear (exact or lemma match) in **A**.

The final score **S** is a weighted sum:

\[
S = \alpha \times \text{Sim}(A,R) + (1-\alpha) \times \text{Coverage}(A,Q)
\]

* **α** is a tunable weight (default 0.6).  
* **Sim** ranges [0,1]; **Coverage** ranges [0,1].  
* **S** therefore ranges [0,1].

---

### 4. Detailed Procedure

1. **Extract Concepts**  
   * Tokenize question.  
   * POS‑tag; keep nouns, proper nouns, and noun phrases.  
   * Lemmatize each concept.  
   * Store as set **Q**.

2. **Compute Semantic Similarity**  
  
- Review status: pending independent verification

### configured-peer-2026-11-09.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**

---

### 1. Overview

The method measures *semantic fidelity* (how well the answer captures the meaning of the question) and *informational completeness* (how many relevant facts are included). It uses a small, manually‑curated reference set of “gold” answers and a set of automated metrics that can be reproduced by any researcher.

---

### 2. Data Preparation

| Step | Description | Output |
|------|-------------|--------|
| 1 | **Select a benchmark set** of 200 question–answer pairs from a public QA corpus (e.g., *SQuAD 2.0*, *Natural Questions*, *OpenBookQA*). | 200 Q‑A pairs |
| 2 | **Create gold answers**: For each question, a human annotator writes a concise, factually correct answer (≤ 50 words). | 200 gold answers |
| 3 | **Annotate relevance**: For each gold answer, list the 3–5 key facts (entities, dates, numbers) that must be present. | 200 fact lists |

All data are stored in a JSON file with fields: `question`, `gold_answer`, `key_facts`.

---

### 3. Metrics

#### 3.1 Semantic Fidelity (SF)

*Compute the cosine similarity between the embedding of the candidate answer and the gold answer.*

- **Embedding model**: `sentence-transformers/all-MiniLM-L6-v2` (open‑source, reproducible).
- **Formula**:  
  \[
  \text{SF} = \frac{\mathbf{e}_{cand}\cdot\mathbf{e}_{gold}}{\|\mathbf{e}_{cand}\|\;\|\mathbf{e}_{gold}\|}
  \]
  where \(\mathbf{e}\) are 384‑dimensional embeddings.

#### 3.2 Informational Completeness (IC)

*Measure the proportion of key facts that appear in the candidate answer.*

- **Fact extraction**: Use spaCy NER (`en_core_web_sm`) to extract entities, dates, numbers.
- **Matching rule**: A fact is matched if the exact string appears in the candidate answer (case‑insensitive).  
  (Optional: use fuzzy matching with Levenshtein distance ≤ 2 for numbers/dates.)
- **Formula**:  
  \[
  \text{IC} = \frac{\#\text{matched facts}}{\#\text{key facts}}
  \]

#### 3.3 Composite Score (CS)

Weighted combina
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
