#!/usr/bin/env python3
"""Validate source catalogs and show administrative processing status."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter

from source_catalog_io import CATALOG_ROOT, read_catalog, require_batch_eligible, validate_source_catalog


def source_ids() -> list[str]:
    return sorted(path.name for path in CATALOG_ROOT.glob("SRC*") if path.is_dir())


def validate(_: argparse.Namespace) -> int:
    errors: list[str] = []
    for source_id in source_ids():
        source_errors = validate_source_catalog(source_id)
        if source_errors:
            errors.extend(source_errors)
            print(f"FAIL {source_id}")
        else:
            print(f"OK {source_id}")
    for error in errors:
        print(f"  {error}", file=sys.stderr)
    return 1 if errors else 0


def status(_: argparse.Namespace) -> int:
    print("source,inventory_status,total,selected,ready,running,completed,blocked,human_approved")
    for source_id in source_ids():
        config, rows = read_catalog(source_id)
        pipeline = Counter(row["pipeline_status"] for row in rows)
        print(",".join(map(str, (
            source_id,
            config["inventory_status"],
            len(rows),
            sum(row["selection_status"] == "selected" for row in rows),
            pipeline["ready"], pipeline["running"], pipeline["completed"], pipeline["blocked"],
            sum(row["human_review_status"] == "approved" for row in rows),
        ))))
    return 0


def queue(args: argparse.Namespace) -> int:
    _, rows = read_catalog(args.source_id)
    writer = csv.writer(sys.stdout)
    writer.writerow(("article_id", "source_entry_id", "title", "rights_status"))
    for row in rows:
        try:
            require_batch_eligible(row)
        except ValueError:
            continue
        writer.writerow((row["article_id"], row["source_entry_id"], row["title"], row["rights_status"]))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate").set_defaults(handler=validate)
    commands.add_parser("status").set_defaults(handler=status)
    queue_parser = commands.add_parser("queue")
    queue_parser.add_argument("--source-id", required=True)
    queue_parser.set_defaults(handler=queue)
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
