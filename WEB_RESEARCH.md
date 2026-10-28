# Anima public-web research

## What it does

`web_roamer.py` provides an explicit, command-line research cycle: search the public web through DuckDuckGo HTML results, fetch selected public HTTP(S) pages, extract readable text, and store source-linked observations in `anima-memory.jsonl`. This is the first internet-research layer for Anima; it does not itself make Anima an always-running agent or a language model.

## Run it

```bash
# Search the web and inspect up to three result pages
python web_roamer.py --query "evidence based reasoning and uncertainty" --limit 3

# Fetch one specific public page
python web_roamer.py --url "https://example.com/article"

# Use a separate memory file
python web_roamer.py --query "your research question" --limit 5 --store anima-memory.jsonl

# Review saved records
python experience_store.py list --store anima-memory.jsonl
```

The tool uses only the Python standard library. Network access must be available on the machine running it. Search provider markup or access policies may change; a failed search is reported rather than silently treated as a successful crawl.

## How learning works in this first version

- Every fetched page becomes a provenance-linked `observation` record with its URL, timestamp, content hash, and extracted text.
- New records start with `outcome: observed`, `confidence: low`, and `review_status: unreviewed`.
- Repeated normalized source URLs in one research batch are fetched only once. Existing memory entries with the same normalized URL and page content hash are skipped across runs. Tracking parameters and URL fragments do not create duplicate memory entries.
- Each run creates a deterministic source inventory report with host, HTTPS status, simple domain-category indicators, extracted-text length, and duplicate URL counts. These indicators are clues for review, not source reliability scores.
- Anima preserves source text as untrusted material; it does not execute page content, obey instructions embedded in webpages, or automatically mark claims as true.
- It can retain information, but this module does not summarize semantically, reconcile claims, train a model, or alter its own code.

## Boundaries

- Only public HTTP(S) pages and standard ports are accepted. Localhost, private/non-public IPs, URL credentials, and unsupported content types are rejected. Redirect destinations are revalidated.
- Each page is capped at 1 MB, extracted text at 12,000 characters, request timeout at 12 seconds, and search results at 10 per run.
- The module performs no login, bypass of paywalls, CAPTCHA solving, form submission, posting, purchasing, or other authenticated actions.
- It does not run continuously. Run it manually or configure a separately reviewed scheduler later.
- The memory store is local runtime data. Do not commit it; do not store secrets or confidential information.
- A source URL and a stored record are provenance, not proof. Compare independent sources and review contradictions before relying on a claim.


## Scheduled exploration

The `.github/workflows/web-research.yml` workflow runs weekly (Monday at 03:00 UTC) and can also be started manually from the repository's **Actions → Anima Scheduled Web Research → Run workflow** page. Leave the optional query blank to use `research_topics.txt`, or enter a one-off research question. The workflow tests the research component first, restores the latest successful run's `anima-web-memory.jsonl` artifact when available, explores a bounded number of results, and uploads the updated memory as a 90-day artifact.

This makes exploration recurring when GitHub Actions is enabled for the repository. It is not uninterrupted browsing: it runs on a schedule, depends on network/search availability, and GitHub retains the memory artifact for a limited time. Download the `anima-web-memory` artifact from the Actions run to inspect or use the records locally. All web observations remain unreviewed; this workflow never edits source code or promotes claims to verified facts. The workflow uses GitHub's temporary workflow token only to read prior run artifacts; it does not require a personal access token.


## Source inventory report

Each successful scheduled or manual research run also uploads an `anima-research-review` artifact containing `anima-research-report.md`. It lists source links, memory record IDs, review status, extracted text size, and transparent domain/transport indicators. It is not a semantic summary, fact-check, or ranking of truth. Domain suffixes and publisher labels can be misleading; read and compare the underlying sources before relying on a claim.

To generate the report locally:

```bash
python web_research_report.py --store anima-memory.jsonl --output anima-research-report.md
python -m unittest -v test_web_roamer.py test_web_research_report.py
```


## Conservative memory cleanup preview

Each successful research run also creates an `anima-memory-cleanup-preview` artifact with a cleaned-copy JSONL file and an audit report. The preview only consolidates observation records when normalized source URL, page-body SHA-256, outcome, confidence, and review status match. Records with changed page hashes, different review statuses, missing page hashes, or non-observation types are preserved separately.

The original `anima-memory.jsonl` artifact remains unchanged. The audit report lists every retained record and collapsed duplicate ID with timestamps, original source URLs, and review status. Do not replace the authoritative memory with the preview until its audit report has been inspected. Cleanup does not verify claims or promote review status.

To create a preview locally:

```bash
python memory_cleanup.py --store anima-memory.jsonl --output anima-memory-cleaned.jsonl --report anima-memory-cleanup-report.md
python -m unittest -v test_memory_cleanup.py
```


## Research diversity and previously visited sources

For query-based expeditions, Anima inspects a wider result pool (up to 10 links) than the number it plans to fetch. It skips normalized source URLs already present in memory and duplicate URLs within the current result batch, then prefers one result per hostname before selecting a second result from a host. This is a simple diversity heuristic, not a guarantee of source independence or quality: different hostnames can share ownership, and search results can still be incomplete. Saved observations remain unreviewed.
