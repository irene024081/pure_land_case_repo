# Legacy M2 Pilot Data

This folder preserves pre-pipeline draft case packs. They are historical review fixtures, not canonical data or import inputs.

Only the public-domain CASE000001 pack is tracked. Modern CASE000002-CASE000005 packs remain under ignored `data/source_entries/restricted/legacy_m2/` because they contain restricted source material.

Default chain:

```text
sources
-> source extractor scripts
-> source_entries
-> AI case extraction job
-> machine check
-> draft case packs
```

Rules:

```text
Draft case packs are review materials, not final import files.
Each pack should include draft rows for the M2-required tables.
Original evidence, reader rendering, creator metadata, dedup status, copyright risk, and privacy risk must be visible.
Each pack must record extraction provenance, including source URL, locator, extraction command or script, and manual judgment steps.
Each pack should point back to one or more `source_entry_id` values when available.
AI output must not replace raw extracted source text.
Raw source artifacts must have a storage manifest and verified hash. Restricted modern material stays outside Git.
Reader renderings must distinguish condensed drafts from full supported accounts.
Creator assistance must include evidence-linked interpretation angles, not only broad themes and generic usage notes.
After the first five cases, pause for schema and workflow review before continuing.
```

First review outcome:

```text
raw source retention model added
four modern source artifacts moved to restricted local storage
five tracked source-entry manifests added
paragraph-level source_segments schema added
narrative analysis added to all five cases
two draft interpretation angles added to each case
condensed reader renderings and creator summaries marked for regeneration
```

Current draft cases:

```text
CASE000001: Chen Yu recites Amitabha while spinning thread
CASE000002: A-dong recites Amitabha for one hundred days
CASE000003: Family guides grandmother to Pure Land
CASE000004: Yanliang follows dream guidance to Donglin Temple
CASE000005: Ms Mak guides her mother with Amitabha recitation
```
