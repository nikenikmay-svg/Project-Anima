"""Run a reproducible, reviewable benchmark experiment without changing source code.

This utility compares a saved baseline benchmark report with a candidate report
produced by an explicitly supplied command. The command is executed in a
temporary copy of the current checkout; source files in the checkout are not
modified. Only trusted local commands should be supplied.
"""
import argparse
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from benchmark_gate import compare_reports


def run_experiment(baseline_path, command, output_dir, timeout=300):
    baseline_path = Path(baseline_path).resolve()
    output_dir = Path(output_dir).resolve()
    if not baseline_path.is_file():
        raise ValueError(f"baseline report does not exist: {baseline_path}")
    if timeout <= 0:
        raise ValueError("timeout must be a positive number")
    argv = shlex.split(command)
    if not argv:
        raise ValueError("candidate command must not be empty")

    repo_root = Path(__file__).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="anima-experiment-") as temp_dir:
        worktree = Path(temp_dir) / "candidate"
        shutil.copytree(
            repo_root,
            worktree,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "baseline",
                "benchmark-results.json", "benchmark-gate-report.json",
                "improvement-proposals.json", "improvement-proposals.md",
            ),
        )
        candidate_report_path = worktree / "benchmark-results.json"
        if candidate_report_path.exists():
            candidate_report_path.unlink()

        try:
            completed = subprocess.run(
                argv,
                cwd=worktree,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
            )
            execution = {
                "command": argv,
                "exit_code": completed.returncode,
                "timed_out": False,
                "output_excerpt": completed.stdout[-12000:],
            }
        except subprocess.TimeoutExpired as exc:
            captured = exc.stdout or ""
            if isinstance(captured, bytes):
                captured = captured.decode("utf-8", errors="replace")
            execution = {
                "command": argv,
                "exit_code": None,
                "timed_out": True,
                "output_excerpt": captured[-12000:],
            }

        if not candidate_report_path.is_file() or candidate_report_path.stat().st_size == 0:
            report = {
                "experiment": "controlled benchmark experiment",
                "status": "candidate_report_missing",
                "gate_passed": False,
                "execution": execution,
                "comparison": None,
                "limitations": [
                    "The candidate command did not produce benchmark-results.json in the temporary copy.",
                    "The runner does not modify source files in the original checkout.",
                    "Only run trusted commands; this utility is not a security sandbox.",
                ],
            }
        else:
            candidate = json.loads(candidate_report_path.read_text(encoding="utf-8"))
            try:
                comparison = compare_reports(baseline, candidate)
                comparison_error = None
            except ValueError as exc:
                comparison = None
                comparison_error = str(exc)

            gate_passed = bool(
                execution["exit_code"] == 0
                and not execution["timed_out"]
                and comparison is not None
                and comparison["gate_passed"]
            )
            report = {
                "experiment": "controlled benchmark experiment",
                "status": "completed" if not execution["timed_out"] else "timed_out",
                "gate_passed": gate_passed,
                "execution": execution,
                "comparison": comparison,
                "comparison_error": comparison_error,
                "limitations": [
                    "The candidate command runs in a temporary copy, not a security sandbox; run trusted commands only.",
                    "This tool does not generate or apply code changes; the command must be supplied by a human.",
                    "Passing means agreement with the small hand-written benchmark labels, not semantic correctness.",
                    "A passing experiment is evidence for review, not automatic approval to merge.",
                ],
            }

    (output_dir / "experiment-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "experiment-report.md").write_text(render_markdown(report), encoding="utf-8")
    return report


def render_markdown(report):
    lines = [
        "# Anima controlled experiment report",
        "",
        f"- Status: **{report.get('status', 'unknown')}**",
        f"- Regression gate passed: **{report.get('gate_passed', False)}**",
        "",
    ]
    execution = report.get("execution", {})
    if execution:
        lines.extend([
            f"- Command: `{' '.join(execution.get('command', []))}`",
            f"- Exit code: {execution.get('exit_code')}",
            f"- Timed out: {execution.get('timed_out')}",
            "",
        ])
    comparison = report.get("comparison")
    if comparison:
        lines.extend([
            "## Outcome comparison",
            "",
            f"- Baseline passing cases: {comparison['baseline']['passed']}/{comparison['baseline']['total']}",
            f"- Candidate passing cases: {comparison['candidate']['passed']}/{comparison['candidate']['total']}",
            f"- Passing-case delta: {comparison['delta']['passed_cases']}",
            f"- Regressions: {len(comparison['regressions'])}",
            f"- Improvements: {len(comparison['improvements'])}",
            "",
        ])
        if comparison["regressions"]:
            lines.extend(["### Regressions", ""])
            lines.extend(f"- {item['id']}" for item in comparison["regressions"])
            lines.append("")
        if comparison["improvements"]:
            lines.extend(["### Improvements", ""])
            lines.extend(f"- {item['id']}" for item in comparison["improvements"])
            lines.append("")
    if report.get("comparison_error"):
        lines.extend(["## Comparison error", "", report["comparison_error"], ""])
    lines.extend(["## Limitations", ""])
    lines.extend(f"- {item}" for item in report.get("limitations", []))
    if execution.get("output_excerpt"):
        lines.extend(["", "## Command output (last 12,000 characters)", "", "```text", execution["output_excerpt"], "```"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", help="path to an existing benchmark-results.json baseline")
    parser.add_argument("--command", default="python benchmark.py", help="trusted command to run in the temporary candidate copy")
    parser.add_argument("--output-dir", default="experiment-output", help="directory for JSON and Markdown reports")
    parser.add_argument("--timeout", type=int, default=300, help="maximum command runtime in seconds")
    args = parser.parse_args(argv)
    try:
        report = run_experiment(args.baseline, args.command, args.output_dir, args.timeout)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Experiment status: {report['status']}")
    print(f"Regression gate passed: {report['gate_passed']}")
    print(f"Reports written to: {Path(args.output_dir).resolve()}")
    return 0 if report["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
