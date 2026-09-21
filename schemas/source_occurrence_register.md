# 来源出现记录 v0.2 / Source Occurrence Register v0.2

一个 `SOURCE_OCCURRENCE` 表示一个 CASE 在一个 Source Item 的具体位置出现。一个条目可产生零个、一个或多个 CASE，每个独立案例各有出现记录；同一 CASE 出现在书、网站、视频和译文中时也各有记录。

A `SOURCE_OCCURRENCE` is one concrete appearance of one CASE at a location in one Source Item. An item may contain zero, one, or many CASEs, each with a separate Occurrence; repeated appearances of one CASE in books, websites, videos, or translations also receive separate Occurrences.

```text
SOURCE -> SOURCE_ITEM -> SOURCE_ENTRY -> SOURCE_SEGMENT
                                           |
                                           v
                                  SOURCE_OCCURRENCE -> CASE
```

## 字段 / Fields

| 字段 / Field | 作用 / Purpose |
|---|---|
| `occurrence_id` | 出现记录的稳定 ID。 / Stable Occurrence ID. |
| `case_id` | 身份解决后的 CASE ID。 / Resolved CASE ID. |
| `source_id` | 所属集合、书籍、网站或频道。 / Parent collection, book, site, or channel. |
| `source_item_id` | 具体文章、古籍条目、视频或信件；现仍存在于 `articles.csv`。 / Concrete article, book entry, video, or letter, currently inventoried in `articles.csv`. |
| `source_entry_id` | 已保存的规范化证据对象。 / Retained normalized evidence object. |
| `supporting_source_segment_ids` | 本次出现所覆盖的原文分段或时间段。 / Source Segments or timestamp ranges covered by this appearance. |
| `locator` | 卷页、段落、URL 或视频时间码。 / Volume/page, paragraph, URL, or video timestamp. |
| `languages` | 此次出现的语言，可多值。 / Languages of this appearance, possibly multiple. |
| `content_form` | 文本载体中的表达形态，例如传记、投稿、口述或视频片段。 / Presentation form, such as biography, submission, oral account, or video segment. |
| `voice` | 第一人称、第三人称、目击者或转述等叙述声音。 / First-person, third-person, witness, or retelling voice. |
| `parent_links` | 指向更早来源出现的传播边。 / Transmission edges to upstream occurrences. |
| `review_status` | 本出现记录的审核状态。 / Review state of this Occurrence. |

`discovery` 是项目如何找到这条记录的采集历史，保存于 CASE 的 `discovery_occurrence_id` 或后续 ingestion log；它不是 `content_form` 或传播关系。`is_primary_citation` 属于页面展示偏好，不决定最早出处。

`discovery` is project ingestion history, stored through CASE `discovery_occurrence_id` or a later ingestion log; it is neither a content form nor a transmission relation. Preferred display provenance does not decide earliest-known provenance.

## 传播边 / Parent Links

传播关系属于两个 Occurrence 之间的边。关系初版为 `reprint_of`, `translation_of`, `quotation_of`, `abridgement_of`, `edited_from`, `retelling_of`, `oral_recount_of`, `derived_from`, `unknown`。每条边必须有判断依据、支持的 Source Segment IDs 和审核状态。

Transmission is an edge between Occurrences. Initial relations are `reprint_of`, `translation_of`, `quotation_of`, `abridgement_of`, `edited_from`, `retelling_of`, `oral_recount_of`, `derived_from`, and `unknown`. Every edge needs a basis, supporting Source Segment IDs, and review status.

```json
{
  "relation": "oral_recount_of",
  "target": {"state": "unresolved_upstream", "description": "A listener's email mentioned in a teacher's talk; original unavailable"},
  "basis": "source_explicit",
  "supporting_source_segment_ids": ["ENT000042-SEG0007"],
  "review_status": "needs_review"
}
```

`target.state = known` 时必须引用已保存的 `occurrence_id`；`unresolved_upstream` 仅记录来源声称存在但尚未取得的上游材料，不创建虚构 Source。相似文字只能产生调查线索，不能单独建立确定传播边。后续如取得原始材料，应新增真实 Occurrence 并以审核过的新关系替代未解决链接。

For `target.state = known`, reference an existing `occurrence_id`. `unresolved_upstream` records claimed but uncaptured upstream material without inventing a Source. Similar wording alone is a research lead, not a proven transmission edge. Once upstream material is captured, create a real Occurrence and replace the unresolved link through review.

## 权限和 ID / Rights And IDs

Occurrence 的存在不表示可以公开原文。全文、节录、摘要和衍生内容分别受 Rights Review 控制。Pipeline v0.2 用 Source Entry、Candidate ID 和证据 Segment IDs 派生试运行 Occurrence ID；正式提升时必须确认它与既有出现记录不重复，不能仅凭运行 ID 生成新出处。

An Occurrence does not grant permission to display its full source. Full text, excerpts, summaries, and derivatives remain governed by Rights Review. Pipeline v0.2 derives a pilot Occurrence ID from Source Entry, Candidate ID, and evidence Segment IDs; canonical promotion must confirm it does not duplicate an existing appearance.
