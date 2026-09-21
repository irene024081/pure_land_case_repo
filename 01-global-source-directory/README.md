# T01 全球来源目录 / Global Source Directory

目标：建立尽可能完整的全球净土感应来源总目录。

Goal: build the most complete practical directory of global sources for Pure Land accounts.

来源总表记录 Source。每个 Source 的逐篇目录、批处理状态和审核记录保存在 `../data/source_catalogs/{source_id}/`。批量抓取或运行 Pipeline 前，必须先建立并校验该目录。

The global register records Sources. Each Source's item-level inventory, batch status, and review ledger are stored in `../data/source_catalogs/{source_id}/`. The catalog must exist and pass validation before batch capture or Pipeline execution.

## 产出 / Outputs

- `source_register_standard.md`：来源登记标准。 / Source registration standard.
- `source_candidates.md`：待核查来源清单。 / Candidate Sources awaiting verification.
- `source_directory_v1.csv`：结构化来源总表（现行 5 个 M2 试点来源的完整字段表）。 / Structured register of the five locked M2 pilot sources.
- `source_registry_v1.csv`：归一化主注册表（385 条，合并 T01 恢复数据，见下节）。 / Normalized master registry (385 entries merged from recovered T01 exports; see below).
- `source_id_map.csv`：T01 编号 ↔ 现行 repo 编号对照表。 / T01 ↔ repo source ID mapping.
- `REVIEW_NEEDED.md`：待审核清单（疑似重复、试点映射确认、字段异常）。 / Pending human review list.
- `MVP_SOURCE_LIST.csv`：T01 MVP v1.0 精选 43 条的 repo 编号映射版。 / T01 MVP shortlist (43 entries) with repo IDs.
- `recovered/`：T01 对话导出的四份原始注册表（原样归档，勿改）。 / Original T01-exported CSVs, archived as-is.
- `../data/source_catalogs/`：每个来源的文章目录、批处理配置和管理员审核台账。 / Per-Source item catalogs, batch configuration, and administrative review ledgers.
- `../schemas/source_article_catalog.md`：文章目录字段、状态和批处理资格规则。 / Catalog fields, statuses, and batch eligibility rules.

## 注册表现状（2026-09-21）

- **385 条恢复条目已入库**：T01 对话时代的三份注册表导出（SRC0001–0385，无断档）已原样归档至 `recovered/`，并合并为归一化的 `source_registry_v1.csv`（统一 14 列；原文件没有的列留空，CP/AP 评级原样保留，未补全的评级不编造）。
- **编号冲突已解决**：T01 的 SRC0001–0005 是古籍，与现行五个 M2 试点编号撞号。现行 ID 不变（T01 SRC0023/0110/0133/0151/0322 → repo SRC0001–0005），其余 380 条按 T01 编号顺序改配 repo SRC0006–SRC0385。对照关系见 `source_id_map.csv`。
- **未验收**：`source_registry_v1.csv` 尚未经负责人审核。其中 5 条为 `pilot_mapped`、30 条为 `duplicate_review`（疑似重复，含 Purelanders 双登记、《念佛感应录》系列与单集重叠）、其余为 `pending_review`。完整待办见 `REVIEW_NEEDED.md`。
- **注意**：`source_directory_v1.csv`（5 个试点，字段完整）与 `source_registry_v1.csv`（385 条总目，字段较粗）目前并存；前者仍是 M2/M3 运行的权威来源表。
- **MVP 清单已映射**：T01 MVP v1.0 精选 43 条已映射为 repo 编号并生成 `MVP_SOURCE_LIST.csv`；42 条映射成功，1 条（T01 SRC0386《现代往生录》系列／雪心）超出恢复数据范围无法映射，且 MVP 的 PILOT 标记与现行 M2 试点体系不完全一致（详见 `REVIEW_NEEDED.md` 第 (d) 节）。
- **ID 分配规则（2026-09-21 负责人确认）**：今后新登记来源的编号以 `source_registry_v1.csv` 为准接续分配，不另起编号体系；现行试点 SRC0001–0005 永久保留，不随 T01 编号重排。
