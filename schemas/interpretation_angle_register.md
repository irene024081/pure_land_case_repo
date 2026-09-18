# Interpretation Angle Register Schema

`interpretation_angles` stores evidence-linked ways to explain or use a case. It supports creator recommendation and future prompt evaluation.

It is analysis, not source evidence and not a doctrinal authority record.

## Core Fields

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
notes
```

## angle_type

```text
doctrinal_explanation
confidence_building
practice_guidance
family_guidance
source_literacy
ethical_caution
narrative_hook
comparative
other
```

## Rules

1. `core_claim` must be narrower than a general teaching theme and supported by cited source segments or normalized case facts.
2. `boundary_notes` states what the case cannot establish.
3. Dream, vision, fragrance, light, and post-death bodily signs must not be presented as independent proof of rebirth.
4. A teacher's interpretation must be attributed to that teacher and stored separately from event facts.
5. Future analysis of Dharma talks may contribute reusable `source_method_ids`. It must not silently imitate a living teacher's personal style.
6. Regenerated angles retain model, prompt, input, and review provenance.
