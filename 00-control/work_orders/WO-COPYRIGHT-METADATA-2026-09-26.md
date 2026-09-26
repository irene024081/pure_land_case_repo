# Work Order: Correct CBETA Rights Metadata

- Work Order ID: `WO-COPYRIGHT-METADATA-2026-09-26`
- Status: `in-progress`
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

Record the final commit, tests, migration counts, and remaining review needs before changing the status to `review-needed`.
