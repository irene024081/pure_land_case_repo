# 已知问题 / Known Issues

本文件记录不会立即阻止证据处理、但会影响产品质量或规模化运行的问题。事实、版权、隐私或身份判断的硬性失败不放在这里，它们必须由对应 Run 阻断或拒绝发布。

This file tracks issues that do not immediately block evidence processing but affect product quality or operation at scale. Hard failures in factual support, rights, privacy, or identity are handled by the affected Run and must block publication.

## KI-001 读者文本表达较平 / Reader Prose Is Too Flat

`reader_generation/v1` 能生成带证据引用的忠实转述，但当前 M2A 文本的信息组织和叙事吸引力有限。它可以作为预览和检索文本，暂不视为最终编辑质量。

`reader_generation/v1` produces a faithful rendering with evidence references, but the M2A result has limited narrative shape and reader appeal. It is suitable as preview and retrieval text, not final editorial quality.

后续处理：建立固定样本和评分表，分析优秀法师讲稿的表达方法，创建 `reader_generation/v2`。新版仍不得补写无证据场景、心理活动、对话、因果或教理结论。

Follow-up: create a fixed evaluation set and rubric, study presentation methods from approved teacher transcripts, and create `reader_generation/v2`. The new version must still avoid unsupported scenes, motives, dialogue, causality, or doctrinal conclusions.

## KI-002 创作者角度过泛 / Creator Angles Are Too Generic

`creator_analysis/v1` 已提供受众、核心主张、证据引用和教理边界，但角度的区分度与选题精度不足。

`creator_analysis/v1` provides audience, core claim, evidence references, and doctrinal boundaries, but its angles are not yet distinctive or precise enough for topic selection.

后续处理：用真实选题任务评测相关度、差异度、可讲述性、所需背景和误读风险，再创建新版 Prompt。

Follow-up: evaluate relevance, distinctiveness, narrative usability, required context, and misinterpretation risk against real topic briefs before creating a new Prompt version.

## KI-003 AI Adapter 尚未自动执行 / AI Adapter Is Still Manual

Runner 会生成固定 Request 并校验 Response，但当前仍需在外部完成模型调用，再通过 `accept` 导入结果。Runner 不管理 API 密钥。

The Runner generates a fixed Request and validates the Response, but model execution still happens outside the Runner and is imported through `accept`. The Runner does not manage API keys.

## KI-004 正式数据提升尚未实现 / Canonical Promotion Is Not Implemented

通过的 Run Output 仍保存在本地运行目录；可提交的 Run Record 只保存状态和哈希。M2D 将增加幂等的数据提升命令和正式数据集。

Accepted Run Outputs still live in local runtime directories; tracked Run Records retain only status and hashes. M2D will add idempotent promotion commands and canonical datasets.

## KI-005 去重候选库是临时范围 / Deduplication Uses a Temporary Corpus Scope

`dedup_candidates/v1` 只扫描同一运行根目录下已完成的本地 Case Run，并使用精确结构化值评分。它可以稳定复现当前候选集，但可能漏掉名称缺失、日期模糊或只在叙事层相似的同案。

`dedup_candidates/v1` scans completed local Case Runs under the same runtime root and scores exact structured values. It makes the current candidate set reproducible, but may miss the same event when names are absent, dates are vague, or similarity exists only at the narrative level.

后续处理：M2D 建立持久化案例索引后，将检索范围改为正式数据集，并单独评测召回率。AI 仍只判断已提供候选，不得自行合并记录。

Follow-up: after M2D creates a persistent case index, query the canonical dataset and evaluate retrieval recall separately. AI still judges only supplied candidates and must not merge records automatically.

## 已解决 / Resolved

- Pipeline `0.1.2` 已让 `factual_check` 直接读取 `case_extraction`，避免事实检查只依赖生成文本中的引用 ID。 / Pipeline `0.1.2` gives `factual_check` direct access to `case_extraction`, so checking no longer relies only on evidence IDs repeated in generated text.
