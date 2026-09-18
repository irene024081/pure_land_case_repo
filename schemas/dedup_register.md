# Dedup Register Schema

Dedup tracks whether multiple records may describe the same case.

AI can suggest duplicates. AI must not silently merge canonical cases.

## dedup_groups

```text
dedup_group_id
dedup_status
canonical_case_id
duplicate_confidence
review_status
notes
```

## dedup_members

```text
dedup_group_id
case_id
member_role
match_reasons
conflict_reasons
notes
```

## dedup_status

```text
not_checked
not_duplicate
possible_same_case
same_case
merged
needs_review
```

## duplicate_confidence

```text
high
medium
low
unknown
```

## member_role

```text
canonical
candidate_duplicate
parallel_version
repost_version
translation_version
not_duplicate_after_review
```

## Match Signals

Compare:

```text
person
place
event year or period
case type
key signs
witnesses
family structure
source chain
distinctive wording
summary similarity
original text similarity
```

## Named vs Unknown Person Rule

If one record names a person and another says only "某居士" or unknown, do not auto-merge.

Use:

```text
dedup_status = possible_same_case
duplicate_confidence = high | medium | low
```

Only mark `same_case` when enough non-name evidence aligns.

## Similar Motif Rule

Similar motifs are not enough.

Two cases both involving fragrance, body softness, or assisted chanting remain separate unless event-specific evidence aligns.
