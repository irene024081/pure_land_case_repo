# Content Claim Register Schema

`content_claims` is the verification ledger for generated reader and creator content.

## Core Fields

```text
claim_id
text_id
article_id
sentence_index
character_start
character_end
claim_text
claim_type
support_relation
supporting_case_fact_ids
supporting_source_segment_ids
supporting_doctrinal_citation_ids
supporting_source_method_ids
attributed_to
uncertainty_required
uncertainty_preserved
entailment_status
contradiction_status
quotation_match_status
rights_status
review_status
review_notes
```

## claim_type

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

## support_relation

```text
direct
faithful_paraphrase
supported_inference
cross_source_synthesis
not_required
unsupported
```

## Check Statuses

```text
entailment_status: not_checked | entailed | partially_entailed | not_entailed
contradiction_status: not_checked | clear | possible_conflict | contradicted
quotation_match_status: not_applicable | not_checked | exact | normalized_exact | mismatch
review_status: pending | machine_passed | human_passed | needs_revision | rejected
```

## Hard Rules

1. Every non-rhetorical claim requires support.
2. `partially_entailed`, `not_entailed`, `possible_conflict`, `contradicted`, or `mismatch` blocks publication.
3. Case facts must cite normalized case facts or source segments.
4. Doctrinal claims and practical guidance must cite approved doctrinal citations.
5. Teacher interpretation must identify the teacher and source segments.
6. A sentence with both fact and doctrine must be split into separate claim records.
7. `machine_passed` means the claim passed the configured checks. It is not a declaration of historical truth or doctrinal consensus.
