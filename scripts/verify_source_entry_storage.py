#!/usr/bin/env python3
"""Verify source-entry manifests against normalized text and source artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line or raw_line.startswith("#"):
            continue
        if ":" not in raw_line:
            raise ValueError(f"{path}:{line_number}: expected key: value")
        key, value = raw_line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def require_path(manifest_path: Path, fields: dict[str, str], key: str) -> Path:
    value = fields.get(key, "")
    if not value:
        raise ValueError(f"{manifest_path}: missing {key}")
    path = Path(value)
    if not path.is_file():
        raise ValueError(f"{manifest_path}: {key} does not exist: {path}")
    return path


def verify_manifest(manifest_path: Path) -> None:
    fields = parse_manifest(manifest_path)
    normalized_path = require_path(manifest_path, fields, "normalized_storage_uri")
    normalized = json.loads(normalized_path.read_text(encoding="utf-8"))

    actual_raw_hash = hashlib.sha256(normalized["raw_text"].encode("utf-8")).hexdigest()
    if actual_raw_hash != fields.get("raw_text_hash"):
        raise ValueError(f"{manifest_path}: raw_text_hash mismatch")

    actual_normalized_hash = sha256_bytes(normalized_path)
    if actual_normalized_hash != fields.get("normalized_artifact_hash"):
        raise ValueError(f"{manifest_path}: normalized_artifact_hash mismatch")

    source_uri = fields.get("source_artifact_uri", "")
    source_hash = fields.get("source_artifact_hash", "")
    if bool(source_uri) != bool(source_hash):
        raise ValueError(f"{manifest_path}: source artifact path and hash must be set together")
    if source_uri and sha256_bytes(Path(source_uri)) != source_hash:
        raise ValueError(f"{manifest_path}: source_artifact_hash mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest-dir",
        default="data/source_entries/manifests",
        help="Directory containing ENT*.yml manifests.",
    )
    args = parser.parse_args()

    manifests = sorted(Path(args.manifest_dir).glob("ENT*.yml"))
    if not manifests:
        raise SystemExit(f"no manifests found in {args.manifest_dir}")

    failures = []
    for manifest in manifests:
        try:
            verify_manifest(manifest)
            print(f"OK {manifest}")
        except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append(str(exc))
            print(f"FAIL {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
