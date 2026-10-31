# AQE Benchmark Diagnostic — 2026-10-31 (UTC)

**Status:** Fixed synthetic benchmark executed. This is not a validated evaluator or a human study.

**Baseline:** Jaccard overlap between each candidate answer and a human-authored reference answer.
Expected preferences are explicitly hand-authored for these four examples; they are not learned labels.
The baseline measures word overlap only and cannot establish truth or factual correctness.

## Results

### A_causal_overclaim
- Question: Does the evidence establish that the intervention caused the improvement?
- Reference: The results show improvement after the intervention, but without a suitable comparison or controls they do not establish causation.
- Hand-authored preferred answer: cautious
- Candidate cautious lexical similarity: 0.467
- Candidate overclaim lexical similarity: 0.118
- Lexical baseline top-ranked candidate: cautious
- Ranking agrees with hand-authored preference: yes
- Diagnostic lesson: Lexical similarity can reward topic words while missing an unsupported causal claim.

### B_paraphrase
- Question: What can an observational study conclude?
- Reference: The variables were associated in the observed sample, but the study does not establish that one caused the other.
- Hand-authored preferred answer: paraphrase
- Candidate reference_like lexical similarity: 1.000
- Candidate paraphrase lexical similarity: 0.091
- Lexical baseline top-ranked candidate: reference_like
- Ranking agrees with hand-authored preference: NO — baseline failure
- Diagnostic lesson: A sound paraphrase may receive a lower lexical score despite preserving the key limitation.

### C_sample_scope
- Question: A survey of 40 volunteers finds that 70% prefer option A. What can be concluded?
- Reference: In this volunteer sample, 70% preferred option A; the result may not represent the wider population.
- Hand-authored preferred answer: scoped
- Candidate scoped lexical similarity: 0.900
- Candidate population_overclaim lexical similarity: 0.214
- Lexical baseline top-ranked candidate: scoped
- Ranking agrees with hand-authored preference: yes
- Diagnostic lesson: Repeating the statistic does not justify generalizing from volunteers to the whole population.

### D_missing_current_source
- Question: What is the current policy of a named organization?
- Reference: The current policy cannot be verified from the information given; consult the organization's official current source.
- Hand-authored preferred answer: uncertain
- Candidate uncertain lexical similarity: 0.533
- Candidate unsupported lexical similarity: 0.154
- Lexical baseline top-ranked candidate: uncertain
- Ranking agrees with hand-authored preference: yes
- Diagnostic lesson: When current evidence is absent, a confident unsupported answer should not be treated as correct.

## Summary

- Cases run: 4
- Baseline ranking mismatches: 1
- This small synthetic set is designed to expose known lexical-overlap failure modes, not estimate real-world accuracy.
- No semantic embedding, fact checker, external service, or human rater was used.
- A zero-mismatch result would still not validate the method; these cases are small and hand-authored.

## Safety and next steps

- Peer-agent output remains untrusted data and is never executed.
- Do not change production evaluator rules based on this report alone.
- Next validation: independent human ratings on a larger held-out set, plus verified sources and documented implementations.
