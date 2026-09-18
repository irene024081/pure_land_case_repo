# Source Article Catalog Schema

Each registered source has one tracked article catalog at:

```text
data/source_catalogs/{source_id}/articles.csv
```

The catalog is the batch queue and administrative review ledger. It records every discovered item, including excluded, duplicate, non-case, failed, and unreviewed items. Source entry files and pipeline run directories do not replace it.

Source-level batch defaults are stored in `source.yml` beside the CSV.

## Source YAML Fields

```text
source_id
catalog_version
catalog_status
inventory_status
inventory_scope
last_inventory_scan_at
inventory_adapter
inventory_refresh_policy
entry_adapter
extractor_name
rights_review_id
storage_class
external_processing_default
```

`catalog_status` describes whether the catalog is operational. `inventory_status` separately describes coverage: `not_started`, `partial`, `complete`, or `needs_refresh`. A valid catalog with one row may still be only a partial inventory.

## CSV Fields

| Field | Required | Purpose |
|---|---:|---|
| `article_id` | Yes | Stable catalog ID, such as `SRC0001-ART000001`. |
| `source_id` | Yes | Parent source ID. Must match the directory and `source.yml`. |
| `source_item_key` | Yes | Stable source-facing key, URL slug, volume-entry key, video ID, or issue-page key. |
| `source_entry_id` | No | Assigned after normalized entry creation. |
| `case_ids` | No | Semicolon-separated case IDs produced from the item. |
| `title` | Yes | Source title without editorial rewriting. |
| `canonical_url` | No | Canonical item URL. Print items use a locator instead. |
| `language` | Yes | Source item language. |
| `published_date` | No | Source publication date when known. |
| `content_type` | Yes | `article`, `book_entry`, `periodical_item`, `video`, `audio`, `letter`, or `other`. |
| `discovery_status` | Yes | Whether the item has been found and cataloged. |
| `selection_status` | Yes | Whether it should enter processing. |
| `rights_review_id` | No | Applicable source-level or item-level rights review. |
| `rights_status` | Yes | Current operational rights result. |
| `capture_status` | Yes | Source capture and integrity state. |
| `boundary_status` | Yes | Article or entry boundary state. |
| `pipeline_status` | Yes | Current end-to-end processing state. |
| `current_stage` | No | Current or next pipeline stage. |
| `last_run_id` | No | Most recent pipeline run. |
| `machine_review_status` | Yes | Latest automated review state. |
| `human_review_status` | Yes | Human review state; may remain `not_reviewed`. |
| `assigned_to` | No | Reviewer or operator. |
| `last_checked_at` | No | Latest catalog verification date. |
| `notes` | No | Exclusion reason, failure detail, duplicate target, or review note. |

## Controlled Values

```text
discovery_status: discovered | metadata_incomplete | inaccessible | removed
selection_status: unreviewed | selected | excluded | deferred
rights_status: pending | public_domain_verified | open_license_verified | permission_obtained | restricted_internal | locator_only | legal_review_required | prohibited | unknown
capture_status: not_started | captured | verified | failed | locator_only
boundary_status: not_started | script_extracted | ai_segmented | machine_checked | human_checked | needs_recheck | rejected
pipeline_status: not_started | ready | running | blocked | completed | failed
machine_review_status: not_reviewed | legacy_machine_checked | passed | failed | needs_revision
human_review_status: not_reviewed | approved | needs_revision | rejected
```

## Batch Eligibility

An article is eligible only when:

1. `selection_status` is `selected`;
2. `capture_status` is `verified`;
3. `pipeline_status` is `ready`;
4. `source_entry_id` exists and matches a retained manifest;
5. `rights_status` is not `prohibited`, `unknown`, or `pending`;
6. external processing is separately allowed before any external adapter receives full text.

Rows are updated in place for operational status. IDs, source keys, URLs, prior run IDs, and reviewer decisions must not be silently replaced; changes belong in version control and review notes.
