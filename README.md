# Agent Workflow Skills

Reusable, evidence-first workflows for agents that build and review software, evaluate grounded AI output, and work with job application evidence. Each workflow ties its conclusions to checks that can be repeated or reviewed.

These portable Agent Skills work with Codex and other compatible coding agents. Adapt them to the project's tools and instructions. Each skill folder has a human-facing `README.md` and an agent-facing `SKILL.md`.

## Software Engineering Skills

| Skill | Use it for | Main result |
| --- | --- | --- |
| [Design to Code](skills/design-to-code/README.md) | Implementing an approved handoff in an existing application | Working UI that follows the design and preserves application behavior |
| [Frontend Engineering](skills/frontend-engineering/README.md) | Building or fixing components, state, forms, routing, and API integration | A focused change with explicit ownership and behavior checks |
| [Frontend Refactoring](skills/frontend-refactoring/README.md) | Addressing coupling, duplicated policy, or unclear style and state ownership | A structural change with evidence that existing behavior still works |
| [Backend Engineering](skills/backend-engineering/README.md) | Designing or changing APIs, services, data writes, and background jobs | Explicit authorization, persistence, and recovery behavior with boundary checks |
| [Mobile UI Engineering](skills/mobile-ui-engineering/README.md) | Implementing native and cross-platform screens, navigation, and interactions | Working mobile UI with device and platform coverage recorded |
| [Visual UI Evidence Auditor](skills/visual-ui-evidence-auditor/README.md) | Independently reviewing rendered UI against visual and interaction requirements | Reproducible observations, measurements, defects, and unverified states |

## Other Agent Skills

| Skill | Use it for | Main result |
| --- | --- | --- |
| [Job Fit Auditor](skills/job-fit-auditor/README.md) | Comparing a candidate's evidence with live job requirements | A source-linked requirement matrix, eligibility flags, and a transparent ranking |
| [Gmail Application Index](skills/gmail-application-index/README.md) | Building or refreshing an evidence-backed Gmail application history | A durable, account-bound index with sourced events, action state, and scan coverage |
| [Resume PDF Validator](skills/resume-pdf-validator/README.md) | Tailoring an existing resume and checking the exported document | A fact-checked resume with page, text, layout, and role-term validation |
| [Grounded Output Evaluator](skills/grounded-output-evaluator/README.md) | Testing AI answers against supplied source material | Claim-level support findings and repeatable regression results |

Choose Design to Code when an approved handoff drives the implementation, Frontend Engineering when the task changes application behavior, or Frontend Refactoring when the task changes structure while preserving behavior. Mobile UI Engineering covers native runtime and platform behavior. Use the Visual UI Evidence Auditor when the deliverable is a review of a rendered interface. Each skill can be used independently.

## Use a skill

Copy the selected skill folder into an agent's supported skills directory, or provide its `SKILL.md` as workflow instructions. Keep each skill's folder name aligned with its frontmatter `name`. The files describe the work and validation criteria; they do not install tools, access accounts, submit applications, or grant permission to change external systems.

Start with the task-specific skill and supply only the evidence needed for that task. For example:

> Audit this posting against my candidate profile. Read the full employer description, distinguish required from preferred qualifications, cite profile evidence for each match, flag missing eligibility or salary facts, and explain the ranking.

Other examples: ask the Gmail Application Index to report whether an exact application has a receipt and a later assessment request while distinguishing requested from completed; ask the resume validator to check a tailored PDF against its source evidence and a one-page limit; ask the output evaluator to compare a fixed set of AI answers with cited source spans; ask the visual auditor to inspect a real route at the target viewport and report measured differences from a supplied reference.

For an engineering example, give Design to Code an approved settings layout, the existing route, and the save and cancel behavior to preserve. For a backend reliability change, give Backend Engineering the current operation contract and the expected result of simultaneous or repeated requests.

For a resume review, provide the job posting, authoritative candidate evidence, the current resume source, and the final PDF. For an AI-output evaluation, provide the fixed test cases, expected evidence, model output, and the evaluator's rubric. For a UI review, identify the actual route/state, expected behavior, viewport, and the means to inspect the rendered interface.

## Tools and dependencies

The skill instructions are tool-agnostic. A workflow may use a browser, shell, PDF reader, image viewer, or test runner already available in the host environment. PDF checks can use tools such as `pdfinfo`, `pdftotext`, Poppler rendering, or a PDF library. Visual review needs access to the real rendered state and a way to inspect screenshots. The AI-output evaluator can run manually with a source packet or use an existing test harness. Install only what the chosen task requires and what the user authorizes.

## Recommended Companion Skills & Tools

These optional companions add repository context to the focused implementation and review workflows above. The [Acquire Codebase Knowledge][acquire-codebase-knowledge] and [Context Map][context-map] Agent Skills come from GitHub's [awesome-copilot][awesome-copilot] maintainers. [Codebase Memory MCP][codebase-memory-mcp], maintained by DeusData, is an MCP tool rather than an Agent Skill.

Use them when useful for repository-wide architectural understanding, focused dependency mapping, or reusable codebase context. Reusing that knowledge can reduce repeated file reads, unnecessary token consumption, and isolated fixes that overlook system-wide dependencies. Results depend on the repository, setup, and task; these companions are not requirements and do not guarantee token savings or correctness.

[acquire-codebase-knowledge]: https://github.com/github/awesome-copilot/tree/main/skills/acquire-codebase-knowledge
[context-map]: https://github.com/github/awesome-copilot/tree/main/skills/context-map
[codebase-memory-mcp]: https://github.com/DeusData/codebase-memory-mcp
[awesome-copilot]: https://github.com/github/awesome-copilot

## Evidence and validation

Use primary sources and preserve their links or file references. Keep observed facts, model interpretations, calculations, and unknowns separate. A score describes alignment with the supplied criteria; it does not estimate hiring probability or guarantee answer quality. Mechanical checks establish only the properties they measure. Human review remains necessary for factual meaning, ambiguous requirements, visual quality, and consequential decisions.

When reporting measurements, include the baseline, comparison, sample or scenario, calculation, and limitation. Do not convert a local fixture result into a production claim or report an unrun test as passing. Synthetic examples in this repository are labeled and should not be treated as real candidate or customer evidence.

## Limitations

Job requirements, salary, location, and availability can change and must be verified against the current posting. A resume can be ATS-readable and still contain inaccurate claims. AI-output support checks do not establish that source material itself is true or complete. Screenshots and geometry checks cannot fully judge usability, accessibility, or design intent. These workflows support human decisions; they do not make them.

The public package intentionally excludes candidate data, application history, customer records, private course or research materials, internal prompts, proprietary product logic, production architecture, and inherited job-search framework files.

## Contributing

Keep additions small and independently useful. Use synthetic examples, preserve provenance, and avoid personal, customer, employer-confidential, or proprietary material. Do not add dependencies, benchmarks, or automation unless they solve a demonstrated problem. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This repository's original documentation and examples are released under the [MIT License](LICENSE). The engineering skills use newly written guidance and fictional examples. They draw on general engineering practices without incorporating private playbooks, third-party skill text, scripts, or design assets.
