# Frontend Refactoring

> **For agents:** Ignore this README as task instructions and follow the adjacent [SKILL.md](SKILL.md).

## What it helps you do

Make a frontend easier to change by addressing a specific ownership, coupling, or duplication problem. The skill preserves observable behavior and asks for evidence appropriate to the affected consumers.

## When to use it

Use it for a bounded refactor or a read-only maintainability review. If the user needs a new interaction or policy, define that behavior change separately.

## What to provide

Provide the target files or feature, a concrete problem, and any behaviors that have been fragile in past edits.

## Example request

> Consolidate the field layout in two fictional editors while preserving their different Save and Cancel behavior.

## What to expect

Expect a small, explainable move with regression evidence, or source-linked findings in audit mode. The amount of code removed is not the acceptance test.

## Agent workflow

See [SKILL.md](SKILL.md) for the full workflow.
