[Readiness Fix] <REPO_NAME> AI IDE Configuration

Fix the failing signal: AI IDE Configuration ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: AI IDE Configuration
**Score**: [0/1]
**Description**: Settings or rules for AI-powered editors/IDEs (Cursor, GitHub Copilot, Claude Code, etc.) checked into the repository
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

AI IDE configuration – check for checked-in, project-tuned configuration for at least one major AI-powered editor. PASS requires a non-empty configuration file at one of the documented paths AND content that demonstrably reflects this repo's stack, conventions, or workflows. Acceptable artifacts:

1. **Cursor (modern)**: one or more `.cursor/rules/*.mdc` files. Each file must be a Markdown file with a YAML-ish frontmatter block (Cursor's frontmatter is *not* strict YAML — `globs` is a comma-separated list, NOT a JSON array, and values are unquoted) and a rule body. Frontmatter fields: `description` (string, agent-facing summary), `globs` (comma-separated patterns, e.g. `src/components/**/*.tsx, src/hooks/**/*.ts`), `alwaysApply` (boolean). Rules can activate in four modes — Always (`alwaysApply: true`), Auto Attached (`globs` populated), Agent Requested (`description` populated, `alwaysApply: false`, no `globs`), and Manual (`@my-rule`). A `.cursor/rules/` directory with at least one substantive `.mdc` file passes.
2. **Cursor (legacy)**: a non-empty `.cursorrules` file at repo root. Still read by Cursor in 2026 but deprecated in favor of `.cursor/rules/`. Counts only if the content is project-tuned (>200 characters and references this repo's stack).
3. **GitHub Copilot**: `.github/copilot-instructions.md` (repo-wide) and/or one or more `.github/instructions/*.instructions.md` files (path-scoped). Path-scoped files MUST include an `applyTo` frontmatter field with a glob, e.g. `applyTo: "**/*.py"` or `applyTo: "src/components/**/*.{tsx,jsx}"`. Both files must be non-empty and reference real concerns (deprecated libs to flag, framework conventions, language-specific rules), not marketing prose.
4. **Claude Code**: `.claude/settings.json` (project, committed) containing at least one of: `permissions`, `hooks`, `env`, `mcpServers`, or `model`. A bare `{}` or a file that only sets `theme` is a stub. `~/.claude/settings.json` is user-scope and lives outside the repo; `.claude/settings.local.json` is gitignored by Claude Code on creation and does NOT satisfy this signal on its own — the team-shared `.claude/settings.json` must exist.
5. **Other supported editors**: `.windsurf/rules/*.md`, `.aider.conf.yml`, `.continue/config.json`, `.zed/settings.json`, JetBrains AI Assistant `.idea/aiAssistantSettings.xml`. Counts when the file is non-empty and project-tuned.

Note: this signal is satisfied by configuration for ONE major AI IDE. Multi-IDE coverage (rules for Cursor AND Copilot AND Claude Code) is feature #3 (AI IDE Coverage) and is evaluated separately — do NOT add four IDE configs in the hope of passing more signals here.

`AGENTS.md` is a separate signal (feature #1) and does NOT satisfy this one. `AGENTS.md` is a portable, IDE-agnostic agent brief; AI IDE Configuration is editor-specific rule plumbing.

A `.cursorrules` file containing only `# Cursor Rules` and a blank line FAILs. A `.github/copilot-instructions.md` that says "Be a helpful assistant. Write clean code." FAILs — it adds nothing the model doesn't already know.

## Your Task

1. Explore the repository to understand the current state related to this signal — list every `.cursor/`, `.cursorrules`, `.github/copilot-instructions.md`, `.github/instructions/`, `.claude/settings.json`, `.windsurf/`, `.continue/`, `.aider.conf.yml`, and `AGENTS.md` file. Note which AI editor the team actually uses (check commit history, `README.md`, or `CONTRIBUTING.md` for hints).
2. Make **substantive improvements** by writing real, project-tuned editor configuration:
   - Pick ONE primary AI IDE based on team usage (default to Cursor if unknown — it has the largest installed base in 2026).
   - For **Cursor**, create `.cursor/rules/` with at least two `.mdc` files: a foundational rule (`alwaysApply: true`) covering stack/language/style, and one or more domain rules with `globs` scoping (e.g. `api-routes.mdc` globs to `src/app/api/**/*.ts`, `components.mdc` globs to `src/components/**/*.tsx`). Each rule body should reference the actual frameworks, file layout, and conventions you find in the repo.
   - For **GitHub Copilot**, create `.github/copilot-instructions.md` with repo-wide guidance (build commands, dependency policy, naming conventions, "flag deprecated X library"), plus path-scoped `.github/instructions/<topic>.instructions.md` files with `applyTo` frontmatter for any language- or directory-specific rules.
   - For **Claude Code**, create `.claude/settings.json` (committed) with at minimum a non-trivial `permissions` block tuned to the repo's actual build/test commands. Do NOT commit `.claude/settings.local.json` as the only artifact — that file is gitignored.
3. Verify the file parses where applicable: open the repo in the target IDE; for Claude Code add `"$schema": "https://json.schemastore.org/claude-code-settings.json"` and confirm the editor doesn't underline it red; for Cursor, confirm rules show up in the Cursor Settings → Rules panel; for Copilot, confirm the file is detected (VS Code Output → GitHub Copilot logs name the file).
4. Keep changes focused on this signal — do not refactor unrelated config and do not add four IDE configs at once (that's feature #3).
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** empty rule files. A `.cursorrules` with `# Project Rules\n` and nothing else, or a `python.instructions.md` with `applyTo: "**/*.py"` and an empty body, FAILs.
- **NO** Cursor frontmatter written as JSON arrays. `globs: ["**/*.ts"]` is wrong — Cursor's frontmatter is not strict YAML; use `globs: **/*.ts` (comma-separated, unquoted, no brackets). Brackets or quotes silently break activation.
- **NO** Copilot path-scoped files missing `applyTo`. Without `applyTo`, Copilot loads the file at repo-wide scope, which defeats the point of putting it in `.github/instructions/` and will misapply language-specific rules to the wrong files.
- **NO** generic copy-paste from Awesome Cursor / awesome-copilot. A Python repo with a rule that says "Use TypeScript strict mode" signals zero project knowledge. Every rule MUST cite something specific to this repo: a real directory, a real framework version, a real linter, a real CI step.
- **NO** committing `.claude/settings.local.json` as the only Claude Code artifact. That file is gitignored on creation by design; team policy belongs in `.claude/settings.json`.
- **NO** marketing prose. "This project values clean, maintainable code and clear communication." is filler — the model has read a million README files like that. Replace with enforceable constraints: "Reject PRs that import `moment`; use `date-fns` (already a dep)."
- **NO** duplicating `AGENTS.md`. If `AGENTS.md` already documents build/test/conventions, the IDE rule files should ADD editor-specific behavior (auto-attach scoping, code-review heuristics) and reference `AGENTS.md` as the source of truth — not restate it.
- **NO** rules that contradict the existing linter / formatter / `tsconfig`. If `prettier` enforces 2-space indent, do not write a rule saying "use 4 spaces" — the rule will be ignored on save and the agent will fight the formatter forever.
- **NO** stuffing all rules into one `alwaysApply: true` file. That floods every chat with irrelevant context and burns tokens. Use `globs` to scope.

Examples of BAD fixes:
- `.cursorrules` containing `You are a helpful AI assistant. Write clean code and follow best practices.` — generic, adds nothing.
- `.cursor/rules/main.mdc` with `globs: ["**/*"]` and `alwaysApply: true` — wrong glob syntax AND defeats scoping; if it's truly global, leave `globs` empty and set `alwaysApply: true`.
- `.github/copilot-instructions.md` that says "Use modern JavaScript" with no mention of the repo's actual frameworks, lint config, or deprecated dependencies.
- `.github/instructions/typescript.instructions.md` with no `applyTo` frontmatter — gets applied to `.py` and `.md` files too.
- `.claude/settings.json` containing `{"theme": "dark"}` — cosmetic, not policy.
- Committing four IDE configs (Cursor + Copilot + Claude + Windsurf) the team doesn't use, all generated from the same template. Multi-IDE is a separate signal; pick one and do it well.

Examples of GOOD fixes:

- For a Next.js + TypeScript repo, create `.cursor/rules/foundation.mdc`:
  ```mdc
  ---
  description: Project stack, structure, and non-negotiable conventions
  alwaysApply: true
  ---
  Next.js 15 App Router + TypeScript 5.4 strict mode. Package manager: pnpm (never npm/yarn — lockfile is `pnpm-lock.yaml`).

  Directory layout:
  - `src/app/` — App Router routes and route handlers
  - `src/components/` — shared React components (server by default; mark `'use client'` only when needed)
  - `src/lib/` — pure utilities (no React imports)
  - `src/server/` — server-only code (DB, auth); never import from `src/components/`

  Forbidden:
  - `moment` (use `date-fns`, already a dep)
  - `lodash` full import (use `lodash-es` named imports for tree-shaking)
  - `any` type without a `// eslint-disable-next-line` justification comment

  Tests: `pnpm test` (Vitest). Lint: `pnpm lint` (Biome). Always run both before claiming done.
  ```

- And a scoped companion `.cursor/rules/api-routes.mdc`:
  ```mdc
  ---
  description: App Router route handler conventions
  globs: src/app/api/**/*.ts
  alwaysApply: false
  ---
  Export named async functions: `GET`, `POST`, `PUT`, `DELETE`.
  Return `NextResponse.json(payload, { status })` — never bare `Response`.
  Validate request bodies with Zod schemas from `src/server/schemas/`.
  Wrap handlers in `withAuth()` from `src/server/auth/middleware.ts` unless the route is in the public allowlist (`src/server/auth/public-routes.ts`).
  Errors: throw `HttpError` from `src/server/errors.ts`; the global handler in `src/app/api/_error.ts` formats the response.
  ```

- For a Python repo using Copilot, create `.github/copilot-instructions.md`:
  ```md
  # Copilot instructions for <REPO_NAME>

  Stack: Python 3.12, FastAPI 0.110, SQLAlchemy 2.0 (async), Pytest, Ruff.
  Package manager: `uv` — never `pip install` directly; edit `pyproject.toml` and run `uv sync`.

  Flag in PRs:
  - Any use of `datetime.utcnow()` (deprecated in 3.12; use `datetime.now(timezone.utc)`)
  - Any new dependency not added via `uv add`
  - Any SQLAlchemy 1.x-style `Query` API (we are 2.0-only; use `select()`)
  - Any test added without an `assert` statement
  - Any route handler missing a Pydantic response model

  Build: `uv sync`. Test: `uv run pytest`. Lint: `uv run ruff check --fix`.
  ```

  Plus a path-scoped `.github/instructions/migrations.instructions.md`:
  ```md
  ---
  applyTo: "alembic/versions/**/*.py"
  ---
  Every migration MUST have a `downgrade()` that actually reverses `upgrade()` (no `pass`).
  Never drop a column in the same migration that adds its replacement — use a two-step migration with a deploy in between.
  Run `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` locally before opening the PR.
  ```

- For a repo where Claude Code is the team's primary tool, `.claude/settings.json`:
  ```json
  {
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "permissions": {
      "allow": [
        "Bash(pnpm install)", "Bash(pnpm test *)", "Bash(pnpm lint *)",
        "Bash(pnpm build)", "Bash(git status)", "Bash(git diff *)",
        "Bash(gh pr view *)", "Read(./src/**)", "Read(./tests/**)"
      ],
      "ask": ["Bash(git push *)", "Bash(gh pr create *)", "Bash(pnpm publish *)"],
      "deny": [
        "Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)",
        "Bash(rm -rf *)", "Bash(curl * | sh)", "Bash(git push --force *)"
      ]
    },
    "env": { "NODE_ENV": "development" }
  }
  ```
  (If the repo also has a Tool Allowlist signal failing, this single file fixes both — but stay scoped: do NOT also add Cursor and Copilot configs in the same PR.)

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Cursor rules (`.cursor/rules/*.mdc`, frontmatter, activation modes): https://cursor.com/docs/rules
- Cursor MDC frontmatter is not strict YAML (globs are comma-separated, unquoted): https://agentspec.sh/rules/2d77063f-4f47-40b2-84d5-c9806a26cdc7
- `.cursorrules` vs `.cursor/rules/` (legacy vs modern, 2026): https://thepromptshelf.dev/blog/cursorrules-vs-mdc-format-guide-2026
- GitHub Copilot custom instructions (`copilot-instructions.md`, `.github/instructions/*.instructions.md`, `applyTo`): https://docs.github.com/en/copilot/concepts/code-review/coding-guidelines
- GitHub Copilot path-scoped instructions tutorial: https://docs.github.com/en/copilot/tutorials/use-custom-instructions
- GitHub Copilot supported instruction types matrix (which IDE reads what): https://docs.github.com/en/copilot/reference/custom-instructions-support
- Claude Code settings hierarchy and precedence (`.claude/settings.json` vs `settings.local.json` vs `~/.claude/`): https://code.claude.com/docs/en/settings
- Awesome GitHub Copilot Customizations (community examples — adapt, do not copy verbatim): https://github.com/github/awesome-copilot
</system-reminder>
