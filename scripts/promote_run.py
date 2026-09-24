#!/usr/bin/env python3
"""Promote accepted pipeline case runs into the canonical store.

Usage:
    python3 scripts/promote_run.py promote --run-dir <case-run-dir>
    python3 scripts/promote_run.py promote --all
    python3 scripts/promote_run.py status
    python3 scripts/promote_run.py verify

Promotion is idempotent: re-promoting a run whose outputs are unchanged is a
no-op. Runs that are not completed, lack a publication package, or are
superseded by a newer promoted run for the same case are rejected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import canonical_store  # noqa: E402
from render_case_report import completed_case_runs  # noqa: E402
from run_pipeline import dedup_features  # noqa: E402

RUNS_ROOT = SCRIPTS_DIR.parent / "data" / "pipeline_runs"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def package_fingerprint(run: dict[str, Any]) -> str:
    parts = [f"{stage}:{state.get('output_hash', '')}" for stage, state in sorted(run["stages"].items())]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def require_output(run_dir: Path, stage: str) -> dict[str, Any]:
    path = run_dir / "outputs" / f"{stage}.json"
    if not path.exists():
        raise SystemExit(f"missing required output: {stage} in {run_dir}")
    return load_json(path)


def build_bundle(run_dir: Path) -> dict[str, Any]:
    """Load and cross-validate one completed case run into a promotion bundle."""
    run = load_json(run_dir / "run.json")
    if run.get("run_kind") != "case":
        raise SystemExit(f"not a case run: {run_dir}")
    if run.get("status") != "completed":
        raise SystemExit(f"run is not completed (status={run.get('status')}): {run['run_id']}")
    for stage_id, state in run["stages"].items():
        if state["status"] != "completed":
            raise SystemExit(f"stage {stage_id} is not completed in {run['run_id']}")

    case_id = run.get("case_id", "")
    if not case_id:
        raise SystemExit(f"run has no case_id: {run['run_id']}")

    extraction = require_output(run_dir, "case_extraction")
    tagging = require_output(run_dir, "entity_tagging")
    resolution = require_output(run_dir, "case_resolution")
    occurrence = require_output(run_dir, "source_occurrence")
    reader = require_output(run_dir, "reader_generation")
    creator = require_output(run_dir, "creator_analysis")
    factual = require_output(run_dir, "factual_check")
    rights = require_output(run_dir, "rights_check")
    packaging = require_output(run_dir, "publication_packaging")
    segmentation = require_output(Path(run["parent_article_run_path"]), "source_segmentation")

    segment_ids = {segment["segment_id"] for segment in segmentation["segments"]}
    fact_ids = {fact["case_fact_id"] for fact in extraction["case_facts"]}

    def check_refs(owner: str, refs: list[str], valid: set[str]) -> None:
        missing = sorted(set(refs) - valid)
        if missing:
            raise SystemExit(f"{owner} references unknown IDs: {missing}")

    # Reference integrity: facts -> segments, tags -> facts, entities -> segments,
    # occurrence -> entry and segments, generated outputs -> facts and segments.
    for fact in extraction["case_facts"]:
        check_refs(fact["case_fact_id"], fact["supporting_source_segment_ids"], segment_ids)
    for group in ("persons", "places"):
        for entity in tagging[group]:
            check_refs(entity["entity_id"], entity["supporting_source_segment_ids"], segment_ids)
    for tag in tagging["tags"]:
        check_refs(tag["tag"], tag["supporting_case_fact_ids"], fact_ids)
    if occurrence["case_id"] != case_id or occurrence["source_entry_id"] != run["source_entry_id"]:
        raise SystemExit("source_occurrence does not match the run's case or entry")
    check_refs(occurrence["occurrence_id"], occurrence["supporting_source_segment_ids"], segment_ids)
    if resolution["case_id"] != case_id or resolution["candidate_id"] != run["candidate_id"]:
        raise SystemExit("case_resolution does not match the run identity")
    if reader.get("case_id") != case_id or creator.get("case_id") != case_id:
        raise SystemExit("generated output case_id mismatch")
    for paragraph in reader["paragraphs"]:
        check_refs(paragraph["paragraph_id"], paragraph["supporting_case_fact_ids"], fact_ids)
        check_refs(paragraph["paragraph_id"], paragraph["supporting_source_segment_ids"], segment_ids)
    for angle in creator["interpretation_angles"]:
        check_refs(angle["angle_id"], angle["supporting_case_fact_ids"], fact_ids)
        check_refs(angle["angle_id"], angle["supporting_source_segment_ids"], segment_ids)
    for claim in factual["claims"]:
        check_refs(claim["claim_id"], claim["supporting_case_fact_ids"], fact_ids)
        check_refs(claim["claim_id"], claim["supporting_source_segment_ids"], segment_ids)
    if rights["rights_review_id"] != run["rights_review_id"]:
        raise SystemExit("rights_check rights_review_id mismatch")
    if packaging["case_id"] != case_id:
        raise SystemExit("publication_packaging case_id mismatch")

    features = dedup_features(extraction, tagging)
    text_versions = [
        {
            "text_version_id": f"{case_id}:reader_title:1",
            "kind": "reader_title",
            "content": reader["reader_title"],
            "origin_run_id": run["run_id"],
        },
        {
            "text_version_id": f"{case_id}:reader_summary:1",
            "kind": "reader_summary",
            "content": reader["reader_summary"],
            "origin_run_id": run["run_id"],
        },
    ]
    for index, paragraph in enumerate(reader["paragraphs"], 1):
        text_versions.append({
            "text_version_id": f"{case_id}:reader_paragraph:{index}",
            "kind": "reader_paragraph",
            "content": paragraph["content"],
            "supporting_case_fact_ids": paragraph["supporting_case_fact_ids"],
            "supporting_source_segment_ids": paragraph["supporting_source_segment_ids"],
            "origin_run_id": run["run_id"],
        })

    now = utc_now()
    return {
        "run_id": run["run_id"],
        "package_fingerprint": package_fingerprint(run),
        "case": {
            "case_id": case_id,
            "title": reader["reader_title"],
            "status": "active",
            "publish_status": packaging["publish_status"],
            "origin_run_id": run["run_id"],
            "origin_run_updated_at": run["updated_at"],
            "pipeline_version": run["pipeline_version"],
            "source_entry_hash": run["source_entry_hash"],
            "promoted_at": now,
        },
        "facts": extraction["case_facts"],
        "entities": [
            {**entity, "entity_kind": kind}
            for kind, group in (("person", "persons"), ("place", "places"))
            for entity in tagging[group]
        ],
        "tags": tagging["tags"],
        "occurrences": [occurrence],
        "text_versions": text_versions,
        "identity_decisions": [
            {
                "candidate_id": resolution["candidate_id"],
                "resolution_kind": resolution["resolution_kind"],
                "decision_basis": resolution["decision_basis"],
                "reviewer_id": resolution.get("reviewer_id"),
                "reason": resolution.get("reason"),
                "dedup_scope": resolution["dedup_scope"],
                "decided_in_run_id": run["run_id"],
                "decided_at": run["stages"]["case_resolution"]["completed_at"],
            }
        ],
        "rights_decisions": [
            {
                "rights_review_id": rights["rights_review_id"],
                "gate_result": rights["gate_result"],
                "allowed_display_scope": rights["allowed_display_scope"],
                "checks": rights["checks"],
                "decided_in_run_id": run["run_id"],
                "decided_at": run["stages"]["rights_check"]["completed_at"],
            }
        ],
        "dedup_index": {
            "persons": sorted(features["persons"]),
            "places": sorted(features["places"]),
            "dates": sorted(features["dates"]),
            "tags": features["tags"],
            "source_id": run["source_id"],
            "source_entry_id": run["source_entry_id"],
            "external_processing": run.get("external_processing", "blocked"),
            "updated_at": run["updated_at"],
        },
    }


def promote_one(conn, run_dir: Path) -> str:
    bundle = build_bundle(run_dir)
    case = bundle["case"]
    existing_record = canonical_store.promotion_record(conn, bundle["run_id"], bundle["package_fingerprint"])
    if existing_record:
        return f"skipped (already promoted, unchanged): {bundle['run_id']}"
    existing = canonical_store.get_case(conn, case["case_id"])
    if existing and existing["origin_run_updated_at"] > case["origin_run_updated_at"]:
        raise SystemExit(
            f"rejected: {bundle['run_id']} is superseded by newer promoted run "
            f"{existing['origin_run_id']} for {case['case_id']}"
        )
    action = canonical_store.replace_case_content(conn, bundle)
    return f"{action}: {case['case_id']} from {bundle['run_id']}"


def cmd_promote(args: argparse.Namespace) -> int:
    conn = canonical_store.connect(args.db)
    if args.all:
        run_dirs = list(completed_case_runs(RUNS_ROOT).values())
    else:
        run_dirs = [args.run_dir.resolve()]
    for run_dir in run_dirs:
        print(promote_one(conn, run_dir))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    conn = canonical_store.connect(args.db)
    cases = canonical_store.list_cases(conn)
    print(f"canonical cases: {len(cases)}")
    for case in cases:
        facts = conn.execute("SELECT COUNT(*) FROM case_facts WHERE case_id = ?", (case["case_id"],)).fetchone()[0]
        print(f"  {case['case_id']}  {case['publish_status']:<10} facts={facts:<3} {case['title']}  ({case['origin_run_id']})")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Rebuild-check: canonical content must match the origin run outputs."""
    conn = canonical_store.connect(args.db)
    problems: list[str] = []
    for case in canonical_store.list_cases(conn):
        case_id = case["case_id"]
        promoted = conn.execute(
            "SELECT package_fingerprint FROM promotion_log WHERE run_id = ? ORDER BY promoted_at DESC LIMIT 1",
            (case["origin_run_id"],),
        ).fetchone()
        run_dir = find_run_dir(case["origin_run_id"])
        if run_dir is None:
            problems.append(f"{case_id}: origin run directory missing: {case['origin_run_id']}")
            continue
        run = load_json(run_dir / "run.json")
        if promoted is None or package_fingerprint(run) != promoted[0]:
            problems.append(f"{case_id}: run outputs changed since promotion")
            continue
        extraction = load_json(run_dir / "outputs" / "case_extraction.json")
        stored = conn.execute(
            "SELECT COUNT(*) FROM case_facts WHERE case_id = ?", (case_id,)
        ).fetchone()[0]
        if stored != len(extraction["case_facts"]):
            problems.append(f"{case_id}: stored fact count {stored} != run output {len(extraction['case_facts'])}")
        occurrence_count = conn.execute(
            "SELECT COUNT(*) FROM source_occurrences WHERE case_id = ?", (case_id,)
        ).fetchone()[0]
        if occurrence_count < 1:
            problems.append(f"{case_id}: no source occurrence stored")
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        return 1
    print(f"verify OK: {len(canonical_store.list_cases(conn))} cases consistent with origin runs")
    return 0


def find_run_dir(run_id: str) -> Path | None:
    for pattern in ("*/candidates/*/run.json", "*/cases/*/run.json"):
        for path in RUNS_ROOT.glob(pattern):
            if load_json(path).get("run_id") == run_id:
                return path.parent
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=canonical_store.DEFAULT_DB_PATH)
    commands = parser.add_subparsers(dest="command", required=True)
    promote = commands.add_parser("promote")
    target = promote.add_mutually_exclusive_group(required=True)
    target.add_argument("--run-dir", type=Path)
    target.add_argument("--all", action="store_true")
    promote.set_defaults(handler=cmd_promote)
    commands.add_parser("status").set_defaults(handler=cmd_status)
    commands.add_parser("verify").set_defaults(handler=cmd_verify)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
