# Data Architecture

## Core Boundaries

```text
Source != Article != Source Entry != Case != Text Version
```

- `Source` is a collection, publication, site, channel, book, or archive.
- `Article` is one inventoried item in a Source. It may contain zero, one, or many cases.
- `Source Entry` is the retained normalized evidence object for an Article.
- `Case` is one normalized event record supported by one or more Source Entries.
- `Text Version` is an original excerpt, faithful rendering, summary, translation, or creator-facing derivative.

## Processing Layers

```text
source profile
-> inventory sync
-> source capture and manifest verification
-> Article Run: segmentation and case detection
-> assign stable Case IDs
-> Case Runs: facts, entities, dedup, reader text, creator analysis
-> independent factual and rights checks
-> publication package
```

Source profiling chooses inventory and entry adapters. Initial inventory backfill is normally one-time. Active sources then use incremental refresh; fixed books and historical collections rerun only when the edition, extractor, or source hash changes.

## Storage

```text
data/source_catalogs/       tracked source inventories and admin status
data/source_entries/public/ tracked public-domain or licensed normalized evidence
data/source_entries/restricted/ local restricted evidence, ignored by Git
data/source_entries/manifests/ tracked integrity and storage metadata
data/pipeline_runs/         local requests, responses, and restricted payloads
data/run_records/           tracked sanitized run provenance
data/legacy_m2/             historical review fixtures, not canonical records
```

## Authority

Domain field definitions live in `../schemas/`. Executable stage order lives in `../pipeline/pipeline.v1.json`. This document defines relationships and ownership boundaries and must not duplicate complete field lists.

## Publication Rule

Public output requires both factual and rights gates to pass. Case facts describe what a source states; they do not declare an event historically true. Doctrinal commentary is a later workflow that also requires approved doctrinal citations and claim-level verification.
