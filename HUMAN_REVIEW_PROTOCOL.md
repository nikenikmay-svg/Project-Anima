# Human Review Protocol for Reasoning Indicators

## Purpose

This protocol separates three different evaluation questions. The current detector only performs lexical matching; it does not perform the human review described here.

1. **Lexical detection:** Did the configured word/phrase matcher fire?
2. **Contextual interpretation:** What does the relevant phrase mean in this sentence?
3. **Reasoning quality:** Is a claim supported by premises, and does the inference follow?

Do not treat success on one question as success on another.

## Unit of review

Review one complete answer at a time, with enough surrounding context to interpret it. Keep the original answer unchanged. Record the detector output separately from human annotations.

## Annotation fields

For each case, reviewers should record:

- `case_id`: stable identifier.
- `reviewer_id`: a non-identifying reviewer code.
- `review_date`: date of annotation.
- `lexical_output_observed`: categories returned by the current detector; copy from the tool output, do not infer.
- `contextual_indicator_labels`: for each category, choose `present`, `absent`, or `ambiguous` based on the meaning in context.
- `evidence_support`: choose `supported`, `unsupported`, or `not_applicable`; cite the exact words or premises that support the judgement.
- `inference_quality`: choose `valid`, `invalid`, `insufficient_context`, or `not_applicable`; explain briefly.
- `rationale`: a concise explanation tied to the answer text.
- `confidence`: `high`, `medium`, or `low`.
- `adjudication_status`: `pending`, `agreement`, or `adjudicated`.

Never use a lexical indicator alone as proof that evidence exists, that a claim is true, or that an inference is valid.

## Review procedure

1. **Blind first pass:** Reviewers read the answer without seeing the detector's category predictions where practical.
2. **Annotate independently:** At least two reviewers label contextual indicator presence and reasoning quality independently. Do not discuss cases before submitting initial labels.
3. **Compare labels:** Calculate agreement separately for contextual indicator labels, evidence support, and inference quality. Do not collapse them into one score.
4. **Resolve disagreements:** Discuss the exact text and record an adjudicated label plus a short reason. If disagreement remains, keep the case marked ambiguous rather than forcing a label.
5. **Audit the dataset:** Preserve initial labels, adjudicated labels, reviewer rationales, and changes. Do not overwrite lexical expected labels with semantic judgments.
6. **Report limitations:** Include the number of cases, reviewer count, unresolved cases, category distribution, and agreement method. A small convenience sample is exploratory, not representative.

## Suggested annotation record

Use this JSON-shaped record as a template; replace the placeholders during actual review.

```json
{
  "case_id": "negated_evidence",
  "reviewer_id": "reviewer_1",
  "review_date": "",
  "lexical_output_observed": ["evidence"],
  "contextual_indicator_labels": {
    "evidence": "ambiguous",
    "reasoning": "absent",
    "uncertainty": "absent"
  },
  "evidence_support": "unsupported",
  "inference_quality": "insufficient_context",
  "rationale": "The answer denies evidence for the claim; the word match does not supply support.",
  "confidence": "medium",
  "adjudication_status": "pending"
}
```

The example illustrates the format only. It is not a completed human annotation for the existing review case.

## Comparing independent worksheets

After at least two reviewers independently complete copies of the same CSV template, run:

```bash
python compare_annotations.py reviewer_a.csv reviewer_b.csv --output comparison.json
```

The script checks that both files contain the same case IDs, summarizes raw agreement separately for each annotation field, reports missing values, and lists every disagreement. It does not change either input file, choose a correct label, or calculate chance-corrected inter-rater reliability. Discuss disagreements using the protocol above and preserve both original worksheets and the adjudicated record.

## Readiness checklist

Before using annotations to compare model versions, confirm:

- [ ] Reviewers used the same written instructions.
- [ ] At least two independent annotations exist per case.
- [ ] Disagreements and adjudications are preserved.
- [ ] Lexical detection metrics and human semantic judgements are reported separately.
- [ ] The evaluation set is not described as representative unless its sampling design supports that claim.
- [ ] No detector change is accepted solely because it improves agreement with a small, unreviewed set.

## Current status

The existing cases in `reasoning_indicator_review_cases.json` remain `pending_human_review`. No human review, inter-rater agreement, or semantic validation is claimed by this repository change.
