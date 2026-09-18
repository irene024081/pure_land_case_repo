# M0 Schema Sample

This file is a structural sample only. It is not a real case and must not be imported into the seed dataset.

Purpose: verify that one case can move through the locked M0 schema without missing critical fields.

## Source Row

```text
source_id: SRC_SAMPLE
name: Sample Source
language: zh-Hans
country_or_region: Sample Region
source_type: website
access_status: online_open
update_status: inactive
is_pure_land_specific: true
amitabha_case_density: medium
collection_priority: B
automation_priority: A2
originality_level: O2
provenance_quality: P2
structure_level: R2
copyright_risk: medium
review_status: verified_source
```

## Case Row

```text
case_id: CASE_SAMPLE
canonical_title: Sample Case Title
primary_language: zh-Hans
period: contemporary
event_year: unknown
date_precision: unknown
region: Sample Region
case_types: assisted_chanting
key_signs: fragrance
reborn_person_names: anonymous_with_descriptor
witness_names: unknown
canonical_summary: Schema-only summary.
provenance_quality: P2
evidence_level: medium
privacy_level: name_redacted
dedup_status: not_checked
review_status: machine_checked
publish_status: public_excerpt_only
```

## Citation Row

```text
citation_id: CIT_SAMPLE
case_id: CASE_SAMPLE
source_id: SRC_SAMPLE
citation_role: primary_source
source_title: Sample Source
article_or_segment_title: Sample Article
publication_date: unknown
date_precision: unknown
url: https://example.invalid/sample
locator_text: sample article section
quote_permission: short_quote_only
display_policy: public_excerpt_only
is_primary_citation: true
review_status: source_checked
```

## Case Text Rows

```text
text_id: TXT_SAMPLE_001
case_id: CASE_SAMPLE
citation_id: CIT_SAMPLE
text_type: original_excerpt
language: zh-Hans
content: [short excerpt placeholder]
source_mode: verbatim
review_status: source_checked
fidelity_status: human_checked
display_scope: public_excerpt_only
publish_status: public_excerpt_only
copyright_risk: medium
```

```text
text_id: TXT_SAMPLE_002
case_id: CASE_SAMPLE
citation_id: CIT_SAMPLE
text_type: reader_rendering
language: zh-Hans
content: [faithful readable rendering placeholder]
source_mode: faithful_rendering
created_by: ai_assisted
generated_from_text_id: TXT_SAMPLE_001
review_status: machine_checked
fidelity_status: machine_checked
display_scope: public
publish_status: public
copyright_risk: low
```

## Tags

```text
TAG assisted_chanting
tag_type: case_type
status: active
```

```text
TAG fragrance
tag_type: rebirth_sign
status: active
```

## Creator Metadata Row

```text
case_id: CASE_SAMPLE
teaching_themes: assisted_chanting_importance
audience_fit: general_reader; family_members
video_fit_score: 2
video_fit_level: medium
video_fit_notes: Schema-only note.
best_video_format: lecture_segment
narrative_clarity: medium
emotional_accessibility: medium
visualizability: low
length_fit: medium
context_required: medium
source_confidence: medium
recommended_usage: Use as an auxiliary example.
avoid_usage: Do not present as a standalone dramatic story.
misinterpretation_risk: medium
privacy_risk: medium
copyright_risk: medium
review_status: machine_checked
```

## Dedup Row

```text
dedup_group_id: DEDUP_SAMPLE
dedup_status: not_checked
canonical_case_id: CASE_SAMPLE
duplicate_confidence: unknown
review_status: candidate
```

## M0 Verification

This sample covers:

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
