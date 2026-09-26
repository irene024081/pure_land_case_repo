# Rights Review Register Schema

`rights_reviews` records operational copyright and platform-term decisions. It is a review trail, not legal advice or a guarantee of non-infringement.

## Source-level Fields

```text
rights_review_id
source_id
rights_status
rights_holder
original_author
publisher_or_platform
license_type
license_url
terms_url
terms_checked_at
source_jurisdiction
intended_publication_jurisdictions
internal_retention_basis
automated_access_policy
ai_processing_policy
external_ai_processing_policy
allowed_ai_providers
provider_data_retention_requirement
provider_training_opt_out_required
cross_border_transfer_status
public_display_policy
allowed_excerpt_scope
translation_policy
commercial_use_policy
dataset_distribution_policy
independent_factual_account_policy
dharma_commentary_policy
expression_similarity_threshold
substitution_risk_threshold
applicable_jurisdictions
legal_exception_basis
review_evidence
reviewed_by
reviewed_at
next_review_at
notes
```

## rights_status

```text
pending
public_domain_verified
open_license_verified
permission_obtained
restricted_internal
locator_only
legal_review_required
prohibited
unknown
```

## Item-level Override Fields

```text
rights_review_id
source_entry_id
inherits_source_review_id
override_reason
third_party_content_present
item_license
item_public_display_policy
item_allowed_excerpt_scope
item_independent_factual_account_policy
item_dharma_commentary_policy
item_translation_policy
item_review_status
notes
```

An item review is required when attribution, license, embedded third-party material, intended use, or publication scope differs from the source default.

## Research-layer Fields

Research records that inform but do not replace an operational review use:

```text
record_layer: research
informs_rights_review_id
review_status
confirmed_by
confirmed_date
tier_internal_retention
tier_ai_processing
tier_summary_link
tier_full_text
tier_translation
```

An operational source or catalog must continue to reference the operational review until a research record is explicitly promoted.

## Intended-use Decision Status

These values apply to one proposed use, not to the source-level `rights_status` field:

```text
allowed_by_documented_exception
metadata_only
permission_required
```

## Rules

1. Review a source before systematic extraction or publication.
2. Reuse a source-level decision for ordinary items from the same source.
3. Review an item separately for long quotations, translation, adaptation, commercial publication, unclear repost chains, or embedded media.
4. `internal_research_copy` is an operational description, not proof of permission or a statutory exception.
5. File format conversion does not change copyright status.
6. Storage, local AI processing, external AI processing, public display, translation, and commercial use are separate permissions.
7. Preserve the evidence used for the decision, including license and terms URLs with check dates.
8. Research internal retention, AI processing, factual accounts, commentary, translation, and dataset distribution as separate intended uses.
9. No fixed quotation length or transformation percentage is treated as a legal safe harbor.
10. `allowed_by_documented_exception` requires jurisdiction-specific reasoning and approved review.
11. `ai_processing_policy: unknown` blocks sending full source text to an external provider. Local processing may be recorded separately.
12. Provider approval is explicit and provider-specific. Approval for one API does not authorize another provider or a different retention policy.
