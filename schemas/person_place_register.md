# Person And Place Register Schema

Persons and places are lightweight in M0. They can become richer later.

## Persons

```text
person_id
display_name
original_name
name_status
anonymity_level
notes
```

## name_status

```text
known
partial
anonymous
unknown
redacted
```

## anonymity_level

```text
public
name_redacted
sensitive
private_internal
unknown
```

## case_persons

```text
case_id
person_id
person_role
confidence
notes
```

## person_role

```text
reborn_person
witness
recorder
speaker
teacher
relative
editor
translator
source_author
unknown
```

## Places

```text
place_id
display_name
original_name
place_type
region
modern_country_or_region
confidence
notes
```

## place_type

```text
country
region
province
city
county
temple
home
hospital
unknown
```

## case_places

```text
case_id
place_id
place_role
confidence
notes
```

## place_role

```text
event_place
death_place
source_place
publication_place
organization_place
unknown
```

## Rules

1. Unknown persons and places are valid records when needed.
2. Do not infer exact locations from vague source text.
3. Keep the source wording in notes when normalizing a place.
