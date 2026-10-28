# Anima Benchmarking Guide

## Run the checks locally

Use Python 3.12 or a compatible recent Python 3 release.

```bash
python -m py_compile anima.py test_anima.py benchmark.py
python -m unittest discover -v
python benchmark.py
```

The benchmark prints a JSON report and writes the same report to
`benchmark-results.json`. GitHub Actions runs these checks on pushes, pull
requests, manual dispatch, and its scheduled daily run. The workflow uploads
the report as an artifact for 30 days.

## Interpret the score

The current baseline contains a small set of hand-written cases. A passing
case means the evaluator produced the expected labels for that specific input.
It does not mean the answer is factually correct, that the system understands
meaning, or that the benchmark represents real-world language.

The evaluator is lexical: it searches for required phrases and uses simple
contradiction markers. Negation, quotations, sarcasm, context, and nuanced
claims can cause false positives or false negatives. Treat scores as debugging
signals, not as a measure of intelligence or truth.

## Safe improvement loop

1. Add a concrete example for a known failure mode.
2. Decide and document the expected label before changing the evaluator.
3. Run the regression tests and benchmark.
4. Review both improvements and regressions, not only the aggregate pass rate.
5. Propose changes on a separate branch and merge only after checks pass.
6. Keep a human in the loop for changes to evaluation logic and for claims about
   what the results mean.

## Current limitations and next priorities

- Expand the test set with realistic, adversarial, and independently reviewed
  examples.
- Improve handling of negation and scope without presenting heuristics as
  semantic understanding.
- Track results across versions so regressions are visible over time.
- Keep benchmark cases, expected labels, and known limitations reviewable.
