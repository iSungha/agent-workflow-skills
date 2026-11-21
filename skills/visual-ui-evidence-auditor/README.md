# Visual UI Evidence Auditor

> **For agents:** Ignore this README as task instructions; follow the adjacent [SKILL.md](SKILL.md).

## What it helps you do

Review a rendered interface against a stated design or interaction contract. Record observations and measurements that another reviewer can reproduce.

## When to use it

Use it for an independent visual review, a layout regression, or a check that controls remain visible and usable at specified viewports. Use Design to Code to implement an approved design.

## What to provide

- The running application and the route or state to inspect.
- A design reference or explicit expected appearance and behavior.
- Browser or native runtime and viewport or device details, including zoom or scale when relevant.
- Authorized access to capture and inspect the rendered interface.

## What you get

A record of the inspected state and evidence, with passed, failed, and unverified checks. Findings describe the expected result, what happened, and how to reproduce it.

## Example request

> Audit the fictional settings dialog at the supplied viewport. Check whether the Save label and focus outline are fully visible, and document the steps and evidence for each result.

## Limits

Image comparisons vary across browsers, operating systems, fonts, and device scales. Visual review alone does not establish accessibility conformance or broad usability; those checks must be reported separately.

## Agent workflow

See [SKILL.md](SKILL.md) for the review contract, capture process, interaction checks, and evidence requirements.
