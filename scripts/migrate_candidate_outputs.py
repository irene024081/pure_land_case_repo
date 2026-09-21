#!/usr/bin/env python3
"""Rekey retained v0.1 case evidence for a v0.2 candidate replay."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def migrate(
    extraction: dict[str, Any], tagging: dict[str, Any], candidate_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", candidate_id):
        raise ValueError("candidate_id must be a safe path component")
    old_case_id = extraction.get("case_id")
    if not re.fullmatch(r"CASE\d{6}", str(old_case_id)) or tagging.get("case_id") != old_case_id:
        raise ValueError("legacy outputs must identify the same CASE ID")

    new_extraction = copy.deepcopy(extraction)
    new_tagging = copy.deepcopy(tagging)
    new_extraction.pop("case_id")
    new_tagging.pop("case_id")
    for output in (new_extraction, new_tagging):
        output["candidate_id"] = candidate_id
        output["migration_source_case_id"] = old_case_id

    id_map: dict[str, str] = {}
    for fact in new_extraction["case_facts"]:
        old_id = fact["case_fact_id"]
        if not re.fullmatch(rf"{re.escape(old_case_id)}-FACT\d{{4}}", old_id):
            raise ValueError(f"fact ID does not belong to legacy CASE: {old_id}")
        new_id = candidate_id + old_id[len(old_case_id):]
        if old_id in id_map:
            raise ValueError(f"duplicate legacy fact ID: {old_id}")
        id_map[old_id] = new_id
        fact["case_fact_id"] = new_id

    for tag in new_tagging["tags"]:
        try:
            tag["supporting_case_fact_ids"] = [id_map[value] for value in tag["supporting_case_fact_ids"]]
        except KeyError as exc:
            raise ValueError(f"unmapped fact reference: {exc.args[0]}") from exc
    return new_extraction, new_tagging


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-case-dir", type=Path, required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    legacy_run = json.loads((args.legacy_case_dir / "run.json").read_text(encoding="utf-8"))
    if legacy_run.get("status") != "completed" or not str(legacy_run.get("pipeline_version", "")).startswith("0.1."):
        raise SystemExit("source must be a completed v0.1.x Case Run")
    paths = {
        stage: args.legacy_case_dir / "outputs" / f"{stage}.json"
        for stage in ("case_extraction", "entity_tagging")
    }
    for stage, path in paths.items():
        if file_hash(path) != legacy_run["stages"][stage]["output_hash"]:
            raise SystemExit(f"legacy output hash mismatch: {stage}")
    extraction, tagging = migrate(
        json.loads(paths["case_extraction"].read_text(encoding="utf-8")),
        json.loads(paths["entity_tagging"].read_text(encoding="utf-8")),
        args.candidate_id,
    )
    outputs = {"case_extraction": extraction, "entity_tagging": tagging}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for stage, output in outputs.items():
        target = args.output_dir / f"{stage}.json"
        if target.exists():
            raise SystemExit(f"output already exists: {target}")
        output["migration_source_run_id"] = legacy_run["run_id"]
        output["migration_input_hash"] = file_hash(paths[stage])
        target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(target)


if __name__ == "__main__":
    main()
