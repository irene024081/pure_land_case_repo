# 净土案例资料库 / Pure Land Cases

长期项目：全球净土感应资料库。

Long-term project: a global database of Pure Land accounts and source evidence.

目标是在同一个 Git 仓库内完成 T00-T10：来源总目录、数据模型、古代文献、近现代刊物、中文网站、YouTube 与法师来信、多语种来源、出处追溯与去重、Agent 自动更新、发布界面。

The repository covers T00-T10: the global source directory, data model, ancient texts, modern periodicals, Chinese websites, YouTube and teacher letters, multilingual sources, provenance and deduplication, agent automation, and the publication interface.

**团队入口 / Team entry point:** [项目总览、当前进度、需求缺口与阶段验收](00-control/PROJECT_HUB.md) / [Project hub, verified progress, gap register, and milestone gates](00-control/PROJECT_HUB.md). Start there before using older plans or case drafts.

## 工作方式 / Working Method

1. 所有项目规则和总状态放在 `00-control/`。
   Store project-wide rules and status in `00-control/`.
2. 每个专题独立一个目录，按 `01-` 到 `10-` 编号推进。
   Keep each workstream in its numbered `01-` through `10-` directory.
3. 通用字段、枚举和评分标准放在 `schemas/`。
   Store shared fields, enumerations, and scoring standards in `schemas/`.
4. 可结构化数据放在 `data/`。
   Store structured data in `data/`.
5. 已被取代的方案和里程碑记录放在 `docs/history/`，不得作为当前执行说明。
   Preserve superseded designs and milestone records in `docs/history/`; do not use them as current operating instructions.

## 数据处理主链条 / Main Processing Pipeline

本项目采用可重跑、可检查、可替换模型的版本化 Pipeline。聊天中的临时输出不直接成为项目数据。当前机器可读阶段定义是 `pipeline/pipeline.v2.json`；历史 Run 仍按其记录的 `pipeline_version` 使用对应旧定义。执行说明位于 `09-agent-automation/README.md`。

The project uses a versioned Pipeline that can be rerun, inspected, and executed with replaceable models. Temporary chat output does not become project data directly. The current machine-readable stage definition is `pipeline/pipeline.v2.json`; historical Runs continue to use the definition recorded by their `pipeline_version`. Operating instructions are in `09-agent-automation/README.md`.

```text
来源配置与目录同步 / source profile and inventory sync
-> 原文获取与版权预检 / source capture and rights precheck
-> Article Run：分段与案例检测 / segmentation and case detection
-> 创建 Candidate Run / create Candidate Runs
-> 原子事实抽取、实体标记与去重 / facts, entities, and deduplication
-> 身份解决后分配或复用 Case ID / resolve identity, then assign or reuse Case ID
-> Source Occurrence 与传播关系 / Source Occurrence and transmission links
-> 读者文本与创作者分析 / reader generation and creator analysis
-> 独立事实与版权检查 / independent factual and rights checks
-> 确定性发布打包 / deterministic publication packaging
```

## 原则 / Principles

1. 脚本负责可复现地抓取和切分来源文本。
   Scripts capture and segment source text reproducibly.
2. `source_entries` 保存接近原文的条目，不等同于最终案例。
   `source_entries` retain source-faithful items; they are not final Cases.
3. 原文按版权状态保存到 public 或 Git 忽略的 restricted storage，并用 manifest 和哈希验证。
   Store source text in public or Git-ignored restricted storage according to rights status, verified by manifests and hashes.
4. `source_segments` 在段落或时间码层级区分事实、推断、梦境和教理说明。
   `source_segments` distinguish facts, inference, dreams, and doctrinal explanation at paragraph or timestamp level.
5. AI 只在固定 Stage 中提出语义结果；prompt、输入输出 contract、模型和运行记录必须版本化。
   AI produces semantic results only in defined Stages; prompts, input/output contracts, models, and Run records must be versioned.
6. 面向读者的教理导读使用独立流程：案例事实来自 Source Segments，教理判断来自审核过的 Doctrinal Citations。
   Reader-facing doctrinal commentary uses a separate workflow: case facts come from Source Segments, while doctrinal judgments come from approved Doctrinal Citations.
7. 导读文章中的每条事实、教理、引文和实践建议都进入 Content Claim Ledger；无依据、矛盾、错引或误归因会阻止发布。
   Every factual, doctrinal, quoted, or practical claim enters the Content Claim Ledger; unsupported, contradictory, misquoted, or misattributed claims block publication.
8. 版权研究分别判断内部保存、AI 处理、摘要、独立事实叙事、教理导读、翻译和数据分发，不能相互推定。
   Rights research evaluates internal retention, AI processing, summaries, independent factual accounts, doctrinal commentary, translation, and dataset distribution separately.
9. 生成和检查必须由不同 Stage 完成；确定性 Validator 决定是否通过，生成模型不能自行批准。
   Generation and checking occur in separate Stages; deterministic Validators decide whether a result passes.
10. 任何公开案例都必须能通过 Source Occurrence 追溯到 Source Item、Source Entry 和 Evidence Locator。
    Every public Case must trace through a Source Occurrence to a Source Item, Source Entry, and Evidence Locator.
11. Stage 失败会阻止后续发布；重跑必须创建新 Run，禁止静默覆盖旧产物。
    A failed Stage blocks publication; reruns require a new Run and never silently overwrite prior outputs.
12. 受限原文只有在 Rights Review 明确允许时，才能交给指定外部 AI Provider。
    Restricted source text may be sent to a named external AI Provider only when the Rights Review explicitly permits it.
13. 一个 Source Item 可以产生零个、一个或多个 Case；Case ID 只能在事实抽取和去重后的身份解决阶段分配。
    A Source Item may yield zero, one, or many Cases; Case IDs are assigned only after extraction, deduplication, and identity resolution.

## 专题目录 / Workstreams

| 编号 / ID | 目录 / Directory | 专题 / Scope |
|---|---|---|
| T00 | `00-control/` | 项目总控 / Project control |
| T01 | `01-global-source-directory/` | 全球净土感应来源总目录 / Global source directory |
| T02 | `02-data-model/` | 数据结构与分类体系 / Data model and taxonomy |
| T03 | `03-ancient-texts/` | 古代文献与出处追踪 / Ancient texts and provenance |
| T04 | `04-modern-periodicals/` | 近现代杂志与出版物 / Modern periodicals and publications |
| T05 | `05-modern-chinese-websites/` | 现代中文净土网站 / Modern Chinese websites |
| T06 | `06-youtube-teacher-letters/` | YouTube 与法师来信 / YouTube and teacher letters |
| T07 | `07-multilingual-sources/` | 全球多语种资料 / Multilingual sources |
| T08 | `08-provenance-dedup/` | 来源追溯与案例去重 / Provenance and deduplication |
| T09 | `09-agent-automation/` | Agent 自动化 / Agent automation |
| T10 | `10-publication-interface/` | 检索、阅读与发布界面 / Search, reading, and publication interface |
