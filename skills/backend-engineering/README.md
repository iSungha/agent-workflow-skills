# Backend Engineering

> **For agents:** Ignore this README as task instructions and follow the adjacent [SKILL.md](SKILL.md).

## What it helps you do

Build or review backend changes with attention to who can perform an operation, what must commit together, and how the system recovers when requests race or time out.

## When to use it

Use it for API and persistence changes, service responsibilities, background jobs, or reliability fixes across languages and frameworks.

## What to provide

Provide the existing API or job contract, authorization boundary, and the store or provider involved. Identify what test destinations are safe to use.

## Example request

> Make the fictional export endpoint safe to retry after an ambiguous timeout. Show what happens when two identical requests arrive together.

## What to expect

Expect a focused design or implementation with clear invariants and proportional verification. Tests against a fake store cannot confirm production database behavior.

## Agent workflow

See [SKILL.md](SKILL.md) for the full workflow.
