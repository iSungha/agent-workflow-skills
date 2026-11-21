---
name: frontend-refactoring
description: Use when reviewing or making a behavior-preserving frontend refactor for concrete duplication, coupled components, unclear state ownership, tangled CSS, or proven dead code. Use for maintainability work with regression risk.
---

# Frontend Refactoring

Start with a maintenance problem you can point to. Choose the smallest structural change that makes future edits safer for the current consumers.

## Inputs

- The code and maintenance problem, known consumers, and the contracts the refactor should preserve.
- Existing behavior tests, rendered states for shared UI, or a measured baseline when performance is part of the request.

## Workflow

1. Name the smell and its consequence. Examples include two copies of a rule drifting apart, styles competing across scopes, or a component that owns unrelated async lifecycles. Trace direct and indirect consumers, including dynamic imports, selectors, theme overrides, tests, and public entry points where relevant.
2. Write down what would regress: draft lifetime, event order, keyboard focus, computed styles, request count, error precedence, or mutation timing. Capture the most direct baseline. If existing evidence misses a risky contract, add a focused characterization check when appropriate. Keep intentional behavior changes separately reviewable.
3. Move one responsibility at a time. Apply single responsibility to things that change for different reasons and DRY to knowledge that must stay consistent. A small pure function or shared presentation component is often sufficient. Preserve distinct mutation lifecycles even when two forms look alike. Keep the simpler local implementation when an extraction needs speculative variants or a new dependency.
4. For CSS, find the rule that actually wins and the owner of the shared default. Check inheritance, order, specificity, responsive conditions, and theme. Consolidate shared styling only when its consumers should move together. Delete obsolete code after tracing its reachable entry points and confirming that the new owner covers the behavior.
5. Compare against the baseline and review the affected consumers. Verify behavior at the smallest suitable boundary, and render affected themes, sizes, or focus states when the change touches layout or shared controls. If asked only for an audit, report the evidence and candidate change without editing.

## Output

State the maintenance problem, the responsibility moved or deleted, the consumers covered, and the before/after evidence. For an audit, identify the source location and explain likely regression risk and a focused check.

## Example

Fictional example: Two editors duplicate their field layout. One applies changes to an enclosing draft, while the other persists immediately. Extract the shared field presentation, preserve the separate handlers, and verify both Cancel paths and the resulting write count.

## Verification and limits

File length, repeated syntax, and fewer components are weak success measures on their own. Static inspection can miss runtime use, and tests can miss consumer-specific styling changes. A speed claim requires a comparable measurement.
