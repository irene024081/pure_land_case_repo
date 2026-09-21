# Next Steps

For the current cross-project status, gaps, decisions, and acceptance criteria, start with [PROJECT_HUB.md](PROJECT_HUB.md). This file keeps the original milestone details.

This plan starts after the v0.1 foundation commit.

## M2A: First Real Baseline (Completed 2026-09-18)

Goal: complete one real Article Run and its Case Run locally with ENT000001.

Tasks:

1. Generate complete offset-based source segments with the v1 prompt.
2. Run case detection and confirm the legacy CASE000001 ID is reused.
3. Complete all Case Run stages with one declared local model adapter.
4. Inspect the factual and rights claim ledgers.
5. Approve the sanitized Run Records as the first regression baseline.

Exit criteria:

- all source characters belong to exactly one segment;
- every fact and generated paragraph resolves to valid evidence IDs;
- unsupported and contradicted factual claim counts are zero;
- Catalog, local Run, and tracked Run Record agree;
- publication package follows RR0005.

Accepted result:

- Pipeline `0.1.1`, Article Run `RUN-ENT000001-M2A-P011`, and Case Run `RUN-ENT000001-M2A-P011-CASE000001` completed.
- `CASE000001` was reused after one case candidate was detected.
- Eight segments cover all 155 source characters; 22 case facts and 22 checked content claims resolve to retained evidence IDs.
- Unsupported and contradicted claim counts are zero. Rights checks cover both published outputs, and the RR0005 package scope is `public`.
- `data/baselines/M2A_ENT000001_P011.json` is the first machine-accepted regression baseline.
- Deduplication was limited to `current_request_only`; corpus candidate retrieval remains required before a corpus-wide no-match decision.

## T02 v0.2 Bridge: M2A Migration And Real Run (Next)

Goal: validate the new identity/provenance model against the accepted M2A evidence without rewriting the historical baseline.

1. Review `02-data-model/T02_V02_MIGRATION.md` and `data/migrations/T02_v0.2_CASE000001.json` against retained M2A segments and facts.
2. Run `ENT000001` with Pipeline `0.2.0` and a new Run ID. Confirm no Case ID exists before deduplication.
3. Resolve the existing `CASE000001` link through an explicit human `reuse` decision with reviewer and reason. Record the new Occurrence and its unresolved upstream citation.
4. Compare factual, rights, and publication gates with the historical baseline. Do not treat different prompt output or new IDs as automatically equivalent.

Progress on 2026-09-21: `RUN-ENT000001-M2A-T02V02` replayed the retained v0.1 evidence with hash-checked fact/tag ID conversion. Deduplication selected the historical `CASE000001` and returned `same_case`. The Candidate Run is blocked at `case_resolution: review_required`; no Case ID has been reused. This replay validates migration mechanics, not the quality of fresh v0.2 AI extraction.

Exit criteria: evidence links validate, no premature Case ID or positional reuse occurs, the new Run is reproducible, and the old baseline hashes remain unchanged. A new baseline requires separate acceptance.

## M2B: Unseen Article Test (After Bridge)

Goal: test generalization with the accepted v0.2 identity flow while retaining unchanged v1 reader/creator/check prompts for comparison.

Select three new items:

1. a standard item from an existing structured Source;
2. a complex item with commentary, multiple reporters, or multiple cases;
3. an item from a new public-domain or open-license Source.

Precondition completed on 2026-09-18:

- Pipeline `0.1.2` adds deterministic dedup candidate retrieval to the request builder.
- Candidate selection rules are versioned in `pipeline/retrieval/dedup_candidates.v1.json`.
- Each Request records selected candidates, scores, reasons, scope, and a candidate-set hash.
- Restricted candidate content forces the deduplication Stage to use a local Adapter.
- `factual_check` now receives `case_extraction` directly.
- Reader, creator, factual, and rights v1 Prompts remain unchanged; v0.2 adds versioned candidate-based extraction, deduplication, and occurrence prompts.

Known non-blocking quality issues are tracked in `KNOWN_ISSUES.md`. In particular, `reader_generation/v1` is faithful but not yet sufficiently engaging, and `creator_analysis/v1` can produce generic angles. Record these failures during M2B and design v2 only after the three unseen results are comparable.

Run each through inventory, capture, Article Run, Candidate Run, identity resolution, and publication checks. Record failures before tuning reader/creator prompts.

Exit criteria:

- zero manual edits to AI response JSON after generation;
- zero silently dropped source sections;
- multi-case and zero-case paths both tested;
- failures are reproducible from tracked Run Records.

## M2C: Inventory Adapters

Goal: fill Source article catalogs reproducibly.

Implement the adapter interface and first reusable adapters:

```text
static_headings
wordpress_archive
paginated_html
pdf_toc
```

Each adapter supports initial backfill, stable source keys, incremental refresh where applicable, exact duplicate detection, and a dry-run diff before updating CSV.

Exit criteria:

- SRC0001 selected section has a complete catalog;
- one active website supports incremental refresh;
- disappeared and changed items remain auditable;
- AI classification is versioned separately from deterministic discovery.

## M2D: Canonical Data Promotion

Goal: move passed Run outputs into machine-readable canonical datasets.

Define promotion commands for segments, case facts, Cases, Source Occurrences and their parent links, text versions, entities, identity decisions, and creator metadata. Promotion is idempotent, collision-checks provisional Occurrence IDs, and refuses failed or superseded runs.

Exit criteria:

- canonical records can be rebuilt from retained evidence and Run Records;
- legacy Markdown Case Packs are no longer queried by application code;
- schema migrations and record versions are explicit.

## M3: Ten-case Dataset

Goal: complete ten cases using the same accepted Pipeline version.

Before adding modern restricted content, record the approved local or external processing policy for each Source. Replace the second Purelanders slot with an open or public-domain English source unless permission is obtained.

Exit criteria:

- ten promoted cases;
- at least three Source types and two languages;
- dedup and translation relations tested;
- regression metrics pass across the complete set.

## M4: Search Prototype

Goal: prove reader and creator retrieval before full website development.

Build a local search index over names, Sources, signs, practices, places, reader text, facts, and creator angles. Test source lookup, person lookup, sign lookup, highlighted evidence, and theme-to-case ranking.

## Deferred

These are intentionally outside the next milestone:

- full public website;
- large doctrinal commentary corpus;
- automated scheduled crawling for every Source;
- 50-100 case scaling;
- Google Sheets or Notion synchronization;
- production database selection.
