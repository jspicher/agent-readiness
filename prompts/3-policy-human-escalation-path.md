[Readiness Fix] <REPO_NAME> Human Escalation Path

Fix the failing signal: Human Escalation Path ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Human Escalation Path
**Score**: [0/1]
**Description**: Documented handoff with sufficient context for a human to take over when the agent gets stuck, exceeds its competence, or hits a permission boundary it cannot cross alone
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Human escalation path — check for a checked-in, agent-readable contract that tells the agent (a) WHEN to stop and ask, (b) WHAT to write in the handoff, and (c) WHERE the handoff lands so a human will actually see it. PASS requires at least one of the following, with a concrete template and a routing mechanism (not just a sentence saying "ask if stuck"):

1. **Handoff template file** at a discoverable path — `escalate-to-human.md`, `.github/HANDOFF_TEMPLATE.md`, `docs/handoff-template.md`, or a `handoff/` skill referenced from `AGENTS.md` / `CLAUDE.md`. The template MUST require the agent to fill in: (a) the goal it was working on, (b) what it tried (commands run, files touched, hypotheses tested), (c) where it got stuck (exact error, line number, failing test name), (d) suspected cause, (e) a minimal reproducer or `git diff`, and (f) one concrete suggested next step or open question. A template with only "describe the problem" is a stub.
2. **PR-description handoff convention** — `.github/pull_request_template.md` (or a stack-specific variant) includes a `## Needs human input` / `## Blocked on` section and the agent is instructed (via `AGENTS.md` / `CLAUDE.md`) to open the PR as a draft with `[NEEDS-HUMAN]` in the title (or apply a `needs-human-review` label) whenever it cannot complete the task. The convention is enforceable only if both the template field AND the agent instruction exist.
3. **Auto-filed GitHub issue on block** — a `Stop` / `SubagentStop` / `Notification` hook (Claude Code) or `Stop` hook (Factory droid) that runs `gh issue create --label needs-human --body-file .claude/handoff.md` when the agent terminates with an unresolved task. The hook must be wired in committed settings, not local overrides.
4. **`PermissionRequest` / `Notification` hook that routes to a channel a human monitors** — Slack DM, Telegram message, push notification, or email when the agent is waiting on approval or has marked itself blocked. The channel MUST be one a human actually watches (not a #bot-noise firehose nobody opens); the hook MUST include a link or path to the handoff context, not just "Claude needs you".
5. **Claude Agent SDK `canUseTool` callback** (for repos that embed the SDK) that routes unknown-tool requests to a human approval queue with the call context attached. A `canUseTool` that auto-denies everything is not escalation; one that auto-approves everything is the opposite of escalation. Both FAIL.

Also verify the path is wired end-to-end:
- The template must be referenced from `AGENTS.md` / `CLAUDE.md` (or surfaced as a slash command) so the agent discovers it. A template nobody tells the agent to read is dead weight.
- The destination must be monitored. A handoff that lands in `.claude/handoff.md` is fine ONLY if a human checks that file (or a hook posts a notification when it changes). A handoff dropped into `/tmp/` or a closed-PR draft is invisible.
- For PR-based handoffs, the draft state + `needs-human-review` label combo is what gets it onto a reviewer's dashboard; just opening a draft PR with no label and no `@mention` is not escalation.

A README sentence saying "the agent should ask for help when stuck" is documentation, not a path, and FAILs this signal. A `CONTRIBUTING.md` that explains how human contributors escalate is also not enough — the signal evaluates the agent's escalation surface, not the human's.

## Your Task

1. Explore the repository to understand the current state related to this signal:
   - Search for existing handoff/escalation artifacts: `escalate*.md`, `handoff*.md`, `HANDOFF*`, `.github/pull_request_template*`, `.github/ISSUE_TEMPLATE/*`, any `AGENTS.md` / `CLAUDE.md` section about getting stuck.
   - Open `.claude/settings.json`, `.factory/settings.json` and list any `Stop`, `SubagentStop`, `Notification`, `PermissionRequest` hooks already wired.
   - Identify the team's actual notification surface — is there a Slack workspace? A Telegram group? Do reviewers watch GitHub PR drafts? Pick the destination a human will actually see; do not invent a channel.
   - Note which runtime(s) the repo targets (Claude Code, Factory droid, Agent SDK embed) — the wiring differs.
2. Make **substantive improvements** by creating both a template AND a routing mechanism:
   - Add `escalate-to-human.md` (or `.github/HANDOFF_TEMPLATE.md`) with the six required fields below. Each field must be a heading the agent fills in, not a prose paragraph the agent might skip.
   - Reference the template from `AGENTS.md` / `CLAUDE.md` under a section like `## When to escalate` with explicit triggers (3+ failed attempts on the same error, a `git push` denied by policy, a destructive op outside its allowlist, a missing credential, an ambiguous spec).
   - Extend `.github/pull_request_template.md` with a `## Needs human input` section so the agent can hand off mid-PR.
   - Wire ONE routing hook so the handoff reaches a human: either (a) a `Stop` hook that opens a draft PR / GitHub issue with the handoff body, or (b) a `Notification` / `PermissionRequest` hook that pings Slack/Telegram with a link to the handoff file. Pick whichever matches the team's existing notification surface.
3. Verify the path actually delivers:
   - Trigger the hook manually (simulate a `Stop` payload with `echo '{"stop_hook_active":false}' | $CLAUDE_PROJECT_DIR/.claude/hooks/escalate.sh` or equivalent) and confirm the notification lands or the issue/PR is created.
   - Open the resulting draft PR / issue / Slack message and confirm a reviewer could pick up the task cold from the handoff alone — if they cannot, the template is missing fields.
4. Keep changes focused on this signal — do not refactor unrelated CI or PR conventions.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** template with only "describe the problem" or a single freeform textarea. The agent will fill it with "I got stuck" and nothing else. Required fields force structure.
- **NO** handoff that lands in a private channel, a closed branch, or a developer's DMs unless that destination is explicitly the team's escalation surface. The signal is about a discoverable, monitored path — not a backchannel.
- **NO** routing the notification to a Slack channel that already firehoses bot output (`#ci`, `#deploys`, `#claude-noise`). The signal is lost in the noise. Pick a low-volume channel humans actually read, or `@mention` a specific reviewer.
- **NO** `Stop` hook that opens an issue / PR on EVERY session end. Only escalate when the agent self-marks blocked (e.g., touches `.claude/blocked.flag`, exits non-zero, or the handoff file's `status` field is `blocked`). Otherwise you spam the issue tracker and humans tune the signal out within a week.
- **NO** PR description marked `[NEEDS-HUMAN]` with an empty body. The label without context is worse than no label — it trains reviewers to ignore the marker.
- **NO** handoff template the agent is never told about. If `AGENTS.md` / `CLAUDE.md` does not reference the file and does not list the escalation triggers, the agent will not use it.
- **NO** "ask for help" instruction with no concrete trigger. "Ask if you're unsure" is uncalibrated — the agent is always somewhat unsure. Use measurable triggers: N retries, M minutes, specific error classes, specific tool denials.
- **NO** `canUseTool` callback that auto-denies (blocks all progress, not escalation) or auto-approves (eliminates the boundary entirely). The callback must route to a human queue with context.
- **NO** handoff template that asks the agent to dump the entire transcript. The reviewer will not read 4000 lines. Force a summary + a pointer to the transcript path.

Examples of BAD fixes:
- Adding `escalate-to-human.md` containing only `# When stuck\n\nDescribe what happened.` — no fields, no routing, no agent instruction. The signal stays failed.
- A `Stop` hook that runs `gh issue create --title "Claude finished"` on every session end with no body and no condition. Within a day the repo has 50 noise issues and the maintainer disables the hook.
- Adding `[NEEDS-HUMAN]` to the PR title from a script with no requirement that the agent fill the `## Needs human input` section. Reviewers see the marker, open the PR, find an empty section, and learn to ignore the marker.
- A `Notification` hook that pings `#general` with `"Claude needs input"`. No link to the file, no summary, no `@mention`. Nobody clicks through.
- A template with one field: `## Problem` (multiline). The agent writes `I cannot get the test to pass` and stops. Useless to the human.
- Documenting escalation in `CONTRIBUTING.md` for human contributors and calling it done — the agent does not read `CONTRIBUTING.md` and the signal evaluates the agent's surface.
- A `canUseTool` callback that `return { behavior: "deny", message: "not allowed" }` on every unknown tool — the agent is blocked, not escalated. There is no human in the loop.

Examples of GOOD fixes:

**1. Handoff template — `escalate-to-human.md`** (referenced from `AGENTS.md`):

```markdown
# Escalate to Human

Use this template when you cannot complete the task autonomously. Fill in every section. Empty sections force the reviewer to ask follow-up questions, which defeats the point.

## Goal
<One sentence: what the user / ticket asked for. Link to the issue or spec.>

## What I tried
<Bulleted list. Each bullet: command run + outcome. Example:>
- `pnpm run test packages/auth` -> 3 failures in `oauth.test.ts`
- Edited `src/auth/oauth.ts:142` to add nullish check -> 2 failures remain
- Rolled back the edit and tried `git bisect` -> failure first appeared in commit `abc1234`

## Where I'm stuck
<Exact error, file:line, failing test name. Paste the smallest stack trace that shows the problem. Do NOT paste the entire log.>

## Suspected cause
<One paragraph. If you have no hypothesis, say so explicitly — that itself is useful information.>

## Reproducer
<Either a minimal `git diff`, a single failing command, or "checkout branch X and run Y". The reviewer must be able to reproduce in under 2 minutes.>

## Suggested next step OR open question
<Pick one:
- "Try X" with a concrete change you would make if you had permission.
- "Need decision on Y" with the options you considered and the tradeoffs.>

## Pointers
- Transcript: <path or session id>
- Branch: <branch name>
- Related files: <up to 5 paths>
```

**2. `AGENTS.md` section** (so the agent discovers the template):

```markdown
## When to escalate to a human

Stop and write a handoff to `escalate-to-human.md` when ANY of these triggers fire:

- 3 consecutive failed attempts at the same error or test
- A `Bash`, `Write`, or MCP tool call is denied by the permission policy and you cannot work around it
- A required credential or env var is missing and not documented
- The spec is ambiguous in a way that affects the data model, API surface, or user-facing behavior (NOT cosmetic ambiguity)
- You have spent more than 30 minutes on one sub-task with no measurable progress
- A destructive operation (DB migration, force-push, prod deploy, `rm -rf` outside `node_modules`) would be required

When a trigger fires:
1. Fill in every section of `escalate-to-human.md`. Do not leave fields blank.
2. Touch `.claude/blocked.flag` so the `Stop` hook routes the handoff.
3. Stop. Do not continue speculating.
```

**3. PR template extension — `.github/pull_request_template.md`**:

```markdown
## Summary
<what changed and why>

## Test plan
- [ ] <command and expected outcome>

## Needs human input
<Delete this section if the PR is complete. Otherwise:>
- **Blocked on**: <one sentence>
- **Decision needed**: <the specific question, with the options you considered>
- **Handoff context**: see `escalate-to-human.md` in this branch
```

If the PR is opened with the `Needs human input` section non-empty, the agent MUST open it as a draft and add the `needs-human-review` label (`gh pr create --draft --label needs-human-review`).

**4. `Stop` hook that routes only when blocked** — `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/escalate-if-blocked.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/escalate-if-blocked.sh` (chmod +x):

```bash
#!/usr/bin/env bash
# Stop hook: route handoff to a human ONLY if the session self-marked blocked.
set -euo pipefail
FLAG="${CLAUDE_PROJECT_DIR:-.}/.claude/blocked.flag"
HANDOFF="${CLAUDE_PROJECT_DIR:-.}/escalate-to-human.md"

[ -f "$FLAG" ] || exit 0
[ -f "$HANDOFF" ] || { echo "blocked.flag set but handoff missing" >&2; rm "$FLAG"; exit 0; }

BRANCH=$(git -C "${CLAUDE_PROJECT_DIR:-.}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
TITLE="[NEEDS-HUMAN] $(head -1 "$HANDOFF" | sed 's/^# *//')"

# File issue with handoff body; tag the on-call reviewer.
gh issue create \
  --title "$TITLE" \
  --body-file "$HANDOFF" \
  --label "needs-human-review" \
  --assignee "@me" \
  >> "${CLAUDE_PROJECT_DIR:-.}/.claude/escalation.log" 2>&1

# Optional: ping Slack with a link to the issue
if [ -n "${SLACK_ESCALATION_WEBHOOK:-}" ]; then
  ISSUE_URL=$(tail -1 "${CLAUDE_PROJECT_DIR:-.}/.claude/escalation.log")
  curl -s -X POST -H 'Content-Type: application/json' \
    -d "{\"text\":\"Agent escalation on \`$BRANCH\`: $ISSUE_URL\"}" \
    "$SLACK_ESCALATION_WEBHOOK" >/dev/null || true
fi

rm "$FLAG"
```

**5. Optional — `canUseTool` callback for SDK embeds** (only if the repo uses `@anthropic-ai/claude-agent-sdk`):

```ts
import { query, type CanUseTool } from "@anthropic-ai/claude-agent-sdk";

const canUseTool: CanUseTool = async (toolName, input) => {
  // Allow read-only and known-safe tools without prompting.
  if (["Read", "Grep", "Glob"].includes(toolName)) {
    return { behavior: "allow", updatedInput: input };
  }
  // Everything else: queue for human approval and attach context.
  const approvalId = await escalationQueue.push({
    tool: toolName,
    input,
    sessionId: process.env.CLAUDE_SESSION_ID,
    handoffPath: ".claude/pending-approval.md",
  });
  await notifySlack(`Approval needed: ${toolName} — ${approvalUrl(approvalId)}`);
  const decision = await escalationQueue.await(approvalId, { timeoutMs: 15 * 60_000 });
  return decision.approved
    ? { behavior: "allow", updatedInput: decision.input ?? input }
    : { behavior: "deny", message: decision.reason ?? "human declined" };
};

for await (const msg of query({ prompt, options: { canUseTool } })) { /* ... */ }
```

The callback fires only for tools not auto-approved by allow rules — it is the runtime backstop, not the first line of defense.

## Why this matters

The failure mode is quiet: an agent runs for hours, hits a wall it cannot cross (denied permission, missing credential, ambiguous spec), and either silently gives up, infinitely retries the same broken command, or — worst case — invents a plausible-looking but wrong workaround and commits it. Practitioners running unsupervised `--resume` sessions in 2026 reported agents blocking for hours on a single permission prompt nobody saw, because Claude Code's permission prompts are local-terminal-only and the operator was AFK. The fix that worked was a `PermissionRequest` / `Notification` hook routing to phone push or Slack, paired with a structured handoff file so the human returning to the terminal had enough context to decide in seconds instead of re-reading the entire session. Without an escalation path, every long-running agent is one ambiguous spec away from either burning hours on retries or shipping a wrong answer with confidence. The handoff template is the warm-transfer; the routing hook is what makes the warm-transfer arrive.

The signal is at L3 because L1/L2 readiness assumes a human is watching the terminal; L3 readiness assumes the agent runs unsupervised long enough to hit a boundary, and the repo must define what happens when it does.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed: which template file, which routing mechanism, where the escalation triggers are documented, and how you verified the path delivers (e.g., "touched `.claude/blocked.flag`, ran `Stop` hook manually, confirmed GitHub issue created with handoff body and `needs-human-review` label")

## References

- Claude Agent SDK `canUseTool` callback (runtime tool approval routing): https://docs.claude.com/en/api/agent-sdk/permissions
- Claude Agent SDK handle approvals and user input (`AskUserQuestion`, `canUseTool` integration): https://platform.claude.com/docs/en/agent-sdk/user-input
- Claude Code hooks reference (`Stop`, `SubagentStop`, `Notification`, `PermissionRequest` payloads): https://code.claude.com/docs/en/hooks
- Practitioner writeup — "Claude Code kept getting stuck while I was AFK — here's how I fixed it with hooks" (PermissionRequest -> push notification pattern): https://medium.com/@microwalks/claude-code-kept-getting-stuck-while-i-was-afk-heres-how-i-fixed-it-with-hooks-90e1f15f7ca7
- Reference handoff skill (`/handoff` slash command, HANDOFF.md create/update flow): https://github.com/ykdojo/claude-code-tips/blob/main/skills/handoff/SKILL.md
- Reference handoff repo (cross-tool agent handoff documents): https://github.com/willseltzer/claude-handoff
- Spec-driven handoff workflow for humans and AI agents (`AGENTS.md`-anchored): https://github.com/NihilDigit/handoff
- HumanLayer — human-in-the-loop approval/escalation framework for AI agents: https://www.humanlayer.dev/
- Augment Code — Agent Handoff Patterns (approval / input / escalation taxonomy): https://www.augmentcode.com/guides/agent-handoff-patterns-human-agent-interface
- AutoGen Handoffs design pattern (multi-agent + human-agent transfer of control): https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/handoffs.html
- GitHub issue — `PermissionRequest` hook subagent gap (known limitation when escalating from Task tool subagents): https://github.com/anthropics/claude-code/issues/23983
</system-reminder>
