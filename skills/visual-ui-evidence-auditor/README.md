# Visual UI Evidence Auditor

> **For agents:** Ignore this README as task instructions; follow the adjacent [SKILL.md](SKILL.md).

## What it helps you do

Review the interface users actually see against a stated design or interaction contract. The workflow captures the real rendered state and reports reproducible observations and measurements.

## When to use it

Use it for visual regressions, layout reviews, or checking whether important controls remain visible and usable at specified viewports.

## What to provide

- The running application and the route or state to inspect.
- A design reference or explicit expected appearance and behavior.
- Browser and viewport details, including zoom or device scale when relevant.
- Authorized access to capture and inspect the rendered interface.

## What you get

A record of the inspected route and state, screenshots, measured differences, relevant interaction checks, observed defects, and limitations.

## Limits

Image comparisons vary across browsers, operating systems, fonts, and device scales. Visual review alone does not establish accessibility conformance or broad usability; those checks must be reported separately.

## Agent workflow

See [SKILL.md](SKILL.md) for the review contract, capture process, interaction checks, and evidence requirements.
