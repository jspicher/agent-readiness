[Readiness Fix] <REPO_NAME> Component-Level Agent Guidance

Fix the failing signal: Component-Level Agent Guidance ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Component-Level Agent Guidance
**Score**: [0/1]
**Description**: Different parts of the codebase have their own agent instructions, scoped to that subtree, so an agent editing a package picks up package-specific conventions instead of falling back to a generic repo-wide doc.
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Component-level agent guidance (L4) – check for instruction files nested below the repo root that scope guidance to a specific package, app, service, or module. PASS requires at least TWO non-root instruction files, each carrying substantive (>40 lines) package-specific content. Accept any of the following surfaces, but each must be wired to the tool that reads it:

1. **AGENTS.md nested convention**: `apps/web/AGENTS.md`, `apps/api/AGENTS.md`, `packages/<name>/AGENTS.md`, `services/<name>/AGENTS.md`. Nearest-AGENTS.md-wins: agents walking from the file under edit upward read the closest AGENTS.md first, then accumulate ancestor files. A nested AGENTS.md extends the root — it does not replace it — so the package file should document only what differs (framework, build command, test runner, owner, gotchas) and rely on the root for repo-wide conventions.
2. **Nested CLAUDE.md**: `packages/<name>/CLAUDE.md` files that Claude Code lazy-loads when it reads or edits files inside that subtree. Root CLAUDE.md may pull deep references in via `@./packages/api/CLAUDE.md` import syntax (max 5 hops, relative paths resolve from the importing file).
3. **Copilot path-scoped instructions**: `.github/instructions/<name>.instructions.md` with frontmatter `applyTo:` glob (e.g. `applyTo: "apps/web/**/*.tsx"` or `applyTo: "packages/api/**/*.ts,packages/api/**/*.sql"`). Multiple globs comma-separated. Glob `**` is recursive.
4. **Cursor `.cursorrules` per-directory** or `.cursor/rules/*.mdc` files with `globs:` frontmatter scoping to a package path.

A subtree with no agent-discoverable instruction file FAILs even if the root AGENTS.md mentions the subtree in prose. The agent walks the file tree from the edit target — it does not search the root file for the relevant section.

## Your Task

1. Map the repository's component boundaries. Look for: `apps/*`, `packages/*`, `services/*`, `crates/*`, `cmd/*`, `internal/*`, workspace entries in `pnpm-workspace.yaml` / `package.json` `workspaces` / `Cargo.toml` `[workspace.members]` / `go.work`. List every component that has a distinct (a) tech stack, (b) build/test command, (c) deploy target, or (d) owner.
2. For each component that diverges from the root, decide whether to ship `AGENTS.md`, nested `CLAUDE.md`, or `.github/instructions/<name>.instructions.md`. Pick ONE surface per repo unless the team uses multiple agents — duplicating the same content into three file formats invites drift.
3. Write the per-component file. It must document only what differs from the root:
   - **Stack and entry point**: framework version, language, where `main` lives.
   - **Commands**: install / dev / build / test / lint commands that differ from the root (e.g. root uses `pnpm`, this package uses `cargo`).
   - **Conventions**: directory layout, naming, test placement, fixture location, mocking strategy.
   - **Gotchas**: known footguns (e.g. "do not run `prisma generate` against the prod DB URL", "this service requires Redis on :6380 not :6379", "fabric.js canvas state must be cloned before mutation").
   - **Owner / on-call**: who reviews PRs touching this subtree.
   - **Pointer back to root**: explicit one-liner "See ../../AGENTS.md for repo-wide conventions" so a human dropping in mid-file knows the root exists.
4. If using `.github/instructions/*.instructions.md`, add the `applyTo:` frontmatter and verify the glob matches by editing a file in the scoped subtree and confirming Copilot picks up the rule.
5. If using nested `CLAUDE.md` and the root file needs to reference a deep one (e.g. surface a critical gotcha at session start), add the explicit `@./packages/<name>/CLAUDE.md` import to the root — Claude Code does NOT auto-load nested CLAUDE.md at session start; it lazy-loads when the subtree is touched.
6. Verify the nested files are actually read by the agent: open a file inside the component, ask the agent "what build command does this package use?", and confirm it answers from the component file, not from the root.
7. Keep changes focused on this signal — do not refactor the root AGENTS.md or move existing content around.
8. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** stub component files. A 5-line `packages/api/AGENTS.md` that only says "this is the API package" provides zero signal over no file at all and is worse than nothing because it suppresses the agent's instinct to ask.
- **NO** copying the root AGENTS.md verbatim into every subdirectory. Nested files **extend** the root — they do not replace it. Duplicating content guarantees drift the first time the root changes.
- **NO** component files that silently contradict the root without explaining why. If `packages/legacy-api/AGENTS.md` says "use callbacks, not async/await" while the root says "always use async/await", the component file MUST state the override and the reason ("this package targets Node 8 for $REASON; do not introduce async/await syntax").
- **NO** putting a component file at the wrong nesting level. `packages/AGENTS.md` (one level above the individual packages) does NOT scope to any single package — the nearest-wins walk picks it up for every sibling. Put the file inside the package directory it describes.
- **NO** Copilot `.instructions.md` files without the `applyTo:` frontmatter — without the glob, the file applies globally and behaves like a second root file, not a scoped override.
- **NO** missing the import chain in nested `CLAUDE.md` when the root needs to surface a deep rule at session start. Lazy-load means "only when the agent touches the subtree" — a critical "never commit to main from this package" rule will not be visible during planning.
- **NO** more than ONE instruction-file format per component. `packages/api/AGENTS.md` AND `packages/api/CLAUDE.md` AND `.github/instructions/api.instructions.md` is three sources of truth that will diverge inside a month.

Examples of BAD fixes:

- Adding `packages/web/AGENTS.md` containing only `# Web package\n\nThis is the web app.` — no commands, no conventions, no gotchas. Stub.
- Copying the 300-line root AGENTS.md into `apps/api/AGENTS.md` and `apps/web/AGENTS.md` unchanged — both files will be stale within a week and the agent now has three places to reconcile.
- Creating `.github/instructions/api.instructions.md` with package-specific rules but no `applyTo:` frontmatter — the file applies to every file in the repo, overriding the root for unrelated languages.
- Putting `services/AGENTS.md` at the `services/` directory level instead of inside each individual service directory — every service inherits the same generic file and none get service-specific guidance.
- Writing `packages/legacy/AGENTS.md` that says "use callbacks" without explaining why it contradicts the root's "use async/await" — the agent has no way to judge which rule wins for the next refactor.
- Adding a nested `packages/api/CLAUDE.md` with a critical "never run migrations against prod" rule and NOT importing it into the root with `@./packages/api/CLAUDE.md` — the rule is invisible until Claude happens to open a file in `packages/api/`.

Examples of GOOD fixes:

- Monorepo with three workspaces (`apps/web` Next.js, `apps/api` Fastify+Prisma, `packages/shared` TypeScript lib) ships three nested `AGENTS.md`:

  Root `AGENTS.md` (repo-wide):
  ```
  # Repo conventions
  - pnpm workspaces. Always run commands from repo root: `pnpm --filter <workspace> <cmd>`.
  - All packages use TypeScript strict mode and Vitest.
  - Conventional Commits enforced via commitlint.
  ```

  `apps/web/AGENTS.md` (Next.js override):
  ```
  # apps/web — Next.js 15 App Router
  See ../../AGENTS.md for repo-wide conventions.

  ## Commands
  - Dev: `pnpm --filter web dev` (port 3000)
  - Build: `pnpm --filter web build`
  - E2E: `pnpm --filter web test:e2e` (Playwright, requires `pnpm --filter web build` first)

  ## Conventions
  - Server Components by default. Add `'use client'` only when needed.
  - Data fetching: use `cache()` from React, not SWR — we standardised on RSC.
  - Styling: Tailwind only. No CSS modules, no styled-components.

  ## Gotchas
  - `next dev --turbo` breaks our MDX pipeline. Use plain `next dev`.
  - Don't import from `apps/api` directly — always go through `packages/shared`.

  ## Owner
  - @web-team
  ```

  `apps/api/AGENTS.md` (Fastify+Prisma override):
  ```
  # apps/api — Fastify + Prisma
  See ../../AGENTS.md for repo-wide conventions.

  ## Commands
  - Dev: `pnpm --filter api dev` (port 4000, requires Postgres on :5432)
  - Migrations: `pnpm --filter api prisma migrate dev --name <name>`
  - Test: `pnpm --filter api test` (uses Testcontainers; Docker must be running)

  ## Conventions
  - Routes live in `src/routes/<resource>.ts`. One file per resource.
  - Validation: zod schemas in `src/schemas/`. Never trust `request.body` directly.
  - Errors: throw `AppError` from `src/errors.ts`, not raw `Error`.

  ## Gotchas
  - **NEVER** run `prisma migrate deploy` against the URL in `.env.production`. Use the migration GitHub Action.
  - Prisma client must be a singleton — import from `src/db.ts`, never `new PrismaClient()`.

  ## Owner
  - @api-team, on-call: PagerDuty service `api-prod`
  ```

- A Claude Code monorepo where the root needs the API's "never migrate prod" rule visible at session start. Add to root `CLAUDE.md`:
  ```
  ## Package-specific rules (auto-imported)
  @./apps/api/CLAUDE.md
  @./apps/web/CLAUDE.md
  ```
  This makes the nested files eager-loaded, not lazy-loaded, so the warning is in context before the agent plans any work.

- A Copilot-first repo uses `.github/instructions/`:
  ```
  .github/instructions/
    api.instructions.md      # applyTo: "apps/api/**/*.ts,apps/api/prisma/**"
    web.instructions.md      # applyTo: "apps/web/**/*.{ts,tsx}"
    sql.instructions.md      # applyTo: "**/*.sql,**/migrations/**"
  ```
  Each file opens with the frontmatter glob, then the same per-package content shape (commands, conventions, gotchas, owner). Editing `apps/api/src/routes/user.ts` triggers `api.instructions.md` + `sql.instructions.md` if the change touches `.sql`.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, which components got their own instruction files, and what each file documents that the root does not

## References

- AGENTS.md spec (precedence, nearest-wins, monorepo guidance): https://agents.md/
- AGENTS.md nested convention in monorepos (Datadog Frontend): https://dev.to/datadog-frontend-dev/steering-ai-agents-in-monorepos-with-agentsmd-13g0
- OpenAI Codex AGENTS.md cascading rules + AGENTS.override.md: https://developers.openai.com/codex/guides/agents-md
- Factory AGENTS.md docs: https://docs.factory.ai/cli/configuration/agents-md
- Claude Code nested CLAUDE.md hierarchical loading + lazy-load: https://dev.to/myougatheaxo/claude-code-in-monorepos-hierarchical-claudemd-and-package-scoped-instructions-1il9
- Claude Code `@path` import syntax (recursive, 5-hop max): https://mcpcat.io/guides/reference-other-files/
- GitHub Copilot `.github/instructions/*.instructions.md` with `applyTo:` glob frontmatter: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
- Copilot path-scoped instructions changelog (code review support): https://github.blog/changelog/2025-09-03-copilot-code-review-path-scoped-custom-instruction-file-support/
</system-reminder>
