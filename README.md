# Project Anima

A small, transparent Python project for evaluating whether an answer mentions required concepts. Anima currently uses phrase matching and conservative lexical contradiction markers; it is **not** a semantic reasoner and does not verify scientific truth.

## Run it

Requires Python 3.

```bash
python anima.py
```

Enter an answer to the sample question. The command-line report shows:
- a keyword coverage score,
- matched, missing, and possibly contradicted criteria,
- the exact clauses that matched each criterion,
- clauses where a contradiction marker triggered review.

## Modular reasoning-indicator checklist

The separate `reasoning.py` module offers `analyze_reasoning_indicators(answer)`. It checks for configured lexical signals in three categories:
- **Evidence:** terms such as evidence, data, observations, studies, and measurements.
- **Reasoning:** terms such as because, therefore, implies, logic, and inference.
- **Uncertainty:** terms such as may, might, likely, estimate, limitation, and unknown.

The result shows detected/not-detected categories and the exact clauses that triggered each category. This is a modular inspection aid, not a semantic reasoning engine: terms can appear in misleading contexts, and sound reasoning may use different wording. Detection does not validate a source, prove an inference, or establish that uncertainty is appropriately calibrated.

## Run the checks

```bash
python -m unittest
python benchmark.py
```

The benchmark writes `benchmark-results.json`, including per-criterion evidence traces. Its cases are hand-written regression examples, not a representative language dataset. A passing benchmark means the program matched those expected labels—not that it understood the answer.

## Current limitations

- Contradiction detection relies on a small list of lexical markers.
- Clause splitting recognizes only a few common contrast transitions.
- Repeated mentions are handled conservatively, but complex negation and context can still be misclassified.
- Evidence traces show which text triggered the heuristic; they do not prove that the text logically supports a claim.
- Reasoning-indicator categories are word-based signals and can produce false positives and false negatives.

Review flagged clauses and use scores and indicator reports as debugging signals, not as stand-alone judgments of reasoning quality.
