# 面向用户的输出 / User-facing Outputs

本文区分当前 Pipeline 已经生成的数据、内部检查数据，以及尚未实现的产品界面。数据存在不等于网站页面已经完成。

This document separates data already produced by the Pipeline, internal review data, and product interfaces that have not been built. Available data does not imply that the website UI exists.

## 当前可展示 / Available For Display

| 用户 / User | Output | 当前内容 / Current Content | 状态 / Status |
|---|---|---|---|
| 普通读者 / General reader | `reader_generation.reader_title` | 案例标题，可选字段。 / Case title; currently optional. | M2A 已有 / available in M2A |
| 普通读者 / General reader | `reader_generation.reader_summary` | 一段简明概述。 / Concise summary. | 可用预览 / preview-ready |
| 普通读者 / General reader | `reader_generation.paragraphs` | 现代中文忠实转述，每段关联事实和原文分段。 / Faithful modern-Chinese rendering with fact and source-segment references per paragraph. | 可用预览，表达待优化 / preview-ready; prose needs revision |
| 研究者、读者 / Researcher, reader | `source_segmentation.segments` | 对应原文及定位信息，可支持原文展开与关键词高亮。 / Source text and locators for evidence expansion and keyword highlighting. | 数据已具备，界面未做 / data available; UI pending |
| 创作者 / Creator | `creator_analysis.creator_metadata` | 视频适配、叙事与风险等结构化指标。 / Structured video-fit, narrative, and risk metadata. | 可用预览 / preview-ready |
| 创作者 / Creator | `creator_analysis.interpretation_angles` | 选题角度、核心主张、受众、证据引用和教理边界。 / Topic angles, core claims, audience, evidence references, and doctrinal boundaries. | 可用预览，角度待优化 / preview-ready; precision needs revision |
| 所有用户 / All users | `publication_packaging.publish_status` | 控制公开、节录、内部或不发布。 / Controls public, excerpt-only, internal, or withheld display. | 已实现 / implemented |

公开页面只能读取通过事实和版权门槛的发布包。原文展示范围由 Rights Review 决定，不能因为技术上已保存全文就默认公开。

Public pages may read only publication packages that pass factual and rights gates. Source-text display scope comes from the Rights Review; retained full text is not automatically public.

## 内部使用 / Internal Only

- `case_extraction`：来源陈述的原子事实与证据定位。 / Atomic source claims and evidence locations.
- `entity_tagging`：人物、地点和检索标签。 / Persons, places, and retrieval tags.
- `deduplication`：候选同案比较及判断理由。 / Candidate identity comparisons and decision reasons.
- `factual_check`：逐条生成内容事实账本。 / Claim-level factual ledger for generated content.
- `rights_check`：逐项版权与展示范围判断。 / Per-output rights and display-scope decisions.

这些数据用于检索、审核和解释系统决定。除经过专门设计的出处与证据视图外，不应把内部 JSON 原样展示给普通读者。

These records support retrieval, review, and decision explanations. Raw internal JSON should not be shown directly to general readers except through a designed provenance or evidence view.

## 尚未完成 / Not Yet Implemented

- 按 Source、姓名、瑞相、修持、地点搜索，并在原文中高亮命中词。 / Search by Source, person, reported sign, practice, and place with source-text highlighting.
- 根据创作者的选题和思路推荐相关案例并解释排序理由。 / Recommend cases for a creator brief and explain ranking reasons.
- 经审核的教理导读文章与教理引用账本。 / Reviewed doctrinal commentary with a doctrinal citation ledger.
- 多语言翻译、对照阅读和翻译关系。 / Multilingual translations, parallel reading, and translation relations.
- 网站页面、导出格式和管理员审核界面。 / Website pages, export formats, and an administrator review interface.

当前质量限制统一记录在 `../00-control/KNOWN_ISSUES.md`。

Current quality limitations are tracked in `../00-control/KNOWN_ISSUES.md`.
