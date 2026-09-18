# Source Segment Register Schema

`source_segments` provides paragraph-level or timestamp-level traceability inside a source entry.

## Core Fields

```text
segment_id
source_entry_id
segment_version
sequence
segment_type
language
start_locator
end_locator
content
content_hash
speaker_or_author
claim_mode
display_scope
review_status
notes
```

## segment_type

```text
title
narrative
dialogue
witness_report
dream_report
author_inference
teacher_commentary
scriptural_quotation
editorial_note
translation
other
```

## claim_mode

```text
direct_observation
first_person_recollection
named_witness_report
anonymous_witness_report
hearsay
dream_or_vision
author_inference
doctrinal_interpretation
unknown
not_applicable
```

## Rules

1. Preserve source order through `sequence`.
2. Do not rewrite `content`; readability changes belong in `case_texts`.
3. A source paragraph may become one segment or several segments when claim modes differ materially.
4. Every factual unit, reader rendering paragraph, and interpretation angle should cite `segment_id` values.
5. For copyrighted material, segment content can remain in restricted storage while the tracked register retains hashes and locators.
