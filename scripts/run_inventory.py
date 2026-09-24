#!/usr/bin/env python3
"""Discover source items with an inventory adapter and sync articles.csv.

Usage:
    python3 scripts/run_inventory.py scan --source-id SRC0003 [--dry-run] [--delay 1.0]

The adapter configuration lives in data/source_catalogs/{source_id}/inventory.yml
(flat key: value). Discovery is metadata-level: it lists item titles, keys, and
URLs only. It does not fetch article bodies and grants no processing or
publication rights. New rows enter with selection_status=unreviewed and a
pending-by-default rights status.

Sync semantics:
- a key already in the catalog keeps its row untouched (incremental safety);
- a key found for the first time is appended with the next article_id;
- a previously discovered key missing from a full-scope scan is marked
  discovery_status=removed, never deleted;
- --dry-run prints the diff without writing anything.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import inventory_adapters  # noqa: E402
from source_catalog_io import CATALOG_ROOT, FIELDS, parse_simple_yaml  # noqa: E402


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def make_fetch(delay_seconds: float):
    state = {"last": 0.0}

    def fetch(url: str) -> str | None:
        wait = delay_seconds - (time.monotonic() - state["last"])
        if wait > 0:
            time.sleep(wait)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                state["last"] = time.monotonic()
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            state["last"] = time.monotonic()
            if exc.code == 404:
                return None
            raise

    return fetch


def discover(source_config: dict, inventory_config: dict, delay_seconds: float) -> list[dict]:
    adapter = source_config.get("inventory_adapter", "")
    fetch = make_fetch(delay_seconds)
    if adapter == "static_headings":
        html_text = fetch(inventory_config["entry_url"])
        return inventory_adapters.discover_static_headings(
            html_text, inventory_config, inventory_config["entry_url"]
        )
    if adapter == "wordpress_archive":
        return inventory_adapters.discover_wordpress_archive(fetch, inventory_config)
    if adapter == "paginated_html":
        return inventory_adapters.discover_paginated_html(fetch, inventory_config)
    if adapter == "pdf_toc":
        return inventory_adapters.discover_pdf_toc(inventory_config["pdf_path"], inventory_config)
    raise SystemExit(f"unknown inventory adapter: {adapter}")


def build_row(source_id: str, source_config: dict, inventory_config: dict,
              item: dict, article_id: str, today: str) -> dict:
    row = {field: "" for field in FIELDS}
    row.update({
        "article_id": article_id,
        "source_id": source_id,
        "source_item_key": item["source_item_key"],
        "title": item["title"],
        "canonical_url": item["canonical_url"],
        "language": inventory_config.get("default_language") or source_config.get("default_language", ""),
        "published_date": item.get("published_date", ""),
        "content_type": inventory_config.get("default_content_type", "article"),
        "discovery_status": "discovered",
        "selection_status": "unreviewed",
        "rights_review_id": source_config.get("rights_review_id", ""),
        "rights_status": inventory_config.get("default_rights_status", "pending"),
        "capture_status": "not_started",
        "boundary_status": "not_started",
        "pipeline_status": "not_started",
        "machine_review_status": "not_reviewed",
        "human_review_status": "not_reviewed",
        "last_checked_at": today,
        "notes": item.get("notes", ""),
    })
    return row


def sync(source_id: str, items: list[dict], dry_run: bool) -> None:
    source_dir = CATALOG_ROOT / source_id
    source_yml = source_dir / "source.yml"
    source_config = parse_simple_yaml(source_yml)
    inventory_config = parse_simple_yaml(source_dir / "inventory.yml")
    catalog_path = source_dir / "articles.csv"
    today = date.today().isoformat()

    with catalog_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    known_keys = {row["source_item_key"] for row in rows}
    new_items = [item for item in items if item["source_item_key"] not in known_keys]
    full_scope = inventory_config.get("scan_scope", "full") == "full"
    scanned_keys = {item["source_item_key"] for item in items}
    removed = [
        row for row in rows
        if full_scope and row["discovery_status"] == "discovered"
        and row["source_item_key"] not in scanned_keys
    ]

    print(f"scan: {len(items)} items; catalog: {len(rows)} rows")
    print(f"+{len(new_items)} new  ~{len(removed)} removed  ={len(rows) - len(removed)} unchanged")
    for item in new_items[:20]:
        print(f"  + {item['source_item_key']}  {item['title']}")
    if len(new_items) > 20:
        print(f"  + ... and {len(new_items) - 20} more")
    for row in removed:
        print(f"  ~ {row['article_id']}  {row['title']} -> removed")

    if dry_run:
        print("dry-run: no files written")
        return

    highest = 0
    prefix = f"{source_id}-ART"
    for row in rows:
        if row["article_id"].startswith(prefix):
            highest = max(highest, int(row["article_id"][len(prefix):]))
    for item in new_items:
        highest += 1
        rows.append(build_row(source_id, source_config, inventory_config, item, f"{prefix}{highest:06d}", today))
        known_keys.add(item["source_item_key"])
    for row in removed:
        row["discovery_status"] = "removed"
        row["last_checked_at"] = today

    with catalog_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = source_yml.read_text(encoding="utf-8").splitlines()
    lines = [
        f"last_inventory_scan_at: {today}" if line.startswith("last_inventory_scan_at:") else line
        for line in lines
    ]
    source_yml.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {catalog_path} ({len(rows)} rows)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("scan")
    scan.add_argument("--source-id", required=True)
    scan.add_argument("--dry-run", action="store_true")
    scan.add_argument("--delay", type=float, default=1.0, help="Seconds between page fetches.")
    args = parser.parse_args()

    source_dir = CATALOG_ROOT / args.source_id
    if not (source_dir / "inventory.yml").exists():
        raise SystemExit(f"missing adapter config: {source_dir / 'inventory.yml'}")
    source_config = parse_simple_yaml(source_dir / "source.yml")
    inventory_config = parse_simple_yaml(source_dir / "inventory.yml")
    items = discover(source_config, inventory_config, args.delay)
    sync(args.source_id, items, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
