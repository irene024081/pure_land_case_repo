# Source Adapters And Entry Capture

## Adapter Model

Different Sources need different selectors and boundary rules, but they should reuse adapter families:

```text
inventory: static_headings | sitemap | rss | wordpress_archive | paginated_html | pdf_toc | youtube_playlist | custom
entry: classical_entry | html_article | wordpress_article | pdf_page_range | transcript | custom
```

`data/source_catalogs/{source_id}/source.yml` records the chosen adapters, implementation, refresh policy, rights review, and storage class. Adapter-specific discovery rules live in `inventory.yml` beside it (flat key: value — entry/list URL templates, selectors, key patterns, page limits, scan scope).

## Inventory Discovery

`scripts/inventory_adapters.py` implements the four inventory families; `scripts/run_inventory.py` runs a scan and syncs `articles.csv`:

```bash
python3 scripts/run_inventory.py scan --source-id SRC0003 --dry-run   # diff only
python3 scripts/run_inventory.py scan --source-id SRC0003             # write catalog
```

Sync semantics: known keys keep their rows untouched; new keys are appended as unreviewed rows (rights pending by default); keys missing from a full-scope scan are marked `discovery_status=removed`, never deleted. Discovery is metadata-level and fetches index pages only — it grants no processing or publication rights.

## Lifecycle

Source analysis is versioned setup work. Inventory execution is one-time for fixed sources and recurring for active sources. An adapter must be revalidated when the source layout, edition, or extractor version changes.

## Extractor Output

Every normalized Source Entry records stable source and entry IDs, source-facing key, title, language, exact raw text, hash, locator, extractor name and version, capture date, and boundary status. Extractors preserve evidence; they do not decide truth, publishability, final Case IDs, or creator use.

## Current Implementations

```text
extract_dazhouxian_entries.py  static historical headings
extract_cbeta_xml.py           CBETA TEI P5 XML (head/p structure, nested-entry split)
extract_pdf_entry.py           reviewed PDF page range
extract_plbtw_article.py       PLBTW HTML article
extract_plb_sea_article.py     PLB-SEA article and parallel versions
extract_wordpress_article.py   WordPress-style article
```

Source-specific implementations may later be folded into generic adapters after at least three compatible Sources demonstrate real reuse.

## Verification

```bash
python3 scripts/verify_source_entry_storage.py
python3 scripts/manage_source_catalog.py validate
```
