# Product Definition

本产品是面向净土宗资料使用者的「案例检索、阅读与创作辅助工作台」。

它不是普通故事网站，也不是自动生成讲稿工具。核心价值是让普通读者能读懂、查到、核对净土感应案例，同时让法师和创作者能按主题找到合适案例，并保留出处、可信度、版权和适配说明。

## Primary User Profiles

### 1. General Reader

用户状态：

- 想阅读真实、可信、可追溯的净土感应与往生案例。
- 可能从人物姓名、瑞相、来源、主题或关键词进入。
- 不一定懂文言文、期刊体系或出处链。
- 关心故事是否可信、原文在哪里、是否还有类似案例。

核心任务：

- 搜索案例。
- 阅读忠实可读版。
- 展开查看原文证据、出处和引用位置。
- 按来源、人物、瑞相、主题、时代、地区继续探索。
- 收藏、分享或引用案例页面。

### 2. Dharma Teacher Or Preacher

用户状态：

- 已经有法义主题、开示方向或视频选题。
- 需要找到能贴合主题的案例。
- 关心案例是否可靠、是否适合大众听、是否会造成误解。

核心任务：

- 输入主题和讲述目标。
- 获取按相关度排序的案例推荐。
- 查看每个案例为什么适合这个主题。
- 查看出处、可信度、引用说明和使用风险。
- 选择案例后生成讲述结构或视频提纲。

### 3. Video Planner, Editor, Or Channel Operator

用户状态：

- 负责栏目策划、短视频、长视频、标题、脚本、剪辑素材。
- 不一定熟悉完整文献系统。
- 需要快速找到故事、主题组合和可讲述素材。

核心任务：

- 按主题、时长、受众、情绪强度和视频类型筛选案例。
- 找到适合短视频、长视频、系列视频的案例包。
- 生成选题列表、脚本大纲、标题方向和引用备注。

### 4. Researcher Or Source Editor

用户状态：

- 关注来源、版本、出处链、重复案例和可信度。
- 可能不制作视频，但负责资料库质量。

核心任务：

- 审核来源。
- 合并重复案例。
- 追踪更早出处。
- 标注版权、隐私和证据等级。

这四类用户都重要。MVP 先同时服务普通读者和法师、弘法者：普通读者需要搜索和可信阅读，法师和创作者需要在同一批可信案例上做主题配例。研究者和编辑所需的数据字段必须从第一版开始保留，避免后续重做模型。

## Core Product Positioning

产品有两个一等入口。

Reader Search 从普通读者的查找和阅读开始：

```text
我想找关于临终异香的案例。
我想查某位往生者的名字。
我想看《净土》杂志里有哪些助念案例。
```

系统应该返回：

```text
搜索结果
命中片段
忠实可读版
原始出处
相关人物、瑞相、标签
相关案例
```

Theme Assistant 从法师或创作者的弘法意图开始。用户不是从空白页开始让 AI 写内容，而是从一个具体主题和受众开始。

典型输入：

```text
我想做一期 8 分钟视频，主题是临终助念为什么重要，希望用现代真实案例，不要太玄奇，要适合普通家属听。
```

系统应该返回：

```text
推荐案例
相关原因
适合插入的位置
原始出处和引用链
可信度等级
视频适配度
版权和隐私注意事项
可选讲述角度
```

## Product Principles

1. 普通读者可以先搜索和阅读，创作者可以先输入主题并获得案例推荐。
2. 推荐必须基于资料库，不凭空编故事。
3. 每个推荐都说明相关原因。
4. 原始证据、可读化文本、整理摘要、AI 辅助内容必须明确区分。
5. AI 可以生成明确标注的教理导读草稿，但每个事实、教理、引文和实践建议都必须绑定审核过的来源并通过发布检查。
6. 可信度、出处链、版权和隐私风险是产品的一部分，不是后台细节。
7. 读者阅读体验是产品核心，不是创作者工具的附属功能。

原文在版权和访问条件允许时作为内部证据层长期保存。读者文本和创作辅助是可以重新生成的派生内容，不能替代原文。

版权研究覆盖来源、单篇条目、保存对象和最终生成内容。公开访问不等于允许复制，内部保存不等于允许AI处理，允许摘要不等于允许翻译或表达性改编。各用途分别记录决定和依据。

## Reader Content Policy

面向读者的核心体验是「保真可读」。读者默认看到 AI 辅助生成或人工编辑的忠实可读版，同时可以展开查看原始证据。

这里的重写不是自由创作，而是受约束的可读化处理。它只允许改善表达、结构、断句、顺序和术语解释，不允许新增人物、情节、因果判断、神异细节或法义结论。

推荐层级：

```text
short_summary
reader_rendering
original_evidence
source_citation
```

普通读者还可以阅读独立的教理导读层：

```text
independent_factual_account
dharma_case_commentary
case_sources
doctrinal_sources
claim_review_status
```

`short_summary` 是一句话到三句话摘要，用于搜索结果、首页卡片和快速判断。

`reader_rendering` 是面向普通读者的忠实可读版。文言文来源做白话译述，第一人称记载做可读整理，YouTube 字幕和口述转录做通顺整理，现代期刊和长文做压缩整理。它可以提高阅读体验，但不能改变事实。

详情页的主要 `reader_rendering` 应当是原文能够支持的完整可读叙事，保留处境、困难、转折、实践过程、结果、报告者归属和未决问题。压缩版本另存为 `reader_summary`，不能用摘要代替正文。

`original_evidence` 是原文证据。公版古籍和允许展示的材料可以展示较完整原文。现代期刊、书籍、网站和视频材料按版权风险展示短摘录、定位信息和来源链接。

页面必须明确标注文本性质：

```text
原文
白话译述
整理摘要
AI 辅助说明
```

读者默认看到 `short_summary` 和 `reader_rendering`，并能展开查看 `original_evidence`。研究者和创作者需要能快速跳到原文和出处。

## Dharma Case Commentary Policy

`dharma_case_commentary` 是面向普通读者的表达性文章。它可以用问题、结构、节奏和解释提高可读性，但不能依靠虚构案例细节制造感染力。

内容职责必须分开：

```text
case evidence -> 人物、时间、地点、事件、报告者和不确定性
doctrinal citations -> 教理判断、经论引文和实践原则
reviewed source methods -> 如何开场、过渡、回应疑问和联系现实
AI -> 独立组织结构与表达
```

禁止使用模型记忆充当教理来源。文章中的事实、教理、引文、法师解释和实践建议都要进入 `content_claims`，并绑定相应证据。

公开页面必须显示：

```text
AI-assisted commentary label
case source links
doctrinal source links
teacher attribution where applicable
machine or human review status
clear separation from independent_factual_account
```

以下情况阻止公开：

```text
存在无来源事实或教理
引用无法核对
引用不支持文章实际结论
把梦境、瑞相、转述或作者推断写成已验证事实
把个案写成往生证明
把某位法师解释写成净土宗统一结论
高影响实践建议缺少审核依据
版权策略不允许当前表达方式
```

版权检查同时评估导读文章是否复用了独特措辞、段落结构、对话、意象和叙事安排，以及是否可能替代受限制原文。符合事实不等于符合版权策略；表达足够独立也不允许增加来源没有的事实。

详细流程见 `../02-data-model/DHARMA_CASE_COMMENTARY_WORKFLOW.md`。

## Source-specific Readability Rules

不同来源需要不同的可读化规则。

| Source situation | Reader default | Evidence retained | Boundary |
|---|---|---|---|
| Classical Chinese text | 白话译述 | 原文、卷数、条目、版本 | 不补充原文没有的情节。 |
| YouTube transcript | 口述整理版 | 原始字幕、时间戳、视频链接 | 可删除口头重复和语气词，但不改变讲述顺序中的事实关系。 |
| First-person testimony | 第一人称整理版或第三人称整理版 | 原文摘录、投稿来源、作者说明 | 尽量保留见证者身份和叙述立场，不把推测写成事实。 |
| Modern periodical article | 摘要加短摘录 | 刊名、期号、页码、文章标题 | 按版权风险控制公开展示长度。 |
| Reposted web article | 标准梗概加追源状态 | 转载页、原始链接、发现来源 | 明确标注是否找到更早出处。 |
| Multilingual source | 中文译述加原文入口 | 原文、译者、语言、版本 | 翻译应保留不确定术语，不强行改成中文净土术语。 |

## Fidelity Rules For AI Rewriting

AI 可读化处理必须遵守以下规则：

```text
preserve_people
preserve_place
preserve_time
preserve_event_order
preserve_source_claims
preserve_uncertainty
do_not_add_doctrinal_claims
do_not_add_emotional_reactions
do_not_add_miraculous_details
do_not_merge_separate_cases
```

每个 `reader_rendering` 都需要能回到 `original_evidence` 和 `source_citation`。如果原始材料含糊，整理版也必须保留含糊，不改成确定叙述。

## Multilingual Expansion

未来可以为同一个案例提供多语言可读版。

```text
reader_rendering_zh
reader_rendering_en
reader_rendering_ja
reader_rendering_ko
reader_rendering_vi
```

多语言版本同样属于 `faithful_rendering` 或 `translation`，不能当作新的案例证据。页面应显示译文所依据的原文、译者或生成方式、审核状态。

## Unified Case Detail

读者和创作者不使用两套事实页面。每个案例只有一个 Case Detail，但有两个显示模式。

Reader View 默认展示：

```text
short_summary
reader_rendering
independent_factual_account
dharma_case_commentary when published
original_evidence
source_citation
tags
related_cases
```

Creator View 默认展示：

```text
short_summary
creator_summary
teaching_themes
interpretation_angles
recommended_usage
video_fit
source_citation
provenance_quality
risk_notes
similar_cases
```

两个视图共享同一个 `case_id`、`occurrence_id`、标签、人物、地点和证据等级。旧 `citation_id` 需通过迁移映射关联到 Source Occurrence。区别只是展示顺序和辅助信息。

`independent_factual_account` 和 `dharma_case_commentary` 不得合并成一个无标签文本。前者回答“来源记载了什么”，后者回答“经过引用核验后，可以怎样理解和实践”。

`creator_summary` 用于快速判断是否值得采用。`interpretation_angles` 才承载精确创作建议，每个角度必须包含目标受众、核心主张、证据段落、建议结构、必要背景和不能越过的法义或证据边界。

## Search And Highlighting

基础搜索必须同时服务读者和创作者。

用户可以按以下入口检索：

```text
source
reborn_person_name
witness_name
case_type
rebirth_sign
keyword
period
region
language
```

搜索结果需要显示命中的字段和片段：

```text
matched_source_title
matched_person_name
matched_original_excerpt
matched_reader_rendering
matched_tag
```

命中关键词应该在结果页和详情页中高亮。高亮只用于阅读和定位，不改变原文。

## MVP Scope

第一版必须同时包含公开阅读层和创作者辅助层：

Public Reader Layer:

1. Homepage：展示若干经典案例、主题入口、来源入口。
2. Case search：按关键词、来源、往生者姓名、见证者、瑞相、时代、地区、案例类型搜索。
3. Search results：展示命中字段、命中片段和高亮关键词。
4. Case detail page：展示摘要、忠实可读版、原始证据、出处、标签、相关案例。
5. Source detail page：展示来源信息、收录范围、处理状态和该来源下的案例。

Creator Layer:

1. Theme-to-case recommendation：输入主题后推荐相关案例。
2. Creator View：在同一个 Case Detail 中展示主题、用途、风险和相似案例。
3. Case basket：把多个案例加入一个选题篮。
4. Creator brief：选定案例后生成视频提纲、讲述摘要和引用说明。

暂不做：

1. 用户社区。
2. 自动发布视频。
3. 自动全文转载现代版权材料。
4. 无审核的自动入库。
