"""Compare research records and draft human-reviewable evaluator test ideas.

Only compares words in titles/snippets. It does not read full papers or infer truth.
No suggested case is added to the benchmark automatically.
"""
from datetime import datetime, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "research_log"
SIGNALS = {
    "evidence and verification": ["evidence", "verify", "verification", "validation", "reproducible", "measurement"],
    "reasoning and evaluation": ["reasoning", "evaluation", "benchmark", "inference", "performance"],
    "agents and autonomy": ["agent", "agents", "autonomous", "orchestration", "tool"],
    "safety and reliability": ["safety", "reliability", "risk", "failure", "robustness", "uncertainty"],
    "human oversight": ["human", "oversight", "review", "direction", "accountability"],
    "memory and context": ["memory", "retrieval", "knowledge", "context", "persistent"],
}

def latest_report():
    reports = sorted(LOG_DIR.glob("roaming-*.md"))
    return reports[-1] if reports else None

def parse_items(text):
    items, current = [], None
    for line in text.splitlines():
        if line.startswith("### "):
            if current:
                items.append(current)
            current = {"title": line[4:].strip(), "url": "", "source": "", "snippet": ""}
        elif current:
            for label, key in (("- Link:", "url"), ("- Source:", "source"), ("- Snippet:", "snippet")):
                if line.startswith(label):
                    current[key] = line[len(label):].strip()
    if current:
        items.append(current)
    return items

def terms_for(item):
    text = (item["title"] + " " + item["snippet"]).lower()
    return {topic: [term for term in terms if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text)] for topic, terms in SIGNALS.items()}

def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output = LOG_DIR / f"comparison-{today}.md"
    report = latest_report()
    lines = [f"# Anima Source Comparison — {today} (UTC)", ""]
    if not report:
        lines += ["No research report found. Run the roaming workflow first.", ""]
        output.write_text("\n".join(lines), encoding="utf-8")
        return
    items = parse_items(report.read_text(encoding="utf-8"))
    annotated = [(item, terms_for(item)) for item in items]
    lines += [
        f"**Input report:** {report.name}",
        f"**Items compared:** {len(items)}",
        "",
        "**Method:** compare visible titles and short snippets using fixed keyword lists. Similar terms are leads for human review, not proof that sources agree.",
        "",
        "## Topic overlap across sources", ""
    ]
    topic_counts = {}
    for topic in SIGNALS:
        matches = [(item, found[topic]) for item, found in annotated if found[topic]]
        topic_counts[topic] = matches
        if matches:
            lines.append(f"### {topic}")
            for item, words in matches:
                link = item["url"] or "No article URL captured"
                lines.append(f"- [{item['title']}]({link}) — terms: {', '.join(words)}")
            lines.append("")
    lines += ["## Comparison questions", "",
        "- Do sources discuss the same problem, or merely use similar terminology?",
        "- Are their datasets, tasks, baselines, and evaluation measures comparable?",
        "- What counterexample would show that a claimed improvement is only keyword overlap?",
        "- What limitations or contradictory findings appear in the full original sources?",
        "", "## Candidate evaluator tests (drafts only)", "",
        "Review these ideas manually. Do not add them to benchmark_cases.json until expected labels are justified independently."
    ]
    candidates = [
        ("quoted_claim", 'The article quotes someone saying "evidence is irrelevant," then rejects that statement.', "Check whether quoted negation is incorrectly treated as the author's own position."),
        ("indicator_without_support", "The answer says, " + '"Evidence proves the claim because I say so."' , "Check whether indicator words are mistaken for a supported argument."),
        ("uncertainty_scope", "The estimate may be unreliable, while the measurement procedure is documented.", "Check whether uncertainty language contaminates a separate supported criterion."),
        ("same_word_different_meaning", "The agent will review the model; the reviewer will assess the agent.", "Check whether repeated terms are treated as repeated evidence of the same claim."),
    ]
    for case_id, answer, rationale in candidates:
        lines += [f"### {case_id}", f"- Example: {answer}", f"- Review question: {rationale}", "- Expected labels: **not assigned**; a human must define them after reviewing intended behavior.", ""]
    lines += ["## Limits", "",
        "- This script does not fetch or verify full articles.",
        "- Keyword overlap does not establish agreement, causality, quality, or truth.",
        "- Test ideas are not benchmark cases and do not alter the evaluator.",
        ""]
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)} comparing {len(items)} research items.")

if __name__ == "__main__":
    main()
