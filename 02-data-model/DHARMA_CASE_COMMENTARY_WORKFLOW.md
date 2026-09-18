# Dharma Case Commentary Workflow

Purpose: produce engaging and accessible reader articles that connect a documented case with traceable Pure Land teaching.

The output is an AI-assisted editorial article. It is not source evidence, a substitute for the original testimony, or an independent doctrinal authority.

## Content Layers

```text
reader_summary
  short search and preview text

independent_factual_account
  independently structured account of supported case facts

dharma_case_commentary
  expressive reader article combining the case, doctrinal sources, explanation, and practical reflection
```

The three layers have separate IDs, generation records, review statuses, and publication policies.

## Non-negotiable Principle

Every checkable statement must have registered support.

```text
case fact -> case_fact_id and source_segment_ids
doctrinal claim -> doctrinal_citation_ids
teacher interpretation -> attributed teacher segment IDs
practical guidance -> doctrinal citation or reviewed method source
quotation -> exact locator and text verification
```

The generator may use registered project inputs only. Model memory, general web recall, or an uncaptured lecture is not acceptable citation support. A missing source must be ingested and reviewed before use.

## Generation Chain

```text
machine-checked case facts and source segments
-> reader question and target audience
-> approved interpretation angle
-> doctrinal citation retrieval
-> approved source-method retrieval
-> evidence-bound outline
-> draft with temporary claim markers
-> atomic claim extraction
-> factual claim check
-> doctrinal claim and quotation check
-> attribution and uncertainty check
-> rights and expression-similarity check
-> publication decision
```

## Stage 1: Input Freeze

Required inputs:

```text
case_id
case_fact_ids
source_segment_ids
interpretation_angle_id
reader_question
target_audience
approved doctrinal_citation_ids
approved source_method_ids
rights policy for every source
```

Generation stops if the case lacks segmented evidence or if the requested doctrinal theme lacks an approved citation.

## Stage 2: Evidence-bound Outline

Every outline section declares its role and support before prose generation.

```text
section_role: case_narrative | doctrinal_explanation | practical_reflection | boundary | source_note
planned_claims
support_ids
allowed_rhetorical_devices
forbidden_inferences
```

An outline section with no support may contain navigation or a clearly framed question, but no factual or doctrinal assertion.

## Stage 3: Drafting Rules

Allowed expressive techniques:

```text
reader-oriented questions
clear transitions
independently written explanation
contrast between common doubt and cited teaching
concise recapitulation
explicitly hypothetical examples that do not alter the case
```

Forbidden invention:

```text
invented scene, dialogue, action, motive, thought, emotion, or sensory detail
unstated causal connection
unstated medical or psychological conclusion
upgrading a dream, sign, report, or author inference into verified fact
presenting one case as proof of rebirth or universal doctrinal outcome
unattributed teacher interpretation
quotation reconstructed from memory
practice instruction with no approved doctrinal or method support
combining distinct Pure Land schools into a false consensus
```

Rhetorical language must not smuggle in a factual claim. For example, “she must have felt completely at peace” remains an unsupported mental-state claim even when used for emotional effect.

## Stage 4: Atomic Claim Ledger

After drafting, split the article into checkable claims. One sentence may create several claims.

Claim types:

```text
case_fact
source_attribution
doctrinal_claim
scriptural_or_teacher_quote
teacher_interpretation
practical_guidance
editorial_synthesis
rhetorical_or_navigation
```

Each non-rhetorical claim requires one or more support IDs and a support relation:

```text
direct
faithful_paraphrase
supported_inference
cross_source_synthesis
```

`supported_inference` and `cross_source_synthesis` must be disclosed in the article or source note when the distinction matters to readers.

## Stage 5: Factual Claim Check

For every `case_fact` and `source_attribution`, verify:

```text
people and relationships
time and date precision
place
event order
who observed or reported the event
claim mode: observation, recollection, hearsay, dream, inference, or commentary
uncertainty and source disagreement
privacy transformation
```

Hard failures:

```text
no supporting case fact or source segment
support contradicts the claim
reporter is omitted in a way that makes a report sound independently verified
date, place, person, dialogue, motive, or result is added
author inference becomes participant speech or event fact
```

## Stage 6: Doctrinal Claim And Citation Check

For every doctrinal claim, quotation, interpretation, and practice recommendation, verify:

```text
citation exists in doctrinal_citations
locator resolves to the retained or externally verifiable source
quotation matches the cited text
paraphrase preserves the source's scope and conditions
claim is actually entailed by the citation
speaker, translator, school, and context are attributed
case evidence is not used as the sole basis for doctrine
different teachers or lineages are not collapsed into consensus
```

Hard failures:

```text
doctrinal statement based only on model memory
fabricated or unverifiable quotation
citation discusses a related topic but does not support the actual conclusion
omitted condition changes the teaching
teacher opinion is labeled as scripture, patriarch teaching, or universal Pure Land doctrine
AI generates a definitive rebirth judgment
```

## Stage 7: Boundary And Safety Check

The article must state relevant limits, including:

```text
what the case reports
what the source does not independently establish
what is doctrinal explanation rather than event evidence
what practical advice requires pastoral, medical, legal, or family judgment
```

Medical treatment, end-of-life decisions, mental health, and family consent must not be decided from a religious case account.

## Stage 8: Rights And Expression Check

Apply the rights policy of the case source and every doctrinal or talk source.

```text
check quotation scope
check paragraph-order and distinctive-expression similarity
check whether the article substitutes for a restricted original
check translation and adaptation permission
withhold restricted source text from public debug or citation views
```

An article can pass factual and doctrinal checks while still being withheld for rights reasons.

Rights review must cover the generated output itself, not only the input source. Apply `COPYRIGHT_RESEARCH_WORKFLOW.md` and record:

```text
source-level rights review
source-entry override when applicable
independent factual account policy
dharma commentary policy
quotation and translation policy
distinctive-expression similarity
structural similarity
substitution risk
publication jurisdictions
decision evidence and review date
```

## Publication Gate

Required statuses:

```text
factual_claim_status: passed
doctrinal_claim_status: passed
quotation_status: passed_or_not_used
attribution_status: passed
uncertainty_status: passed
rights_status: allowed_by_current_policy
privacy_status: passed
unsupported_claim_count: 0
contradicted_claim_count: 0
```

Machine review may publish only against approved doctrinal citations and approved method patterns. Any new doctrinal interpretation, disputed teaching, unresolved citation, or high-impact practical guidance requires human doctrinal review.

`allowed_by_current_policy` is an operational publication decision, not a guarantee of non-infringement. Unclear source ownership, translation rights, platform terms, or jurisdiction-specific exceptions produce `legal_review_required` or `withheld`.

## Verification Examples

Unsupported factual expansion:

```text
draft: Her mother understood the Buddha-name and felt peaceful.
source: the mother followed family members in recitation; her internal understanding and emotion were not reported.
result: reject the mental-state claims.
```

Preserved attribution:

```text
draft: Family members reported that her face appeared calmer after support-chanting.
support: case_fact for the family's observation plus the exact source segments.
result: eligible to pass factual review when wording and timing match.
```

Citation-topic mismatch:

```text
draft: This case proves that every person with dementia will attain rebirth through family recitation.
support: one family testimony and a citation discussing the accessibility of name-recitation.
result: reject; neither source entails the universal outcome or a definitive rebirth judgment.
```

Proper doctrinal framing:

```text
draft: Within the cited teaching, family recitation is presented as compassionate support; the case itself records how one family applied that practice.
support: approved doctrinal citation plus case facts.
result: eligible to pass when attribution, scope, and rights checks also pass.
```

## Correction And Regeneration

Never silently overwrite a published article.

```text
mark affected claims needs_revision
withhold the affected text version when risk is material
retain the prior generation and review record
create a new generation_run_id
rerun every publication gate
record the correction reason
```
