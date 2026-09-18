# M0 Schema Lock

M0 freezes the MVP data shape before seed extraction starts. It does not implement a database yet.

The locked model must support:

1. Public reader search and case detail.
2. Creator theme-to-case recommendation.
3. Citation, provenance, and dedup review.
4. Future multilingual renderings.

## Locked ID Rules

```text
SRC0001      source
ENT000001    source entry
CASE000001   canonical case
CIT000001    citation
TXT000001    case text version
TAG0001      tag
PER0001      person
PLC0001      place
ORG0001      organization
DEDUP0001    dedup group
```

Rules:

1. IDs are stable and never reused.
2. Deleted or rejected records keep their ID with status notes.
3. A public page should use `case_id`, not citation ID, as the primary route.

## Locked MVP Tables

```text
sources
source_entries
cases
citations
case_texts
tags
case_tags
creator_metadata
persons
places
case_persons
case_places
dedup_groups
dedup_members
```

`source_entries` was added before M2 scaling because extraction must be reproducible. `organizations` and `provenance_links` are expected later, but M0 can represent them through `sources`, `citations`, and notes.

## Source Entry Boundary

`source_entries` are reproducible segments from a source. They are not final cases.

Rules:

```text
source extractor scripts create source_entries
AI extraction jobs read source_entries
machine check validates the AI output
cases are created only after entry classification and normalization
```

One source entry can produce zero, one, or many cases. One case can cite multiple source entries across different sources.

## Confirmed Decisions

### Unknown People

Unknown or anonymized persons are allowed.

Examples:

```text
unknown_person
某居士
某妇人
anonymous_with_descriptor
```

Use `privacy_level` and `anonymity_level` to distinguish unknown, anonymized, and intentionally redacted records.

### One Source Segment, Multiple Cases

One article, chapter, letter, or video can produce multiple `case_id` records.

The same source segment may map to multiple `citation_id` records or one shared citation with different locators.

### One Case, Multiple Citations

The same canonical case can appear in multiple sources.

Examples:

```text
ancient compilation
modern retelling
website repost
YouTube lecture
translation
```

All are recorded as separate `citation_id` records under one `case_id` when confirmed.

## Dedup And Same-case Rules

AI can identify possible duplicates and assign confidence. AI should not silently merge canonical cases.

Dedup statuses:

```text
not_checked
not_duplicate
possible_same_case
same_case
merged
needs_review
```

### Named vs Unknown Person

If one version names the person and another says "某居士" or unknown, do not auto-merge.

Use:

```text
dedup_status = possible_same_case
duplicate_confidence = high | medium | low
```

A record can become `same_case` only when enough evidence aligns:

```text
event sequence
place
time or period
key signs
witnesses or family structure
source chain
distinctive wording
```

If only the motif is similar, keep separate cases.

### Canonical Case Selection

When multiple citations describe the same case, choose the canonical case record by:

1. Earliest verifiable source.
2. Most complete factual record.
3. Lowest privacy and copyright risk for public display.
4. Clearest citation locator.

The canonical case can still display later citations as parallel or derivative sources.

## Evidence And Provenance

Use two separate concepts:

```text
provenance_quality = quality of source chain
evidence_level = strength of case facts
```

## Review And Publish Status

Processing status and public display status are separate.

```text
review_status:
candidate
extracted
normalized
source_checked
machine_checked
human_reviewed
ready_to_publish
needs_recheck
rejected
```

```text
publish_status:
internal
public
public_excerpt_only
withheld
retired
```

A case can be well reviewed but withheld from public display because of copyright, privacy, or uncertainty.

## Reader Rendering Review

`reader_rendering` can be public after `machine_checked`.

Future human review is supported:

```text
fidelity_status:
not_checked
machine_checked
human_checked
needs_revision
rejected
```

If later review finds a problem, set the text version to `needs_revision` or `withheld` without deleting the underlying case.

## Copyright Boundary

Modern copyrighted materials should not be publicly displayed in full unless rights are clear.

Default:

```text
original_evidence = internal or public_excerpt_only
reader_rendering = public if faithful and checked
source locator = public
```

## Privacy Boundary

Privacy is preserved even if current MVP does not use all privacy features.

```text
privacy_level:
public
name_redacted
sensitive
private_internal
unknown
```

## Tag Boundary

Case type, rebirth sign, and teaching theme are separate.

```text
case_type = assisted_chanting
rebirth_sign = fragrance
teaching_theme = family_support_at_death
```

The taxonomy can grow as seed cases reveal new patterns.

## Date And Place Boundary

Unknown dates are allowed.

```text
period = Tang
event_year = unknown
date_precision = dynasty
```

M0 allows free-text `region`, while `places` can progressively normalize important locations.

## Multilingual Boundary

M0 only locks multilingual structure.

It does not require the seed dataset to contain many multilingual cases.

Translations are stored as `case_texts` with:

```text
text_type = translation
language = en | ja | ko | vi | ...
generated_from_text_id
fidelity_status
```

Translations are not original evidence.

## M0 Exit Criteria

M0 is complete when one sample case can be represented with:

```text
source row
case row
citation row
original evidence or locator
reader rendering
tags
creator metadata
dedup status
review status
publish status
```
