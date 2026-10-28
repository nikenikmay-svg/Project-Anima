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
- Identical page content at the same canonical URL is skipped on later runs.
- Anima preserves source text as untrusted material; it does not execute page content, obey instructions embedded in webpages, or automatically mark claims as true.
- It can retain information, but this module does not summarize semantically, reconcile claims, train a model, or alter its own code.

## Boundaries

- Only public HTTP(S) pages and standard ports are accepted. Localhost, private/non-public IPs, URL credentials, and unsupported content types are rejected. Redirect destinations are revalidated.
- Each page is capped at 1 MB, extracted text at 12,000 characters, request timeout at 12 seconds, and search results at 10 per run.
- The module performs no login, bypass of paywalls, CAPTCHA solving, form submission, posting, purchasing, or other authenticated actions.
- It does not run continuously. Run it manually or configure a separately reviewed scheduler later.
- The memory store is local runtime data. Do not commit it; do not store secrets or confidential information.
- A source URL and a stored record are provenance, not proof. Compare independent sources and review contradictions before relying on a claim.
