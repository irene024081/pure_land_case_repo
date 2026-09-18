#!/usr/bin/env python3
"""Extract a PLB-SEA Squarespace article into a source_entry record."""

from __future__ import annotations

import argparse
import ast
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

from source_entry_io import emit_records
from urllib.parse import urlparse


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


class TextBlockParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[str] = []
        self.stack: list[str] = []
        self.current: list[str] = []
        self.capture_tag = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(tag)
        if tag in {"h1", "h2", "h3", "p", "li"}:
            self.capture_tag = tag
            self.current = []
        if tag == "br" and self.capture_tag:
            self.current.append("\n")

    def handle_data(self, data: str) -> None:
        if self.capture_tag:
            self.current.append(data)

    def handle_entityref(self, name: str) -> None:
        if self.capture_tag:
            self.current.append(html.unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if self.capture_tag:
            self.current.append(html.unescape(f"&#{name};"))

    def handle_endtag(self, tag: str) -> None:
        if tag == self.capture_tag:
            text = normalize_space("".join(self.current))
            if text:
                self.blocks.append(text)
            self.capture_tag = ""
            self.current = []
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()


def load_text(input_ref: str) -> str:
    if input_ref.startswith(("http://", "https://")):
        request = urllib.request.Request(input_ref, headers={"User-Agent": DEFAULT_USER_AGENT})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
        return data.decode("utf-8", errors="replace")
    return Path(input_ref).read_text(encoding="utf-8", errors="replace")


def normalize_space(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*", "\n", text)
    return text.strip()


def extract_meta(raw_html: str, name: str) -> str:
    patterns = [
        rf'<meta itemprop="{re.escape(name)}" content="([^"]+)"',
        rf'<meta property="{re.escape(name)}" content="([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, raw_html, flags=re.IGNORECASE)
        if match:
            return html.unescape(match.group(1)).split("T")[0]
    return ""


def extract_article_html(raw_html: str) -> str:
    start = raw_html.find('<div class="article" id="article">')
    if start == -1:
        raise SystemExit("PLB-SEA article container not found")
    end = raw_html.find('<div style="text-align:center', start)
    if end == -1:
        raise SystemExit("PLB-SEA article end marker not found")
    return raw_html[start:end]


def extract_js_html(raw_html: str, variable_name: str) -> str:
    match = re.search(rf"var {re.escape(variable_name)}='(.*?)';", raw_html, flags=re.DOTALL)
    if not match:
        return ""
    return ast.literal_eval("'" + match.group(1) + "'")


def html_to_text(fragment: str) -> tuple[str, str]:
    subtitle_match = re.search(r'<p class="subtitle">(.+?)</p>', fragment, flags=re.DOTALL)
    title = normalize_space(re.sub(r"<[^>]+>", "", subtitle_match.group(1))) if subtitle_match else ""
    parser = TextBlockParser()
    parser.feed(fragment)
    blocks = [block for block in parser.blocks if block != title]
    return title, "\n\n".join(blocks).strip()


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return path.split("/")[-1] if path else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Local HTML path or URL.")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-title", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--language", default="zh-Hans")
    parser.add_argument("--source-entry-id", default="")
    parser.add_argument("--section", default="念佛真实案例 Accounts")
    parser.add_argument("--output", default="", help="Optional .json output path.")
    args = parser.parse_args()

    raw = load_text(args.input)
    article_html = extract_article_html(raw)
    title, body = html_to_text(article_html)
    if not title:
        title_match = re.search(r"<title>(.*?)</title>", raw, flags=re.DOTALL)
        title = normalize_space(title_match.group(1)) if title_match else ""
    if not title or not body:
        raise SystemExit("article title or body not found")

    raw_text = f"{title}\n\n{body}".strip()
    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    alt_languages = []
    for lang, variable_name in [("en", "enHTML"), ("id", "idHTML")]:
        if extract_js_html(raw, variable_name):
            alt_languages.append(lang)

    slug = slug_from_url(args.source_url)
    published_date = extract_meta(raw, "datePublished")
    modified_date = extract_meta(raw, "dateModified")

    record = {
        "source_entry_id": args.source_entry_id,
        "source_entry_key": ":".join(
            item for item in [args.source_id, "plb-sea", slug, digest[:12]] if item
        ),
        "source_id": args.source_id,
        "parent_entry_id": "",
        "source_title": args.source_title,
        "volume": "",
        "section": args.section,
        "entry_title": title,
        "entry_sequence": slug,
        "language": args.language,
        "raw_text": raw_text,
        "raw_text_hash": digest,
        "source_url": args.source_url,
        "locator_text": f"{args.source_title}; {args.section}; {title}; {slug}",
        "extraction_method": "PLB-SEA Squarespace #article extraction",
        "extractor_name": Path(__file__).name,
        "extractor_version": "0.1.0",
        "extraction_command": " ".join(sys.argv),
        "captured_at": date.today().isoformat(),
        "access_date": date.today().isoformat(),
        "published_date": published_date,
        "modified_date": modified_date,
        "boundary_status": "script_extracted",
        "boundary_confidence": "medium",
        "entry_type": "mixed",
        "ai_case_candidate_count": "",
        "linked_case_ids": "",
        "review_status": "extracted",
        "notes": (
            "Article may contain first-person account, teacher note, and embedded alternate "
            f"language versions: {', '.join(alt_languages) if alt_languages else 'none'}."
        ),
    }
    emit_records([record], args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
