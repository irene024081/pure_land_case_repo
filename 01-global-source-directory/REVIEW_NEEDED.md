# REVIEW_NEEDED — 注册表待审核清单

生成日期：2026-09-21。来源：合并 `recovered/` 三份 T01 导出（共 385 条）生成 `source_registry_v1.csv` 时发现的待人工确认事项。**未做任何自动合并**。

## (a) 疑似重复条目（12 组）

以下条目在 T01 不同对话中被登记了两次（内容指向同一来源）。已各分配独立 repo ID，`source_id_map.csv` 与 `source_registry_v1.csv` 的 note/notes 列已标 `possible_duplicate_of:`，请确认后决定是否合并：

| repo ID A | 名称 A | repo ID B | 名称 B |
|---|---|---|---|
| SRC0075 | 念佛感应见闻记 | SRC0304 | 林看治《念佛感应见闻记》 |
| SRC0076 | 菩提树／Bodhedrum | SRC0314 | 《菩提樹》杂志 |
| SRC0078 | 明伦月刊 | SRC0313 | 《明倫月刊》"念佛往生／助念案例链" |
| SRC0079 | 近代往生随闻录 | SRC0307 | 宽律法师《近代往生随闻录》 |
| SRC0080 | 现代往生见闻录（第一、二集） | SRC0306 | 福建莆田广化寺《现代往生见闻录》一、二集 |
| SRC0082 | e世纪往生传 | SRC0308 | 学谦居士《e世纪往生传》 |
| SRC0083 | 新世代念佛往生录 | SRC0309 | 学谦居士《新世代念佛往生录》 |
| SRC0084 | 莲池海会念佛往生见闻记 | SRC0312 | 《蓮池海會—念佛往生見聞記》 |
| SRC0086 | 念佛感应记（林慈超） | SRC0305 | 林慈超《念佛感应记》 |
| SRC0098 | 念佛癒病（一） | SRC0303 | 《念佛癒病（一）》 |
| SRC0005 | Purelanders.com 现代 testimonials / support-chanting 系列（= T01 SRC0322，试点映射） | SRC0334 | Purelanders.com — Testimonies / PPF Testimonies（= T01 SRC0334） |

另有一组「系列 vs 单集」重叠，不算严格重复但需决定登记粒度：

- SRC0302《念佛感应录》系列（T01 SRC0301）↔ SRC0090–SRC0097《念佛感应录》第一至八集（T01 SRC0086–0093）。T01 先按单集登记、后又登记了整个系列。

## (b) 与五个 M2 试点来源的映射（请确认无误）

| repo ID（现行，不变） | 试点来源 | 匹配到的 T01 条目 | 匹配依据 |
|---|---|---|---|
| SRC0001 | 《净土圣贤录》X1549 | T01 SRC0023 净土圣贤录 | 同名 |
| SRC0002 | 《当代念佛感应集》 | T01 SRC0110 当代念佛感应集 | 同名 |
| SRC0003 | PLBTW／净土宗网站「念佛感应事蹟」 | T01 SRC0133 净土宗官方网站（中华净土宗协会／净土宗文教基金会） | 同为中华净土宗协会官网（plb.tw） |
| SRC0004 | PLB-SEA「念佛真实案例」 | T01 SRC0151 净土宗 Pure Land Buddhism Southeast Asia | 同为 PLB-SEA |
| SRC0005 | Purelanders case accounts | T01 SRC0322 Purelanders.com 现代 testimonials 系列 | 同站；选 SRC0322 而非 SRC0334，因其记录更完整（CP1/AP1、案例编号至 [123] 以上） |

注意：T01 体系中另有多个以 SRC0133 为 parent 的子来源（SRC0161、SRC0162、SRC0184、SRC0185 净宗法师信函／问答／文章栏目），映射后它们与 repo SRC0003 是父子关系而非重复，尚未单独处理。

## (c) 字段异常与数据质量问题

1. **T01 编号冲突**：T01 SRC0001–0005（净土论、瑞应传等古籍）与 repo 试点编号撞号，已改配为 repo SRC0006–SRC0010。引用旧对话记录时务必对照 `source_id_map.csv`。
2. **`cp_current` 大量为空**：T01 SRC0251–0323 文件中约 60 条 `cp_current` 留空（备注称「最终 CP 待逐条冻结，批量降为 CP4–CP5 范围」），`source_registry_v1.csv` 的 `collection_priority` 已回退用 `cp_at_registration` 填入，原值保留在 notes 列。这批日本寺报的 CP 重评从未完成。
3. **`ap_at_selection` 全部为 Unknown**：T01 SRC0324–0385 文件 62 条的 AP 均未评级（AP 列统一为 Unknown）。
4. **file2 的 AP 列部分为空**：SRC0296–0309 等越南／韩国／台湾现代案例集条目未填 AP。
5. **编号无断档、无缺失名称**：385 条 T01 编号 SRC0001–0385 连续完整，每条均有名称。
6. **file1 带 UTF-8 BOM**：`T01_source_registry_selected_SRC0001-SRC0250.csv` 文件头有 BOM，用 Excel 以外的工具读取时需留意（`source_registry_v1.csv` 已无 BOM）。

## (d) MVP 清单（T01_MVP_v1.0_sources.csv）映射问题

`MVP_SOURCE_LIST.csv`（43 条，2026-09-21 由 T01 MVP 清单映射生成）中有以下待确认项：

1. **T01 SRC0386 无对照、无法映射**：《现代往生录》系列（雪心编辑室／雪心基金会），MVP 清单中标 PILOT，但超出已恢复的 385 条范围（T01 编号止于 SRC0385），`source_id_map.csv` 中无记录，`MVP_SOURCE_LIST.csv` 中其 `repo_source_id` 留空。该条疑似与 SRC0140 雪心文教基金会网站／雪心助念团数据库（T01 SRC0138）相关，请确认是同一来源家族还是新来源；若为新来源需补登记并分配 repo 编号。
2. **MVP 的 PILOT 标记与现行 M2 试点体系不一致**：MVP 清单标 PILOT 的为 T01 SRC0019（莲池《往生集》→ repo SRC0024）、SRC0133（→ repo SRC0003，与现行试点一致）、SRC0334（Purelanders → repo SRC0334）、SRC0344（《引路宝镜》→ repo SRC0344）。其中 T01 SRC0334 正是上文 (a) 中 Purelanders 疑似重复条目——现行 repo 试点 SRC0005 映射的是 T01 SRC0322，请确认 MVP 清单里的 Purelanders 试点条目应指向哪一个（疑似 T01 对话当时把重复登记的 SRC0334 当成了正式条目）。T01 SRC0019、SRC0344 在现行体系中不是试点。
3. **BACKUP_PILOT / HOLD_VERIFY**：T01 SRC0110《当代念佛感应集》（→ repo SRC0002，现行试点）在 MVP 中为 BACKUP_PILOT；T01 SRC0004 飞锡《往生净土传》（→ repo SRC0009，佚失书）为 HOLD_VERIFY。
4. MVP 清单的 `current_cp` 与主注册表 CP 评级可能存在差异（MVP 是 T01 后期的重评结果），已按 MVP 文件原样写入 `MVP_SOURCE_LIST.csv` 的 `collection_priority` 列，未与 `source_registry_v1.csv` 对齐。

## 关联但不算重复（供参考，未标 possible_duplicate_of）

- SRC0112 净土（杂志，T01 SRC0108）与试点 SRC0002《当代念佛感应集》：后者是前者的选编索引，属上下游关系。
- SRC0314《菩提樹》杂志是 SRC0304《念佛感应见闻记》的连载首发载体（上下游）。
- SRC0317《慈雲》杂志是 SRC0316《佛菩薩探訪錄》的上游首发载体之一。
- SRC0339 Bom Amigo 是 SRC0338 Revista Coração Confiante 的上游历史刊物。
- SRC0345 Amitabha Path 是 SRC0344《引路宝镜》的英文翻译传播层。
- SRC0113 弘化（现代复刊）与 SRC0063 弘化月刊：同名刊物的不同时期版本。
- SRC0111 狮子吼（台湾复刊）与 SRC0123 狮子吼（槟城本）是不同地区版本。
- 净土圣贤录三编：SRC0001（= T01 SRC0023）、SRC0029（续编）、SRC0060（三编）是三部不同著作。
