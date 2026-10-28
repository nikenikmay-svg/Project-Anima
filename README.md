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

## Combined reasoning report

The `reasoning_pipeline.py` module offers `evaluate_reasoning(answer, required_points)`, which combines the existing criterion-coverage report with the reasoning-indicator checklist in one result. It keeps both component reports separate so readers can inspect what each heuristic found. It does not replace the original `evaluate_answer` function or claim semantic understanding.

Example:

```python
from reasoning_pipeline import evaluate_reasoning

report = evaluate_reasoning(
    "Evidence supports the claim. The reasoning follows because data were collected. The estimate may remain uncertain.",
    ["evidence", "reasoning", "uncertainty"],
)
print(report["criterion_evaluation"]["score"])
print(report["reasoning_indicators"]["detected_categories"])
```

## Run the checks

```bash
python -m unittest
python benchmark.py
```

The benchmark writes `benchmark-results.json`, including per-criterion evidence traces and an `error_counts` summary. Each case includes an `error_analysis` classification: correct, false positive, false negative, mixed contradiction errors, or score mismatch. These classifications compare program output with hand-written expected labels; they do not independently establish semantic truth. The cases cover repeated mentions, negation markers, contrast clauses, semicolon scope, and word-boundary matching. This is a small regression set, not a representative language dataset.

## Current limitations

- Contradiction detection relies on a small list of lexical markers.
- Clause splitting recognizes only a few common contrast transitions.
- Repeated mentions are handled conservatively, but complex negation and context can still be misclassified.
- Evidence traces show which text triggered the heuristic; they do not prove that the text logically supports a claim.
- Reasoning-indicator categories are word-based signals and can produce false positives and false negatives.

Review flagged clauses and use scores and indicator reports as debugging signals, not as stand-alone judgments of reasoning quality.
