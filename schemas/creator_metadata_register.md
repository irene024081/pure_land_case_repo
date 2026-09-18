# Creator Metadata Register Schema

Creator metadata supports theme-to-case recommendation and creator brief generation.

It is not evidence and does not evaluate whether a case is true.

## Core Fields

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
primary_narrative_arc
turning_points
observable_changes
unresolved_questions
interpretation_angle_ids
review_status
notes
```

## Common Scale

```text
high
medium
low
unknown
```

## video_fit_level

```text
high
medium
low
not_recommended
unknown
```

## best_video_format

```text
short_video
long_video
lecture_segment
case_compilation
quote_only
not_recommended
unknown
```

## Rules

1. `video_fit` means video expression fit, not truth.
2. A case with low `video_fit` can still have high evidence value.
3. `recommended_usage` should say how to use the case without inventing facts.
4. `avoid_usage` should flag sensational, privacy-heavy, or doctrinally risky use.
5. `recommended_usage` is a short routing field. Detailed creator reasoning belongs in `interpretation_angles`.
6. Every interpretation angle must state its supporting segments and doctrinal boundary.
7. A broad theme such as `name_recitation` is not yet a usable angle. A usable angle identifies a claim, audience, evidence, structure, and limitation.
