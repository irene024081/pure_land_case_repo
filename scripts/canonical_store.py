#!/usr/bin/env python3
"""Canonical store access layer (SQLite backend, Postgres-ready schema).

The store is the promoted, queryable dataset built from accepted pipeline
run outputs. It can be rebuilt at any time by re-promoting completed runs.
Only this module knows which database engine is underneath; the DDL in
data/canonical/schema.sql stays portable.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT / "data" / "canonical" / "canonical.db"
SCHEMA_PATH = ROOT / "data" / "canonical" / "schema.sql"
SCHEMA_VERSION = 1


def connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA foreign_keys = ON")
    apply_schema(conn)
    return conn


def apply_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.execute(
        "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, datetime('now'))",
        (SCHEMA_VERSION,),
    )
    conn.commit()


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def get_case(conn: sqlite3.Connection, case_id: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
    if row is None:
        return None
    columns = [item[0] for item in conn.execute("SELECT * FROM cases LIMIT 0").description]
    return dict(zip(columns, row))


def promotion_record(conn: sqlite3.Connection, run_id: str, fingerprint: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM promotion_log WHERE run_id = ? AND package_fingerprint = ?",
        (run_id, fingerprint),
    ).fetchone()
    if row is None:
        return None
    columns = [item[0] for item in conn.execute("SELECT * FROM promotion_log LIMIT 0").description]
    return dict(zip(columns, row))


def replace_case_content(conn: sqlite3.Connection, bundle: dict[str, Any]) -> str:
    """Insert or replace one case bundle. Returns 'inserted' or 'replaced'.

    The caller has already done eligibility and supersede checks. The bundle
    keys map one-to-one onto the schema tables.
    """
    case = bundle["case"]
    existing = get_case(conn, case["case_id"])
    action = "replaced" if existing else "inserted"
    with conn:
        if existing:
            for table in (
                "case_facts", "entities", "case_tags", "source_occurrences",
                "text_versions", "rights_decisions", "dedup_index",
            ):
                conn.execute(f"DELETE FROM {table} WHERE case_id = ?", (case["case_id"],))
            conn.execute(
                "DELETE FROM identity_decisions WHERE case_id = ?", (case["case_id"],)
            )
            conn.execute("DELETE FROM cases WHERE case_id = ?", (case["case_id"],))
        conn.execute(
            "INSERT INTO cases (case_id, title, status, publish_status, origin_run_id,"
            " origin_run_updated_at, pipeline_version, source_entry_hash, promoted_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                case["case_id"], case["title"], case["status"], case["publish_status"],
                case["origin_run_id"], case["origin_run_updated_at"], case["pipeline_version"],
                case["source_entry_hash"], case["promoted_at"],
            ),
        )
        for fact in bundle["facts"]:
            conn.execute(
                "INSERT INTO case_facts (case_fact_id, case_id, proposition_text, fact_type,"
                " claim_mode, uncertainty, supporting_source_segment_ids, review_status)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    fact["case_fact_id"], case["case_id"], fact["proposition_text"],
                    fact["fact_type"], fact["claim_mode"], fact["uncertainty"],
                    dumps(fact["supporting_source_segment_ids"]), fact.get("review_status", ""),
                ),
            )
        for entity in bundle["entities"]:
            conn.execute(
                "INSERT INTO entities (case_id, entity_kind, entity_id, display_name, source_name,"
                " name_status, roles, place_type, notes, supporting_source_segment_ids)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    case["case_id"], entity["entity_kind"], entity["entity_id"],
                    entity["display_name"], entity["source_name"], entity.get("name_status"),
                    dumps(entity.get("roles")) if entity.get("roles") is not None else None,
                    entity.get("place_type"), entity.get("notes"),
                    dumps(entity["supporting_source_segment_ids"]),
                ),
            )
        for tag in bundle["tags"]:
            conn.execute(
                "INSERT INTO case_tags (case_id, tag, tag_class, status, supporting_case_fact_ids)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    case["case_id"], tag["tag"], tag["tag_class"], tag.get("status"),
                    dumps(tag["supporting_case_fact_ids"]),
                ),
            )
        for occurrence in bundle["occurrences"]:
            conn.execute(
                "INSERT INTO source_occurrences (occurrence_id, case_id, source_id, source_item_id,"
                " source_entry_id, supporting_source_segment_ids, locator, languages, content_form,"
                " voice, parent_links, review_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    occurrence["occurrence_id"], case["case_id"], occurrence["source_id"],
                    occurrence["source_item_id"], occurrence["source_entry_id"],
                    dumps(occurrence["supporting_source_segment_ids"]), dumps(occurrence["locator"]),
                    dumps(occurrence["languages"]), occurrence["content_form"], occurrence["voice"],
                    dumps(occurrence["parent_links"]), occurrence["review_status"],
                ),
            )
        for text in bundle["text_versions"]:
            conn.execute(
                "INSERT INTO text_versions (text_version_id, case_id, kind, content,"
                " supporting_case_fact_ids, supporting_source_segment_ids, origin_run_id)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    text["text_version_id"], case["case_id"], text["kind"], text["content"],
                    dumps(text["supporting_case_fact_ids"]) if text.get("supporting_case_fact_ids") else None,
                    dumps(text["supporting_source_segment_ids"]) if text.get("supporting_source_segment_ids") else None,
                    text["origin_run_id"],
                ),
            )
        for decision in bundle["identity_decisions"]:
            conn.execute(
                "INSERT INTO identity_decisions (candidate_id, case_id, resolution_kind,"
                " decision_basis, reviewer_id, reason, dedup_scope, decided_in_run_id, decided_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    decision["candidate_id"], case["case_id"], decision["resolution_kind"],
                    decision["decision_basis"], decision.get("reviewer_id"), decision.get("reason"),
                    decision["dedup_scope"], decision["decided_in_run_id"], decision["decided_at"],
                ),
            )
        for decision in bundle["rights_decisions"]:
            conn.execute(
                "INSERT INTO rights_decisions (case_id, rights_review_id, gate_result,"
                " allowed_display_scope, checks, decided_in_run_id, decided_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    case["case_id"], decision["rights_review_id"], decision["gate_result"],
                    decision["allowed_display_scope"], dumps(decision["checks"]),
                    decision["decided_in_run_id"], decision["decided_at"],
                ),
            )
        index = bundle["dedup_index"]
        conn.execute(
            "INSERT INTO dedup_index (case_id, persons, places, dates, tags, source_id,"
            " source_entry_id, external_processing, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                case["case_id"], dumps(index["persons"]), dumps(index["places"]),
                dumps(index["dates"]), dumps(index["tags"]), index["source_id"],
                index["source_entry_id"], index["external_processing"], index["updated_at"],
            ),
        )
        conn.execute(
            "INSERT INTO promotion_log (run_id, package_fingerprint, case_id, action, promoted_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                bundle["run_id"], bundle["package_fingerprint"], case["case_id"],
                action, case["promoted_at"],
            ),
        )
    return action


def list_cases(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    columns = [item[0] for item in conn.execute("SELECT * FROM cases LIMIT 0").description]
    rows = conn.execute("SELECT * FROM cases ORDER BY case_id").fetchall()
    return [dict(zip(columns, row)) for row in rows]


def dedup_index_rows(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Dedup candidates in the shape dedup_candidates/v2 scoring consumes."""
    rows = conn.execute("SELECT * FROM dedup_index ORDER BY case_id").fetchall()
    result = []
    for (case_id, persons, places, dates, tags, source_id, source_entry_id,
         external_processing, updated_at) in rows:
        result.append({
            "candidate_case_id": case_id,
            "source_id": source_id,
            "source_entry_id": source_entry_id,
            "external_processing": external_processing,
            "persons": json.loads(persons),
            "places": json.loads(places),
            "dates": json.loads(dates),
            "tags": json.loads(tags),
            "updated_at": updated_at,
        })
    return result
