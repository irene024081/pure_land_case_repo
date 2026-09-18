# Source Article Catalogs

Each `SRC####` directory contains:

```text
source.yml     inventory adapter, entry adapter, refresh, rights, and storage defaults
articles.csv  complete item inventory, processing queue, and review ledger
```

Validate all catalogs and print an administrative summary:

```bash
python3 scripts/manage_source_catalog.py validate
python3 scripts/manage_source_catalog.py status
```

List batch-eligible articles for one source:

```bash
python3 scripts/manage_source_catalog.py queue --source-id SRC0001
```

Catalog rows are metadata and remain tracked. Restricted full text stays under `data/source_entries/restricted/`.

Initial inventory analysis is versioned setup work. Fixed Sources normally run one full backfill; active Sources continue with incremental refresh according to `inventory_refresh_policy`.
