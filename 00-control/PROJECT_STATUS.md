# Project Status

状态：v0.1 Pipeline foundation 准备提交。Article Run、Case fan-out、Case Run、版权预检和可追溯运行记录已实现；真实 AI baseline 尚未运行。

已完成：

- 初始化 Git 仓库。
- 创建 T00-T10 专题目录。
- 创建通用 schema、data、checkpoints、notes 目录。
- 创建 T10 产品定义、PRD 草案和工作流文档。
- 创建 seed dataset 计划和数据处理 workflow 文档。
- 完成 M0 Schema Lock：ID 规则、核心表、引用、文本版本、标签、创作者元数据、人物地点、去重规则。
- 完成 M1 Source Shortlist：锁定 5 个 seed 来源，每个来源 M2 取 2 个案例。
- 完成 M2 Ten-case Pilot 取样计划确认：先处理前 5 个案例，暂停审查，再处理后 5 个。
- 确定默认数据处理链条：rights precheck -> source capture -> segmentation -> atomic facts -> entity and dedup checks -> generated texts -> independent checks -> publication package。
- 已创建 M2 第一条草稿案例：CASE000001 陈妪随纺车念佛坐化。
- 已创建 M2 第二条草稿案例：CASE000002 阿冬师姐念佛百日自在往生。
- 已创建 M2 第三条草稿案例：CASE000003 家人为祖母助念引导往生。
- 已创建 M2 第四条草稿案例：CASE000004 演良居士梦中受指引至东林寺并临终助念往生。
- 已创建 M2 第五条草稿案例：CASE000005 麦居士引导失智母亲念佛并记述往生瑞相。
- 已建立原文保存策略：公版内容可提交，现代版权来源进入 Git 忽略的 restricted storage，manifest 与哈希可提交。
- 已保存并校验四个现代来源的 HTML/PDF 原始抓取文件，五个 source entry 均已建立 manifest。
- 已新增 source_segments、narrative analysis、interpretation_angles 和 generation provenance 数据结构。
- 已为前五条案例补充叙事分析和十个精确阐释角度。
- 已将四条过度压缩的 reader rendering 和五条 creator summary 标记为需要重新生成。
- 已定义法师讲稿的方法分析与 Prompt 评测工作流。
- 已定义面向普通读者的 `dharma_case_commentary`，与摘要和独立事实叙事分开保存与展示。
- 已新增 doctrinal citations、content claims 和 dharma commentary schema。
- 已建立导读文章硬性发布门槛：逐条事实、教理、引文、归因、版权与隐私检查；无依据或矛盾主张数量必须为零。
- 已建立独立版权研究流程，覆盖术语定义、来源级与单条审核、保存对象、AI处理、摘要、导读、翻译和数据分发。
- 已增加来源级与单条版权审核 schema，并完成 M2 四个现代来源的第一轮来源级审核。
- Purelanders 明确限制复制，标记为 `restricted_internal`；SRC0002、SRC0003、SRC0004 未找到足够的全文再利用许可，标记为 `legal_review_required`。
- 已完成五条 source entry 的正规化 JSON 保存；现代来源同时保留受限 HTML/PDF 原始载体。
- 提取脚本现可用 `--output` 原子写入单条 JSON 或批量 JSONL。
- 已将 T09 重构为 provider-neutral 的可复现 Pipeline：Article Run 先检测 0..N 个候选，程序随后分配 Case ID 并创建独立 Case Run。
- 已建立版本化 prompt、机器可读 contract、运行清单、依赖状态机、禁止覆盖规则和确定性 validator。
- 已建立前五条 M2 案例的回归测试政策；事实或版权硬门槛不能被可读性评分抵消。
- 已增加外部 AI 处理权限字段；`ai_processing_policy: unknown` 默认禁止发送完整原文。
- 已为 SRC0001-SRC0005 建立逐来源文章目录：`source.yml` 保存批处理默认值，`articles.csv` 保存完整文章清单、处理进度和人工审核状态。
- Pipeline runner 已接入文章目录资格检查；真实条目必须处于 selected、verified、ready 且版权状态不阻断，才能创建新 run。
- rights precheck 现核对 Source 配置、Article Catalog、rights review、manifest 路径与哈希；外部处理权限不能由命令行放宽。
- Catalog 状态由 Runner 在创建、推进、失败和完成时同步更新。
- 完整运行载荷保存在忽略目录，脱敏后的运行版本、状态、模型和哈希保存在可提交的 `data/run_records/`。
- 已将早期 M0/M1/M2 讨论稿、旧流程和五个 Markdown Case Pack 移入历史目录；当前架构文档压缩为实体边界、六步流程和 Adapter 说明。

进行中：

- T01-1：建立来源登记标准、评级体系和纳入标准。
- T10-0：定义产品用户画像、MVP 范围和创作辅助工作流。
- T02-3：执行 M2 Ten-case Pilot。

待开始：

- T01-2：中国大陆、台湾、香港、新马中文来源。
- T01-3：法师、YouTube、听众来信来源。
- T01-4：日本来源。
- T01-5：越南和韩国来源。
- T01-6：英语和欧美来源。
- T01-7：其他语种来源。

关键规则：

- Source 不等于 Case。
- 每个来源同时记录 Collection Priority 和 Automation Priority。
- 后期汇编不能直接当作最早出处。
- 转载、节录、讲述、翻译都需要保留转引链。

未决问题：

- 最终结构化数据格式使用 CSV、JSONL、SQLite、Postgres 还是组合方式。
- 是否需要同步到 Google Sheets 或 Notion 作为阅读界面。
- 主题到案例推荐的排序权重如何定义。
- 现代版权来源默认先采用 public_excerpt_only，需要逐案复核。
- 每个 source 的 extractor 质量需要在批量导入前逐源验证。
- 首个实际 AI adapter 和模型尚未选定；runner 当前只生成标准请求并接收标准响应，不持有 API 密钥。

下一步：

- 使用 `scripts/run_pipeline.py` 为 ENT000001 创建首个 Article Run，完成分段、候选检测和自动 Case fan-out。
- 将首个通过的 Article Run 与 Case Run 设为 baseline，然后以相同 Pipeline 运行 ENT000002-ENT000005。
- 对五条结果执行固定回归指标，修订 prompt 时创建新版本，不覆盖 v1。
- 建立第一批经过核对的净土教理引用，包含经论、祖师文献和明确归因的法师讲解。
- 选择一条 M2 案例试做 `dharma_case_commentary`，生成逐条 claim ledger 并执行完整发布检查。
- 在公开发布前联系四个现代来源的权利人或机构，确认内部保存、AI处理、翻译和公开摘录范围。
- 完成第一轮生成质量检查后，再继续 M2 后五条案例。
