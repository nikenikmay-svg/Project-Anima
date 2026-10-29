"""Experimental evidence-grounding checklist for Anima's AQE tests.

This is a transparent, rule-based diagnostic over hand-authored claim labels,
not a general-purpose fact checker. It does not call an external model, execute
peer output, or modify production evaluator behavior.
"""
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "research_log"

CASES = [
    {
        "id": "E1_causality",
        "evidence": "The intervention group improved from baseline. There was no control group and participants self-selected.",
        "candidates": {
            "grounded": {"supported": ["improved from baseline", "no control group", "self-selected"], "unsupported": []},
            "overclaim": {"supported": ["improved from baseline"], "unsupported": ["proves the intervention caused improvement"]}
        },
        "preferred": "grounded",
        "rationale": "Improvement is observed, but the design does not establish causality."
    },
    {
        "id": "E2_sample_scope",
        "evidence": "A voluntary online poll of 40 respondents found 28 preferred option A.",
        "candidates": {
            "grounded": {"supported": ["40 respondents", "28 preferred option A", "voluntary poll"], "unsupported": []},
            "overgeneralized": {"supported": ["28 preferred option A"], "unsupported": ["represents the entire population"]}
        },
        "preferred": "grounded",
        "rationale": "The poll supports a result about its respondents, not the entire population."
    },
    {
        "id": "E3_missing_information",
        "evidence": "No current policy document or official source was supplied.",
        "candidates": {
            "cautious": {"supported": ["no current policy document supplied"], "unsupported": []},
            "fabricated": {"supported": [], "unsupported": ["current policy is definitely X"]}
        },
        "preferred": "cautious",
        "rationale": "No supplied evidence supports a specific current policy."
    },
    {
        "id": "E4_mixed_evidence",
        "evidence": "In a small observational sample, sleep duration was associated with self-reported mood. The study did not test causality.",
        "candidates": {
            "grounded": {"supported": ["association in observational sample", "self-reported mood", "causality not tested"], "unsupported": []},
            "causal_claim": {"supported": ["association in observational sample"], "unsupported": ["more sleep caused improved mood"]}
        },
        "preferred": "grounded",
        "rationale": "An association in an observational study does not by itself show cause and effect."
    }
]

def score(candidate):
    supported = candidate["supported"]
    unsupported = candidate["unsupported"]
    total = len(supported) + len(unsupported)
    # A transparent checklist score: supported evidence items help; unsupported
    # assertions incur a stronger penalty. This is not a probability of truth.
    raw = (len(supported) - 2 * len(unsupported)) / total if total else 0.0
    return max(-1.0, min(1.0, raw))

def main():
    LOG_DIR.mkdir(exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = LOG_DIR / f"aqe-evidence-grounding-{date}.md"
    lines = [
        f"# AQE Evidence-Grounding Diagnostic — {date} (UTC)", "",
        "**Status:** Experimental structured checklist run; not a general-purpose fact checker.",
        "**Method:** Human-authored supported/unsupported claim labels with an explicit penalty for unsupported claims.",
        "**Caution:** The labels are pre-authored for synthetic examples. This does not independently determine whether claims are true.", "",
        "## Results", ""
    ]
    mismatches = 0
    for case in CASES:
        ranked = sorted(
            ((name, score(candidate)) for name, candidate in case["candidates"].items()),
            key=lambda row: row[1], reverse=True
        )
        winner = ranked[0][0]
        expected = case["preferred"]
        mismatch = winner != expected
        mismatches += int(mismatch)
        lines += [
            f"### {case['id']}", f"- Evidence: {case['evidence']}",
            f"- Expected preferred candidate: {expected}",
            f"- Rationale: {case['rationale']}"
        ]
        for name, candidate in case["candidates"].items():
            lines += [
                f"- Candidate {name} score: {score(candidate):.3f}",
                f"  - Supported checklist items: {len(candidate['supported'])}",
                f"  - Unsupported-claim flags: {len(candidate['unsupported'])}"
            ]
        lines += [
            f"- Top-ranked candidate: {winner}",
            f"- Agreement with hand-authored preference: {'NO — diagnostic failure' if mismatch else 'yes'}", ""
        ]
    lines += [
        "## Summary", "",
        f"- Cases: {len(CASES)}",
        f"- Ranking mismatches: {mismatches}",
        "- This score is a transparent checklist, not a calibrated confidence or truth probability.",
        "- The claim labels were supplied by the benchmark author; the script does not extract claims from arbitrary prose.",
        "- It does not replace source verification, entailment review, or human evaluation.",
        "- Production AQE code was not changed.", "",
        "## Next validation", "",
        "Expand the benchmark with independently reviewed examples, adversarial cases, and blinded human ratings. Keep unsupported-claim penalties experimental until tested on held-out data.", ""
    ]
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)}; cases={len(CASES)}; ranking_mismatches={mismatches}")

if __name__ == "__main__":
    main()
