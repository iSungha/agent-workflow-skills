# Contributing

Contributions should improve a reusable workflow for agents across projects. Before adding files, explain the failure or repeated task the change addresses and why the existing skills do not cover it.

Keep the skill instructions focused. Separate evidence collection from interpretation, identify which checks are mechanical and which require judgment, and state the workflow's limits. Examples must be synthetic, clearly labeled, and small enough to review. Do not include personal data, private project names, customer information, credentials, internal prompts, or implementation details that are not yours to release.

Avoid new dependencies and infrastructure for documentation-only changes. If you add executable tooling, include a focused test of its behavior, document its requirements, and show how it handles missing or malformed input. Do not claim test, performance, adoption, or production results without reproducible evidence.

Before proposing a contribution, run the package checks from the repository root:

```powershell
python -m unittest discover -s tests -v
```

If the Agent Skills validator is available in your environment, run it for every changed skill as well. A metadata validator does not verify factual quality or privacy. Review the full diff and every included example separately.
