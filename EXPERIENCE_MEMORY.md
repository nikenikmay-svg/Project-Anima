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
