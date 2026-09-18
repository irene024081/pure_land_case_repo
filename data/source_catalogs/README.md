# 来源文章目录 / Source Article Catalogs

每个 `SRC####` 目录包含：

Each `SRC####` directory contains:

```text
source.yml     目录 Adapter、Entry Adapter、刷新、版权和存储默认值
               inventory Adapter, Entry Adapter, refresh, rights, and storage defaults
articles.csv  完整项目目录、处理队列和审核台账
               complete item inventory, processing queue, and review ledger
```

校验所有 Catalog 并输出管理摘要：

Validate all Catalogs and print an administrative summary:

```bash
python3 scripts/manage_source_catalog.py validate
python3 scripts/manage_source_catalog.py status
```

列出一个 Source 中可批量处理的 Article：

List batch-eligible Articles for one Source:

```bash
python3 scripts/manage_source_catalog.py queue --source-id SRC0001
```

Catalog 行属于元数据并进入 Git。受限全文保存在 `data/source_entries/restricted/`。

Catalog rows are metadata and remain tracked. Restricted full text stays under `data/source_entries/restricted/`.

首次目录分析属于版本化配置工作。固定 Source 通常执行一次完整回填；持续更新的 Source 按 `inventory_refresh_policy` 增量刷新。

Initial inventory analysis is versioned setup work. Fixed Sources normally run one full backfill; active Sources continue with incremental refresh according to `inventory_refresh_policy`.
