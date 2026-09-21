# Project Hub / 项目总览与执行计划

**Last verified / 核对日期:** 2026-09-21  
**Audience / 读者:** 项目负责人、非技术背景协作者、开发者与接手工作的 AI。 / Project owner, nontechnical stakeholders, developers, and incoming AI agents.  
**Current state / 当前状态:** 产品与数据流程已有设计，网站尚未开发；只有一条历史案例拥有已接受的完整 Pipeline baseline。Pipeline 0.2.0 的迁移重放停在人工身份审核。 / Product and data workflows are designed, but no website exists. Only one historical Case has an accepted full Pipeline baseline. The Pipeline 0.2.0 migration replay awaits human identity review.  
**Next decision / 下一项决定:** 项目负责人确认 `ENT000001-CAND0001` 是否复用 `CASE000001`，并提供审核记录使用的姓名或代号。 / The project owner must decide whether `ENT000001-CAND0001` reuses `CASE000001` and provide a reviewer name or identifier.

本页是团队入口，说明产品目标、已核实进度、缺口、待决定事项、执行顺序和验收标准。设计文档的存在不代表功能已运行。[进度记录](PROJECT_STATUS.md)与[下一步细节](NEXT_STEPS.md)保留补充历史；跨项目路线图以本页为准。

This is the team entry point. It describes the intended product, verified progress, gaps, decisions, sequence of work, and acceptance criteria. A design document is not evidence that a feature is running. The current [status log](PROJECT_STATUS.md) and [next-step detail](NEXT_STEPS.md) provide additional history; this page owns the cross-project roadmap.

## 1. One-minute Brief / 一分钟了解项目

本项目要把分散在古籍、期刊、网站、视频、来信和多语种资料中的净土案例，整理为可检索、可阅读、可核对出处的资料库。普通读者可以按来源、人物、瑞相或主题寻找案例；法师和视频创作者可以先提出选题，再获得有证据、有适配理由和风险提示的案例推荐。研究整理者可以追踪同案、转载、译本和来源链。

The project organizes Pure Land accounts scattered across historical texts, periodicals, websites, videos, letters, and multilingual sources into a searchable, readable database with traceable citations. Readers can search by source, person, reported sign, or theme. Teachers and video creators can start with a topic and receive cases with evidence, fit reasons, and cautions. Researchers can trace shared identities, reposts, translations, and source chains.

产品有两个同等重要的入口：**普通读者搜索与阅读**、**法师和创作者按主题配例**。两者使用同一个有证据支撑的 Case 记录与详情页。系统不判定历史真实性或教理，不虚构案例，也不因文章可以在线访问就推定具有再利用许可。详见[产品定义](../10-publication-interface/PRODUCT_DEFINITION.md)和 [PRD](../10-publication-interface/PRD_DRAFT.md)。

The product has two equal first-screen workflows: **reader search and reading**, and **theme-to-case assistance for teachers and creators**. Both use the same evidence-backed Case record and detail page. The system does not establish historical truth, decide doctrine, invent a case, or grant rights merely because a text is accessible online. See the [product definition](../10-publication-interface/PRODUCT_DEFINITION.md) and [PRD](../10-publication-interface/PRD_DRAFT.md).

**尚未上线 / Not yet a public product:** 目前没有公开网站、正式案例数据库、搜索索引、推荐服务、选题篮或自动调用 AI API 的 Adapter。现有五个 Pipeline 之前的案例包是历史草稿，不是五个已验收案例。 / There is no public website, canonical case database, production search index, recommendation service, creator basket, or automatic AI API adapter. The existing five pre-Pipeline case packs are historical drafts, not five accepted Cases.

## 2. How To Read Progress / 进度口径

| 状态 / Label | 含义 / Meaning |
|---|---|
| `done` | Deliverable exists and its stated checks passed. / 有产物并通过对应检查。 |
| `partial` | Some artifacts or code exist, but the milestone exit gate has not passed. / 有局部成果，未通过阶段验收。 |
| `blocked` | A named decision, rights restriction, or missing input prevents the next dependent step. / 有明确阻断条件。 |
| `planned` | Documented intention without executable or accepted output. / 有设计，无可验收产物。 |
| `deferred` | Intentionally outside the next release. / 明确暂缓。 |

证据优先顺序：已保存的 Source Entry 与校验通过的 Manifest；不可覆盖的 Pipeline Request/Response 和 Run 状态；已接受的 baseline；将来产生的正式数据提升记录；最后才是计划文档。历史案例包、通过的单元测试和 AI 草稿各自只能证明不同的事情，单独一项都不能证明可公开发布。

Evidence precedence: retained Source Entry and verified Manifest; immutable Pipeline Request/Response and Run status; accepted baseline; canonical promotion record when available; then planning documents. A historical case pack, a passing unit test, and an AI-generated draft each prove different things. None alone proves public-release readiness.

本次审计使用了当前项目中可见的对话与仓库资料。先前提供的[初始讨论](https://chatgpt.com/share/6aa8a227-9994-83ee-92ca-36f3ca9523f4)和[后续 T02 意见](https://chatgpt.com/share/6aace210-6800-83ee-a140-1621caf98ca7)在 2026-09-21 无法读取，因此本页**不宣称**掌握其完整内容。取得对话导出后，应与第 5 节核对并补入遗漏决定，之后才能称为完整对话审计。

This audit used the conversation visible in this project and the repository. The two previously supplied ChatGPT pages, [initial discussion](https://chatgpt.com/share/6aa8a227-9994-83ee-92ca-36f3ca9523f4) and [later T02 feedback](https://chatgpt.com/share/6aace210-6800-83ee-a140-1621caf98ca7), could not be fetched on 2026-09-21. Their full contents are **not** asserted here. If exported transcripts become available, compare them with section 5 and add any missing decisions before claiming a complete conversation audit.

## 3. People, Product, And Evidence / 用户与数据链

| 用户 / User | 首要任务 / First task | 第一版结果 / MVP result |
|---|---|---|
| 普通读者 / General reader | 按来源、姓名、瑞相、主题或关键词搜索。<br>Search by source, name, sign, theme, or keyword. | 高亮结果、可读叙事、允许展示的原文证据、出处与相关案例。<br>Highlighted result, readable account, permitted original evidence, provenance, and related cases. |
| 法师、弘法者 / Dharma teacher or preacher | 从教理主题和受众出发。<br>Start with a teaching topic and audience. | 按相关性排序的案例、具体适配理由、证据、教理边界与使用提醒。<br>Ranked cases with specific fit reasons, evidence, doctrinal boundaries, and use cautions. |
| 视频策划、剪辑、运营 / Video planner or editor | 为目标形式和时长选择案例。<br>Select cases for a format and duration. | 选题篮和关联证据的创作提纲，不自动发布讲稿。<br>Case basket and evidence-linked creator brief, not an auto-published script. |
| 研究整理者 / Researcher or source editor | 核对来源、身份、版权与修订。<br>Check sources, identity, rights, and corrections. | 文本版本、出现记录与审核队列；公开与内部视图分离。<br>Version and occurrence trail with a review queue; public and internal views remain distinct. |

```text
SOURCE (书、网站、频道 / book, site, channel)
  -> SOURCE_ITEM (单篇文章、古籍条目、视频或来信 / article, book entry, video, or letter; catalog column article_id)
  -> SOURCE_ENTRY (保存的规范化原文、清单和版权规则 / retained normalized text, manifest, and rights policy)
  -> SOURCE_SEGMENT (原文段落或视频时间码 / exact paragraph or timestamp evidence)
  -> CANDIDATE (待确认案例，尚无 Case ID / possible episode, no Case ID yet)
  -> CASE_FACT + ENTITY_TAGGING + DEDUPLICATION
     (原子事实、实体标记、去重 / facts, entity tagging, deduplication)
  -> CASE_RESOLUTION (分配新 ID 或经审核复用 / new ID or reviewed reuse)
  -> CASE (底层叙事事件 / narrated episode) + SOURCE_OCCURRENCE (本次出现和定位 / appearance and locator)
  -> 读者与创作者输出 / reader and creator outputs
  -> 事实与版权检查 / factual and rights checks
  -> 发布包 / publication package
  -> 正式数据提升 / canonical promotion (未实现 / not implemented)
  -> 搜索与产品界面 / search and product surfaces (未实现 / not implemented)
```

原始来源始终是证据。Case Fact 记录的是**来源说了什么**，不等于项目已独立证实事件。一个 Case 可以有多个 Source Occurrence。转载或翻译描述出现记录之间的传播关系，不能自动证明两个叙事属于同一事件。来源中提及但尚未取得的上游材料，应标为 `unresolved_upstream`。详细规范见[架构](../02-data-model/ARCHITECTURE.md)、[v0.2 迁移映射](../02-data-model/T02_V02_MIGRATION.md)和[处理流程](../02-data-model/DATA_PROCESSING_WORKFLOW.md)。

The raw source remains the evidence. A Case Fact records **what a source says**, not whether the event has been independently proven. Multiple Source Occurrences can describe one Case. A reprint or translation relation is about transmission between occurrences, not automatically about event identity. A source named inside another source is `unresolved_upstream` until captured and checked. The [architecture](../02-data-model/ARCHITECTURE.md), [v0.2 migration map](../02-data-model/T02_V02_MIGRATION.md), and [workflow](../02-data-model/DATA_PROCESSING_WORKFLOW.md) are the detailed specifications.

| 术语 / Term | 通俗解释 / Plain meaning |
|---|---|
| Manifest | A receipt describing a saved source object and its integrity hashes. / 原文文件的存储及校验清单。 |
| Candidate | A possible Case detected in one item; identity is not settled. / 从文章中找到的待确认案例。 |
| Case | The project ID for one underlying narrated episode. / 同一底层故事的登记身份。 |
| Source Occurrence | Where that Case appears in one specific item, with a locator. / 这个故事在某篇文章或视频中的一次出现。 |
| Run | One versioned execution with saved inputs, outputs, checks, and status. / 一次有版本与记录的数据处理。 |
| Baseline | An accepted example used to detect regressions; it is not the full database. / 用于比较质量的已验收样本。 |
| Promotion | Moving checked Run outputs into the official searchable dataset. / 将通过检查的结果提升为正式数据。 |
| Publication gate | The final factual, rights, privacy, and identity checks for a specific public output. / 针对某项公开内容的发布审核。 |

面向读者的文本分工不同：短摘要用于检索，忠实可读版用于完整阅读，原文按版权规则展示，需要时另写独立事实叙事，并把教理导读单独保存。表达性文章可以借鉴已审核的讲解方法，但每条事实、教理、引文和实践建议都要有独立依据。译文是派生文本，不是新的原始见证。

Reader text has distinct jobs: a short summary for search, a faithful readable account, rights-limited original evidence, an independently written factual account where needed, and a separate doctrinal commentary. A compelling article may use a reviewed teaching method, but every factual, doctrinal, quoted, and practical claim needs its own support. Translation is a derived text, never a new source witness.

## 4. Verified Snapshot / 已核实的现状

| 范围 / Area | 已有证据 / Current evidence | 状态与边界 / Status and limit |
|---|---|---|
| 来源短名单 / Source shortlist | M2 已登记 `SRC0001`-`SRC0005` 五个来源；见[短名单](../01-global-source-directory/M1_SOURCE_SHORTLIST_LOCKED.md)。<br>Five M2 sources registered; see the [shortlist](../01-global-source-directory/M1_SOURCE_SHORTLIST_LOCKED.md). | `partial`：尚未建立全球覆盖。<br>Global coverage has not been built. |
| 逐来源目录 / Per-source inventory | 五个 `articles.csv` 各只有**一条**试点项目；五个 `source.yml` 均为 `inventory_status: partial`。<br>Each catalog has **one** pilot item; all five profiles report partial coverage. | `partial`：已有目录文件，不等于来源文章目录完整。<br>Catalog files exist, but inventories are incomplete. |
| 已保存证据 / Stored evidence | 五份 Source Entry Manifest 通过 `verify_source_entry_storage.py`；一条公开规范化条目、四条本地受限条目。<br>Five Manifests passed storage verification; one public and four locally restricted normalized entries. | `partial`：现代全文不是公开数据，本地受限文件不进入 Git。<br>Modern full text is not public; local restricted files are not in Git. |
| 历史试点 / Historical pilot | Pipeline 建立前有五个案例草稿包；只有公版 `CASE000001` 包进入[历史目录](../data/legacy_m2/README.md)的 Git 跟踪。<br>Five pre-Pipeline draft packs exist; only public-domain `CASE000001` is tracked. | 历史审核样本，不是五个正式提升的 Case。<br>Historical samples, not five promoted Cases. |
| 已接受 baseline / Accepted baseline | [M2A baseline](../data/baselines/M2A_ENT000001_P011.json)：Pipeline 0.1.1、8 段原文、22 条事实、4 段读者文本、2 个创作角度、22 条已检查主张，unsupported 与 contradicted 均为 0。<br>Pipeline 0.1.1 with 8 segments, 22 facts, 4 reader paragraphs, 2 creator angles, 22 checked claims, and zero unsupported/contradicted claims. | `done`：机器验收的回归样本，不是网站或经人工批准的正式 Case。<br>Machine-accepted regression fixture, not a website or human-approved canonical record. |
| 当前 Pipeline / Current Pipeline | [Pipeline 0.2.0](../pipeline/pipeline.v2.json) 与 Runner 已实现先建 Candidate、后解决身份及 Source Occurrence。<br>Pipeline 0.2.0 and Runner implement Candidate-first resolution and Source Occurrence. | `partial`：2026-09-21 有 27 项测试通过，但尚无已接受的 v0.2 真实端到端 Run。<br>27 tests passed; no accepted end-to-end real v0.2 Run. |
| 当前 M2A 重放 / Current M2A replay | `RUN-ENT000001-M2A-T02V02` 重放旧分段并转换事实与标签 ID；去重与 `CASE000001` 比较结果为 `same_case`。<br>The Run replayed historical segmentation and migrated fact/tag IDs; dedup returned `same_case`. | `blocked` 于 `case_resolution: review_required`；本 Run 未复用 Case ID，也未评估新 v2 Prompt 的生成质量。<br>No Case ID was reused; this replay does not evaluate fresh v2 extraction quality. |
| 版权 / Rights | `SRC0001` 古籍可用于试点；四个现代来源的公开或翻译权限受限或未定，见 [M2 版权审核](../02-data-model/M2_RIGHTS_REVIEW.md)。<br>`SRC0001` historical text is available for the pilot; four modern Sources have restricted or unresolved rights. | **不得推定**现代全文、大篇幅翻译或表达性转述可以公开。<br>Public full text, substantial translation, and expressive retelling are **not** presumed allowed. |
| 产品 / Product | 已有[产品定义](../10-publication-interface/PRODUCT_DEFINITION.md)、[PRD](../10-publication-interface/PRD_DRAFT.md) 与[输出清单](../10-publication-interface/OUTPUT_INVENTORY.md)。<br>Product definition, PRD, and output inventory exist. | `planned`：没有前端、搜索、推荐或管理员界面。<br>No frontend, search, recommendation, or admin UI. |
| 仓库发布 / Repository release | 核对时工作区仍有未提交的 v0.2 代码、文档和 Run Record。<br>The working tree contains uncommitted v0.2 code, docs, and Run Records. | 不得称为已推送或打标签的版本；本次文档修改不包含提交或推送。<br>Do not call it a pushed or tagged release; this edit does not commit or push. |

2026-09-21，27 项单元测试、五份 Catalog 校验和五份存储 Manifest 校验通过。这些检查只验证代码路径与已保存对象的完整性，不批准现代来源的公开再利用，也不验证新版模型文本的读者质量。

The 27 unit tests, five catalog validations, and five storage-manifest checks passed on 2026-09-21. These checks validate code paths and retained-object integrity. They do not approve a modern source for public reuse or validate the reader quality of a new model response.

### Workstream Map / T00-T10 状态

| 专题 / Track | 现状 / Progress | 下一项产物 / Next delivery |
|---|---|---|
| T00 总控 / Control | 已有状态、问题和里程碑记录。<br>Status, issue, and milestone notes exist. | 持续更新本页与证据关联的进度。<br>Keep this hub and evidence-linked status current. |
| T01 全球来源 / Global sources | 五个试点来源，目录覆盖不完整。<br>Five pilot Sources with partial catalogs. | 扩大来源调查并完成明确范围的目录。<br>Broader discovery and complete scoped inventories. |
| T02 数据模型 / Data model | v0.2 Schema 和迁移提案已写。<br>v0.2 schemas and migration proposal exist. | 审核迁移并实现正式数据提升。<br>Review migration and implement canonical promotion. |
| T03 古籍 / Ancient texts | `SRC0001` 提取脚本和一个已接受 baseline。<br>`SRC0001` extractor and one accepted baseline. | 完成选定章节目录并测试更多条目。<br>Complete selected-section inventory and test more items. |
| T04 近现代刊物 / Modern periodicals | `SRC0002` 试点抓取及版权初审。<br>`SRC0002` pilot capture and rights review. | 建立页码、期号目录并确认允许用途。<br>Build page/issue catalog and permitted-use decision. |
| T05 现代中文网站 / Modern Chinese sites | `SRC0003`、`SRC0004` 已试点抓取。<br>`SRC0003`/`SRC0004` pilot captures exist. | 可复用的网站目录 Adapter 与出处测试。<br>Reusable archive inventory and provenance tests. |
| T06 视频与来信 / Video and letters | 只有存储与字幕策略。<br>Storage and transcript policy only. | 一个版权允许、带时间戳的字幕试点。<br>One rights-cleared timestamped transcript pilot. |
| T07 多语言 / Multilingual | 有受限英文试点与翻译模型设计。<br>Restricted English pilot and translation model design. | 选一个开放许可或已获授权的第二语言来源。<br>Select an open or permission-cleared second-language source. |
| T08 出处与去重 / Provenance and dedup | 已有本地候选检索与 v0.2 出现模型。<br>Local retrieval and v0.2 Occurrence model exist. | 持久化跨库比较及经审核的传播图。<br>Persistent corpus comparison and reviewed occurrence graph. |
| T09 Agent 自动化 / Agent automation | Runner、Prompt、Contract 和测试有版本；模型调用仍手动。<br>Versioned Runner, prompts, contracts, and tests; model calls remain manual. | 真实未见样本 Run 与可替换 Provider 的任务 Adapter。<br>Unseen real Runs and provider-neutral job adapter. |
| T10 发布界面 / Publication | 已有产品定义、PRD 和输出设计。<br>Product, PRD, and output designs exist. | 搜索推荐原型，然后可用网站。<br>Search/recommendation prototype, then usable website. |

## 5. Requirement And Gap Register / 对话需求与缺口

`D` 表示现有文档已设计但未交付；`U` 表示定义仍不足；`B` 表示目前有明确阻断。G01-G14 汇总对话和产品文档中的需求；G15-G18 是从团队协作和公开发布推导出的工程前提，负责人接受前仅为提议。G05 中的重试和成本记录也是建议实现方式。关闭一项缺口必须提供阶段验收证据，不能只改状态标签。

`D` means designed in existing documents but not delivered; `U` means insufficiently specified in existing documents; `B` means presently blocked. G01-G14 consolidate conversation and product-document requirements. G15-G18 include engineering prerequisites inferred from team collaboration and public release; they are proposals until the project owner accepts their scope. Retry/cost logging in G05 is also a proposed implementation detail. Each row must be closed by the milestone's evidence, not by rewriting its status label.

| ID | 需求 / Requirement | 当前缺口 / Gap | 状态 / State | 目标阶段 / Target |
|---|---|---|---|---|
| G01 | 法师先提出选题，系统给出有具体理由和边界的案例推荐。<br>A teacher starts with a topic and receives cases with specific fit reasons and limits. | 尚无检索排序服务或经过评测的推荐任务。<br>No retrieval/ranking service or evaluated recommendation tasks. | D | M4-M5 |
| G02 | 读者按来源、主体姓名、见证者、瑞相和关键词搜索，并查看高亮原文。<br>Readers search by Source, subject, witness, signs, and words, then inspect highlighted evidence. | 只有原文分段和产品要求，没有索引或界面。<br>Source segments and requirements exist, but no index or UI. | D | M4-M5 |
| G03 | 同一 Case Detail 支持读者和创作者模式，并提供选题篮与创作提纲。<br>One Case Detail supports reader/creator modes, a basket, and a creator brief. | 尚无页面、选题篮或提纲生成器。<br>No page, basket, or brief generator. | D | M5 |
| G04 | 批量处理前形成完整且可审核的项目目录；刷新不能抹掉已移除项目。<br>Keep a complete reviewable item inventory before bulk work; refresh must retain removed items. | 五个目录只有试点行，缺少通用目录 Adapter 和差异检查。<br>Five catalogs have only pilot rows; generic inventory adapters and diff workflow are absent. | D | M2C |
| G05 | 从 10 条扩到 20 条时沿用相同的版本化任务，并可替换 AI Provider。<br>Scale from 10 to 20 Cases with the same versioned jobs across AI providers. | Prompt/Contract 已有，模型调用、重试、成本记录和批量恢复仍手动或未定义。<br>Prompts/contracts exist; invocation, retries, cost logs, and recovery are manual or unspecified. | D/U | M2B-M2D |
| G06 | 抽取后判断身份；同案及有名/无名疑似同案要复核，传播关系另记。<br>Resolve identity after extraction; review named/unknown possible matches and separate transmission. | v0.2 代码已有，当前 Run 待人工决定，跨库召回仅本地且偏重精确匹配。<br>v0.2 code exists; replay awaits human review and corpus recall is local and exact-match-heavy. | B/D | M2A-M2D |
| G07 | 机器检查必需；日后人工纠错不能静默覆盖证据。<br>Require machine checks and preserve evidence during later human correction. | 有门槛概念，没有持久审核队列、修订传播或下架工具。<br>Gate concepts exist; durable review queue, correction propagation, and takedown tools do not. | D | M2D-M5 |
| G08 | 分别按来源、单项、存储对象和生成输出决定保存、AI 处理、引用、摘要、转述、翻译和分发权限。<br>Decide retention, AI use, quotation, summary, rendering, translation, and distribution per Source, item, object, and output. | 四个现代来源缺明确许可或最终法律依据；公开输出过滤和法律复核流程不完整。<br>Four modern Sources lack permission or final legal basis; output filtering and legal review operations are incomplete. | B/D | 全阶段 / Every stage |
| G09 | 文言、口述、第一人称和现代长文按不同方式可读化，不新增事实。<br>Adapt classical, oral, first-person, and long modern text without invented facts. | `reader_generation/v1` 忠实但平淡、有时太短；缺按来源形态划分的固定质量评测。<br>v1 is faithful but flat or condensed; no source-form quality rubric exists. | D | M3-M4 |
| G10 | 创作角度明确法义或信心切入点、受众、结构、依据和边界。<br>Creator angles specify teaching/confidence use, audience, structure, evidence, and boundary. | `creator_analysis/v1` 角度仍泛，尚无经评测的 v2 Prompt。<br>v1 angles remain generic; no evaluated v2 prompt. | D | M3-M4 |
| G11 | 导读结合已检查案例事实与独立审核的教理引用；法师讲座提供方法，不冒充教理依据或复制风格。<br>Commentary uses checked case facts and approved doctrine; talks provide methods, not unverified doctrine or copied style. | 有流程和 Schema，没有批准的教理库、方法库或完整导读 Run。<br>Workflows and schemas exist, but no approved citation/method corpus or full commentary Run. | D | M6，M3 试点 / M6, pilot in M3 |
| G12 | 多语言版本保留原语言证据，并单独检查翻译与改编许可。<br>Multilingual versions retain original-language evidence and separate translation/adaptation rights. | 没有已接受译文；`SRC0005` 限制公开大篇幅翻译。<br>No accepted translation; `SRC0005` restricts substantial public translation. | B/D | M3/M6 |
| G13 | 视频优先保存带时间戳字幕，不默认归档大视频文件。<br>Prefer timestamped transcripts; do not archive full video by default. | 已有存储规则，没有视频/来信 Source Item 或字幕评测。<br>Storage rule exists; no captured video/letter item or transcript evaluation. | D | M6 |
| G14 | 来源写出姓名时不自动匿名；现代敏感细节单独审核。<br>Do not automatically anonymize named source subjects; review sensitive modern details separately. | 早期对话已确定默认值，但单项例外和公开遮蔽标准仍不清。<br>The default was discussed, but item-level exceptions and public redaction criteria remain unclear. | U | M3 公开前 / Before M3 public outputs |
| G15 | 其他机器上的成员可复现获准的 Run，Git 不暴露受限全文。<br>Another team member can reproduce an authorized Run without Git exposing restricted full text. | 受限对象与完整 Run 载荷仅本地保存；未决定安全共享、授权、备份与恢复。<br>Restricted objects and full Run payloads are local; secure sharing, access, backup, and recovery are undecided. | U | M2D |
| G16 | 搜索、推荐与生成文本不得在片段、响应、日志或导出中泄露受限原文。<br>Search, recommendation, and generated text must not leak restricted source text in snippets, payloads, logs, or exports. | 版权预检保护模型输入，但公开 API、索引和导出边界尚无实现。<br>Rights precheck protects model input; public API/index/export boundary is absent. | U | M4-M5 |
| G17 | 用读者、法师、创作者、研究者的真实任务评估产品，不只看 Schema 是否通过。<br>Evaluate user tasks across personas, not only schema pass rates. | PRD 有目标，但缺固定选题、人工评判样本和验收负责人。<br>PRD has goals, but no fixed briefs, judged examples, or acceptance owner. | U | M4-M5 |
| G18 | 扩容和更换 Prompt 后，来源目录、去重、文本版本与出处保持稳定。<br>Keep inventories, identity, text versions, and provenance stable as sources and prompts change. | 缺正式数据集、ID 别名、版本差异及回滚/提升工具。<br>No canonical store, ID aliases, version diff, or rollback/promotion tooling. | D | M2D-M7 |

产品定义将收藏、分享与引用案例列为用户任务，但这些功能不在已锁定的 MVP 功能表中。M5 规划时确定首版范围，不能把它们说成已承诺交付。

Reader bookmarking, sharing, and citation export appear as user tasks in the product definition but are not in the locked MVP feature list. Decide their first-release scope during M5 planning; do not present them as already committed features.

此表不授予任何公开或法律再利用许可。`machine_checked` 只表示当前机器 Contract 与已记录检查通过，不是历史真实性、教理共识或法律意见。

No item in this table authorizes publication or legal reuse. A `machine_checked` label means the current machine contracts and recorded checks passed; it is not a historical-truth verdict, doctrinal consensus, or legal opinion.

## 6. Decisions And Document Conflicts / 需确认与口径冲突

| ID | 待决定事项 / Decision needed | 当前安全口径 / Present rule | 负责人及时间 / Owner and timing |
|---|---|---|---|
| Q01 | 是否为 `ENT000001-CAND0001` 复用 `CASE000001`，并由谁审核？<br>Reuse `CASE000001` for the candidate, and who is the reviewer? | M2A v0.2 Run 保持 `blocked`；AI 不冒充人工审核者。<br>Keep the Run blocked; AI must not impersonate a human reviewer. | 项目负责人，现在。<br>Project owner, now. |
| Q02 | 公开发布地区、商业用途和获准 AI Provider 是哪些？<br>Which launch jurisdictions, commercial uses, and AI providers apply? | 各用途分别判断；现代来源公开用途不明时交合格版权审核。<br>Treat uses separately and escalate uncertain publication to qualified rights review. | 项目负责人及版权审核者，现代来源公开前。<br>Project owner and rights reviewer, before modern publication. |
| Q03 | 未获许可时，哪个第二语言来源替代第二个 Purelanders 名额？<br>Which second-language source replaces the second Purelanders slot without permission? | 面向公开数据集，较新的[下一步计划](NEXT_STEPS.md)优先于[M1 历史短名单](../01-global-source-directory/M1_SOURCE_SHORTLIST_LOCKED.md)的两个 Purelanders 规划名额。<br>The newer next steps supersede the historical two-Purelanders allocation for public dataset selection. | 项目负责人，M3 前。<br>Project owner, before M3. |
| Q04 | 来源公开姓名时，哪些现代敏感情况应隐藏或遮蔽？<br>When should a named modern subject be withheld or redacted? | 内部保留来源身份，公开另做隐私审核；不一律匿名或一律公开。<br>Preserve source identity internally; review public disclosure separately. | 项目负责人及隐私审核者，M3 公开前。<br>Project owner and privacy reviewer, before M3 public outputs. |
| Q05 | 采用何种数据存储与受限资料安全共享方式？<br>Which backend and secure artifact exchange are acceptable? | 不擅自选生产数据库，也不将受限载荷上传新服务。<br>Do not choose a production database or upload restricted payloads by implication. | 技术负责人及项目负责人，M2D。<br>Technical and project owners, M2D. |
| Q06 | 是否需要 Google Sheets/Notion 镜像，由谁维护？<br>Is a Google Sheets/Notion mirror useful, and who owns it? | 只能作为可选审核界面，不作证据权威源。<br>Optional review UI, never the evidence source of truth. | 项目负责人，M2D 后。<br>Project owner, after M2D. |

受影响阶段开始前需统一旧文档口径：[Seed Plan](../02-data-model/SEED_DATASET_PLAN.md)目标是后期 50-100 条且仍列有 v0.1 字段，M3 的近期目标是 **10 条**，M2D 必须把字段映射到 v0.2。[PRD](../10-publication-interface/PRD_DRAFT.md)提到主题推荐至少五条；如果没有五条同时相关且可依法展示的案例，只返回实际数量并提示覆盖不足，不能凑数。[产品定义](../10-publication-interface/PRODUCT_DEFINITION.md)描述现代来源读者转述，但某条能否公开由 [M2 版权审核](../02-data-model/M2_RIGHTS_REVIEW.md)决定。“可信”指来源可追溯及质量说明，不代表已经证实往生事件。

Document reconciliation required before each affected milestone: the [seed plan](../02-data-model/SEED_DATASET_PLAN.md) targets 50-100 reviewed Cases and still lists v0.1 fields; M3 first targets **10**, and M2D must map seed fields to v0.2. The [PRD](../10-publication-interface/PRD_DRAFT.md) says a theme returns at least five Cases; until a theme has five qualifying, rights-cleared Cases, the product must return fewer with an honest coverage note, never pad results. The [product definition](../10-publication-interface/PRODUCT_DEFINITION.md) discusses modern reader renderings; [M2 rights review](../02-data-model/M2_RIGHTS_REVIEW.md) controls whether a specific rendering may be public. The word “credible” describes traceable reporting and source quality, not proof of a reported rebirth.

## 7. Execution Roadmap / 分阶段执行与验收

细化的执行路线图（任务、负责人、验收、依赖）见 [ROADMAP.md](ROADMAP.md)；本表保留阶段口径与验收标准。

有依赖关系的阶段按顺序推进。版权研究、来源联络、评测集设计，以及获准使用的讲稿和引文收集可以并行。不能仅凭文档写了某项工作，就把该阶段记为完成。

Complete stages in order where dependencies apply. Rights research, source outreach, evaluation-set design, and approved talk/citation collection may proceed in parallel. Do not count a stage as done because a document says it should exist.

| 阶段 / Stage | 当前状态 / Current state | 负责角色 / Lead role | 阶段产物 / Exit artifact |
|---|---|---|---|
| M0/M1 基础工作 / Foundation | 历史决议已完成 / `done` as historical decisions | 项目负责人及来源编辑 / Project owner + source editor | Schema、五来源短名单、试点范围。<br>Schemas, five-source shortlist, pilot scope. |
| M2A v0.2 迁移 / Bridge | 被 Q01 阻断 / `blocked` on Q01 | 项目负责人审核身份，数据工程师处理 Run。<br>Project owner for identity; data engineer for Run. | 已接受的新 Run 和经审核的迁移对比。<br>Accepted new Run and reviewed migration comparison. |
| M2B 未见样本测试 / Unseen test | 计划中 / `planned` | 来源编辑及数据工程师 / Source editor + data engineer | 可复现的普通、复杂/多案例、新来源 Run，以及零案例测试。<br>Reproducible standard, complex/multi-case, and new-source Runs; zero-case test. |
| M2C 来源目录 / Source inventories | 仅有部分试点行 / `partial` pilot rows only | 数据工程师及来源编辑 / Data engineer + source editor | 四类可复用目录 Adapter 与指定范围内的完整目录。<br>Four reusable inventory adapter families and scoped complete catalogs. |
| M2D 正式数据提升 / Canonical promotion | 计划中 / `planned` | 数据工程师及版权审核者 / Data engineer + rights reviewer | 有版本的正式数据、持久化去重、按版权规则提升。<br>Versioned canonical data, persistent dedup, rights-aware promotion. |
| M3 十案例试点 / Ten-Case pilot | 仅有部分历史草稿 / `partial` historical drafts only | 来源编辑及版权审核者 / Source editor + rights reviewer | 跨来源形式和语言的十条已检查并提升的案例。<br>Ten promoted, checked Cases across source forms and languages. |
| M4 本地产品原型 / Local product prototype | 计划中 / `planned` | 产品负责人及数据工程师 / Product owner + data engineer | 搜索、证据高亮、可解释推荐与提纲评测。<br>Search, highlighted evidence, explainable recommendation, brief evaluation. |
| M5 可用网站 / Usable MVP website | 计划中 / `planned` | 产品负责人、前端工程师及审核者 / Product owner + frontend engineer + reviewer | 读者、创作者、来源及基础审核流程与发布关卡。<br>Reader, creator, source, and basic review workflows with release gates. |
| M6 教理与多语言深化 / Doctrinal/multilingual depth | 计划中 / `planned` | 教理审核者及编辑 / Doctrinal reviewer + editor | 已检查的导读和翻译试点、讲解方法评测。<br>Checked commentary and translation pilots, teacher-method evaluation. |
| M7 扩充至 50-100 案例 / Scale | MVP 前暂缓 / `deferred` until MVP | 运营及来源编辑 / Operations + source editor | 可重复执行的收录、覆盖、纠错和维护流程。<br>Repeatable ingestion, coverage, correction, and operations. |

表中角色是职责，尚非具体人员任命。项目负责人应在每个阶段开始前指定人员；没有人力安排前，本计划不承诺交付日期。

Roles are responsibilities, not named assignments. The project owner should assign people before starting each stage; no delivery dates are claimed without capacity information.

### M2A v0.2 Bridge / 当前阻断

**目标 / Goal:** 在不改动已接受的 0.1.1 baseline 的前提下，用 `ENT000001` 验证先建立 Candidate 的迁移流程。 / Prove candidate-first migration on `ENT000001` without altering the accepted 0.1.1 baseline.  
**已完成 / Done:** 已迁移历史证据、与本地 `CASE000001` 比对，并在复用 ID 前停止。 / Migrated historic evidence, compared to local `CASE000001`, and stopped before ID reuse.  
**待完成 / Remaining:** 完成 Q01 人工身份裁定；创建 Source Occurrence，并把文中提及的 `《净土约说书后》` 标为 `unresolved_upstream`；在新 Run 记录中完成读者文本、创作分析、事实检查、版权检查和打包阶段。 / Resolve Q01 with human review; create Source Occurrence with the cited `《净土约说书后》` marked `unresolved_upstream`; complete reader, creator, factual, rights, and packaging stages in a new Run record.

**验收 / Acceptance:** 身份裁定前不分配 Case ID；保存审核者身份与理由；出现记录定位能指向已保存片段；无依据和相矛盾的主张数量均为零；版权决定覆盖每项公开输出；Catalog 与 Run 状态一致；旧 baseline 哈希校验仍通过。与原 M2A 的差异单独报告。旧回复的重放仅标为迁移证据，不视作新版 v2 Prompt 质量测试。 / No Case ID before resolution; review identity and reviewer/reason retained; occurrence locators resolve to retained segments; unsupported/contradicted claim counts are zero; rights decision covers every public output; Catalog and Run status agree; old baseline hashes still pass. Report any difference from M2A separately. A replayed old response is labeled migration evidence, not fresh v2 prompt quality.

### M2B Unseen Article Test / 未参与设计的新条目

**目标 / Goal:** 验证同一条 Pipeline 能处理普通条目、讲解较多或包含多个案例的条目，以及来自新公版或开放许可来源的条目。如果这三条都包含案例，另加零案例测试样本。逐条记录 Candidate 边界和来源特定版权规则。 / Test whether one Pipeline handles a normal item, a commentary-heavy or multi-Case item, and an item from a new public-domain/open-permission Source. Include a separate zero-Case fixture if none of the three is zero-Case. Record candidate boundaries and source-specific rights for each item.

**验收 / Acceptance:** 至少三个新的 Article Run，且覆盖零案例情形；文本片段无遗漏或重叠；多案例拆分不混淆身份；提交后的 AI 响应不人工修补；失败仍保留在有版本的 Run 证据中；受限输入不发送给未经授权的 Provider；拟公开输出通过回归规则中事实与版权方面的硬性指标。本阶段评测 v2 提取与去重 Prompt，而非只重放 M2A。 / At least three new Article Runs plus zero-Case coverage; no omitted or overlapping text segments; multi-Case fan-out does not swap identities; AI responses are not manually repaired after submission; failures remain in versioned Run evidence; restricted inputs never reach an unauthorized provider; the regression policy's hard factual/rights metrics pass for any proposed output. This stage evaluates v2 extraction/dedup prompts rather than only replaying M2A.

### M2C Source Inventories / 批量前完成来源目录

**目标 / Goal:** 实现 `static_headings`、`wordpress_archive`、`paginated_html` 和 `pdf_toc` 四类目录 Adapter，必要时为各 Source 配置选择器。先补全指定范围的目录，再为活跃网站增量刷新。管理员仍能看见被排除、无法访问、已变化、已移除、重复和非案例条目。 / Implement `static_headings`, `wordpress_archive`, `paginated_html`, and `pdf_toc` inventory adapter families using Source-specific selectors where necessary. Start with complete scoped backfill, then incremental refresh for an active site. Keep excluded, inaccessible, changed, removed, duplicate, and non-case items visible to administrators.

**验收 / Acceptance:** `SRC0001` 选定章节的目录条数及覆盖范围与提取器发现结果一致；至少一个活跃网站的刷新能生成可检查的试运行差异；重复扫描不会产生重复行或悄悄删除行；稳定条目键在重跑后不变；`source.yml` 记录 Adapter 与覆盖状态；审核者可以辨认未处理条目。文章正文提取是另一个 Entry Adapter 步骤。 / Selected `SRC0001` section catalog agrees with its extractor's discovered item count and coverage scope; at least one active site refresh produces an inspectable dry-run diff; a repeated scan does not duplicate or silently remove rows; stable item keys survive reruns; `source.yml` records adapter and coverage state; a reviewer can tell which items remain unprocessed. Extraction of article bodies is a separate Entry Adapter step.

### M2D Canonical Data And Review / 正式数据与审核

**目标 / Goal:** 将已接受的 Run 提升为机器可读的 Case、Fact、Source Occurrence、文本版本、实体、版权决定和创作元数据。选择能够支持搜索、关联完整性、修订、受限对象安全访问及后续迁移的最小存储方案。历史 ID 与 v0.1 baseline 仍须可查询。 / Promote accepted Runs into machine-readable Cases, Facts, Source Occurrences, text versions, entities, rights decisions, and creator metadata. Choose the smallest storage system that supports search, referential integrity, revisions, secure restricted-object access, and future migration. Keep historical IDs and v0.1 baselines addressable.

**验收 / Acceptance:** 数据提升可重复执行而不产生额外结果，拒绝失败、已取代或受阻的 Run；验证每条事实到片段及出现记录到来源条目的关联；识别重复或临时 ID 冲突；记录审核行为；能从已保存证据重建同一公开数据集。持久化语料检索测试覆盖有名与匿名、翻译与转载版本。公开导出不包含受限原文。纠错时可撤下一项受影响输出并找出依赖的文本版本，同时保留审核轨迹。另一名获授权操作者可凭受控资料复现获准的 Run。 / Promotion is idempotent, rejects failed/superseded/blocked Runs, validates every fact-to-segment and occurrence-to-item link, catches duplicate or provisional-ID collisions, records reviewer actions, and can rebuild the same public dataset from retained evidence. A persistent corpus retrieval test covers named/anonymous and translated/reposted versions. Public exports exclude restricted text. A correction can withhold one affected output and identify dependent text versions without deleting the audit trail. Another authorized operator can reproduce an allowed Run with access-controlled artifacts.

### M3 Ten-Case Pilot / 十案例数据集

**目标 / Goal:** 用同一已接受版本的 Pipeline 处理十个 Case，覆盖至少三种来源形式及两种语言；面向公众的示例只用版权已核清的材料。每次 Run 前确认来源、条目、AI 处理及输出各层权限。最初五个历史案例包可用于设计回归测试，但不自动视为已接受记录。 / Process ten Cases through one accepted Pipeline version, including at least three source forms and two languages, while using rights-cleared material for public-facing examples. Confirm source-level, item-level, AI-processing, and output rights before each Run. Use the first five historical packs as regression ideas, not as automatically accepted records.

**验收 / Acceptance:** 十个不同且已提升的 Case 均有证据定位、明确身份决定、版权及审核状态、读者摘要、受证据支持的完整叙事或无法发布的明确原因，以及创作元数据；不存在未经审核的公开文本。版权允许时，测试至少一组真实重复/传播关系和一组翻译关系。固定评测集要求 Schema 与引用覆盖率 100%，无依据或矛盾的事实主张、无声合并与版权违规均为 0。读者与创作者质量分别打分；质量未达标时按新 Prompt 版本重新生成，不能补造细节。 / Ten distinct promoted Cases with evidence locators, explicit identity decisions, rights/review status, reader summary and supported full-depth account or an explicit reason it cannot be published, creator metadata, and no unreviewed public text. Test at least one real duplicate/transmission relation and one translation relationship when rights permit. Run the fixed evaluation set: schema/reference coverage 100%; unsupported/contradicted factual claims, silent merges, and rights violations 0. Reader and creator quality receive separate scored reviews; a quality failure triggers regeneration under a new prompt version, not fabricated detail.

### M4 Local Search And Recommendation / 产品核心能力原型

**目标 / Goal:** 在决定网站架构前，先用正式数据集验证读者搜索和创作者按主题选例。索引只收录各展示范围允许的字段。建立一小组固定搜索问题和创作选题，并写明预期结果及理由。 / Prove reader search and theme-based creator selection on the promoted dataset before choosing the website architecture. Index only fields allowed at each display scope. Build a small fixed set of search queries and creator briefs with expected results and explanations.

**验收 / Acceptance:** 按来源、人物、瑞相和自由文本检索能返回正确 Case 及允许展示的高亮片段；同一 Case 的多个 Occurrence 合并为一条结果，并可切换来源；原文片段与整理文本片段明确标注；主题排序提供具体适配理由、出处、不确定性、版权与隐私提醒，缺少合适案例时如实提示；在至少三例符合条件的预设测试中，三个选中案例能组成证据关联提纲。索引、API 响应和日志均不泄露受限原文。测试衡量相关性，而非仅检查 JSON 字段存在。 / Lookup by Source, person, sign, and free text returns the correct Case and a highlighted permitted snippet; one Case's multiple Occurrences collapse into one result with source choices; original/rendering snippets are labeled; topic ranking gives specific reasons, citation, uncertainty, rights/privacy caution, and an honest “insufficient suitable Cases” result when applicable; three selected Cases can form an evidence-linked brief in a curated test where three qualify. No restricted text leaks through index, API response, or logs. Tests measure relevance, not only whether JSON fields exist.

### M5 Usable Website / 读者与创作者第一版

**目标 / Goal:** 将已验证的产品任务做成第一版可用界面，包括展示数个版权已核清经典案例的首页、来源页、搜索及结果页、兼顾读者/创作者/研究者的案例详情页、主题助手、选题篮、创作提纲，以及仅供管理员使用的审核与状态界面。读者路径与创作辅助同等重要。 / Turn the tested product tasks into the first usable interface. Include a homepage with several rights-cleared classic Cases, Source pages, search/results, one Case Detail with reader/creator/research emphasis, theme assistant, basket, creator brief, and a restricted administrator review/status view. The reader path is equal in prominence to creator assistance.

**验收 / Acceptance:** 利益相关者能在桌面端和移动端完成 [PRD](../10-publication-interface/PRD_DRAFT.md) 中的读者与创作者任务；搜索高亮能追溯证据且不暴露受限全文；来源、AI、审核标识及更正可见；法师能查看每条推荐的适配原因与证据不能证明的内容；管理员能查看条目状态和审核队列决定；公开页面仅提供已批准的发布包。部署前的发布审核覆盖版权、隐私、无障碍、基本安全性及失败/空状态。不自动发布视频，也不无限制展示有版权的全文。 / Stakeholders can complete the reader and creator journeys in the [PRD](../10-publication-interface/PRD_DRAFT.md) on desktop and mobile; search highlights trace to evidence without exposing restricted full text; source/AI/review labels and corrections are visible; a teacher can inspect why each recommended Case fits and what it cannot prove; an operator can inspect item status and queue decisions; public routes serve only approved publication packages. A release review covers rights, privacy, accessibility, basic security, and failure/empty states before deployment. No automatic video publication or unrestricted copyrighted full-text display.

### M6 Doctrinal, Talk, And Multilingual Depth / 深化内容

**目标 / Goal:** 通过固定评测改善读者文本的可读性与创作角度的精准度；用已批准的案例事实和教理引文试写一篇读者导读；分析获准使用的法师讲稿中的讲解方法，但不模仿在世法师的个人风格。选取许可允许的来源试做一篇译文。视频优先保存带时间戳的字幕，而非完整视频文件。 / Improve readability and creator-angle specificity with fixed evaluations; pilot one doctrinal reader article using approved case facts and doctrinal citations; analyze authorized teacher talks for explanation methods without copying a living teacher's style. Pilot one translation from a Source whose rights permit it. Timestamped transcripts are preferred to retaining full video files.

**验收 / Acceptance:** 新 Prompt 版本提高经评审的读者与创作者质量，且不降低事实、出处和版权关卡；一篇导读逐项通过事实、教理、引文、隐私和表达检查，无依据或矛盾的主张为零；讲解方法记录可定位到讲稿时间码；译文标明准确来源、模型或译者、不确定处、审核和许可。影响重大的教理或修行指导经过人工审核。这些产物均不标为原始证据。 / A prompt version improves judged reader/creator quality without worsening factual, attribution, or rights gates; one commentary passes a claim-by-claim factual, doctrinal, quotation, privacy, and expression check with zero unsupported/contradicted claims; method records point to talk timestamps; translation identifies its exact source, model/translator, uncertainty, review, and permission. High-impact doctrinal or practical guidance receives human review. None of these outputs is labeled original evidence.

### M7 Scale And Operations / 扩充与持续维护

**目标 / Goal:** 十案例 Pipeline 和 MVP 任务通过验收后，才向[50-100 案例的种子集目标](../02-data-model/SEED_DATASET_PLAN.md)扩展。有目的地扩大国家、语言、来源类型和复杂案例覆盖，不只追求数量。 / Expand toward the [50-100 Case seed target](../02-data-model/SEED_DATASET_PLAN.md) only after the ten-Case pipeline and MVP tasks work. Broaden countries, languages, source types, and difficult cases deliberately rather than maximizing raw count.

**验收 / Acceptance:** 使用相同的有版本阶段处理下一批十例，并取得可比较的质量指标；目录刷新与去重不产生未察觉的重复；审核纠错和版权变化能同步到搜索及公开输出；安全备份和恢复经过测试；宣称达到更大种子集目标前，至少覆盖五种来源类型和八种案例类型；覆盖程度与推荐质量按真实用户任务评测。 / Another batch of ten can be ingested with the same versioned stages and comparable quality metrics; inventory refresh and dedup do not create silent duplicates; reviewer corrections and rights changes propagate to search/public outputs; secure backups and recovery are tested; at least five source types and eight case types are represented before claiming the broader seed target; coverage and recommendation quality are measured against real user tasks.

## 8. Team Operating Rules / 团队更新规则

1. 从本页开始，再阅读相关的[处理流程](../02-data-model/DATA_PROCESSING_WORKFLOW.md)、[Pipeline 指南](../09-agent-automation/README.md)、版权审核和阶段 Contract。`docs/history/` 中的旧记录解释决策过程，不作为当前操作指令。<br>Start here, then read the relevant [workflow](../02-data-model/DATA_PROCESSING_WORKFLOW.md), [pipeline guide](../09-agent-automation/README.md), rights review, and stage contract. Historical notes under `docs/history/` explain decisions but are not current instructions.
2. 每项任务执行前，记录负责人、输入 Source Item 或 Run ID、版本、版权状态、预期输出及验收检查。即使存在命令行开关或公开网址，也不能据此把受限文本发给外部 AI。<br>For each task, record owner, input Source Item or Run ID, version, rights status, expected output, and acceptance checks before execution. Never send restricted text to an external AI because a command-line switch or public URL exists.
3. 完整 Request/Response 保存在获授权的存储位置；Git 只追踪清理后的 Run Record 和哈希。失败、纠正或已发布的输出不能悄悄覆盖，应开启新 Run 并保留出处链。<br>Keep complete Requests/Responses in authorized storage; track sanitized Run Records and hashes in Git. Do not silently overwrite a failed, corrected, or published output. Use a new Run and preserve provenance.
4. 分别记录 `machine_checked`、`human_approved`、`rights_reviewed` 和 `published`。必须由人作出的身份或教理决定，不能让 AI 借用某个人的名字代签。<br>Record `machine_checked`, `human_approved`, `rights_reviewed`, and `published` separately. A human-required identity or doctrine decision cannot be supplied by an AI using a person's name.
5. 标记里程碑完成时，附上产物与测试结果，记录日期和审核者，更新本页、[进度记录](PROJECT_STATUS.md)及[已知问题](KNOWN_ISSUES.md)，并消除或解释其他文档中的冲突。不能为了让新 Run 通过而修改已接受的 M2A baseline。<br>To mark a milestone done, link its artifact and test results, note the date and reviewer, update this page plus [status](PROJECT_STATUS.md) and [known issues](KNOWN_ISSUES.md), and remove or explain contradictory instructions elsewhere. Do not change the accepted M2A baseline to make a new Run pass.
6. 如果尚未取得的共享对话导出揭示新需求，应在第 5 节注明来源和所属阶段。不能把推测悄悄写成已获批准的决定。<br>If the missing shared-conversation exports reveal new requirements, add them to section 5 with a source note and stage assignment. Do not silently present an inference as an approved decision.

**当前交接 / Immediate handoff:** 下一位执行者应检查 `RUN-ENT000001-M2A-T02V02` 与 Q01。在项目负责人给出真实审核者身份及 Case ID 复用决定前，让 `case_resolution` 保持 `review_required`。M2B 来源选择、版权研究和评测集设计可以独立推进；M2A 尚不能标为完成。 / The next operator should inspect `RUN-ENT000001-M2A-T02V02` and Q01. Until the project owner supplies a real reviewer identity and Case reuse decision, leave `case_resolution` in `review_required`. Other independent work may continue on M2B source selection, rights research, and the evaluation set; M2A cannot be marked complete.
