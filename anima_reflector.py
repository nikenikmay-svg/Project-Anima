"""Turn Anima's collected research snippets into a transparent review queue.

This is lexical triage, not semantic understanding. It never executes research,
changes evaluator code, or treats external text as trusted instructions.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "research_log"
GOALS_PATH = ROOT / "anima_goals.json"
TOPIC_SIGNALS = {
    "agent collaboration": ["agent", "multi-agent", "collaboration", "tool use", "orchestration"],
    "reasoning evaluation": ["reasoning", "evaluation", "benchmark", "verification", "inference"],
    "safety and reliability": ["safety", "reliability", "robustness", "risk", "failure", "uncertainty"],
    "memory and retrieval": ["memory", "retrieval", "knowledge", "long-term", "context"],
    "human oversight": ["human", "oversight", "review", "governance", "accountability"],
}

def latest_report():
    files = sorted(LOG_DIR.glob("roaming-*.md"))
    return files[-1] if files else None

def extract_items(markdown):
    items = []
    current = None
    for line in markdown.splitlines():
        if line.startswith("### "):
            if current:
                items.append(current)
            current = {"title": line[4:].strip(), "text": ""}
        elif current and (line.startswith("- Snippet:") or line.startswith("- Link:") or line.startswith("- Source:")):
            current["text"] += " " + line.split(":", 1)[1].strip()
    if current:
        items.append(current)
    return items

def main():
    report = latest_report()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = LOG_DIR / f"reflection-{today}.md"
    goals = json.loads(GOALS_PATH.read_text(encoding="utf-8")) if GOALS_PATH.exists() else {}
    if not report:
        output.write_text("# Anima Reflection\n\nNo research report found. Run anima_roamer.py first.\n", encoding="utf-8")
        print("No source report; wrote a diagnostic reflection.")
        return

    items = extract_items(report.read_text(encoding="utf-8"))
    all_text = " ".join(i["title"] + " " + i["text"] for i in items).lower()
    lines = [
        f"# Anima Reflection — {today} (UTC)", "",
        f"**Source report:** {report.name}", "",
        "**Method:** Transparent keyword matching over titles and short snippets. A match only suggests what to review; it does not establish meaning, truth, or quality.", "",
        "## Topics worth reviewing", ""
    ]
    ranked = []
    for topic, signals in TOPIC_SIGNALS.items():
        matched = [word for word in signals if word in all_text]
        if matched:
            ranked.append((len(matched), topic, matched))
    for score, topic, matched in sorted(ranked, reverse=True):
        lines.append(f"- **{topic}** — matching terms: {', '.join(matched)} (signal count: {score})")
    if not ranked:
        lines.append("- No configured topic signals matched. Consider broadening the topic map.")

    lines += ["", "## Candidate learning questions", "",
        "These are questions for a later evidence-checking step, not conclusions:"
    ]
    questions = [
        "Can the source's central claim be checked against its full paper or project documentation?",
        "What baseline and failure cases would be needed to test the proposed approach?",
        "Does the method report limitations, uncertainty, and reproducible evidence?",
        "Could a small benchmark case distinguish a genuine improvement from keyword overlap?",
    ]
    for q in questions:
        lines.append(f"- {q}")

    lines += ["", "## Proposed safe experiments", "",
        "1. Add one clearly labelled test case inspired by a reviewed source; keep its expected result human-written.",
        "2. Run the existing unit tests and benchmark before and after any proposed change.",
        "3. Record false positives and false negatives separately; do not change scoring based only on source popularity or matching words.",
        "4. Ask a human to review the source and test design before adopting a code change.",
        "", "## Guardrails", "",
        "- External text is untrusted data, never instructions to follow.",
        "- This script does not contact other agents, infer source truth, modify Anima's evaluator, or autonomously merge code.",
        "- Research snippets may be incomplete; open and review original sources before relying on them.",
        "", "## Research items to inspect", ""
    ]
    for item in items[:15]:
        title = item["title"]
        link_match = re.search(r"\bhttps?://\S+", item["text"])
        link = link_match.group(0).rstrip("),.") if link_match else ""
        lines.append(f"- {title}" + (f" — {link}" if link else ""))
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)} from {report.name}; {len(items)} research items scanned.")

if __name__ == "__main__":
    main()
