"""Render reviewer comparison data as a readable Markdown report."""
import json


def render_comparison_markdown(report):
    """Render a comparison report without changing or interpreting reviewer labels."""
    overview = report["worksheet_comparison_overview"]
    lines = [
        "# Reviewer Worksheet Comparison",
        "",
        "> Descriptive comparison only. This report does not adjudicate disagreements "
        "or establish semantic reasoning quality.",
        "",
        "## Overview",
        "",
        f"- Cases: {report['total_case_ids']}",
        f"- Annotation fields: {overview['fields_compared']}",
        f"- Case-field pairs compared (both labels present): {overview['completed_pairs_compared']}",
        f"- Agreements: {overview['agreements']}",
        f"- Disagreements requiring human review: {overview['disagreements_requiring_human_review']}",
        f"- Pairs missing at least one label: {overview['missing_pairs']}",
        f"- Raw agreement: {_percent(overview['raw_agreement'])}",
        f"- Missing cells — reviewer A: {report['missing_value_counts']['reviewer_a']}",
        f"- Missing cells — reviewer B: {report['missing_value_counts']['reviewer_b']}",
        "",
        "Raw agreement uses only case-field pairs where both reviewers supplied a label. "
        "It is not chance-corrected inter-rater reliability.",
        "",
        "## Field-by-field metrics",
        "",
        "| Field | Compared | Agreements | Disagreements | Missing pairs | Raw agreement |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for field, metric in report["field_metrics"].items():
        lines.append(
            f"| {_cell(field)} | {metric['compared_cases']} | {metric['agreements']} | "
            f"{metric['disagreements']} | {metric['missing_from_at_least_one_reviewer']} | "
            f"{_percent(metric['raw_agreement'])} |"
        )

    lines.extend(["", "## Disagreements requiring human review", ""])
    disagreements = report["disagreements"]
    if disagreements:
        lines.extend([
            "| Case | Field | Reviewer A | Reviewer B |",
            "|---|---|---|---|",
        ])
        for item in disagreements:
            lines.append(
                f"| {_cell(item['case_id'])} | {_cell(item['field'])} | "
                f"{_cell(item['reviewer_a'])} | {_cell(item['reviewer_b'])} |"
            )
    else:
        lines.append("No disagreements among nonblank paired labels.")

    lines.extend(["", "## Missing annotations", ""])
    missing = report["missing_annotations"]
    if missing:
        lines.extend([
            "| Case | Field | Reviewer A missing | Reviewer B missing |",
            "|---|---|---|---|",
        ])
        for item in missing:
            lines.append(
                f"| {_cell(item['case_id'])} | {_cell(item['field'])} | "
                f"{'Yes' if item['reviewer_a_missing'] else 'No'} | "
                f"{'Yes' if item['reviewer_b_missing'] else 'No'} |"
            )
    else:
        lines.append("No missing annotations.")

    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report["limitations"])
    fence = chr(96) * 3
    lines.extend([
        "",
        "## Machine-readable report",
        "",
        "The JSON report contains the full structured comparison data:",
        "",
        fence + "json",
        json.dumps(report, indent=2, ensure_ascii=False),
        fence,
        "",
    ])
    return "\n".join(lines)


def _percent(value):
    return "N/A" if value is None else f"{value:.1%}"


def _cell(value):
    """Escape values for safe inclusion in Markdown table cells."""
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")
