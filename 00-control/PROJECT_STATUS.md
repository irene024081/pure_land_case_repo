# Project Status

团队入口与阶段验收以 [PROJECT_HUB.md](PROJECT_HUB.md) 为准；本文件保留详细进度记录。 / The [project hub](PROJECT_HUB.md) is the team entry point and milestone gate; this file retains the detailed status log.

状态：Pipeline `0.2.0` 的 Candidate-first 流程已实现；M2A 迁移重放与 M2B 未见样本测试（两批共 4 个条目、5 个新 Case Run）均已完成，十阶段全部通过。首个已接受的 M2A baseline 仍是历史 `0.1.1` Run。

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
- 已将 T09 重构为 provider-neutral 的可复现 Pipeline：Article Run 先检测 0..N 个候选；v0.2 为每个候选创建独立 Run，提取和去重后再解决身份、分配 Case ID。
- 已建立版本化 prompt、机器可读 contract、运行清单、依赖状态机、禁止覆盖规则和确定性 validator。
- 已建立前五条 M2 案例的回归测试政策；事实或版权硬门槛不能被可读性评分抵消。
- 已增加外部 AI 处理权限字段；`ai_processing_policy: unknown` 默认禁止发送完整原文。
- 已为 SRC0001-SRC0005 建立逐来源文章目录：`source.yml` 保存批处理默认值，`articles.csv` 保存完整文章清单、处理进度和人工审核状态。
- Pipeline runner 已接入文章目录资格检查；真实条目必须处于 selected、verified、ready 且版权状态不阻断，才能创建新 run。
- rights precheck 现核对 Source 配置、Article Catalog、rights review、manifest 路径与哈希；外部处理权限不能由命令行放宽。
- Catalog 状态由 Runner 在创建、推进、失败和完成时同步更新。
- 完整运行载荷保存在忽略目录，脱敏后的运行版本、状态、模型和哈希保存在可提交的 `data/run_records/`。
- 已将早期 M0/M1/M2 讨论稿、旧流程和五个 Markdown Case Pack 移入历史目录；当前架构文档压缩为实体边界、六步流程和 Adapter 说明。
- 已完成 M2A：`ENT000001` 生成一个候选并沿用 `CASE000001`，Article Run 与 Case Run 全部完成。
- 首个 baseline 包含 8 个原文分段、22 条原子事实、4 段读者文本、2 个创作角度和 22 条事实检查声明；unsupported 与 contradicted 均为 0。
- Pipeline `0.1.1` 将 `creator_analysis` 纳入版权检查输入，并强制版权账本覆盖发布包中的全部输出。
- 已将 `RUN-ENT000001-M2A-P011` 与对应 Case Run 的脱敏记录登记为首个 machine-accepted regression baseline。
- Pipeline `0.1.2` 已加入版本化去重候选检索；候选、分数、命中理由、范围和候选集合哈希进入 Request 与 Run 状态。
- 去重候选包含受限数据时，该 Stage 自动禁止外部 Adapter；检索不会自动合并案例。
- Pipeline `0.1.2` 已让事实检查直接读取 `case_extraction`，并在去重身份未解决时将发布包设为 `withheld`。
- 已区分执行阻断、发布门槛和非阻塞质量问题，并建立 `KNOWN_ISSUES.md`。
- 已登记当前面向读者和创作者的 Output 及尚未实现的界面，见 `10-publication-interface/OUTPUT_INVENTORY.md`。
- Pipeline `0.2.0` 已新增 Candidate-first 的 `case_resolution` 和 `source_occurrence`，将案例身份与来源传播关系分离；自动复用旧 Case ID 被禁止。
- 已建立 T02 v0.2 字段迁移说明和 `CASE000001` 的拟迁移样例；旧 M2A baseline 与历史 contract 保持不变，尚未正式提升新 schema 数据。
- 已创建 `RUN-ENT000001-M2A-T02V02`：重放旧 Run 的原文分段和候选检测，并通过 `migrate_candidate_outputs.py` 对 22 条事实及标签引用作可核验的 ID 转换。此 Run 未使用新版 Prompt 重新生成事实。
- 新 Run 的去重请求在本地检索到旧 `CASE000001`；比较结果为 `same_case`，`case_resolution` 当前是 `review_required`，尚未复用 Case ID 或生成 Source Occurrence。
- 已提取两段 GPT 对话原文至 `notes/chatgpt_transcripts/`（2026-09-15 来源地图、2026-09-18 T02 最小架构），需求核对以此为准。
- 已完成产品需求访谈四轮并锁定 D1–D16，写入 `10-publication-interface/PRD_DRAFT.md`；新增 `THEME_ASSISTANT_DESIGN.md` 与 `PRODUCT_AI_ROLES.md`。
- 已建立 `00-control/ROADMAP.md`：从当前到产品落地的六阶段执行路线图。
- 已完成 M2A v0.2 迁移 Run：负责人（owner）裁定 `ENT000001-CAND0001` 复用 `CASE000001`，十阶段全部完成，无依据/矛盾主张为 0，发布包 public。
- 已找回 T01 全球来源注册表（385 条，三份对话导出）并归一化为 `01-global-source-directory/source_registry_v1.csv`；编号冲突经 `source_id_map.csv` 解决（现行 SRC0001-0005 不变，T01 编号保留为别名）；12 组疑似重复列入 `REVIEW_NEEDED.md` 待审。
- 已归档并映射 MVP 精选清单（43 条，42 条映射成功；T01 SRC0386 超出恢复范围待确认）。
- 已完成 M2B 第一批未见样本测试（2026-09-22，三个条目全部来自 SRC0001《净土圣贤录》卷九，AI 响应按 v2 prompt 全新生成，model 记为 `kimi-code local`）：
  - 普通条目 `ENT000006` 卢氏（名智福）传：`RUN-ENT000006-M2B-01`，分段 14 段无遗漏重叠，去重在检索范围内无候选（CASE000001 得分低于阈值），自动裁定新案例 `CASE000006`，十阶段完成，发布包 public。
  - 多案例条目 `ENT000007`（extractor 未拆分的三则传记）：`RUN-ENT000007-M2B-01`，正确拆为 3 个候选；`CASE000007` 温静文妻、`CASE000008` 钟离夫人任氏、`CASE000009` 越国夫人王氏，去重中同条目候选均被正确判为 distinct_case，身份无混淆，三个 Case Run 全部完成，发布包均 public。
  - 零案例样本 `ENT000008`《净土圣贤录叙》（彭际清撰）：`RUN-ENT000008-M2B-01`，分段 13 段，案例检测正确输出零候选，Article Run 直接完成、不产生 Case Run。
- 已完成 M2B 第二批新来源接入（2026-09-22，SRC0024《往生集》，明·袾宏，CBETA T51n2072 公版）：新建 `data/source_catalogs/SRC0024/`（source.yml + articles.csv）、版权记录 `data/rights_reviews/RR0006.yml`、条目 `ENT000009`（卷上·沙门往生类·僧濟）及 manifest；`RUN-ENT000009-M2B-01` 分段 13 段全覆盖，去重检索到 4 个已完成案例（CASE000001/0006/0007/0009，均仅凭流派标签得分 16 入选）并全部判 distinct_case，自动裁定新案例 `CASE000010`，十阶段完成，发布包 public。
- 已建立 `09-agent-automation/PIPELINE_STAGES.md`：Pipeline v0.2.0 十五个阶段的面向人工审核文档（目的/输入输出/是否用 AI/验收标准/常见失败），开头附全流程总表。
- 已建立 `scripts/render_case_report.py`（纯标准库）：输入 case run 或 article run 目录（或 `--all`）生成中文 HTML 审核报告到 `data/reports/`（git 跟踪）；单案例页含基本信息、原文分段、读者文本对照、事实清单、实体标签、去重记录、创作分析、事实检查、版权检查、审核状态；总览页一行一案例；受限来源原文自动遮蔽（按 manifest 的 storage_class 判断）。已为 6 个已完成案例生成报告 + 总览页。
- 已完成 ROADMAP 1.3 CBETA XML 适配器：`scripts/extract_cbeta_xml.py` v0.1.0（extraction_method `cbeta_xml_tei_structure`）。按 TEI `<head>`+`<p>` 结构切条目，目录 `<list>` 不参与切分；嵌套条目按 div 祖先关系正确拆分并在父记录 notes 标 `contains_nested_entries`。冒烟：T51n2072 全书提取 263 条（卷上 100 / 卷中 135 / 卷下 28），僧濟条 raw_text 与既有 ENT000009 逐字一致；X78n1549 往生女人第九提取 79 条，温静文妻/任氏/王氏被正确拆成三条（修复了 dazhouxian 提取器在 ENT000007 暴露的盲区）。测试见 `tests/test_extractors.py`（合成 fixture 4 用例）。
- 已完成 ROADMAP 1.4 最小正式数据提升（M2D 精简版，三样交付）：`data/canonical/schema.sql`（11 张表：cases、case_facts、entities、case_tags、source_occurrences、text_versions、identity_decisions、rights_decisions、dedup_index、promotion_log、schema_migrations；DDL 同时兼容 SQLite 与 Postgres）+ `scripts/canonical_store.py`（SQLite 落地 `data/canonical/canonical.db`，Git 忽略可重建）+ `scripts/promote_run.py`（promote/status/verify 三命令）。技术选型：本机暂无 Postgres，先以 SQLite 落地同一 schema，生产按 D10 切 Postgres 时只换存储层连接（详见 `data/canonical/README.md`）。提升幂等（同 Run 同指纹重复执行无操作）、拒绝未完成/已被取代的 Run、提升前校验全部 fact→segment、tag→fact、occurrence→entry、生成文本引用完整性；持久去重索引 dedup_index 按 `dedup_candidates.v2.json` 的归一化特征（persons/places/dates/tags）落库，供去重检索从扫目录升级为查库。6 个已完成案例（CASE000001、0006-0010）全部提升，verify 通过；删除 DB 后由 Run 证据重建内容哈希一致。
- 已完成 ROADMAP 1.6 Provider 中立 AI API 适配器：`scripts/ai_adapter.py` + `run_pipeline.py run-stage`。统一接口输入 runner 生成的 request JSON、输出 accept 格式响应；OpenAI / Anthropic / Google / Kimi 四家配置（端点、模型、密钥环境变量名）放 Git 忽略的 `scripts/ai_providers.json`（模板 `ai_providers.example.json`）；每次调用记录 prompt 版本、模型、token、估算成本、重试次数、耗时至 Git 忽略的 `data/adapter_logs/calls.jsonl`，脱敏摘要写入 run.json 阶段 `api_call` 并同步 run_records；指数退避重试，失败写日志并中止。红线复用现有拦截：`external_processing` 非 allowed 时 run-stage 直接拒绝（当前所有来源均 blocked，故现有 Run 仍全部走本地 adapter）。KI-003 标记已解决；真实厂商联调待负责人提供密钥。
- 已完成 ROADMAP 2.0 前半（四类网页目录适配器）：`scripts/inventory_adapters.py`（static_headings / wordpress_archive / paginated_html / pdf_toc 四家族统一接口）+ `scripts/run_inventory.py`（scan/--dry-run；增量去重、消失条目标 removed 不删除、新行默认 unreviewed+pending）。真实来源验证：paginated_html → SRC0003 plb.tw 往生故事栏目落库 481 条（含修正会话参数与栏目自链两个问题）；wordpress_archive → SRC0387 duongvecoitinh 归档页发现 268 条（未注册该来源目录，dry 验证）；static_headings → 保存的 X78n1549 页（往生女人第九 70 条，与既有清点一致）；pdf_toc → SRC0002 保存的受限 PDF 目录页解析 109 条（仅标题+页码元数据，未落库）。注意：目录发现只登记元数据，不代表任何来源获准 AI 处理或公开。
- 已完成 ROADMAP 2.0 后半（YouTube 频道登记与发现/文字稿工具）：`data/youtube_watch/channel_registry.csv` 预填五个重点频道（净本/净平→SRC0159、道晟→SRC0176、净土宗官方→SRC0158、信愿→注册表无 repo 行已标 pending、净空体系→SRC0170；channel_id 全部 pending 待人工确认）；`scripts/youtube_watch.py` 提供 channels / scan / transcript 三命令——发现只走官方 Data API（playlistItems.list），不爬网页和字幕；文字稿链实现前两级（官网目录匹配+来源提取器、description 提取），字幕 API 与本地转写留占位待授权。测试全 mock（8 用例）。

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
- M2A 使用声明为 `local` 的 `codex-gpt5` 生成标准响应；runner 仍未实现自动 API adapter，也不持有 API 密钥。
- `reader_generation/v1` 的转述较平，`creator_analysis/v1` 的角度可能过泛；两项暂作为预览质量问题，M2B 后再设计 v2。
- 当前 v0.2 去重候选检索只扫描同一运行根目录中的已完成 Case Run，并使用精确结构化值；正式案例索引和模糊召回留到 M2D。
- v0.2 已就《净土圣贤录》未见条目完成端到端 Run（M2B 第一批），但 M2B 的 AI 响应由本地 adapter 人工撰写，仍不能替代新版 Prompt 在真实模型上的独立质量评估。

下一步：

- 由人工明确审核 `ENT000001-CAND0001` 是否复用 `CASE000001`，并记录审核人和理由；之后完成 Source Occurrence、生成文本、独立检查与发布门槛。
- 再执行 M2B 第二批：一个新公版或开放许可 Source 的条目（第一批已覆盖普通、多案例、零案例三类，均出自 SRC0001）。
- 对 unseen results 执行固定回归指标；修订 prompt 时创建新版本，不覆盖已使用版本。
- M2B 后续观察：extractor 对「内层标题下一段不以标题开头」的条目有拆分盲区（ENT000007 实例）；CBETA XML 尚无版本化提取脚本（ROADMAP 1.3），ENT000009 用临时解析完成。
- 建立第一批经过核对的净土教理引用，包含经论、祖师文献和明确归因的法师讲解。
- 选择一条 M2 案例试做 `dharma_case_commentary`，生成逐条 claim ledger 并执行完整发布检查。
- 在公开发布前联系四个现代来源的权利人或机构，确认内部保存、AI处理、翻译和公开摘录范围。
- 完成第一轮生成质量检查后，再继续 M2 后五条案例。
