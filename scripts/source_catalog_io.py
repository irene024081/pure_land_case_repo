#!/usr/bin/env python3
"""Read and validate per-source article catalogs."""

from __future__ import annotations

import csv
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = ROOT / "data" / "source_catalogs"
MANIFEST_ROOT = ROOT / "data" / "source_entries" / "manifests"

FIELDS = [
    "article_id", "source_id", "source_item_key", "source_entry_id", "case_ids",
    "title", "canonical_url", "language", "published_date", "content_type",
    "discovery_status", "selection_status", "rights_review_id", "rights_status",
    "capture_status", "boundary_status", "pipeline_status", "current_stage",
    "last_run_id", "machine_review_status", "human_review_status", "assigned_to",
    "last_checked_at", "notes",
]

ALLOWED = {
    "discovery_status": {"discovered", "metadata_incomplete", "inaccessible", "removed"},
    "selection_status": {"unreviewed", "selected", "excluded", "deferred"},
    "rights_status": {"pending", "public_domain_verified", "open_license_verified", "permission_obtained", "restricted_internal", "locator_only", "legal_review_required", "prohibited", "unknown"},
    "capture_status": {"not_started", "captured", "verified", "failed", "locator_only"},
    "boundary_status": {"not_started", "script_extracted", "ai_segmented", "machine_checked", "human_checked", "needs_recheck", "rejected"},
    "pipeline_status": {"not_started", "ready", "running", "blocked", "completed", "failed"},
    "machine_review_status": {"not_reviewed", "legacy_machine_checked", "passed", "failed", "needs_revision"},
    "human_review_status": {"not_reviewed", "approved", "needs_revision", "rejected"},
}


def parse_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{path}:{number}: expected key: value")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def read_catalog(source_id: str, catalog_root: Path = CATALOG_ROOT) -> tuple[dict[str, str], list[dict[str, str]]]:
    source_dir = catalog_root / source_id
    config = parse_simple_yaml(source_dir / "source.yml")
    with (source_dir / "articles.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"{source_dir / 'articles.csv'}: header does not match schema")
        rows = list(reader)
    return config, rows


def manifest_fields(entry_id: str, manifest_root: Path = MANIFEST_ROOT) -> dict[str, str]:
    return parse_simple_yaml(manifest_root / f"{entry_id}.yml")


def validate_source_catalog(
    source_id: str,
    catalog_root: Path = CATALOG_ROOT,
    manifest_root: Path = MANIFEST_ROOT,
) -> list[str]:
    errors: list[str] = []
    try:
        config, rows = read_catalog(source_id, catalog_root)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    if config.get("source_id") != source_id:
        errors.append(f"{source_id}: source.yml source_id mismatch")
    if config.get("inventory_status") not in {"not_started", "partial", "complete", "needs_refresh"}:
        errors.append(f"{source_id}: invalid inventory_status")
    if not config.get("inventory_scope"):
        errors.append(f"{source_id}: missing inventory_scope")
    for field in ("inventory_adapter", "inventory_refresh_policy", "entry_adapter", "rights_review_id"):
        if not config.get(field):
            errors.append(f"{source_id}: missing {field}")
    if not rows:
        errors.append(f"{source_id}: catalog has no rows")

    for field in ("article_id", "source_item_key", "source_entry_id", "canonical_url"):
        values = [row[field] for row in rows if row[field]]
        for value, count in Counter(values).items():
            if count > 1:
                errors.append(f"{source_id}: duplicate {field}: {value}")

    for number, row in enumerate(rows, 2):
        label = f"{source_id}/articles.csv:{number}"
        if row["source_id"] != source_id:
            errors.append(f"{label}: source_id mismatch")
        if not row["article_id"].startswith(f"{source_id}-ART"):
            errors.append(f"{label}: invalid article_id")
        for field in ("article_id", "source_item_key", "title", "language", "content_type"):
            if not row[field]:
                errors.append(f"{label}: missing {field}")
        for field, allowed in ALLOWED.items():
            if row[field] not in allowed:
                errors.append(f"{label}: invalid {field}: {row[field]}")
        if row["capture_status"] == "verified" and not row["source_entry_id"]:
            errors.append(f"{label}: verified item has no source_entry_id")
        if row["source_entry_id"]:
            try:
                manifest = manifest_fields(row["source_entry_id"], manifest_root)
            except OSError:
                errors.append(f"{label}: missing manifest for {row['source_entry_id']}")
            else:
                if manifest.get("source_id") != source_id:
                    errors.append(f"{label}: manifest source_id mismatch")
                if row["rights_review_id"] and manifest.get("rights_review_id") not in ("", row["rights_review_id"]):
                    errors.append(f"{label}: rights_review_id differs from manifest")
    return errors


def find_entry_row(source_id: str, source_entry_id: str) -> dict[str, str]:
    _, rows = read_catalog(source_id)
    matches = [row for row in rows if row["source_entry_id"] == source_entry_id]
    if len(matches) != 1:
        raise ValueError(f"expected one catalog row for {source_entry_id}, found {len(matches)}")
    return matches[0]


def find_article(source_id: str, article_id: str) -> tuple[dict[str, str], dict[str, str]]:
    config, rows = read_catalog(source_id)
    matches = [row for row in rows if row["article_id"] == article_id]
    if len(matches) != 1:
        raise ValueError(f"expected one catalog row for {article_id}, found {len(matches)}")
    return config, matches[0]


def update_article(
    source_id: str,
    article_id: str,
    changes: dict[str, str],
    catalog_root: Path = CATALOG_ROOT,
) -> dict[str, str]:
    source_dir = catalog_root / source_id
    catalog_path = source_dir / "articles.csv"
    config, rows = read_catalog(source_id, catalog_root)
    del config
    matches = [row for row in rows if row["article_id"] == article_id]
    if len(matches) != 1:
        raise ValueError(f"expected one catalog row for {article_id}, found {len(matches)}")
    row = matches[0]
    unknown = sorted(set(changes) - set(FIELDS))
    if unknown:
        raise ValueError(f"unknown catalog fields: {unknown}")
    row.update(changes)

    temp_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=source_dir, delete=False
        ) as handle:
            temp_name = handle.name
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, catalog_path)
    finally:
        if temp_name and Path(temp_name).exists():
            Path(temp_name).unlink()
    return row


def require_batch_eligible(row: dict[str, str]) -> None:
    required = {
        "selection_status": "selected",
        "capture_status": "verified",
        "pipeline_status": "ready",
    }
    for field, expected in required.items():
        if row[field] != expected:
            raise ValueError(f"{row['article_id']}: {field} must be {expected}, got {row[field]}")
    if row["rights_status"] in {"pending", "unknown", "prohibited"}:
        raise ValueError(f"{row['article_id']}: rights_status blocks processing")
