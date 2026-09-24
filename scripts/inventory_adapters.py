#!/usr/bin/env python3
"""Inventory adapters: discover source items (articles/entries) for catalogs.

Four adapter families, one interface: each returns a list of discovered items
with a stable source-facing key, title, and URL. Discovery only lists what a
source contains; it grants no processing or publication rights, and it never
fetches article bodies.

Families:
    static_headings     single static page: link list or text-heading TOC
    wordpress_archive   WordPress category/archive pagination
    paginated_html      custom paginated HTML list (legacy sites)
    pdf_toc             TOC pages of an issue-based PDF periodical

Fetch functions are injected so tests run offline against saved fixtures.
"""

from __future__ import annotations

import html as html_module
import re
from html.parser import HTMLParser
from urllib.parse import urljoin

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import extract_dazhouxian_entries as dazhouxian  # noqa: E402


def make_item(key: str, title: str, url: str, notes: str = "", published_date: str = "") -> dict:
    return {
        "source_item_key": key,
        "title": title,
        "canonical_url": url,
        "published_date": published_date,
        "notes": notes,
    }


# --- CSS-lite selector matching -------------------------------------------------


def parse_selector(selector: str) -> dict:
    """Parse a minimal selector: tag, tag.class, .class, #id, tag#id."""
    match = re.fullmatch(r"(?:(?P<tag>[a-zA-Z][a-zA-Z0-9]*)?)(?:\.(?P<cls>[\w-]+))?(?:#(?P<id>[\w-]+))?", selector.strip())
    if not match or not match.group(0):
        raise ValueError(f"unsupported selector: {selector}")
    return {"tag": match.group("tag"), "cls": match.group("cls"), "id": match.group("id")}


def element_matches(tag: str, attrs: dict[str, str], selector: dict) -> bool:
    if selector["tag"] and tag != selector["tag"]:
        return False
    if selector["cls"] and selector["cls"] not in attrs.get("class", "").split():
        return False
    if selector["id"] and attrs.get("id") != selector["id"]:
        return False
    return True


class LinkCollector(HTMLParser):
    """Collect <a> elements, optionally scoped to a container selector."""

    def __init__(self, link_selector: str, container_selector: str = "") -> None:
        super().__init__(convert_charrefs=True)
        self.target = parse_selector(link_selector)
        self.container = parse_selector(container_selector) if container_selector else None
        self.container_depth: int | None = None
        self.stack: list[str] = []
        self.links: list[dict] = []
        self._current: dict | None = None

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {k: v or "" for k, v in attrs_list}
        if self.container is not None and self.container_depth is None and element_matches(tag, attrs, self.container):
            self.container_depth = len(self.stack)
        self.stack.append(tag)
        if element_matches(tag, attrs, self.target) and (
            self.container is None or self.container_depth is not None
        ):
            self._current = {"href": attrs.get("href", ""), "title_attr": attrs.get("title", ""), "text": []}

    def handle_endtag(self, tag: str) -> None:
        if self._current is not None and tag == "a":
            self._current["text"] = html_module.unescape("".join(self._current["text"])).strip()
            self.links.append(self._current)
            self._current = None
        if self.stack:
            self.stack.pop()
        if self.container_depth is not None and len(self.stack) <= self.container_depth:
            self.container_depth = None

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["text"].append(data)


def collect_links(html_text: str, link_selector: str, container_selector: str = "") -> list[dict]:
    parser = LinkCollector(link_selector, container_selector)
    parser.feed(html_text)
    parser.close()
    return parser.links


def items_from_links(html_text: str, config: dict, page_url: str) -> list[dict]:
    """Shared link-to-item mapping used by the HTML families."""
    links = collect_links(html_text, config.get("link_selector", "a"), config.get("container_selector", ""))
    include = re.compile(config["include_pattern"]) if config.get("include_pattern") else None
    exclude = re.compile(config["exclude_pattern"]) if config.get("exclude_pattern") else None
    key_pattern = re.compile(config["key_pattern"]) if config.get("key_pattern") else None
    items: list[dict] = []
    seen: set[str] = set()
    for link in links:
        href = link["href"]
        title = link["title_attr"] if config.get("title_from") == "title_attr" else link["text"]
        if not href or not title:
            continue
        if include and not include.search(href):
            continue
        if exclude and exclude.search(href):
            continue
        if config.get("key_from", "href") == "text":
            key = title
        else:
            if key_pattern is None:
                key = href
            else:
                match = key_pattern.search(href)
                if not match:
                    continue
                key = match.groupdict().get("key") or match.group(1)
        key = (config.get("key_prefix", "") + key).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        url = urljoin(page_url, href)
        if config.get("url_strip_pattern"):
            url = re.sub(config["url_strip_pattern"], "", url)
        items.append(make_item(key, title, url))
    return items


# --- Family 1: static_headings ---------------------------------------------------


def discover_static_headings(html_text: str, config: dict, page_url: str) -> list[dict]:
    """Single static page: either a link list or a text-heading TOC."""
    mode = config.get("mode", "links")
    if mode == "links":
        return items_from_links(html_text, config, page_url)
    if mode == "headings":
        # Turn block-level tags into line breaks so text headings stay lines.
        blocked = re.sub(r"(?i)</p>|</div>|</li>|<br[^>]*>", "\n", html_text)
        text = dazhouxian.normalize_html(blocked)
        section = dazhouxian.slice_section(
            text, config.get("start_heading") or None, config.get("end_heading") or None
        )
        entries = dazhouxian.extract_entries(section)
        base = page_url.rstrip("/")
        return [
            make_item(f"{config.get('key_prefix', 'entry')}:{title}", title, base)
            for title, _raw in entries
        ]
    raise ValueError(f"unknown static_headings mode: {mode}")


# --- Family 2: wordpress_archive -------------------------------------------------


def discover_wordpress_archive(fetch, config: dict) -> list[dict]:
    """Walk WordPress archive pages until a page yields no new items."""
    template = config["archive_url_template"]
    max_pages = int(config.get("max_pages", "50"))
    wp_config = dict(config)
    wp_config.setdefault("container_selector", "article")
    wp_config.setdefault("link_selector", "a")
    items: list[dict] = []
    seen: set[str] = set()
    for page in range(1, max_pages + 1):
        url = template.format(page=page)
        html_text = fetch(url)
        if html_text is None:
            break
        page_items = items_from_links(html_text, wp_config, url)
        fresh = [item for item in page_items if item["source_item_key"] not in seen]
        if not fresh:
            break
        for item in fresh:
            seen.add(item["source_item_key"])
            items.append(item)
    return items


# --- Family 3: paginated_html ----------------------------------------------------


def discover_paginated_html(fetch, config: dict) -> list[dict]:
    """Walk a custom paginated list until an empty page or max_pages."""
    template = config["list_url_template"]
    start_page = int(config.get("start_page", "1"))
    max_pages = int(config.get("max_pages", "100"))
    items: list[dict] = []
    seen: set[str] = set()
    for page in range(start_page, max_pages + 1):
        url = template.format(page=page)
        html_text = fetch(url)
        if html_text is None:
            break
        page_items = items_from_links(html_text, config, url)
        fresh = [item for item in page_items if item["source_item_key"] not in seen]
        if not fresh:
            break
        for item in fresh:
            seen.add(item["source_item_key"])
            items.append(item)
    return items


# --- Family 4: pdf_toc -----------------------------------------------------------

DEFAULT_TOC_PATTERN = r"^(?P<title>.+?)\s*\.{3,}\s*(?:(?P<author>[^/\d]{1,30}?)\s*/\s*)?(?P<page>\d{1,4})\s*$"


def discover_pdf_toc(pdf_path: str | Path, config: dict) -> list[dict]:
    """Parse the TOC pages of an issue-based PDF periodical.

    Only lines that fully match the entry pattern become items; wrapped
    continuation fragments are skipped and counted in the notes. Titles and
    page numbers are metadata-level discovery output; body text is not read.
    """
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise SystemExit("pypdf is required for pdf_toc: python3 -m pip install pypdf") from exc

    page_range = config["toc_pages"].split("-")
    start, end = int(page_range[0]), int(page_range[-1])
    pattern = re.compile(config.get("entry_pattern", DEFAULT_TOC_PATTERN))
    issue = config.get("issue", "issue")
    pdf_url = config.get("pdf_url", "")
    reader = PdfReader(str(pdf_path))
    items: list[dict] = []
    skipped = 0
    for page_number in range(start - 1, min(end, len(reader.pages))):
        text = reader.pages[page_number].extract_text() or ""
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            match = pattern.match(line)
            if not match:
                skipped += 1
                continue
            title = match.group("title").strip()
            page = match.group("page")
            author = (match.groupdict().get("author") or "").strip()
            notes = f"作者：{author}" if author else ""
            items.append(make_item(
                f"{issue}:p{page}:{len(items) + 1:04d}",
                title,
                f"{pdf_url}#page={page}" if pdf_url else "",
                notes=notes,
            ))
    print(f"pdf_toc: {len(items)} entries parsed; {skipped} non-entry TOC lines skipped", file=sys.stderr)
    return items


FAMILIES = {
    "static_headings": "page",
    "wordpress_archive": "walk",
    "paginated_html": "walk",
    "pdf_toc": "pdf",
}
