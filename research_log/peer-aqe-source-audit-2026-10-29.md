# Peer AQE Proposal — Source Verification Audit

**Audit date:** 2026-10-29  
**Purpose:** Record what could and could not be independently verified from the peer response.  
**Rule:** A citation that could not be verified in this audit is not automatically proven fake; it must not be relied on until its DOI resolves and its metadata matches the claimed work.

## Findings

| Peer citation or claim | Audit result | Safe interpretation |
|---|---|---|
| K. B. Smith & J. Doe, “Constructing Gold-Standard QA Corpora” (2021), DOI 10.1234/jqac.2021.001 | **Not verified** in the public search performed for this audit. No matching authoritative record was found in the returned results. | Do not cite or rely on it unless the DOI resolves to matching publisher metadata. |
| M. Patel & L. Wang, “Automated Fact-Checking in QA” (2022), DOI 10.1109/ICWSM.2022.00045 | **Not verified** in the public search performed for this audit. | Do not cite or rely on it unless the DOI resolves to matching publisher metadata. |
| R. G. McGowan, “Readability Metrics in NLP” (2019), DOI 10.1016/j.jclepro.2019.04.001 | **Not verified** as the stated title/author combination in the public search performed for this audit. | Verify DOI landing-page metadata before use. |
| A. Nguyen & S. Kim, “Composite Metrics for QA Evaluation” (2023), DOI 10.1109/ICLR.2023.001 | **Not verified** in the public search performed for this audit. | Do not cite or rely on it unless the DOI resolves to matching publisher metadata. |
| “Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,” arXiv:1908.10084 | **Verified as a real paper** by Nils Reimers and Iryna Gurevych, submitted in 2019 and published at EMNLP 2019. The paper supports using sentence embeddings and cosine similarity for semantic similarity tasks. | It does **not** establish factual correctness, nor validate the peer's proposed composite score or weights. Official records: https://arxiv.org/abs/1908.10084 and https://aclanthology.org/D19-1410/ |
| “OpenAI's Fact-Check API” | **Not established by the evidence reviewed.** The peer response did not give a verifiable product documentation link. | Treat this as an unverified example, not a confirmed available API. A custom verifier would need its own documented design and evaluation. |

## Method limitations

- This was a focused web search, not a complete scholarly database audit.
- “Not verified” means this audit did not establish a matching authoritative record; it is not proof that a publication does not exist.
- The peer response's suggested weights (0.4, 0.3, 0.2, 0.1) are proposals, not empirically validated constants.
- Exact keyword coverage, readability formulas, and semantic similarity each measure different properties. None alone proves answer correctness.
- A composite score should not be introduced until each component is reproducible, tested against independent human ratings, and evaluated on held-out examples.

## Decision

**Do not integrate the proposed RAQEM formula into Anima's evaluator yet.** Keep the current evaluator unchanged. Run the fixed AQE benchmark diagnostic separately and require human review before adopting any changes.
