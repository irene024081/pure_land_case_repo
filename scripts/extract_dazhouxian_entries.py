#!/usr/bin/env python3
"""Extract repeated-title entries from a Dazhouxian CBETA-style HTML page.

This script creates source-entry candidates. It does not decide whether an
entry is a case, whether facts are true, or how a case should be tagged.
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
from pathlib import Path

from source_entry_io import emit_records


PUNCTUATION = set("。？！；：，、（）()《》〈〉「」『』[]【】,.!?;:")


def load_text(input_ref: str) -> str:
    if input_ref.startswith(("http://", "https://")):
        with urllib.request.urlopen(input_ref, timeout=30) as response:
            data = response.read()
        return data.decode("utf-8", errors="replace")
    return Path(input_ref).read_text(encoding="utf-8", errors="replace")


def normalize_html(raw: str) -> str:
    text = raw.replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def find_heading(text: str, heading: str, start_at: int = 0) -> re.Match[str] | None:
    pattern = re.compile(rf"(?m)^[\s\u3000]*{re.escape(heading)}[\s\u3000]*$")
    return pattern.search(text, start_at)


def looks_like_entry_heading(lines: list[str], index: int) -> bool:
    title = lines[index].strip()
    if not title:
        return False
    if title.startswith(("No.", "净土圣贤录卷", "论曰")):
        return False
    if len(title) > 24:
        return False
    if any(ch in PUNCTUATION for ch in title):
        return False

    next_line = ""
    for line in lines[index + 1 : index + 5]:
        stripped = line.strip()
        if stripped:
            next_line = stripped
            break

    if not next_line:
        return False

    return next_line.startswith(title + "。") or next_line.startswith(title + "者")


def slice_section(text: str, start_heading: str | None, end_heading: str | None) -> str:
    start = 0
    if start_heading:
        match = find_heading(text, start_heading)
        if not match:
            raise SystemExit(f"start heading not found: {start_heading}")
        start = match.end()

    end = len(text)
    if end_heading:
        match = find_heading(text, end_heading, start)
        if not match:
            raise SystemExit(f"end heading not found: {end_heading}")
        end = match.start()

    return text[start:end].strip()


def extract_entries(section: str) -> list[tuple[str, str]]:
    lines = section.splitlines()
    headings = [i for i in range(len(lines)) if looks_like_entry_heading(lines, i)]
    entries: list[tuple[str, str]] = []

    for offset, line_index in enumerate(headings):
        next_index = headings[offset + 1] if offset + 1 < len(headings) else len(lines)
        title = lines[line_index].strip()
        raw_text = "\n".join(lines[line_index:next_index]).strip()
        if raw_text:
            entries.append((title, raw_text))

    return entries


def make_entry_id(prefix: str, sequence: int) -> str:
    return f"{prefix}{sequence:06d}"


def make_entry_key(source_id: str, volume: str, section: str, title: str, digest: str) -> str:
    parts = [source_id, volume, section, title, digest[:12]]
    return ":".join(part for part in parts if part)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Local HTML path or URL.")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-title", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--language", default="zh-Hans")
    parser.add_argument("--volume", default="")
    parser.add_argument("--section", default="")
    parser.add_argument("--start-heading")
    parser.add_argument("--end-heading")
    parser.add_argument("--entry-id-prefix", default="ENT")
    parser.add_argument("--start-sequence", type=int, default=1)
    parser.add_argument("--output", default="", help="Optional .jsonl output path.")
    args = parser.parse_args()

    raw = load_text(args.input)
    text = normalize_html(raw)
    section_text = slice_section(text, args.start_heading, args.end_heading)
    entries = extract_entries(section_text)

    records = []
    for index, (title, raw_text) in enumerate(entries, start=args.start_sequence):
        digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
        record = {
            "source_entry_id": make_entry_id(args.entry_id_prefix, index),
            "source_entry_key": make_entry_key(
                args.source_id,
                args.volume,
                args.section or args.start_heading or "",
                title,
                digest,
            ),
            "source_id": args.source_id,
            "parent_entry_id": "",
            "source_title": args.source_title,
            "volume": args.volume,
            "section": args.section or args.start_heading or "",
            "entry_title": title,
            "entry_sequence": index,
            "language": args.language,
            "raw_text": raw_text,
            "raw_text_hash": digest,
            "source_url": args.source_url,
            "locator_text": "; ".join(
                item
                for item in [args.source_title, args.volume, args.section or args.start_heading, title]
                if item
            ),
            "extraction_method": "repeated-title heading segmentation",
            "extractor_name": Path(__file__).name,
            "extractor_version": "0.1.0",
            "extraction_command": " ".join(sys.argv),
            "captured_at": date.today().isoformat(),
            "access_date": date.today().isoformat(),
            "boundary_status": "script_extracted",
            "boundary_confidence": "medium",
            "entry_type": "unknown",
            "ai_case_candidate_count": "",
            "linked_case_ids": "",
            "review_status": "extracted",
            "notes": "Entry requires AI or human classification before case normalization.",
        }
        records.append(record)

    emit_records(records, args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
