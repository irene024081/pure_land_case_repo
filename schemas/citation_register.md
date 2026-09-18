# Citation Register Schema

`citations` records where a case appears inside a source.

One case can have many citations. One source can contain many citations.

## Core Fields

```text
citation_id
case_id
source_id
source_entry_id
citation_role
source_title
article_or_segment_title
author_or_speaker
translator
publication_date
date_precision
volume
issue
page_start
page_end
url
archive_url
timestamp_start
timestamp_end
locator_text
access_date
quote_permission
display_policy
is_primary_citation
provenance_note
review_status
notes
```

## citation_role

```text
primary_source
parallel_source
discovery_source
repost
retelling
translation
commentary
index_only
unknown
```

## display_policy

```text
public
public_excerpt_only
internal
restricted
withheld
```

## quote_permission

```text
public_domain
open_license
short_quote_only
locator_only
permission_required
unknown
```

## date_precision

```text
exact_date
year
month
issue
dynasty
period
unknown
```

## Review Rules

1. A public case must have at least one citation.
2. `is_primary_citation` marks the citation preferred for display and recommendation.
3. Modern reposts can be discovery sources, but should not be treated as earliest sources.
4. YouTube citations should use `timestamp_start` and `timestamp_end` when available.
5. When a case is derived from a reproducible extracted segment, `source_entry_id` should be recorded.
