---
name: design-to-code
description: Use when implementing an approved Figma design, screenshot, or prototype from Claude, Codex, or another design tool in an existing application. Translate the handoff into working UI and preserve existing behavior. A request solely to inspect rendered UI belongs to visual QA.
---

# Design to Code

Use the approved handoff for appearance and intended interaction. Learn what the running application and its contracts already do before changing the markup, layout, or controls.

## Inputs

- Approved screens or states, assets the team can use, and any specified responsive, theme, or interaction variants.
- The existing route or screen, nearby components, and the behaviors and data contracts that must survive.

## Workflow

1. Map the handoff to the application. For each affected screen or meaningful state, identify the reference, component and style owners, data source, action handler, and acceptance check. Separate specified behavior from inferences. If the reference omits an existing action, preserve it unless removal is authorized. Resolve a conflict with product or accessibility requirements before changing that behavior.
2. Inspect generated HTML or prototype code as reference material. Rebuild with the application's components and styling conventions. Keep demo data, mock persistence, and prototype scripts outside production paths. Reuse approved assets and tokens. Ask for a usable reference or asset when its absence blocks a faithful choice.
3. Implement a complete interaction through its existing owners. Match hierarchy, type, spacing, surfaces, and alignment with the actual content and constraints. Use shared defaults for rules that apply to their consumers and local styles for real exceptions. Align the responsive layout to the content and specified variants. Keep semantic controls, visible focus, labels and errors, touch reachability, and appropriate motion preferences.
4. Wire each in-scope action to its existing operation. Carry forward loading, pending, error, empty, and disabled states where relevant. Keep edits intact across resize or layout changes and preserve validation, cancellation, permissions, and save timing. Use an isolated fixture to exercise a write or failure when that scenario needs controlled data.
5. Check the running result against the relevant approved states. Include the reported viewport and a narrower or breakpoint-adjacent case where layout can change. Check a meaningful interaction, keyboard or touch access, and affected consumers of any changed shared component. Use the repository's focused checks for behavior changes.

## Output

Summarize the implemented states, the existing behavior preserved, and any intentional design differences and why they were needed. Include the checks actually performed and any manual acceptance still pending.

## Example

Fictional example: A prototype replaces an account form with a two-column layout and omits an existing reset action. Keep reset reachable, implement the new layout through existing fields, and verify narrow stacking, error focus, and the current save/cancel behavior with a test account.

## Verification and limits

A static frame cannot establish an interaction or API contract. A screenshot of the reference or an isolated component does not verify the integrated route. Report which rendered states, interactions, or platforms were unavailable.
