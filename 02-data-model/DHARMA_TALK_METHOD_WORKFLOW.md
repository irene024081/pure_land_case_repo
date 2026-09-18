# Dharma Talk Method Analysis Workflow

Purpose: study reusable explanation methods from Dharma talks so creator assistance can produce more precise teaching, confidence-building, and practice-oriented angles.

This workflow analyzes methods. It does not treat a teacher's talk as event evidence, doctrinal consensus, or a style template to imitate.

## Processing Chain

```text
authorized talk source
-> transcript capture with timestamps
-> speaker and quotation segmentation
-> scripture, case, explanation, exhortation, and transition classification
-> rhetorical method extraction
-> doctrinal citation check
-> reusable method pattern
-> prompt evaluation set
-> human or machine review
```

## Required Separation

```text
quoted scripture or patriarch text
case narrative
teacher interpretation
practical instruction
confidence-building statement
rhetorical transition
personal anecdote
```

Each extracted method records the exact timestamp segments that support it.

Method records improve explanation structure. They cannot serve as doctrinal evidence unless the underlying teaching segment is separately registered and approved in `doctrinal_citations`.

## Method Record

```text
source_method_id
source_entry_id
teacher_id
talk_title
segment_ids
method_type
audience_problem
opening_move
case_use
doctrinal_bridge
confidence_move
practical_application
caution_or_boundary
closing_move
doctrinal_citation_ids
language
review_status
notes
```

## Initial Method Types

```text
question_to_case
case_to_doctrine
doctrine_to_practice
doubt_to_confidence
misunderstanding_correction
comparative_case
stepwise_guidance
source_explanation
ethical_caution
```

## Prompt Optimization

Prompt versions should be evaluated against a fixed case set. At minimum, score:

```text
factual fidelity
segment citation coverage
angle specificity
doctrinal attribution
audience fit
useful structure
uncertainty preservation
sensationalism risk
style imitation risk
```

The preferred prompt is the one that improves useful specificity while preserving evidence and attribution. Fluency alone is not a passing criterion.

## Use In Reader Commentary

Before a method can be used in `dharma_case_commentary`:

```text
the talk transcript is retained with timestamps
the method is supported by identified segments
any doctrinal claim has separate approved doctrinal citations
teacher-specific interpretation remains attributed
rights policy permits the intended use
```

The method may guide opening, transition, question handling, and practical structure. It may not authorize new facts or doctrine.

## Rights And Attribution

1. Retain transcripts only when permitted for internal research or licensed use.
2. Public output should cite the talk and timestamp without reproducing long transcript passages.
3. Store teacher-specific observations as attributed source methods.
4. Derive reusable abstract methods across multiple talks where possible.
5. Do not instruct the model to write in the distinctive style of a living teacher.
