# Source Entry Storage

This directory separates durable source evidence from public case records.

Article discovery, batch selection, pipeline progress, and human review status are tracked in `../source_catalogs/{source_id}/articles.csv`. This storage directory must not be used as an implicit processing queue.

```text
manifests/   tracked storage metadata and integrity information
public/      tracked public-domain or licensed source entries
restricted/  local copyrighted or sensitive source entries, ignored by Git
```

The M2 pilot predates this layout. Its first five source entries have been migrated and hash-verified.

The first five M2 entries now use this pattern:

```text
public historical entry -> tracked normalized JSON
modern entry -> ignored normalized JSON plus ignored source HTML or PDF
all entries -> tracked manifest with text, normalized-file, and source-artifact hashes
```

For online video, retain metadata and a timestamped transcript by default. Retain the media file only when ownership, permission, license, or a documented review basis allows it.

See `../../02-data-model/RAW_SOURCE_STORAGE.md` for storage and rights rules.
