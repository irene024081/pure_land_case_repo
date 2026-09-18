# Pipeline Regression Policy

## Fixed Evaluation Set

The initial regression set is CASE000001 through CASE000005. It covers classical Chinese, modern PDF, Chinese web material, multilingual web material, and restricted English material.

Restricted source text stays local unless its rights record permits the selected provider. A local-only run is still part of the regression set.

## Required Metrics

| Metric | Passing rule |
|---|---|
| schema validity | 100% |
| referenced segment existence | 100% |
| factual claim support coverage | 100% |
| unsupported factual claims | 0 |
| contradicted factual claims | 0 |
| missing uncertainty or attribution | 0 known cases |
| silent case merges | 0 |
| rights-policy violations | 0 |
| required-field completion | 100% |

Narrative depth, readability, creator usefulness, and tag quality are scored separately. They cannot compensate for a failed factual or rights gate.

## Promotion Rule

A new prompt, model, or pipeline version may replace the current version only when all blocking metrics pass, no supported material fact is lost without an explicit reason, no restricted content appears in a public output, and output differences are retained in the evaluation record.

Human review is optional for routine runs. It is required to approve a new baseline, resolve ambiguous deduplication, approve new doctrinal interpretations, or override a blocking rights decision.
