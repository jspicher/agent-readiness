[Readiness Fix] <REPO_NAME> Per-Repo Policy Visibility

Fix the failing signal: Per-Repo Policy Visibility ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Per-Repo Policy Visibility
**Score**: [0/1]
**Description**: The agent can read its own constraints — off-limits paths, approval-required actions, destructive operations — from a checked-in policy file that is loaded into context at session start, BEFORE the agent attempts the action
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Per-repo policy visibility (Pillar 7, L3) — distinct from Tool Allowlist / Permission Policy (#121). #121 asks whether the OS/runtime will DENY a forbidden action. #131 asks whether the agent KNOWS the action is forbidden before it tries — so it can reason about it, ask the user, or pick a different approach instead of hitting an opaque permission wall mid-task. Both matter; a repo can pass #121 and fail #131 (deny list exists, agent has no idea what it says) or pass #131 and fail #121 (agent reads "don't push to main" but nothing actually stops it).

PASS requires ALL of the following:

1. **A checked-in, machine-readable policy file** that enumerates at minimum: (a) off-limits READ paths (credentials, customer data, vendored secrets), (b) off-limits WRITE/EDIT paths (generated code, lockfiles the agent must not regenerate, migration history), (c) actions that require human approval before execution (deploys, force pushes, schema migrations, data backfills, anything irreversible), and (d) destructive operations the agent must refuse outright. Accepted shapes:
   - `AGENTS.md` (or `CLAUDE.md`) with a `## Policy` / `## Constraints` / `## Do Not Touch` section using imperative language ("Never edit `prisma/migrations/**`", not "we generally avoid editing migrations").
   - A dedicated file referenced from AGENTS.md, e.g. `.agent/restricted-paths.md`, `.agent/policy.md`, `docs/agent-policy.md`, or `agent-policy.json`.
   - A JSON/YAML manifest (`agent-policy.json`, `.agent/policy.yaml`) with named arrays: `read_denied`, `write_denied`, `requires_approval`, `forbidden_commands`.

2. **The policy is actually loaded into agent context.** A file the agent never reads is not visibility. Acceptable loaders:
   - Filename the harness reads automatically: `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*.mdc`, `.github/copilot-instructions.md`, `.factory/AGENTS.md`. The policy lives directly in one of these, or the file `@`-references the policy doc (`See @.agent/restricted-paths.md`).
   - A `SessionStart` hook in `.claude/settings.json` that runs a script whose stdout is the policy text (Claude Code injects SessionStart stdout into the conversation as model-visible context).
   - A documented `/memory` import or `--append-system-prompt` invocation in the repo's run scripts.

3. **The policy is consistent with enforcement (#121).** If `agent-policy.json` says "never push to main" but `.claude/settings.json` `permissions` block has no matching `ask`/`deny` rule, the policy is performative. The two should reference each other (AGENTS.md links to the settings file; settings file's deny rules are explained in AGENTS.md).

A FAIL looks like: policy exists only in a private wiki the agent can't fetch; policy is buried in a developer-onboarding doc the harness doesn't load; AGENTS.md describes "what the agent does" (a tour of the codebase) but never says "what the agent must not do"; CLAUDE.md is 4000 lines so the policy section is past the context budget; `agent-policy.json` exists at repo root but no loader references it; policy contradicts `.claude/settings.json` or `.factory/settings.json`.

## Your Task

1. Explore the repository to understand the current state related to this signal:
   - List every `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*`, `.github/copilot-instructions.md`, `.factory/AGENTS.md`, `agent-policy.*`, `.agent/**`, `docs/agent-policy*`, `docs/contributing*` file.
   - Identify the agent harness(es) actually used (Claude Code, Factory droid, Cursor, Copilot, Codex). Check `.claude/`, `.factory/`, `.cursor/`, `.codex/`, plus README mentions.
   - Identify the real off-limits zones for THIS repo: read `.gitignore`, find `secrets/`, `credentials/`, `.env*`, `**/__generated__/**`, `**/migrations/**`, `**/*.lock`, `dist/`, `build/`, vendored deps, customer-data fixtures.
   - Check whether existing `.claude/settings.json` / `.factory/settings.json` permission rules (from signal #121, if it passes) are mirrored anywhere the agent can read.

2. Make **substantive improvements** by writing a real, project-tuned, machine-readable policy AND wiring it into agent context:

   a. Create or extend `AGENTS.md` at the repo root with a `## Policy` section that names the actual paths and commands. Use imperative voice. Keep the policy section under 80 lines so it fits in context after the rest of AGENTS.md.

   b. For long policy lists, factor into `.agent/restricted-paths.md` (or `.agent/policy.md`) and `@`-reference it from AGENTS.md so the loader pulls both. Mirror the same constraints in machine form at `.agent/policy.json` if the repo's tooling (lint, pre-commit, CI guard script) can consume it.

   c. For Claude Code repos, add a SessionStart hook that echoes the policy file so it is injected as context every session — not relying on AGENTS.md alone, which the model can de-prioritize:
      ```json
      {
        "hooks": {
          "SessionStart": [
            {
              "hooks": [
                { "type": "command", "command": "cat .agent/restricted-paths.md" }
              ]
            }
          ]
        }
      }
      ```

   d. Cross-link with #121 enforcement: every `deny` / `ask` rule in `.claude/settings.json` (or `commandDenylist` in `.factory/settings.json`) gets a one-line explanation in the policy file. Every "requires approval" item in the policy maps to an `ask` rule in settings. Audit for drift.

3. Verify the policy is actually loaded:
   - Run `claude /memory` (or restart the harness) and confirm the policy text appears in the loaded context.
   - For a SessionStart hook, run `claude --debug` and confirm the stdout was captured (look for the policy text in the transcript before the first user turn).
   - Pick one rule from the policy ("never edit `prisma/migrations/**`") and confirm the matching `.claude/settings.json` `deny` rule exists; pick one `deny` rule and confirm it is explained in AGENTS.md.

4. Keep changes focused on this signal — do not refactor unrelated docs or restructure AGENTS.md beyond adding/repairing the policy section.

5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** policy that lives only in a private wiki, Notion, Confluence, or any URL the agent harness cannot fetch at session start. If the agent has to be told "go read this URL," the policy is not visible.
- **NO** generic platitudes — "be careful with production," "use good judgment," "follow best practices." A policy that does not name specific paths and specific commands is not a policy.
- **NO** describing what the agent SHOULD DO without a matching list of what it MUST NOT DO. A "How to contribute" guide is not a policy.
- **NO** policy whose paths don't exist in the repo (`Never edit src/legacy/**` in a repo with no `src/legacy/`). Signals the policy was copy-pasted from a template; the agent learns to ignore it.
- **NO** policy that contradicts `.claude/settings.json` or `.factory/settings.json` — e.g. AGENTS.md says "you may run `terraform apply` after asking" but settings has `Bash(terraform apply *)` in `deny`. The agent will get blocked mid-task and re-attempt forever.
- **NO** dumping the policy into a 4000-line `CLAUDE.md` such that the constraints section falls outside the model's effective attention window. Keep the policy concentrated, near the top, and ideally in its own short file referenced by `@`.
- **NO** adding `agent-policy.json` at repo root and nothing else — no loader reads it, the agent never sees it, the signal stays failed. The file must be wired to a loader (AGENTS.md `@`-ref, SessionStart hook, or harness-native path).
- **NO** policy written in a passive, advisory voice ("ideally agents would avoid touching the migrations folder"). The agent will treat it as a soft preference. Use imperative refusals: "Refuse any edit to `prisma/migrations/**`. If a change there is needed, stop and ask the human."
- **NO** committing the policy and then never updating it. Add a line to the policy itself: "If you find this policy out of sync with `.claude/settings.json` or the codebase, stop and surface the drift before continuing."

Examples of BAD fixes:
- Adding `AGENTS.md` containing `## Security\n\nBe mindful of security when making changes.` — non-actionable; the agent learns nothing operational.
- Creating `agent-policy.json` with `{"forbidden_commands": ["rm -rf /"]}` — `rm -rf /` is not a realistic agent failure mode; the realistic ones are recursive deletes inside the repo, force pushes, prod migrations, leaking `.env`. List those.
- Adding a `## Do Not Touch` section that lists 200 paths the agent legitimately needs to read (`node_modules/**`, `dist/**`) — the agent stops trusting the list. Restrict to paths that are genuinely off-limits for safety/secrecy reasons.
- Linking from AGENTS.md to `https://internal-wiki.company.com/agent-policy` — the harness cannot fetch it; the link is invisible context.
- Writing the policy in `docs/onboarding/agents.md` (not a path any harness auto-loads) and assuming the agent will discover it.
- A `SessionStart` hook that runs `cat .agent/policy.md` but the file doesn't exist — silent stderr, the session starts with no policy and no warning.

Examples of GOOD fixes:

- An `AGENTS.md` `## Policy` section, terse and concrete:
  ```markdown
  ## Policy

  Read this before editing anything. Mirrors `.claude/settings.json` — keep them in sync.

  **Off-limits to read** (contain secrets or customer data):
  - `./.env`, `./.env.*`
  - `./secrets/**`
  - `./test/fixtures/customer-pii/**`
  - `./infra/terraform/*.tfstate*`

  **Off-limits to edit** (generated, vendored, or history-sensitive):
  - `./prisma/migrations/**` — never edit existing migrations; create a new one
  - `./packages/*/dist/**`, `./packages/*/build/**` — generated, regenerate via `pnpm build`
  - `./pnpm-lock.yaml` — regenerate via `pnpm install`, do not hand-edit
  - `./CHANGELOG.md` — written by release tooling

  **Requires human approval before running** (irreversible or production-touching):
  - `git push` to `main` or `release/*`
  - `git push --force` to any branch
  - `pnpm publish`
  - `prisma migrate deploy` (dev migrations OK locally; deploy is approval-gated)
  - Any `gh pr merge`, `gh release create`, or `terraform apply`

  **Refuse outright**:
  - `rm -rf` with a path that expands from an unset variable (`rm -rf "$DIR/"` when `$DIR` may be empty)
  - `curl <url> | sh`, `wget <url> | sh`
  - `sudo` anywhere — this repo never needs root
  - Editing `.github/CODEOWNERS` without a linked issue
  - Disabling CI checks, adding `// @ts-nocheck`, adding `# noqa` to bypass lint

  If a task seems to require something on the refuse list, stop and ask the human.
  See `.agent/restricted-paths.md` for the longer reference list and rationale.
  ```

- A companion `.agent/restricted-paths.md` with the same content in a longer narrative form, plus rationale for each entry (why each path is off-limits), wired in by AGENTS.md `@.agent/restricted-paths.md`.

- A `.claude/settings.json` `SessionStart` hook that guarantees the policy is in context every session, not just when the model decides to read AGENTS.md:
  ```json
  {
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "hooks": {
      "SessionStart": [
        {
          "hooks": [
            {
              "type": "command",
              "command": "test -f .agent/restricted-paths.md && cat .agent/restricted-paths.md || echo 'WARN: .agent/restricted-paths.md missing'"
            }
          ]
        }
      ]
    }
  }
  ```
  The `test -f ... || echo WARN` pattern surfaces drift (someone deleted the policy file) instead of failing silently.

- A machine-readable `.agent/policy.json` that pre-commit and a CI guard script consume, so the same constraints are enforced two ways (visibility for the agent, hard enforcement for everyone):
  ```json
  {
    "$schema": "./policy.schema.json",
    "read_denied": ["./.env", "./.env.*", "./secrets/**", "./test/fixtures/customer-pii/**"],
    "write_denied": ["./prisma/migrations/**", "./pnpm-lock.yaml", "./packages/*/dist/**"],
    "requires_approval": ["git push origin main", "git push --force *", "pnpm publish", "prisma migrate deploy", "terraform apply"],
    "forbidden_commands": ["sudo *", "curl * | sh", "wget * | sh"]
  }
  ```

- A `## Policy` section that ends with a drift-detection line: "If `.claude/settings.json` permissions contradict this policy, stop and ask the human which is authoritative — do not silently follow either."

## Why this matters

Signal #121 (Tool Allowlist) is the wall. Signal #131 is the agent knowing where the wall is. An agent that hits a deny rule mid-task with no prior knowledge will either (a) retry the same command in different shells trying to find a hole, (b) refactor the task to route around the wall in ways that introduce bugs, or (c) report success because the destructive step "succeeded" before the deny rule fired on the follow-up. All three failure modes have been observed in production agent runs in 2025–2026.

A visible policy lets the agent plan correctly the first time: "I would normally run `prisma migrate deploy` here, but the policy requires human approval — surfacing for review." That single behavior change is the difference between an agent that ships PRs and an agent that ships incidents.

The visibility-vs-enforcement split is non-negotiable. Visibility without enforcement = a polite agent that a prompt injection will reason past in one turn. Enforcement without visibility = an agent that thrashes against opaque walls and produces broken work. You need both. This signal is the visibility half; #121 is the enforcement half; they must point to each other.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- AGENTS.md open format spec: https://agents.md/
- AGENTS.md complete guide (2026), section structure and security considerations: https://blog.buildbetter.ai/agents-md-complete-guide-for-engineering-teams-in-2026/
- Factory droid `AGENTS.md` loading behavior: https://docs.factory.ai/cli/configuration/agents-md
- OpenAI Codex AGENTS.md custom instructions: https://developers.openai.com/codex/guides/agents-md
- Claude Code hooks reference (SessionStart stdout injected as context): https://code.claude.com/docs/en/hooks
- Claude Code SessionStart hooks for guaranteed context injection: https://www.mindstudio.ai/blog/session-start-hooks-claude-code-force-context
- Claude Code file path constraint enforcement gaps (issue #16733): https://github.com/anthropics/claude-code/issues/16733
- OpenCode proposal for per-agent filesystem allow/deny boundaries (issue #5529): https://github.com/sst/opencode/issues/5529
- Anthropic CLAUDE.md / memory import patterns: https://code.claude.com/docs/en/memory
</system-reminder>
