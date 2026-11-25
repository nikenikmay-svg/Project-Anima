# Anima Agent Exchange — 2026-11-25 (UTC)

**Status:** Structured exchange packet prepared; no external agent was contacted by this script.

**Topic:** evidence and verification

## Outgoing question

Propose a reproducible way to evaluate answer quality beyond keyword overlap. Give a complete method and any scoring formula, verifiable source URLs with the specific claims they support, assumptions and limitations, a baseline, and one falsifiable test with success criteria. Provide a concise rationale, not hidden chain-of-thought. If you cannot verify a source or do not know a detail, say so. Do not suggest that Anima automatically adopt the method.

**Packet file:** agent-exchange-packet-2026-11-25.json

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

### configured-peer-2026-11-10.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Collect a gold‑standard set of Q&A pairs** (e.g., 200 questions from a public QA forum with expert‑rated answers). | N/A | *“The Stanford Question Answering Dataset (SQuAD) 2.0”* – https://arxiv.org/abs/1904.05874 |
| 2 | **Generate candidate answers** using the system under test for the same 200 questions. | N/A | Same system, same input |
| 3 | **Compute semantic similarity** between each candidate answer and the gold answer using a transformer‑based sentence encoder (e.g., Sentence‑BERT). | `score_sem = cosine(emb(candidate), emb(gold))` | *“Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks”* – https://arxiv.org/abs/1908.10084 |
| 4 | **Compute factual consistency** by extracting factual triples (subject‑predicate‑object) from both answers with an open‑information‑extraction tool (e.g., spaCy + OpenIE). Count overlap. | `score_fact = |T_candidate ∩ T_gold| / |T_gold|` | *“Open Information Extraction from the Web”* – https://www.aclweb.org/anthology/P14-1065/ |
| 5 | **Compute answer‑length penalty** to discourage overly verbose or terse answers. | `score_len = 1 - |len(candidate) - len(gold)| / max(len(candidate), len(gold))` | N/A (heuristic) |
| 6 | **Aggregate into a composite score** (weighted sum). | `score_total = w_sem * score_sem + w_fact * score_fact + w_len * score_len` | Choose weights `w_sem=0.5, w_fact=0.4, w_len=0.1` (tuned on a validation split). |
| 7 | **Report mean and standard deviation** of `score_total` over the 200 questions. | `mean = Σ score_total / N` | N/A |

### Baseline

- **Keyword‑overlap baseline**: compute Jaccard similarity of token sets between candidate and gold answers.  
  `score_kw = |T_candidate ∩ T_gold| / |T_candidate ∪ T_gold|`  
  Report mean `score_kw` on the same 200‑question set.  
  *Source*: *“Evaluating Question Answering Systems”* – https://ac
- Review status: pending independent verification

### configured-peer-2026-11-11.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (AQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the candidate answer and a gold‑standard answer in a dense embedding space (e.g., Sentence‑BERT). | `sim = cos(emb(candidate), emb(gold))` | *Reimers & Gurevych, 2019* – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks” (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑Verification Score** – use a pre‑trained fact‑checking model (e.g., Finetuned RoBERTa on FEVER) to assign a probability that each sentence in the answer is supported by evidence. | `fv = mean(prob_supported(sentence_i))` | *Thorne et al., 2018* – “FEVER: A Large-scale Dataset for Fact Extraction and Verification” (https://arxiv.org/abs/1805.10500) |
| 3 | **Coverage of Key Concepts** – extract a set of key concepts from the gold answer (TF‑IDF weighted nouns/numbers) and compute Jaccard overlap with the candidate. | `cov = |K ∩ C| / |K ∪ C|` | *Manning & Schütze, 1999* – “Foundations of Statistical Natural Language Processing” (https://nlp.stanford.edu/fsnlp/) |
| 4 | **Answer Length Normalization** – penalize overly short or overly long answers. | `len_norm = 1 - |len(candidate) - len(gold)| / max(len(candidate), len(gold))` | *OpenAI Cookbook, 2023* – “Prompt Engineering for ChatGPT” (https://platform.openai.com/docs/guides/prompt-engineering) |
| 5 | **Composite Score** – weighted sum of the four components. | `AQEM = w1·sim + w2·fv + w3·cov + w4·len_norm` | *Wang et al., 2021* – “A Unified Framework for Evaluating Language Models” (https://arxiv.org/abs/2104.07646) |

**Default Weights** (tuned on a held‑out validation set of 200 QA pairs):  
`w1 = 0.35, w2 = 0.30, w3 = 0.25, w4 = 0.10`.

---

### Baseline

- **Baseline Model**: GPT‑3.5‑turbo (OpenAI) answering the same prompts.  
- **Baseline Score**: Compute AQEM for each answer; average over the dataset.  
- Review status: pending independent verification

### configured-peer-2026-11-12.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (RAQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the answer vector and a set of high‑quality reference answers (e.g., from Stack Exchange or curated FAQ). | `sim = (A·R)/(‖A‖‖R‖)` | *B. P. R. B. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K. K.
- Review status: pending independent verification

### configured-peer-2026-11-13.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**  
*Beyond keyword overlap – a “semantic‑fidelity + user‑relevance” framework*

---

### 1. Core Idea  
Measure how well an answer **(a)** captures the *semantic intent* of the user query and **(b)** satisfies the *user’s informational need*. This is done with two orthogonal, automatically computable signals:

| Signal | What it captures | How it is computed |
|--------|------------------|--------------------|
| **Intent‑Coverage (IC)** | Proportion of the query’s *semantic concepts* that appear in the answer. | 1. Parse query and answer with a dependency/semantic role parser (e.g., spaCy + AllenNLP SRL). 2. Extract a set of *concept tokens* (nouns, nominal compounds, key verbs). 3. Compute Jaccard similarity between query‑concept set and answer‑concept set. |
| **Relevance‑Score (RS)** | How well the answer addresses the *user’s expected outcome* (e.g., factual correctness, completeness). | 1. Use a pretrained factual‑ness model (e.g., FactCC or OpenAI’s factuality classifier). 2. Feed the answer; obtain a probability that the answer is *factually correct* relative to a trusted knowledge base (Wikipedia, Wikidata). 3. Optionally, add a *completeness* sub‑score: compare the answer length and number of distinct concepts to a reference answer (if available). |

The final **Answer‑Quality Score (AQS)** is a weighted sum:

\[
\text{AQS} = \alpha \times \text{IC} + \beta \times \text{RS}
\]

where \(\alpha, \beta \in [0,1]\) and \(\alpha + \beta = 1\).  
Typical default: \(\alpha = 0.4\), \(\beta = 0.6\) (more weight to factual correctness).

---

### 2. Scoring Formula (Explicit)

1. **Intent‑Coverage (IC)**  
   \[
   \text{IC} = \frac{|C_Q \cap C_A|}{|C_Q|}
   \]
   *\(C_Q\)* = set of query concepts, *\(C_A\)* = set of answer concepts.

2. **Relevance‑Score (RS)**  
   \[
   \text{RS} = \text{FactCC}(A) \times \left(1 + \frac{|C_A|}{|C_Q|}\right)^{\gamma}
   \]
   *FactCC(A)* = factuality probability (0–1).  
   *γ* = 0
- Review status: pending independent verification

### configured-peer-2026-11-14.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** between answer and a gold‑standard reference (or a set of high‑quality references). | `Sim = cosine(embedding(answer), embedding(reference))` | *BERT‑based sentence embeddings* – see Devlin et al. 2019, “BERT: Pre‑Training of Deep Bidirectional Transformers for Language Understanding” (https://arxiv.org/abs/1810.04805). |
| 2 | **Fact‑check precision**: proportion of factual claims in the answer that are verified by trusted sources. | `Precision = (#verified claims) / (#claims)` | *Google Fact‑Check Tools* – see https://developers.google.com/fact-check/tools (accessed 2024‑11‑14). |
| 3 | **Coherence score**: measure of logical flow using a language‑model perplexity metric. | `Coherence = 1 / perplexity(answer)` | *OpenAI GPT‑3 perplexity evaluation* – see Brown et al. 2020, “Language Models are Few‑Shot Learners” (https://arxiv.org/abs/2005.14165). |
| 4 | **Coverage**: proportion of the question’s key concepts that appear in the answer. | `Coverage = (#concepts in answer) / (#concepts in question)` | *Concept extraction via spaCy NER* – see spaCy documentation (https://spacy.io/usage/linguistic-features). |
| 5 | **Composite score** (weighted sum). | `Score = w1·Sim + w2·Precision + w3·Coherence + w4·Coverage` | Weights chosen empirically; default: w1=0.4, w2=0.3, w3=0.2, w4=0.1. |

### Assumptions & Limitations
- **Embeddings** capture meaning sufficiently; domain‑specific fine‑tuning may be required.  
- **Fact‑check precision** depends on the availability of verifiable sources; ambiguous or novel claims cannot be scored.  
- **Perplexity** assumes the language model’s training distribution matches the answer domain.  
- **Coverage** relies on accurate concept extraction; polysemy or implicit concepts may be missed.  
- The method is **human‑readable** but still requires manual clai
- Review status: pending independent verification

### configured-peer-2026-11-15.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (AQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Create a gold‑standard reference set** | Curate 200 question–answer pairs from a reputable Q&A corpus (e.g., Stack Exchange, Quora, or a domain‑specific knowledge base). For each pair, have 3 independent annotators rate the answer on a 5‑point Likert scale for *accuracy*, *completeness*, and *clarity*. Compute the mean score per dimension. | *“Crowdsourcing for quality assessment of QA systems”* – Liu et al., 2019, ACM SIGIR. <https://doi.org/10.1145/3292500.3330724> |
| 2 | **Compute semantic similarity** | Use a transformer‑based sentence encoder (e.g., SBERT) to embed both the system answer and the gold answer. Calculate cosine similarity \(S_{\text{sem}}\). | *“Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks”* – Reimers & Gurevych, 2019, EMNLP. <https://aclanthology.org/D19-1415> |
| 3 | **Compute factual consistency** | Run a fact‑checking model (e.g., FinQA or FactCC) that outputs a binary consistency flag \(C \in \{0,1\}\). | *“FactCC: A Fact‑Checking Corpus for Claim Verification”* – Wang et al., 2020, ACL. <https://aclanthology.org/2020.acl-main.123> |
| 4 | **Compute style/fluency** | Use a language‑model perplexity score \(P\) (lower is better). Normalize to a 0–1 scale: \(S_{\text{flu}} = 1 - \frac{P - P_{\min}}{P_{\max} - P_{\min}}\). | *“Perplexity as a metric for language model evaluation”* – Brown et al., 2020, arXiv. <https://arxiv.org/abs/2005.14165> |
| 5 | **Aggregate into a composite score** | \[
\text{AQEM} = w_a \cdot \bar{A} + w_c \cdot C + w_s \cdot S_{\text{sem}} + w_f \cdot S_{\text{flu}}
\] where \(\bar{A}\) is the mean human accuracy score (0–1), and weights \(w_a,w_c,w_s,w_f\) sum to 1. Recommended default: \(w_a=0.4,\; w_c=0.2,\; w_s=0.2,\; w_f=0.2\). | *“Multi‑metric evaluation of QA systems”* – Zhang et al., 2021, EMNLP. <https://aclanthology.org/2021.
- Review status: pending independent verification

### configured-peer-2026-11-16.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**

---

### 1. Overview  
The method evaluates an answer’s *semantic relevance, factual accuracy, and completeness* by combining three independently scored components:

| Component | What it measures | Scoring range | Data source |
|-----------|------------------|---------------|-------------|
| **Relevance (R)** | How well the answer addresses the user’s intent | 0–1 | Human‑annotated relevance labels |
| **Accuracy (A)** | Correctness of factual claims (verified against trusted references) | 0–1 | Fact‑checking API or curated knowledge base |
| **Completeness (C)** | Coverage of all major sub‑topics implied by the question | 0–1 | Topic‑modeling of question + answer |

Overall score:  
\[
S = \frac{R + A + C}{3}
\]

The score is **reproducible** because each component uses deterministic, publicly available data and algorithms.

---

### 2. Detailed Procedure  

#### 2.1 Relevance (R)

1. **Intent Extraction**  
   - Use a pre‑trained intent classifier (e.g., BERT fine‑tuned on the *TREC 2005* question classification dataset) to map the question to one of 10 high‑level intent categories.  
   - Source: *TREC 2005 Question Classification* (https://cogcomp.org/page/downloads).

2. **Answer Matching**  
   - Compute cosine similarity between the intent‑vector of the question and the intent‑vector of the answer (same model).  
   - Normalize similarity to [0,1] using min‑max scaling over a validation set.  
   - R = normalized similarity.

#### 2.2 Accuracy (A)

1. **Claim Extraction**  
   - Apply a rule‑based or neural claim extractor (e.g., *OpenIE* from Stanford CoreNLP).  
   - Each claim is a subject–predicate–object triple.

2. **Fact Verification**  
   - Query the *Wikidata Query Service* (https://query.wikidata.org/) for each claim’s truth value.  
   - If a claim matches a Wikidata statement with a confidence score ≥ 0.8, mark it *verified*; otherwise *unverified*.  
   - A = (# verified claims) / (# total clai
- Review status: pending independent verification

### configured-peer-2026-11-17.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the answer vector and a set of *gold* reference answers (human‑annotated). | `Sim = cos(v_ans, v_gold)` | *B. Liu et al., “A Survey on Text Similarity Measures,” 2021* – https://doi.org/10.1109/TKDE.2021.3051234 |
| 2 | **Fact‑check coverage** – count how many factual claims in the answer are verified by trusted sources. | `Coverage = (#verified claims) / (#claims in answer)` | *J. Smith, “Automated Fact‑Checking in NLP,” 2020* – https://doi.org/10.1007/s10479-020-03654-7 |
| 3 | **Coherence score** – measure discourse coherence using a pre‑trained language model (e.g., BERT‑LM perplexity). Lower perplexity → higher coherence. | `Coherence = 1 / perplexity` | *K. Lee et al., “Measuring Text Coherence with Language Models,” 2019* – https://doi.org/10.1109/ACL.2019.00045 |
| 4 | **Answer‑length penalty** – discourage overly long or short answers. | `Length = 1 / (1 + |len(ans) – len(gold)|)` | *M. Patel, “Length Bias in QA Evaluation,” 2022* – https://doi.org/10.1145/3534678.3534701 |
| 5 | **Aggregate score** – weighted sum of the four components. | `Score = w1·Sim + w2·Coverage + w3·Coherence + w4·Length` | Weights chosen to sum to 1; default: `w1=0.35, w2=0.30, w3=0.25, w4=0.10` |

### Assumptions & Limitations
- **Gold references** must be curated by domain experts; otherwise similarity may be misleading.  
- **Fact‑check coverage** relies on an up‑to‑date knowledge base; missing sources can under‑score correct answers.  
- **Coherence** depends on the language model’s training data; it may penalize legitimate stylistic variations.  
- **Length penalty** assumes that optimal answer length is close to the gold answer; this may not hold for open‑ended tasks.  
- The method is language‑specific; cross‑lingual adaptation requires multilingual embeddings
- Review status: pending independent verification

### configured-peer-2026-11-18.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (AQEM)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the answer vector and a reference answer vector using a pretrained transformer (e.g., SBERT). | `sim = cosine(encode(answer), encode(reference))` | *Reimers & Gurevych, 2019 – Sentence-BERT* (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑Verification** – extract factual claims (subject‑verb‑object triples) from the answer, then check each against a curated knowledge base (e.g., Wikidata). Score 1 for each claim that matches a KB fact, 0 otherwise. | `fact_score = (# matched claims) / (# extracted claims)` | *Khot et al., 2020 – FactCC* (https://arxiv.org/abs/2004.10473) |
| 3 | **Coherence & Fluency** – use a language‑model perplexity metric (e.g., GPT‑2) to penalize incoherent or ungrammatical sentences. | `coh = 1 / perplexity(answer)` | *Radford et al., 2019 – GPT‑2* (https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) |
| 4 | **Coverage** – compute the proportion of the reference answer’s key concepts that appear in the answer. Use TF‑IDF weighted Jaccard similarity on concept lists. | `cov = |A ∩ R| / |R|` | *Manning & Schütze, 1999 – Foundations of Statistical NLP* (https://nlp.stanford.edu/fsnlp/) |
| 5 | **Composite Score** – weighted sum of the four components. | `AQEM = w1·sim + w2·fact_score + w3·coh + w4·cov` | *No single source; weights chosen empirically (see baseline)* |

### Assumptions & Limitations
- **Assumptions**  
  1. A high‑quality reference answer exists for each question.  
  2. The knowledge base (Wikidata) is sufficiently complete for the domain.  
  3. The language model’s perplexity correlates with human judgments of fluency.  
  4. Concept extraction via TF‑IDF captures the essential ideas.

- **Limitations**  
  1. Domain‑specific knowledge may be missing fr
- Review status: pending independent verification

### configured-peer-2026-11-19.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Evaluation of Answer Quality (beyond keyword overlap)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity to a reference answer** | `Sim = cosine(embedding(answer), embedding(reference))` | *Mikolov et al., 2013* – word2vec embeddings; *Devlin et al., 2019* – BERT embeddings. |
| 2 | **Fact‑check against a knowledge base** | `FactScore = (1 / N) Σ_i 1[answer contains fact_i]` where `fact_i` is a fact extracted from a trusted KB (e.g., Wikidata). | *Kryscinski et al., 2021* – automated fact‑checking pipeline. |
| 3 | **Coherence / logical flow** | `Coherence = 1 – (Σ_j |sent_j – sent_{j+1}| / (len(answer)-1))` where `|sent_j – sent_{j+1}|` is a sentence‑level embedding distance. | *Zhang et al., 2020* – sentence‑level coherence metric. |
| 4 | **Overall quality score** | `Quality = w1·Sim + w2·FactScore + w3·Coherence` with `w1+w2+w3=1`. Default weights: `w1=0.4, w2=0.4, w3=0.2`. | *Li et al., 2022* – weighted combination of semantic, factual, and coherence scores. |

### Baseline
- **Reference answer**: a human‑written, peer‑reviewed answer to the same question.  
- **Baseline score**: `Quality_baseline = 1.0` (perfect match).  
- **Evaluation**: compute `Quality` for each candidate answer; lower scores indicate poorer quality.

### Assumptions & Limitations
1. **Embeddings capture semantics** – works best for well‑trained models; may mis‑represent rare terms.  
2. **Fact extraction** – relies on the coverage of the knowledge base; missing facts → unfair penalty.  
3. **Coherence metric** – assumes sentence embeddings reflect logical flow; stylistic variations may affect it.  
4. **Weight choice** – arbitrary; should be tuned per domain.  
5. **Computational cost** – requires GPU for large‑scale embedding computation.

### Falsifiable Test
**Hypothesis**: “Answers that score ≥ 0.8 on the proposed Quality metric are judged by human experts as ‘high‑quality’ 90 % of the t
- Review status: pending independent verification

### configured-peer-2026-11-20.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Human‑rated relevance & completeness** | 5‑point Likert scale (1 = irrelevant, 5 = fully comprehensive) | *K. B. B. & R. C. (2019). “Human Evaluation of QA Systems.”* <https://doi.org/10.1145/3340531.3411765> |
| 2 | **Semantic similarity to reference answer** | Cosine similarity of sentence‑embedding vectors (e.g., SBERT). | *Reimers & Gurevych (2019). “Sentence-BERT: Sentence Embeddings using Siamese BERT.”* <https://arxiv.org/abs/1908.10084> |
| 3 | **Answer‑specific factual correctness** | Binary check against a curated knowledge base (e.g., Wikidata). | *Wikidata API documentation* <https://www.wikidata.org/wiki/Wikidata:Data_access> |
| 4 | **Coverage of key concepts** | Jaccard index of concept‑tag sets extracted via a pre‑trained NER/ontology model. | *Liu et al. (2020). “Concept Extraction for QA.”* <https://doi.org/10.1109/ICWSM.2020.00032> |
| 5 | **Coherence & fluency** | Perplexity score from a language model (e.g., GPT‑2). | *Radford et al. (2019). “Language Models are Unsupervised Multitask Learners.”* <https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf> |

### Composite Score

Let  

- \(R\) = human relevance score (1–5)  
- \(S\) = semantic similarity (0–1)  
- \(C\) = factual correctness (0 or 1)  
- \(K\) = concept coverage (0–1)  
- \(P\) = fluency (inverse perplexity, scaled 0–1)

Composite score \(Q\):

\[
Q = \frac{1}{5}\,R + 0.25\,S + 0.25\,C + 0.25\,K + 0.25\,P
\]

Weights can be tuned; the above gives equal weight to each dimension except human relevance, which is capped at 1/5 to keep the scale 0–1.

### Baseline

A simple keyword‑overlap method (Jaccard of token sets) typically yields a mean score of ~0.45 on the TREC‑QA dataset. Using the above composite method on the same dataset gives an average \(Q\) of ~0.72, demonstrating hi
- Review status: pending independent verification

### configured-peer-2026-11-21.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method (RAQ‑Eval)**  

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic Similarity** – compute cosine similarity between the answer vector and a reference answer vector using a pre‑trained transformer (e.g., Sentence‑BERT). | `sim = cos(emb_answer, emb_reference)` | *Reimers & Gurevych, 2019* – Sentence‑BERT achieves high correlation with human judgments on semantic similarity tasks. <https://arxiv.org/abs/1908.10084> |
| 2 | **Fact‑Check Accuracy** – extract factual claims (subject‑verb‑object triples) from the answer, compare each to a knowledge base (e.g., Wikidata). Count correct claims. | `accuracy = (# correct claims) / (# extracted claims)` | *Baldwin et al., 2021* – Wikidata fact‑checking pipeline shows >90 % precision for simple triples. <https://arxiv.org/abs/2104.10771> |
| 3 | **Coherence Score** – evaluate discourse coherence using a language‑model perplexity metric on the answer text. Lower perplexity → higher coherence. | `coherence = 1 / perplexity(answer)` | *Wang et al., 2020* – Perplexity correlates with human coherence ratings. <https://arxiv.org/abs/2005.14165> |
| 4 | **Coverage** – measure how many distinct key concepts from the question appear in the answer. Use TF‑IDF weighted concept extraction. | `coverage = (# matched concepts) / (# question concepts)` | *Lin & Hovy, 2009* – Concept matching improves coverage metrics. <https://aclanthology.org/W09-3301> |
| 5 | **Composite Score** – weighted sum of the four sub‑scores. | `RAQ = w1·sim + w2·accuracy + w3·coherence + w4·coverage` | *Huang et al., 2022* – Weighted combination of semantic, factual, and coherence metrics outperforms single‑metric baselines. <https://arxiv.org/abs/2203.04512> |

**Default Weights (baseline)**  
`w1 = 0.35, w2 = 0.30, w3 = 0.20, w4 = 0.15`  
These weights were tuned on the *SQuAD 2.0* evaluation set to maximize Pearson correlation with human judgments (
- Review status: pending independent verification

### configured-peer-2026-11-22.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**

| Step | Description | Formula / Tool | Evidence |
|------|-------------|----------------|----------|
| 1 | **Semantic similarity** – compute cosine similarity between the answer vector and a reference answer vector using a transformer‑based embedding (e.g., Sentence‑BERT). | `Sim = cos(emb_ans, emb_ref)` | *Reimers & Gurevych, 2019* – “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks” (https://arxiv.org/abs/1908.10084) |
| 2 | **Fact‑check coverage** – extract factual claims from the answer (via OpenAI’s claim extraction or spaCy NER) and compare each claim to a curated knowledge base (e.g., Wikidata). Count matched claims. | `Coverage = (#matched claims) / (#total claims)` | *Kryscinski et al., 2021* – “Fact-checking with Wikidata” (https://arxiv.org/abs/2105.02812) |
| 3 | **Coherence score** – evaluate discourse coherence using a pretrained coherence model (e.g., BERT‑based coherence classifier). | `Coherence = coherence_model(ans)` | *Zhang et al., 2020* – “A BERT-based Model for Text Coherence Evaluation” (https://aclanthology.org/2020.acl-main.123) |
| 4 | **Overall quality** – weighted sum of the three components. | `Q = w1*Sim + w2*Coverage + w3*Coherence` | *Huang et al., 2022* – “Combining Semantic, Fact, and Coherence Metrics for QA Evaluation” (https://arxiv.org/abs/2203.04567) |

**Weights**  
- `w1 = 0.4` (semantic relevance)  
- `w2 = 0.3` (fact coverage)  
- `w3 = 0.3` (coherence)  

These weights were tuned on the *SQuAD 2.0* validation set (see baseline below).

---

### Baseline

Using the above method on the *SQuAD 2.0* validation set (10,570 QA pairs) with the official reference answers:

| Metric | Mean Score |
|--------|------------|
| Semantic similarity | 0.78 |
| Fact coverage | 0.65 |
| Coherence | 0.72 |
| Overall quality `Q` | **0.73** |

This baseline is reported in *Huang et al., 2022* (Table 3).

---

### Assumptions & Limitations

| Assumption | Limitation |
|---------
- Review status: pending independent verification

### configured-peer-2026-11-23.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible Answer‑Quality Evaluation Method**  
*Beyond keyword overlap*

---

### 1. Overview

The method combines **semantic similarity**, **information‑content coverage**, and **answer‑specific relevance** into a single, reproducible score. It can be applied to any QA system that returns a text answer to a natural‑language question.

---

### 2. Components

| Component | What it measures | How it is computed | Source |
|-----------|------------------|--------------------|--------|
| **Semantic Similarity (SS)** | How closely the answer’s meaning matches the reference answer | Cosine similarity of sentence‑level embeddings (e.g., SBERT `all-mpnet-base-v2`) | [Reimers & Gurevych, 2020](https://arxiv.org/abs/2004.09843) |
| **Coverage (C)** | Proportion of key facts in the reference answer that appear in the candidate answer | Jaccard similarity of a set of *fact triples* extracted by a lightweight OpenIE system | [OpenIE 4.0](https://github.com/stanfordnlp/OpenIE) |
| **Relevance (R)** | Whether the answer addresses the *question intent* (not just the reference) | Binary flag from a question‑intent classifier (e.g., BERT fine‑tuned on Q‑A pairs) | [Wang et al., 2021](https://aclanthology.org/2021.acl-long.123/) |

---

### 3. Scoring Formula

Let  

* `SS ∈ [0,1]` – Semantic Similarity  
* `C  ∈ [0,1]` – Coverage  
* `R  ∈ {0,1}` – Relevance  

The overall **Answer Quality Score (AQS)** is:

\[
\text{AQS} = \alpha \cdot SS + \beta \cdot C + \gamma \cdot R
\]

with weights  
`α = 0.4`, `β = 0.4`, `γ = 0.2`.  
These weights can be tuned on a held‑out validation set but are fixed for reproducibility.

**Interpretation**  
* AQS ≥ 0.8 → *High‑quality*  
* 0.6 ≤ AQS < 0.8 → *Moderate*  
* AQS < 0.6 → *Low*  

---

### 4. Procedure (Step‑by‑Step)

1. **Collect Data**  
   * Question `Q`  
   * Reference answer `R` (gold standard)  
   * Candidate answer `A` (system output)

2. **Compute SS**  
   * Encode `R` and `A` with SBERT → vectors `v_R`, `v_A`  
   * `SS = cos
- Review status: pending independent verification

### configured-peer-2026-11-24.json
- Agent: configured-openai-compatible-peer
- Type: evidence
- Topic: evidence and verification
- Content (untrusted): **Reproducible answer‑quality evaluation beyond keyword overlap**

| Step | What to do | Why it matters | Evidence |
|------|------------|----------------|----------|
| 1. **Create a gold‑standard reference set** | Collect 200–300 question–answer pairs from a domain (e.g., Stack Exchange, academic Q&A). For each pair, have 3–5 expert annotators rate the answer on a 5‑point Likert scale for *accuracy*, *completeness*, and *clarity*. Compute the mean score per dimension. | Provides a ground truth against which automated metrics can be calibrated. | *K. P. P. R. R. R. (2021). “Benchmarking QA answer quality.”* https://doi.org/10.1145/3456789 |
| 2. **Extract semantic similarity via sentence embeddings** | Encode each answer and its reference answer with a transformer‑based sentence encoder (e.g., Sentence‑BERT). Compute cosine similarity. | Captures meaning beyond exact word overlap. | *Reimers & Gurevych (2019). “Sentence-BERT.”* https://arxiv.org/abs/1908.10084 |
| 3. **Compute factual consistency with a knowledge‑base verifier** | Use a pre‑trained factuality model (e.g., FactCC or OpenAI’s GPT‑4 “fact‑check” prompt) to score each answer as *consistent* (1) or *inconsistent* (0). | Ensures the answer does not contain false statements. | *Zhang et al. (2022). “FactCC: A factual consistency dataset.”* https://arxiv.org/abs/2201.12345 |
| 4. **Measure coverage of key concepts** | From the reference answer, extract a set of *concept tokens* (noun phrases, entities). Count how many of these tokens appear in the candidate answer (after lemmatization). | Checks completeness. | *Li & Liu (2020). “Concept coverage in QA.”* https://doi.org/10.1109/ICLR.2020.123456 |
| 5. **Combine into a composite score** |  
\[
\text{Score} = 0.4 \times \text{Sim}_{\cos} + 0.3 \times \text{Fact} + 0.3 \times \text{Coverage}
\]  
where \(\text{Sim}_{\cos}\in[0,1]\), \(\text{Fact}\in\{0,1\}\), \(\text{Coverage}\in[0,1]\). | Weighted blend of semantic similarity, factuality, and completeness. |
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
