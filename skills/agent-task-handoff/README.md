# Agent Task Handoff

> **For agents:** Follow the adjacent [SKILL.md](SKILL.md) for the workflow.

## What it helps you do

Turn a rough development request into a short, reviewable prompt that a coding agent can execute in a fresh conversation. Use it before implementation when the task needs clearer scope, acceptance criteria, or approval boundaries.

Bring the request and any evidence that changes the task, such as a reproduction, a design, or a decision the repository does not record. The Driver drafts the prompt. Review it, then give it and any referenced attachments to an Executor in the target workspace. For implementation, use the relevant engineering skill if one is installed.

## Model and effort

Verified against official documentation on **2026-11-21**. The table gives this project's suggested starting points. Check your client's model picker and supported settings before use. Claude model aliases can resolve differently by provider, and some Claude surfaces may manage effort for you.

| Role | Suggested start | When to escalate |
| --- | --- | --- |
| OpenAI/Codex Driver | GPT-6.2 Sol, low reasoning | Try medium when several constraints interact. Consider GPT-6.2 Astra at medium for architecture trade-offs the user needs help resolving. |
| OpenAI/Codex Executor | GPT-6.2 Sol, medium reasoning | Try high for a difficult diagnosis with clear scope. Consider GPT-6.2 Astra at medium for complex changes spanning several parts of the system. |
| Claude Driver | Claude Sonnet 5.5, low effort where selectable | Try medium when the prompt must reconcile competing requirements or several evidence sources. |
| Claude Code Executor | Claude Sonnet 5.5, medium effort | Try high for subtle bugs or edge cases with stronger verification needs. Consider Claude Opus 5.5 at medium for harder architectural reasoning. |

Select the model and effort in the client when possible. Keep the lightest setting that produces a usable, verifiable result for similar tasks. Resolve missing evidence or unclear requirements before spending more tokens on reasoning. Higher effort can add latency and cost, and does not reliably improve every result.

## Fictional example

**Rough request.** "In the existing profile form, a second click on Save can send another request if the first one is slow. Fix it locally, keep the current save and error behavior, and show me how you checked it."

**Executor prompt**

> In the current repository, fix duplicate submissions from the existing profile form when Save is clicked again while a save is pending. Follow the applicable repository instructions and confirm where submission is handled before editing.
>
> Keep the change focused on the form's submission behavior. During a pending save, repeated clicks must produce only one request. After a failed save, the existing error feedback must appear and the user must be able to retry. A normal successful save must still work.
>
> Use the relevant existing check or reproduce these cases with a delayed response in a local environment. Report what changed, the checks you ran, and anything you could not verify. Stop with a local diff for review.

**Suggested settings.** Use Sol at low reasoning or Sonnet 5.5 at low effort for the Driver. Start the Executor at medium on Sol or Sonnet 5.5. Escalate if reproduction shows the duplication crosses multiple parts of the system.

## Sources and workflow choices

**Documented guidance**

- OpenAI recommends concise skill triggers, task-relevant context, and a clear definition of completion. Its Codex Cookbook illustrates how to record scope, observable acceptance criteria, verification, and approval boundaries for larger development workflows. [OpenAI's skill and prompt guidance][openai-prompts], [Codex Cookbook workflow example][codex-workflows].
- OpenAI identifies Sol as a starting model for most Codex work and Astra for complex projects. Its model guide illustrates Sol at medium for routine coding and recommends comparing settings on real tasks. [OpenAI model selection][openai-models].
- Anthropic recommends supplying context Claude cannot readily discover and an observable check. Its guide illustrates starting a fresh session to implement a specification. The model documentation explains available Claude Code models, effort levels, and their trade-offs. [Claude Code best practices][claude-practices], [Claude Code model configuration][claude-models].

**Project design.** The Driver and Executor roles, compact prompt, and role-specific starting settings are this skill's design. Separate sessions make the responsibilities and transferred context explicit. Accuracy still depends on the evidence, implementation, and verification.

[openai-prompts]: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
[openai-models]: https://developers.openai.com/api/docs/guides/model-selection
[codex-workflows]: https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex
[claude-practices]: https://code.claude.com/docs/en/best-practices
[claude-models]: https://code.claude.com/docs/en/model-config
