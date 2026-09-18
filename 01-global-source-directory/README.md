# T01 全球来源目录 / Global Source Directory

目标：建立尽可能完整的全球净土感应来源总目录。

Goal: build the most complete practical directory of global sources for Pure Land accounts.

来源总表记录 Source。每个 Source 的逐篇目录、批处理状态和审核记录保存在 `../data/source_catalogs/{source_id}/`。批量抓取或运行 Pipeline 前，必须先建立并校验该目录。

The global register records Sources. Each Source's item-level inventory, batch status, and review ledger are stored in `../data/source_catalogs/{source_id}/`. The catalog must exist and pass validation before batch capture or Pipeline execution.

## 产出 / Outputs

- `source_register_standard.md`：来源登记标准。 / Source registration standard.
- `source_candidates.md`：待核查来源清单。 / Candidate Sources awaiting verification.
- `source_directory_v1.csv`：结构化来源总表。 / Structured global Source register.
- `../data/source_catalogs/`：每个来源的文章目录、批处理配置和管理员审核台账。 / Per-Source item catalogs, batch configuration, and administrative review ledgers.
- `../schemas/source_article_catalog.md`：文章目录字段、状态和批处理资格规则。 / Catalog fields, statuses, and batch eligibility rules.
