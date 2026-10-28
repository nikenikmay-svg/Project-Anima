"""No-network demo of Anima's multi-agent discussion flow.

This script uses fixed templates, not an AI model. It makes no network requests,
needs no API key, and is intended to verify the report shape on a phone.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_demo(question: str) -> dict:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must not be blank")
    if len(question) > 8_000:
        raise ValueError("question exceeds 8000 characters")

    responses = [
        {
            "agent": "Researcher",
            "role": "identify evidence needed and assumptions",
            "status": "simulated",
            "response": (
                "DEMO ONLY — I am not an AI model. For this question, first define the "
                "claim precisely, identify primary evidence and relevant comparison groups, "
                "and record source quality and limitations. Question: " + question.strip()
            ),
        },
        {
            "agent": "Skeptic",
            "role": "challenge assumptions and seek alternatives",
            "status": "simulated",
            "response": (
                "DEMO ONLY — I am not an AI model. Check for alternative explanations, "
                "selection bias, missing counterexamples, and whether the evidence could "
                "support a weaker conclusion. Question: " + question.strip()
            ),
        },
    ]
    synthesis = {
        "agent": "Synthesizer",
        "role": "compare views",
        "status": "simulated",
        "response": (
            "DEMO ONLY — no real model compared these answers. The report format can hold "
            "an evidence-focused view and a skeptical view. A real synthesis would need to "
            "inspect the actual responses, identify agreement and disagreement, and verify "
            "claims against reliable sources."
        ),
    }
    return {
        "schema_version": 1,
        "mode": "offline_template_demo",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "responses": responses,
        "synthesis": synthesis,
        "limitations": [
            "This is a fixed-template demonstration, not AI reasoning or a real agent conversation.",
            "No network requests are made and no API key is needed.",
            "No facts are researched or verified.",
            "The report is not automatically saved to Anima's long-term memory.",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", required=True, help="question to include in the demo report")
    parser.add_argument("--output", help="optional JSON report path; defaults to stdout")
    args = parser.parse_args(argv)
    try:
        rendered = json.dumps(run_demo(args.question), ensure_ascii=False, indent=2) + "\n"
    except ValueError as exc:
        parser.error(str(exc))
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
