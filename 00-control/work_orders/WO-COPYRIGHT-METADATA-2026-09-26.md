# Work Order: Correct CBETA Rights Metadata

- Work Order ID: `WO-COPYRIGHT-METADATA-2026-09-26`
- Status: `review-needed`
- Owner approval: confirmed in chat on 2026-09-26

## Goal

Correct CBETA-derived source records so that the public-domain status of the underlying historical works is not confused with the CC BY-NC-SA 4.0 conditions attached to the retained CBETA electronic edition.

## In Scope

- Make batch capture inherit the selected rights review instead of hard-coding public-domain metadata.
- Keep the Dazhouxian delivery of `SRC0001` under `RR0005` and create a separate CBETA delivery review for later `SRC0001` entries.
- Correct the 361 CBETA-derived entries and their catalog rows.
- Require open-license provenance fields during Pipeline rights precheck.
- Render open-license attribution and flag stale rights-check wording without modifying accepted Pipeline responses.
- Correct related licensing and jurisdiction documentation.

## Out Of Scope

- Rewriting accepted Pipeline responses or baselines.
- Obtaining permissions from modern-source rights holders.
- Changing the legal treatment of modern sources beyond correcting unsupported research wording.

## Acceptance Criteria

- All CBETA-derived manifests use `open_license_verified` and the correct rights review.
- All CBETA-derived manifests include license, terms, version, revision, modification notice, and public-display policy.
- The four Dazhouxian-derived `SRC0001` entries remain under `RR0005`.
- Batch capture tests cover open-license inheritance.
- Catalog, manifest, and project test suites pass.
- No accepted Pipeline response or baseline is modified.

## Handoff

- Implementation commit: `7ac24e3`
- Corrected 361 CBETA-derived entries that were mislabeled as public domain.
- Completed the license metadata on one existing CBETA entry without changing its accepted normalized-content hash.
- Kept four Dazhouxian-derived `SRC0001` entries under `RR0005` as public-domain records.
- Verified 370 source-entry manifests and all six source catalogs.
- Ran 68 unit tests successfully; one test was skipped.
- Confirmed that no accepted Pipeline response or baseline changed.
- Owner review is still required before this work order is accepted.
- Permissions for the six modern sources remain unresolved. Their research records now block external AI processing pending a documented rights basis and provider review.
- `CASE000010` retains historical wording inside its accepted rights-check response. The generated report flags that wording and displays the current CBETA license notice; a future Pipeline rerun may replace it without editing the accepted response in place.
