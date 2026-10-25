---
name: grounded-output-evaluator
description: Evaluate generated answers against a fixed source packet and expected criteria, with claim-level support labels and repeatable regression cases. Use for source-grounded or educational AI output; not as proof that the underlying sources are correct.
---

# Grounded Output Evaluator

Check whether generated content follows the task and is supported by the supplied sources. Make the evidence for each finding inspectable. Separate deterministic checks from rubric-based judgment and never treat a model's confidence as evidence.

## Inputs

- A fixed set of representative inputs and the source material available to the system.
- The generated outputs being evaluated.
- Task-specific success criteria, including required coverage, citation rules, and unacceptable errors.
- A known-good baseline or expected answers when regression comparison is needed.

If there is no expected answer, define observable criteria before scoring. Mark ambiguous cases for review rather than creating a convenient answer after seeing the output.

## Workflow

1. Freeze the evaluation set and record its version, source identifiers, system configuration relevant to the run, and evaluation date. Keep private source data out of public examples and logs.
2. Break each output into material factual claims and task requirements. Ignore stylistic differences unless style is part of the explicit rubric.
3. For every material claim, locate the supporting source span. Label it `supported`, `contradicted`, `insufficient evidence`, or `not applicable`. Check that quotations, citations, dates, quantities, and scope match the source.
4. Score each predeclared dimension using the supplied rubric. Useful dimensions include factual support, source attribution, required coverage, instruction compliance, uncertainty handling, and readability. Define anchors for score levels before comparing runs; do not invent a universal threshold.
5. Record critical errors separately from aggregate scores. A correct average can hide one unsupported high-impact claim or one omitted required concept.
6. Compare candidate and baseline outputs on the same fixed cases. Report changed outcomes, counts, denominator, evaluator method, and examples of regressions. If an automated judge is used, validate it against human-labeled cases and disclose its limits.
7. Classify the result using the task's predefined quality bands. If none exist, report the dimension results without imposing arbitrary `pass` or `fail` thresholds.

## Output

Report the evaluation-set identity, rubric, per-case findings, claim-to-source references, critical errors, aggregate calculations, baseline comparison, quality classification if predefined, and limitations. Use stable case identifiers so later runs can reproduce the comparison.

## Example

See [the fictional source-support example](../../examples/grounded-output-review.md) for a small claim-level review. Its source and answer are invented for illustration.

## Verification and limits

Mechanical citation presence is not the same as citation support. A grounded answer can repeat an inaccurate source, and a small test set cannot establish general reliability. Report sample size and evaluation method. Do not publish confidential prompts, proprietary rubrics, personal records, or private source text.
