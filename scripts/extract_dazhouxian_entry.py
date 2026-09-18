#!/usr/bin/env python3
"""Extract one titled entry from a Dazhouxian CBETA-style HTML page."""

from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.request
from pathlib import Path


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


def find_heading(text: str, title: str, start_at: int = 0) -> re.Match[str] | None:
    pattern = re.compile(rf"(?m)^[\s\u3000]*{re.escape(title)}[\s\u3000]*$")
    return pattern.search(text, start_at)


def extract_entry(text: str, title: str, next_title: str | None) -> str:
    heading = find_heading(text, title)
    if not heading:
        raise SystemExit(f"entry heading not found: {title}")

    start = heading.start()

    if next_title:
        next_heading = find_heading(text, next_title, heading.end())
        if not next_heading:
            raise SystemExit(f"next entry heading not found: {next_title}")
        end = next_heading.start()
    else:
        next_heading = re.search(r"(?m)^\s*\S{1,12}\s*$", text[heading.end() :])
        end = heading.end() + next_heading.start() if next_heading else len(text)

    return text[start:end].strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Local HTML path or URL.")
    parser.add_argument("--title", required=True, help="Exact entry heading.")
    parser.add_argument("--next-title", help="Exact heading of the following entry.")
    args = parser.parse_args()

    raw = load_text(args.input)
    text = normalize_html(raw)
    entry = extract_entry(text, args.title, args.next_title)
    print(entry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
