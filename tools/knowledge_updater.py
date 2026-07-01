#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
knowledge_updater.py - self-improving knowledge pipeline for
`networking-coach-introverts` (idea #198).

Pipeline:
  1. Fetch - query the arXiv API (cs.SI, cs.CY) over HTTPS and (optionally)
     crawl the authoritative domain sources via crawl4ai when installed.
  2. Parse - title, authors, date, URL, abstract/summary.
  3. Score - recency + domain-keyword relevance (0..1).
  4. Dedupe - skip URLs whose sha256[:16] hash already exists in the brain.
  5. Append - date-stamped, scored entries into SECOND-KNOWLEDGE-BRAIN.md.

Design notes:
  - The arXiv path uses only the standard library (urllib + xml.etree) so the
    pipeline works with no third-party dependencies. crawl4ai is optional and
    used only for the non-arXiv domain sources when present.
  - Graceful degradation: any network/parse error is logged and the run exits
    0 so the skill keeps working from the existing knowledge brain. The skill
    never blocks on a crawl failure.
  - Recommended schedule: weekly cron. See `--help`.

CLI:
  python tools/knowledge_updater.py                  # live fetch + append
  python tools/knowledge_updater.py --dry-run        # fetch, print, do not write
  python tools/knowledge_updater.py --limit 20       # cap entries per source
  python tools/knowledge_updater.py --sources arxiv  # restrict source set
  python tools/knowledge_updater.py --brain PATH     # override brain path
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime
import hashlib
import html
import logging
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

LOG = logging.getLogger("knowledge_updater")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BRAIN = os.path.normpath(os.path.join(HERE, "..", "SECOND-KNOWLEDGE-BRAIN.md"))

ARXIV_CATEGORIES = ["cs.SI", "cs.CY"]
ARXIV_API = "http://export.arxiv.org/api/query"
DOMAIN_SOURCES = [
    "https://www.sciencedirect.com/journal/social-networks",
    "https://hbr.org/",
    "https://www.quietrev.com/",
    "https://www.apa.org/",
    "https://adamgrant.net/",
]
SEARCH_QUERIES = [
    "weak ties job opportunities replication 2026",
    "introvert networking strategy evidence",
    "social capital career outcomes study",
    "authentic networking reciprocity research",
]
RELEVANCE_KEYWORDS = [w for q in SEARCH_QUERIES for w in q.lower().split()
                      if len(w) > 3]
RELEVANCE_MIN = 0.05
HTTP_TIMEOUT = 20  # seconds
POLITE_DELAY = 3.0  # seconds between arXiv page requests (arXiv etiquette)


@dataclass
class Entry:
    title: str
    authors: str
    date: str
    url: str
    abstract: str = ""
    source: str = "arxiv"
    relevance: float = 0.0

    def to_markdown(self, hash16: str) -> str:
        abstract = (self.abstract or "").strip().replace("\n", " ")[:280]
        return (
            f"\n### [{self.date}] {self.title}\n"
            f"- Authors: {self.authors or '-'}\n"
            f"- Venue/Source: {self.url}\n"
            f"- Key finding: {abstract}\n"
            f"- Relevance score: {self.relevance}\n"
            f"<!--hash:{hash16}-->\n"
        )


# ---------------------------------------------------------------------------
# Hashing + dedupe
# ---------------------------------------------------------------------------

def url_hash(url: str) -> str:
    norm = url.strip().lower()
    if norm.startswith("http://"):
        norm = "https://" + norm[len("http://"):]
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def existing_hashes(text: str) -> set:
    return set(re.findall(r"<!--hash:([0-9a-f]{16})-->", text))


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def relevance_score(title: str, abstract: str) -> float:
    blob = (title + " " + abstract).lower()
    if not blob.strip():
        return 0.0
    hits = sum(1 for kw in RELEVANCE_KEYWORDS if kw in blob)
    return round(min(1.0, hits / max(1, len(RELEVANCE_KEYWORDS))), 3)


# ---------------------------------------------------------------------------
# arXiv fetch (stdlib only)
# ---------------------------------------------------------------------------

def _http_get(url: str, timeout: int = HTTP_TIMEOUT) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "networking-coach-introverts/1.0 (knowledge_updater)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - controlled URLs
        data = resp.read()
    encoding = resp.headers.get_content_charset() or "utf-8"
    return data.decode(encoding, errors="replace")


def fetch_arxiv(categories: Sequence[str], limit: int) -> List[Entry]:
    """Query the arXiv API for recent papers in the given categories."""
    entries: List[Entry] = []
    for cat in categories:
        query = urllib.parse.urlencode({
            "search_query": f"cat:{cat}",
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        })
        url = f"{ARXIV_API}?{query}"
        try:
            body = _http_get(url)
        except Exception as exc:  # network/HTTP error -> degrade per source
            LOG.warning("arXiv fetch failed for %s: %s", cat, exc)
            continue
        entries.extend(_parse_arxiv(body, cat))
        time.sleep(POLITE_DELAY)  # be polite to the arXiv API
    return entries


def _parse_arxiv(body: str, cat: str) -> List[Entry]:
    out: List[Entry] = []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(body)
    except ET.ParseError as exc:
        LOG.warning("arXiv XML parse error for %s: %s", cat, exc)
        return out
    for el in root.findall("a:entry", ns):
        title_el = el.find("a:title", ns)
        summary_el = el.find("a:summary", ns)
        published_el = el.find("a:published", ns)
        link = ""
        for link_el in el.findall("a:link", ns):
            if link_el.attrib.get("type") == "text/html":
                link = link_el.attrib.get("href", "")
                break
        if not link:
            id_el = el.find("a:id", ns)
            link = id_el.text.strip() if id_el is not None and id_el.text else ""
        authors = ", ".join(
            (a.find("a:name", ns).text or "").strip()
            for a in el.findall("a:author", ns)
            if a.find("a:name", ns) is not None and a.find("a:name", ns).text
        )
        title = html.unescape((title_el.text or "").strip()) if title_el is not None else ""
        abstract = html.unescape((summary_el.text or "").strip()) if summary_el is not None else ""
        date = (published_el.text or "")[:10] if published_el is not None else datetime.date.today().isoformat()
        if not title or not link:
            continue
        out.append(Entry(title=title, authors=authors, date=date, url=link,
                         abstract=abstract, source="arxiv"))
    return out


# ---------------------------------------------------------------------------
# Optional crawl4ai path for domain sources
# ---------------------------------------------------------------------------

def fetch_domain_sources(sources: Sequence[str], limit: int) -> List[Entry]:
    try:
        from crawl4ai import WebCrawler  # type: ignore
    except Exception as exc:
        LOG.info("crawl4ai unavailable (%s); skipping domain-source crawl.", exc)
        return []
    out: List[Entry] = []
    try:
        crawler = WebCrawler()
        crawler.warmup()
        for src in sources:
            try:
                res = crawler.run(url=src)
                md = getattr(res, "markdown", "") or ""
                if md:
                    out.append(Entry(
                        title=f"Update from {src}", authors="-",
                        date=datetime.date.today().isoformat(), url=src,
                        abstract=md[:500], source="domain"))
                    if len(out) >= limit:
                        break
            except Exception as exc:
                LOG.warning("crawl failed for %s: %s", src, exc)
    except Exception as exc:
        LOG.warning("crawl4ai init failed: %s", exc)
    return out


# ---------------------------------------------------------------------------
# Append
# ---------------------------------------------------------------------------

def append_entries(entries: Sequence[Entry], brain_path: str,
                   dry_run: bool = False) -> int:
    if not os.path.exists(brain_path):
        LOG.error("brain not found at %s", brain_path)
        return 0
    with open(brain_path, "r", encoding="utf-8") as fh:
        text = fh.read()
    seen = existing_hashes(text)
    today = datetime.date.today().isoformat()
    added = 0
    blocks: List[str] = []
    for e in entries:
        e.relevance = relevance_score(e.title, e.abstract)
        if e.relevance < RELEVANCE_MIN:
            LOG.info("skip (relevance=%.3f): %s", e.relevance, e.title)
            continue
        h = url_hash(e.url)
        if h in seen:
            LOG.info("skip (duplicate): %s", e.url)
            continue
        seen.add(h)
        blocks.append(e.to_markdown(h))
        added += 1
    if dry_run:
        LOG.info("dry-run: would append %d entries.", added)
        for b in blocks:
            sys.stdout.write(b)
        return added
    if added:
        with open(brain_path, "a", encoding="utf-8") as fh:
            fh.write(f"\n<!-- crawl {today}: +{added} entries -->\n")
            fh.write("".join(blocks))
        # also log to the knowledge update log section if present
        _append_log_line(brain_path, today, added)
    LOG.info("appended %d new entries.", added)
    return added


def _append_log_line(brain_path: str, today: str, added: int) -> None:
    try:
        with open(brain_path, "r", encoding="utf-8") as fh:
            text = fh.read()
        marker = "## Knowledge update log"
        line = f"- **{today}** - crawl appended {added} new entries (arxiv/domain)."
        if marker in text:
            text = text.replace(marker, marker + "\n" + line, 1)
            with open(brain_path, "w", encoding="utf-8") as fh:
                fh.write(text)
    except OSError as exc:
        LOG.warning("could not update log section: %s", exc)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(sources: Sequence[str], limit: int, brain_path: str, dry_run: bool) -> int:
    entries: List[Entry] = []
    if "arxiv" in sources:
        entries.extend(fetch_arxiv(ARXIV_CATEGORIES, limit))
    if "domain" in sources:
        entries.extend(fetch_domain_sources(DOMAIN_SOURCES, limit))
    LOG.info("fetched %d candidate entries.", len(entries))
    return append_entries(entries, brain_path, dry_run=dry_run)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="networking-coach-introverts knowledge updater")
    parser.add_argument("--dry-run", action="store_true", help="fetch and print without writing")
    parser.add_argument("--limit", type=int, default=25, help="max entries per source (default 25)")
    parser.add_argument("--sources", nargs="+", default=["arxiv", "domain"],
                        choices=["arxiv", "domain"], help="source set to use")
    parser.add_argument("--brain", type=str, default=DEFAULT_BRAIN, help="path to the brain markdown")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(levelname)s] %(message)s",
    )
    LOG.info("starting knowledge crawl for networking-coach-introverts ...")
    n = run(args.sources, args.limit, args.brain, args.dry_run)
    LOG.info("done; %d entries added.", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())