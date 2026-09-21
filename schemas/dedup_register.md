# 身份去重 v0.2 / Identity Deduplication v0.2

去重回答“两个候选是否叙述同一个底层事件”。转载、翻译、删节和转述回答“两个来源文本有什么传播关系”；后者记录在 `SOURCE_OCCURRENCE.parent_links`，不能替代身份判断。

Deduplication asks whether two candidates narrate the same underlying episode. Reprint, translation, abridgement, and retelling describe relations between source texts; they belong in `SOURCE_OCCURRENCE.parent_links` and do not replace identity decisions.

## Candidate Comparison

`deduplication.v2` 对每个被检索出的现有 CASE 返回一次比较：

`deduplication.v2` returns one comparison per retrieved existing CASE:

```text
candidate_id
overall_decision: new_case | same_case | possible_same_case | needs_human_review
candidate_matches[]:
  candidate_case_id
  match_decision: same_case | distinct_case | possible_same_case | needs_human_review
  similarities
  differences
  confidence: high | medium | low | unknown
decision_reasons[]
```

`new_case` 只说明在请求明确记录的候选检索范围内没有同案，不证明全球唯一。算法评分只是召回候选，不是同案裁决。人物、地点、时间、家属、目击者、罕见细节、事件顺序和来源链应综合比较；相同瑞相、教理主题或匿名称谓本身不足以合并。

`new_case` means no match within the recorded retrieval scope, not global uniqueness. Retrieval scores only select candidates. Compare person, place, time, family, witnesses, distinctive details, sequence, and source chain. Shared signs, doctrine, or an anonymous label alone cannot justify merging.

## Resolution

`new_case` 且当前 Source Item 没有既有 Case ID 时，Runner 可以在去重后分配新 ID，并把该记录视为待正式提升的 provisional CASE。`same_case`、`possible_same_case`、`needs_human_review`，或当前 Source Item 已有关联 Case ID 时，必须由人工明确决定 `new` 或 `reuse`，写明审核人和理由。AI 不自动合并，也不按候选顺序复用旧 ID。

When the result is `new_case` and the Source Item has no prior Case IDs, the Runner may allocate a new ID after deduplication as a provisional CASE pending canonical promotion. `same_case`, `possible_same_case`, `needs_human_review`, or a Source Item with prior Case IDs requires an explicit human `new` or `reuse` decision with reviewer and reason. AI never merges, and old IDs are not reused by candidate order.

既有 `dedup_groups` 可继续作为人工复核后的关系登记，但 `parallel_version`, `repost_version`, `translation_version` 成员角色须迁移为 Occurrence 传播边。旧 M2A `no_match` 只在 `current_request_only` 范围内有效，不能直接升级为跨库无重复结论。

Existing `dedup_groups` may remain a post-review relation ledger, but `parallel_version`, `repost_version`, and `translation_version` member roles move to Occurrence transmission edges. The M2A `no_match` applies only to `current_request_only` and is not a corpus-wide uniqueness finding.
