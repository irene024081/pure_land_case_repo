# Pure Land Cases

长期项目：全球净土感应资料库。

目标是在同一个 Git 仓库内完成 T00-T10：来源总目录、数据模型、古代文献、近现代刊物、中文网站、YouTube 与法师来信、多语种来源、出处追溯与去重、Agent 自动更新、发布界面。

## 工作方式

1. 所有项目规则和总状态放在 `00-control/`。
2. 每个专题独立一个目录，按 `01-` 到 `10-` 编号推进。
3. 通用字段、枚举、评分标准放在 `schemas/`。
4. 可结构化数据放在 `data/`。
5. 已被取代的方案和里程碑记录放在 `docs/history/`，不得作为当前执行说明。

## 数据处理主链条

本项目采用可重跑、可检查、可替换模型的版本化 pipeline。聊天中的临时输出不直接成为项目数据。唯一的机器可读阶段定义是 `pipeline/pipeline.v1.json`，执行说明位于 `09-agent-automation/README.md`。

```text
source profile and inventory sync
-> source capture and rights precheck
-> Article Run: segmentation and case detection
-> assign Case IDs and create Case Runs
-> atomic case extraction
-> reader generation and creator analysis
-> independent factual check and rights check
-> deterministic publication packaging
```

原则：

1. 脚本负责可复现地抓取和切分来源文本。
2. `source_entries` 保存接近原文的条目，不等同于最终案例。
3. 原文按版权状态保存到 public 或 Git 忽略的 restricted storage，并用 manifest 和哈希验证。
4. `source_segments` 提供段落或时间码级的事实、推断、梦境与法义说明区分。
5. AI 只在固定 stage 中提出语义结果；prompt、输入输出 contract、模型和运行记录必须版本化。
6. 面向读者的教理导读使用独立流程：案例事实来自 source segments，教理判断来自审核过的 doctrinal citations。
7. 导读文章中的每条事实、教理、引文和实践建议都进入 content claim ledger；无依据、矛盾、错引或误归因会阻止发布。
8. 版权研究分别判断内部保存、AI处理、摘要、独立事实叙事、教理导读、翻译和数据分发，不能相互推定。
9. 生成和检查必须由不同 stage 完成；确定性 validator 决定是否通过，不由生成模型自行批准。
10. 任何公开案例都必须能追溯到 source、source entry、citation 或 evidence locator。
11. Stage 失败会阻止后续发布，重跑必须创建新 run，禁止静默覆盖旧产物。
12. 受限原文只有在 rights review 明确允许时，才能交给指定外部 AI provider。
13. 一篇 Article 可以产生零个、一个或多个 Case；Case ID 只能在候选检测后分配。

## 专题目录

| 编号 | 目录 | 专题 |
|---|---|---|
| T00 | `00-control/` | 项目总控 |
| T01 | `01-global-source-directory/` | 全球净土感应来源总目录 |
| T02 | `02-data-model/` | 数据结构与分类体系 |
| T03 | `03-ancient-texts/` | 古代净土感应文献与出处追踪 |
| T04 | `04-modern-periodicals/` | 近现代净土杂志与出版物 |
| T05 | `05-modern-chinese-websites/` | 现代中文净土网站 |
| T06 | `06-youtube-teacher-letters/` | YouTube 与法师来信案例 |
| T07 | `07-multilingual-sources/` | 全球多语种净土资料 |
| T08 | `08-provenance-dedup/` | 来源追溯与案例去重 |
| T09 | `09-agent-automation/` | Agent 自动更新 |
| T10 | `10-publication-interface/` | 检索、阅读与发布界面 |
