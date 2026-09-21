# T02 v0.2 Migration / T02 v0.2 迁移

T02 v0.2 区分事件身份 (`CASE`)、某个来源中出现的事件 (`SOURCE_OCCURRENCE`) 与来源文本之间的传播关系。`SOURCE_ITEM` 是文章、书中条目、视频或来信等逻辑对象；当前 `articles.csv.article_id` 是它的物理字段名，本次不改 CSV 列名。

T02 v0.2 separates event identity (`CASE`), a concrete appearance in a source (`SOURCE_OCCURRENCE`), and transmission between source appearances. `SOURCE_ITEM` is the logical name for an article, book entry, video, or letter; `articles.csv.article_id` remains its physical field name in this release.

## Authority And Compatibility / 权威版本与兼容

- `../pipeline/pipeline.v2.json` defines new Pipeline `0.2.0` Runs. Existing `0.1.0`-`0.1.2` definitions, contracts, prompts, and baseline hashes remain unchanged. / 新 Run 使用 v0.2.0；旧版本和 baseline 哈希不变。
- `data/baselines/M2A_ENT000001_P011.json` remains the accepted historical v0.1.1 baseline. `../data/migrations/T02_v0.2_CASE000001.json` is a proposed mapping for review, not a promoted canonical record. / M2A 旧 baseline 保留；迁移样例仅供审核。
- New Case Runs are created under `candidates/{candidate_id}`. Case IDs are assigned after deduplication and recorded by `case_resolution`; old `cases/{case_id}` paths remain readable. / 新 Run 先使用 Candidate ID；旧路径仍可读取。
- The runner does not yet write a canonical `CASE` or `SOURCE_OCCURRENCE` store. M2D must implement idempotent promotion, migration validation, and collision checks. / Runner 尚未生成正式库；M2D 负责提升。

## CASE Field Mapping / 案例字段映射

| Old field / 旧字段 | v0.2 destination / 去向 | Rule / 规则 |
|---|---|---|
| `case_id` | `CASE.case_id` | Assign only after identity resolution. / 身份解决后分配。 |
| `canonical_title` | `CASE.canonical_label` | Human label, not an authoritative source title. / 仅作识别标签。 |
| `primary_language` | `CASE.canonical_record_language` | Language of the record, not event or source language. / 登记语言。 |
| `reborn_person_names`, `witness_names`, `related_person_names` | `CASE_FACT`, entity links, `CASE.primary_subject` | Keep each person's role and evidence; unknown names stay unknown. / 保留角色和证据。 |
| `period`, `event_year`, `date_precision` | `CASE.event_time_anchor` and `CASE_FACT` | Anchor must cite facts; retain ranges and uncertainty. / 时间锚点引用事实。 |
| `region` | `CASE.event_place_anchor` and `CASE_FACT` | Preserve source wording and location precision. / 保留原称和精度。 |
| `case_types`, `key_signs` | Tags | Do not duplicate authoritative tag lists in CASE. / 不在 CASE 复制标签。 |
| `source_summary`, `canonical_summary` | `CASE_TEXT` | Version and rights-check each text. / 摘要分别版本化及审核。 |
| `provenance_quality`, `evidence_level` | Research/evidence metadata | Do not imply historical truth from source count. / 不把来源数量当真实性。 |
| `privacy_level`, `review_status` | `CASE` | Retain explicit review scope. / 保留审核范围。 |
| `creator_fit` | Creator Metadata | Keep creator judgments separate from event identity. / 创作评价与身份分离。 |
| `dedup_status` | Identity decision ledger | Do not store a stale decision on CASE. / 不保留易过期副本。 |
| `publish_status` | Publication package | Gate each public output separately. / 按输出审核。 |
| `notes` | Research note with provenance | Classify before migration; do not silently discard. / 先分类再迁移。 |

## Citation And Transmission Mapping / 引用与传播映射

| Old field / 旧字段 | v0.2 destination / 去向 |
|---|---|
| `citation_id` | Migration alias to `occurrence_id`; do not renumber historical references without a map. / 旧 ID 保留映射。 |
| `case_id`, `source_id`, `source_entry_id` | `SOURCE_OCCURRENCE` foreign keys. / 出现记录外键。 |
| `article_or_segment_title`, `translator`, `editor`, `publication_year`, `language` | Source Item metadata or occurrence-specific language/form. / 来源项目元数据或出现属性。 |
| `volume`, `page`, `timestamp`, `url`, `locator_text` | `SOURCE_OCCURRENCE.locator`; retain exact source keys. / 出现位置。 |
| `citation_role` | Split into project discovery, display preference, and `parent_links`. / 分离发现、展示和传播。 |
| `is_primary_citation` | Display preference only; not earliest-source evidence. / 仅展示偏好。 |
| `provenance_note` | Research note plus supported `parent_links`. / 研究备注和有证据的传播边。 |
| `quote_permission`, `display_policy` | Rights Review and output gate. / 版权审核。 |

Old dedup roles such as `parallel_version`, `repost_version`, and `translation_version` are not identity outcomes. Migrate supported relations to `SOURCE_OCCURRENCE.parent_links`; keep unresolved claims as `unresolved_upstream`. `same_case`, `possible_same_case`, and `distinct_case` remain separate identity decisions. / 旧去重角色中的平行版、转载、译本归传播关系；同案判断单独记录。

## Explicit Unknown / 显式未知

For subject, time, and place use `known`, `unknown`, `not_applicable`, or `withheld`. Omission and `null` are not synonyms for unknown. A known anchor must cite the fact IDs supporting it. An upstream work mentioned in a source but not yet captured is `unresolved_upstream`, not a fabricated `SOURCE_OCCURRENCE`. / 人物、时间、地点采用显式状态。被提及却未取得的上游文献标记为未解决，不创建虚构记录。

## Acceptance Before M2D / 正式提升前验收

1. Recheck Candidate-to-Case decisions against a corpus index and record the retrieval scope; `new_case` is not a global uniqueness proof. / 复核候选身份和检索范围。
2. Verify every migrated anchor, fact, and transmission edge against retained segments. / 核对锚点、事实、传播边的证据。
3. Resolve historical citation aliases and prevent duplicate Occurrences across reruns. / 处理旧 ID 与重复出现。
4. Keep rights and publication decisions per output; a retained Occurrence does not grant public-text rights. / 每种公开输出独立审核版权。
5. Promote only passed, non-superseded Runs with an idempotent command and a reviewable diff. / 只提升通过且未被取代的 Run。
