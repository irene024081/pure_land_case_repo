# Case Register Schema

本文件定义案例登记标准。它和 `source_register.md` 配合使用。

## Core Fields

```text
case_id
canonical_title
primary_language
period
event_year
date_precision
region
case_types
key_signs
reborn_person_names
witness_names
related_person_names
source_summary
canonical_summary
provenance_quality
evidence_level
privacy_level
creator_fit
dedup_status
review_status
publish_status
notes
```

## date_precision

```text
exact_date
year
month
issue
dynasty
period
unknown
```

## privacy_level

```text
public
name_redacted
sensitive
private_internal
unknown
```

## publish_status

```text
internal
public
public_excerpt_only
withheld
retired
```

## dedup_status

```text
not_checked
not_duplicate
possible_same_case
same_case
merged
needs_review
```

## Creator Fit Fields

```text
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
misinterpretation_risk
recommended_usage
avoid_usage
```

`video_fit` 只表示视频表达适配度，不表示真实性或法义价值。

## Text Versions

每个案例可以有多个文本版本。不要把所有文本塞进 `cases` 表。

```text
original_full
original_excerpt
classical_to_modern_rendering
oral_record_cleanup
first_person_testimony_cleanup
long_article_summary
reader_rendering
reader_summary
creator_summary
search_digest
translation
editor_note
ai_note
```

## Reader Display Rule

读者页默认展示：

```text
short summary
reader rendering
original evidence
source citation
```

`reader rendering` 可以是文言文白话译述、口述整理或字幕整理，但必须忠实于原文，不新增事实。

## Fidelity Rule

AI 可读化文本必须记录依据来源。

```text
generated_from_text_id
citation_id
fidelity_status
display_scope
```

允许处理：

```text
clean repetition
add punctuation
clarify pronoun references when supported by context
reorder only when the event sequence remains unchanged
translate into another language
```

禁止处理：

```text
add people
add place
add time
add miraculous details
add doctrinal explanation as case fact
merge separate cases
remove uncertainty
```

## Creator Display Rule

创作者页默认展示：

```text
short summary
creator summary
teaching themes
recommended usage
source citation
risk notes
similar cases
```

## Review Status

```text
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
