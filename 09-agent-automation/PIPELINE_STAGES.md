# Pipeline v0.2.0 逐步骤说明

本文用大白话讲解流水线的每个阶段：它干什么、吃什么、产出什么、机器怎么验收、失败了怎么办。
依据是代码与契约本身：`pipeline/pipeline.v2.json`、`pipeline/prompts/`、`pipeline/contracts/`、`scripts/run_pipeline.py`。
先看运行方式请看同目录 `README.md`。

## 全流程总表

| # | 阶段 | 属于 | 用 AI？ | 输入 → 输出 | 不过会怎样 |
|---|------|------|---------|-------------|-----------|
| 1 | source_registration 来源登记 | Article | 否（确定性门槛） | 来源目录 → 登记证据 | 建不了 Run |
| 2 | rights_precheck 版权预检 | Article | 否（确定性门槛） | 目录 + rights review + manifest → 许可结论 | 建不了 Run |
| 3 | source_capture 原文落库 | Article | 否（确定性门槛） | 条目 JSON + 哈希核对 → 捕获证据 | 建不了 Run |
| 4 | source_segmentation 原文分段 | Article | 是 | 条目原文 → 分段清单 | 拒绝该响应，重写重交 |
| 5 | case_detection 案例检测 | Article | 是 | 分段清单 → 0..N 个候选 | 拒绝该响应，重写重交 |
| 6 | case_extraction 原子事实 | Case | 是 | 候选边界 + 分段 → 事实清单 | 拒绝该响应，重写重交 |
| 7 | entity_tagging 实体与标签 | Case | 是 | 分段 + 事实 → 人物/地点/标签 | 拒绝该响应，重写重交 |
| 8 | deduplication 去重比较 | Case | 是（受限时只许本地） | 已完成案例的检索候选 → 同案/异案判断 | 拒绝该响应；判断含糊则进人工 |
| 9 | case_resolution 身份裁定 | Case | 否（确定性） | 去重结论 → Case ID | 非明确新案时停下来等负责人 |
| 10 | source_occurrence 来源出现记录 | Case | 是 | 候选边界 + 种子 → 本条在来源中的出现档案 | 拒绝该响应，重写重交 |
| 11 | reader_generation 读者文本 | Case | 是 | 事实 + 分段 → 白话正文与摘要 | 拒绝该响应，重写重交 |
| 12 | creator_analysis 创作分析 | Case | 是 | 事实 + 实体 → 创作元数据与角度 | 拒绝该响应，重写重交 |
| 13 | factual_check 事实检查 | Case | 是 | 读者文本 + 创作分析 vs 事实 → 逐条裁决 | gate=fail 则发布包被扣下 |
| 14 | rights_check 版权检查 | Case | 是 | 生成文本 vs 版权记录 → 逐输出结论 | gate≠pass 则发布包被扣下 |
| 15 | publication_packaging 发布打包 | Case | 否（确定性） | 各检查结论 → 发布包 | 有阻断项则 publish_status=withheld |

「拒绝该响应」的意思是：runner 的 validator 不收这份 AI 响应，阶段的 request 文件还在，重新生成一份响应再 `accept` 即可；已接受的输出永远不覆盖，要重来就开新 Run。

---

## 一、Article Run 的确定性门槛（1–3）

这三个阶段没有 AI，创建 Article Run 时由 runner 一次性完成，任何一项不过就直接建不了 Run（命令报错退出）。

### 1. source_registration 来源登记

- **目的**：确认这个条目属于一个已登记的来源。
- **输入**：source entry JSON 里的 `source_id`；对应的 `data/source_catalogs/{source_id}/source.yml` 和 `articles.csv`。
- **输出**：`run.json` 里该阶段标记 completed，证据为来源 ID。
- **AI**：不用。
- **验收**：来源目录存在且条目在目录中有唯一一行。
- **常见失败**：目录里查不到该 `source_entry_id`，或一行都匹配不到（报 "expected one catalog row"）。处理：先把条目登记进 articles.csv。

### 2. rights_precheck 版权预检

- **目的**：在动工之前确认这份材料的版权允许处理，并决定能否用外部 AI。
- **输入**：`source.yml`、`articles.csv` 行、`data/rights_reviews/{RR}.yml`、`data/source_entries/manifests/{ENT}.yml`。
- **输出**：`run.json` 里记 `rights_review_id`、`external_processing`（allowed/blocked）。
- **AI**：不用。
- **验收**（全部硬核对）：
  - 文章行必须 selection=selected、capture=verified、pipeline=ready，且版权状态不是 pending/unknown/prohibited；
  - source.yml 与文章行指向同一个 rights review；
  - rights review 的 source_id、版权状态与目录一致；
  - manifest 的捕获状态是 `persisted_verified`，其记录的文件路径和哈希与条目文件实际一致。
- **常见失败**：manifest 哈希对不上（条目文件被改过）——停下来核对，不许改 manifest 凑数；文章行状态不对——先按目录流程改状态。
- **注意**：只有 `source.yml` 的 `external_processing_default: allowed` 且 rights review 允许时，`external_processing` 才是 allowed；命令行参数无法放宽。

### 3. source_capture 原文落库

- **目的**：确认本次处理用的原文就是落库的那份，一字不差。
- **输入**：条目 JSON 的 `raw_text` 与 `raw_text_hash`。
- **输出**：阶段 completed，证据为 `raw_text_hash`。
- **AI**：不用。
- **验收**：`sha256(raw_text) == raw_text_hash`。
- **常见失败**：哈希不符（文件被编辑过）。处理：恢复原文或重走条目登记。

---

## 二、Article Run 的 AI 阶段（4–5）

### 4. source_segmentation 原文分段

- **目的**：把整条原文切成最小有用的小段，每段标清是谁在说、属于什么性质。
- **输入**：条目原文（request 里带完整 source_entry）。
- **输出**：`outputs/source_segmentation.json`：每段有 segment_id（`{条目}-SEGxxxx`）、起止字符位置、原文、内容哈希、类型（叙述/对话/梦或见/编者注等）、claim_mode（自述/传闻/梦境/编者推断等）、说话人。
- **AI**：用。Prompt：`pipeline/prompts/source_segmentation/v1.md`。核心要求：
  1. 逐字照抄原文，不许改写、翻译、省略；
  2. 说话人、观察者、文体功能变了就切开；
  3. 梦/见与外部事件分开；
  4. 每段给零基起止偏移，全部字符恰好属于一段，不重不漏；
  5. 每段 content_hash 是其内容的 SHA-256。
- **验收（validator）**：段序从 1 连续；segment_id 唯一；偏移首尾相接、无重叠无缺口；`raw_text[start:end]` 与 content 逐字一致；哈希一致；类型/claim_mode 在允许值内。
- **常见失败**：偏移算错或漏了换行缩进（报 "segments must cover source text" / "offsets do not match"）。处理：用脚本按切分点重算偏移和哈希，不要手改数字。

### 5. case_detection 案例检测

- **目的**：判断这条原文里有几个案例（可以是零个），圈出每个案例的边界，但还不分配正式 Case ID。
- **输入**：分段清单。
- **输出**：`outputs/case_detection.json`：`case_candidates` 数组，每个候选有 candidate_id（`{条目}-CANDxxxx`）、暂定标题、支撑段 ID、边界置信度、说明。零案例时是空数组。
- **AI**：用。Prompt：`pipeline/prompts/case_detection/v1.md`。核心要求：
  1. 不分配正式 Case ID；
  2. 候选要引全自己边界所需的段；
  3. 不同人物/事件分开，除非文本明确是同一件事；
  4. 没有案例就返回空数组，不许硬造；
  5. 评论、目录、教理议论不是案例。
- **验收**：candidate_id 唯一且是安全路径字符；每个候选的支撑段都来自分段阶段的真实段 ID。
- **之后**：runner 自动为每个候选在 `candidates/` 下创建 Case Run。空数组则 Article Run 直接完成（零案例条目到此结束）。
- **常见失败**：引了不存在的段 ID（报 unknown IDs）。处理：对照分段输出重写。

---

## 三、Case Run 阶段（6–15）

每个候选一个独立 Case Run，目录在 `Article Run 目录/candidates/{candidate_id}/`。

### 6. case_extraction 原子事实抽取

- **目的**：把候选边界内的内容拆成一条条可独立核对的事实。
- **输入**：候选边界 + 分段清单。
- **输出**：`outputs/case_extraction.json`：事实清单，每条有 case_fact_id（`{候选}-FACTxxxx`）、命题、类型、claim_mode、支撑段、不确定说明。
- **AI**：用。Prompt：`pipeline/prompts/case_extraction/v2.md`。核心要求：
  1. 事实 ID 用候选前缀（此时还没有正式 Case ID）；
  2. 保留谁说的/谁见的、出处、不确定性、时间、梦与醒的区分；
  3. 每条事实引确切的支撑段，不合并可独立检验的命题；
  4. 只描述来源记载了什么，不断言宗教体验为真；
  5. 不猜身份、不补细节、不加 case_id。
- **验收**：事实 ID 唯一且用候选前缀；每条事实的支撑段都在本候选边界内。
- **常见失败**：事实引了边界外的段（报 "cites a Source Segment outside its candidate boundary"）。处理：回到 case_detection 核对边界。

### 7. entity_tagging 实体与标签

- **目的**：列出案例里的人物、地点和检索标签。
- **输入**：分段 + 事实清单。
- **输出**：`outputs/entity_tagging.json`：persons（含 name_status：known/partial/anonymous 等）、places、tags（带 tag_class）。
- **AI**：用。Prompt：`pipeline/prompts/entity_tagging/v2.md`。核心要求：
  1. 只用给定的段和事实，每个实体/标签都要引证据；
  2. 已知名、半名、匿名要分清，不许用「他妻子」这种关系称呼当名字；
  3. 不许从大地名推小地名；
  4. 瑞相按「来源的报告」处理，不当已验证事件。
- **验收**：persons/places 引真实段 ID，tags 引真实事实 ID；tags 至少 1 条。
- **常见失败**：标签引了不存在的事实 ID。处理：对照事实清单重写。

### 8. deduplication 去重比较

- **目的**：查这个候选和库里的旧案例是不是同一个人/同一件事。
- **输入**：runner 先按 `pipeline/retrieval/dedup_candidates.v2.json` 做确定性检索——从同一运行根目录里所有**已完成**的 Case Run 中，按人名/地名/日期/标签的精确匹配打分，超过阈值（15 分）的才交给 AI 比较；检索的版本、得分、理由都写进 request。若候选含受限数据，本阶段强制只用本地 adapter。
- **输出**：`outputs/deduplication.json`：对**每个**被检索到的候选案例给一条比较记录（same_case / distinct_case / possible_same_case / needs_human_review），加 overall_decision 与理由。
- **AI**：用。Prompt：`pipeline/prompts/deduplication/v2.md`。核心要求：
  1. 每个送来的候选都必须比较一次，即使明显不同；
  2. 只有全部判不同（或根本没送来候选）才能 overall=new_case，且这只是"检索范围内无匹配"，不是全球唯一证明；
  3. 情节、修法、瑞相相似永远不足以判同案，要对人名、日期、地点、家属、事件顺序、独有细节、来源传承；
  4. 拿不准就用 possible_same_case/needs_human_review；
  5. 不合并记录、不分配 Case ID。
- **验收**：比较记录与送来的候选一一对应、不重不漏；overall 与逐条判断逻辑自洽（如 new_case 要求全部 distinct）；理由非空。
- **常见失败**：漏比某个候选（报 "must compare every supplied candidate"）。处理：补齐。overall 判了非 new_case 时，下一阶段会停下来等人工——这是设计，不是故障。

### 9. case_resolution 身份裁定

- **目的**：给候选一个正式身份——新 Case ID，或复用旧 Case ID。
- **输入**：去重结论。
- **输出**：`outputs/case_resolution.json`：candidate_id、case_id、resolution_kind（new/reuse）、裁定依据。
- **AI**：不用（确定性）。规则：
  - overall=new_case 且该文章没有预登记案例 → 自动分配新 Case ID（依据 scoped_no_match）；
  - 其他情况（new_case 但文章已有预登记案例、或判了 same/possible/needs_review）→ 状态变为 `review_required`，整个 Run 标记 **blocked**，等负责人裁定；
  - 负责人用 `run_pipeline.py resolve-identity --action new|reuse --reviewer ... --reason ...` 裁定；reuse 只能指向已知 Case ID，必须署名和写理由。
- **常见失败**：误以为自己可以 resolve。**只有负责人能做身份裁定**；AI 执行者看到 review_required 就停下报告。

### 10. source_occurrence 来源出现记录

- **目的**：记录这个案例在这条来源里的具体"出现档案"——在哪、什么文体、从哪传下来的。
- **输入**：`occurrence_seed`（runner 预生成，含 occurrence_id、case_id、条目、支撑段、locator）+ 该案例已知的其他 occurrence。
- **输出**：`outputs/source_occurrence.json`：seed 原样保留 + content_form、voice、parent_links（上游传承关系）、review_status。
- **AI**：用。Prompt：`pipeline/prompts/source_occurrence/v1.md`。核心要求：
  1. seed 里的字段逐字照抄，不许改；
  2. 上游关系只对「文中明确提到但未捕获」的文本用 unresolved_upstream，不假装读过；
  3. 不许编 occurrence ID 或来源 ID；
  4. 没有依据支持上游关系时 parent_links 留空。
- **验收**：seed 各字段原样；parent link 的 target 状态合法、known 必须指向已知 occurrence；链接引的段在本案例边界内。
- **注意**：occurrence 的 review_status 若为 needs_review，最终发布包会被扣下（withheld）。
- **常见失败**：改了 seed 里的值（报 "must preserve occurrence_seed.xxx"）。处理：从 request 里复制。

### 11. reader_generation 读者文本

- **目的**：写一份给普通读者看的忠实白话版 + 一段摘要。
- **输入**：事实清单 + 分段（此时 Case ID 已定）。
- **输出**：`outputs/reader_generation.json`：reader_title、paragraphs（每段引支撑事实与段）、reader_summary。
- **AI**：用。Prompt：`pipeline/prompts/reader_generation/v1.md`。核心要求：
  1. 保住时间顺序、人物、归因、不确定性和重要上下文；
  2. 提高可读性但不许编造场景、对话、情绪、因果、感官细节或教理结论；
  3. 瑞相要标明是谁报告的；
  4. 每段引全支撑事实和段。
- **验收**：每段的支撑事实/段 ID 真实存在；至少一段。
- **常见失败**：引了不存在的事实 ID。处理：对照事实清单重写。

### 12. creator_analysis 创作分析

- **目的**：给内容创作者用的元数据和"精确阐释角度"（这个案例可以怎么讲、边界在哪）。
- **输入**：事实 + 实体标签（Case ID 已定）。
- **输出**：`outputs/creator_analysis.json`：creator_metadata（主题、受众、视频适配度、风险提示等）+ interpretation_angles（每个角度：核心主张、受众、证据、建议用法、教理边界）。
- **AI**：用。Prompt：`pipeline/prompts/creator_analysis/v1.md`。核心要求：
  1. 描述"可以怎么用"，不讨论历史真假；
  2. 每个角度要有窄而明确的主张、受众、证据、用法、教理边界；
  3. 没有已审核教理引用时不许下教理结论；
  4. 要指出缺失上下文、煽情风险、隐私风险、不适合的用法；
  5. 「念佛」这种宽泛标签不算角度。
- **验收**：至少一个角度；角度引的事实/段 ID 真实存在。
- **常见失败**：角度写成大词空话（机器查不出，靠人工阅读把关——这正是审核报告要呈现的内容）。

### 13. factual_check 事实检查

- **目的**：换一个"独立检查员"视角，把读者文本和创作分析拆成逐条 claim，对照事实清单核验。
- **输入**：case_extraction + reader_generation + creator_analysis。
- **输出**：`outputs/factual_check.json`：claims（每条 claim 引支撑事实/段 + verdict：supported/partially_supported/unsupported/contradicted/not_factual）、unsupported/contradicted 计数、gate_result。
- **AI**：用。Prompt：`pipeline/prompts/factual_check/v1.md`。核心要求：
  1. 查事实支撑、归因、不确定性、时间顺序、来源性质；
  2. supported 必须有足够引用证据；
  3. 新增内容判 unsupported，冲突判 contradicted；
  4. 文字通顺、言之成理不算证据；
  5. 有任何 unsupported/contradicted 就必须 gate=fail。
- **验收**：计数与实际 verdict 一致；gate_result 与计数一致（有未支撑即 fail）。
- **常见失败**：计数或 gate 与 claims 不符（机器报 mismatched）。处理：如实重算。gate=fail 时发布包 withheld——不许回头改生成文本凑通过，要改就开新 Run。

### 14. rights_check 版权检查

- **目的**：对照该来源的版权审核记录，逐项检查生成文本能不能发布、能发布到什么程度。
- **输入**：reader_generation + creator_analysis + rights review。
- **输出**：`outputs/rights_check.json`：checks（每个被检查的输出：引用情况、表达相似风险、结论）、gate_result、allowed_display_scope。
- **AI**：用。Prompt：`pipeline/prompts/rights_check/v1.md`。核心要求：
  1. 保存、AI 处理、引用、摘要、转述、翻译、评论、商用、数据集分发是各自独立的用途，逐项看；
  2. 查直接引用、近似改写、独特选材编排、对话、意象、节奏、替代风险；
  3. 事实可留，受保护的表达要删或减；
  4. 未知许可不是许可；不许用字数或改写比例推"合理使用"。
- **验收**：rights_review_id 与 Run 一致；checks 恰好覆盖 reader_generation 和 creator_analysis 两个输出、不多不少；gate=pass 时不许有被标 fail 的输出；allowed_display_scope 不得超过 rights review 的公开政策。
- **常见失败**：漏查一个输出（报 missing required outputs）。处理：补齐。gate≠pass 时发布包 withheld。

### 15. publication_packaging 发布打包

- **目的**：把一切汇总成一个发布包，标明能不能公开。
- **输入**：case_resolution + source_occurrence + factual_check + rights_check（全部完成后 runner 自动生成，无 request）。
- **输出**：`outputs/publication_packaging.json`：case_id、publish_status（public / public_excerpt_only / internal / withheld）、withheld_reasons、包含的输出、溯源（run_id、pipeline 版本、条目哈希）。
- **AI**：不用（确定性）。
- **验收逻辑**：publish_status 以 rights_check 的 allowed_display_scope 为上限；只要事实检查 fail、版权检查 fail、或 occurrence 仍需审核，就一律 withheld 并记录原因。
- **常见失败**：不会失败；若结果 withheld，读 withheld_reasons 找原因。

---

## 附：状态与记录

- 每个阶段的 request（完整输入+prompt）在 `requests/`，AI 响应原件在 `responses/`，验收后的输出在 `outputs/`，全部保存在 Git 忽略的 `data/pipeline_runs/`。
- 脱敏后的运行身份、模型、阶段状态、哈希同步在可提交的 `data/run_records/`。
- 已完成的输出不覆盖；重跑用新 Run ID。
- 接受响应前 runner 会重校 request 哈希，防止运行中途输入被改。
