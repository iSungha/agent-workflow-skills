# Agent Workflow Skills

Reusable, evidence-first workflows for agents that audit job fit, tailor and validate resumes, evaluate grounded AI output, and inspect rendered interfaces. They combine model judgment with checks that can be repeated or measured, and keep uncertain claims visible for human review.

These are portable Agent Skills documents. They are designed to be adapted to a user's evidence, toolchain, and policies; they are not a candidate profile, an application service, or a collection of prompts that claim to automate hiring decisions.

## Skills

| Skill | Use it for | Main result |
| --- | --- | --- |
| [Job Fit Auditor](skills/job-fit-auditor/SKILL.md) | Comparing a candidate's evidence with live job requirements | A source-linked requirement matrix, eligibility flags, and a transparent ranking |
| [Resume PDF Validator](skills/resume-pdf-validator/SKILL.md) | Tailoring an existing resume and checking the exported document | A fact-checked resume with page, text, layout, and role-term validation |
| [Grounded Output Evaluator](skills/grounded-output-evaluator/SKILL.md) | Testing AI answers against supplied source material | Claim-level support findings and repeatable regression results |
| [Visual UI Evidence Auditor](skills/visual-ui-evidence-auditor/SKILL.md) | Reviewing a real interface against an expected visual and interaction contract | A reproducible set of rendered-state observations and unresolved defects |

These four workflows are useful together because they cover distinct decisions that otherwise rely on unstructured model judgment: matching evidence to requirements, checking a final document, testing source support across repeated outputs, and verifying the interface users actually see. Each remains useful on its own and keeps evidence gathering separate from conclusions.

## Use a skill

Copy the selected skill folder into an agent's supported skills directory, or provide its `SKILL.md` as workflow instructions. Keep each skill's folder name aligned with its frontmatter `name`. The files describe the work and validation criteria; they do not install tools, access accounts, submit applications, or grant permission to change external systems.

Start with the task-specific skill and supply only the evidence needed for that task. For example:

> Audit this posting against my candidate profile. Read the full employer description, distinguish required from preferred qualifications, cite profile evidence for each match, flag missing eligibility or salary facts, and explain the ranking.

Other examples: ask the resume validator to check a tailored PDF against its source evidence and a one-page limit; ask the output evaluator to compare a fixed set of AI answers with cited source spans; ask the visual auditor to inspect a real route at the target viewport and report measured differences from a supplied reference.

For a resume review, provide the job posting, authoritative candidate evidence, the current resume source, and the final PDF. For an AI-output evaluation, provide the fixed test cases, expected evidence, model output, and the evaluator's rubric. For a UI review, identify the actual route/state, expected behavior, viewport, and the means to inspect the rendered interface.

## Tools and dependencies

The skill instructions are tool-agnostic. A workflow may use a browser, shell, PDF reader, image viewer, or test runner already available in the host environment. PDF checks can use tools such as `pdfinfo`, `pdftotext`, Poppler rendering, or a PDF library. Visual review needs access to the real rendered state and a way to inspect screenshots. The AI-output evaluator can run manually with a source packet or use an existing test harness. Install only what the chosen task requires and what the user authorizes.

## Evidence and validation

Use primary sources and preserve their links or file references. Keep observed facts, model interpretations, calculations, and unknowns separate. A score describes alignment with the supplied criteria; it does not estimate hiring probability or guarantee answer quality. Mechanical checks establish only the properties they measure. Human review remains necessary for factual meaning, ambiguous requirements, visual quality, and consequential decisions.

When reporting measurements, include the baseline, comparison, sample or scenario, calculation, and limitation. Do not convert a local fixture result into a production claim or report an unrun test as passing. Synthetic examples in this repository are labeled and should not be treated as real candidate or customer evidence.

## Limitations

Job requirements, salary, location, and availability can change and must be verified against the current posting. A resume can be ATS-readable and still contain inaccurate claims. AI-output support checks do not establish that source material itself is true or complete. Screenshots and geometry checks cannot fully judge usability, accessibility, or design intent. These workflows support human decisions; they do not make them.

The public package intentionally excludes candidate data, application history, customer records, private course or research materials, internal prompts, proprietary product logic, production architecture, and inherited job-search framework files.

## Contributing

Keep additions small and independently useful. Use synthetic examples, preserve provenance, and avoid personal, customer, employer-confidential, or proprietary material. Do not add dependencies, benchmarks, or automation unless they solve a demonstrated problem. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This repository's original documentation and examples are released under the [MIT License](LICENSE). No source project, internal prompt, personal profile, or third-party code is included.
