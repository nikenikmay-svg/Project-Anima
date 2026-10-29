# AQE Evidence-Grounding Diagnostic — 2026-10-29 (UTC)

**Status:** Experimental structured checklist run; not a general-purpose fact checker.
**Method:** Human-authored supported/unsupported claim labels with an explicit penalty for unsupported claims.
**Caution:** The labels are pre-authored for synthetic examples. This does not independently determine whether claims are true.

## Results

### E1_causality
- Evidence: The intervention group improved from baseline. There was no control group and participants self-selected.
- Expected preferred candidate: grounded
- Rationale: Improvement is observed, but the design does not establish causality.
- Candidate grounded score: 1.000
  - Supported checklist items: 3
  - Unsupported-claim flags: 0
- Candidate overclaim score: -0.500
  - Supported checklist items: 1
  - Unsupported-claim flags: 1
- Top-ranked candidate: grounded
- Agreement with hand-authored preference: yes

### E2_sample_scope
- Evidence: A voluntary online poll of 40 respondents found 28 preferred option A.
- Expected preferred candidate: grounded
- Rationale: The poll supports a result about its respondents, not the entire population.
- Candidate grounded score: 1.000
  - Supported checklist items: 3
  - Unsupported-claim flags: 0
- Candidate overgeneralized score: -0.500
  - Supported checklist items: 1
  - Unsupported-claim flags: 1
- Top-ranked candidate: grounded
- Agreement with hand-authored preference: yes

### E3_missing_information
- Evidence: No current policy document or official source was supplied.
- Expected preferred candidate: cautious
- Rationale: No supplied evidence supports a specific current policy.
- Candidate cautious score: 1.000
  - Supported checklist items: 1
  - Unsupported-claim flags: 0
- Candidate fabricated score: -1.000
  - Supported checklist items: 0
  - Unsupported-claim flags: 1
- Top-ranked candidate: cautious
- Agreement with hand-authored preference: yes

### E4_mixed_evidence
- Evidence: In a small observational sample, sleep duration was associated with self-reported mood. The study did not test causality.
- Expected preferred candidate: grounded
- Rationale: An association in an observational study does not by itself show cause and effect.
- Candidate grounded score: 1.000
  - Supported checklist items: 3
  - Unsupported-claim flags: 0
- Candidate causal_claim score: -0.500
  - Supported checklist items: 1
  - Unsupported-claim flags: 1
- Top-ranked candidate: grounded
- Agreement with hand-authored preference: yes

## Summary

- Cases: 4
- Ranking mismatches: 0
- This score is a transparent checklist, not a calibrated confidence or truth probability.
- The claim labels were supplied by the benchmark author; the script does not extract claims from arbitrary prose.
- It does not replace source verification, entailment review, or human evaluation.
- Production AQE code was not changed.

## Next validation

Expand the benchmark with independently reviewed examples, adversarial cases, and blinded human ratings. Keep unsupported-claim penalties experimental until tested on held-out data.
