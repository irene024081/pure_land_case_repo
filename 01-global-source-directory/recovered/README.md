# recovered/ — T01 对话时代来源注册表原件

本目录保存从 ChatGPT T01 系列对话导出的四份原始来源注册表 CSV，**原样归档、未做任何修改**（找回日期：2026-09-21）。它们是历史证据，请勿编辑；日常使用请以上一级目录的 `source_registry_v1.csv` 和 `source_id_map.csv` 为准。

## 文件清单与列含义

### `T01_source_registry_selected_SRC0001-SRC0250.csv`（250 条）

T01-2 各 Part（中国古代文献、民国期刊、战后港台纸本、中文网站、YouTube、日本来源）正式入选清单。

| 列 | 含义 |
|---|---|
| `source_id` | T01 编号（SRC0001–SRC0250） |
| `source_name` | 来源名称 |
| `t01_section` | T01 对话内的分节（如「T01-2 Part 1｜中国古代文献来源池」） |
| `selection_status` | 选择状态（全部为 FORMAL_SELECTED） |
| `special_note` | 特殊备注（如「佚失」「parent=SRC0159」），多为空 |

注意：本文件带 UTF-8 BOM。

### `T01_sources_selected_in_this_conversation_SRC0251-SRC0323.csv`（73 条）

T01 后续对话入选来源（日本地方寺报、日本/越南/韩国 CORE 来源、台湾现代案例集等）。

| 列 | 含义 |
|---|---|
| `source_id` | T01 编号（SRC0251–SRC0323） |
| `source_name` | 来源名称 |
| `region` | 地区 |
| `tradition_or_context` | 宗派／语境 |
| `source_type` | 来源类型 |
| `current_role` | 角色（CORE / DISCOVERY / INFRASTRUCTURE 等） |
| `cp_at_registration` | 登记时的收集优先级（Collection Priority） |
| `cp_current` | 当前收集优先级（部分为空，表示尚未重评） |
| `ap` | 自动化优先级（Automation Priority；部分为空） |
| `date_or_range` | 年代或起止范围 |
| `key_note` | 关键备注 |
| `registry_status` | 登记状态（全部为 REGISTERED） |

### `T01_sources_selected_in_this_conversation_SRC0324_SRC0385.csv`（62 条）

T01 后期对话入选来源（欧美、藏区、俄语圈、拉美等多语来源），冻结状态导出。

| 列 | 含义 |
|---|---|
| `src_id` | T01 编号（SRC0324–SRC0385） |
| `source_name` | 来源名称 |
| `role` | 角色（CORE / DISCOVERY / INFRASTRUCTURE 及组合） |
| `cp_at_selection` | 选择时的收集优先级 |
| `ap_at_selection` | 选择时的自动化优先级（本文件全部为 Unknown） |
| `region` | 地区 |
| `language` | 语言 |
| `notes` | 备注 |
| `selection_status` | 选择状态（全部为 FROZEN） |

### `T01_MVP_v1.0_sources.csv`（43 条）

T01 对话后期整理的 MVP 精选来源清单（v1.0），即从总池中挑出的优先落地批次。

| 列 | 含义 |
|---|---|
| `source_id` | T01 编号（注意：含一条 SRC0386，超出前三份文件的 SRC0001–0385 范围） |
| `source_name` | 来源名称 |
| `current_cp` | 当时的收集优先级重评结果（可能与主注册表 CP 不一致） |
| `recommended_phase` | 建议落地阶段（P1 / P2 / P1/P2） |
| `pilot_status` | 试点标记（PILOT / BACKUP_PILOT / HOLD_VERIFY / 空）；注意这是 T01 时代的试点计划，与现行 M2 试点体系不完全一致 |

映射为 repo 编号后的版本见 `../MVP_SOURCE_LIST.csv`。

## ⚠️ 编号冲突警告

这些文件使用 T01 对话的编号体系，其中 **T01 SRC0001–0005 是古籍**（净土论、瑞应传等）。但仓库现行运行体系中 **SRC0001–0005 是五个 M2 试点来源**（净土圣贤录、当代念佛感应集、PLBTW、PLB-SEA、Purelanders），已有 Pipeline Run、Manifest 和版权审核挂在这些 ID 上。

**引用任何 SRC 编号时必须先确认语境**（T01 编号 vs repo 编号）。对照关系见 `../source_id_map.csv`：

- T01 SRC0023（净土圣贤录）= repo SRC0001
- T01 SRC0110（当代念佛感应集）= repo SRC0002
- T01 SRC0133（净土宗官方网站／中华净土宗协会）= repo SRC0003（PLBTW）
- T01 SRC0151（Pure Land Buddhism Southeast Asia）= repo SRC0004（PLB-SEA）
- T01 SRC0322（Purelanders）= repo SRC0005
- 其余 T01 条目按 T01 编号顺序改配 repo SRC0006–SRC0385。
