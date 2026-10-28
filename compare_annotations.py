"""Compare two independent reviewer CSV files without overwriting either."""
import argparse
import csv
import json
from pathlib import Path

COMPARE_FIELDS = (
    "contextual_evidence",
    "contextual_reasoning",
    "contextual_uncertainty",
    "evidence_support",
    "inference_quality",
    "confidence",
)

def load_annotations(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "case_id" not in reader.fieldnames:
            raise ValueError(f"{path}: CSV must contain a case_id column")
        rows = {}
        for row in reader:
            case_id = (row.get("case_id") or "").strip()
            if not case_id:
                raise ValueError(f"{path}: found a row without case_id")
            if case_id in rows:
                raise ValueError(f"{path}: duplicate case_id {case_id!r}")
            rows[case_id] = row
        return rows

def compare_annotations(path_a, path_b):
    a = load_annotations(path_a)
    b = load_annotations(path_b)
    if set(a) != set(b):
        only_a = sorted(set(a) - set(b))
        only_b = sorted(set(b) - set(a))
        raise ValueError(f"case IDs differ; only in reviewer A: {only_a}; only in reviewer B: {only_b}")

    fields = {}
    disagreements = []
    for field in COMPARE_FIELDS:
        compared = 0
        agreements = 0
        missing = 0
        for case_id in sorted(a):
            value_a = (a[case_id].get(field) or "").strip()
            value_b = (b[case_id].get(field) or "").strip()
            if not value_a or not value_b:
                missing += 1
                continue
            compared += 1
            if value_a == value_b:
                agreements += 1
            else:
                disagreements.append({
                    "case_id": case_id,
                    "field": field,
                    "reviewer_a": value_a,
                    "reviewer_b": value_b,
                })
        fields[field] = {
            "compared_cases": compared,
            "agreements": agreements,
            "disagreements": compared - agreements,
            "missing_from_at_least_one_reviewer": missing,
            "raw_agreement": agreements / compared if compared else None,
        }
    return {
        "reviewer_a_file": str(path_a),
        "reviewer_b_file": str(path_b),
        "total_case_ids": len(a),
        "field_metrics": fields,
        "disagreements": disagreements,
        "limitations": [
            "Raw agreement is descriptive and is not chance-corrected inter-rater reliability.",
            "Blank values are excluded field-by-field; a high missing count can make a rate misleading.",
            "Disagreements require human discussion and adjudication; this script does not decide which reviewer is correct.",
            "Compare only independently completed copies made from the same worksheet version.",
        ],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reviewer_a_csv", help="First reviewer's completed worksheet")
    parser.add_argument("reviewer_b_csv", help="Second reviewer's completed worksheet")
    parser.add_argument("--output", help="Optional path to save the JSON report")
    args = parser.parse_args()
    report = compare_annotations(args.reviewer_a_csv, args.reviewer_b_csv)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered + "\\n", encoding="utf-8")
    print(rendered)

if __name__ == "__main__":
    main()
