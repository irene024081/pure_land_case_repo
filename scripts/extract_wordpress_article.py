#!/usr/bin/env python3
"""Extract title, date, and paragraph text from a WordPress article page."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from source_entry_io import emit_records


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


class ArticleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[tuple[str, str]] = []
        self.current_tag = ""
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2", "h3", "p"}:
            self.current_tag = tag
            self.current_text = []
        if tag == "br" and self.current_tag:
            self.current_text.append("\n")

    def handle_data(self, data: str) -> None:
        if self.current_tag:
            self.current_text.append(data)

    def handle_entityref(self, name: str) -> None:
        if self.current_tag:
            self.current_text.append(html.unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if self.current_tag:
            self.current_text.append(html.unescape(f"&#{name};"))

    def handle_endtag(self, tag: str) -> None:
        if tag == self.current_tag:
            text = normalize_space("".join(self.current_text))
            if text:
                self.blocks.append((tag, text))
            self.current_tag = ""
            self.current_text = []


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


def extract_article_html(raw_html: str) -> str:
    match = re.search(r"<article\b.*?</article>", raw_html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        raise SystemExit("article element not found")
    return match.group(0)


def extract_published_date(raw_html: str) -> str:
    match = re.search(r'<meta property="article:published_time" content="([^"]+)"', raw_html)
    if match:
        return match.group(1).split("T")[0]
    match = re.search(r'<time[^>]+datetime="([^"]+)"', raw_html)
    if match:
        return match.group(1).split("T")[0]
    return ""


def date_from_url(url: str) -> str:
    parts = urlparse(url).path.strip("/").split("/")
    if len(parts) >= 3 and all(part.isdigit() for part in parts[:3]):
        year, month, day = parts[:3]
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return ""


def article_text(raw_html: str) -> tuple[str, str]:
    parser = ArticleTextParser()
    parser.feed(extract_article_html(raw_html))
    title = ""
    paragraphs: list[str] = []
    for tag, text in parser.blocks:
        if not title and tag == "h1":
            title = text
            continue
        if title and tag == "p" and text != title:
            paragraphs.append(text)
    if not title:
        raise SystemExit("article h1 title not found")
    return title, "\n\n".join(paragraphs).strip()


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return path.split("/")[-1] if path else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Local HTML path or URL.")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-title", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--language", default="en")
    parser.add_argument("--source-entry-id", default="")
    parser.add_argument("--output", default="", help="Optional .json output path.")
    args = parser.parse_args()

    raw = load_text(args.input)
    title, body = article_text(raw)
    raw_text = f"{title}\n\n{body}".strip()
    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    published_date = extract_published_date(raw) or date_from_url(args.source_url)
    slug = slug_from_url(args.source_url)

    record = {
        "source_entry_id": args.source_entry_id,
        "source_entry_key": ":".join(
            item for item in [args.source_id, "wordpress", slug, digest[:12]] if item
        ),
        "source_id": args.source_id,
        "parent_entry_id": "",
        "source_title": args.source_title,
        "volume": "",
        "section": "article",
        "entry_title": title,
        "entry_sequence": slug,
        "language": args.language,
        "raw_text": raw_text,
        "raw_text_hash": digest,
        "source_url": args.source_url,
        "locator_text": f"{args.source_title}; {title}; {published_date}; {slug}",
        "extraction_method": "WordPress article h1+p extraction",
        "extractor_name": Path(__file__).name,
        "extractor_version": "0.1.0",
        "extraction_command": " ".join(sys.argv),
        "captured_at": date.today().isoformat(),
        "access_date": date.today().isoformat(),
        "published_date": published_date,
        "boundary_status": "script_extracted",
        "boundary_confidence": "medium",
        "entry_type": "unknown",
        "ai_case_candidate_count": "",
        "linked_case_ids": "",
        "review_status": "extracted",
        "notes": "Article may include multiple perspectives or teaching notes; classify before case normalization.",
    }
    emit_records([record], args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
