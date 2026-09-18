# Tag Register Schema

Tags support search, filtering, recommendation, and homepage entry points.

Case type, rebirth sign, and teaching theme must remain separate.

## Core Fields

```text
tag_id
tag_type
slug
label
original_label
parent_tag_id
description
status
notes
```

## tag_type

```text
case_type
rebirth_sign
teaching_theme
audience_context
source_feature
content_warning
language
period
region
```

## Initial case_type Values

```text
rebirth_signs
foreknowledge_of_death
seeing_amitabha_or_pure_land
dream_or_vision
assisted_chanting
illness_recovery
disaster_escape
dedication_or_transfer
animal_rebirth
ghost_spirit_related
other_worldly_benefit
doctrinal_or_historical_only
unknown
```

## Initial rebirth_sign Values

```text
fragrance
light
music
body_softness
relics
calm_death
seated_passing
standing_passing
clear_mind_at_death
seeing_amitabha
seeing_lotus
auspicious_dream
unknown
```

## Initial teaching_theme Values

```text
faith_and_vow
name_recitation
assisted_chanting_importance
family_support_at_death
preparation_for_death
do_not_disturb_dying_person
ordinary_people_can_practice
power_of_dedication
cause_and_effect
compassion_for_animals
source_verification
unknown
```

## Status

```text
active
candidate
deprecated
merged
```

## Rules

1. Add candidate tags freely during extraction.
2. Promote tags to active only after repeated use or clear product value.
3. Do not use teaching themes as proof of doctrine; they are recommendation aids.
