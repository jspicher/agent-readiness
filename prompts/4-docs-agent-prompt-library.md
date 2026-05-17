[Readiness Fix] <REPO_NAME> Agent Prompt Library

Fix the failing signal: Agent Prompt Library ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Agent Prompt Library
**Score**: [0/1]
**Description**: Pre-built prompts for common, repeatable tasks in this repo (release cuts, onboarding walkthroughs, test-locally runbooks, incident triage, dependency bumps) — checked in, discoverable, and invokable from at least one agent harness without copy-paste
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Agent prompt library – check for a directory of repeatable, task-shaped prompts the agent (or a human invoking the agent) can run by name. PASS requires at least TWO non-trivial prompt files in one of the canonical locations below, each tuned to this repo's actual workflows (not generic "write a function" stubs):

1. **GitHub Copilot prompt files**: `.github/prompts/<name>.prompt.md` with YAML frontmatter containing at minimum `description`, plus optionally `mode` (`ask` | `edit` | `agent`), `model`, and a `tools` array scoping which Copilot tools the prompt may invoke. Body is markdown with the templated instructions. Prompts must be loadable in VS Code via the `Chat: Run Prompt` command or by typing `/` in chat.
2. **Claude Code slash commands**: `.claude/commands/<name>.md` (project scope) or `~/.claude/commands/<name>.md` (personal — does NOT count for repo signal). Optional frontmatter: `description`, `argument-hint`, `allowed-tools`, `model`. Body may include `$ARGUMENTS` placeholder for user input and `!`-prefixed bash for pre-execution context. The filename becomes the slash command name.
3. **Cursor saved prompts / project rules acting as prompts**: `.cursor/rules/<name>.mdc` with YAML frontmatter (`description`, `globs`, `alwaysApply`) ONLY counts when the file is task-shaped ("run the release checklist", "triage this bug") rather than a passive convention rule. Cursor rules that just say "use 2-space indentation" belong to feature #1 (agent instructions), not the prompt library.
4. **Vendor-neutral prompt cookbook**: an `AGENTS.md` section titled `## Prompts` (or a `prompts/` / `docs/prompts/` directory) listing named, copy-pasteable prompts mapped to repo workflows. This counts only if the README or AGENTS.md surfaces the location — orphaned `prompts/` directories with no discovery path FAIL.

Each prompt must be **task-shaped**: a verb in the title, a concrete trigger condition, and either explicit steps or a structured output contract. A file containing only "You are a helpful assistant that writes code" is not a prompt library entry.

A `prompts/` directory containing one README and no actual prompts is a FAIL. A single `.prompt.md` file is a FAIL — the signal asks for a *library* (≥2).

## Your Task

1. Explore the repository to understand the current state related to this signal — list every `.github/prompts/`, `.claude/commands/`, `.cursor/rules/`, `prompts/`, `docs/prompts/`, and any `## Prompts` section in `AGENTS.md` / `README.md`. Note the repeatable workflows in this repo (release process, local dev bootstrap, PR review checklist, incident runbook, dependency bumps, schema migrations, on-call rotation handoff).
2. Make **substantive improvements** by writing real, repo-tuned prompt files:
   - Pick the harness this repo already uses. If `.claude/settings.json` exists, add `.claude/commands/<name>.md` files. If `.github/copilot-instructions.md` exists, add `.github/prompts/<name>.prompt.md` files. If both are present, ship both (the prompts can share content).
   - Author at LEAST 3 task-shaped prompts mapped to the repo's actual workflows. Suggested starting set: (a) `/release` — cut a versioned release from `main` (changelog, tag, publish), (b) `/test-locally` — bootstrap deps and run the test suite the way CI runs it, (c) `/review-pr` — fetch a PR diff and walk the project's review checklist, (d) `/triage-bug` — reproduce + bisect from a bug report, (e) `/bump-deps` — run the dependency upgrade flow with the project's lockfile + verification commands.
   - Each prompt MUST: (i) name the trigger in one sentence, (ii) list the concrete files/commands it touches (use repo-real paths), (iii) define the output contract (PR? changelog entry? comment on issue?), (iv) reference the deny list from the tool allowlist policy so prompts do not silently re-enable blocked commands.
   - Surface the library: add a `## Prompts` section to `AGENTS.md` (or create one) listing each prompt, when to invoke it, and which harness reads it. If `README.md` has a "For contributors" section, link from there too.
3. Verify the prompts load in the target harness:
   - Claude Code: in a session inside the repo, type `/` and confirm each new command appears with its `description`. Run one end-to-end on a throwaway branch.
   - Copilot: open VS Code in the repo, run `Chat: Run Prompt` from the command palette, confirm the prompt picker lists each new file. Hover the frontmatter to confirm `tools` resolves.
4. Keep changes focused on this signal — do not refactor unrelated config, do not rewrite existing skills (feature #4), do not move convention rules out of `.cursorrules` / `CLAUDE.md`.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** single-prompt directories. A `prompts/` folder with one file is a stub. Ship at least 3 task-shaped prompts on the first PR.
- **NO** prompts that just say "You are an expert engineer. Help the user." That is a system prompt, not a task template. Each entry must encode a SPECIFIC workflow with concrete trigger + concrete output.
- **NO** prompts that hardcode credentials, API keys, tokens, internal hostnames, customer names, or PII. The library is checked in and indexed by search engines.
- **NO** prompts that duplicate `AGENTS.md` content verbatim — if the agent already knows the build command from `AGENTS.md`, the prompt should reference it, not restate it. Duplication causes drift the moment one file changes.
- **NO** orphan directories. `prompts/` with no link from `README.md` or `AGENTS.md` is invisible to humans and gets stale within a sprint. Surface it.
- **NO** prompts in `~/.claude/commands/` or personal Cursor settings as the only artifact — those are per-developer and do not satisfy a repo-level signal. The team library lives in `.claude/commands/` (project), `.github/prompts/`, or `prompts/`.
- **NO** copy-pasted Awesome-Copilot prompts without removing irrelevant tools and tuning paths. A `tools: [terminal, browser, codebase, githubRepo]` array on a prompt that only reads files signals zero curation.
- **NO** prompts that re-enable commands the tool allowlist denies (e.g. a `/deploy-prod` prompt with `Bash(kubectl apply -f *)` when `kubectl apply` is in `deny`). Prompts inherit the policy — verify, do not bypass.

Examples of BAD fixes:
- Creating `.claude/commands/help.md` containing `Help the user with their question.` — zero task shape, zero repo specificity.
- A `.github/prompts/refactor.prompt.md` with `description: Refactor the code` and no body steps, no scope, no output contract.
- A `prompts/` directory with 12 generic LLM prompts copy-pasted from a blog post, none mentioning this repo's stack, build tool, or branching model.
- Adding `## Prompts` to `AGENTS.md` listing 4 prompt files that don't exist in the repo.
- A `/release` prompt that runs `npm publish` directly with no human-approval step on a repo where `npm publish` is in the policy `ask` list — the prompt punches through governance.

Examples of GOOD fixes:

`.github/prompts/release.prompt.md` (GitHub Copilot, Node + changesets repo):
```markdown
---
description: Cut a versioned release from main using changesets
agent: agent  # the older `mode: agent` key was deprecated in late 2025; current GitHub Docs use `agent: 'agent'`
# model: optional -- omit unless you need to pin; the Copilot picker has GPT-5.5 / 5.4 / 5.3-Codex / 5.2 / etc.
tools: [codebase, terminal, githubRepo]
---

# Release

Trigger: Maintainer wants to cut a release after merging changeset PRs.

Steps:
1. Confirm current branch is `main` and working tree is clean (`git status`).
2. Run `pnpm changeset version` — this updates package versions and `CHANGELOG.md`.
3. Run `pnpm install --lockfile-only` to refresh `pnpm-lock.yaml`.
4. Run `pnpm build && pnpm test` — must pass before tagging.
5. Commit with message `chore(release): version packages` and push to `main`.
6. Wait for GitHub Actions `release.yml` workflow to publish to npm and create the GitHub Release.

Output contract:
- A PR is NOT created — releases ship directly from `main` via the release workflow.
- Report the new version numbers (one per package) and the GitHub Release URL.

Notes:
- Do not run `npm publish` manually. The release workflow handles publishing with the `NPM_TOKEN` secret.
- If `pnpm test` fails, STOP. Open an issue describing the failure rather than skipping tests.
```

`.claude/commands/test-locally.md` (Claude Code, Python + pytest repo):
```markdown
---
description: Run the test suite the way CI runs it
argument-hint: [optional pytest path filter]
allowed-tools: Bash(uv sync), Bash(uv run pytest *), Bash(uv run ruff *), Read
---

# Test Locally

Trigger: Before opening a PR, or when reproducing a CI failure locally.

Steps:
1. Run `uv sync --frozen` to install deps matching `uv.lock` (mirrors CI).
2. Run `uv run ruff check .` and `uv run ruff format --check .` — CI fails on either.
3. Run `uv run pytest $ARGUMENTS` (defaults to full suite when `$ARGUMENTS` is empty).
4. If a test fails, fetch the same job from CI to confirm it is not a local-environment skew: `gh run list --workflow=ci.yml --limit 1`.

Output contract:
- Print pass/fail counts and the first failing test's full traceback.
- If everything passes, suggest the next action (open PR, push to existing branch).
```

`.claude/commands/triage-bug.md` (Claude Code, any repo):
```markdown
---
description: Reproduce a reported bug and bisect to the introducing commit
argument-hint: <issue-number-or-url>
allowed-tools: Bash(gh issue view *), Bash(git bisect *), Bash(git log *), Read, Grep
---

# Triage Bug

Trigger: A new bug report needs reproduction + root cause before fix work.

Steps:
1. Fetch the issue: `gh issue view $ARGUMENTS --json title,body,labels,comments`.
2. Identify the minimal reproduction from the issue body. If absent, list the gaps and stop.
3. Reproduce on `main`. If it does not reproduce, post a comment requesting more info and stop.
4. Run `git bisect start HEAD <last-known-good-tag>` and bisect using the reproduction as the test command.
5. Post a triage comment on the issue with: reproduction confirmed (y/n), introducing commit SHA, suspected file(s), suggested fix owner (use `CODEOWNERS`).

Output contract:
- A comment on the issue, formatted as the project's triage template (see `.github/ISSUE_TEMPLATE/triage-comment.md`).
- Do NOT push a fix from this prompt — open a separate branch for the fix work.
```

Add to `AGENTS.md`:
```markdown
## Prompts

Task-shaped prompts live in `.claude/commands/` (Claude Code) and `.github/prompts/` (GitHub Copilot). Both directories are checked in. Invoke from Claude Code with `/<name>`; from Copilot with `Chat: Run Prompt`.

| Prompt | When to use | Harness |
| --- | --- | --- |
| `release` | Cutting a versioned release after changeset PRs merge | Copilot |
| `test-locally` | Reproducing CI failures or pre-PR verification | Claude Code |
| `triage-bug` | New bug report needs reproduction + bisect | Claude Code |
| `bump-deps` | Weekly Renovate batch needs review + merge | Both |

Prompts inherit the tool policy from `.claude/settings.json` `permissions`. Do not author prompts that bypass `deny` rules.
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- GitHub Copilot prompt files (`.github/prompts/*.prompt.md`, frontmatter spec): https://code.visualstudio.com/docs/copilot/customization/prompt-files
- GitHub Copilot prompt files tutorial: https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files
- awesome-copilot prompt format & quality standards: https://github.com/github/awesome-copilot/blob/main/instructions/prompt.instructions.md
- Claude Code slash commands (`.claude/commands/*.md`, `allowed-tools`, `argument-hint`, `$ARGUMENTS`): https://code.claude.com/docs/en/slash-commands.md
- Claude Code SDK slash commands reference: https://code.claude.com/docs/en/agent-sdk/slash-commands
- Cursor rules (`.cursor/rules/*.mdc`, `@-symbol` references): https://docs.cursor.com/context/@-symbols/@-cursor-rules
- AGENTS.md open spec (prompt cookbook section pattern): https://agents.md
</system-reminder>
