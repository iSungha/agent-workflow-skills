---
name: agent-task-handoff
description: Turn a rough software development request into a self-contained execution prompt for Codex or Claude Code. Use when asked to refine a coding prompt or prepare a task handoff.
---

# Agent Task Handoff

Work as the Driver. Clarify the request and return a prompt for the user to review. Leave implementation to the Executor.

Use this skill for a prompt or handoff deliverable. Direct coding requests belong to the relevant implementation workflow.

## Inputs

- The user's request, target repository or workspace if known, and preferred agent if specified.
- Relevant evidence already available, such as an issue, reproduction, design, repository instructions, or a prior decision.
- Any constraints, actions already authorized, and checks the user expects.

## Workflow

1. Identify the outcome and what must stay intact. Separate user requirements and observed evidence from assumptions. Ask one focused question only if an essential decision blocks a meaningful prompt. Otherwise, state any assumption that affects scope or acceptance.
2. Carry forward only context that changes the work. Include verified paths, decisions, evidence, and reproduction steps when available. Point the Executor to applicable project instructions, such as `AGENTS.md` or `CLAUDE.md`, and to relevant installed skills or existing codebase knowledge where available. Use targeted read-only checks when needed to ground a material fact. Leave unknown repository details for the Executor to confirm.
3. Write the prompt so it works in a fresh conversation. State the objective, scope, relevant non-goals, and what the user should be able to observe when it is done. Ask the Executor to follow repository instructions, reuse evidence, investigate the root cause when it is unknown, make focused changes, and verify the result through its normal entry point. Name a check or command only when supported by supplied evidence or the repository. Otherwise, describe the behavior to check and have the Executor identify the relevant existing check.
4. Carry forward the user's approval boundaries. Distinguish authorized work from actions requiring separate approval. Treat unrelated refactoring as outside scope. Require explicit authorization for deployment, merging, destructive actions, and any publishing steps outside the request. A prompt draft does not grant permissions.

## Output

Return one copy-ready Executor prompt, with any material assumptions clearly marked. Ask the user to review it and paste the approved prompt into a separate Codex or Claude Code conversation opened in the target workspace. Include or identify any necessary attachments the Executor can access. Ask the Executor to report what changed, which checks actually ran and their results, and any remaining limitations.

Use the [dated matrix in the README](README.md#model-and-effort) to suggest starting settings for the target client. Keep settings outside the copy-ready prompt and account for the user's available options and budget.

## Example

See the [fictional Save button handoff](README.md#fictional-example) for a rough request, refined prompt, and settings recommendation.

## Verification and limits

Read the handoff as if the Driver conversation were unavailable. Check that references resolve or are called out as missing, acceptance criteria can be observed, and scope and permissions match the request. Separate conversations help manage context and responsibilities. They cannot guarantee accuracy or eliminate hallucinations. The Executor still needs to check the current repository and verify the outcome.
