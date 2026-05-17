[Readiness Fix] <REPO_NAME> Multi-Model Support

Fix the failing signal: Multi-Model Support ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Multi-Model Support
**Score**: [0/1]
**Description**: Repository ships agent instructions for two or more distinct AI coding tools, with no vendor lock-in
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Multi-model support — check for instructions across different AI models/tools, not locked to a single vendor. PASS requires **two or more distinct agent config types from features 1–2 present in the same repo**, AND those configs do not contradict each other. Acceptable pairs include:

1. **`AGENTS.md` at repo root** as the canonical, tool-neutral source of truth. AGENTS.md is the open spec at https://agents.md/ supported natively by OpenAI Codex CLI, Cursor, Aider, OpenCode, Gemini CLI, Jules, Factory droid, RooCode, Kilo Code, Zed, Warp, and Amp. File should be >100 chars and contain real project info (setup, build, test, conventions) — not a stub.
2. **Claude Code bridge**: a `CLAUDE.md` that imports AGENTS.md via `@AGENTS.md` (Claude Code expands `@path` imports inline at load, up to 5 hops). A `.claude/settings.json` alone does NOT satisfy this — Claude reads instructions from `CLAUDE.md` / `~/.claude/CLAUDE.md`, not `settings.json`.
3. **Cursor bridge**: `.cursor/rules/*.mdc` files with YAML frontmatter (`alwaysApply: true` for project-wide, `globs:` for path-scoped). At minimum one rule should reference AGENTS.md or restate its key constraints. The legacy single `.cursorrules` file is deprecated — use `.cursor/rules/` directory.
4. **GitHub Copilot bridge**: `.github/copilot-instructions.md` for repo-wide defaults, and/or `.github/instructions/NAME.instructions.md` files with YAML frontmatter `applyTo: '<glob>'` for path-scoped rules.
5. **Gemini bridge**: `GEMINI.md` (Gemini CLI looks for this name specifically; it does not yet auto-read AGENTS.md in every release — verify the version in use).

Counting rules:
- AGENTS.md + a bridge file that points to AGENTS.md (import, symlink, or short pointer) = PASS.
- AGENTS.md alone with no second-tool bridge = FAIL for this signal (it's still a PASS for feature #2, but not #3).
- Two bridge files that each duplicate full instructions and don't import a shared source = FAIL (it's a drift trap, not multi-model support).
- A single `.cursorrules` file with no other tool config = FAIL (single-vendor lock).

## Your Task

1. Explore the repository: list every `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, `.cursor/rules/`, `.github/copilot-instructions.md`, `.github/instructions/`, `.factory/AGENTS.md`, `CONVENTIONS.md`, and any other agent instruction file. Note which AI tools the team actually uses (check git history for `.claude/`, `.cursor/`, `.github/copilot-*` touches; check open editor configs in `.vscode/extensions.json` for `github.copilot`, `anthropic.claude-code`, etc.).
2. Make **substantive improvements**:
   - If no `AGENTS.md` exists, create one first (this fix depends on feature #2 — if feature #2 also failed, run that remediation first).
   - Add at least one bridge file for a second tool the team uses. Bridge files MUST point back to AGENTS.md rather than duplicate its contents:
     - `CLAUDE.md` containing `@AGENTS.md` on its own line, followed by any Claude-specific additions (skills, hooks, MCP notes).
     - `.cursor/rules/00-agents-md.mdc` with `alwaysApply: true` and a body that says "Follow all instructions in `AGENTS.md` at the repo root" plus any Cursor-specific behavioral notes (e.g. "use Plan Mode for refactors >5 files").
     - `.github/copilot-instructions.md` whose body begins with "This project's primary instructions live in `AGENTS.md`. Read it first." then enumerates any Copilot-only constraints.
   - If `.cursor/rules/` already exists and contains the entire instruction set duplicated, REFACTOR: keep the rule file, replace its body with a pointer to AGENTS.md, and move any project-specific content into AGENTS.md.
3. Verify: confirm `AGENTS.md` and each bridge file are tracked (`git ls-files | grep -E '(AGENTS|CLAUDE|GEMINI|copilot-instructions)\.md|\.cursor/rules/'`), and confirm the configs don't contradict each other (a quick read of all four should produce the same answer to "what test command does this repo use?").
4. Keep changes focused on this signal — do not rewrite the existing AGENTS.md content unless it's stub-quality.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** symlinking `CLAUDE.md -> AGENTS.md` on Windows-friendly repos. Git symlinks on Windows require `core.symlinks=true` and Developer Mode; on a fresh clone they appear as plaintext stubs containing the target path. Use the `@AGENTS.md` import line instead — it is portable and survives `core.autocrlf`.
- **NO** copy-paste duplication. If `CLAUDE.md` and `AGENTS.md` both contain the full setup/test/conventions sections, they will drift within a sprint. One canonical file; everything else imports or points to it.
- **NO** contradictory configs. If `AGENTS.md` says "use pnpm" and `.cursor/rules/setup.mdc` says "use npm install", you have negative multi-model support — agents flip behavior by IDE. Reconcile before committing.
- **NO** single-vendor bridges in vendor-neutral clothing. A `CLAUDE.md` that imports AGENTS.md but also contains 200 lines of Claude-specific MCP and skill instructions is fine; a `CLAUDE.md` that imports nothing and just restates AGENTS.md content in Claude-flavored prose is not multi-model — it's a fork.
- **NO** bridges to tools the team does not use. Adding `.cursor/rules/` to a Claude-only shop is theater. Inspect git history; bridge only to tools with evidence of actual use (recent commits touching that tool's config, editor extensions pinned in `.vscode/extensions.json`, or CI steps).
- **NO** legacy `.cursorrules` as the second config. Cursor deprecated it in favor of `.cursor/rules/*.mdc` with MDC frontmatter. New files must use the directory format.
- **NO** empty `applyTo:` frontmatter in `.github/instructions/*.instructions.md`. Without a glob, the file is dead config — Copilot won't attach it.

Examples of BAD fixes:
- Creating an empty `CLAUDE.md` containing only the literal string `@AGENTS.md` when AGENTS.md itself is a 3-line stub — the import resolves to nothing useful.
- `ln -s AGENTS.md CLAUDE.md` committed to a repo with Windows contributors — appears as the text `AGENTS.md` on Windows clones.
- A `.cursor/rules/conventions.mdc` with no frontmatter at all — Cursor needs `alwaysApply: true` or `globs:` to attach the rule, otherwise it sits inert.
- `.github/copilot-instructions.md` that says "be helpful and write clean code" — adds zero project knowledge and counts as a stub.
- AGENTS.md (vendor-neutral) + CLAUDE.md that overrides `Run tests with: pytest` to `Run tests with: pytest --no-header -ra` — small contradictions cause agent-flip-flop between sessions.

Examples of GOOD fixes:
- **Three-file bridge pattern (cross-IDE team using Claude Code + Cursor + Copilot)**:
  - `AGENTS.md` (canonical, 200+ lines):
    ```markdown
    # AGENTS.md
    ## Setup
    pnpm install
    ## Test
    pnpm test (Vitest) — single file: pnpm test path/to/file.test.ts
    ## Build
    pnpm build (tsup, outputs to dist/)
    ## Conventions
    - All async handlers must wrap with `asyncHandler()` from src/lib/async.ts
    - Database migrations live in supabase/migrations/ — never edit applied migrations
    - No console.log in src/ — use the logger from src/lib/log.ts
    ```
  - `CLAUDE.md`:
    ```markdown
    @AGENTS.md

    ## Claude-Code-specific notes
    - MCP servers configured in `.mcp.json`: github, supabase, filesystem
    - Skills available in `.claude/skills/`: see `.claude/skills/README.md` for the index
    - Use the `pomodoro` skill when starting any task >30 min
    ```
  - `.cursor/rules/00-agents-md.mdc`:
    ```markdown
    ---
    description: Project conventions (canonical source AGENTS.md)
    alwaysApply: true
    ---
    Follow all instructions in `AGENTS.md` at the repo root. Treat it as source of truth.

    Cursor-specific:
    - Prefer Plan Mode for any change touching >5 files.
    - When invoking `@Codebase`, scope queries to `src/` unless investigating tests.
    ```
  - `.github/copilot-instructions.md`:
    ```markdown
    This project's primary instructions live in `AGENTS.md`. Read it first.

    Copilot-specific:
    - PR titles follow Conventional Commits (`feat:`, `fix:`, `chore:`).
    - When reviewing PRs, flag any new `console.log` in `src/` — use `src/lib/log.ts`.
    ```
- **Path-scoped Copilot rule** in `.github/instructions/python.instructions.md`:
    ```markdown
    ---
    applyTo: '**/*.py'
    ---
    Python files must pass `ruff check` and use type hints on all public functions. See AGENTS.md for full conventions.
    ```
- **Verification command** in the PR description:
    ```bash
    git ls-files | grep -E '(AGENTS|CLAUDE|GEMINI|copilot-instructions)\.md|\.cursor/rules/.*\.mdc'
    # Expect at least 2 lines: AGENTS.md and one bridge file.
    ```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- AGENTS.md open spec & tool support matrix: https://agents.md/
- Claude Code `@import` syntax in CLAUDE.md (up to 5 hops): https://docs.claude.com/en/docs/claude-code/memory
- Cursor rules (`.cursor/rules/*.mdc`, MDC frontmatter, `alwaysApply` / `globs`): https://cursor.com/docs/context/rules
- GitHub Copilot custom instructions (`.github/copilot-instructions.md` + `.github/instructions/*.instructions.md` with `applyTo`): https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
- Copilot path-scoped instructions changelog: https://github.blog/changelog/2025-09-03-copilot-code-review-path-scoped-custom-instruction-file-support/
- OpenAI Codex AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md
- Factory droid AGENTS.md handling: https://docs.factory.ai/cli/configuration/agents-md
- AGENTS.md adoption tracker (Codex, Cursor, Aider, OpenCode, Gemini CLI, Jules, Zed, Warp, Amp, RooCode, Kilo): https://socket.dev/blog/agents-md-gains-traction-as-an-open-format-for-ai-coding-agents
- Windows symlink caveat for `CLAUDE.md -> AGENTS.md`: https://claudelog.com/faqs/claude-md-agents-md-symlink/
</system-reminder>
