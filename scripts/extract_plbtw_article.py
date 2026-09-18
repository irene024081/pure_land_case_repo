#!/usr/bin/env python3
"""Extract article text from a PLBTW story article page.

This creates a source-entry candidate from one structured article URL. It does
not decide which parts are case facts and which parts are commentary.
"""

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
from urllib.parse import parse_qs, urlparse

from source_entry_io import emit_records


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


class TextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.blocks: list[tuple[str, str]] = []
        self.current_tag = ""
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(tag)
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
        if self.stack:
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
    text = text.replace("\u3000", " ")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*", "\n", text)
    return text.strip()


def extract_in_right(raw_html: str) -> str:
    start = raw_html.rfind('<div id="in_right">')
    if start < 0:
        raise SystemExit("content container not found: div#in_right")

    candidates = [
        raw_html.find('<div id="page">', start),
        raw_html.find('<div id="share">', start),
        raw_html.find("</div><!--content", start),
    ]
    stops = [item for item in candidates if item >= 0]
    end = min(stops) if stops else len(raw_html)
    return raw_html[start:end]


def article_blocks(raw_html: str) -> list[tuple[str, str]]:
    collector = TextCollector()
    collector.feed(extract_in_right(raw_html))
    blocks = collector.blocks
    while blocks and blocks[0][0] == "h2" and blocks[0][1] in {"念佛感應事蹟", "念佛感应事蹟"}:
        blocks = blocks[1:]
    return blocks


def article_text(blocks: list[tuple[str, str]]) -> tuple[str, str]:
    title = ""
    body: list[str] = []
    for tag, text in blocks:
        if not title and tag in {"h1", "h2", "h3"}:
            title = text
            continue
        if title and tag == "p":
            body.append(text)
    if not title:
        raise SystemExit("article title not found")
    return title, "\n\n".join(body).strip()


def story_id_from_url(url: str) -> str:
    query = parse_qs(urlparse(url).query)
    return query.get("id", [""])[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Local HTML path or URL.")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-title", default="PLBTW 念佛感應事蹟")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--language", default="zh-Hant")
    parser.add_argument("--source-entry-id", default="")
    parser.add_argument("--output", default="", help="Optional .json output path.")
    args = parser.parse_args()

    raw = load_text(args.input)
    title, body = article_text(article_blocks(raw))
    raw_text = f"{title}\n\n{body}".strip()
    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    story_id = story_id_from_url(args.source_url)
    source_entry_key = ":".join(
        item for item in [args.source_id, "story_1_in", story_id, title, digest[:12]] if item
    )

    record = {
        "source_entry_id": args.source_entry_id,
        "source_entry_key": source_entry_key,
        "source_id": args.source_id,
        "parent_entry_id": "",
        "source_title": args.source_title,
        "volume": "",
        "section": "念佛往生(新)",
        "entry_title": title,
        "entry_sequence": story_id,
        "language": args.language,
        "raw_text": raw_text,
        "raw_text_hash": digest,
        "source_url": args.source_url,
        "locator_text": f"{args.source_title}; 念佛往生(新); {title}; id={story_id}",
        "extraction_method": "PLBTW article div#in_right h2+p extraction",
        "extractor_name": Path(__file__).name,
        "extractor_version": "0.1.0",
        "extraction_command": " ".join(sys.argv),
        "captured_at": date.today().isoformat(),
        "access_date": date.today().isoformat(),
        "boundary_status": "script_extracted",
        "boundary_confidence": "high",
        "entry_type": "unknown",
        "ai_case_candidate_count": "",
        "linked_case_ids": "",
        "review_status": "extracted",
        "notes": "Article may include case narrative and commentary; classify before case normalization.",
    }
    emit_records([record], args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
