# Data Processing Workflow

The executable workflow is `../pipeline/pipeline.v1.json`.

## 1. Source Profile

Register the Source, complete its rights review, and select two adapters:

- inventory adapter discovers item metadata;
- entry adapter captures and normalizes one selected item.

Use a generic adapter when possible. Add Source-specific code only when the generic adapters cannot express the boundary.

## 2. Inventory Sync

Write every discovered item to `data/source_catalogs/{source_id}/articles.csv`. Preserve excluded, inaccessible, duplicate, and non-case items so coverage can be audited.

```text
fixed source: initial full backfill -> rerun on edition or extractor change
active source: initial full backfill -> scheduled incremental refresh
unstable source: incremental refresh -> boundary anomaly review
```

AI may classify items and estimate case likelihood. Scripts own discovery completeness, stable keys, deduplication by exact identifiers, and CSV persistence.

## 3. Capture

Selected items become normalized Source Entries. Verify raw text and artifact hashes against tracked manifests. Rights policy decides storage and whether an external AI provider may receive full text.

## 4. Article Run

Segment the complete Source Entry without gaps or overlap, then detect zero or more case candidates. The system assigns Case IDs only after detection.

## 5. Case Runs

Each candidate receives an independent run for atomic facts, entities, tags, deduplication, reader text, creator analysis, factual checking, rights checking, and publication packaging.

## 6. Review

Machine checks are required. Human review remains optional for routine low-risk runs and required for ambiguous deduplication, new baseline approval, doctrinal interpretation, privacy escalation, or rights overrides.

## Stop Conditions

Stop when evidence boundaries are unclear, required content is missing, rights policy blocks the intended processing, duplicate identity is ambiguous, or any generated factual claim lacks support.
