# Source Entry 存储 / Source Entry Storage

本目录将长期保存的来源证据与公开案例记录分开。

This directory separates durable source evidence from public Case records.

Article 发现、批量选择、Pipeline 进度和人工审核状态记录在 `../source_catalogs/{source_id}/articles.csv`。本目录不能作为隐含处理队列。

Article discovery, batch selection, Pipeline progress, and human review status are tracked in `../source_catalogs/{source_id}/articles.csv`. This storage directory must not be used as an implicit processing queue.

```text
manifests/   进入 Git 的存储元数据与完整性信息 / tracked storage metadata and integrity information
public/      进入 Git 的公版或已许可 Source Entries / tracked public-domain or licensed Source Entries
restricted/  Git 忽略的本地版权或敏感 Source Entries / local copyrighted or sensitive Source Entries, ignored by Git
```

M2 试点早于这一目录结构。前五个 Source Entry 已迁移并完成哈希校验。

The M2 pilot predates this layout. Its first five Source Entries have been migrated and hash-verified.

前五个 M2 条目现在使用以下模式：

The first five M2 entries now use this pattern:

```text
公版历史条目 / public historical entry -> 进入 Git 的规范化 JSON / tracked normalized JSON
现代条目 / modern entry -> Git 忽略的规范化 JSON 与来源 HTML 或 PDF / ignored normalized JSON plus ignored source HTML or PDF
全部条目 / all entries -> 包含正文、规范化文件和来源载体哈希的 Manifest / tracked Manifest with text, normalized-file, and source-artifact hashes
```

在线视频默认保存元数据和带时间码的 Transcript。只有在所有权、许可、License 或书面审核依据允许时，才保存媒体文件。

For online video, retain metadata and a timestamped Transcript by default. Retain the media file only when ownership, permission, License, or a documented review basis allows it.

存储和版权规则见 `../../02-data-model/RAW_SOURCE_STORAGE.md`。

See `../../02-data-model/RAW_SOURCE_STORAGE.md` for storage and rights rules.
