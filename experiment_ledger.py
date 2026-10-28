"""Create and validate a traceable ledger for Anima improvement experiments.

The ledger records hypotheses, baseline/candidate report paths, outcomes, and
review decisions. It does not infer semantic correctness or approve code changes.
"""
import argparse
import json
from pathlib import Path

STATUSES = {"proposed", "tested", "accepted", "rejected", "needs_revision"}
REQUIRED = {
    "experiment_id", "hypothesis", "target_case_ids", "baseline_report",
    "candidate_report", "test_summary", "reviewer_decision",
}


def validate_record(record):
    if not isinstance(record, dict):
        raise ValueError("ledger record must be a JSON object")
    missing = sorted(REQUIRED - set(record))
    if missing:
        raise ValueError(f"missing required fields: {missing}")
    for key in ("experiment_id", "hypothesis", "baseline_report", "candidate_report", "test_summary"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValueError(f"{key} must be a nonblank string")
    case_ids = record["target_case_ids"]
    if not isinstance(case_ids, list) or not case_ids or any(not isinstance(x, str) or not x.strip() for x in case_ids):
        raise ValueError("target_case_ids must be a non-empty list of nonblank strings")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("target_case_ids must be unique")
    decision = record["reviewer_decision"]
    if not isinstance(decision, dict):
        raise ValueError("reviewer_decision must be an object")
    if decision.get("status") not in STATUSES:
        raise ValueError(f"reviewer_decision.status must be one of {sorted(STATUSES)}")
    if not isinstance(decision.get("reviewed_by"), str) or not decision["reviewed_by"].strip():
        raise ValueError("reviewer_decision.reviewed_by must be a nonblank string")
    if not isinstance(decision.get("rationale"), str) or not decision["rationale"].strip():
        raise ValueError("reviewer_decision.rationale must be a nonblank string")
    if decision["status"] == "accepted" and decision.get("human_verified") is not True:
        raise ValueError("accepted records require reviewer_decision.human_verified=true")
    if "gate_passed" in record and not isinstance(record["gate_passed"], bool):
        raise ValueError("gate_passed must be boolean when provided")
    return record


def validate_ledger(data):
    if not isinstance(data, list):
        raise ValueError("ledger must be a JSON array")
    seen = set()
    for index, record in enumerate(data):
        try:
            validate_record(record)
        except ValueError as exc:
            raise ValueError(f"record {index}: {exc}") from exc
        experiment_id = record["experiment_id"]
        if experiment_id in seen:
            raise ValueError(f"duplicate experiment_id: {experiment_id}")
        seen.add(experiment_id)
    return data


def render_markdown(records):
    lines = [
        "# Anima experiment ledger",
        "",
        f"Recorded experiments: **{len(records)}**",
        "",
        "This ledger is a traceability aid, not proof of semantic correctness.",
        "",
    ]
    if not records:
        lines.append("No experiments recorded yet.")
    for record in records:
        decision = record["reviewer_decision"]
        lines.extend([
            f"## {record['experiment_id']}",
            "",
            f"- Status: **{decision['status']}**",
            f"- Hypothesis: {record['hypothesis']}",
            f"- Target cases: {', '.join(record['target_case_ids'])}",
            f"- Baseline report: `{record['baseline_report']}`",
            f"- Candidate report: `{record['candidate_report']}`",
            f"- Test summary: {record['test_summary']}",
            f"- Gate passed: {record.get('gate_passed', 'not recorded')}",
            f"- Reviewer: {decision['reviewed_by']}",
            f"- Rationale: {decision['rationale']}",
            f"- Human verified: {decision.get('human_verified', False)}",
            "",
        ])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON file containing an array of experiment records")
    parser.add_argument("--json-output", default="experiment-ledger-validated.json")
    parser.add_argument("--markdown-output", default="experiment-ledger.md")
    args = parser.parse_args(argv)
    try:
        records = validate_ledger(json.loads(Path(args.input).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    Path(args.json_output).write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    Path(args.markdown_output).write_text(render_markdown(records), encoding="utf-8")
    print(f"Validated {len(records)} experiment record(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
