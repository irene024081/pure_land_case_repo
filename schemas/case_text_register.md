# Case Text Register Schema

`case_texts` stores original evidence, readable renderings, summaries, translations, and creator-facing text.

Do not store long text directly in `cases`.

## Core Fields

```text
text_id
case_id
occurrence_id
text_type
language
content
content_depth
source_mode
created_by
generated_from_text_id
generated_from_source_entry_id
generated_from_segment_ids
generation_run_id
prompt_version
generation_status
review_status
fidelity_status
display_scope
publish_status
copyright_risk
search_weight
notes
```

`occurrence_id` identifies the source appearance underlying an original or source-derived text. Historical `citation_id` values require an explicit migration alias; see `../02-data-model/T02_V02_MIGRATION.md`. Derivative texts retain their `generated_from_*` lineage and rights decisions.

## text_type

```text
original_full
original_excerpt
evidence_locator
classical_to_modern_rendering
oral_record_cleanup
first_person_testimony_cleanup
long_article_summary
independent_factual_account
reader_summary
reader_rendering
creator_summary
search_digest
translation
editor_note
ai_note
```

`reader_rendering` is a full readable account when the source supports one. It should retain the material narrative sequence, actors, uncertainty, and important context. It is not limited to a short summary.

`reader_summary` is compressed search and preview text. Do not use it as a substitute for `reader_rendering`.

`independent_factual_account` reconstructs the supported event in independently organized language for modern rights-restricted sources. It preserves facts and attribution while avoiding distinctive expression and close structural substitution.

Expressive teaching articles belong in `dharma_case_commentaries`, not `case_texts`, because they combine case evidence with separate doctrinal sources.

## content_depth

```text
snippet
condensed
full_supported_account
extended
```

## generation_status

```text
current
needs_regeneration
superseded
failed_check
```

A faithful but over-compressed rendering uses `content_depth: condensed` and can be marked `needs_regeneration` without calling its factual fidelity invalid.

## source_mode

```text
verbatim
faithful_rendering
summary
translation
ai_assisted
human_editorial
locator
```

## fidelity_status

```text
not_checked
machine_checked
human_checked
needs_revision
rejected
```

## display_scope

```text
public
public_excerpt_only
internal
restricted
withheld
```

## publish_status

```text
internal
public
public_excerpt_only
withheld
retired
```

## Fidelity Rules

New generated outputs should use `generated_from_segment_ids` for paragraph-level traceability. Entry-level provenance remains required but is not precise enough for claim checking.

Allowed:

```text
clean repetition
add punctuation
improve readability
translate
clarify pronoun references when supported
```

Forbidden:

```text
add people
add place
add time
add miraculous details
add doctrinal explanation as case fact
merge separate cases
remove uncertainty
```
