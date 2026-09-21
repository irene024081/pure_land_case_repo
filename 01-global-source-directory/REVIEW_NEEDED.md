# REVIEW_NEEDED — 注册表待审核清单

生成日期：2026-09-21。来源：合并 `recovered/` 三份 T01 导出（共 385 条）生成 `source_registry_v1.csv` 时发现的待人工确认事项。**未做任何自动合并**。

## (a) 疑似重复条目（12 组）—— resolved 2026-09-21

负责人已于 2026-09-21 在聊天中确认全部 12 组判断并执行完毕：10 组书籍/杂志合并（字段少的 A 并入字段全的 B）、Purelanders 双登记并入试点 SRC0005、《念佛感应录》系列/单集按父子关系处理不合并。被合并行未删除，`registry_status=merged` 并保留 T01 编号为别名（见 `source_id_map.csv` 的 `merged_into:` 标注）。每组结论：

1. SRC0075 → SRC0304 念佛感应见闻记：same_source，已并入 SRC0304。
2. SRC0076 → SRC0314 菩提树：same_source，已并入 SRC0314。
3. SRC0078 → SRC0313 明伦月刊：same_source，已并入 SRC0313。
4. SRC0079 → SRC0307 近代往生随闻录：same_source，已并入 SRC0307。
5. SRC0080 → SRC0306 现代往生见闻录：same_source，已并入 SRC0306。
6. SRC0082 → SRC0308 e世纪往生传：same_source，已并入 SRC0308。
7. SRC0083 → SRC0309 新世代念佛往生录：same_source，已并入 SRC0309。
8. SRC0084 → SRC0312 莲池海会念佛往生见闻记：same_source，已并入 SRC0312。
9. SRC0086 → SRC0305 念佛感应记（林慈超）：same_source，已并入 SRC0305。
10. SRC0098 → SRC0303 念佛癒病（一）：same_source，已并入 SRC0303。
11. SRC0334 → SRC0005 Purelanders：same_source，已并入试点 SRC0005（试点 ID 保留；SRC0334 的名称与 notes 已由 SRC0005 吸收）。
12. SRC0302《念佛感应录》系列 ↔ SRC0090–SRC0097 单集：父子关系，**不合并**；SRC0302 为系列父条目（parent_of:SRC0090-SRC0097），单集为子条目（child_of:SRC0302），notes 已互相标注。

以下为原始疑似重复清单（存档）：

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

## (b) 与五个 M2 试点来源的映射 —— resolved 2026-09-21

负责人已于 2026-09-21 在聊天中确认：下表五个试点映射全部无误。原表保留如下（存档）：

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

1. ~~**T01 SRC0386 无对照、无法映射**~~ **resolved 2026-09-21**：负责人确认《现代往生录》系列（雪心编辑室／雪心基金会）是独立新来源，已补登记为 repo SRC0386（`source_registry_v1.csv` / `source_id_map.csv` / `MVP_SOURCE_LIST.csv` 三处均已更新）。注意它与 SRC0140 雪心文教基金会网站／雪心助念团数据库的关系（出版物 vs 网站）尚未标注，留待后续审核。
2. **MVP 的 PILOT 标记与现行 M2 试点体系不一致**：MVP 清单标 PILOT 的为 T01 SRC0019（莲池《往生集》→ repo SRC0024）、SRC0133（→ repo SRC0003，与现行试点一致）、SRC0334（Purelanders → repo SRC0334）、SRC0344（《引路宝镜》→ repo SRC0344）。~~其中 T01 SRC0334 正是上文 (a) 中 Purelanders 疑似重复条目……请确认 MVP 清单里的 Purelanders 试点条目应指向哪一个。~~ **resolved 2026-09-21**：负责人确认 MVP 的 Purelanders 试点指向 repo SRC0005；T01 SRC0334 已合并入 SRC0005，`MVP_SOURCE_LIST.csv` 中该行 repo_source_id 已改为 SRC0005 并加注。T01 SRC0019、SRC0344 在现行体系中不是试点（仍待确认是否保留其 T01 时代 PILOT 语义）。
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

## (e) URL 回填记录（2026-09-21）

从 `notes/chatgpt_transcripts/2026-09-15_整理净土资料来源.md` 提取对话中明确写出的来源 URL，回填 `source_registry_v1.csv` 新增的 `url` 列。只回填对话中明确写出的；对应不上注册表条目的不猜。

### 已回填（3 条）

| repo ID | 来源 | URL | 出处 |
|---|---|---|---|
| SRC0177 | 十方圆通寺官方网站 | https://www.around-all-the-world.com/ | 2026-09-15 对话第 159 条消息（url 标记「十方圆通寺官网」） |
| SRC0315 | 「佛教見聞錄」 | https://www.buddhist-experience.org/ | 2026-09-15 对话第 105 条消息（助手纠正正式名称并给出网址）；第 159 条消息再次出现。注意：注册表原名称记的是 buddhist-experience.org.tw，对话给出的是 .org，域名差异待核实 |
| SRC0333 | PureLandBuddhism.org | https://purelandbuddhism.org/ | 2026-09-15 对话第 83 条消息（第九节标题「慧净体系英文官网 PureLandBuddhism.org」，域名明确写出但未给完整 URL 标记） |

### 试点来源：对话中出现了 URL，但 `source_directory_v1.csv` 已有，以该文件为准，未重复回填

- SRC0003（PLBTW）：对话第 83 条消息给出 https://plb.tw/；`source_directory_v1.csv` 已录 https://plb.tw/tc/story_1.aspx。
- SRC0004（PLB-SEA）：对话第 159 条消息给出 https://www.plb-sea.org/dharma/stories；`source_directory_v1.csv` 已录同地址。
- SRC0005（Purelanders）：对话第 83、159 条消息给出 https://purelanders.com/；`source_directory_v1.csv` 已录具体案例页 URL。

### 对话中明确写出 URL、但注册表无对应条目，未回填（4 条）

按规则不猜测归属，登记在此供后续补登记：

| URL | 对话中的来源名 | 出处 | 未回填原因 |
|---|---|---|---|
| https://www.pure-land-buddhism.com/ | Pure Land Buddhism 英文资料站（设 Rebirth Cases 栏目） | 第 83 条消息第十节 | 注册表无对应条目；SRC0159「净宗讲堂 YouTube / Pure Land Buddhism」是 YouTube 频道，不能确认同主体 |
| https://www.duongvecoitinh.com/category/guong-vang-sanh/ | Đường Về Cõi Tịnh：Gương Vãng Sanh（越南，40+ 页往生实例目录） | 第 83 条消息 | 注册表越南条目（SRC0297–0299 等）均为书籍，无此网站 |
| https://www.niemphat.vn/ | Niệm Phật 越南念佛资料站 | 第 83 条消息 | 注册表无对应条目 |
| https://www.amitabha-terre-pure.net/ | Amitabha Terre Pure 法语净土站（设 Anecdotes Véridiques Amitabha 栏目） | 第 83 条消息 | 注册表法语条目 SRC0336 是 jodoshinshu.fr，域名不同，不能合并 |

以上 4 条是 T01 对话讨论过但未进入三份注册表导出的来源，建议补登记（分配新 repo 编号 SRC0387 起），待负责人确认。
