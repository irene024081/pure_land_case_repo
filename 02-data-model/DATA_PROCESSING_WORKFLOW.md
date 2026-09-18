# 数据处理工作流 / Data Processing Workflow

当前可执行工作流定义在 `../pipeline/pipeline.v1.2.json`。Runner 会根据每个 Run 记录的 `pipeline_version` 加载相应的历史定义。

The current executable workflow is `../pipeline/pipeline.v1.2.json`. The runner resolves historical definitions from each Run's recorded `pipeline_version`.

## 1. 来源配置 / Source Profile

登记 Source，完成来源级版权审核，并为它选择两类 Adapter。

Register the Source, complete its source-level rights review, and select two adapter types.

| 组件 / Component | 中文说明 | English Description |
|---|---|---|
| Inventory Adapter | 发现并登记来源中的文章、视频、书目条目等项目及其元数据。 | Discovers item metadata for articles, videos, book entries, and other source items. |
| Entry Adapter | 获取一个已选项目，并将正文整理为规范化 Source Entry。 | Captures one selected item and normalizes its content into a Source Entry. |

优先使用通用 Adapter。只有当通用 Adapter 无法准确表达来源结构或条目边界时，才增加 Source 专用代码。

Use a generic adapter when possible. Add Source-specific code only when generic adapters cannot represent the source structure or entry boundary accurately.

## 2. 目录同步 / Inventory Sync

将发现的每个项目写入 `data/source_catalogs/{source_id}/articles.csv`。被排除、无法访问、重复或不含案例的项目也应保留，以便审核目录覆盖范围。

Write every discovered item to `data/source_catalogs/{source_id}/articles.csv`. Preserve excluded, inaccessible, duplicate, and non-case items so inventory coverage remains auditable.

```text
固定来源 / fixed source:
首次完整回填 -> 版本、提取器或来源内容变化时重新运行
initial full backfill -> rerun when the edition, extractor, or source content changes

持续更新来源 / active source:
首次完整回填 -> 定期增量刷新
initial full backfill -> scheduled incremental refresh

结构不稳定来源 / unstable source:
增量刷新 -> 检查条目边界异常
incremental refresh -> boundary anomaly review
```

AI 可以协助分类项目并估计其中是否包含案例。脚本负责发现完整性、稳定 Source Key、依据精确标识去重，以及 CSV 持久化。

AI may classify items and estimate case likelihood. Scripts own discovery completeness, stable Source Keys, deduplication by exact identifiers, and CSV persistence.

## 3. 原文获取 / Capture

被选中的项目会转换为规范化 Source Entry。系统必须根据已登记的 manifest 校验原文哈希和载体哈希。版权规则决定原文如何保存，以及能否把完整内容发送给外部 AI Provider。

Selected items become normalized Source Entries. The system must verify raw-text and source-artifact hashes against the registered manifest. Rights policy determines storage scope and whether a complete item may be sent to an external AI provider.

## 4. 文章运行 / Article Run

Article Run 面向一篇完整 Source Entry。它先把全文切分为没有遗漏、重叠或顺序变化的 Source Segments，再识别其中零个、一个或多个 Case Candidates。

An Article Run processes one complete Source Entry. It first divides the full text into Source Segments without omissions, overlaps, or ordering changes, then detects zero, one, or many Case Candidates.

AI 只识别候选边界，不分配正式 Case ID。候选识别完成后，由程序复用已有 Case ID 或分配新 ID，并为每个候选创建独立 Case Run。

AI identifies candidate boundaries but does not assign canonical Case IDs. After detection, the program reuses an existing Case ID or allocates a new one and creates an independent Case Run for each candidate.

## 5. 案例运行 / Case Run

每个 Case Candidate 都有独立的 Case Run，依次处理原子事实、人物地点、标签、去重、读者文本、创作者分析、事实检查、版权检查和发布打包。

Each Case Candidate receives an independent Case Run covering atomic facts, persons and places, tags, deduplication, reader text, creator analysis, factual checking, rights checking, and publication packaging.

```text
case_extraction
-> entity_tagging
-> deduplication
-> reader_generation + creator_analysis
-> factual_check + rights_check
-> publication_packaging
```

所有事实、读者段落和创作角度都必须引用有效的 `case_fact_id` 或 `source_segment_id`。Case Fact 表达“来源记载了什么”，不表示系统已经证明事件在历史上真实发生。

Every fact, reader paragraph, and creator angle must cite valid `case_fact_id` or `source_segment_id` values. A Case Fact records what a source states; it does not mean the system has established the event as historical truth.

## 6. 审核 / Review

机器检查是必需步骤。常规低风险 Run 可以暂不进行人工审核；遇到去重身份不明确、新 baseline 审批、教理解释、隐私风险升级或版权规则例外时，需要人工审核。

Machine checks are required. Human review may remain pending for routine low-risk Runs, but it is required for ambiguous deduplication, new baseline approval, doctrinal interpretation, privacy escalation, or rights overrides.

通过机器检查表示输出符合当前 contract、证据引用和门槛规则，不表示对历史真实性、教理共识或法律结论作出最终保证。

Passing machine checks means the output satisfies the current contracts, evidence references, and gate rules. It is not a final guarantee of historical truth, doctrinal consensus, or legal status.

## 停止条件 / Stop Conditions

“停止”只作用于当前 Run 的相关 Stage 或自动发布，不代表停止整个项目，也不会删除已经通过的上游产物。修正输入、版权规则或 Prompt 后，应创建新 Run，不得覆盖旧结果。

“Stop” applies only to the affected Stage or automatic publication in the current Run. It does not stop the project or delete accepted upstream artifacts. After correcting an input, rights rule, or Prompt, create a new Run instead of overwriting the old result.

### 执行阻断 / Execution Block

下列问题使当前 Stage 无法可靠执行，应将 Run 标记为 `blocked` 或 `failed` 并记录原因：原文或必需字段缺失；Manifest、哈希或 Source 身份不一致；无法在不遗漏或虚构内容的情况下确定文章或案例边界；版权规则禁止把所需内容交给当前 Adapter。

The current Stage cannot run reliably when required source content or fields are missing, Manifest or hash identity fails, article or case boundaries cannot be established without omission or invention, or rights policy forbids sending required content to the selected Adapter. Mark the Run `blocked` or `failed` and record the reason.

### 发布门槛 / Publication Gate

以下问题允许保留检查结果，但发布包必须为 `withheld`，也不能提升为正式数据：事实检查出现 `unsupported` 或 `contradicted`；版权检查失败；去重结果仍为候选或需要人工判断；公开范围超过 Rights Review。这里的“证据边界不清”具体指无法确定某条主张由哪些 Source Segments 支持，或无法区分来源陈述、人物自述、转述与编者推断。

The outputs may be retained for diagnosis, but the publication package must be `withheld` and cannot be promoted when factual checking finds an `unsupported` or `contradicted` claim, rights checking fails, deduplication remains a candidate or needs human review, or public scope exceeds the Rights Review. An unclear evidence boundary means the system cannot identify the Source Segments supporting a claim or cannot distinguish source narration, subject report, hearsay, and editorial inference.

### 非阻塞质量问题 / Non-blocking Quality Issue

表达平淡、叙事不够吸引人、创作角度过泛或检索排序不理想，不属于证据或版权失败。只要事实与版权门槛通过，可以保留为预览输出，同时在 `../00-control/KNOWN_ISSUES.md` 登记，后续用新版 Prompt 和固定评测集重新生成。提高可读性不得通过增加无证据场景、心理活动、对话或教理结论实现。

Flat prose, weak narrative appeal, generic creator angles, or poor retrieval ranking are quality issues rather than evidence or rights failures. If factual and rights gates pass, retain the result as preview output, record the issue in `../00-control/KNOWN_ISSUES.md`, and regenerate later with a new Prompt version and fixed evaluation set. Readability must not be improved by inventing scenes, motives, dialogue, or doctrinal conclusions.
