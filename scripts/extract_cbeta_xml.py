#!/usr/bin/env python3
"""Extract source-entry records from a CBETA TEI P5 XML file.

Entry boundary rules (version 0.1.0):

- The document is walked in order. `<cb:juan fun="open">` (or a
  `milestone unit="juan"`) updates the current volume; a `<head>` that is
  followed by at least one `<p>` before the next `<head>` starts an entry;
  a `<head>` with no following `<p>` is structural (work title, category,
  juan label) and only updates the recorded section.
- `<head>` elements inside `<list>` belong to the table of contents and are
  never treated as entries.
- Entry text is the concatenation of its `<p>` blocks. Apparatus that is not
  part of the reading text (`<note>`, `<anchor>`, `<cb:mulu>`) is dropped;
  `<lb>`/`<pb>` line breaks are removed inside a paragraph; paragraphs are
  joined with a blank line and an ideographic indent.
- Nested entries: a `<head>` nested deeper than the current entry's level
  still starts a new entry (the TEI structure is followed exactly, which is
  what avoids the merged-entry blind spot of heading heuristics). When an
  entry contains such nested headings, the parent record's notes carry a
  `contains_nested_entries` flag listing the split-off headings so later
  case detection knows the parent text is not atomic.

The extractor preserves evidence; it does not decide whether an entry is a
case, whether facts are true, or how a case should be tagged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from source_entry_io import emit_records


EXTRACTOR_VERSION = "0.1.1"
EXTRACTION_METHOD = "cbeta_xml_tei_structure"

TEI = "{http://www.tei-c.org/ns/1.0}"
CB = "{http://www.cbeta.org/ns/1.0}"

# Elements whose content is apparatus, not reading text.
DROPPED_TAGS = {TEI + "note", TEI + "anchor", CB + "mulu", TEI + "figDesc"}

CN_NUMERALS = {
    1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八",
    9: "九", 10: "十", 11: "十一", 12: "十二", 13: "十三", 14: "十四",
    15: "十五", 16: "十六", 17: "十七", 18: "十八", 19: "十九", 20: "二十",
}


def load_xml(input_ref: str) -> ET.Element:
    if input_ref.startswith(("http://", "https://")):
        with urllib.request.urlopen(input_ref, timeout=60) as response:
            data = response.read()
    else:
        data = Path(input_ref).read_bytes()
    return ET.fromstring(data)


def volume_label(n: str, labels: list[str]) -> str:
    if labels:
        try:
            return labels[int(n) - 1]
        except (ValueError, IndexError):
            pass
    try:
        number = int(n)
    except ValueError:
        return f"卷{n}"
    return f"卷{CN_NUMERALS.get(number, str(number))}"


def inner_text(element: ET.Element) -> str:
    """Reading text of an element, skipping apparatus subtrees and line breaks."""
    chunks: list[str] = []

    def walk(node: ET.Element) -> None:
        if node.tag in DROPPED_TAGS:
            return
        if node.text:
            chunks.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                chunks.append(child.tail)

    walk(element)
    return re.sub(r"\s+", "", "".join(chunks))


def stream_events(body: ET.Element) -> list[dict]:
    """Flatten the body into an ordered stream of juan/head/paragraph events.

    Each event records the chain of enclosing cb:div serial numbers so nested
    headings can be recognised by true ancestor relationships. Heads inside a
    <list> (table of contents) are marked and never treated as entries.
    """
    events: list[dict] = []
    div_counter = 0

    def walk(node: ET.Element, div_path: tuple[int, ...], in_list: bool) -> None:
        nonlocal div_counter
        tag = node.tag
        if tag == CB + "juan" and node.get("fun") == "open":
            events.append({"kind": "juan", "n": node.get("n", "")})
        elif tag == TEI + "milestone" and node.get("unit") == "juan":
            events.append({"kind": "juan", "n": node.get("n", "")})
        elif tag == TEI + "head":
            events.append({
                "kind": "head",
                "text": inner_text(node),
                "div_path": div_path,
                "in_list": in_list,
            })
            return
        elif tag == TEI + "p":
            events.append({"kind": "p", "text": inner_text(node), "in_list": in_list})
            return
        child_in_list = in_list or tag == TEI + "list"
        child_path = div_path
        if tag == CB + "div":
            div_counter += 1
            child_path = div_path + (div_counter,)
        for child in node:
            walk(child, child_path, child_in_list)

    walk(body, (), False)
    return events


def extract_entries(
    events: list[dict],
    start_heading: str | None,
    end_heading: str | None,
    juan: str | None = None,
) -> list[dict]:
    """Group the event stream into entry records under the boundary rules.

    With `juan` set, only entries in that volume (by the nearest preceding
    juan marker) are returned; structural headings outside it are ignored.
    """
    volume = ""
    section = ""
    entries: list[dict] = []
    current: dict | None = None
    started = start_heading is None
    pending_head: dict | None = None

    def close_current() -> None:
        nonlocal current
        if current is not None:
            entries.append(current)
            current = None

    def close_pending() -> None:
        nonlocal pending_head, section
        if pending_head is not None:
            # A head with no following <p> is structural; it only updates the section.
            section = pending_head["text"]
            pending_head = None

    for event in events:
        if event["kind"] == "juan":
            volume = event["n"]
            continue
        if event["kind"] == "head":
            title = event["text"]
            if juan is not None and volume != juan:
                # Outside the selected volume: track nothing.
                continue
            if not started:
                if title == start_heading:
                    started = True
                else:
                    continue
            if end_heading is not None and title == end_heading:
                close_pending()
                close_current()
                break
            if event["in_list"]:
                continue
            close_pending()
            pending_head = {
                "text": title,
                "div_path": event["div_path"],
                "volume": volume,
                "section": section,
                "paragraphs": [],
            }
            continue
        # paragraph
        if not started or event["in_list"]:
            continue
        if juan is not None and volume != juan:
            continue
        if pending_head is not None:
            # The pending head has real content: it is an entry.
            close_current()
            current = {
                "title": pending_head["text"],
                "volume": pending_head["volume"],
                "section": pending_head["section"],
                "div_path": pending_head["div_path"],
                "paragraphs": [],
                "nested_heads": [],
            }
            pending_head = None
        if current is not None and event["text"]:
            current["paragraphs"].append(event["text"])
    close_pending()
    close_current()

    # Detect nested entries: entry B is nested in entry A when the cb:div
    # containing B's head is a proper descendant of the cb:div containing
    # A's head. A head directly under the body has no containing div and can
    # never be a nesting parent. The nested heads were already split out as
    # their own entries; here we only flag the parent record.
    for index, entry in enumerate(entries):
        if not entry["div_path"]:
            continue
        prefix = entry["div_path"]
        nested = [
            item["title"]
            for item in entries
            if item is not entry
            and len(item["div_path"]) > len(prefix)
            and item["div_path"][: len(prefix)] == prefix
        ]
        if nested:
            entry["nested_heads"] = nested
    return entries


def make_entry_id(prefix: str, sequence: int) -> str:
    return f"{prefix}{sequence:06d}"


def make_entry_key(source_id: str, volume: str, section: str, title: str, digest: str) -> str:
    parts = [source_id, volume, section, title, digest[:12]]
    return ":".join(part for part in parts if part)


def build_records(
    entries: list[dict],
    *,
    source_id: str,
    source_title: str,
    source_url: str,
    sutra_no: str,
    language: str,
    volume_labels: list[str],
    entry_id_prefix: str,
    start_sequence: int,
    extraction_command: str,
) -> list[dict]:
    """Turn extracted entries into normalized source-entry records."""
    records = []
    for index, entry in enumerate(entries, start=start_sequence):
        volume = volume_label(entry["volume"], volume_labels)
        raw_text = entry["title"] + "\n\n" + "\n\n".join(
            "　　" + paragraph for paragraph in entry["paragraphs"]
        )
        digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
        notes = "Entry requires AI or human classification before case normalization."
        if entry["nested_heads"]:
            notes = (
                "contains_nested_entries: the TEI structure nested these headings inside this entry and they were split out: "
                + "、".join(entry["nested_heads"])
                + ". " + notes
            )
        records.append({
            "source_entry_id": make_entry_id(entry_id_prefix, index),
            "source_entry_key": make_entry_key(source_id, volume, entry["section"], entry["title"], digest),
            "source_id": source_id,
            "parent_entry_id": "",
            "source_title": source_title,
            "volume": volume,
            "section": entry["section"],
            "entry_title": entry["title"],
            "entry_sequence": index,
            "language": language,
            "raw_text": raw_text,
            "raw_text_hash": digest,
            "source_url": source_url,
            "locator_text": "，".join(
                part for part in [sutra_no, f"《{source_title}》", volume, entry["section"], entry["title"]] if part
            ),
            "extraction_method": EXTRACTION_METHOD,
            "extractor_name": Path(__file__).name,
            "extractor_version": EXTRACTOR_VERSION,
            "extraction_command": extraction_command,
            "captured_at": date.today().isoformat(),
            "access_date": date.today().isoformat(),
            "boundary_status": "script_extracted",
            "boundary_confidence": "high",
            "entry_type": "unknown",
            "ai_case_candidate_count": "",
            "linked_case_ids": "",
            "review_status": "extracted",
            "notes": notes,
        })
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Local CBETA XML path or URL.")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-title", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--sutra-no", default="", help="CBETA text number, e.g. T51n2072.")
    parser.add_argument("--language", default="zh-Hant")
    parser.add_argument("--volume-labels", default="", help="Comma-separated juan labels, e.g. 卷上,卷中,卷下.")
    parser.add_argument("--start-heading", help="First head to include (exact text).")
    parser.add_argument("--end-heading", help="Head at which to stop (exclusive).")
    parser.add_argument("--juan", help="Only include entries in this volume number (cb:juan n).")
    parser.add_argument("--entry-id-prefix", default="ENT")
    parser.add_argument("--start-sequence", type=int, default=1)
    parser.add_argument("--output", default="", help="Optional .jsonl or single-record .json output path.")
    args = parser.parse_args()

    labels = [label for label in args.volume_labels.split(",") if label]
    root = load_xml(args.input)
    body = root.find(f"{TEI}text/{TEI}body")
    if body is None:
        raise SystemExit("no TEI body found in input")
    events = stream_events(body)
    entries = extract_entries(events, args.start_heading, args.end_heading, juan=args.juan)
    records = build_records(
        entries,
        source_id=args.source_id,
        source_title=args.source_title,
        source_url=args.source_url,
        sutra_no=args.sutra_no,
        language=args.language,
        volume_labels=labels,
        entry_id_prefix=args.entry_id_prefix,
        start_sequence=args.start_sequence,
        extraction_command=" ".join(sys.argv),
    )

    emit_records(records, args.output)
    print(f"extracted {len(records)} entries", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
