# M2 Source Rights Review

Review date: 2026-09-17

Scope: operational review for internal retention, extraction, and public display in the M2 pilot. This is not a legal opinion. National exceptions differ, and permission may still be required.

The public-domain baseline for SRC0001 is recorded separately in `../data/rights_reviews/RR0005.yml`. It permits pipeline testing with the normalized historical text while excluding modern delivery-site code, images, and editorial assets.

## Decisions

| Review | Source | Status | Internal handling | Public handling | Required follow-up |
|---|---|---|---|---|---|
| RR0001 | SRC0002, 《当代念佛感应集》 | `legal_review_required` | Restricted local artifact and normalized text for pilot processing. | Metadata, factual summary, locator, and minimal excerpt only. | Ask Donglin Temple or the identified publisher about digital retention, quotation, adaptation, and translation. |
| RR0002 | SRC0003, PLBTW | `legal_review_required` | Restricted local artifact and normalized text for pilot processing. | Metadata, factual summary, link, and minimal excerpt only. | Ask the site or foundation whether testimony pages may be retained, adapted, translated, and republished. |
| RR0003 | SRC0004, PLB-SEA | `legal_review_required` | Restricted local artifact and normalized text for pilot processing. | Metadata, factual summary, link, and minimal excerpt only. | Clarify whether the page's copy, share, and download controls grant reuse beyond personal access. |
| RR0004 | SRC0005, Purelanders | `restricted_internal` | Restricted local artifact and normalized text; no public full text. | Metadata, factual summary, link, and minimal excerpt only. | Obtain permission through the site's contact channel before recirculation, translation publication, or substantial quotation. |

## RR0001: SRC0002

The host website states that its article materials may be reposted and circulated. The selected object is a downloadable PDF compiled and printed by Donglin Temple, however, and contains articles selected from issues of 《净土》 published from 2003 through 2021. The PDF describes circulation as a goal and includes a dedication for people who circulate it, but no explicit copyright license or permission scope was found in the inspected front matter and final page.

Evidence:

- [Jingtumen home page](https://jingtumen.com/) states that site article materials may be reposted and circulated.
- [Download page for 《当代念佛感应集》](https://jingtumen.com/download/2033.html) identifies the Donglin Temple edition and provides a download.
- The locally retained PDF identifies Donglin Temple as printer and the Donglin Pure Land Culture Research Institute as compiler. Its publication note says articles were selected from 《净土》 issues.

Assessment:

```text
the host's blanket statement may cover its own article materials
it does not establish that the host can sublicense every third-party PDF and underlying periodical article
the book's circulation language indicates intent but does not define modification, translation, commercial, or database rights
```

## RR0002: SRC0003

No copyright, open-license, terms, or testimony-specific republication statement was found on the inspected PLBTW home page or retained case page. Some separately published PLBTW books contain statements such as “no copyright, welcome to reprint,” but that language belongs to those identified publications and is not applied to all website testimony pages.

Evidence:

- [PLBTW home page](https://plb.tw/tc/index.aspx) identifies the Chinese Pure Land Buddhist Association and Pure Land Buddhism Foundation as site operators and provides contact information.
- The selected article page identifies an oral narrator and recorder but provides no license in the retained page.

Assessment:

```text
do not inherit a license from a different PLBTW book or PDF
retain the pilot copy as restricted while permission is unresolved
public full text and published translation require permission or a jurisdiction-specific legal basis
```

## RR0003: SRC0004

The selected PLB-SEA article identifies the organization as publisher and provides copy, share, and download controls. No explicit copyright license, terms page, or statement authorizing republication, translation, or commercial reuse was found.

Evidence:

- [PLB-SEA case article](https://www.plb-sea.org/nfgy/mmsz) identifies the publisher, authorial contributor, publication context, multilingual versions, and copy/share/download controls.
- [PLB-SEA home page](https://www.plb-sea.org/) and article footer provide organizational contact details but no reuse license found during this review.

Assessment:

```text
copy, share, and download controls support access but are not treated as a republication license
the contributor, organization, teacher commentary, and translations may involve separate rights
retain internally and publish only summary, locator, and minimal excerpt until clarified
```

## RR0004: SRC0005

Purelanders displays a site copyright notice and the statement “You cannot copy content of this page.” Other Purelanders translation pages state that recirculation requires permission through the site's contact channel. This is direct evidence against assuming an open reuse license.

Evidence:

- [Purelanders home page](https://purelanders.com/) displays the copyright and no-copy statements.
- [Purelanders scripture and commentary directory](https://purelanders.com/2021/05/24/jinglun/) states that recirculation of English text requires permission through the site contact page.
- [Selected testimony](https://purelanders.com/2025/08/28/123-how-we-guided-grand-mother-to-reach-pure-land-together/) remains publicly readable but contains no separate open license.

Assessment:

```text
public access does not grant republication rights
do not publicly reproduce the article or publish a substantial translation without permission
use metadata, original factual analysis, a minimal quotation when justified, and a direct source link
```

## Common Publication Rule

Until permission or legal review changes an item-level decision:

```text
allowed: metadata, source link, factual index fields, independently written summary, risk notes
conditional: minimal quotation with attribution and a clear purpose
withheld: full original text, substantial translation, downloadable source artifact, extensive close paraphrase
```

Reader renderings for modern sources require an additional similarity check. They should communicate facts in an independently structured account and must not function as substitutes for the original article.

## Generated Content Research

The source decision does not automatically decide every generated output. Each `independent_factual_account` and `dharma_case_commentary` requires an output review under `COPYRIGHT_RESEARCH_WORKFLOW.md`.

For RR0001 through RR0003, independently structured factual accounts and doctrine-led commentary may proceed only as provisional drafts until item-level attribution, quotation scope, expression similarity, substitution risk, and publication jurisdiction are checked.

RR0004 is stricter because Purelanders presents an explicit no-copy and permission position. Use a brief facts-only account by default. A commentary that retells substantial case detail requires permission or legal review even when its doctrinal explanation is independently written.

None of the four reviews permits public distribution of normalized full text, source artifacts, or a full-text dataset.
