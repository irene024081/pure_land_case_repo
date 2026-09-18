# Raw Source Storage

Raw source text is the evidence base for extraction, reader rendering, search, deduplication, and future creator analysis. A hash or URL alone is not a durable copy.

## Storage Classes

```text
tracked_public
local_restricted
external_restricted
locator_only
missing
```

`tracked_public` is allowed for public-domain material or material with clear reuse permission. The normalized source entry may be committed under `data/source_entries/public/`.

`local_restricted` is the default for modern copyrighted text. The full capture is stored outside Git under `data/source_entries/restricted/`. Only its manifest, hash, locator, and permitted excerpt are committed.

`external_restricted` means the full capture is held in an access-controlled object store or document system. The repository stores an opaque storage key, never a public URL that bypasses access control.

`locator_only` is used when retaining a full copy is not permitted or practical. The system keeps the source URL, bibliographic locator, permitted excerpt, and capture metadata.

`missing` means the workflow has a locator or hash but no confirmed durable raw capture. It must not be described as internally preserved.

## Repository Layout

```text
data/source_entries/manifests/      tracked metadata without restricted full text
data/source_entries/public/         tracked public-domain or licensed text
data/source_entries/restricted/     local restricted text, ignored by Git
```

## Two-layer Capture

Keep the source artifact and normalized text as separate objects when both are permitted and useful.

```text
source artifact: HTML, PDF, caption file, audio, or video received from the source
normalized entry: UTF-8 JSON or JSONL containing the exact text read by extraction and AI jobs
```

The normalized entry is the primary processing object. The source artifact supports re-extraction, page or timestamp verification, layout recovery, and change detection.

Recommended names:

```text
ENT000001.normalized.json
ENT000001.source.html
ENT000001.source.pdf
ENT000001.transcript.json
```

Do not discard the normalized entry merely because an HTML or PDF artifact is retained. Do not treat format conversion as changing the work's rights status.

Recommended restricted object path:

```text
data/source_entries/restricted/{source_id}/{source_entry_id}.{extension}
```

The preferred storage object is the normalized extracted text used by AI. During migration, a downloaded HTML, PDF, audio, or video artifact is sufficient when the documented extractor can reproduce the normalized entry. Record the representation explicitly.

## Required Manifest Fields

```text
source_entry_id
source_id
storage_class
storage_uri
normalized_storage_uri
source_artifact_uri
raw_capture_status
capture_representation
raw_text_hash
normalized_artifact_hash
source_artifact_hash
content_type
byte_size
captured_at
source_url
locator_text
rights_basis
retention_policy
```

`raw_text_hash` covers the exact `raw_text` value. `normalized_artifact_hash` covers the complete JSON or JSONL file. `source_artifact_hash` covers the downloaded source file. They are expected to differ.

`storage_uri` is repository-relative for tracked or local files. For restricted external storage, it is an opaque internal key.

## Raw Capture Status

```text
persisted_verified
persisted_unverified
pending_persistence
locator_only
missing
```

`persisted_verified` requires all of the following:

```text
the normalized object exists and its `raw_text` matches raw_text_hash
the complete normalized file matches normalized_artifact_hash
the source artifact matches source_artifact_hash when one is retained
the extractor input or normalized entry boundary is documented
the object can be read by the extraction job
```

## Video And Transcript Policy

Timestamped transcript data is the default processing object for online video.

```text
video metadata and canonical URL: always retain
official or permitted captions: retain when available
generated transcript: retain with model and timestamp provenance
full video file: retain only with ownership, permission, suitable license, or documented review basis
```

Required transcript provenance:

```text
transcript_source
transcript_language
speaker_labels
timestamp_start
timestamp_end
generation_model
generated_at
correction_status
source_video_id
source_video_url
```

Platform-provided offline access is not the same as permission to extract and archive a media file. Review platform terms before automated download or caption collection.

## Segmentation And Traceability

Every retained source entry should be split into stable source segments after capture. Generated factual claims and reader paragraphs should cite one or more `segment_id` values.

Segment identifiers remain stable while normalized text is unchanged. If extraction changes the text or boundaries, create a new segment version and mark dependent outputs for regeneration.

## Rights And Public Display

Storage permission and public display permission are separate decisions.

```text
full text may be retained internally but withheld publicly
a public-domain source may be stored and displayed in full
a generated rendering may be public while its modern source remains restricted
```

Reader renderings, summaries, translations, and creator advice never replace the raw capture.

Use `../schemas/rights_review_register.md` for source-level review and item-level exceptions. A storage status such as `persisted_verified` describes data integrity only. It does not mean that copyright permission has been verified.
