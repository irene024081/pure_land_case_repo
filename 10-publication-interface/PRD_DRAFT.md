# PRD Draft

## Locked Product Decisions / 已锁定产品决策

2026-09-21 由项目负责人确认（需求访谈 Round 1）：

| # | 决策点 | 决定 | 影响 |
|---|---|---|---|
| D1 | 访问范围 | **第一版即公开网站**，任何人可访问 | 所有上线内容必须版权核清；现代受限来源默认不进公开层 |
| D2 | 法师选题 AI 形态 | **对话式**（多轮追问澄清后推荐） | AI 只能推荐库内案例、不得虚构；对话最终产出结构化选题单，与表单式走同一套事实与版权检查 |
| D3 | 账号体系 | 读者免登录；创作者登录后使用选题篮、保存提纲；管理员独立后台 | 需要账号系统与创作者资产存储 |
| D4 | 上线数据规模 | **50–100 条**案例才上线 | 原 M7 种子集目标前移为上线门槛；公开版以公版古籍批量 + 版权已清现代精品为主 |

2026-09-21 由项目负责人确认（需求访谈 Round 2）：

| # | 决策点 | 决定 | 影响 |
|---|---|---|---|
| D5 | 对话边界 | AI **只做案例检索推荐**；教理问题引导到已审核导读文章 | 对话助手的 system prompt 必须明确拒绝自由教理问答；导读文章是唯一的教理内容载体 |
| D6 | 现代版权内容 | 现代案例**只放摘要+外链**，引导读者去原网站读全文 | 公开站可覆盖现代案例但篇幅受限；摘要长度逐案审核；详情页必须有明显的原文来源跳转 |
| D7 | 界面语言 | 第一版**仅中文** | 多语言案例仍可入库，但界面和读者文本先做中文 |
| D8 | 提纲交付 | **网页查看+复制文本**，不做文件导出、不生成讲稿初稿 | Creator Brief 页面化；讲稿写作留给创作者自己 |

2026-09-21 由项目负责人确认（需求访谈 Round 3）：

| # | 决策点 | 决定 | 影响 |
|---|---|---|---|
| D9 | 开发方式 | **AI 主导开发**，项目负责人决策与验收 | 技术方案需写到可照做的颗粒度；每次交付附验收方法 |
| D10 | 技术栈 | **主流栈，方便交接**：Postgres + Python(FastAPI) + React；先单机部署，保留迁移余地 | 与 9-15 对话"SQLite→Postgres"路径一致，直接以 Postgres 起步 |
| D11 | 产品侧 AI 功能 | 第一版三件：**对话选题推荐、搜索辅助、教理导读草稿** | 每个功能独立 prompt 版本与验收；选题单/提纲改用确定性模板组装，不经 AI 生成 |
| D12 | 审核人力 | 项目负责人 + 少数协作者 | 审核队列按小团队设计：任务列表、认领、决定留痕，暂不做复杂权限层级 |

2026-09-21 由项目负责人确认（需求访谈 Round 4）：

| # | 决策点 | 决定 | 影响 |
|---|---|---|---|
| D13 | 商业化 | **完全公益**：无广告、无付费、无捐赠入口 | 版权审核按非商业口径；如未来改变需重审全部现代来源授权 |
| D14 | 现代当事人隐私 | **来源实名则实名**；病情、家庭矛盾等敏感细节逐案审核 | 与原 GPT 对话默认值一致；敏感细节遮蔽标准仍需在 M3 前写成规则（G14） |
| D15 | 导读教理审核 | 项目负责人审事实与表达；教理部分**只引用已审核的经论与祖师文献**，不做新教理发挥 | 导读写作范围收窄为"案例 + 既有教理引文"；AI 与负责人均不作教理创新 |
| D16 | 上线节奏 | **分阶段开放**：先读者搜索阅读（古籍为主），再对话推荐，再导读 | 每阶段独立验收；公开网站可以先上线读者层 |

## Problem

净土宗案例资料分散在古籍、期刊、网站、视频、法师来信和多语种资料中。法师、视频制作者和研究整理者需要可检索、可追溯、可引用的案例库，而不是零散搜索结果。

## Goal

建立一个网站和工作台，让普通读者能搜索、阅读、核对净土感应案例，让法师和创作者能从主题出发找到合适案例，并获得出处、可信度、使用风险和讲述辅助。

## MVP Users

Primary user:

- 普通读者。
- 法师、弘法者。

Secondary users:

- 视频策划、剪辑、运营。
- 研究整理者。

## Main User Journey

Reader journey:

1. 用户从首页、来源页、人物姓名、瑞相、关键词或标签进入。
2. 系统返回搜索结果，并高亮命中片段。
3. 用户打开 Case Detail。
4. 用户默认阅读忠实可读版。
5. 用户展开原文证据、出处和引用位置。
6. 用户继续查看相关案例、同来源案例或同类瑞相案例。

Creator journey:

1. 用户输入主题、受众、视频长度和案例偏好。
2. 系统检索案例库。
3. 系统按主题相关度、证据等级、叙事清晰度、视频适配度排序。
4. 用户查看推荐理由和出处。
5. 用户选择若干案例。
6. 系统生成 creator brief。
7. 用户根据 brief 自行完成讲稿、开示或视频。

## Core Features

### Homepage

Sections:

```text
featured_classic_cases
popular_case_types
source_entry_points
rebirth_sign_entry_points
latest_or_newly_processed_cases
theme_assistant_entry
```

Homepage purpose:

```text
help ordinary readers start reading
show the database is evidence-based
provide quick paths into search
introduce creator workflow without hiding reader search
```

### Theme-to-case Recommendation

交互形态为对话式（D2）：用户以自然语言对话，系统在多轮中逐步收集以下条件。以下字段不再是表单，而是对话需要填满的条件槽（slot），完整流程见 [THEME_ASSISTANT_DESIGN.md](THEME_ASSISTANT_DESIGN.md)。

Input fields (slots):

```text
topic
audience
duration
preferred_case_period
preferred_source_type
case_tone
avoid_types
```

Ranking factors:

```text
semantic_relevance
tag_match
source_quality
provenance_quality
narrative_clarity
video_fit
privacy_risk
copyright_risk
```

Output fields:

```text
case_id
title
short_summary
why_relevant
recommended_usage
source_citation
provenance_quality
video_fit
risk_notes
```

### Case Search

Filters:

```text
keyword
source
reborn_person_name
witness_name
case_type
rebirth_sign
period
region
language
provenance_quality
collection_priority
modern_or_historical
video_fit
```

Search result requirements:

```text
show matched field
show highlighted snippet
collapse duplicate citations under one canonical case
allow switching between original snippet and reader rendering snippet
```

### Case Detail

Page sections:

```text
short_summary
reader_rendering
independent_factual_account
dharma_case_commentary
original_evidence
source_citations
provenance_chain
people
places
dates
tags
evidence_notes
copyright_notes
creator_summary
interpretation_angles
creator_notes
related_cases
```

Reader rendering requirements:

```text
generated_from_citation
clear_text_type_label
expandable_original_evidence
fidelity_review_status
source_specific_processing_note
multilingual_version_status
content_depth
paragraph_level_source_segments
claim_review_status
doctrinal_source_list
```

Dharma commentary requirements:

```text
approved interpretation angle
approved doctrinal citations
registered case facts and source segments
atomic content claim ledger
zero unsupported claims
zero contradicted claims
verified quotations
preserved attribution and uncertainty
passed rights and privacy checks
source, item, and generated-output rights decisions
expression-similarity and substitution-risk checks
visible AI and review labels
```

Supported readability treatments:

```text
classical_to_modern_rendering
oral_record_cleanup
first_person_testimony_cleanup
long_article_summary
translation
```

Display modes:

```text
reader_view
creator_view
research_view
```

The page uses one canonical case record. Display modes change ordering and emphasis, not facts.

### Creator Brief

Generated after user selects one or more cases.

Sections:

```text
video_topic
main_message
case_order
talking_points
case_summaries
transition_notes
source_citations
risk_notes
selected_interpretation_angle
supporting_source_segments
doctrinal_boundary
alternative_reading
```

Creator angle requirements:

```text
one narrow core claim
explicit target audience and creator goal
evidence-linked supporting segments or normalized facts
suggested narrative or teaching structure
required doctrinal and historical context
clear statement of what the case cannot prove
attribution when an angle comes from a teacher's commentary
prompt and generation provenance
```

## Field Definitions And Scoring

本节定义 PRD 中容易含糊的字段。所有字段都应能落到数据模型，不能只作为界面文案。

### Common Scale

推荐使用统一等级：

```text
high
medium
low
unknown
```

需要排序时可映射为：

```text
high = 3
medium = 2
low = 1
unknown = 0
```

风险类字段反向使用：

```text
low risk = better
medium risk = caution
high risk = downrank or require warning
unknown risk = require review
```

### Homepage Sections

| Field | Meaning | Notes |
|---|---|---|
| `featured_classic_cases` | 首页展示的经典案例。 | 应优先选择出处清楚、叙事完整、版权风险低的案例。 |
| `popular_case_types` | 常见案例类型入口。 | 如临终瑞相、预知时至、助念、梦感、念佛免难。 |
| `source_entry_points` | 来源入口。 | 如《净土》《净土圣贤录》、PLBTW、YouTube 来源。 |
| `rebirth_sign_entry_points` | 瑞相入口。 | 如异香、身软、见佛、预知时至、光明。 |
| `latest_or_newly_processed_cases` | 最近整理完成的案例。 | 展示已通过审核或至少可公开阅读的案例。 |
| `theme_assistant_entry` | 创作者主题配例入口。 | 不应压过普通读者的搜索入口。 |

### Theme Recommendation Input Fields

| Field | Meaning | Example | Use |
|---|---|---|---|
| `topic` | 用户想讲或查的主题。 | 临终助念为什么重要 | 语义检索和主题匹配的主输入。 |
| `audience` | 目标受众。 | 普通家属、初学者、莲友、青少年 | 影响案例语气、背景解释和风险判断。 |
| `duration` | 目标内容长度。 | 60 秒、8 分钟、30 分钟开示 | 影响 `length_fit` 和案例数量。 |
| `preferred_case_period` | 偏好的时代。 | 古代、近现代、当代、不限 | 用于筛选或加权。 |
| `preferred_source_type` | 偏好的来源类型。 | 古籍、现代期刊、网站、YouTube、法师来信 | 用于筛选和版权处理。 |
| `case_tone` | 用户希望案例呈现的语气。 | 平实、感人、警策、适合家庭 | 影响推荐排序，不改变案例事实。 |
| `avoid_types` | 用户希望避免的内容。 | 太玄奇、隐私强、死亡细节重、出处弱 | 高风险或不适配案例降权。 |

### Ranking Factors

| Field | Meaning | How To Judge |
|---|---|---|
| `semantic_relevance` | 案例内容与用户主题的语义相关度。 | 用主题、摘要、标签、creator summary、teaching themes 综合判断。 |
| `tag_match` | 案例标签与用户筛选项的匹配度。 | 如用户要助念案例，`assisted_chanting` 直接命中。 |
| `source_quality` | 来源本身的质量。 | 结合来源级别、是否可访问、是否一手或近一手、是否结构清楚。 |
| `provenance_quality` | 该案例出处链质量。 | P1/P2 优先，P3 可用，P4 需要提示。 |
| `narrative_clarity` | 故事线是否清楚。 | 谁、何时、何地、发生什么、结果如何是否完整。 |
| `video_fit` | 案例是否适合视频表达。 | 见下方 `Video Fit` 细分。 |
| `privacy_risk` | 是否涉及敏感个人信息。 | 现代案例、病情、家庭关系、未公开姓名需谨慎。 |
| `copyright_risk` | 公开展示或改编是否有版权风险。 | 现代书籍、期刊、视频字幕通常高于公版古籍。 |

### Video Fit

`video_fit` 指案例适不适合改编成视频内容。它不等于真实性，也不等于法义价值。一个案例可以非常重要，但不适合短视频。

细分维度：

| Field | Meaning | High | Low |
|---|---|---|---|
| `narrative_clarity` | 故事线是否清楚。 | 人物、地点、经过、结果完整。 | 只有一句线索，背景缺失。 |
| `emotional_accessibility` | 普通观众是否容易理解和共情。 | 处境清楚，情感自然。 | 需要大量宗教或历史背景。 |
| `visualizability` | 是否容易转化成画面、旁白或字幕。 | 有明确场景、动作、人物关系。 | 主要是抽象议论或书目说明。 |
| `length_fit` | 是否适合目标长度。 | 能支撑指定时长，不拖沓。 | 过短或需要很长解释。 |
| `context_required` | 需要多少背景解释。 | 背景少，容易进入。 | 背景多，短视频适配低。 |
| `risk_level` | 是否容易被误解或猎奇化。 | 平实、边界清楚。 | 容易被夸大神异、断章取义。 |
| `source_confidence` | 出处是否足够清楚，适合公开引用。 | 有明确来源、页码、时间戳或原文。 | 来源链弱或只见转载。 |

推荐落库字段：

```text
video_fit_score
video_fit_level
video_fit_notes
best_video_format
narrative_clarity
emotional_accessibility
visualizability
length_fit
context_required
misinterpretation_risk
source_confidence
```

`best_video_format` 取值：

```text
short_video
long_video
lecture_segment
case_compilation
quote_only
not_recommended
unknown
```

### Recommendation Output Fields

| Field | Meaning |
|---|---|
| `case_id` | 推荐对应的规范案例 ID。 |
| `title` | 案例展示标题。 |
| `short_summary` | 一句话到三句话摘要。 |
| `why_relevant` | 为什么这个案例切合用户主题。必须具体说明。 |
| `recommended_usage` | 建议放在视频或开示的哪个位置，以及如何使用。 |
| `source_citation` | 可展示的出处。至少包括 source、位置或链接。 |
| `provenance_quality` | 出处链质量，帮助用户判断证据强弱。 |
| `video_fit` | 视频适配结论，应附简短说明。 |
| `risk_notes` | 版权、隐私、误解、猎奇化、出处弱等提示。 |

### Search Filters

| Field | Meaning |
|---|---|
| `keyword` | 任意关键词，匹配标题、摘要、原文摘录、可读版、标签、来源。 |
| `source` | 来源筛选，如某本书、期刊、网站、频道。 |
| `reborn_person_name` | 往生者或案例主体姓名。未知时可为空。 |
| `witness_name` | 见证者、讲述者、记录者姓名。 |
| `case_type` | 案例类型，如助念、预知时至、梦感、免难。 |
| `rebirth_sign` | 具体瑞相，如异香、身软、见佛、光明。 |
| `period` | 时代，如古代、民国、当代，或具体朝代/年份段。 |
| `region` | 地区，如中国大陆、台湾、日本、越南、美国。 |
| `language` | 来源语言或展示语言。 |
| `provenance_quality` | 出处质量筛选。 |
| `collection_priority` | 来源收录优先级。 |
| `modern_or_historical` | 现代案例或历史案例。 |
| `video_fit` | 视频适配筛选。 |

### Search Result Requirements

| Requirement | Meaning |
|---|---|
| `show matched field` | 明确告诉用户命中的是姓名、来源、标签、原文还是可读版。 |
| `show highlighted snippet` | 展示命中片段并高亮关键词。 |
| `collapse duplicate citations` | 同一案例的多个转载或引用折叠在一个 canonical case 下。 |
| `switch original/rendering snippet` | 用户可在原文片段和可读化片段之间切换。 |

### Case Detail Sections

| Section | Meaning |
|---|---|
| `short_summary` | 快速理解案例。 |
| `reader_rendering` | 面向普通读者的忠实可读版。 |
| `independent_factual_account` | 独立组织的事实叙事，重点保留事件、报告者和不确定性。 |
| `dharma_case_commentary` | 基于案例与已审核教理来源生成的表达性导读文章。 |
| `original_evidence` | 原文、原始摘录、字幕片段或受版权控制的证据定位。 |
| `source_citations` | 一个或多个出处位置。 |
| `provenance_chain` | 从发现来源追到更早来源的链条。 |
| `people` | 往生者、见证者、记录者、法师等。 |
| `places` | 事件地点、来源地区、机构地点。 |
| `dates` | 事件日期、记录日期、出版日期。 |
| `tags` | 案例类型、瑞相、主题标签。 |
| `evidence_notes` | 证据强弱、疑点、版本差异。 |
| `copyright_notes` | 公开展示限制和引用限制。 |
| `creator_summary` | 面向创作者的用途摘要。 |
| `interpretation_angles` | 精确阐释角度，包含受众、主张、依据、结构和边界。 |
| `creator_notes` | 适合说明的主题、受众、风险和用法。 |
| `related_cases` | 相同人物、来源、瑞相、主题或相似叙事的案例。 |

### Reader Rendering Requirements

| Field | Meaning |
|---|---|
| `generated_from_citation` | 可读化文本必须绑定出处。 |
| `clear_text_type_label` | 页面明确标注原文、白话译述、整理摘要、AI 辅助说明。 |
| `expandable_original_evidence` | 用户可以展开查看原文或证据定位。 |
| `fidelity_review_status` | 标明是否经过机器检查或人工审核。 |
| `source_specific_processing_note` | 标明处理方式，如字幕整理、文言白话译述、长文摘要。 |
| `multilingual_version_status` | 标明是否有译文、译文审核状态和所依据原文。 |
| `content_depth` | 区分摘要、压缩整理和完整可读叙事。详情页主文本要求 `full_supported_account`。 |
| `paragraph_level_source_segments` | 每个生成段落绑定其依据的原文段落或时间码。 |
| `claim_review_status` | 事实、教理、引文、归因、版权和隐私的逐条验证状态。 |
| `doctrinal_source_list` | 导读文章使用的经论、祖师、传承或法师讲解来源。 |

### Display Modes

| Mode | Primary User | Default Emphasis |
|---|---|---|
| `reader_view` | 普通读者 | 摘要、忠实可读版、原文证据、相关案例。 |
| `creator_view` | 法师、创作者 | 主题适配、讲述用途、video fit、风险、选题篮。 |
| `research_view` | 研究者、编辑 | 引用链、版本差异、去重、审核状态、证据说明。 |

### Creator Brief Sections

| Field | Meaning |
|---|---|
| `video_topic` | 用户当前选题。 |
| `main_message` | 用户希望表达的主旨。不得自动替用户决定法义。 |
| `case_order` | 推荐案例使用顺序。 |
| `talking_points` | 每个案例可支持的讲述点。 |
| `case_summaries` | 可用于讲稿准备的案例摘要。 |
| `transition_notes` | 案例之间如何过渡。 |
| `source_citations` | 每个案例对应的引用说明。 |
| `risk_notes` | 版权、隐私、出处弱、误解风险。 |
| `selected_interpretation_angle` | 当前 brief 采用的精确阐释角度。 |
| `supporting_source_segments` | 支撑该角度的原文段落或时间码。 |
| `doctrinal_boundary` | 明确案例不能证明或不应推出的结论。 |
| `alternative_reading` | 对材料的其他合理理解，防止单一过度解释。 |

## Non Goals

1. The system does not decide doctrine.
2. The system does not invent cases.
3. The system does not replace editorial review.
4. The system does not republish copyrighted modern full text unless permitted.
5. The system does not treat AI rewriting or translation as original evidence.

## Success Criteria

1. On a curated topic with at least five eligible, rights-cleared Cases, a teacher can get five relevant recommendations. For thinner coverage, return fewer with a clear coverage note; never pad with weak or invented matches.
2. Each recommendation includes a reason and a citation.
3. A video planner can create a usable outline from selected cases.
4. A researcher can inspect the source chain for each case.
5. New sources and cases can be added without changing the product model.
