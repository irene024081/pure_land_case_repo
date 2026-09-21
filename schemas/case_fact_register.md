# Case Fact Register Schema

`case_facts` stores atomic normalized propositions extracted from source segments. It is the factual bridge between source evidence and generated content.

Pipeline 0.2.0 first emits candidate-scoped facts with `candidate_id` and IDs such as `ENT000001-CAND0001-FACT0001`. `case_id` is assigned only after `case_resolution`. Canonical promotion associates the fact with that Case without rewriting the historical Run output or losing its candidate provenance. Older v0.1.x Runs retain their `CASE...-FACT...` IDs.

## Core Fields

```text
case_fact_id
case_id
fact_type
subject_entity_id
predicate
object_value
normalized_value
unit
date_value
date_precision
place_id
proposition_text
claim_mode
reported_by_person_id
observed_by_person_ids
supporting_source_segment_ids
support_relation
uncertainty
source_disagreement
sensitivity
review_status
notes
```

## fact_type

```text
identity
relationship
date
place
practice
event
observation
reported_sign
dream_or_vision
speech
author_inference
teacher_commentary
source_metadata
other
```

## claim_mode

```text
direct_source_statement
first_person_recollection
named_witness_report
anonymous_witness_report
hearsay
dream_or_vision
author_inference
doctrinal_interpretation
normalized_metadata
unknown
```

## support_relation

```text
direct
normalized_from_source
supported_inference
conflicting_sources
```

## review_status

```text
candidate
machine_extracted
machine_checked
human_checked
needs_revision
rejected
```

## Rules

1. Store one independently checkable proposition per row.
2. Preserve the reporter, observer, and claim mode.
3. Do not turn a witness report into a direct observation by the database.
4. Do not turn an author inference into participant speech or established event fact.
5. Keep dream and vision content distinct from external observation.
6. Record conflicting versions instead of choosing silently.
7. Generated factual claims must cite `case_fact_id` values and inherit their uncertainty.
8. `case_facts` describes what sources state. It does not declare the event historically true.
