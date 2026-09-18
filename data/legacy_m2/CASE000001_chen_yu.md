# CASE000001: Chen Yu Recites Amitabha While Spinning Thread

Status: M2 draft, machine checked.

This is a draft case pack for workflow testing. It should not be treated as a final public record until the pilot review confirms field quality.

## Extraction Provenance

```text
source_id: SRC0001
source_entry_id: ENT000001
source_entry_key: SRC0001:卷九:往生女人第九:陈妪:66df9b5e39bc
registered_source_name: 净土圣贤录
exact_text_source_url: https://www.dazhouxian.com/dzz/Html/X78n1549.html
cross_check_source_url: https://deerpark.app/cbeta/X1549/9#h-X1549-009-88
source_work: 卍新续藏第78册 No.1549《净土圣贤录》
source_author: 清 彭希涑述
source_section: 卷九，往生女人第九，陈妪
extraction_method: downloaded the Dazhouxian HTML page, then sliced the entry from heading “陈妪” to the next heading “张寡妇”.
repro_command_1: curl -L -o /private/tmp/X78n1549.html 'https://www.dazhouxian.com/dzz/Html/X78n1549.html'
repro_command_2: python3 scripts/extract_dazhouxian_entry.py --input /private/tmp/X78n1549.html --title 陈妪 --next-title 张寡妇
batch_repro_command: python3 scripts/extract_dazhouxian_entries.py --input /private/tmp/X78n1549.html --source-id SRC0001 --source-title 净土圣贤录 --source-url https://www.dazhouxian.com/dzz/Html/X78n1549.html --volume 卷九 --section 往生女人第九 --start-heading 往生女人第九 --end-heading 往生物类第十
manual_steps: selected this entry as the first SRC0001 pilot case; mapped extracted facts into schema fields; normalized 顺治十年 to 1653; generated faithful reader rendering and summaries; assigned tags and creator metadata.
not_automated: fact extraction, tag assignment, provenance_quality, evidence_level, reader_rendering, creator_metadata.
notes: The script extracts source text only. It does not decide whether the case is true, unique, publishable, or suitable for video.
```

## Source Entry Row

```text
source_entry_id: ENT000001
source_entry_key: SRC0001:卷九:往生女人第九:陈妪:66df9b5e39bc
source_id: SRC0001
parent_entry_id:
source_title: 净土圣贤录
volume: 卷九
section: 往生女人第九
entry_title: 陈妪
entry_sequence: 61
language: zh-Hans
raw_text: 陈妪。常熟人。居于城南。以纺为业。笃信佛法。随纺车声唱阿弥陀佛。终日不绝口。如是三十年。一日忽呼其子谓曰。而不见空中宝盖幡幢乎。吾其逝矣。因拍手大笑。取汤沐浴竟。即合掌化去。事在顺治十年。翁尚书叔元。方微时。闻其事。亲往视之。见妪凝然危坐。室中香气袭人。晚着净土约说。书其事以证焉(净土约说书后)。
raw_text_storage_scope: public
storage_class: tracked_public
storage_uri: data/source_entries/public/ENT000001.normalized.json
normalized_storage_uri: data/source_entries/public/ENT000001.normalized.json
source_artifact_uri:
raw_capture_status: persisted_verified
capture_representation: normalized_entry_json
normalized_artifact_hash: 71eaac499ea2173a5b3f1d349f1af300a5bdf1bba800c3534c51ff64a20c31ef
rights_status: public_domain_verified
raw_text_hash: 66df9b5e39bc63f6a5f3b3c2988ded932de527073fc923e0069c88087a26b72c
source_url: https://www.dazhouxian.com/dzz/Html/X78n1549.html
locator_text: 卍新续藏第78册 No.1549《净土圣贤录》卷九，往生女人第九，陈妪
extraction_method: repeated-title heading segmentation
extractor_name: extract_dazhouxian_entries.py
extractor_version: 0.1.0
extraction_command: python3 scripts/extract_dazhouxian_entries.py --input /private/tmp/X78n1549.html --source-id SRC0001 --source-title 净土圣贤录 --source-url https://www.dazhouxian.com/dzz/Html/X78n1549.html --volume 卷九 --section 往生女人第九 --start-heading 往生女人第九 --end-heading 往生物类第十
captured_at: 2026-09-16
access_date: 2026-09-16
boundary_status: machine_checked
boundary_confidence: high
entry_type: single_case_candidate
ai_case_candidate_count: 1
linked_case_ids: CASE000001
review_status: machine_checked
notes: `source_entry_id` is the pilot registry ID. `entry_sequence` is the order produced by the source-wide extractor within 卷九/往生女人第九.
```

## Case Row

```text
case_id: CASE000001
canonical_title: 陈妪随纺车念佛坐化
primary_language: zh-Hans
period: Qing
event_year: 1653
date_precision: year
region: China; Jiangsu; Changshu
case_types: rebirth_signs; foreknowledge_of_death
key_signs: canopy_and_banners; seated_passing; fragrance
reborn_person_names: 陈妪
witness_names: 翁叔元
related_person_names: 陈妪之子
source_summary: 《净土圣贤录》卷九“往生女人第九”载，陈妪为常熟城南人，以纺织为业，随纺车声称念阿弥陀佛三十年，临终见空中宝盖幡幢，沐浴后合掌坐化，室中有香气。
canonical_summary: 陈妪住在常熟城南，以纺织为业。她长期随纺车声称念阿弥陀佛。顺治十年，她临终前告诉儿子自己见到空中宝盖幡幢，沐浴后合掌坐化。翁叔元听闻后亲往查看，见其端坐，室中有香气。
provenance_quality: P3
evidence_level: medium
privacy_level: public
creator_fit: medium
dedup_status: not_checked
review_status: machine_checked
publish_status: public
notes: Source note cites 《净土约说书后》. Event year is normalized from 顺治十年.
```

## Citation Row

```text
citation_id: CIT000001
case_id: CASE000001
source_id: SRC0001
source_entry_id: ENT000001
citation_role: primary_source
source_title: 净土圣贤录
article_or_segment_title: 陈妪
author_or_speaker: 彭希涑
translator:
publication_date: unknown
date_precision: unknown
volume: 卷九
issue:
page_start:
page_end:
url: https://www.dazhouxian.com/dzz/Html/X78n1549.html
archive_url:
timestamp_start:
timestamp_end:
locator_text: 卍新续藏第78册 No.1549《净土圣贤录》卷九，往生女人第九，陈妪
access_date: 2026-09-16
quote_permission: public_domain
display_policy: public
is_primary_citation: true
provenance_note: 《净土圣贤录》条末注“净土约说书后”，说明此条可能转录自较早来源。Deerpark 对应路径为 https://deerpark.app/cbeta/X1549/9#h-X1549-009-88。
review_status: source_checked
notes: Text was checked against the Dazhouxian CBETA-style full-text page.
```

## Case Text Rows

```text
text_id: TXT000001
case_id: CASE000001
citation_id: CIT000001
text_type: original_excerpt
language: zh-Hans
content: 陈妪。常熟人。居于城南。以纺为业。笃信佛法。随纺车声唱阿弥陀佛。终日不绝口。如是三十年。一日忽呼其子谓曰。而不见空中宝盖幡幢乎。吾其逝矣。因拍手大笑。取汤沐浴竟。即合掌化去。事在顺治十年。翁尚书叔元。方微时。闻其事。亲往视之。见妪凝然危坐。室中香气袭人。晚着净土约说。书其事以证焉。
source_mode: verbatim
created_by: source
generated_from_text_id:
review_status: source_checked
fidelity_status: machine_checked
display_scope: public
publish_status: public
copyright_risk: low
search_weight: high
notes: Parenthetical source note is recorded in citation provenance_note.
```

```text
text_id: TXT000002
case_id: CASE000001
citation_id: CIT000001
text_type: reader_rendering
language: zh-Hans
content_depth: full_supported_account
generation_status: current
content: 陈妪是常熟人，住在城南，以纺织为业。她笃信佛法，常随着纺车的声音称念“阿弥陀佛”，整天不断，持续了三十年。有一天，她忽然叫儿子来说：“你没有看见空中的宝盖和幡幢吗？我大概快要走了。”说完拍手大笑。她取水沐浴之后，合掌坐化。此事发生在顺治十年。翁叔元当时还未显达，听说此事后亲自前去查看，见陈妪端坐不动，屋中香气袭人。他晚年写《净土约说》时，把这件事记录下来作为证明。
source_mode: faithful_rendering
created_by: ai_assisted
generated_from_text_id: TXT000001
review_status: machine_checked
fidelity_status: machine_checked
display_scope: public
publish_status: public
copyright_risk: low
search_weight: high
notes: Rendering keeps the event sequence and does not add facts beyond the source text.
```

```text
text_id: TXT000003
case_id: CASE000001
citation_id: CIT000001
text_type: reader_summary
language: zh-Hans
content: 常熟陈妪以纺织为业，随纺车声念佛三十年。临终前她说见到空中宝盖幡幢，沐浴后合掌坐化。翁叔元后来记下此事，并称亲往查看时见其端坐，室中有香气。
source_mode: summary
created_by: ai_assisted
generated_from_text_id: TXT000001
review_status: machine_checked
fidelity_status: machine_checked
display_scope: public
publish_status: public
copyright_risk: low
search_weight: medium
notes: This row satisfies the M2 short_summary requirement through reader_summary.
```

```text
text_id: TXT000004
case_id: CASE000001
citation_id: CIT000001
text_type: search_digest
language: zh-Hans
content: 常熟，陈妪，纺织，随纺车念阿弥陀佛三十年，顺治十年，宝盖幡幢，沐浴，合掌坐化，翁叔元亲往查看，室中香气，净土约说。
source_mode: summary
created_by: ai_assisted
generated_from_text_id: TXT000001
review_status: machine_checked
fidelity_status: machine_checked
display_scope: public
publish_status: public
copyright_risk: low
search_weight: high
notes: Search-oriented digest for person, place, practice, signs, witness, and source-chain queries.
```

```text
text_id: TXT000005
case_id: CASE000001
citation_id: CIT000001
text_type: creator_summary
language: zh-Hans
content_depth: condensed
generation_status: needs_regeneration
content: 这是一个适合在讲解“日常职业中念佛”“长期相续称名”“临终瑞相”时引用的短案例。它情节很短，更适合作为开示片段或案例合集中的一则，不适合作为单集长视频主线。引用时应说明资料来自《净土圣贤录》，条末另标《净土约说书后》。
source_mode: summary
created_by: ai_assisted
generated_from_text_id: TXT000001
review_status: machine_checked
fidelity_status: machine_checked
display_scope: public
publish_status: public
copyright_risk: low
search_weight: medium
notes: Creator-facing text separates usage advice from evidence.
```

## Narrative Analysis Row

```text
case_id: CASE000001
opening_situation: 陈妪住在常熟城南，以纺织为业，日常生活没有脱离普通劳作环境。
practice_background: 她笃信佛法，随着纺车转动的声音称念阿弥陀佛，终日不断，持续三十年。
central_difficulty: 原文没有记载特殊困难；案例的重点是长期劳作中如何维持称名。
intervention_or_turning_point: 临终当天，她忽然问儿子是否看见空中的宝盖幡幢，并表示自己将要离世。
practice_process: 劳作声成为持续念佛的节奏提示，修行与职业生活相连。
death_or_resolution_sequence: 告知儿子所见 -> 拍手大笑 -> 沐浴 -> 合掌坐化。
reported_signs_by_observer: 宝盖幡幢由陈妪本人报告；端坐与室内香气由翁叔元事后前往查看时记录。
observable_changes: 原文只记载临终动作和死后端坐状态，没有病程或身体变化细节。
aftermath: 翁叔元后来在《净土约说》中记录此事，《净土圣贤录》再行收录。
primary_narrative_arc: 普通劳作中的长期称名 -> 自述临终所见 -> 从容准备 -> 合掌坐化 -> 后人记录。
unresolved_questions: 翁叔元到场与陈妪离世相隔多久不明；《净土约说》原始文本仍需进一步追溯。
supporting_segment_ids: pending_segmentation
review_status: machine_checked
```

## Interpretation Angle Rows

```text
angle_id: ANG000001
case_id: CASE000001
angle_type: practice_guidance
title: 把念佛嵌入重复性的日常劳动
core_claim: 案例最有辨识度的部分不是临终异象，而是陈妪把纺车声变成持续称名的节奏提示，并长期保持。
audience: 在家居士; 工作繁忙者; 普通读者
creator_goal: 说明日常工作与持续念佛可以在具体习惯上结合。
supporting_segment_ids: pending_segmentation
doctrinal_topics: name_recitation; continuity_of_practice
suggested_structure: 从“没有整段空闲时间如何修行”提问 -> 讲纺车声与佛号 -> 强调三十年相续 -> 最后简述临终记录。
required_context: 说明这是清代汇编中的短传记，细节有限。
confidence_basis: 长期随纺车声念佛是原文直接陈述。
boundary_notes: 不能据此承诺某种念佛方法必然产生相同临终现象。
counter_reading: 该记载也可能具有传统往生传的劝信写作目的。
source_method_ids:
generated_by: AI draft
prompt_version: creator_angle_v0.2
review_status: machine_checked
```

```text
angle_id: ANG000002
case_id: CASE000001
angle_type: source_literacy
title: 如何分别理解自述瑞相与他人观察
core_claim: 宝盖幡幢是陈妪临终前的自述，端坐和香气则来自翁叔元的事后观察，创作时应分别归因。
audience: 视频创作者; 研究整理者
creator_goal: 示范瑞相叙述中的报告者区分。
supporting_segment_ids: pending_segmentation
doctrinal_topics: rebirth_signs; source_attribution
suggested_structure: 列出三项记载 -> 标明各自报告者 -> 说明出处链 -> 提醒不把记载升级为独立验证。
required_context: 需要说明《净土圣贤录》引用更早记录。
confidence_basis: 原文明确区分陈妪所说与翁叔元所见。
boundary_notes: 香气与端坐记录不能单独证明往生结论。
counter_reading: 后期汇编可能压缩了原始事件的语境。
source_method_ids:
generated_by: AI draft
prompt_version: creator_angle_v0.2
review_status: machine_checked
```

## Tag Rows

```text
tag_id: TAG0001
tag_type: case_type
slug: rebirth_signs
label: 往生瑞相
original_label:
parent_tag_id:
description: Case includes signs traditionally associated with Pure Land rebirth.
status: active
notes:
```

```text
tag_id: TAG0002
tag_type: case_type
slug: foreknowledge_of_death
label: 预知时至
original_label:
parent_tag_id:
description: Case includes awareness or announcement of approaching death.
status: active
notes:
```

```text
tag_id: TAG0003
tag_type: rebirth_sign
slug: fragrance
label: 异香
original_label: 香气袭人
parent_tag_id:
description: Fragrance appears after or around death.
status: active
notes:
```

```text
tag_id: TAG0004
tag_type: rebirth_sign
slug: seated_passing
label: 坐化
original_label: 合掌化去; 凝然危坐
parent_tag_id:
description: Passing while seated or found seated after passing.
status: active
notes:
```

```text
tag_id: TAG0005
tag_type: rebirth_sign
slug: canopy_and_banners
label: 宝盖幡幢
original_label: 宝盖幡幢
parent_tag_id:
description: Vision of canopy and banners before passing.
status: candidate
notes: Candidate tag added during M2 because this sign is not in the initial rebirth_sign list.
```

```text
tag_id: TAG0006
tag_type: teaching_theme
slug: name_recitation
label: 称名念佛
original_label: 唱阿弥陀佛
parent_tag_id:
description: Case centers on Amitabha name recitation.
status: active
notes:
```

```text
tag_id: TAG0007
tag_type: teaching_theme
slug: ordinary_people_can_practice
label: 平常人也能修
original_label:
parent_tag_id:
description: Case is useful for ordinary lay practice themes.
status: active
notes:
```

## Case Tag Rows

```text
case_id: CASE000001
tag_id: TAG0001
tag_role: primary
confidence: high
notes:
```

```text
case_id: CASE000001
tag_id: TAG0002
tag_role: secondary
confidence: medium
notes: The source phrase “吾其逝矣” suggests awareness of approaching death.
```

```text
case_id: CASE000001
tag_id: TAG0003
tag_role: primary
confidence: high
notes:
```

```text
case_id: CASE000001
tag_id: TAG0004
tag_role: primary
confidence: high
notes:
```

```text
case_id: CASE000001
tag_id: TAG0005
tag_role: secondary
confidence: high
notes: Keep as candidate until repeated use proves product value.
```

```text
case_id: CASE000001
tag_id: TAG0006
tag_role: primary
confidence: high
notes:
```

```text
case_id: CASE000001
tag_id: TAG0007
tag_role: secondary
confidence: medium
notes: Inferred for creator recommendation from occupation and daily practice pattern, not an evidence claim.
```

## Creator Metadata Row

```text
case_id: CASE000001
teaching_themes: name_recitation; ordinary_people_can_practice; preparation_for_death
audience_fit: general_reader; lay_practitioner; dharma_video_creator
video_fit_score: 2
video_fit_level: medium
video_fit_notes: Storyline is clear but very short. It is better as a supporting example than as a standalone video.
best_video_format: lecture_segment
narrative_clarity: high
emotional_accessibility: medium
visualizability: medium
length_fit: low
context_required: medium
source_confidence: medium
emotional_intensity: medium
recommended_usage: Use when explaining daily name recitation, continuity of practice, or traditional rebirth signs. Pair with source citation and avoid expanding scenes not present in the text.
avoid_usage: Do not present the vision, fragrance, or sitting posture as independently verified beyond the cited source. Do not turn the case into a sensational miracle story.
misinterpretation_risk: medium
privacy_risk: low
copyright_risk: low
brief_notes: Good first classical pilot case because the entry has a clear person, place, practice, signs, and source-chain note.
primary_narrative_arc: ordinary work -> thirty years of continuous recitation -> reported vision -> composed preparation -> seated passing -> later record
turning_points: recitation synchronized with spinning; announcement to her son; bathing before death
observable_changes: seated posture after death; fragrance reported by Weng Shuyuan
unresolved_questions: interval before Weng's observation; earliest extant wording in 净土约说
interpretation_angle_ids: ANG000001; ANG000002
review_status: machine_checked
notes: Creator metadata is recommendation metadata, not a truth judgment.
```

## Person Rows

```text
person_id: PER0001
display_name: 陈妪
original_name: 陈妪
name_status: partial
anonymity_level: public
notes: Source gives surname and age descriptor, not a full personal name.
```

```text
person_id: PER0002
display_name: 翁叔元
original_name: 翁尚书叔元
name_status: known
anonymity_level: public
notes: Source says he heard the case, personally inspected, and later wrote it in 《净土约说》.
```

```text
person_id: PER0003
display_name: 陈妪之子
original_name: 其子
name_status: anonymous
anonymity_level: public
notes: Source mentions only “其子”.
```

## Case Person Rows

```text
case_id: CASE000001
person_id: PER0001
person_role: reborn_person
confidence: high
notes:
```

```text
case_id: CASE000001
person_id: PER0002
person_role: witness
confidence: medium
notes: Witnessed the body and fragrance after hearing the event, not necessarily the passing itself.
```

```text
case_id: CASE000001
person_id: PER0002
person_role: recorder
confidence: medium
notes: The case was reportedly recorded in 《净土约说》.
```

```text
case_id: CASE000001
person_id: PER0003
person_role: relative
confidence: high
notes:
```

## Place Rows

```text
place_id: PLC0001
display_name: 常熟
original_name: 常熟
place_type: county
region: Jiangsu
modern_country_or_region: China
confidence: high
notes: Source says “常熟人，居于城南”. Do not infer a more exact modern address.
```

## Case Place Rows

```text
case_id: CASE000001
place_id: PLC0001
place_role: event_place
confidence: medium
notes: The event likely occurred in Changshu city south area, but the exact death place is not separately named.
```

## Dedup Rows

```text
dedup_group_id: DEDUP0001
dedup_status: not_checked
canonical_case_id: CASE000001
duplicate_confidence: unknown
review_status: candidate
notes: First M2 record from SRC0001. No parallel source searched yet beyond the source note.
```

```text
dedup_group_id: DEDUP0001
case_id: CASE000001
member_role: canonical
match_reasons: source entry; person; place; event year; signs
conflict_reasons:
notes:
```

## Pilot Issues Found

```text
1. M2 requires short_summary, but case_text_register currently uses reader_summary. For this draft, TXT000003 uses reader_summary as the short summary row.
2. The initial rebirth_sign taxonomy does not include 宝盖幡幢. This draft adds canopy_and_banners as a candidate tag.
3. 翁叔元 is a post-event witness and recorder, not a direct deathbed witness. Creator and evidence fields should keep that distinction.
4. P3 provenance is appropriate unless 《净土约说书后》 is later checked directly.
```
