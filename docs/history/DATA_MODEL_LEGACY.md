# Data Model

本数据模型同时服务三个目标：读者搜索阅读、创作者主题配例、研究者追源去重。

## Core Principle

案例事实、来源定位、文本版本和创作辅助信息必须分开。

```text
Source
  where material comes from

Source Entry
  reproducible extracted segment from a source

Source Segment
  paragraph or timestamp unit used for claim-level traceability

Citation
  where a case appears inside a source

Case
  canonical event or story unit

Case Fact
  atomic proposition preserving reporter, claim mode, evidence, and uncertainty

Case Text
  original text, excerpt, summary, reader rendering, translation, creator summary

Creator Metadata
  teaching themes, video fit, usage notes, risk notes

Interpretation Angle
  evidence-linked creator or doctrinal explanation angle

Doctrinal Citation
  verified scripture, commentary, lineage, or teacher source for doctrinal claims

Dharma Case Commentary
  expressive reader article grounded in case facts and approved doctrine sources

Content Claim
  atomic factual, doctrinal, quotation, or guidance statement with explicit support
```

## Entity Overview

```text
sources
source_entries
source_segments
cases
case_facts
citations
case_texts
persons
organizations
places
tags
case_tags
case_persons
case_places
provenance_links
dedup_groups
dedup_members
creator_metadata
interpretation_angles
doctrinal_citations
dharma_case_commentaries
content_claims
generation_runs
```

## Required MVP Tables

第一版必须有这些表：

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

`source_entries` was added before M2 scaling to make extraction reproducible. `organizations` and `provenance_links` can be added later. M0 can still represent source institutions through `sources` and provenance through `citations` plus notes.

The reader commentary extension requires these tables before the feature can publish:

```text
source_segments
case_facts
doctrinal_citations
dharma_case_commentaries
content_claims
generation_runs
```

## Relationship Model

```text
sources 1 -> many citations
sources 1 -> many source_entries
source_entries 1 -> many source_segments
source_entries 0 -> many citations
cases 1 -> many citations
cases 1 -> many case_facts
cases 1 -> many case_texts
cases many -> many tags
cases 1 -> 1 creator_metadata
cases 1 -> many interpretation_angles
cases 1 -> many dharma_case_commentaries
doctrinal_citations many -> many dharma_case_commentaries
dharma_case_commentaries 1 -> many content_claims
source_segments many -> many case texts, case facts, and interpretation angles
cases many -> many persons
cases many -> many places
citations many -> many provenance_links
cases many -> many dedup_groups
```

## Source Entries

`source_entries` 保存从一个 source 中脚本切出的原文条目。它是抽取层，不是案例层。

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
raw_text_hash
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

Rules:

```text
one source_entry may produce zero, one, or many cases
one case may have citations from many source_entries
source_entries must preserve raw extracted text
AI can classify source_entries but must not silently change raw_text
```

Use `raw_text_hash` to detect extractor changes, source page changes, and boundary drift.

Raw text must have an explicit storage record. A URL and hash do not prove that the text is durably retained. Use `storage_class`, `storage_uri`, and `raw_capture_status` according to `RAW_SOURCE_STORAGE.md`.

`source_entry_id` is the stable database ID. `source_entry_key` is the reproducible source-facing key produced by extraction, and `entry_sequence` is only the order within a source or section.

## Source Segments

`source_segments` divides a retained source entry into stable paragraphs, speaker turns, or timestamp ranges.

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

This layer makes it possible to identify which exact source passage supports a reader paragraph, factual claim, or creator angle. It also separates witness reports, dreams, author inference, and teacher commentary before generation.

## Cases

`cases` 保存一个案例的规范事实，不保存长篇原文。

```text
case_id
canonical_title
primary_language
period
event_year
date_precision
region
case_status
provenance_quality
evidence_level
privacy_level
canonical_summary
dedup_status
publish_status
created_at
updated_at
review_status
notes
```

`canonical_summary` 是事实梗概，用于去重、快速理解和推荐召回。它不替代原文。

## Case Facts

`case_facts` stores atomic propositions used for factual verification.

```text
case_fact_id
case_id
fact_type
subject_entity_id
predicate
object_value
normalized_value
proposition_text
claim_mode
reported_by_person_id
observed_by_person_ids
supporting_source_segment_ids
support_relation
uncertainty
source_disagreement
review_status
```

Case facts preserve whether information is a direct source statement, witness report, hearsay, dream, author inference, or doctrinal interpretation. They describe what the source states and do not declare historical truth.

## Citations

`citations` 保存某个案例在某个来源中的具体位置。

```text
citation_id
case_id
source_id
source_entry_id
source_title
author_or_speaker
publication_date
date_precision
volume
issue
page_start
page_end
url
archive_url
timestamp_start
timestamp_end
locator_text
access_date
quote_permission
display_policy
is_primary_citation
review_status
notes
```

一个案例可以有多个引用。`is_primary_citation` 标记当前展示优先使用的出处。

## Case Texts

`case_texts` 保存同一案例的不同文本层级。推荐、搜索、读者页、创作者页和未来多语言页面都从这里取不同版本。

```text
text_id
case_id
citation_id
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

### text_type

```text
original_full
original_excerpt
evidence_locator
classical_to_modern_rendering
oral_record_cleanup
first_person_testimony_cleanup
long_article_summary
reader_summary
reader_rendering
creator_summary
search_digest
translation
editor_note
ai_note
independent_factual_account
```

### source_mode

```text
verbatim
faithful_rendering
summary
translation
ai_assisted
human_editorial
```

`faithful_rendering` 只允许改善可读性，不允许新增事实。

### fidelity_status

```text
not_checked
machine_checked
human_checked
needs_revision
rejected
```

AI 生成的 `reader_rendering`、`translation`、`creator_summary` 默认不能直接视为证据。它们必须通过 `generated_from_text_id`、`generated_from_source_entry_id` 或 `citation_id` 追溯到原文、摘录、字幕、页码或时间戳。

New outputs should use `generated_from_segment_ids` for paragraph-level traceability. Entry-level provenance remains required but is not precise enough for claim checking.

### display_scope

```text
public
public_excerpt_only
internal
restricted
withheld
```

现代版权材料通常使用 `public_excerpt_only` 或 `internal`。公开页面展示摘要、短摘录、出处和定位信息。

### publish_status

```text
internal
public
public_excerpt_only
withheld
retired
```

Processing review status and public display status are separate. A reviewed item can remain withheld.

## Creator Metadata

`creator_metadata` 保存辅助创作用的结构化信息。

```text
case_id
teaching_themes
audience_fit
video_fit_score
video_fit_level
video_fit_notes
best_video_format
narrative_clarity
emotional_accessibility
visualizability
length_fit
context_required
source_confidence
emotional_intensity
recommended_usage
avoid_usage
misinterpretation_risk
privacy_risk
copyright_risk
brief_notes
review_status
```

这些字段让系统能从上千条案例中推荐合适材料，而不是只靠原文相似度。

## Narrative Analysis

Narrative analysis records enough detail to generate a rich reader account and a precise creator brief without repeatedly compressing the source into a short summary.

```text
case_id
opening_situation
practice_background
central_difficulty
intervention_or_turning_point
practice_process
death_or_resolution_sequence
reported_signs_by_observer
observable_changes
aftermath
primary_narrative_arc
unresolved_questions
supporting_segment_ids
review_status
```

This is structured analysis. It does not replace the raw source or the full reader rendering.

## Interpretation Angles

`interpretation_angles` stores precise, evidence-linked creator uses.

```text
angle_id
case_id
angle_type
title
core_claim
audience
creator_goal
supporting_segment_ids
supporting_case_fact_ids
doctrinal_topics
suggested_structure
required_context
confidence_basis
boundary_notes
counter_reading
source_method_ids
generated_by
prompt_version
review_status
```

The broad `teaching_themes` field supports retrieval. Interpretation angles support explanation and production. Several angles may exist for one case, and each must identify what the evidence supports and what it cannot establish.

## Generation Runs

Generated text and angles should be reproducible.

```text
generation_run_id
job_type
model
prompt_version
input_source_entry_ids
input_segment_ids
output_ids
generated_at
machine_check_version
review_status
notes
```

Prompt improvement creates a new generation run. It does not overwrite the raw source or silently replace a previously published version.

## Doctrinal Citations

`doctrinal_citations` is the approved evidence layer for doctrine, teacher interpretation, and practice guidance.

```text
doctrinal_citation_id
authority_type
tradition_or_lineage
author_or_speaker
work_or_talk_title
source_entry_id
source_segment_ids
canonical_locator
context_summary
supported_topics
scope_conditions
known_interpretive_limits
rights_review_id
review_status
```

Only citations with verified text, locator, and doctrinal scope may be used for public generation. Model memory is never a doctrinal citation.

## Dharma Case Commentaries

`dharma_case_commentaries` stores engaging reader articles that combine a documented case with approved doctrinal explanation.

```text
article_id
case_id
reader_question
main_teaching_point
interpretation_angle_id
independent_factual_account_text_id
case_fact_ids
source_segment_ids
doctrinal_citation_ids
source_method_ids
content
claim_ids
generation_run_id
factual_claim_status
doctrinal_claim_status
quotation_status
attribution_status
uncertainty_status
rights_status
privacy_status
unsupported_claim_count
contradicted_claim_count
review_status
publish_status
```

This content type is commentary, not evidence. Expressive quality may come from structure, questions, pacing, and explanation. It may not come from invented case facts, mental states, dialogue, causation, or quotations.

## Content Claims

Every checkable statement in a generated commentary becomes a `content_claim`.

```text
claim_id
article_id
claim_text
claim_type
support_relation
supporting_case_fact_ids
supporting_source_segment_ids
supporting_doctrinal_citation_ids
supporting_source_method_ids
attributed_to
uncertainty_preserved
entailment_status
contradiction_status
quotation_match_status
rights_status
review_status
```

Publication is blocked when a non-rhetorical claim is unsupported, only partially entailed, contradicted, misattributed, or based on an unverified quotation.

### best_video_format

```text
short_video
long_video
lecture_segment
case_compilation
quote_only
not_recommended
unknown
```

`video_fit` 不代表案例真实性，只代表视频表达适配度。真实性和出处质量由 `provenance_quality`、`evidence_level`、`source_confidence` 表达。

## Dedup Model

AI may suggest duplicate candidates. It must not silently merge canonical cases.

```text
dedup_group_id
dedup_status
canonical_case_id
duplicate_confidence
review_status
notes
```

Statuses:

```text
not_checked
not_duplicate
possible_same_case
same_case
merged
needs_review
```

When one version has a named person and another has an unknown person, use `possible_same_case` until enough non-name evidence confirms the match.

## Search Index Inputs

搜索索引应同时使用：

```text
case canonical title
canonical summary
reader summary
reader rendering
translations
creator summary
original excerpt
tags
persons
places
source names
teaching themes
```

不同字段权重不同：

```text
person_name: high
source_title: high
tags: high
canonical_summary: medium
reader_rendering: medium
original_excerpt: medium
creator_summary: medium
translation: medium
original_full: low
```

原文全文可用于内部搜索，但公开结果展示受 `display_scope` 控制。

## Recommendation Inputs

主题到案例推荐至少使用：

```text
semantic relevance to topic
case tags
teaching themes
provenance quality
evidence level
narrative clarity
video fit
audience fit
privacy risk
copyright risk
dedup status
```

推荐结果必须返回 `case_id` 和至少一个可展示的 `citation_id`。

## Dedup Rule

重复判断不只看标题。应同时比较：

```text
reborn person
witness
place
event year
case type
key signs
source chain
summary similarity
original text similarity
```

同一案例的多处转载应该合并为一个 `case_id`，并把每个来源保存为 `citation`。
