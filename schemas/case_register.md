# CASE 登记 v0.2 / CASE Register v0.2

CASE 表示一个底层叙事事件，不表示文章、文本版本或该事件已被证明真实。一个 CASE 可以有多个 `SOURCE_OCCURRENCE`。古代和现代材料共用这一模型。

A CASE identifies one underlying narrated episode, not an article, a text version, or a historically verified event. One CASE may have multiple `SOURCE_OCCURRENCE` records. Ancient and modern material use the same model.

## 核心字段 / Core Fields

| 字段 / Field | 作用 / Purpose |
|---|---|
| `case_id` | 稳定替代 ID；只有身份解决后才能分配。 / Stable surrogate ID assigned only after identity resolution. |
| `record_status` | `active`, `provisional`, `merged`, `retired`。 / Record lifecycle. |
| `canonical_label` | 供人辨认的短标题，不等同于来源标题。 / Short identification label, not the source title. |
| `canonical_record_language` | 标签和管理字段使用的语言，不是事件的语言。 / Language of the canonical record, not of the event. |
| `primary_subject` | 身份状态与显示称谓；可以匿名、部分姓名或未知。 / Identity state and display label, including anonymous, partial, or unknown. |
| `event_time_anchor` | 用于检索和身份判断的时间锚点。 / Time anchor for search and identity comparison. |
| `event_place_anchor` | 用于检索和身份判断的地点锚点。 / Place anchor for search and identity comparison. |
| `discovery_occurrence_id` | 本项目首次发现该 CASE 的已保存出现记录。 / First retained occurrence through which this project discovered the CASE. |
| `earliest_known` | 当前研究范围内最早已取得的出现记录及研究状态。 / Earliest captured occurrence in the current research scope and its research status. |
| `privacy_level` | 公开身份与敏感信息的处理级别。 / Identity and sensitive-data handling level. |
| `review_status` | 机器和人工审核状态。 / Machine and human review status. |

`canonical_label`、时间和地点锚点都是检索用投影；证据仍由 `CASE_FACT -> SOURCE_SEGMENT` 保存。摘要进入 `CASE_TEXT`，人物与地点的细节进入事实和实体关系，瑞相与案例类别进入 Tags，视频适配度进入 Creator Metadata。不要在 CASE 里复制它们的权威值。

The label and time/place anchors are search projections; evidence remains in `CASE_FACT -> SOURCE_SEGMENT`. Summaries belong in `CASE_TEXT`, person and place details in facts and entity links, signs and categories in Tags, and video fit in Creator Metadata. Do not duplicate their authoritative values on CASE.

## 显式状态 / Explicit States

时间、地点与人物身份使用 `known`, `unknown`, `not_applicable`, `withheld`。`unknown` 表示理论上有值但资料不足；`not_applicable` 表示此概念不适用；`withheld` 表示内部已知但按隐私或版权规则不展示。字段仅在 Schema 明确标记可选时允许省略。`null` 不表示 Unknown。

Time, place, and subject identity use `known`, `unknown`, `not_applicable`, or `withheld`. `unknown` means the value could exist but is not established; `not_applicable` means the concept does not apply; `withheld` means it is intentionally hidden. Omission is allowed only for schema-declared optional fields. `null` does not mean Unknown.

已知锚点必须列出支持它的 `case_fact_ids`。模糊时间可以保存范围与精度，例如年号或朝代，不得假装有精确日期。

A known anchor must list supporting `case_fact_ids`. Vague periods may use a range and precision such as reign period or dynasty; do not invent an exact date.

```json
{
  "case_id": "CASE000001",
  "record_status": "provisional",
  "canonical_label": "陈妪随纺车声念佛",
  "canonical_record_language": "zh-Hans",
  "primary_subject": {"state": "known", "display_label": "陈妪", "identity_status": "partial", "case_fact_ids": ["CASE000001-FACT0001"]},
  "event_time_anchor": {"state": "known", "display": "顺治十年", "normalized": {"start": "1653", "end": "1653", "precision": "year"}, "case_fact_ids": ["CASE000001-FACT0015", "CASE000001-FACT0016"]},
  "event_place_anchor": {"state": "known", "display": "常熟", "precision": "county", "case_fact_ids": ["CASE000001-FACT0002"]},
  "discovery_occurrence_id": "OCC23815674AEDE2FED",
  "earliest_known": {"status": "earlier_unresolved", "occurrence_ids": ["OCC23815674AEDE2FED"]},
  "privacy_level": "public",
  "review_status": "machine_checked"
}
```

示例来自 M2A，只用于迁移评审，尚未提升为正式 CASE 数据。完整样例见 `../data/migrations/T02_v0.2_CASE000001.json`。

The example comes from M2A for migration review only; it has not been promoted to a canonical CASE record. See `../data/migrations/T02_v0.2_CASE000001.json`.

## 身份规则 / Identity Rules

- CASE ID 不是内容哈希。相同主题、瑞相或修持方式不能单独证明同案。 / A CASE ID is not a content hash. Shared themes, signs, or practice do not establish identity.
- AI 可以提出候选和比较理由，但不能自动合并或复用已有 CASE ID。 / AI may propose candidates and reasons but cannot merge or reuse an existing CASE ID automatically.
- 歧义案例保留 Candidate ID 并等待人工审核；不得为了继续生成而提前分配 CASE ID。 / Ambiguous episodes retain a Candidate ID pending human review; do not allocate a CASE ID merely to continue generation.
- `earliest_known` 不宣称找到原始见证；页面优先展示哪个出处也由另一套产品规则决定。 / `earliest_known` does not claim an original witness; preferred display provenance is a separate product decision.
