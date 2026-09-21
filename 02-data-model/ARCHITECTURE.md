# Data Architecture

## Core Boundaries

```text
Source != Source Item != Source Entry != Source Occurrence != Case != Text Version
```

- `Source` is a collection, publication, site, channel, book, or archive.
- `Source Item` is one inventoried article, book entry, video, or letter. Its current catalog column is `article_id`. It may contain zero, one, or many cases.
- `Source Entry` is the retained normalized evidence object for a Source Item.
- `Source Occurrence` is one Case appearing at a specific location in a Source Item, backed by retained Source Segments. Transmission links connect Occurrences.
- `Case` is one underlying narrated episode, with one or more Source Occurrences; the record does not assert historical truth.
- `Text Version` is an original excerpt, faithful rendering, summary, translation, or creator-facing derivative.

## Processing Layers

```text
source profile
-> inventory sync
-> source capture and manifest verification
-> Article Run: segmentation and case detection
-> Candidate Runs: facts, entities, dedup
-> resolve identity and assign or reuse Case ID
-> Source Occurrence, reader text, creator analysis
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
data/migrations/            proposed mappings for review, not canonical data
data/legacy_m2/             historical review fixtures, not canonical records
```

## Authority

Domain field definitions live in `../schemas/`. The current executable stage order lives in `../pipeline/pipeline.v2.json`; historical Runs retain their recorded definition version. Field-level migration rules live in `T02_V02_MIGRATION.md`. This document defines relationships and ownership boundaries and must not duplicate complete field lists.

## Publication Rule

Public output requires both factual and rights gates to pass. Case facts describe what a source states; they do not declare an event historically true. Doctrinal commentary is a later workflow that also requires approved doctrinal citations and claim-level verification.
