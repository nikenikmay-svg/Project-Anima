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

Benchmark cases are stored separately in `benchmark_cases.json` and labelled by category (for example, negation, phrase matching, clause scope, repeated mentions, and input edges). The JSON report includes `category_metrics` with per-category case totals, pass rates, error counts, and case IDs grouped by error type, making failures easy to locate. Regression tests enforce unique case IDs and a controlled set of category labels, so typos or accidental duplicates are caught early. `benchmark.py` loads this dataset and writes `benchmark-results.json`, including per-criterion evidence traces, an `error_counts` summary, `criterion_error_counts`, and `criterion_metrics`. Per-criterion confusion counts report true positives, false positives, false negatives, and true negatives only across cases that request that criterion. The metrics report precision, recall, F1, and specificity; a metric is `null` when its denominator is zero. Each case also includes an `error_analysis` classification: correct, false positive, false negative, mixed contradiction errors, or score mismatch. These counts compare program output with hand-written expected labels; they do not independently establish semantic truth. The cases cover repeated mentions, negation markers, contrast clauses, semicolon scope, word-boundary matching, multiword criteria, duplicate criteria, and an empty criteria list. This expanded hand-written regression set is still small and is not a representative language dataset.

## Current limitations

- Contradiction detection relies on a small list of lexical markers.
- Clause splitting recognizes only a few common contrast transitions.
- Repeated mentions are handled conservatively, but complex negation and context can still be misclassified.
- Evidence traces show which text triggered the heuristic; they do not prove that the text logically supports a claim.
- Reasoning-indicator categories are word-based signals and can produce false positives and false negatives.

Review flagged clauses and use scores and indicator reports as debugging signals, not as stand-alone judgments of reasoning quality.


## Reasoning-indicator benchmark

Run `python reasoning_indicator_benchmark.py` to check the evidence, reasoning, and uncertainty word-indicator checklist against a separate set of hand-labelled examples. The cases live in `reasoning_indicator_cases.json`; the report lists false-positive and false-negative case IDs plus per-category confusion counts, precision, recall, and F1 to make misses easier to inspect. The regression set includes positive and negative examples for each indicator category, varied lexical forms, negation, and contexts where indicator words do not imply sound reasoning. Expected labels describe whether the configured lexical signal is present, not whether the underlying statement is logically good. This benchmark measures agreement with its small expected-label set, not semantic reasoning quality. Run `python -m unittest` to include its regression checks.
