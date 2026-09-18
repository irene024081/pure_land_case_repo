# Dharma Case Commentary Register Schema

`dharma_case_commentaries` stores expressive, evidence-bound reader articles derived from cases and approved doctrinal sources.

## Core Fields

```text
article_id
case_id
title
language
target_audience
reader_question
main_teaching_point
interpretation_angle_id
independent_factual_account_text_id
case_fact_ids
source_segment_ids
doctrinal_citation_ids
source_method_ids
content
generation_run_id
prompt_version
claim_ids
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
notes
```

## review_status

```text
draft
claims_extracted
machine_checked
human_doctrinal_reviewed
needs_revision
rejected
ready_to_publish
```

## Rules

1. `dharma_case_commentary` is commentary, not source evidence.
2. Narrative effect may come from structure, pacing, questions, and explanation. It may not come from invented case details.
3. Every checkable sentence is covered by `content_claims`.
4. Case claims and doctrinal claims use different support types.
5. `unsupported_claim_count` and `contradicted_claim_count` must both equal zero for publication.
6. Display the article's AI assistance, review status, case source, and doctrinal sources.
7. Withhold the article when rights policy would make it a substitute for a restricted source.
