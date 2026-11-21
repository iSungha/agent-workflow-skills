---
name: frontend-engineering
description: Use when building or fixing frontend components, forms, routing, client state, typed API integration, or rendering and request performance. Focus on functional behavior and ownership. Use a design handoff workflow for visual implementation and a refactor workflow for behavior-preserving restructuring.
---

# Frontend Engineering

Trace the user action through the view, state, and transport before choosing what to change. Reuse the existing boundary that already owns the behavior.

## Inputs

- The intended interaction or failure, relevant routes, current API and UI contracts, and the framework versions in the project.
- A nearby working flow and the existing tests or fixtures for the affected behavior.

## Workflow

1. Trace a representative path from route and component through state, API adapter, and completion. Identify each affected consumer and the expected success, empty, pending, and failure behavior. For a bug, start with the smallest reliable reproduction.
2. Assign state a lifetime. Use the existing server cache for remote data, feature state for an editable draft, the last saved revision for dirty comparisons, and URL state for navigation users should be able to revisit. Derive display values when possible. Key draft resets to deliberate transitions such as switching records. Guard late responses by request, entity, or account identity as appropriate.
3. Keep transport and UI contracts explicit. With TypeScript, narrow unknown inputs at the boundary and use the repository's validators where needed. Keep zero, null, and omission distinct when the API does. Separate refresh and denial from empty data. On writes, preserve duplicate-submit protection, revision checks, actionable errors, and invalidation of affected views. Keep edits made after a submitted snapshot. A timeout can leave the write outcome unknown.
4. Keep view composition, domain decisions, and data transport at their existing boundaries. Prefer cohesive props and pure transforms to generic hooks or global state. Share a contract when its consumers need the same behavior. Follow existing server/client and cache boundaries, keep private results scoped to their account, and send untrusted content through the project's safe rendering path. Use semantic controls, labels, keyboard access, and visible status or errors.
5. Investigate performance at the user action in question. Compare render cost, request waterfalls, payload size, or bundles under matching conditions before adding memoization, lazy loading, or virtualization. Clean up owned subscriptions and timers. Preserve keyboard and focus behavior if the rendering strategy changes.
6. Exercise the changed path with the repository's focused checks. For an asynchronous editor change, include late success or failure and a record change when either can corrupt current state. Confirm that the real completion path updates the intended consumers.

## Output

Describe the behavior, the state or API owner that changed, and the targeted checks. If performance motivated the change, report the measured quantity and conditions or label the improvement as an expectation.

## Example

Fictional example: A profile editor loses typed text when a background refresh returns. Keep remote data and the active draft separate. After save, update the saved baseline from the server while retaining any text typed after submission. Verify refresh, failed save, and a late response after switching profiles.

## Verification and limits

Choose evidence that exercises the risk: pure tests for mappings, interaction tests for state transitions, and a real or isolated integration path for transport and cache effects. Static types cannot establish runtime payload validity, and a profiler result covers only its measured scenario.
