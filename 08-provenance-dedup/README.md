# T08 出处追溯与去重 / Provenance And Deduplication

目标：建立来源追溯、转引链和案例去重规则。

Goal: establish rules for provenance tracing, transmission chains, and Case deduplication.

同一个案例可以有多个来源，但只应对应一个 case_id，并保留发现来源、引用来源、最早可确认出处。

One Case may have multiple Sources, but it should normally resolve to one `case_id` while preserving the discovery source, cited source, and earliest verifiable source.

Current T02 v0.2 representation: one `CASE` has one or more `SOURCE_OCCURRENCE` records. Identity comparisons belong in `../schemas/dedup_register.md`; reprints, translations, and other transmission links belong in `../schemas/source_occurrence_register.md`. The field mapping from historical Citations is in `../02-data-model/T02_V02_MIGRATION.md`.
