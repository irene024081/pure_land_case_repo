# Source Register Schema

本文件定义 T01「全球净土感应来源总目录」的来源登记标准。

每一个来源记录一行。来源可以是古籍、杂志、书籍、网站、YouTube 频道、寺院、莲社、法师栏目、投稿栏目、数据库、档案馆或公开文献集合。

核心原则：

1. Source 不等于 Case。来源只回答「资料从哪里来」，案例另行建模。
2. 一个 Case 可以对应多个 Source。转载、节录、讲述、翻译都要保留关系。
3. Collection Priority 和 Automation Priority 分开评分。
4. 后期汇编可作为发现入口，但不能自动视为最早出处。
5. 不因版权、格式、语言、自动化难度而排除重要来源。版权和自动化是单独字段。

## Field List

```text
source_id
name
original_name
language
country_or_region
source_type
operator_or_author
institution
tradition_or_lineage
url
access_status
update_status
earliest_year
latest_year
coverage_note
is_pure_land_specific
amitabha_case_density
case_content_types
has_modern_original_cases
modern_original_ratio
historical_reprint_ratio
accepts_submission
has_teacher_listener_letters
has_video
has_audio
has_html_fulltext
has_pdf
has_print_only_material
estimated_case_count
collection_priority
automation_priority
originality_level
provenance_quality
structure_level
copyright_risk
processing_notes
review_status
last_checked_date
notes
```

## Field Definitions

| Field | Required | Value Type | Description |
|---|---:|---|---|
| `source_id` | Yes | ID | Stable ID, format `SRC0001`. Do not reuse after deletion. |
| `name` | Yes | Text | Common Chinese or English display name. |
| `original_name` | No | Text | Original language title, such as Japanese, Korean, Vietnamese, Sanskrit, classical Chinese variant. |
| `language` | Yes | Enum/List | Main language or languages. Use ISO-like names: `zh-Hans`, `zh-Hant`, `ja`, `ko`, `vi`, `en`, `fr`, `es`. |
| `country_or_region` | Yes | Text/List | Main region connected to the source, not necessarily hosting location. |
| `source_type` | Yes | Enum | See `Source Type`. |
| `operator_or_author` | No | Text | Person, compiler, editor, channel owner, teacher, publisher, site maintainer. |
| `institution` | No | Text | Temple, association, publisher, university, archive, platform. |
| `tradition_or_lineage` | No | Text | For example: Chinese Pure Land, Jodo Shu, Jodo Shinshu, Vietnamese Tinh Do, Amitabha Buddhist Society. |
| `url` | No | URL/List | Canonical page if online. For print-only sources, leave blank and explain in `notes`. |
| `access_status` | Yes | Enum | See `Access Status`. |
| `update_status` | Yes | Enum | See `Update Status`. |
| `earliest_year` | No | Year | Earliest known publication, archive, article, issue, video, or text date. |
| `latest_year` | No | Year | Latest known publication, archive, article, issue, video, or text date. |
| `coverage_note` | No | Text | Known gaps, issue range, volume range, archive scope. |
| `is_pure_land_specific` | Yes | Boolean/Unknown | Whether the source is primarily Pure Land. |
| `amitabha_case_density` | Yes | Enum | See `Amitabha Case Density`. |
| `case_content_types` | No | List | See `Case Content Types`. |
| `has_modern_original_cases` | Yes | Boolean/Unknown | Whether it contains modern first-hand or near first-hand cases. |
| `modern_original_ratio` | No | Enum | Estimated proportion of modern original cases. |
| `historical_reprint_ratio` | No | Enum | Estimated proportion of copied or retold historical materials. |
| `accepts_submission` | No | Boolean/Unknown | Whether it accepts reader letters, layperson submissions, help requests, reports. |
| `has_teacher_listener_letters` | No | Boolean/Unknown | Whether cases appear in teacher replies, call-ins, email answers, Q&A. |
| `has_video` | No | Boolean/Unknown | Whether video materials exist. |
| `has_audio` | No | Boolean/Unknown | Whether audio materials exist. |
| `has_html_fulltext` | No | Boolean/Unknown | Whether full text is available as HTML. |
| `has_pdf` | No | Boolean/Unknown | Whether PDF scans or born-digital PDFs exist. |
| `has_print_only_material` | No | Boolean/Unknown | Whether some materials are print-only or offline. |
| `estimated_case_count` | No | Range | Estimated number of relevant cases, such as `1-10`, `10-100`, `100-1000`, `1000+`. |
| `collection_priority` | Yes | Enum | See `Collection Priority`. |
| `automation_priority` | Yes | Enum | See `Automation Priority`. |
| `originality_level` | Yes | Enum | See `Originality Level`. |
| `provenance_quality` | Yes | Enum | See `Provenance Quality`. |
| `structure_level` | Yes | Enum | See `Structure Level`. |
| `copyright_risk` | Yes | Enum | See `Copyright Risk`. |
| `processing_notes` | No | Text | How to process later: OCR, manual table of contents, YouTube API, PDF split, web crawl. |
| `review_status` | Yes | Enum | See `Review Status`. |
| `last_checked_date` | No | Date | Format `YYYY-MM-DD`. |
| `notes` | No | Text | Evidence, caveats, known duplicates, source chain hints. |

## Source Type

| Value | Meaning |
|---|---|
| `canonical_text` | Canonical Buddhist text or major premodern collection. |
| `ancient_compilation` | Premodern compilation, anthology, wangsheng zhuan, temple record, gazetteer. |
| `modern_book` | Modern book or edited volume. |
| `periodical` | Magazine, journal, temple periodical, newsletter. |
| `website` | Website with articles or archives. |
| `article_column` | Specific website or magazine column. |
| `youtube_channel` | YouTube channel. |
| `video_playlist` | Playlist or video series. |
| `teacher_qa` | Teacher Q&A, letters, replies, call-ins. |
| `temple_or_association` | Temple, lotus society, Buddhist association as an institutional source. |
| `database_or_archive` | Text database, archive, catalog, OCR corpus. |
| `social_media` | Facebook, WeChat public account, X, forum, blog platform. |
| `other` | Use only when no existing type fits. Explain in `notes`. |

## Access Status

| Value | Meaning |
|---|---|
| `online_open` | Publicly accessible online. |
| `online_restricted` | Online but login, subscription, region, or account needed. |
| `partial_online` | Some volumes/pages online, some missing. |
| `offline_known` | Known source, offline or print-only. |
| `not_found` | Mentioned by other sources, not yet located. |
| `dead_link` | URL known but currently unavailable. |
| `unknown` | Not checked yet. |

## Update Status

| Value | Meaning |
|---|---|
| `active` | Still publishing or updating. |
| `inactive` | No longer updating, archive remains. |
| `completed` | Fixed historical collection or completed publication series. |
| `irregular` | Updates occasionally or unpredictably. |
| `unknown` | Not checked yet. |

## Amitabha Case Density

| Value | Meaning |
|---|---|
| `high` | Relevant cases are a major recurring content type. |
| `medium` | Relevant cases appear regularly but are not the main content. |
| `low` | Relevant cases appear occasionally. |
| `unknown` | Not enough evidence yet. |

## Case Content Types

Use one or more values:

```text
rebirth_signs
foreknowledge_of_death
seeing_amitabha_or_pure_land
dream_or_vision
fragrance_light_music
body_softness
relics
illness_recovery
disaster_escape
assisted_chanting
dedication_or_transfer
ghost_spirit_related
animal_rebirth
other_worldly_benefit
doctrinal_or_historical_only
unknown
```

## Ratio Fields

Use these values for `modern_original_ratio` and `historical_reprint_ratio`:

| Value | Meaning |
|---|---|
| `none` | None observed. |
| `low` | Less than about 25%. |
| `medium` | About 25%-60%. |
| `high` | More than about 60%. |
| `unknown` | Not enough evidence. |

## Collection Priority

回答：为了做到详尽，这个来源是否必须收录。

| Value | Meaning | Typical Examples |
|---|---|---|
| `S` | 必收。核心来源，必须完整覆盖。 | 《净土》、核心往生传、净土宗双月刊、高密度原创案例库。 |
| `A` | 高优先级。应系统覆盖。 | 重要寺院网站、法师来信栏目、地区性净土刊物。 |
| `B` | 有价值。条件允许时覆盖。 | 低密度佛教综合网站、零散博客、辅助档案。 |
| `C` | 辅助来源。主要用于线索、交叉验证或补充。 | 搜索入口、书目页、百科页、转载页。 |

## Automation Priority

回答：这个来源是否适合自动化监控或批量处理。

| Value | Meaning | Typical Processing |
|---|---|---|
| `A1` | 高适配。独立网页、结构清晰、持续更新。 | Scheduled crawl, RSS, sitemap, API. |
| `A2` | 可自动化。需要分页、栏目解析或轻量清洗。 | Custom scraper, URL pattern extraction. |
| `B1` | 可批处理。PDF、期刊、合集，需要分篇提取。 | PDF download, OCR, table of contents parsing. |
| `B2` | 半自动。版式复杂或来源分散，需要人工抽查。 | Manual sampling plus assisted extraction. |
| `C` | 低频检查。古籍、固定档案、更新极少。 | Quarterly or one-time catalog review. |

## Originality Level

| Value | Meaning |
|---|---|
| `O1` | First-hand or near first-hand: author, family, witness, helper, direct letter. |
| `O2` | Edited from submitted or recorded material, with identifiable source. |
| `O3` | Historical compilation with citations or source clues. |
| `O4` | Retelling, lecture story, repost, translation, source unclear. |
| `unknown` | Not enough evidence. |

## Provenance Quality

| Value | Meaning |
|---|---|
| `P1` | 当事人、亲属、在场者、原始记录。 |
| `P2` | 同时代或近时代记录，注明消息来源。 |
| `P3` | 后期汇编，保留出处线索。 |
| `P4` | 现代转述、讲述、转载，出处不完整。 |
| `unknown` | Not enough evidence. |

## Structure Level

| Value | Meaning |
|---|---|
| `R1` | Highly structured: database, table, clear metadata, stable IDs. |
| `R2` | Structured pages: titles, dates, categories, pagination. |
| `R3` | Semi-structured: PDFs, magazines, scans, playlists. |
| `R4` | Unstructured: long videos, scattered posts, mixed archives. |
| `unknown` | Not enough evidence. |

## Copyright Risk

| Value | Meaning |
|---|---|
| `low` | Public domain, canonical text, open license, or clearly reusable metadata only. |
| `medium` | Public webpage or article where summary and citation are likely acceptable, but full reuse should be limited. |
| `high` | Modern books, magazines, paid content, scans, unclear rights, or full-text republication risk. |
| `unknown` | Not assessed. |

## Review Status

| Value | Meaning |
|---|---|
| `candidate` | Added as a lead, not verified. |
| `verified_source` | Source identity and access checked. |
| `sampled` | Sample content checked for case density and originality. |
| `ready_for_extraction` | Ready to extract Case records. |
| `extracted` | Cases have been extracted. |
| `needs_recheck` | Conflicting data, dead links, missing years, or uncertain attribution. |

## Inclusion Standard

纳入来源总目录的最低标准：

1. 和阿弥陀佛、净土、念佛、往生、助念、回向、净土宗信仰实践有明确关系。
2. 能作为案例来源、案例线索、出处追踪线索、版本底本、书目依据或机构入口。
3. 至少能记录一个可核查字段：名称、URL、书名、机构、作者、刊物、频道、馆藏或被引用出处。

不排除以下来源：

1. 自动化难度高的 PDF、扫描件、纸本。
2. 版权风险高但可作为索引或元数据记录的来源。
3. 非中文来源。
4. 转载来源。转载来源仍可用于发现案例和追踪传播链。
5. 低密度综合佛教来源。低密度只影响优先级，不影响是否可登记。

## Source ID Rules

```text
SRC0001
SRC0002
SRC0003
```

规则：

1. `source_id` 永久稳定。
2. 删除来源时不要复用 ID。可将 `review_status` 标为 `needs_recheck` 或在 `notes` 说明作废原因。
3. 同一实体的不同层级可以分开建源。例如「东林寺」是机构源，《净土》是 periodical，某个栏目是 article_column。
4. 同一本书的不同在线底本通常不要拆成不同 Source，除非版本差异本身有研究价值。在线底本可放入 `url` 或后续 `source_versions` 表。

## Recording Template

```csv
source_id,name,original_name,language,country_or_region,source_type,operator_or_author,institution,tradition_or_lineage,url,access_status,update_status,earliest_year,latest_year,coverage_note,is_pure_land_specific,amitabha_case_density,case_content_types,has_modern_original_cases,modern_original_ratio,historical_reprint_ratio,accepts_submission,has_teacher_listener_letters,has_video,has_audio,has_html_fulltext,has_pdf,has_print_only_material,estimated_case_count,collection_priority,automation_priority,originality_level,provenance_quality,structure_level,copyright_risk,processing_notes,review_status,last_checked_date,notes
```

Canonical rows live only in `../01-global-source-directory/source_directory_v1.csv`; examples are not duplicated here because stable IDs must never conflict with real records.

Operational rights status is not duplicated in the global discovery table. It lives in `data/source_catalogs/{source_id}/source.yml` and the referenced `data/rights_reviews/{rights_review_id}.yml`.
