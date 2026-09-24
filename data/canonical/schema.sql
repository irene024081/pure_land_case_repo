-- Canonical store schema v1 for the Pure Land case dataset.
--
-- Dialect note: this DDL is deliberately portable. It runs unchanged on
-- SQLite (the current local backend, scripts/canonical_store.py) and on
-- Postgres (the D10 production target): TEXT primary keys, JSON payloads as
-- TEXT, no engine-specific column types. The storage layer is the only
-- component that knows which engine is underneath.
--
-- Historical addressability: case_id values are the CASE###### IDs already
-- used by v0.1 baselines and v0.2 runs (e.g. CASE000001). fact IDs keep
-- their run-scoped form ({candidate_id}-FACT####) so v0.1 references such as
-- CASE000001-FACT0001 remain resolvable through the origin_run_id.

CREATE TABLE IF NOT EXISTS schema_migrations (
    version         INTEGER PRIMARY KEY,
    applied_at      TEXT NOT NULL
);

-- One row per resolved case (narrated episode). The row tracks which run
-- last supplied its content; history of earlier promotions is in
-- promotion_log.
CREATE TABLE IF NOT EXISTS cases (
    case_id             TEXT PRIMARY KEY,
    title               TEXT NOT NULL,
    status              TEXT NOT NULL,          -- active | merged | withdrawn
    publish_status      TEXT NOT NULL,          -- publication_packaging.publish_status
    origin_run_id       TEXT NOT NULL,          -- case run that supplied current content
    origin_run_updated_at TEXT NOT NULL,        -- updated_at of that run (supersede check)
    pipeline_version    TEXT NOT NULL,
    source_entry_hash   TEXT NOT NULL,
    promoted_at         TEXT NOT NULL
);

-- Atomic facts. Primary key is the run-scoped fact ID; it is stable because
-- fact IDs are never reused across runs for a different proposition.
CREATE TABLE IF NOT EXISTS case_facts (
    case_fact_id        TEXT PRIMARY KEY,
    case_id             TEXT NOT NULL REFERENCES cases(case_id),
    proposition_text    TEXT NOT NULL,
    fact_type           TEXT NOT NULL,
    claim_mode          TEXT NOT NULL,
    uncertainty         TEXT NOT NULL,
    supporting_source_segment_ids TEXT NOT NULL,  -- JSON array of segment IDs
    review_status       TEXT NOT NULL
);

-- Persons and places extracted by entity_tagging. entity_id is run-scoped
-- (PER0001, PLC0001), so the primary key includes the case.
CREATE TABLE IF NOT EXISTS entities (
    case_id             TEXT NOT NULL REFERENCES cases(case_id),
    entity_kind         TEXT NOT NULL,          -- person | place
    entity_id           TEXT NOT NULL,
    display_name        TEXT NOT NULL,
    source_name         TEXT NOT NULL,
    name_status         TEXT,                   -- persons only
    roles               TEXT,                   -- JSON array, persons only
    place_type          TEXT,                   -- places only
    notes               TEXT,
    supporting_source_segment_ids TEXT NOT NULL,
    PRIMARY KEY (case_id, entity_kind, entity_id)
);

-- Search tags from entity_tagging.
CREATE TABLE IF NOT EXISTS case_tags (
    case_id             TEXT NOT NULL REFERENCES cases(case_id),
    tag                 TEXT NOT NULL,
    tag_class           TEXT NOT NULL,
    status              TEXT,
    supporting_case_fact_ids TEXT NOT NULL,     -- JSON array
    PRIMARY KEY (case_id, tag)
);

-- One case appearing in one source entry.
CREATE TABLE IF NOT EXISTS source_occurrences (
    occurrence_id       TEXT PRIMARY KEY,
    case_id             TEXT NOT NULL REFERENCES cases(case_id),
    source_id           TEXT NOT NULL,
    source_item_id      TEXT NOT NULL,
    source_entry_id     TEXT NOT NULL,
    supporting_source_segment_ids TEXT NOT NULL,
    locator             TEXT NOT NULL,          -- JSON object
    languages           TEXT NOT NULL,          -- JSON array
    content_form        TEXT NOT NULL,
    voice               TEXT NOT NULL,
    parent_links        TEXT NOT NULL,          -- JSON array
    review_status       TEXT NOT NULL
);

-- Generated reader-facing text versions.
CREATE TABLE IF NOT EXISTS text_versions (
    text_version_id     TEXT PRIMARY KEY,       -- {case_id}:{kind}:{ordinal}
    case_id             TEXT NOT NULL REFERENCES cases(case_id),
    kind                TEXT NOT NULL,          -- reader_title | reader_paragraph | reader_summary
    content             TEXT NOT NULL,
    supporting_case_fact_ids TEXT,              -- JSON array, paragraphs only
    supporting_source_segment_ids TEXT,         -- JSON array, paragraphs only
    origin_run_id       TEXT NOT NULL
);

-- Identity resolution audit trail, one row per resolved candidate.
CREATE TABLE IF NOT EXISTS identity_decisions (
    candidate_id        TEXT PRIMARY KEY,
    case_id             TEXT NOT NULL REFERENCES cases(case_id),
    resolution_kind     TEXT NOT NULL,          -- new | reuse
    decision_basis      TEXT NOT NULL,          -- scoped_no_match | human_review
    reviewer_id         TEXT,                   -- set for human_review
    reason              TEXT,
    dedup_scope         TEXT NOT NULL,
    decided_in_run_id   TEXT NOT NULL,
    decided_at          TEXT NOT NULL
);

-- Rights gate outcome per promoted case.
CREATE TABLE IF NOT EXISTS rights_decisions (
    case_id             TEXT NOT NULL REFERENCES cases(case_id),
    rights_review_id    TEXT NOT NULL,
    gate_result         TEXT NOT NULL,
    allowed_display_scope TEXT NOT NULL,
    checks              TEXT NOT NULL,          -- JSON array
    decided_in_run_id   TEXT NOT NULL,
    decided_at          TEXT NOT NULL,
    PRIMARY KEY (case_id, decided_in_run_id)
);

-- Persistent dedup index: the exact-normalized feature sets that
-- pipeline/retrieval/dedup_candidates.v2.json scores on (persons, places,
-- dates, tags), rebuilt from case_facts + entities at promotion time.
-- This replaces directory scanning for completed local runs.
CREATE TABLE IF NOT EXISTS dedup_index (
    case_id             TEXT PRIMARY KEY REFERENCES cases(case_id),
    persons             TEXT NOT NULL,          -- JSON array of normalized strings
    places              TEXT NOT NULL,
    dates               TEXT NOT NULL,
    tags                TEXT NOT NULL,          -- JSON object tag -> tag_class
    source_id           TEXT NOT NULL,
    source_entry_id     TEXT NOT NULL,
    external_processing TEXT NOT NULL,
    updated_at          TEXT NOT NULL
);

-- Promotion audit log. Idempotency key: run_id + package_fingerprint.
CREATE TABLE IF NOT EXISTS promotion_log (
    run_id              TEXT NOT NULL,
    package_fingerprint TEXT NOT NULL,
    case_id             TEXT NOT NULL REFERENCES cases(case_id),
    action              TEXT NOT NULL,          -- inserted | replaced | skipped
    promoted_at         TEXT NOT NULL,
    PRIMARY KEY (run_id, package_fingerprint)
);
