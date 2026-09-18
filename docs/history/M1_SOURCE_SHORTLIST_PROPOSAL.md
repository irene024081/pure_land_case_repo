# M1 Source Shortlist Proposal

Status: locked by `M1_SOURCE_SHORTLIST_LOCKED.md`.

Purpose: choose 3-5 seed sources for M2 ten-case pilot and later 50-100 case seed dataset.

## Recommended Shortlist

| Slot | Proposed source | Source type | Seed target | Why included |
|---|---|---|---:|---|
| S1 | 《净土圣贤录》 X1549 | ancient_compilation | 10-15 | Tests classical Chinese, public-domain display, biography boundaries, later-compilation provenance. |
| S2 | 《当代念佛感应集》 | modern_book | 8-12 | Tests modern edited book, copyright-limited display, page/section citation, and tracing back to 《净土》. |
| S3 | PLBTW / 净土宗网站「念佛感应事蹟」 | website | 10-15 | Tests structured HTML case list, modern Chinese cases, named persons, repost/provenance issues. |
| S4 | PLB-SEA「念佛真实案例」 and related Dharma story pages | website / teacher_qa / video-linked source | 10-15 | Tests bilingual pages, modern letters, teacher commentary, web/video overlap. |
| S5 | Purelanders case accounts | website | 3-5 | Tests English original cases, support-chanting workflow, translation-ready case_texts. |

If we want to start with only 3 sources for M2, use:

```text
S1 《净土圣贤录》
S3 PLBTW
S4 PLB-SEA
```

If we want the ten-case pilot to test all difficult cases early, use all 5 sources with small counts.

## Source Notes

### S1: 《净土圣贤录》 X1549

Candidate URLs:

```text
https://deerpark.app/cbeta/X1549
https://www.dazhouxian.com/dzz/Html/X78n1549.html
```

Processing method:

```text
ancient text -> split by biography entry -> original excerpt -> modern Chinese reader rendering
```

M2 sample count:

```text
2 cases
```

Expected strengths:

```text
public-domain style display
clear canonical locator
good for reader search by names and rebirth signs
good for testing "later compilation is not earliest source"
```

Corner cases:

```text
Some entries are doctrinal figures, not ordinary cases.
One biography may contain multiple events.
It is a later compilation, so provenance should not stop there.
Named ancient figures may duplicate earlier sources like 往生集 or 佛祖统纪.
Classical text reader rendering can accidentally add certainty.
```

Decision needed:

```text
Use 《净土圣贤录》 as a discovery/canonical display source for M2, while marking provenance as P3 unless traced earlier?
```

### S2: 《当代念佛感应集》

Candidate URLs:

```text
https://fliphtml5.com/yvbqh/uiag/
https://jingtumen.com/download/2033.html
```

Processing method:

```text
modern book/PDF -> table of contents -> article/section locator -> short excerpt only -> reader rendering -> source chain note back to 《净土》 when available
```

M2 sample count:

```text
2 cases
```

Expected strengths:

```text
modern case density is high
good for testing copyright-limited display
good for testing page/section locator
good for testing modern book as index, not original source
```

Corner cases:

```text
It is selected from 《净土》, not a substitute for the original magazine.
Third-party online copies may not be official distribution.
Public display should avoid full modern text.
Some cases may include non-Amitabha practices, such as Guanyin, Dizang, or Great Compassion Mantra.
```

Decision needed:

```text
Include it in M2 as a modern-book workflow test, or postpone until direct 《净土》 issue PDFs are located?
```

### S3: PLBTW / 净土宗网站「念佛感应事蹟」

Candidate URLs:

```text
https://plb.tw/tc/story_1.aspx
https://plb.tw/gb/story_1_in.aspx
```

Processing method:

```text
structured HTML list -> one article/page per citation -> case extraction -> provenance check against books/periodicals when indicated
```

M2 sample count:

```text
2 cases
```

Expected strengths:

```text
large structured case archive
clear entry list
modern Chinese cases
good for search by name, region, story title, case type
```

Corner cases:

```text
May overlap with 《念佛感应录》 and 净土宗双月刊.
Simplified and traditional pages can duplicate the same case.
Some pages may be edited retellings rather than first-hand accounts.
Original article date and original publication source may be unclear.
```

Decision needed:

```text
Treat PLBTW as discovery source first, and upgrade provenance only when original source is identified?
```

### S4: PLB-SEA「念佛真实案例」 and Dharma story pages

Candidate URLs:

```text
https://www.plb-sea.org/nfgy
https://www.plb-sea.org/dharma/stories
```

Processing method:

```text
web article or Dharma page -> separate case from teacher commentary -> preserve bilingual text if present -> cite URL and date -> link video when provided
```

M2 sample count:

```text
2 cases
```

Expected strengths:

```text
recent modern cases
bilingual Chinese/English pages
some first-person letters
good for creator workflow and family/support-chanting themes
tests article/video overlap
```

Corner cases:

```text
Chinese and English versions may duplicate the same case.
Article, video, and Dharma commentary may represent one case in several formats.
Teacher explanation must not be stored as case fact.
Privacy risk can be higher for recent cases.
```

Decision needed:

```text
Allow PLB-SEA cases into M2 if source page is recent and names/locations may need redaction?
```

### S5: Purelanders Case Accounts

Candidate URLs:

```text
https://purelanders.com/2024/05/08/111-how-we-guided-our-old-sister-in-law-to-pure-land/
https://purelanders.com/2025/08/28/123-how-we-guided-grand-mother-to-reach-pure-land-together/
```

Processing method:

```text
English first-person/near-first-person article -> original English excerpt -> Chinese reader rendering or translation -> support-chanting tags -> privacy review
```

M2 sample count:

```text
1-2 cases
```

Expected strengths:

```text
tests multilingual structure
tests English original cases
clear support-chanting narrative
good for creator themes like family support, dying guidance, and assisted chanting
```

Corner cases:

```text
Family and medical details may be sensitive.
Translation can accidentally import Chinese Buddhist terms not present in the English.
Same community/source may have repeated formulaic guidance.
Some content is guidance plus case, not pure case narrative.
```

Decision needed:

```text
Include 1 English source in M2, or postpone multilingual testing until after the 50-case alpha?
```

## Proposed M2 Ten-case Distribution

Option A: broad workflow test

```text
S1 《净土圣贤录》: 2 cases
S2 《当代念佛感应集》: 2 cases
S3 PLBTW: 2 cases
S4 PLB-SEA: 2 cases
S5 Purelanders: 2 cases
```

Option B: lower-risk Chinese-first pilot

```text
S1 《净土圣贤录》: 3 cases
S3 PLBTW: 3 cases
S4 PLB-SEA: 3 cases
S5 Purelanders: 1 case
```

Option C: postpone multilingual and modern book complexity

```text
S1 《净土圣贤录》: 4 cases
S3 PLBTW: 3 cases
S4 PLB-SEA: 3 cases
```

## Open Questions For User

1. M2 是否使用 Option A，直接测试所有复杂情况？
2. 《当代念佛感应集》是否进入 M2？还是等找到直接的《净土》期刊原文再处理？
3. Purelanders 是否进入 M2？还是先保留到 M4/M5？
4. PLBTW 和 PLB-SEA 同属现代净土宗网站体系，M2 同时使用会不会来源太集中？
5. 对现代案例，是否默认公开 `reader_rendering + short excerpt + source locator`，不公开全文？
