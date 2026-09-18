# Data Processing Workflow

This document defines domain rules and milestone behavior. The executable stage sequence is not duplicated here. `../pipeline/pipeline.v1.json` is authoritative for ordering and dependencies; `../09-agent-automation/README.md` defines run state, prompt versioning, external adapters, and regression gates.

Any example in this document that refers to an "AI job" means a versioned pipeline stage with a contract and run record. Ad hoc chat generation is not an accepted processing method.

本文件定义从来源到可发布案例的处理流程。目标是把资料搜集拆成可验证的小里程碑。

## Processing Stages

```text
source_selection
source_profile
ingestion_plan
raw_capture
source_entry_generation
source_segmentation
entry_classification
case_extraction
case_normalization
claim_and_narrative_analysis
text_version_generation
tagging_and_entities
citation_and_provenance
dedup_check
creator_metadata
doctrinal_source_preparation
dharma_commentary_generation
content_claim_verification
quality_review
publish_ready
```

## Default Automation Boundary

Do not treat AI as a black-box URL processor.

Default chain:

```text
source URL or file
-> source registration and rights precheck
-> source-specific extractor script
-> source_entries
-> source_segments and atomic case facts
-> entity tagging and deduplication
-> reader generation and creator analysis
-> independent factual and rights checks
-> deterministic publication package
```

Script responsibility:

```text
download or read source material
preserve raw text
split reproducible entries
record locator, command, extractor version, hash
persist the normalized source entry according to its storage class
```

AI responsibility:

```text
classify whether an entry contains case material
extract case facts
generate faithful reader rendering and summaries
suggest tags, entities, dedup candidates, creator metadata
record uncertainties
generate doctrine-linked commentary only from approved project citations
emit an atomic claim ledger for every commentary
```

Machine check responsibility:

```text
verify required fields
verify that raw_capture_status matches an existing object and hash when marked persisted
check that generated text is grounded in the source entry
flag missing citation or locator
flag copyright and privacy risk
flag dedup uncertainty and stop points
block unsupported, contradicted, misattributed, or quotation-mismatched claims
```

## Stage Definitions

### 1. source_selection

选择进入 seed dataset 的来源。

Output:

```text
source_id
source group
reason for inclusion
expected case count
copyright risk
processing difficulty
```

Exit criteria:

```text
source is relevant
source can support at least one product scenario
source risk is understood
```

### 2. source_profile

建立来源档案。

Output:

```text
source register row
access status
update status
case density estimate
originality estimate
automation priority
collection priority
```

Exit criteria:

```text
source can be cited
processing method is known
display limitations are known
```

### 3. ingestion_plan

定义该来源如何处理。

Output:

```text
input format
capture method
case boundary rule
text cleanup rule
copyright display rule
review requirements
```

Examples:

```text
ancient text -> split by biography entries
periodical PDF -> split by article and page range
website -> one article per citation
YouTube -> timestamped transcript segments
```

### 4. raw_capture

保存可追溯的原始证据或证据定位。

Output:

```text
original_full or original_excerpt
evidence_locator
url, page, volume, issue, timestamp
capture date
```

Rule:

```text
public display follows display_scope
internal evidence must still be traceable
```

### 5. source_entry_generation

把来源材料切成可复现的 source entries。

Output:

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
extractor_version
extraction_command
boundary_confidence
review_status
```

Risk:

```text
one article may contain multiple cases
one case may span multiple paragraphs
one video may contain multiple cases
one entry may be commentary rather than a case
```

Rule:

```text
source_entry is not final case
do not drop non-case entries silently when running a source-wide extractor
entry_sequence is not a global ID
hash or URL alone does not count as a persisted raw capture
```

### 6. source_segmentation

Split each retained entry into traceable paragraphs, speaker turns, or timestamp ranges.

Output:

```text
segment_id
sequence
segment_type
locator
speaker_or_author
claim_mode
content_hash
display_scope
```

Rule:

```text
preserve source order
separate event report from author inference and teacher commentary
do not rewrite source wording
version segments when extraction boundaries change
```

### 7. entry_classification

判断 source entry 是否包含案例材料。

Output:

```text
entry_type
ai_case_candidate_count
linked_case_ids when known
classification_notes
uncertainties
```

Entry types:

```text
single_case_candidate
multi_case_candidate
non_case_material
commentary
index_only
mixed
unknown
```

### 8. case_extraction

从候选段落中提取案例事实。

Output:

```text
who
what happened
when
where
witnesses
key signs
case type
source claims
uncertainties
```

Rule:

```text
unknown remains unknown
do not infer missing names, places, dates
```

### 9. case_normalization

生成规范案例记录。

Output:

```text
case_id
canonical_title
canonical_summary
period
region
case_types
key_signs
provenance_quality
evidence_level
privacy_level
```

Rule:

```text
case is the event/story unit
citation is where it appears
text version is how it is displayed
```

### 10. claim_and_narrative_analysis

Build a detailed account before generating reader or creator text.

Output:

```text
atomic case facts with supporting_segment_ids
opening situation
central difficulty
turning points
practice process
death or resolution sequence
reported signs grouped by observer and claim mode
aftermath
unresolved questions
```

Rule:

```text
keep direct observation, family report, dream, inference, and commentary separate
do not convert a reported sign into proof of rebirth
retain details needed for a coherent account even when they are not search tags
```

### 11. text_version_generation

生成不同文本层级。

Output:

```text
short_summary
reader_rendering
search_digest
creator_summary
translation when needed
```

Fidelity rule:

```text
can clean repetition
can add punctuation
can improve readability
can translate
cannot add facts
cannot remove uncertainty
cannot add doctrinal explanation as case fact
```

Reader rendering quality rule:

```text
tell the complete supported sequence, not only the indexed facts
retain relevant motivation, difficulty, turning points, practice, outcome, and attribution
use the reader summary for compression
attach source segment IDs to each generated paragraph
```

### 12. tagging_and_entities

标注案例类型、人物、地点和主题。

Output:

```text
case_tags
reborn_person_names
witness_names
places
teaching_themes
rebirth_signs
```

Rule:

```text
tags should support search and recommendation
tags should not overstate evidence
```

### 13. citation_and_provenance

建立引用和出处链。

Output:

```text
citation_id
source_id
source_entry_id
locator
is_primary_citation
provenance_chain
earliest_known_source
```

Rule:

```text
modern repost is discovery source
earlier source remains citation/provenance target
```

### 14. dedup_check

检查是否与已有案例重复。

Compare:

```text
person
place
event year
case type
key signs
source chain
summary similarity
original text similarity
```

Output:

```text
dedup_status
canonical_case_id
duplicate_confidence
merge_notes
```

### 15. creator_metadata

生成创作者辅助字段。

Output:

```text
teaching_themes
recommended_usage
avoid_usage
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
primary_narrative_arc
interpretation_angles
```

Rule:

```text
creator metadata is recommendation support
it is not original evidence
each detailed angle cites source segments or normalized facts
each angle includes a boundary note and target audience
```

### 16. doctrinal_source_preparation

Register the doctrinal sources allowed to support public explanation.

Output:

```text
doctrinal_citation_id
authority_type
tradition_or_lineage
exact locator
verified quotation or restricted text locator
context and scope conditions
supported topics
known interpretive limits
rights policy
review_status
```

Rule:

```text
do not cite model memory
do not use search snippets as quotation evidence
do not treat one teacher's interpretation as universal consensus
do not allow public generation until text, locator, and doctrinal scope are approved
```

### 17. dharma_commentary_generation

Generate an expressive article for ordinary readers from separate case and doctrine evidence layers.

Output:

```text
dharma_case_commentary
reader_question
main_teaching_point
evidence-bound outline
case_fact_ids
doctrinal_citation_ids
source_method_ids
temporary claim markers
generation provenance
```

Rule:

```text
case evidence supplies the event
doctrinal citations supply teaching claims
source methods supply reviewed explanation patterns
AI supplies structure and original wording
AI may not supply uncited facts, doctrine, quotations, or practice rules
```

Follow `DHARMA_CASE_COMMENTARY_WORKFLOW.md`.

### 18. content_claim_verification

Split the article into atomic claims and verify each one.

Required checks:

```text
factual entailment and contradiction
reporter and claim-mode attribution
uncertainty preservation
doctrinal entailment and source scope
quotation match
teacher and lineage attribution
rights and expression similarity
source-level, item-level, and generated-output copyright research
privacy and high-impact guidance boundaries
```

Publication blockers:

```text
unsupported_claim_count > 0
contradicted_claim_count > 0
partially entailed or not entailed claim
unverified or mismatched quotation
case report used as sole doctrinal authority
model-memory doctrinal claim
definitive judgment that a person attained rebirth
```

### 19. quality_review

人工或半自动审核。

Checklist:

```text
source citation present
raw capture status is truthful and storage object hash is verified when marked persisted
reader rendering faithful
reader rendering is sufficiently complete for the available source
generated paragraphs and interpretation angles cite source segments
original evidence or locator present
case tags reasonable
copyright risk set
privacy risk set
dedup checked
creator metadata reasonable
dharma commentary claims pass factual and doctrinal checks when commentary exists
unsupported_claim_count equals zero
contradicted_claim_count equals zero
```

Review status:

```text
candidate
extracted
normalized
source_checked
human_reviewed
ready_to_publish
needs_recheck
```

### 20. publish_ready

进入公开网站或创作者工作台。

Required:

```text
ready_to_publish status
display_scope set
reader view content present
citation present
risk notes present when needed
every public dharma commentary has approved doctrinal citations and a passed claim ledger
every public generated text has an output-specific rights decision
```

## Milestones

### M0: Schema Lock

Goal:

```text
freeze MVP fields for sources, cases, citations, case_texts, tags, creator_metadata
```

Deliverables:

```text
M0_SCHEMA_LOCK.md
source_register.md
case_register.md
citation_register.md
case_text_register.md
tag_register.md
creator_metadata_register.md
person_place_register.md
dedup_register.md
DATA_MODEL.md
SEED_DATASET_PLAN.md
M0_SCHEMA_SAMPLE.md
```

Exit criteria:

```text
one sample case can be represented without missing critical fields
```

### M1: Source Shortlist

Goal:

```text
select 3-5 seed sources
```

Deliverables:

```text
source_directory_v1.csv rows
source processing notes
copyright and access notes
```

Exit criteria:

```text
each source maps to a processing method
each source has target case count
```

### M2: Ten-case Pilot

Goal:

```text
process 10 cases end to end
```

Detailed plan:

```text
M2_TEN_CASE_PILOT_PLAN.md
```

Required mix:

```text
at least 1 ancient case
at least 1 modern written case
at least 1 web case
at least 1 oral/video or first-person case
```

Exit criteria:

```text
each case has citation, reader rendering, tags, creator metadata
```

### M3: Workflow Repair

Goal:

```text
fix schema and workflow problems discovered in pilot
```

Exit criteria:

```text
no recurring blocker in extraction, display, search, or recommendation fields
```

### M4: Fifty-case Alpha

Goal:

```text
create 50 reviewed cases
```

Exit criteria:

```text
search tests pass
case detail tests pass
theme recommendation can return 5 cases for 3 common themes
```

### M5: Recommendation And Creator Test

Goal:

```text
validate theme-to-case recommendation and creator brief
```

Test themes:

```text
临终助念
预知时至
异香瑞相
念佛免难
家属如何陪伴临终者
```

Exit criteria:

```text
recommendations include why_relevant, citation, video_fit, risk_notes
creator brief is usable without inventing facts
```

### M6: Hundred-case Beta

Goal:

```text
expand to 80-100 cases
```

Exit criteria:

```text
reader search works across sources and case types
creator workflow has enough variety
research review can inspect citations and dedup status
website MVP can start with real data
```

## Agent Role By Stage

| Stage | Agent role | Human role |
|---|---|---|
| source_selection | suggest candidates and risks | approve source scope |
| source_profile | fill draft source rows | verify source identity |
| raw_capture | prepare evidence locator | check copyright boundary |
| case_extraction | draft structured facts | correct omissions and errors |
| text_version_generation | draft rendering and summaries | review fidelity |
| tagging_and_entities | propose tags and entities | approve controlled vocabulary |
| provenance | suggest earlier sources | verify evidence |
| dedup | flag possible duplicates | decide merge |
| creator_metadata | draft fit and usage notes | approve religious and editorial appropriateness |
| quality_review | run checklist | final publish decision |

## Operating Rule

Do not scale extraction until M2 proves one complete case can move through the workflow.

Do not scale source count until M4 proves search and case detail work.

Do not make Agent ingestion autonomous until M5 proves recommendation and creator brief do not invent or distort facts.
