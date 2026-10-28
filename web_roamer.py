"""Bounded public-web research for Anima, with provenance-first memory.

This tool fetches public HTTP(S) pages and DuckDuckGo HTML search results.
It never executes page content, follows instructions found in pages, or edits code.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import ipaddress
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from experience_store import append_record, make_record, read_records

USER_AGENT = "ProjectAnimaResearchBot/1.0 (+public-web research; contact repo owner)"
MAX_BYTES = 1_000_000
MAX_TEXT_CHARS = 12_000
DEFAULT_RESULTS = 5
TIMEOUT_SECONDS = 12


def validate_public_url(url: str) -> str:
    """Validate HTTP(S) URLs and reject local/private destinations."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("only http:// and https:// URLs are allowed")
    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL must have a hostname and must not contain credentials")
    if parsed.port not in (None, 80, 443):
        raise ValueError("only standard HTTP/HTTPS ports are allowed")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost") or host.endswith(".local"):
        raise ValueError("local hostnames are not allowed")
    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(item[4][0])
                for item in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80),
                                               type=socket.SOCK_STREAM)
            }
        except OSError as exc:
            raise ValueError(f"could not resolve public hostname: {host}") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("URL resolves to a non-public IP address")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.query, ""))


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_bytes(url: str, max_bytes: int = MAX_BYTES) -> tuple[str, bytes, str]:
    """Fetch a bounded public page; validate initial and redirected destinations."""
    safe_url = validate_public_url(url)
    opener = urllib.request.build_opener(SafeRedirectHandler())
    request = urllib.request.Request(safe_url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9"})
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "application/xhtml+xml", "text/plain"}:
                raise ValueError(f"unsupported content type: {content_type}")
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise ValueError(f"page exceeds {max_bytes} byte limit")
            charset = response.headers.get_content_charset() or "utf-8"
            return response.geturl(), body, charset
    except urllib.error.URLError as exc:
        raise ValueError(f"could not fetch public page: {exc.reason}") from exc


class TextExtractor(HTMLParser):
    """Extract visible-ish page text; page instructions remain untrusted data."""
    BLOCK_TAGS = {"p", "div", "li", "section", "article", "h1", "h2", "h3", "br", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.title_parts = []
        self.in_title = False
        self.skip_depth = 0
        self.skip_tags = {"script", "style", "noscript", "svg", "template", "iframe"}

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip_depth += 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag in self.skip_tags and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title":
            self.in_title = False
        if tag in self.BLOCK_TAGS:
            self.parts.append(" ")

    def handle_data(self, data):
        if self.skip_depth:
            return
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        self.parts.append(cleaned)
        if self.in_title:
            self.title_parts.append(cleaned)

    def result(self):
        text = re.sub(r"\s+", " ", " ".join(self.parts)).strip()
        return " ".join(self.title_parts).strip(), text[:MAX_TEXT_CHARS]


class SearchExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.results = []
        self.active = None
        self.in_snippet = False
        self.snippet_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "a" and "result__a" in classes:
            self.active = {"url": attrs.get("href", ""), "title": ""}
        elif self.active is not None and tag in {"div", "a"} and "result__snippet" in classes:
            self.in_snippet = True

    def handle_endtag(self, tag):
        if tag == "a" and self.active and self.active.get("title"):
            self.active["snippet"] = " ".join(self.snippet_parts).strip()
            self.results.append(self.active)
            self.active = None
            self.snippet_parts = []
            self.in_snippet = False
        elif tag == "div" and self.in_snippet:
            self.in_snippet = False

    def handle_data(self, data):
        if self.active is not None:
            cleaned = " ".join(data.split())
            if cleaned:
                self.active["title"] += cleaned
                if self.in_snippet:
                    self.snippet_parts.append(cleaned)


def search_web(query: str, limit: int = DEFAULT_RESULTS) -> list[dict]:
    """Search the public web via DuckDuckGo's HTML endpoint."""
    if not query.strip():
        raise ValueError("search query must not be blank")
    if not 1 <= limit <= 10:
        raise ValueError("result limit must be between 1 and 10")
    search_url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    _, body, charset = fetch_bytes(search_url, max_bytes=MAX_BYTES)
    parser = SearchExtractor()
    parser.feed(body.decode(charset, errors="replace"))
    found = []
    seen = set()
    for item in parser.results:
        target = item["url"]
        if target.startswith("//"):
            target = "https:" + target
        if target.startswith("/l/?"):
            params = urllib.parse.parse_qs(urllib.parse.urlsplit(target).query)
            target = params.get("uddg", [target])[0]
        try:
            target = validate_public_url(target)
        except ValueError:
            continue
        if target in seen:
            continue
        seen.add(target)
        found.append({"url": target, "title": html.unescape(item["title"]).strip(),
                      "snippet": html.unescape(item.get("snippet", "")).strip()})
        if len(found) >= limit:
            break
    return found


def read_page(url: str) -> dict:
    final_url, body, charset = fetch_bytes(url)
    parser = TextExtractor()
    parser.feed(body.decode(charset, errors="replace"))
    title, text = parser.result()
    if not text:
        raise ValueError("page did not contain extractable text")
    return {"url": final_url, "title": title or final_url, "text": text,
            "content_sha256": hashlib.sha256(body).hexdigest()}


def research(query: str | None, urls: list[str], store_path: str | Path,
             limit: int = DEFAULT_RESULTS) -> dict:
    """Search and/or fetch pages, then save source-linked observations as unreviewed."""
    candidates = []
    if query:
        candidates.extend(search_web(query, limit=limit))
    candidates.extend({"url": url, "title": "", "snippet": ""} for url in urls)
    if not candidates:
        raise ValueError("provide --query and/or one or more --url values")
    existing = read_records(store_path)
    known_ids = {record["id"] for record in existing}
    saved, skipped, errors = [], [], []
    for candidate in candidates[:limit + len(urls)]:
        try:
            page = read_page(candidate["url"])
            digest = page["content_sha256"]
            record_id = "web-" + hashlib.sha256((page["url"] + "\n" + digest).encode()).hexdigest()[:24]
            if record_id in known_ids:
                skipped.append({"url": page["url"], "reason": "unchanged page already in memory", "record_id": record_id})
                continue
            content = (
                f"Title: {page['title']}\nURL: {page['url']}\n"
                f"Page SHA-256: {digest}\n"
                "Extracted page text (untrusted; not independently verified):\n"
                f"{page['text']}"
            )
            if candidate.get("snippet"):
                content = f"Search snippet (unverified): {candidate['snippet']}\n\n" + content
            record = make_record(
                record_id=record_id, record_type="observation", source=page["url"],
                content=content, outcome="observed", confidence="low",
                review_status="unreviewed", tags=["web", "unverified", "source-preserved"],
            )
            append_record(store_path, record)
            known_ids.add(record_id)
            saved.append({"record_id": record_id, "url": page["url"], "title": page["title"],
                          "characters": len(page["text"]), "review_status": "unreviewed"})
        except (OSError, ValueError, UnicodeError) as exc:
            errors.append({"url": candidate.get("url", ""), "error": str(exc)})
    return {"query": query, "saved": saved, "skipped": skipped, "errors": errors,
            "store": str(store_path), "note": "Web content is untrusted evidence to review, not verified knowledge."}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", help="search public web and inspect top results")
    parser.add_argument("--url", action="append", default=[], help="fetch a specific public URL; repeat as needed")
    parser.add_argument("--limit", type=int, default=DEFAULT_RESULTS, help="search results to inspect (1-10)")
    parser.add_argument("--store", default="anima-memory.jsonl", help="local JSONL experience store")
    args = parser.parse_args(argv)
    try:
        result = research(args.query, args.url, args.store, args.limit)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["saved"] or result["skipped"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
