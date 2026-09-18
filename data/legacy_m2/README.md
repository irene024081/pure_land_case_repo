# M2 历史试点数据 / Legacy M2 Pilot Data

本目录保留 Pipeline 建立前的案例草稿包。它们是历史审核样本，不是正式数据或导入输入。

This folder preserves pre-Pipeline draft Case Packs. They are historical review fixtures, not canonical data or import inputs.

只有公版 `CASE000001` 草稿包进入 Git。`CASE000002` 至 `CASE000005` 含有受限现代来源材料，保存在 Git 忽略的 `data/source_entries/restricted/legacy_m2/`。

Only the public-domain `CASE000001` pack is tracked. Modern `CASE000002` through `CASE000005` packs remain under ignored `data/source_entries/restricted/legacy_m2/` because they contain restricted source material.

## 默认链条 / Default Chain

```text
来源 / Sources
-> 来源提取脚本 / source extractor scripts
-> Source Entries
-> AI 案例抽取任务 / AI Case extraction job
-> 机器检查 / machine check
-> 案例草稿包 / draft Case Packs
```

## 规则 / Rules

- 案例草稿包是审核材料，不是最终导入文件。 / Draft Case Packs are review materials, not final import files.
- 每个草稿包应包含 M2 必需表的草稿行。 / Each pack should include draft rows for the M2-required tables.
- 必须显示原始证据、读者文本、创作者元数据、去重状态、版权风险和隐私风险。 / Original evidence, reader rendering, creator metadata, dedup status, copyright risk, and privacy risk must remain visible.
- 必须记录来源 URL、定位信息、提取命令或脚本，以及人工判断步骤。 / Each pack must record the source URL, locator, extraction command or script, and manual judgment steps.
- 在存在 Source Entry 时，草稿包应指向一个或多个 `source_entry_id`。 / Each pack should point to one or more `source_entry_id` values when available.
- AI Output 不能替代抽取的原文。 / AI output must not replace raw extracted source text.
- 原始来源载体必须有 Manifest 和已验证哈希；受限现代材料保留在 Git 之外。 / Raw source artifacts require a Manifest and verified hash; restricted modern material stays outside Git.
- 读者文本必须区分压缩草稿和完整证据支持叙事。 / Reader renderings must distinguish condensed drafts from full supported accounts.
- 创作者辅助必须包含绑定证据的阐释角度，不能只有宽泛主题和通用建议。 / Creator assistance must include evidence-linked interpretation angles, not only broad themes and generic usage notes.
- 完成前五个案例后暂停，检查 Schema 和 Workflow，再继续扩展。 / After the first five Cases, pause for Schema and Workflow review before continuing.

## 首轮检查结果 / First Review Outcome

- 增加原文保存模型。 / Added the raw-source retention model.
- 四个现代来源载体移入受限本地存储。 / Moved four modern source artifacts to restricted local storage.
- 增加五个可追踪的 Source Entry Manifest。 / Added five tracked Source Entry Manifests.
- 增加段落级 `source_segments` Schema。 / Added the paragraph-level `source_segments` Schema.
- 为五个案例增加叙事分析。 / Added narrative analysis to all five Cases.
- 为每个案例增加两个阐释角度草稿。 / Added two draft interpretation angles to each Case.
- 将压缩读者文本和创作者摘要标记为需要重新生成。 / Marked condensed reader renderings and creator summaries for regeneration.

## 当前草稿案例 / Current Draft Cases

```text
CASE000001：陈妪随纺车声念佛 / Chen Yu recites Amitabha while spinning thread
CASE000002：阿冬念佛一百天 / A-dong recites Amitabha for one hundred days
CASE000003：家人引导祖母求生净土 / Family guides grandmother to Pure Land
CASE000004：演良循梦中指引前往东林寺 / Yanliang follows dream guidance to Donglin Temple
CASE000005：麦居士引导母亲念佛 / Ms Mak guides her mother with Amitabha recitation
```
