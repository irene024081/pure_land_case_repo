# Seed Dataset Plan

Seed dataset 是产品和数据流程的验证集，不是完整资料库的开始冲量。

目标是用 50-100 个高质量案例验证四件事：

1. 普通读者能搜索、阅读、核对出处。
2. 法师能按主题获得案例推荐。
3. 创作者能把案例加入选题篮并生成 creator brief。
4. 研究者能检查来源、出处链、文本版本和去重状态。

## Scope

第一批数据建议来自 3-5 类来源，覆盖不同文本形态。

| Source group | Target count | Why included |
|---|---:|---|
| 古代公版来源 | 10-20 cases | 验证文言原文、白话译述、古代出处链。 |
| 现代期刊或书籍 | 15-25 cases | 验证版权限制、现代纪实、期号页码、摘要展示。 |
| 现代中文网站 | 15-25 cases | 验证网页抽取、转载追源、HTML 来源展示。 |
| YouTube 或法师来信 | 5-15 cases | 验证口述整理、时间戳、第一人称和 creator fit。 |
| 多语言来源 | 3-5 cases | 验证翻译字段和未来多语言展示，不作为第一批主量。 |

总量目标：

```text
minimum: 50 reviewed cases
target: 80 reviewed cases
upper bound: 100 reviewed cases
```

超过 100 条之前，先完成检索、推荐、详情页和 creator brief 验收。

## Candidate Source Mix

### Ancient Public-domain Source

候选：

```text
《净土圣贤录》
《往生集》
《净土往生传》
```

优先选标准：

```text
online text available
case boundaries clear
public display allowed
contains common rebirth signs
```

### Modern Periodical Or Book

候选：

```text
庐山东林寺《净土》
《当代念佛感应集》
《净土宗双月刊》
```

优先选标准：

```text
source citation clear
modern case density high
contains names, places, dates, witnesses
copyright handling can be tested
```

### Modern Chinese Website

候选：

```text
PLBTW
PLB-SEA
佛教见闻录
东林寺网站
```

优先选标准：

```text
HTML text accessible
article pages stable
case titles and dates visible
repost/provenance questions present
```

### Video Or Teacher Letter Source

候选：

```text
法师来信案例
YouTube subtitle/transcript source
teacher Q&A case material
```

优先选标准：

```text
timestamp can be recorded
oral cleanup is needed
case is useful for creator workflow
source confidence can be assessed
```

### Multilingual Source

候选：

```text
English Pure Land case source
Japanese wangsheng source
Vietnamese niệm Phật source
```

优先选标准：

```text
small sample only
translation workflow can be tested
original language text retained
```

## Case Type Coverage

Seed dataset should deliberately cover common search and recommendation themes.

```text
rebirth_signs
foreknowledge_of_death
seeing_amitabha_or_pure_land
dream_or_vision
fragrance_light_music
body_softness
assisted_chanting
illness_recovery
disaster_escape
dedication_or_transfer
animal_rebirth
```

Minimum coverage:

```text
at least 8 case types
at least 5 source types
at least 3 time periods
at least 3 regions
at least 10 cases with strong creator fit
at least 10 cases with weak or difficult fit for comparison
```

## Required Fields Per Case

Each seed case must have:

```text
case_id
canonical_title
short_summary
canonical_summary
reader_rendering
original_evidence or evidence_locator
source_citation
source_id
case_types
key_signs
period
region
provenance_quality
evidence_level
copyright_risk
privacy_risk
review_status
```

For creator workflow, each seed case should also have:

```text
creator_summary
teaching_themes
recommended_usage
avoid_usage
video_fit_level
video_fit_notes
best_video_format
narrative_clarity
emotional_accessibility
visualizability
length_fit
context_required
source_confidence
misinterpretation_risk
```

## Acceptance Tests

The seed dataset is successful when these checks pass:

```text
search "异香" returns relevant cases with highlighted snippets
search by reborn person name returns the correct case
search by source returns cases under that source
case detail shows reader rendering and original evidence locator
case detail distinguishes original evidence from AI-assisted rendering
theme "临终助念" returns at least 5 usable recommendations
creator can select 3 cases and generate a creator brief
research view shows citation and provenance status
duplicate or reposted cases are not shown as separate canonical cases
```

## Non Goals

Do not use seed dataset to maximize total case count.

Do not import unreviewed cases directly into public pages.

Do not solve all global source coverage before website MVP.

Do not display modern copyrighted full text publicly unless rights are clear.
