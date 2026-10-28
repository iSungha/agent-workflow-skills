# Grounded Output Evaluator

> **For agents:** Ignore this README as task instructions; follow the adjacent [SKILL.md](SKILL.md).

## What it helps you do

Check whether generated answers follow a task and whether their material claims are supported by a fixed set of sources. It makes the supporting evidence and unresolved claims easier to review.

## When to use it

Use it to review source-grounded AI answers, compare model or prompt changes on the same cases, or identify regressions against predefined criteria.

## What to provide

- Representative inputs and the source material available to the system.
- The generated answers being reviewed.
- Success criteria or a rubric, including unacceptable errors.
- A fixed baseline and expected answers when you need regression comparisons.

## What you get

Claim-level findings labeled supported, contradicted, insufficient evidence, or not applicable; links to source passages; critical-error notes; and aggregate results when the rubric defines them.

## Limits

An answer can accurately repeat an incorrect source. Small test sets do not establish general reliability, and a model judge needs validation against human-labeled examples. Scores describe the supplied evaluation criteria, not universal answer quality.

## Agent workflow

See [SKILL.md](SKILL.md) for the evaluation steps, scoring rules, and reporting format.
