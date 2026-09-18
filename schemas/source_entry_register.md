# Source Entry Register Schema

`source_entries` stores reproducible source segments extracted from one source.

It is the layer between `sources` and `cases`.

Rule:

```text
source_entry is not the same as case
```

A source entry can become:

```text
one case
multiple cases
no case
commentary only
index only
duplicate or parallel source material
```

## Core Fields

```text
source_entry_id
source_entry_key
source_id
parent_entry_id
source_title
volume
section
entry_title
entry_sequence
language
raw_text
raw_text_excerpt
raw_text_storage_scope
storage_class
storage_uri
normalized_storage_uri
source_artifact_uri
raw_capture_status
raw_text_hash
normalized_artifact_hash
source_artifact_hash
content_type
byte_size
source_url
locator_text
extraction_method
extractor_name
extractor_version
extraction_command
captured_at
access_date
boundary_status
boundary_confidence
entry_type
ai_case_candidate_count
linked_case_ids
review_status
notes
```

`raw_text_storage_scope` controls access to the text. `storage_class` says where it is retained. `raw_capture_status` says whether retained objects have passed integrity verification. These fields must not be collapsed into one status or into copyright status.

For modern copyrighted sources, a public or review-facing case pack may omit full `raw_text` and keep:

```text
raw_text: internal_capture_not_reproduced
raw_text_excerpt: short quote for verification
raw_text_storage_scope: internal
storage_class: local_restricted
normalized_storage_uri: data/source_entries/restricted/{source_id}/{source_entry_id}.normalized.json
source_artifact_uri: data/source_entries/restricted/{source_id}/{source_entry_id}.source.html
raw_capture_status: persisted_verified
raw_text_hash: hash of the full extracted entry
normalized_artifact_hash: hash of the complete normalized JSON file
source_artifact_hash: hash of the downloaded HTML, PDF, caption, audio, or video file
```

The extractor output or internal capture must still preserve the full entry for machine checking.

If the capture is no longer available, use:

```text
storage_class: missing
storage_uri:
raw_capture_status: missing
```

Do not use `internal_capture_not_reproduced` as evidence that a durable copy exists.

## ID Rules

```text
ENT000001
```

Rules:

1. `source_entry_id` is stable once assigned.
2. Rejected, non-case, and duplicate entries keep their IDs.
3. If the extractor changes and produces different boundaries, create new entries or mark old entries `needs_recheck`; do not silently rewrite history.
4. `source_entry_key` is extractor-facing and source-facing. It can include source, volume, section, title, and text hash.
5. `entry_sequence` records the order within a source or section. It is not a global ID.

## boundary_status

```text
script_extracted
ai_segmented
manual_segmented
machine_checked
human_checked
needs_recheck
rejected
```

## boundary_confidence

```text
high
medium
low
unknown
```

## entry_type

```text
single_case_candidate
multi_case_candidate
non_case_material
commentary
index_only
mixed
unknown
```

## Review Rules

Raw storage follows `../02-data-model/RAW_SOURCE_STORAGE.md`.

```text
public-domain or licensed text -> tracked_public
modern copyrighted text -> local_restricted or external_restricted
retention not permitted -> locator_only
unconfirmed historical pilot capture -> missing or pending_persistence
```

After persistence, split the entry into `source_segments`. Generated factual units and reader paragraphs should reference segment IDs.

1. Extraction scripts create `source_entries`; they should not decide final case truth or publishability.
2. AI may classify entry type and propose case candidates, but must keep the raw source entry unchanged.
3. `raw_text_hash` supports re-run checks and boundary drift detection.
4. A `citation` should point to `source_entry_id` when the case comes from a reproducible entry.
5. If one entry produces multiple cases, create multiple citations or case links that share the same `source_entry_id`.
6. If one case appears in multiple entries or sources, dedup review decides whether they share one canonical `case_id`.

## Minimum M2 Fields

For M2 pilot entries, capture at least:

```text
source_entry_id
source_entry_key
source_id
entry_title
raw_text
raw_text_hash
source_url
locator_text
extraction_method
extractor_name
extraction_command
access_date
boundary_status
boundary_confidence
entry_type
review_status
```
