---
name: mobile-ui-engineering
description: Use when implementing or fixing native or cross-platform mobile screens, navigation, sheets, gestures, adaptive layout, accessibility, or app lifecycle behavior. Apply iOS and Android conventions through the app's existing components and runtime.
---

# Mobile UI Engineering

Treat navigation, input, lifecycle, and accessibility as parts of the screen's behavior. Reuse the native application's owners for these concerns.

## Inputs

- The affected screen, supported platforms, reference states if supplied, and current navigation and data contracts.
- The existing development build, simulator or device access, and relevant screen or integration fixtures.

## Workflow

1. Trace the screen into its route, shared primitives and tokens, state owner, and API action. Map each visible control to a real operation, an honest disabled state, or a scoped demo. Resolve platform or contract conflicts without letting prototype data decide what the app saves.
2. Adapt layout to available content space, safe areas, keyboard, orientation, and text scaling. Reuse native roles, accessible names, visible errors, and established focus behavior. Provide a visible or accessible alternative to gesture-only actions. Keep scrollable content and fixed actions operable as constraints change.
3. Check navigation and dismissal paths together. Preserve Back, deep links, modal or sheet dismissal, and state restoration where supported. Keep sheet-local edits isolated until Apply or Save, and keep dirty work on accidental dismissal according to the product contract. Prevent a row swipe from triggering its tap action. Request permissions in context and handle denial and reentry from system settings.
4. Separate transient screen state from data that should survive navigation or process recreation. Use existing restoration and secure persistence mechanisms for their intended lifetimes. Guard late results after route or account changes. Release screen-owned listeners, timers, and media when their lifecycle ends. For slow lists or transitions, measure on a representative build before changing rendering or caching.
5. Exercise a real native screen for high-risk interactions. Select device or simulator conditions that expose the issue, such as larger text, a visible keyboard, or a short viewport. Verify the relevant platform-specific navigation and assistive inputs where available, along with applicable focused tests. Use isolated data for state-changing scenarios.

## Output

Report the screen and interaction changes, OS and device or simulator used, relevant display and input settings, and observed states. Separate platform coverage from fixture and build results.

## Example

Fictional example: A delivery preferences sheet hides Save behind the keyboard, and tapping Back can discard a draft. Use the app's keyboard-aware sheet and dirty-state handler. Verify scrolling to Save with larger text, unchanged dismissal, and the dirty confirmation on supported targets.

## Verification and limits

An exported bundle, browser preview, or screenshot verifies a narrower claim than a native interaction run. Simulator results can miss hardware, keyboard, performance, and assistive technology differences. State which platforms and lifecycle transitions were exercised.
