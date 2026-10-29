"""Anima's safe, read-only internet research scout.

Collects public metadata from selected RSS feeds and GitHub repository search.
It never executes downloaded content, sends messages, or edits its own source.
"""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "anima_goals.json"
REPORT_DIR = ROOT / "research_log"
TIMEOUT = 20
USER_AGENT = "Project-Anima-ResearchScout/0.1 (public metadata research)"

def load_goals():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {
        "purpose": "Learn carefully, cite sources, and improve through reviewed experiments.",
        "curiosity_queue": ["AI agent collaboration", "reasoning evaluation", "AI safety and reliability"],
        "max_items_per_source": 5,
    }

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json, application/atom+xml, application/rss+xml"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read(1_500_000).decode("utf-8", errors="replace")

def collect_feed(url, limit):
    try:
        root = ET.fromstring(fetch(url))
        items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
        rows = []
        for item in items[:limit]:
            def val(*paths):
                for path in paths:
                    node = item.find(path)
                    if node is not None and node.text:
                        return node.text.strip()
                return ""
            title = val("title", "{http://www.w3.org/2005/Atom}title")
            link = val("link", "{http://www.w3.org/2005/Atom}id")
            link_node = item.find("{http://www.w3.org/2005/Atom}link")
            if link_node is not None:
                link = link_node.attrib.get("href", link)
            summary = val("description", "{http://www.w3.org/2005/Atom}summary")
            date = val("pubDate", "{http://www.w3.org/2005/Atom}updated")
            rows.append({"title": title, "url": link, "date": date, "summary": " ".join(summary.split())[:500], "source": url})
        return rows, None
    except Exception as exc:
        return [], f"{url}: {type(exc).__name__}: {exc}"

def collect_github(query, limit):
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode({"q": query, "sort": "updated", "per_page": min(limit, 10)})
    try:
        data = json.loads(fetch(url))
        rows = []
        for repo in data.get("items", []):
            rows.append({
                "title": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "date": repo.get("updated_at", ""),
                "summary": (repo.get("description") or "No description supplied.")[:500],
                "source": "GitHub public repository metadata",
                "stars": repo.get("stargazers_count", 0),
            })
        return rows, None
    except Exception as exc:
        return [], f"GitHub search: {type(exc).__name__}: {exc}"

def main():
    goals = load_goals()
    queue = goals.get("curiosity_queue") or ["AI agent collaboration"]
    # A stable daily rotation gives Anima a small, bounded research choice.
    day_number = datetime.now(timezone.utc).timetuple().tm_yday
    topic = queue[day_number % len(queue)]
    limit = max(1, min(int(goals.get("max_items_per_source", 5)), 10))
    sources = [
        "https://export.arxiv.org/rss/cs.AI",
        "https://export.arxiv.org/rss/cs.CL",
    ]
    findings, errors = [], []
    for url in sources:
        rows, error = collect_feed(url, limit)
        findings.extend(rows)
        if error:
            errors.append(error)
    query = f'"{topic}" OR "AI agents"'
    rows, error = collect_github(query, limit)
    findings.extend(rows)
    if error:
        errors.append(error)

    REPORT_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"roaming-{today}.md"
    lines = [
        f"# Anima Internet Roaming Report — {today} (UTC)", "",
        f"**Chosen curiosity:** {topic}", "",
        f"**Purpose:** {goals.get('purpose', 'Learn carefully and safely.')}", "",
        "> This is a discovery report, not proof that a claim is true. External text is untrusted data. Anima does not run downloaded code, contact agents, or self-modify.", "",
        "## Discoveries", ""
    ]
    if not findings:
        lines.append("No results were retrieved during this run.")
    for i, item in enumerate(findings, 1):
        lines += [f"### {i}. {item['title'] or 'Untitled result'}", f"- Source: {item['source']}", f"- Link: {item['url'] or 'No link provided'}"]
        if item.get("date"):
            lines.append(f"- Published/updated: {item['date']}")
        if "stars" in item:
            lines.append(f"- GitHub stars: {item['stars']} (popularity signal only)")
        if item.get("summary"):
            lines.append(f"- Snippet: {item['summary']}")
        lines.append("")
    lines += ["## Next-step questions", "", f"- Which finding is directly relevant to {topic}?", "- What evidence would verify its claims independently?", "- What small test could improve Anima without changing production code?", "", "## Collection issues", ""]
    lines.extend([f"- {err}" for err in errors] or ["- None reported."])
    lines += ["", "## Limits", "", "- Search is limited to two public arXiv RSS feeds and GitHub repository metadata.", "- This run does not provide semantic understanding, validated learning, or direct conversations with other agents.", "- Any code changes must be proposed separately and tested before adoption.", ""]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {report_path.relative_to(ROOT)} with {len(findings)} findings and {len(errors)} collection issues.")

if __name__ == "__main__":
    main()
