# T02 Data Model

目标：定义 Source、Case、Person、Organization、Citation、Provenance Chain、Dedup Group 等核心实体。

当前原则：

1. Source 不等于 Case。
2. Case 不等于原文段落。
3. 同一个 Case 可以有多个 Citation。
4. 同一个 Case 可以有多个 Text Version：原文、白话译述、摘要、创作者摘要、搜索摘要。
5. 面向读者和面向创作者使用同一个 Case Detail，只切换显示模式。

Current operating documents:

- `ARCHITECTURE.md`：核心实体边界、处理层和存储职责。
- `DATA_PROCESSING_WORKFLOW.md`：当前六步数据处理流程。
- `SOURCE_ENTRY_PIPELINE.md`：Source adapter、目录同步和 Source Entry 抓取边界。
- `RAW_SOURCE_STORAGE.md`：原文保存、版权隔离、manifest、哈希验证和段落级溯源规则。
- `DHARMA_TALK_METHOD_WORKFLOW.md`：法师讲稿的方法分析、教理归因、Prompt 评测和风格边界。
- `DHARMA_CASE_COMMENTARY_WORKFLOW.md`：案例教理导读文章、逐条事实与教理验证、发布门槛和纠错流程。
- `M2_RIGHTS_REVIEW.md`：M2 现代来源的版权、平台条款证据、当前处理决定和待确认事项。
- `COPYRIGHT_RESEARCH_WORKFLOW.md`：版权术语、来源与单条研究、用途矩阵、生成文本检查和发布决定。
- `SEED_DATASET_PLAN.md`：第一批 50-100 个审核案例的来源、数量和验收标准。
- `../docs/history/`：M0/M1/M2 讨论稿和已被取代的早期流程，仅供追溯决策。
- `../schemas/case_register.md`：案例登记标准。
- `../schemas/citation_register.md`：引用和出处定位登记标准。
- `../schemas/source_entry_register.md`：来源条目登记标准。
- `../schemas/source_article_catalog.md`：每个来源的完整文章目录、批处理队列和管理员审核状态。
- `../schemas/source_segment_register.md`：原文段落、说话人、事实类型和段落级溯源标准。
- `../schemas/case_fact_register.md`：原子案例事实、报告者、观察者、事实类型、不确定性和原文依据。
- `../schemas/case_text_register.md`：原文、可读化文本、摘要、翻译登记标准。
- `../schemas/tag_register.md`：标签体系登记标准。
- `../schemas/creator_metadata_register.md`：创作者辅助字段登记标准。
- `../schemas/interpretation_angle_register.md`：精确创作角度、证据依据和法义边界登记标准。
- `../schemas/rights_review_register.md`：来源级和单条版权、平台条款、保存与公开展示审核记录。
- `../schemas/doctrinal_citation_register.md`：经论、祖师、传承和法师讲解的可用教理引用登记标准。
- `../schemas/content_claim_register.md`：生成内容逐条主张及其证据、蕴含、冲突和引文校验标准。
- `../schemas/dharma_commentary_register.md`：面向普通读者的案例教理导读文章登记标准。
- `../schemas/person_place_register.md`：人物和地点轻量登记标准。
- `../schemas/dedup_register.md`：疑似重复和同案判断登记标准。
