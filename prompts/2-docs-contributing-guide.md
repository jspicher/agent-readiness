[Readiness Fix] <REPO_NAME> Contributing Guide

Fix the failing signal: Contributing Guide ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Contributing Guide
**Score**: [0/1]
**Description**: How to contribute — code style, PR process, commit conventions
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Contributing guide — a checked-in `CONTRIBUTING.md` (root, `.github/`, or `docs/`) that gives a contributor (human or agent) enough to open a correctly-formatted PR on the first try. PASS requires concrete, project-specific guidance in at least the following areas:

1. **Local dev setup** — exact commands to install deps, bootstrap the dev DB/env, and run the app locally. Either inline or a link to a README section that has them.
2. **Branch & PR workflow** — the source branch (`main`, `develop`, `staging`), how to name branches (e.g. `feat/<scope>-<slug>`), how to keep the branch up to date (rebase vs merge), and what the PR title/body must contain (issue link? changelog entry? screenshots for UI?).
3. **Commit convention** — an explicit format. Either Conventional Commits (`type(scope): subject`) with the allowed types enumerated, or another documented scheme. "Write descriptive commits" is NOT a convention.
4. **Code style & linting** — the exact lint/format commands the agent must run before opening a PR (`pnpm run lint`, `ruff check .`, `go fmt ./...`) and where the config lives. Auto-fix command if available.
5. **Test requirements** — which test commands must pass locally (`pnpm test`, `pytest -q`), whether new code requires new tests, and the minimum coverage bar if enforced.
6. **Review & merge expectations** — who reviews, expected response time, squash vs merge-commit, who merges (author or maintainer).
7. **Discovery** — file lives where GitHub auto-discovers it (root, `.github/`, or `docs/`) so it surfaces in the "Contributing" tab and on new-issue / new-PR pages.

Locations checked, in GitHub's resolution order: `.github/CONTRIBUTING.md` → `CONTRIBUTING.md` (root) → `docs/CONTRIBUTING.md`. Case-insensitive on the filename. A `Contributing` section inside README.md counts ONLY if it covers all seven areas above; a one-line "see issues, open PRs" does not.

A stub file (welcome message + "send PRs!") FAILs. A file that documents a workflow the repo no longer uses (references `master` when default is `main`, references `make test` when there is no Makefile) FAILs.

## Your Task

1. Explore the repo. Note: (a) any existing `CONTRIBUTING.md` / `.github/CONTRIBUTING.md` / `docs/CONTRIBUTING.md` / contributing section in `README.md`; (b) the real default branch (`git remote show origin | grep "HEAD branch"` or read `.git/HEAD` of a fresh clone); (c) the actual install / lint / test commands from `package.json` scripts, `pyproject.toml`, `Makefile`, `justfile`, `composer.json`, etc.; (d) whether the repo already enforces a commit format (look for `commitlint.config.*`, `.husky/commit-msg`, `.gitmessage`, prior commit log patterns); (e) PR / issue templates under `.github/`; (f) presence of `AGENTS.md` or `CLAUDE.md`.
2. Write or rewrite `CONTRIBUTING.md` so it covers every required area above with the repo's actual commands, branch names, and conventions. Place it at the repo root unless the repo already organizes community files under `.github/` (in which case use `.github/CONTRIBUTING.md`).
3. If a commit convention is not yet enforced, adopt Conventional Commits 1.0.0 and list the allowed types (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `build`, `ci`, `perf`, `style`, `revert`) with one-line meanings; show one good and one bad example from this repo's domain.
4. If `AGENTS.md` exists, add a short "AI / agent contributions" section to `CONTRIBUTING.md` that points to it for machine-readable build/test/lint commands, and add a reciprocal pointer from `AGENTS.md` to `CONTRIBUTING.md` for the human-facing workflow.
5. If `.github/PULL_REQUEST_TEMPLATE.md` or `.github/ISSUE_TEMPLATE/*` exist, ensure the PR title format and required body sections (checklist, test plan, screenshots) match what CONTRIBUTING.md says — fix whichever is wrong. If no templates exist and the repo is non-trivial, add a minimal `.github/PULL_REQUEST_TEMPLATE.md` that references CONTRIBUTING.md.
6. Verify: open a fresh "New Pull Request" page on GitHub for this repo (or run `gh pr create --web --draft` against a throwaway branch) and confirm the "contribution guidelines" link appears at the top of the PR body. Run every command CONTRIBUTING.md tells a contributor to run and confirm it exits 0 against a clean checkout.
7. Keep changes scoped — do not edit unrelated docs.
8. When done, open a PULL REQUEST and return the URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** stub files. A `CONTRIBUTING.md` containing only "Thanks for your interest! Please open a PR." FAILs the signal and signals zero project knowledge.
- **NO** generic "write clean code", "follow best practices", "be respectful" content with no actionable commands. Style guidance MUST be a command (`pnpm run lint`) or a link to a config file, not a vibe.
- **NO** missing commit convention. "Use descriptive commit messages" is not a convention. Either adopt Conventional Commits and name the types, or document the existing project-specific format.
- **NO** copy-pasted template from `contributing.md` / Mozilla Science / a starter kit with `<PROJECT_NAME>` placeholders left in, or with sections that reference tools the repo doesn't use (e.g. `npm test` in a Python repo, Slack channels that don't exist).
- **NO** commands that don't actually work. If you write `pnpm test`, run it. If `pnpm` is not the package manager, do not write `pnpm`.
- **NO** orphan file. CONTRIBUTING.md must live where GitHub auto-discovers it (root, `.github/`, or `docs/`). A file at `documentation/contributing.md` will NOT surface on new-PR pages and FAILs discovery.
- **NO** branch name that doesn't match reality. If the default branch is `main`, do not tell contributors to PR against `master`.
- **NO** committing a CONTRIBUTING that contradicts an existing `AGENTS.md` (different test command, different lint config). Reconcile both.
- **NO** removing existing useful content during rewrite — preserve project-specific context (e.g. CLA notes, DCO sign-off requirement, security-disclosure pointer) and integrate it into the new structure.

Examples of BAD fixes:
- `# Contributing\n\nPRs welcome! Please make sure your code is clean and tests pass. Thanks!` — zero of the seven required areas.
- A file that says "follow our coding standards" with no link to a style guide, lint config, or formatter command.
- "Use semantic commits" without listing the allowed types or showing an example — agents will guess wrong.
- A guide that mandates `npm install` in a repo whose lockfile is `pnpm-lock.yaml` — contributors and agents will install the wrong thing.
- A "Code of Conduct" section in lieu of any actual contribution workflow — that's `CODE_OF_CONDUCT.md`'s job, not CONTRIBUTING.md's.
- A 500-line file with three nested tables of contents and no concrete commands — length is not substance.

Examples of GOOD fixes:
- A `CONTRIBUTING.md` skeleton for a TypeScript monorepo:
  ```markdown
  # Contributing to <REPO_NAME>

  Thanks for contributing. This guide is the single source of truth for the
  PR workflow. For AI agents, see also [AGENTS.md](./AGENTS.md).

  ## Local setup
  Requires Node 20.x and pnpm 9.x.
  ```bash
  pnpm install
  cp .env.example .env.local      # fill in the values listed in README §Env
  pnpm db:migrate                 # spins up local Postgres via docker compose
  pnpm dev                        # http://localhost:3000
  ```

  ## Branch & PR workflow
  - Default branch: `main`. Branch off `main`; never PR into `develop` (it doesn't exist).
  - Branch name: `<type>/<short-slug>` — e.g. `feat/checkout-apple-pay`, `fix/login-csrf`.
  - Keep your branch current with `git rebase main` (we do not allow merge commits in PRs).
  - PR title MUST follow Conventional Commits (see below) — `commitlint` will block otherwise.
  - PR body MUST include: a link to the issue (`Closes #123`), a "Test plan" checklist, and
    before/after screenshots for any UI change. Use `.github/PULL_REQUEST_TEMPLATE.md`.

  ## Commit convention
  We use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
  Allowed types:
  - `feat` — user-facing feature
  - `fix` — bug fix
  - `docs` — docs only
  - `chore` — tooling, deps, no code change
  - `refactor` — code change that is neither feat nor fix
  - `test` — adding or fixing tests
  - `build`, `ci`, `perf`, `style`, `revert`

  Good: `feat(checkout): add Apple Pay button to cart drawer`
  Bad:  `updated checkout stuff`

  Breaking changes: add `!` after the type (`feat(api)!: drop /v1 endpoints`)
  AND a `BREAKING CHANGE:` footer.

  ## Code style
  ```bash
  pnpm run lint        # eslint + biome, must exit 0
  pnpm run lint:fix    # auto-fix where possible
  pnpm run typecheck   # tsc --noEmit
  ```
  Config: `eslint.config.mjs`, `biome.json`, `tsconfig.json`. Do not disable
  rules inline (`// eslint-disable-next-line`) without a comment explaining why.

  ## Tests
  ```bash
  pnpm test                       # vitest, ~30s
  pnpm test --coverage            # must stay >= 80% lines on touched files
  pnpm test:e2e                   # playwright, only required for UI changes
  ```
  New `feat` PRs MUST include tests. `fix` PRs MUST include a regression test
  unless you explain in the PR body why one isn't feasible.

  ## Review
  - One approval from a CODEOWNER is required (see `.github/CODEOWNERS`).
  - Reviewers respond within two business days; ping `#eng-reviews` on Slack if stalled.
  - Author merges via "Squash and merge". The squashed commit message MUST also
    follow Conventional Commits — edit the title at merge time if your last
    commit drifted.

  ## AI / agent contributions
  Agents must read [AGENTS.md](./AGENTS.md) for machine-readable commands and
  tool policy. Agent-authored PRs follow the same rules above and MUST include
  `[agent: <agent-name>]` in the PR body and a link to the run log if available.
  ```
- A Python repo's CONTRIBUTING that wires up real tools: `uv sync`, `ruff check .`, `ruff format .`, `pytest -q`, `mypy src/`, and points at `pyproject.toml` for the source of truth.
- A `.github/PULL_REQUEST_TEMPLATE.md` whose checklist (`[ ] ran pnpm test`, `[ ] updated docs`) matches verbatim what CONTRIBUTING.md tells contributors to do.
- A two-line "AI / agent contributions" section in CONTRIBUTING.md + reciprocal one-line pointer in AGENTS.md, so both files agree on which is canonical for which audience.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- GitHub: setting guidelines for repository contributors (auto-discovery, location precedence): https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors
- GitHub: about default community health files (`.github/CONTRIBUTING.md` fallback): https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
- Conventional Commits 1.0.0 specification: https://www.conventionalcommits.org/en/v1.0.0/
- commitlint (enforce Conventional Commits on PR titles / commits): https://commitlint.js.org/
- AGENTS.md format (the agent-facing companion to CONTRIBUTING.md): https://agents.md/
- contributing.md — sections a strong CONTRIBUTING file should include: https://contributing.md/how-to-build-contributing-md/
- GitHub PR / issue template structure (`.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/`): https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests
</system-reminder>
