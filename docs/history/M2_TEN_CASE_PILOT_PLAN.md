# M2 Ten-case Pilot Plan

Status: first M2 review completed at the schema level. Raw storage, narrative analysis, and interpretation-angle changes are applied; source segmentation and text regeneration remain before cases 6-10.

Purpose: process 10 cases end to end, two from each locked seed source, to test the full workflow before scaling.

## Locked Distribution

```text
SRC0001 《净土圣贤录》: 2 cases
SRC0002 《当代念佛感应集》: 2 cases
SRC0003 PLBTW: 2 cases
SRC0004 PLB-SEA: 2 cases
SRC0005 Purelanders: 2 cases
```

## Global Selection Rules

Each selected case should satisfy:

```text
clear enough case boundary
at least one citable source locator
extractable core facts
usable reader rendering
at least one search tag
dedup status can be evaluated
creator metadata can be meaningfully assigned
```

Avoid as first M2 cases:

```text
only doctrinal discussion, no case narrative
extremely long multi-case article
heavy privacy details without clear redaction path
unclear source locator
unclear whether Amitabha/Pure Land related
same motif but no distinct event details
```

M2 should deliberately include both easy and difficult examples:

```text
at least 1 classical case
at least 1 modern copyrighted source case
at least 1 structured HTML case
at least 1 first-person or letter-like case
at least 1 English original case
at least 1 high video_fit case
at least 1 low or quote_only video_fit case
at least 1 possible dedup/provenance challenge
```

## Per-source Sampling Plan

### SRC0001: 《净土圣贤录》

Select:

```text
1 named person case with clear rebirth sign
1 case where earlier-source tracing is likely needed
```

Prefer:

```text
short to medium biography entry
clear person boundary
clear sign such as fragrance, light, body softness, seeing Amitabha, foreknowledge
```

Avoid:

```text
entry mainly about doctrine
entry with many people and no single case boundary
entry that is too famous and already has many versions unless used for dedup testing
```

Workflow tested:

```text
classical original excerpt
faithful modern Chinese rendering
P3 provenance quality
possible earlier source note
```

### SRC0002: 《当代念佛感应集》

Select:

```text
1 modern first-person or family-witness case
1 case with explicit original 《净土》 issue locator if available
```

Prefer:

```text
clear article title or section title
named or semi-named people
place or date available
case type useful for creator workflow
```

Avoid:

```text
long multi-case compilation section
case that is mostly non-Amitabha practice unless selected intentionally for boundary testing
case with no locator beyond the book as a whole
```

Workflow tested:

```text
modern copyrighted source
public short excerpt only
reader rendering public
source chain note back to 《净土》
```

### SRC0003: PLBTW

Select:

```text
1 case from a clearly structured story page
1 case likely to overlap with another publication or simplified/traditional duplicate
```

Prefer:

```text
stable article URL
title includes case theme or person
HTML text easy to segment
contains one primary case
```

Avoid:

```text
page containing many short anecdotes
page with no date, no author, and no source note if another better page exists
pure teaching article without a concrete case
```

Workflow tested:

```text
structured HTML extraction
traditional/simplified dedup handling
discovery source vs original source distinction
```

### SRC0004: PLB-SEA

Select:

```text
1 first-person or letter-like modern case
1 bilingual or article/video-overlap case
```

Prefer:

```text
case fact separable from Dharma commentary
URL stable
English/Chinese text pairing if available
recent source with clear public page
```

Avoid:

```text
mostly general Dharma talk without distinct case
highly sensitive private family details unless redaction is straightforward
case where article and video relationship is too unclear for pilot
```

Workflow tested:

```text
case fact vs teacher commentary separation
privacy review
bilingual overlap
creator metadata for family/support themes
```

### SRC0005: Purelanders

Select:

```text
1 assisted chanting / family guidance case
1 case with clear narrative but translation sensitivity
```

Prefer:

```text
English original story
clear people roles
clear sequence of support chanting or guidance
manageable length
```

Avoid:

```text
very long article with multiple stories
highly private medical detail
article that is mainly instruction with no concrete case
```

Workflow tested:

```text
English original excerpt
Chinese reader rendering / translation
translation fidelity
support-chanting tags
```

## M2 Extraction Order

Use this order to discover schema problems early:

```text
1. SRC0001 case 1: classical simple case
2. SRC0003 case 1: structured HTML simple case
3. SRC0005 case 1: English original case
4. SRC0002 case 1: modern copyrighted book case
5. SRC0004 case 1: first-person/letter case
6. repair workflow if needed
7. process second case from each source
```

Rationale:

```text
Start with one easier classical source and one easier web source.
Add multilingual early.
Add copyright-limited and first-person complexity before scaling.
Pause after five cases to repair schema and workflow.
```

## Case Record Requirements

Every M2 case must produce draft rows for:

```text
cases
citations
case_texts
case_tags
creator_metadata
dedup_groups or dedup_status
persons if named or meaningfully anonymous
places if available
```

Minimum text versions:

```text
original_excerpt or evidence_locator
short_summary
reader_rendering
search_digest
creator_summary
```

Additional requirements found in the first-five review:

```text
verified raw capture manifest
source segments before final text generation
detailed narrative analysis
reader_rendering content_depth
at least one evidence-linked interpretation angle
generation and prompt provenance
```

Reader commentary extension:

```text
do not generate public dharma_case_commentary before source segmentation
register and approve doctrinal citations before doctrinal generation
generate an atomic content claim ledger
require zero unsupported or contradicted claims
verify every quotation against its retained source and locator
keep independent_factual_account separate from dharma_case_commentary
```

M2 should test this extension on one case after the factual pipeline is repaired. It is not required for all ten cases until the first commentary passes the full publication gate.

Minimum review statuses:

```text
review_status >= machine_checked for reader_rendering
publish_status set
dedup_status set
copyright_risk set
privacy_risk set
```

## Stop Points

Stop and ask before continuing if:

```text
a source page cannot be accessed
case boundary is ambiguous
same-case/dedup decision is unclear
modern full text seems necessary but copyright risk is high
privacy redaction would materially change the case
AI rendering requires adding missing facts to become readable
case is not clearly Amitabha/Pure Land related
```

## User Confirmations Needed Before Extraction

Confirmed:

```text
Use the extraction order above.
After the first 5 cases, pause for user review before processing the second 5.
For first-person modern cases, do not anonymize by default. Anonymize only when the source text is already anonymous.
If a selected source page fails access, stop and ask. Do not choose a replacement without user confirmation.
```

Unresolved:

```text
Modern copyrighted sources default display policy is not yet locked.
Do not assume public_excerpt_only as a global default until reviewed case by case.
```

Operational rule:

```text
For each modern copyrighted case, propose display_policy and copyright_risk during extraction.
Pause if full-text display seems necessary, if excerpt length is unclear, or if source rights are unclear.
```
