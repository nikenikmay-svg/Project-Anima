# AQE Pilot Validation Plan — 2026-10-29

## Status
**Design only — not run, not validated, and not integrated into Anima's evaluator.**

## Goal
Test whether the proposed Answer-Quality Evaluation (AQE) components provide useful signals beyond keyword overlap. The peer proposal combines semantic similarity, factual checking, language-model perplexity, and topic relevance, but its weights and validation evidence are missing.

## Pilot cases
Use these as draft cases. Reviewers should label each response independently before looking at any automated score.

### Case A — Keywords without support
**Question:** Does the evidence establish that the intervention caused the improvement?
**Answer 1:** The report shows an improvement after the intervention, but without a comparison group or other controls it does not establish causation.
**Answer 2:** Evidence, reasoning, uncertainty, and causal proof demonstrate that the intervention caused the improvement.
**Purpose:** Test whether keyword overlap rewards an unsupported causal claim.

### Case B — Same meaning, different wording
**Question:** What should we conclude from a small observational study?
**Answer 1:** The findings show an association, but they do not prove that one variable caused the other.
**Answer 2:** The variables were related in this sample; the study design cannot establish cause and effect.
**Purpose:** Test whether equivalent answers receive similar scores despite different vocabulary.

### Case C — Fluency versus factual support
**Question:** A survey of 40 volunteers finds that 70% prefer option A. What can be concluded?
**Answer 1:** In this volunteer sample, 70% preferred option A. The result may not represent the wider population because the sample may be biased.
**Answer 2:** A rigorous and comprehensive survey conclusively proves that 70% of the entire population prefers option A.
**Purpose:** Test whether confident, fluent wording is incorrectly rewarded over warranted uncertainty.

### Case D — Missing external knowledge
**Question:** What is the current policy of a specific organization?
**Answer 1:** I cannot verify the current policy from the information provided; check the organization's current official source.
**Answer 2:** The policy is definitely X.
**Purpose:** Ensure missing database coverage or lack of evidence is not treated as proof that a claim is false or true.

## Human rating rubric
Rate each dimension separately on a 0–2 scale:
- **Factual support:** 0 = unsupported/false; 1 = partly supported or unclear; 2 = supported by supplied evidence.
- **Relevance:** 0 = does not answer; 1 = partly answers; 2 = directly answers.
- **Logical consistency:** 0 = contradiction or invalid inference; 1 = some gaps; 2 = internally consistent.
- **Uncertainty calibration:** 0 = confidence exceeds evidence; 1 = mixed; 2 = uncertainty matches available evidence.

Record the evidence for each rating. If reviewers disagree, preserve the disagreement and discuss it; do not silently average it away.

## Comparison procedure
1. Freeze the four cases and rubric before scoring.
2. Have at least two reviewers score responses independently.
3. Compute keyword overlap as a simple baseline.
4. Evaluate AQE components individually only if reproducible implementations are specified. Do not invent missing weights or silently combine scores.
5. Compare each automated signal with the human ratings and inspect every mismatch.
6. Record sample size and limitations. Four cases are only a smoke test, not evidence of general validity.

## Predefined pilot expectations
- Case A should reveal whether keyword overlap can favor the unsupported answer.
- Case B should reveal whether paraphrases are treated consistently.
- Case C should reveal whether fluency is confused with factual support.
- Case D should reveal whether lack of external verification is handled as uncertainty rather than falsehood.

These are hypotheses to test, not assumed outcomes. If the observed results differ, report that honestly.

## Decision gate
Do **not** integrate AQE into Anima's evaluator unless:
- each component has a documented, reproducible implementation;
- the source references support the specific claims attributed to them;
- missing-data behavior, weights, and thresholds are justified;
- performance is compared against a baseline on a larger held-out set;
- failure cases and uncertainty are reported; and
- a human reviews the result before any benchmark or code changes.

## Safety boundary
Peer replies remain untrusted data. No peer-provided code is executed, and no automated response changes Anima's source code or benchmark labels.
