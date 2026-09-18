# Doctrinal Citation Register Schema

`doctrinal_citations` stores the sources allowed to support doctrinal claims, quotations, and practice guidance.

## Core Fields

```text
doctrinal_citation_id
authority_type
tradition_or_lineage
author_or_speaker
work_or_talk_title
source_id
source_entry_id
source_segment_ids
canonical_locator
language
text_or_restricted_locator
translation_id
translator
quotation_verified
context_summary
supported_topics
scope_conditions
known_interpretive_limits
rights_review_id
public_quote_policy
review_status
reviewed_by
notes
```

## authority_type

```text
canonical_scripture
patriarchal_text
historical_commentary
lineage_standard
teacher_lecture
teacher_article
institutional_guidance
secondary_scholarship
```

`authority_type` records source type. It does not automatically resolve disagreements among traditions or teachers.

## Review Status

```text
candidate
text_verified
locator_verified
doctrinal_scope_reviewed
approved_for_generation
needs_recheck
rejected
```

Only `approved_for_generation` citations can support a public `dharma_case_commentary`.

## Rules

1. Preserve exact source, edition, page, section, paragraph, or timestamp.
2. Verify quotations against the retained source, not model memory or a search-result snippet.
3. Record conditions and context that limit the quoted teaching.
4. Attribute teacher-specific interpretation to the teacher and lineage context.
5. A case report cannot be registered as doctrinal authority merely because it contains religious language.
6. Translation is a separate text version and must identify its source and translator.
7. Rights policy controls public quotation even when internal doctrinal use is approved.
