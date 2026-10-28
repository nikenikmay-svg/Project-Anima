"""Run Anima's controlled experiment and record the result in its ledger.

This orchestrator does not generate or apply source changes. It runs only the
trusted command supplied by the user, records the result, and leaves the review
decision pending for a human.
"""
import argparse
import json
from pathlib import Path

from controlled_experiment import run_experiment
from experiment_ledger import validate_ledger, render_markdown


def resolve_candidate_inputs(queue, hypothesis=None, target_case_ids=None):
    """Resolve explicit inputs or default to the highest-ranked queue candidate."""
    target_case_ids = list(target_case_ids or [])
    if queue is not None:
        if not isinstance(queue, dict) or not isinstance(queue.get("candidates"), list):
            raise ValueError("candidate queue must be an object containing a candidates list")
        if not queue["candidates"]:
            raise ValueError("candidate queue is empty; no experiment candidate is available")
        first = queue["candidates"][0]
        if not isinstance(first, dict):
            raise ValueError("top candidate must be an object")
        case_id = first.get("case_id")
        candidate_hypothesis = first.get("hypothesis")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("top candidate must contain a nonblank case_id")
        if not isinstance(candidate_hypothesis, str) or not candidate_hypothesis.strip():
            raise ValueError("top candidate must contain a nonblank hypothesis")
        if not target_case_ids:
            target_case_ids = [case_id]
        if not hypothesis:
            hypothesis = candidate_hypothesis
    if not hypothesis or not hypothesis.strip():
        raise ValueError("provide --hypothesis or a valid --candidate-queue")
    if not target_case_ids:
        raise ValueError("provide at least one --target-case-id or a valid --candidate-queue")
    return hypothesis, target_case_ids


def run_cycle(baseline, experiment_id, hypothesis, target_case_ids, command, output_dir, timeout=300):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = run_experiment(baseline, command, output_dir / "experiment", timeout=timeout)
    gate_passed = report.get("gate_passed") is True
    decision_status = "tested" if gate_passed else "needs_revision"
    rationale = (
        "Experiment ran and the regression gate passed; awaiting human review before acceptance."
        if gate_passed
        else "Experiment did not satisfy the regression gate; inspect the report and revise before review."
    )
    record = {
        "experiment_id": experiment_id,
        "hypothesis": hypothesis,
        "target_case_ids": target_case_ids,
        "baseline_report": str(Path(baseline).resolve()),
        "candidate_report": str((output_dir / "experiment" / "experiment-report.json").resolve()),
        "test_summary": (
            f"Command exit code: {report.get('execution', {}).get('exit_code')}; "
            f"timed out: {report.get('execution', {}).get('timed_out')}; "
            f"gate passed: {gate_passed}; status: {report.get('status')}"
        ),
        "gate_passed": gate_passed,
        "reviewer_decision": {
            "status": decision_status,
            "reviewed_by": "pending human review",
            "rationale": rationale,
            "human_verified": False,
        },
    }
    ledger = validate_ledger([record])
    json_path = output_dir / "experiment-ledger.json"
    markdown_path = output_dir / "experiment-ledger.md"
    json_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(ledger), encoding="utf-8")
    return {
        "gate_passed": gate_passed,
        "decision_status": decision_status,
        "experiment_report": str(output_dir / "experiment" / "experiment-report.json"),
        "ledger_json": str(json_path),
        "ledger_markdown": str(markdown_path),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", help="saved baseline benchmark-results.json")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--hypothesis", help="experiment hypothesis; defaults to the top candidate when --candidate-queue is used")
    parser.add_argument("--target-case-id", action="append", dest="target_case_ids",
                        help="target case ID; repeat for multiple cases")
    parser.add_argument("--candidate-queue",
                        help="prioritized-candidates.json; uses its first-ranked candidate when hypothesis/target IDs are omitted")
    parser.add_argument("--command", default="python benchmark.py",
                        help="trusted candidate command to run in a temporary repository copy")
    parser.add_argument("--output-dir", default="improvement-cycle-output")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args(argv)
    try:
        queue = (
            json.loads(Path(args.candidate_queue).read_text(encoding="utf-8"))
            if args.candidate_queue else None
        )
        hypothesis, target_case_ids = resolve_candidate_inputs(
            queue, args.hypothesis, args.target_case_ids
        )
        result = run_cycle(
            args.baseline, args.experiment_id, hypothesis,
            target_case_ids, args.command, args.output_dir, args.timeout,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
