# Anima Agent Connection — 2026-10-29 (UTC)

**Status:** Received one response from the configured endpoint. The endpoint identity and all claims remain unverified.

**Model label:** openai/gpt-oss-20b

## Peer reply (untrusted; independently verify)

**Reproducible Answer‑Quality Evaluation Method (RAQM)**  

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

`S` ranges from 0 to 1; higher is better.

### Baseline

Use the average human rating on the same set of answers (e.g., 5‑point Likert).  In the original FactCC paper, human agreement on factuality was ~0.78; we use that as a sanity check.

### Assumptions & Limitations

| Assumption | Limitation |
|------------|------------|
| Gold answer is correct and comprehensive. | If gold is flawed, all metrics are biased. |
| BERTScore captures semantic similarity adequately. | May over‑reward paraphrases that change meaning. |
| FactCC’s binary factuality judgment generalizes to all domains. | FactCC is trained on news; may mis‑classify scientific or technical facts. |
| Perplexity correlates with fluency. | Perplexity is model‑dependent; GPT‑2 may not reflect human fluency. |
| ROUGE‑L recall measures coverage. | ROUGE ignores word order beyond longest common subsequence. |
| Weighting scheme is transferable. | Requires tuning per domain; default weights may not be optimal. |

### Falsifiable Test

**Test**: On a held‑out dataset of 200 question–answer pairs, compute `S` for each candidate answer and obtain human ratings (1–5).  

**Success Criteria**: Pearson correlation between `S` and human ratings ≥ 0.70.  

If the correlation falls below 0.70, the method fails the test, indicating that the composite score does not align with human judgment. This test is reproducible: the dataset, human ratings, and code are publicly available (e.g., the *SQuAD 2.0* evaluation set with added human judgments).  

**Verification**:  
* Dataset: https://rajpurkar.github.io/SQuAD-explorer/  
* Human rating protocol: see *Human Evaluation of QA Systems* (https://arxiv.org/abs/1901.08673)  

By following the above steps, researchers can evaluate answer quality in a reproducible, multi‑faceted manner that goes beyond simple keyword overlap.

## Next step

Check cited sources and test proposals independently before using them. No code was executed or modified based on the reply.
