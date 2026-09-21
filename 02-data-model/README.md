# T02 数据模型 / Data Model

目标：定义 Source、Source Item、Source Entry、Source Occurrence、Case、Person、Organization、身份判断与传播关系等核心实体。

Goal: define Source, Source Item, Source Entry, Source Occurrence, Case, Person, Organization, identity decisions, and transmission relations.

## 当前原则 / Current Principles

1. Source 不等于 Case。 / A Source is not a Case.
2. Case 不等于原文段落。 / A Case is not a source paragraph.
3. 同一个 Case 可以有多个 Source Occurrence。 / One Case may have multiple Source Occurrences.
4. 同一个 Case 可以有多个 Text Version：原文、白话译述、摘要、创作者摘要、搜索摘要。 / One Case may have original, reader rendering, summary, creator summary, and search-summary Text Versions.
5. 面向读者和面向创作者使用同一个 Case Detail，只切换显示模式。 / Reader and creator views use the same Case Detail with different display modes.

## 当前执行文档 / Current Operating Documents

- `ARCHITECTURE.md`：核心实体边界、处理层和存储职责。 / Core entity boundaries, processing layers, and storage ownership.
- `T02_V02_MIGRATION.md`：v0.1 字段迁移、显式未知与兼容规则。 / v0.1 field mapping, explicit unknown states, and compatibility.
- `DATA_PROCESSING_WORKFLOW.md`：当前六步数据处理流程。 / Current six-step data processing workflow.
- `SOURCE_ENTRY_PIPELINE.md`：Source Adapter、目录同步和 Source Entry 抓取边界。 / Source Adapters, inventory sync, and Source Entry capture boundaries.
- `RAW_SOURCE_STORAGE.md`：原文保存、版权隔离、manifest、哈希验证和段落级溯源规则。 / Raw-source retention, rights isolation, manifests, hash verification, and segment-level provenance.
- `DHARMA_TALK_METHOD_WORKFLOW.md`：法师讲稿的方法分析、教理归因、Prompt 评测和风格边界。 / Dharma-talk method analysis, doctrinal attribution, Prompt evaluation, and style boundaries.
- `DHARMA_CASE_COMMENTARY_WORKFLOW.md`：案例教理导读、逐条验证、发布门槛和纠错流程。 / Case commentary, claim-level verification, publication gates, and correction workflow.
- `M2_RIGHTS_REVIEW.md`：M2 现代来源的版权证据、处理决定和待确认事项。 / Rights evidence, current decisions, and open questions for modern M2 Sources.
- `COPYRIGHT_RESEARCH_WORKFLOW.md`：版权术语、用途矩阵、生成文本检查和发布决定。 / Copyright terminology, use matrix, generated-text checks, and publication decisions.
- `SEED_DATASET_PLAN.md`：第一批 50-100 个审核案例的来源、数量和验收标准。 / Sources, counts, and acceptance criteria for the first 50-100 reviewed Cases.
- `../docs/history/`：已被取代的讨论稿，仅供追溯决策。 / Superseded discussions retained for decision history only.

## Schema 索引 / Schema Index

- `../schemas/case_register.md`：案例登记。 / Case records.
- `../schemas/source_occurrence_register.md`：案例在来源中的出现、定位和传播关系。 / Case appearances, locators, and transmission links.
- `../schemas/citation_register.md`：历史 Citation 字段与迁移入口。 / Legacy Citation fields and migration entry point.
- `../schemas/source_entry_register.md`：来源条目。 / Source Entries.
- `../schemas/source_article_catalog.md`：完整文章目录、批处理队列和审核状态。 / Complete item catalogs, batch queues, and review status.
- `../schemas/source_segment_register.md`：原文段落、说话人和段落级溯源。 / Source segments, speakers, and segment-level provenance.
- `../schemas/case_fact_register.md`：原子事实、报告者、观察者和不确定性。 / Atomic facts, reporters, observers, and uncertainty.
- `../schemas/case_text_register.md`：原文、可读化文本、摘要和翻译。 / Original text, reader renderings, summaries, and translations.
- `../schemas/tag_register.md`：标签体系。 / Tag taxonomy.
- `../schemas/creator_metadata_register.md`：创作者辅助字段。 / Creator-facing metadata.
- `../schemas/interpretation_angle_register.md`：创作角度、证据和教理边界。 / Interpretation angles, evidence, and doctrinal boundaries.
- `../schemas/rights_review_register.md`：版权、平台条款、保存与展示审核。 / Rights, platform terms, retention, and display review.
- `../schemas/doctrinal_citation_register.md`：可用教理引用。 / Approved doctrinal citations.
- `../schemas/content_claim_register.md`：内容主张及证据、冲突和引文校验。 / Content claims, evidence, conflicts, and quotation checks.
- `../schemas/dharma_commentary_register.md`：普通读者教理导读。 / Reader-facing Dharma commentary.
- `../schemas/person_place_register.md`：人物和地点。 / Persons and places.
- `../schemas/dedup_register.md`：疑似重复和同案判断。 / Duplicate candidates and same-case decisions.
