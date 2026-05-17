[Readiness Fix] <REPO_NAME> Module-Level READMEs

Fix the failing signal: Module-Level READMEs ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Module-Level READMEs
**Score**: [0/1]
**Description**: Individual packages, crates, services, or modules in the repo have their own README that documents the unit for human consumers — purpose, install, usage example, public API, link back to root.
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Module-level READMEs (L3) – check for `README.md` files inside individual workspace members, not just the repo root. PASS requires at least TWO non-root READMEs, each carrying substantive package-specific content (>30 lines of real prose, not boilerplate). Evidence surfaces by ecosystem:

1. **pnpm / npm / yarn workspaces**: every entry in `pnpm-workspace.yaml` `packages:` or root `package.json` `"workspaces"` should have `packages/<name>/README.md` (or `apps/<name>/README.md`, `services/<name>/README.md`). For any package with `"private": false` in its `package.json`, the README is **mandatory** — npm/pnpm/yarn publish it to the registry and surface it as the package landing page.
2. **Turborepo / Nx / Rush monorepos**: same workspace rule as above; Turborepo's own `create-turbo` template ships per-app and per-package READMEs, and Nx's `nx g lib` generator creates one by default. A repo that has stripped those out fails this signal.
3. **Cargo workspaces (Rust)**: every entry in root `Cargo.toml` `[workspace] members` should have `crates/<name>/README.md` referenced from that crate's `Cargo.toml` via `readme = "README.md"`. crates.io requires the README path to resolve at publish time and renders it on the crate page.
4. **Go workspaces / multi-module repos**: each module listed in `go.work` `use (...)` or each top-level `cmd/<name>/` and `internal/<name>/` directory with a non-trivial public API should have its own README. `pkg.go.dev` renders `README.md` next to package docs.
5. **Python multi-package repos (Poetry / hatch / uv workspaces, src-layout monorepos)**: every distribution defined in `pyproject.toml` (root `[tool.uv.workspace] members` or per-package `pyproject.toml`) should have a sibling README. PyPI surfaces it as `long_description` when `readme = "README.md"` is set in `[project]`.

A subdirectory README that is (a) empty, (b) a literal copy of the root README, (c) just the package name as an H1, or (d) only the auto-generated `create-next-app` / `cargo new` boilerplate fails the substantive-content bar.

This signal is distinct from Component-Level Agent Guidance (feature #7): that signal evaluates AGENTS.md / CLAUDE.md / `.github/instructions/*.instructions.md` files written for **agents** with package-specific conventions. **This** signal evaluates README.md files written for **humans** (and registry pages) who need to consume or contribute to the package. Both can ship in the same directory; they do not substitute for each other.

## Your Task

1. Enumerate every workspace member the repo declares. Read root `pnpm-workspace.yaml`, root `package.json` `workspaces`, root `Cargo.toml` `[workspace.members]`, `go.work`, root `pyproject.toml` `[tool.uv.workspace]` / `[tool.hatch.envs]`, and `rush.json` `projects[]`. List every package directory you find and note which already have a README.
2. For each package without a substantive README, decide whether it is:
   - **Published** (npm `"private": false`, crate published to crates.io, Python dist on PyPI) → README is mandatory and rendered on the registry page; write a full consumer-facing README.
   - **Workspace-internal** (`"private": true`, internal crate, app target like `apps/web`) → README is still required for this signal, but its audience is contributors, not registry users; lean on contributor onboarding (run/build/test, dependency graph position).
3. Write each `<package>/README.md` with these sections, in this order:
   - **Title** — exact package name as published, in `# <name>` (e.g. `# @acme/utils`, `# acme-utils` for crates), one-line tagline.
   - **Purpose** — 2-4 sentences: what problem this package solves, who uses it, where it sits in the monorepo (`apps/*` consumer, `packages/*` shared lib, `services/*` deployable).
   - **Install** — registry install command for published packages (`pnpm add @acme/utils`, `cargo add acme-utils`, `pip install acme-utils`); for internal packages, the workspace dependency syntax (`"@acme/utils": "workspace:*"` in pnpm, `acme-utils = { path = "../utils" }` in Cargo).
   - **Usage** — at least ONE runnable code example showing the most common API call. Real imports, real function names — not `// TODO: example here`.
   - **Public API** — bulleted list of the exported symbols / commands / endpoints, each with a one-line description. Link to TypeDoc / rustdoc / pdoc output if generated.
   - **Local development** — commands that work from inside this directory (or via `pnpm --filter <name>`): `dev`, `build`, `test`, `lint`.
   - **Link back to root** — explicit `See [../../README.md](../../README.md) for repo-wide setup, contribution flow, and license.`
4. For published packages, wire the README into the package manifest so the registry picks it up:
   - **npm/pnpm**: add `"readme": "README.md"` or rely on the default; verify with `npm publish --dry-run` that `README.md` appears in the tarball.
   - **Cargo**: set `readme = "README.md"` under `[package]` in the crate's `Cargo.toml`.
   - **Python**: set `readme = "README.md"` in `[project]` of the package's `pyproject.toml`.
5. Add a CI check (`.github/workflows/readme-check.yml` or a `scripts/check-readmes.*` script wired into the existing lint job) that fails the build when a workspace member is missing `README.md` or its README is below a minimum size. See the working example below.
6. Verify the fix: from the repo root, run the CI check locally and confirm exit code 0. For at least one published package, run the publish dry-run (`npm publish --dry-run`, `cargo publish --dry-run`, `python -m build` then inspect the sdist) and confirm the README ships.
7. Keep changes focused on this signal — do not refactor package source code, rename packages, or rewrite the root README.
8. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** empty `packages/<name>/README.md`. A zero-byte file passes a naive `test -f` check but fails the substantive-content bar and is worse than no file because it suppresses contributor instinct to ask.
- **NO** copying the root README verbatim into every package. The root describes the monorepo; the package README describes the package. Identical content guarantees drift and tells consumers nothing about THIS unit.
- **NO** stub READMEs containing only the package name as an H1 and nothing else. The `cargo new` / `create-next-app` default counts as a stub — replace it.
- **NO** README that references commands or files that do not exist in the package. If the usage example imports `acme/utils/legacy` and that path was removed two refactors ago, the README is actively misleading.
- **NO** README without a runnable usage example. "See the source for usage" is not documentation. Consumers landing on the npm or crates.io page have no source view.
- **NO** README for a published package that omits the install command, the import statement, and the license — npm / crates.io render this as the landing page and an incomplete one tanks adoption.
- **NO** identical README scaffolding generated by a script with placeholder text left intact (`<TODO: describe purpose>`, `Lorem ipsum`). Either fill the placeholders or do not commit the file.
- **NO** CI check that only verifies file existence — it must also verify a minimum content length (~30 non-blank lines) to catch the empty-file and stub patterns.
- **NO** skipping internal-workspace packages. Apps in `apps/*` and private libs in `packages/*` still need a contributor-facing README; "it's private so it doesn't matter" is the most common excuse for this signal failing.

Examples of BAD fixes:

- Adding `packages/utils/README.md` containing only `# utils`. Stub.
- `for dir in packages/*; do cp README.md "$dir/README.md"; done`. Every package now claims to be the monorepo root.
- A `packages/api/README.md` whose usage example imports `from '@acme/api'` when the package is `@acme/api-client`. Wrong name, broken example, agent will propagate the bug.
- A CI check `find packages -name README.md | wc -l` compared against the number of packages. Passes when every package has an empty README.
- Adding READMEs to `packages/*` but skipping `apps/*` because "apps are not libraries" — apps still need build/run/deploy docs for contributors.
- Setting `readme = "README.md"` in `Cargo.toml` but the file does not exist at that path — `cargo publish` will fail at the next release.

Examples of GOOD fixes:

- A pnpm-workspaces monorepo with `apps/web`, `apps/api`, `packages/utils`, `packages/ui` ships four READMEs, each ~50-120 lines. `packages/utils/README.md` opens with `# @acme/utils`, documents install via `pnpm add @acme/utils`, shows three usage snippets (date helpers, retry, env parsing), lists every exported function with a one-line description, and links back to root. `apps/api/README.md` documents `pnpm --filter api dev`, the Postgres dependency, the migration command, and links to `apps/api/AGENTS.md` for agent-specific rules.

- A Cargo workspace with `crates/parser`, `crates/cli`, `crates/server` ships three READMEs. Each crate's `Cargo.toml` sets `readme = "README.md"`, `description`, and `repository`. The `crates/parser/README.md` is the same content crates.io renders at https://crates.io/crates/acme-parser — install, usage, feature flags, MSRV.

- A `packages/utils/README.md` skeleton (drop in and fill the bracketed slots):

  ```markdown
  # @acme/utils

  Shared TypeScript helpers for the Acme monorepo: date formatting, retry, env parsing.

  ## Purpose

  Single source of truth for utility functions used by both `apps/web` and `apps/api`.
  Lives in `packages/utils` and is consumed via the `workspace:*` protocol — do not
  publish to npm; internal-only.

  ## Install

  Inside the monorepo:

  ```json
  {
    "dependencies": {
      "@acme/utils": "workspace:*"
    }
  }
  ```

  Then `pnpm install` from the repo root.

  ## Usage

  ```ts
  import { retry, parseEnv, formatDate } from '@acme/utils';

  const data = await retry(() => fetch('/api/users'), { attempts: 3, backoffMs: 200 });
  const config = parseEnv(process.env, { PORT: 'number', DEBUG: 'boolean' });
  const stamp = formatDate(new Date(), 'yyyy-MM-dd');
  ```

  ## Public API

  - `retry(fn, opts)` — exponential-backoff retry wrapper. Throws after `opts.attempts`.
  - `parseEnv(source, schema)` — typed env parsing with zod under the hood.
  - `formatDate(date, pattern)` — date-fns wrapper pinned to UTC.
  - `sleep(ms)` — promise-based delay.

  Full type docs: `pnpm --filter @acme/utils docs` generates `docs/` via TypeDoc.

  ## Local development

  ```sh
  pnpm --filter @acme/utils build       # tsup
  pnpm --filter @acme/utils test        # vitest
  pnpm --filter @acme/utils test:watch
  pnpm --filter @acme/utils lint
  ```

  ## See also

  - Repo-wide setup, contribution flow, and license: [../../README.md](../../README.md)
  - Package-specific agent rules: [./AGENTS.md](./AGENTS.md)
  ```

- A CI check at `scripts/check-readmes.mjs` (Node, no deps), wired into the `lint` job:

  ```js
  #!/usr/bin/env node
  // scripts/check-readmes.mjs — fails CI if any workspace package lacks a substantive README.
  import { readFileSync, existsSync, statSync } from 'node:fs';
  import { join } from 'node:path';
  import fg from 'fast-glob'; // npm i -D fast-glob -- portable across Node 18/20/22; the built-in `globSync` from 'node:fs' is Node 22+ and still experimental

  const MIN_NON_BLANK_LINES = 30;
  const root = process.cwd();
  const pkgJson = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  const patterns = pkgJson.workspaces ?? [];
  const pkgDirs = patterns.flatMap((p) =>
    fg.sync(p, { cwd: root, onlyDirectories: true })
  );

  const failures = [];
  for (const dir of pkgDirs) {
    const readme = join(root, dir, 'README.md');
    if (!existsSync(readme)) {
      failures.push(`${dir}: README.md missing`);
      continue;
    }
    const nonBlank = readFileSync(readme, 'utf8')
      .split('\n')
      .filter((l) => l.trim().length > 0).length;
    if (nonBlank < MIN_NON_BLANK_LINES) {
      failures.push(`${dir}: README.md has ${nonBlank} non-blank lines, need >= ${MIN_NON_BLANK_LINES}`);
    }
  }

  if (failures.length) {
    console.error('Module-level README check failed:');
    for (const f of failures) console.error('  -', f);
    process.exit(1);
  }
  console.log(`OK: ${pkgDirs.length} workspace packages have substantive READMEs.`);
  ```

  Wire it into `.github/workflows/ci.yml`:

  ```yaml
  - name: Module READMEs
    run: node scripts/check-readmes.mjs
  ```

  For Cargo workspaces, the equivalent is a `cargo xtask check-readmes` or a shell loop over `cargo metadata --format-version 1 | jq -r '.workspace_members[]'` that asserts each member has `README.md` and a `readme = "README.md"` line in its `Cargo.toml`.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, how many package READMEs were added or rewritten, which packages are published vs internal, and confirm the CI check is wired into the existing lint/test job

## References

- pnpm workspaces (workspace member resolution): https://pnpm.io/workspaces
- npm publishing — README rendered on the registry page: https://docs.npmjs.com/cli/v10/configuring-npm/package-json#readme
- Turborepo monorepo handbook (per-package README convention): https://turborepo.com/docs/crafting-your-repository/structuring-a-repository
- Nx library generators (`nx g lib` ships README): https://nx.dev/nx-api/js/generators/library
- Cargo manifest `readme` field (crates.io publish requirement): https://doc.rust-lang.org/cargo/reference/manifest.html#the-readme-field
- crates.io README rendering: https://doc.rust-lang.org/cargo/reference/publishing.html
- Go `pkg.go.dev` README rendering for module pages: https://pkg.go.dev/about#adding-a-readme
- PyPI long_description via `readme` in `[project]`: https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
- uv workspaces (Python multi-package layout): https://docs.astral.sh/uv/concepts/projects/workspaces/
- Standard README spec (sections and ordering): https://github.com/RichardLitt/standard-readme
</system-reminder>
