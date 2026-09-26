#!/usr/bin/env python3
"""Batch capture: catalog -> entry extraction -> retained source entries.

Reads a source's adapter configuration, runs the matching entry extractor over
the selected scope, and writes one normalized source entry JSON plus manifest
per item under data/source_entries/. This only retains evidence; it never
starts a pipeline run.

Usage:
    python3 scripts/batch_capture.py --source-id SRC0024
    python3 scripts/batch_capture.py --source-id SRC0001 --juan 9
    python3 scripts/batch_capture.py --source-id SRC0024 --dry-run

Rules:
- Rights gate: only sources whose rights review settles internal retention
  (public_domain_verified / open_license_verified / permission_obtained) are
  captured. Everything else is skipped with the reason recorded.
- Idempotent: an item whose stable key is already captured is skipped; rerun
  produces no new files or catalog rows.
- Failures are recorded with their reason and the batch continues.
- A summary report (captured / skipped / failed) prints at the end.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import date
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import extract_cbeta_xml  # noqa: E402
from source_catalog_io import CATALOG_ROOT, parse_simple_yaml, read_catalog  # noqa: E402
from source_entry_io import emit_records  # noqa: E402

ROOT = SCRIPTS_DIR.parent
PUBLIC_DIR = ROOT / "data" / "source_entries" / "public"
MANIFEST_DIR = ROOT / "data" / "source_entries" / "manifests"
RIGHTS_DIR = ROOT / "data" / "rights_reviews"

SETTLED_RIGHTS = {"public_domain_verified", "open_license_verified", "permission_obtained"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def existing_entry_numbers(public_dir: Path, manifest_dir: Path) -> set[int]:
    numbers: set[int] = set()
    import re

    for base in (public_dir, manifest_dir):
        if base.exists():
            for path in base.glob("ENT*"):
                match = re.match(r"ENT(\d+)", path.name)
                if match:
                    numbers.add(int(match.group(1)))
    return numbers


def write_manifest(entry_id: str, source_id: str, entry_path: Path, record: dict,
                   rights_review_id: str, manifest_dir: Path) -> Path:
    rel = os.path.relpath(entry_path.resolve(), Path(ROOT).resolve())
    manifest = f"""source_entry_id: {entry_id}
source_id: {source_id}
storage_class: tracked_public
storage_uri: {rel}
normalized_storage_uri: {rel}
source_artifact_uri:
raw_capture_status: persisted_verified
capture_representation: normalized_entry_json
raw_text_hash: {record['raw_text_hash']}
normalized_artifact_hash: {sha256_file(entry_path)}
source_artifact_hash:
content_type: application/json
byte_size: {entry_path.stat().st_size}
captured_at: {record['captured_at']}
rights_basis: public_domain_historical_text
rights_status: public_domain_verified
rights_review_id: {rights_review_id}
terms_url:
terms_checked_at:
public_display_policy: full_normalized_historical_text
retention_policy: permanent
"""
    target = manifest_dir / f"{entry_id}.yml"
    target.write_text(manifest, encoding="utf-8")
    return target


def rights_gate(source_id: str, source_config: dict, rights_dir: Path = RIGHTS_DIR) -> str:
    """Return '' when capture is allowed, else the refusal reason."""
    review_id = source_config.get("rights_review_id", "")
    review_path = Path(rights_dir) / f"{review_id}.yml"
    if not review_id or not review_path.exists():
        return f"no rights review ({review_id or 'none'})"
    review = parse_simple_yaml(review_path)
    status = review.get("rights_status", "")
    if status in SETTLED_RIGHTS:
        return ""
    basis = review.get("internal_retention_basis", "")
    return f"rights_status={status}, internal_retention_basis={basis}: 非明确允许内部保存，跳过"


def catalog_key(record: dict) -> str:
    return ":".join(part for part in (record["volume"], record["section"], record["entry_title"]) if part)


def append_catalog_rows(source_id: str, source_config: dict, new_rows: list[dict],
                        catalog_root: Path) -> None:
    import csv

    from source_catalog_io import FIELDS

    catalog_path = catalog_root / source_id / "articles.csv"
    _, rows = read_catalog(source_id, catalog_root=catalog_root)
    rows.extend(new_rows)
    with catalog_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def capture_cbeta_source(source_id: str, source_config: dict, inventory_config: dict,
                         args: argparse.Namespace, paths: dict) -> dict:
    """Capture a CBETA-backed classical source. Returns the summary report."""
    report = {"captured": [], "skipped": [], "failed": []}
    _, catalog_rows = read_catalog(source_id, catalog_root=paths["catalog_root"])
    known_keys = {row["source_item_key"]: row for row in catalog_rows}
    preexisting_captured = {
        row["source_item_key"] for row in catalog_rows if row["source_entry_id"]
    }

    xml_ref = args.xml or inventory_config.get("xml_path", "")
    if not xml_ref:
        raise SystemExit(f"inventory.yml for {source_id} lacks xml_path; pass --xml")
    root = extract_cbeta_xml.load_xml(xml_ref)
    body = root.find(f"{extract_cbeta_xml.TEI}text/{extract_cbeta_xml.TEI}body")
    if body is None:
        raise SystemExit("no TEI body found")
    events = extract_cbeta_xml.stream_events(body)
    entries = extract_cbeta_xml.extract_entries(
        events,
        inventory_config.get("start_heading") or None,
        inventory_config.get("end_heading") or None,
        juan=args.juan,
    )
    labels = [v for v in inventory_config.get("volume_labels", "").split(",") if v]
    records = extract_cbeta_xml.build_records(
        entries,
        source_id=source_id,
        source_title=inventory_config.get("source_title", ""),
        source_url=inventory_config.get("source_url", ""),
        sutra_no=inventory_config.get("sutra_no", ""),
        language=inventory_config.get("language") or source_config.get("default_language", "zh-Hant"),
        volume_labels=labels,
        entry_id_prefix="TMP",
        start_sequence=1,
        extraction_command="batch_capture.py " + " ".join(sys.argv[1:]),
    )

    used_numbers = existing_entry_numbers(paths["public_dir"], paths["manifest_dir"])
    next_number = max(used_numbers, default=0) + 1
    today = date.today().isoformat()
    new_catalog_rows: list[dict] = []
    batch_seen: set[str] = set()
    highest_art = 0
    prefix = f"{source_id}-ART"
    for row in catalog_rows:
        if row["article_id"].startswith(prefix):
            highest_art = max(highest_art, int(row["article_id"][len(prefix):]))

    from source_catalog_io import FIELDS

    for record in records:
        key = catalog_key(record)
        try:
            if key in preexisting_captured:
                report["skipped"].append((key, "already captured as " + known_keys[key]["source_entry_id"]))
                batch_seen.add(key)
                continue
            if key in batch_seen:
                # Same title appears more than once in the work: disambiguate
                # by extraction sequence so distinct entries are never merged.
                key = f"{key}#{record['entry_sequence']}"
            batch_seen.add(key)
            entry_id = f"ENT{next_number:06d}"
            next_number += 1
            record["source_entry_id"] = entry_id
            entry_path = paths["public_dir"] / f"{entry_id}.normalized.json"
            if not args.dry_run:
                paths["public_dir"].mkdir(parents=True, exist_ok=True)
                paths["manifest_dir"].mkdir(parents=True, exist_ok=True)
                emit_records([record], str(entry_path))
                write_manifest(entry_id, source_id, entry_path, record,
                               source_config.get("rights_review_id", ""), paths["manifest_dir"])
            report["captured"].append((key, entry_id))
            if key not in known_keys:
                highest_art += 1
                row = {field: "" for field in FIELDS}
                row.update({
                    "article_id": f"{prefix}{highest_art:06d}",
                    "source_id": source_id,
                    "source_item_key": key,
                    "source_entry_id": entry_id,
                    "title": record["entry_title"],
                    "canonical_url": inventory_config.get("source_url", "") + "#" + record["source_entry_key"],
                    "language": record["language"],
                    "content_type": "book_entry",
                    "discovery_status": "discovered",
                    "selection_status": "unreviewed",
                    "rights_review_id": source_config.get("rights_review_id", ""),
                    "rights_status": "public_domain_verified",
                    "capture_status": "verified",
                    "boundary_status": "script_extracted",
                    "pipeline_status": "not_started",
                    "machine_review_status": "not_reviewed",
                    "human_review_status": "not_reviewed",
                    "last_checked_at": today,
                    "notes": record["notes"] if "contains_nested_entries" in record["notes"] else "",
                })
                new_catalog_rows.append(row)
                known_keys[key] = row
        except Exception as exc:  # record and continue
            report["failed"].append((key, str(exc)))
    if new_catalog_rows and not args.dry_run:
        append_catalog_rows(source_id, source_config, new_catalog_rows, paths["catalog_root"])
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--xml", default="", help="Override CBETA XML path/URL.")
    parser.add_argument("--juan", default=None, help="Only capture this volume (CBETA sources).")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--catalog-root", type=Path, default=CATALOG_ROOT)
    parser.add_argument("--public-dir", type=Path, default=PUBLIC_DIR)
    parser.add_argument("--manifest-dir", type=Path, default=MANIFEST_DIR)
    args = parser.parse_args()

    source_config = parse_simple_yaml(Path(args.catalog_root) / args.source_id / "source.yml")
    inventory_path = Path(args.catalog_root) / args.source_id / "inventory.yml"
    inventory_config = parse_simple_yaml(inventory_path) if inventory_path.exists() else {}

    refusal = rights_gate(args.source_id, source_config)
    if refusal:
        print(f"SKIP {args.source_id}: {refusal}")
        return 0

    paths = {"catalog_root": Path(args.catalog_root), "public_dir": Path(args.public_dir),
             "manifest_dir": Path(args.manifest_dir)}
    extractor = source_config.get("extractor_name", "")
    if extractor == "extract_cbeta_xml.py":
        report = capture_cbeta_source(args.source_id, source_config, inventory_config, args, paths)
    else:
        raise SystemExit(f"batch capture not implemented for extractor: {extractor}")

    print(f"== {args.source_id} 批量捕获汇总 ==")
    print(f"成功 {len(report['captured'])}  跳过 {len(report['skipped'])}  失败 {len(report['failed'])}"
          + ("  (dry-run)" if args.dry_run else ""))
    for key, reason in report["failed"]:
        print(f"  失败 {key}: {reason}")
    return 0 if not report["failed"] else 1


if __name__ == "__main__":
    sys.exit(main())
