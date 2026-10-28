# Anima experience memory

## Purpose

`experience_store.py` provides a small, local, append-only JSON Lines store for observations, experiment outcomes, and lessons. It is a foundation for a later learning loop, not an autonomous learner by itself.

Each record includes a stable ID, timestamp, record type, source/provenance, content, declared outcome, confidence, review status, and tags. New records default to `review_status: "unreviewed"`. The store does not infer truth, promote claims to verified status, or modify evaluator code.

## Usage

Add a record:

```bash
python experience_store.py add \
  --id exp-001 \
  --type experiment \
  --source "benchmark run 12" \
  --content "Semicolon-separated clauses should be evaluated independently." \
  --outcome observed \
  --confidence medium \
  --tag clause-scope
```

List records as Markdown or JSON:

```bash
python experience_store.py list
python experience_store.py list --format json
```

The default store is `anima-memory.jsonl`; use `--store path/to/file.jsonl` to select another path. The file is runtime data and should not be committed automatically.

## Safeguards and limitations

- Records retain their stated source and status; saving is not verification.
- IDs must be unique. Invalid or malformed existing stores fail closed rather than being silently repaired.
- The first version is intended for a single writer; it does not provide cross-process locking or encryption.
- Do not store passwords, access tokens, private personal information, or confidential source material.
- The store does not fetch the web, call a language model, generate code, or run unattended background jobs.
- Human review and independent evaluation remain necessary before a lesson is treated as reliable or used to change behavior.


## Recording improvement-cycle results

To retain the outcome of a controlled experiment, pass the store path to the existing improvement-cycle runner:

```bash
python run_improvement_cycle.py baseline-results.json \
  --experiment-id exp-003 \
  --hypothesis "A focused change may fix case-17 without regressions" \
  --target-case-id case-17 \
  --memory-store anima-memory.jsonl \
  --output-dir improvement-cycle-output
```

The runner appends an `experiment` record after it writes the experiment ledger. The record contains the hypothesis, target cases, and observed command/gate summary. It is deliberately marked `unreviewed`, with low confidence and outcome `observed`, even if the regression gate passes. This records what happened in the experiment; it does not establish semantic correctness or approve a code change. The option is opt-in, so existing runs do not create a memory file unless requested.

Experiment IDs must be unique within the selected memory store. A duplicate causes an error instead of overwriting history. The experiment ledger may already have been written before the duplicate is detected; inspect the output directory and choose a new ID for a fresh run.
