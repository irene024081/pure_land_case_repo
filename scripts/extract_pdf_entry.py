#!/usr/bin/env python3
"""Extract a source_entry record from a text-readable PDF page range."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

from source_entry_io import emit_records

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - local environment guard
    raise SystemExit(
        "pypdf is required. Install it with: python3 -m pip install pypdf"
    ) from exc


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_running_headers(text: str, running_headers: list[str]) -> str:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            lines.append("")
            continue
        if re.fullmatch(r"[IVXLC]+|\d+", line):
            continue
        if line in running_headers:
            continue
        lines.append(raw_line)
    return normalize_text("\n".join(lines))


def trim_text(text: str, trim_before: str, trim_after: str) -> str:
    if trim_before:
        start = text.find(trim_before)
        if start == -1:
            raise SystemExit(f"trim-before marker not found: {trim_before}")
        text = text[start:]
    if trim_after:
        end = text.find(trim_after)
        if end == -1:
            raise SystemExit(f"trim-after marker not found: {trim_after}")
        text = text[:end]
    return normalize_text(text)


def extract_pages(pdf_path: Path, page_start: int, page_end: int) -> str:
    reader = PdfReader(str(pdf_path))
    if page_start < 1 or page_end < page_start or page_end > len(reader.pages):
        raise SystemExit(
            f"invalid page range {page_start}-{page_end}; PDF has {len(reader.pages)} pages"
        )
    chunks: list[str] = []
    for page_number in range(page_start, page_end + 1):
        page = reader.pages[page_number - 1]
        chunks.append(page.extract_text() or "")
    return normalize_text("\n\n".join(chunks))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Local PDF path.")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-title", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--source-entry-id", default="")
    parser.add_argument("--volume", default="")
    parser.add_argument("--section", default="")
    parser.add_argument("--entry-title", required=True)
    parser.add_argument("--entry-sequence", required=True)
    parser.add_argument("--language", default="zh-Hans")
    parser.add_argument("--page-start", type=int, required=True)
    parser.add_argument("--page-end", type=int, required=True)
    parser.add_argument("--printed-page-start", default="")
    parser.add_argument("--printed-page-end", default="")
    parser.add_argument("--trim-before", default="")
    parser.add_argument("--trim-after", default="")
    parser.add_argument("--running-header", action="append", default=[])
    parser.add_argument("--output", default="", help="Optional .json output path.")
    args = parser.parse_args()

    raw_pages = extract_pages(Path(args.input), args.page_start, args.page_end)
    clean_text = remove_running_headers(raw_pages, args.running_header)
    raw_text = trim_text(clean_text, args.trim_before, args.trim_after)
    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    locator_bits = [
        args.source_title,
        args.volume,
        args.section,
        args.entry_title,
        f"PDF pages {args.page_start}-{args.page_end}",
    ]
    if args.printed_page_start:
        printed = args.printed_page_start
        if args.printed_page_end and args.printed_page_end != args.printed_page_start:
            printed = f"{printed}-{args.printed_page_end}"
        locator_bits.append(f"printed pages {printed}")

    record = {
        "source_entry_id": args.source_entry_id,
        "source_entry_key": ":".join(
            item
            for item in [
                args.source_id,
                args.volume,
                args.section,
                args.entry_title,
                digest[:12],
            ]
            if item
        ),
        "source_id": args.source_id,
        "parent_entry_id": "",
        "source_title": args.source_title,
        "volume": args.volume,
        "section": args.section,
        "entry_title": args.entry_title,
        "entry_sequence": args.entry_sequence,
        "language": args.language,
        "raw_text": raw_text,
        "raw_text_hash": digest,
        "source_url": args.source_url,
        "locator_text": "; ".join(item for item in locator_bits if item),
        "extraction_method": "PDF pypdf page-range text extraction",
        "extractor_name": Path(__file__).name,
        "extractor_version": "0.1.0",
        "extraction_command": " ".join(sys.argv),
        "captured_at": date.today().isoformat(),
        "access_date": date.today().isoformat(),
        "published_date": "",
        "page_start": args.page_start,
        "page_end": args.page_end,
        "printed_page_start": args.printed_page_start,
        "printed_page_end": args.printed_page_end,
        "boundary_status": "script_extracted",
        "boundary_confidence": "medium",
        "entry_type": "unknown",
        "ai_case_candidate_count": "",
        "linked_case_ids": "",
        "review_status": "extracted",
        "notes": "PDF page range requires source-specific boundary review before case normalization.",
    }
    emit_records([record], args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
