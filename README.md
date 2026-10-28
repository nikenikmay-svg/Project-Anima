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

## Layered evaluation summary

Run `python evaluate_summary.py` to create `anima-evaluation-summary.json`. The report keeps the criterion lexical benchmark, reasoning-indicator lexical benchmark, optional human-review comparison, and reasoning-quality validation status in separate sections. To include two independently completed reviewer worksheets, run `python evaluate_summary.py --reviewer-a reviewer_a.csv --reviewer-b reviewer_b.csv`. It reports raw agreement and disagreements without adjudicating them. Without reviewer files, human review is marked `not_provided`; reasoning-quality validation is explicitly `not_established`. This report does not turn lexical scores into a semantic reasoning score.

## Contextual stress-review cases

`reasoning_indicator_stress_cases.json` adds a separate set of challenging examples involving quoted claims, negation, ambiguous connectors, uncertainty scope, unsupported assertions, multiple indicator categories, and contraction boundaries. Each case records the detector's **observed lexical matches** and remains marked `pending_human_review`. These matches document current program behavior; they are **not gold-standard labels** and do not count toward the baseline benchmark score. Run `python -m unittest` to validate the dataset schema and confirm the recorded outputs still match the current detector. Human reviewers should use `HUMAN_REVIEW_PROTOCOL.md` before making semantic judgments.

## Current limitations

- Contradiction detection relies on a small list of lexical markers.
- Clause splitting recognizes only a few common contrast transitions.
- Repeated mentions are handled conservatively, but complex negation and context can still be misclassified.
- Evidence traces show which text triggered the heuristic; they do not prove that the text logically supports a claim.
- Reasoning-indicator categories are word-based signals and can produce false positives and false negatives.

Review flagged clauses and use scores and indicator reports as debugging signals, not as stand-alone judgments of reasoning quality.

## Human review protocol

See [HUMAN_REVIEW_PROTOCOL.md](HUMAN_REVIEW_PROTOCOL.md) for a structured protocol that separates lexical detection, contextual interpretation, and reasoning quality. It defines annotation fields, independent review and adjudication steps, and a record template. The current review cases remain pending; no human validation or reviewer agreement is claimed.

## Reasoning-indicator review set

`reasoning_indicator_review_cases.json` is a separate, focused review set for negation, context-sensitive words, ambiguous connectors, and indicator words that can appear in weak or invalid arguments. It records the detector's expected lexical output, a review question, and an interpretation note. Every case is deliberately marked `pending_human_review`: these notes are prompts for future review, not independent human-validated semantic labels. The tests verify the stated lexical outputs without changing detector behavior.

## Contextual stress review set

`reasoning_indicator_stress_review_cases.json` adds 10 difficult examples involving quoted negation, past-ability uses of modal words, temporal uses of connectors, unsupported conclusions, conflicting confidence language, implicit comparisons, mixed indicator signals, and word-boundary edge cases. Their `lexical_expected_detected` values record the current detector output only; they are **not gold-standard semantic labels**. All cases remain `pending_human_review`, and the existing benchmark scores are unchanged until an independently designed evaluation is justified.

## Reasoning-indicator benchmark

Run `python reasoning_indicator_benchmark.py` to check the evidence, reasoning, and uncertainty word-indicator checklist against a separate set of hand-labelled examples. The command exits with a non-zero status if any case disagrees with its expected lexical labels, so CI can block regressions. The cases live in `reasoning_indicator_cases.json`; each case includes a `label_rationale` explaining which literal indicator words support its expected labels, or why none are expected. These rationales make the hand-written labels auditable, but they describe lexical triggers only—not semantic quality. The report carries each rationale alongside false-positive and false-negative case IDs plus per-category confusion counts, precision, recall, and F1 to make misses easier to inspect. The regression set includes positive and negative examples for each indicator category, varied lexical forms, negation, and contexts where indicator words do not imply sound reasoning. Expected labels describe whether the configured lexical signal is present, not whether the underlying statement is logically good. This benchmark measures agreement with its small expected-label set, not semantic reasoning quality. Run `python -m unittest` to include its regression checks.

### Contextual stress review cases

The review set now also includes additional stress cases for quoted negation, past-ability uses of modal words, temporal uses of connectors, unsupported conclusions, conflicting confidence language, implicit comparisons, mixed indicator signals, and word-boundary edge cases. Their `lexical_expected_detected` values record the current detector output only; they are **not gold-standard semantic labels**. All cases remain `pending_human_review`, and the existing benchmark scores are unchanged until an independently designed evaluation is justified.

## Reasoning-quality review cases

`reasoning_quality_review_cases.json` is a separate set of 10 prompts for future human evaluation of evidence support and inference quality. Cases cover causal attribution, correlation versus causation, overgeneralization, confounding, unsupported motive attribution, uncertainty calibration, quotation attribution, scope mismatch, and insufficient context. Each case supplies the prompt, a claim to assess, context, and a review question; it deliberately contains **no pre-filled correctness or reasoning-quality label**. All cases remain `pending_human_review`. This is a review instrument, not an automated evaluator or a validated gold-standard dataset. Use `HUMAN_REVIEW_PROTOCOL.md` and independent reviewers before drawing conclusions.

## Claim-audit prototype and improvement gates

Run `python reasoning_audit_benchmark.py` to create `reasoning-audit-report.json`. The prototype highlights selected lexical patterns that deserve human review, including causal wording, broad generalizations, motive attribution, and strong certainty language. It shows the exact matched phrase and why it was flagged. It does **not** determine whether a claim is true, whether evidence supports it, or whether an inference is valid; those fields remain `not_assessed`.

The 10 examples in `reasoning_audit_cases.json` are a small, designed rule-smoke-test set. The pass rate means only that the current rules match the expected trigger lists in these examples. It is not a semantic accuracy score and is not a representative benchmark. CI runs the smoke tests, unit tests, existing lexical benchmarks, claim audit smoke tests, and report generation. A change that breaks the explicit expected behavior fails CI; human review remains necessary before treating any rule as an improvement.

## Structured arguments and review worksheet

`structured_arguments.py` validates the shape of an explicitly supplied argument object with an ID, one or more premise strings, and a conclusion string. Example:

```python
from structured_arguments import validate_argument

report = validate_argument({
    "id": "example-1",
    "premises": ["All mammals are animals.", "Whales are mammals."],
    "conclusion": "Whales are animals.",
})
print(report)
```

This validates only the data structure. The result deliberately reports `logical_validity: "not_assessed"`; it does not prove that premises are true or that a conclusion follows. `test_structured_arguments.py` covers valid structure, missing fields, empty values, malformed inputs, and duplicate IDs. `argument_review_worksheet.csv` is a blank worksheet for human reviewers to independently record premises, conclusions, evidence support, missing context, alternative explanations, inference quality, confidence, and notes. No reviewer labels are pre-filled. Run `python -m unittest discover -v` to run the regression suite.


## Evidence mapping and counterexample review

`argument_review.py` builds a structured review report from an argument and optional reviewer-supplied evidence items, unstated assumptions, and counterexamples. Evidence entries are attached to premise positions so reviewers can inspect which premise each item is meant to support. Missing entries mean only that no item was supplied to this report. The tool does not verify sources, decide whether evidence entails a premise, discover assumptions, or prove a conclusion. Support and inference quality remain explicitly `not_assessed`, and each report remains `pending_human_review`.

Example:

```python
from argument_review import review_argument

report = review_argument(
    {
        "id": "example-1",
        "premises": ["All mammals are animals.", "Whales are mammals."],
        "conclusion": "Whales are animals.",
    },
    evidence_by_premise={
        "1": ["Reviewer-supplied source A, section 2"],
        "2": ["Reviewer-supplied source B, paragraph 4"],
    },
    unstated_assumptions=[],
    counterexamples=[],
)
print(report["premise_evidence"])
print(report["review_prompts"])
```

`argument_review_cases.json` contains three prompts for future human review: correlation versus causation, alternative explanations, and universal claims from small samples. Their status is `pending_human_review`; no quality labels are pre-filled. The helper records only caller-provided evidence, assumptions, and counterexamples. It does not automatically generate or validate them. Run `python -m unittest discover -v` for regression tests.


## Compact human-review summary

`argument_review_summary.py` provides `summarize_review(report)`, which counts only information already supplied in an `argument_review.py` report: premise count, evidence items attached to premises, assumptions listed by a reviewer, and counterexamples listed by a reviewer. These counts are inventory, not quality scores. The summary always keeps conclusion evidence status and inference quality at `not_assessed`, and preserves the need for human review.

Example:

```python
from argument_review import review_argument
from argument_review_summary import summarize_review

review = review_argument(
    {
        "id": "example-1",
        "premises": ["Premise one.", "Premise two."],
        "conclusion": "Conclusion.",
    },
    evidence_by_premise={"1": ["Reviewer-supplied source A"]},
)
print(summarize_review(review))
```

The summary does not verify sources, infer unstated assumptions, generate counterexamples, assess evidence quality, or decide whether a conclusion follows. Its tests cover count accuracy, malformed entries, and the invariant that inference quality remains `not_assessed`.


## JSON command-line review reports

Use `argument_review_cli.py` to turn a JSON input file into a shareable JSON review report containing both the review inventory and its compact summary. The CLI accepts an input file with an `argument` object and optional `evidence_by_premise`, `unstated_assumptions`, and `counterexamples` fields.

Run the included example:

```bash
python argument_review_cli.py argument_review_example.json --output argument-review-report.json
```

Omit `--output` to print the report to standard output. Invalid JSON, unreadable files, and missing required input fields produce a clear error and a non-zero exit code. The example includes explicit placeholder evidence, not real citations; replace it with source details before any real review.

The output uses schema version `1.0` and includes a limitation notice. It remains an inventory of caller-supplied material: the CLI does not fetch or verify sources, infer missing premises, generate counterexamples, or judge whether the conclusion follows. Conclusion evidence status and inference quality remain `not_assessed`. Tests cover JSON document shape, output-file writing, malformed JSON, and required fields.


## Markdown review report export

The argument-review CLI supports both JSON and readable Markdown output. JSON remains the default and is useful for programmatic processing. To create a Markdown report:

```bash
python argument_review_cli.py argument_review_example.json --format markdown --output argument-review-report.md
```

Omit `--output` to print to the terminal. The Markdown view shows the argument ID, premises, supplied evidence items, assumptions, counterexamples, inventory counts, and limitation notice. It preserves `not_assessed` states rather than presenting counts as proof of quality. This is a presentation/export feature only; it does not change the review logic or validate sources and inference. Tests cover key sections, empty lists, malformed documents, and CLI file output.


## Evidence input validation

The evidence review layer now emits `input_warnings` when the evidence map has the wrong type, a key does not match a 1-based premise position, a premise's evidence value is not a list, or an evidence item is empty/non-text. Invalid entries are ignored rather than silently treated as valid evidence. The Markdown export includes these warnings so they remain visible in a human-readable report. Warnings identify input-shape problems only; they do not assess evidence quality or logical validity. Run `python -m unittest discover -v` to test the cases.


## Strict input mode

For automation, the CLI offers `--strict-input`. It still writes the normal JSON or Markdown report, but exits with status `3` if the review contains input-shape warnings. It exits `0` when no such warnings are present, and `2` for input/read/parse errors. This lets scripts stop or flag a review when evidence keys or item shapes need correction without losing the diagnostic report.

```bash
python argument_review_cli.py argument_review_example.json --strict-input --output review.json
```

The strict mode checks input formatting only. It does not mean that the evidence is trustworthy or that the argument is valid. Tests cover both warning and warning-free strict-mode runs.

## Export a paired review bundle

To create both machine-readable JSON and readable Markdown from the same review input, use bundle format with an output prefix:

```bash
python argument_review_cli.py argument_review_example.json --format bundle --output review-bundle
```

This writes `review-bundle.json`, `review-bundle.md`, and `review-bundle.manifest.json`. The manifest records SHA-256 hashes for the JSON and Markdown file contents so consumers can detect accidental changes and verify the bundle's files match the manifest. Hashes establish file integrity only, not source trustworthiness or reasoning quality. Bundle mode requires an output prefix so two formats are not mixed on standard output. Both reports preserve the same supplied review data and limitations; bundle export does not add semantic validation. Regression tests verify the files, hashes, and missing-prefix behavior. An end-to-end regression test also exports a bundle, verifies it successfully, alters the Markdown file, and confirms verification then fails.

Strict-input mode also works with bundle export: the CLI writes both diagnostic reports and then returns exit code `3` when input-shape warnings are present. Consumers should treat that code as a review-needed signal, not as a semantic verdict.

To verify that the paired files still match their manifest, run:

```bash
python verify_review_bundle.py review-bundle
```

The verifier exits `0` when both file hashes match and `1` when the manifest is missing, malformed, or a report differs. It checks integrity only; it does not authenticate the report's author, verify cited sources, or assess reasoning quality. Run `python -m unittest discover -v` to test valid bundles, altered files, malformed manifests, and missing manifests. GitHub Actions also builds and verifies this example bundle and uploads the JSON, Markdown, and manifest as the `anima-sample-review-bundle` artifact for 30 days. The example evidence is placeholder text, not a real citation.


The reviewer comparison tool now checks that both CSV worksheets contain every required annotation column before comparing values. Missing columns are reported explicitly rather than silently appearing as missing annotations. Blank cells are still allowed for unfinished worksheets and are reported separately. This is a format check, not a judgement about reviewer correctness.


The reviewer worksheet comparator now validates nonblank annotation values against the review protocol's allowed labels: present/absent/ambiguous, the documented evidence-support and inference-quality labels, and high/medium/low confidence. Blank values remain permitted for incomplete reviews. Invalid labels stop comparison with a clear error; this guards data consistency but does not validate the substance of any judgement.


The worksheet comparator also rejects duplicate or blank CSV column names. Duplicate headers can cause a CSV parser to overwrite one column silently, so these malformed files are stopped before any agreement metrics are calculated. This is structural validation only.


The reviewer comparison JSON now includes a `missing_annotations` list identifying the case, field, and which reviewer left it blank. This makes follow-up work actionable while preserving the existing field-level missing counts. Blank entries remain missing data, not agreement or disagreement.


The comparison report also summarizes blank annotation values by reviewer and overall, alongside the total number of possible annotation cells. This makes worksheet completeness easier to assess, but completeness counts are not quality scores and do not change agreement calculations.

The paired-review report now includes a `worksheet_comparison_overview` with aggregate counts for completed case-field pairs, agreements, disagreements requiring human review, and pairs missing at least one reviewer label. Its overall raw-agreement rate is calculated only from pairs where both reviewers supplied a value; it is `null` when no pairs can be compared. Read it alongside the per-field metrics and missing-value counts: missing pairs are not agreements, and a high rate based on very few completed pairs can be misleading. This overview is descriptive only; it is not chance-corrected inter-rater reliability, an adjudication result, or evidence of semantic reasoning quality.

## Markdown reviewer comparison report

The reviewer worksheet comparator can export a human-readable Markdown report alongside its default JSON output. Run:

```bash
python compare_annotations.py reviewer_a.csv reviewer_b.csv --format markdown --output reviewer-comparison.md
```

The report contains the aggregate overview, per-field metrics, each disagreement requiring human review, missing annotations with reviewer identity, and the limitations. The JSON output remains the default and is unchanged in purpose. Markdown is a presentation format only: it does not adjudicate labels, verify sources, or establish semantic reasoning quality. Raw agreement is calculated only from nonblank paired labels and is not chance-corrected reliability.

## Review-guided regression feedback (human approval required)

Use `review_feedback_template.json` as a starting point to record a failure that a human reviewer has checked. Each record must include the exact answer and requested criteria, the expected score and contradiction labels, a status, an explicit `human_verified` boolean, and a rationale. Set `status` to `approved` and `human_verified` to `true` only after independently checking the expected labels. Pending or rejected records are not exported.

Validate the feedback and export approved candidates to a separate file:

```bash
python review_feedback.py review_feedback_template.json --output proposed-regression-cases.json
```

The exporter checks required fields, unique IDs, score bounds, label consistency, and duplicate IDs against `benchmark_cases.json`. It does **not** edit the baseline benchmark or evaluator code. Review the generated candidates, then propose any baseline changes in a separate pull request and run the full test suite. CI remains the regression gate; a passing test suite only demonstrates consistency with the curated expected labels, not semantic correctness. The feedback status and `human_verified` flag are workflow declarations, not cryptographic proof of who reviewed the data.


## Saved-report benchmark regression gate

Use `benchmark_gate.py` to compare a baseline report with a candidate report generated from a different evaluator revision:

```bash
python benchmark.py
cp benchmark-results.json baseline-results.json
# After changing the evaluator, run the benchmark again:
python benchmark.py
python benchmark_gate.py baseline-results.json benchmark-results.json --output benchmark-gate-report.json
```

The gate requires both reports to contain exactly the same unique case IDs and boolean pass/fail outcomes. It lists cases that regressed from pass to fail, improved from fail to pass, and any changed `actual_score` values. It exits with status 1 if any previously passing case regresses; malformed reports or changed case sets are rejected. Keep the baseline report from the earlier revision before regenerating the candidate report.

This is a deterministic comparison tool, not an automatic improvement system. A pass means agreement with the project's hand-written expected labels, not semantic correctness. The gate does not itself check out two revisions, generate both reports, or replace human review.


## Human-reviewable improvement proposal queue

Run `python improvement_proposal.py benchmark-results.json` after generating a benchmark report. The tool creates `improvement-proposals.json` and `improvement-proposals.md`, listing failed cases, their recorded error types, score differences, and suggested investigation steps. The pull-request benchmark workflow generates and uploads this queue as the `anima-improvement-proposals` artifact so a reviewer can inspect it.

The queue is intentionally advisory: it does not write patches, change evaluator behavior, or approve its own suggestions. Reviewers should reproduce a failing case, verify the expected label, implement one small change, add a regression test, and let the baseline-versus-candidate gate evaluate the proposal. If no failures appear, the queue says so while reminding readers that matching a small hand-written benchmark is not proof of semantic reasoning.


## Controlled benchmark experiments

The `controlled_experiment.py` utility runs a trusted candidate command in a temporary copy of the repository, compares the resulting `benchmark-results.json` with a saved baseline, and writes JSON and Markdown reports. Example:

```bash
python benchmark.py
cp benchmark-results.json baseline-results.json
python controlled_experiment.py baseline-results.json --command "python benchmark.py" --output-dir experiment-output
```

The candidate command must create `benchmark-results.json` in the temporary copy. The original checkout is not edited by the runner. The experiment exits successfully only if the command exits successfully and the comparison gate passes. If the candidate report is missing or the case sets differ, the experiment fails closed.

**Safety and scope:** run trusted commands only. The temporary directory is not a security sandbox. The runner does not invent code changes, apply patches, merge pull requests, or validate semantic truth. Treat reports as evidence for a human reviewer, not automatic approval.


## Traceable experiment ledger

Use `experiment_ledger_template.json` as a starting point for recording a proposed improvement. Fill in the target case IDs, hypothesis, baseline and candidate report paths, test summary, and reviewer decision, then validate and render it:

```bash
python experiment_ledger.py experiment_ledger_template.json
```

The validator writes a validated JSON ledger and a Markdown report. Experiment IDs and target case IDs must be unique. A record marked `accepted` requires `human_verified: true`, a reviewer identity, and a rationale. These fields record a declared review decision; they do not cryptographically authenticate a reviewer or prove that a change is correct. Keep proposals pending until the actual reports and tests have been inspected.
