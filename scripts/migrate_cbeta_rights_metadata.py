#!/usr/bin/env python3
"""Repair rights metadata for normalized entries derived from CBETA XML P5."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import batch_capture
from source_catalog_io import FIELDS, parse_simple_yaml


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "data/source_entries/public"
MANIFEST_DIR = ROOT / "data/source_entries/manifests"
CATALOG_ROOT = ROOT / "data/source_catalogs"
RIGHTS_ROOT = ROOT / "data/rights_reviews"

CBETA_REVIEW_BY_SOURCE = {
    "SRC0001": "RR0013",
    "SRC0024": "RR0006",
}
CBETA_URL_MARKERS = ("cbetaonline.dila.edu.tw", "cbeta-org/xml-p5")
LICENSE_NOTE = (
    "The underlying historical work is public domain. This normalized entry is derived "
    "from the CBETA XML P5 electronic edition under CC BY-NC-SA 4.0; see data/NOTICE.md."
)


def with_version_fields(record: dict[str, Any], inventory: dict[str, str]) -> dict[str, Any]:
    updated: dict[str, Any] = {}
    for key, value in record.items():
        updated[key] = value
        if key == "source_url":
            updated["source_version"] = inventory["source_version"]
            updated["source_revision"] = inventory["source_revision"]
    notes = str(updated.get("notes", "")).strip()
    if "CC BY-NC-SA 4.0" not in notes or "data/NOTICE.md" not in notes:
        updated["notes"] = f"{notes} {LICENSE_NOTE}".strip()
    return updated


def migrate_entries() -> dict[str, list[str]]:
    migrated: dict[str, list[str]] = {source_id: [] for source_id in CBETA_REVIEW_BY_SOURCE}
    for path in sorted(PUBLIC_DIR.glob("ENT*.normalized.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        source_id = record.get("source_id", "")
        source_url = record.get("source_url", "")
        if source_id not in CBETA_REVIEW_BY_SOURCE or not any(
            marker in source_url for marker in CBETA_URL_MARKERS
        ):
            continue
        inventory = parse_simple_yaml(CATALOG_ROOT / source_id / "inventory.yml")
        review = parse_simple_yaml(RIGHTS_ROOT / f"{CBETA_REVIEW_BY_SOURCE[source_id]}.yml")
        updated = with_version_fields(record, inventory)
        path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        batch_capture.write_manifest(
            updated["source_entry_id"], source_id, path, updated, review, inventory, MANIFEST_DIR
        )
        migrated[source_id].append(updated["source_entry_id"])
    return migrated


def migrate_catalog(source_id: str, entry_ids: set[str], review_id: str) -> None:
    path = CATALOG_ROOT / source_id / "articles.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if row["source_entry_id"] in entry_ids:
            row["rights_review_id"] = review_id
            row["rights_status"] = "open_license_verified"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    migrated = migrate_entries()
    for source_id, entry_ids in migrated.items():
        migrate_catalog(source_id, set(entry_ids), CBETA_REVIEW_BY_SOURCE[source_id])
        print(f"{source_id}: processed {len(entry_ids)} CBETA-derived entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
