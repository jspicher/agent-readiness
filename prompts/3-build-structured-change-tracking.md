[Readiness Fix] <REPO_NAME> Structured Change Tracking

Fix the failing signal: Structured Change Tracking ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Structured Change Tracking
**Score**: [0/1]
**Description**: Changesets, conventional commits, or similar discipline that captures the intent of each change at the moment it lands
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Structured change tracking – check for an enforced convention that records the intent of each change at commit or PR time, in a format both agents and tools can parse. PASS requires one of the following, with actual enforcement (not just an opt-in convention):

1. **Conventional Commits enforced via commitlint + git hook**: a checked-in `commitlint.config.{js,cjs,mjs,ts}` (or `.commitlintrc.{json,yaml}`) that extends `@commitlint/config-conventional`, paired with a working `commit-msg` hook installed via Husky (`.husky/commit-msg`) or Lefthook (`lefthook.yml`). The hook MUST actually invoke commitlint — a `commitlint` package in `devDependencies` with no hook is a FAIL. Verify by running `git log -20 --pretty=%s` and confirming ≥80% of recent subjects match the `type(scope?): subject` shape (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `perf:`, `test:`, `build:`, `ci:`, `revert:`).
2. **Changesets** (`.changeset/` directory with a real `config.json` and ≥1 non-`README.md` `.md` file in the last 90 days, or shipped via a merged "Version Packages" release PR). Each changeset file MUST contain a frontmatter package/bump block (`---\n"@scope/pkg": patch\n---`) and a one-sentence summary. An empty `.changeset/` with only `README.md` and `config.json` is a FAIL when the repo has shipped releases since the directory was added — it proves the discipline has lapsed.
3. **CI-enforced PR title check** that rejects PRs whose title does not match Conventional Commits — `amannn/action-semantic-pull-request@v6.1.1` in `.github/workflows/*.yml`, or equivalent. The workflow MUST run on `pull_request` events with `types: [opened, edited, synchronize]` and fail the check (not just comment). A workflow that only posts a hint is a FAIL.
4. **Repo-specific change-intent file required by PR template**: a `.github/PULL_REQUEST_TEMPLATE.md` with a non-optional "Change type / summary" section AND a CI job (`danger-js`, custom `actions/github-script` step, or a `pr-lint` workflow) that fails when the section is empty or unchecked. A pretty template with no enforcement is a FAIL.

Distinguish this signal from feature #14 (Changelog) and #59 (Release notes automation). #57 is the DISCIPLINE that captures change intent at commit/PR time — the raw input. #14 is the human-readable OUTPUT file. #59 is the automation that turns #57 into #14. A repo can ship #14 by hand (PASS #14, FAIL #57). A repo can wire release-please without ever enforcing Conventional Commits (PASS #59 config but empty release PRs forever, FAIL #57).

A `CONTRIBUTING.md` sentence saying "please use Conventional Commits" with no commitlint, no hook, and no CI check is documentation, not discipline, and FAILs this signal.

## Your Task

1. Explore the repository to understand the current state:
   - `ls .changeset/ commitlint.config.* .commitlintrc* .husky/ lefthook.yml .github/workflows/ 2>/dev/null`
   - `git log -30 --pretty=%s` — what shape do recent commits take?
   - `cat package.json | jq '.devDependencies | with_entries(select(.key | test("commitlint|husky|lefthook|changesets|commitizen")))'` — what's already installed?
   - `ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null` — is there a PR template?
   - Decide: single package (commitlint + Husky) or monorepo (Changesets + commitlint). Check `pnpm-workspace.yaml` / `lerna.json` / `package.json` `workspaces` to confirm.
2. Make **substantive improvements**:
   - **Single-package repo** — install `@commitlint/cli` + `@commitlint/config-conventional` + `husky` as devDependencies, drop `commitlint.config.cjs` (see Working Example), run `npx husky init` then write `.husky/commit-msg` to invoke `npx --no-install commitlint --edit "$1"`. Add a `prepare: "husky"` script to `package.json` so fresh clones bootstrap the hook on `npm install`.
   - **Monorepo** — add Changesets (`pnpm add -Dw @changesets/cli && pnpm changeset init`), commit `.changeset/config.json` tuned to the repo's package layout (private packages, baseBranch), and ALSO add commitlint + Husky as above for commit hygiene. Wire `.github/workflows/release.yml` using `changesets/action@v1` so merged release PRs cut versions automatically.
   - **CI safety net** — add `.github/workflows/commitlint.yml` running `wagoid/commitlint-github-action@v6` on `pull_request` AND `push` so even a developer who bypassed Husky with `--no-verify` is caught. Add `amannn/action-semantic-pull-request@v6.1.1` to validate the PR title against the same ruleset.
   - **Contributor docs** — add a short `## Commit conventions` block to `CONTRIBUTING.md` (or `AGENTS.md`) pointing at https://www.conventionalcommits.org/en/v1.0.0/ and listing the allowed `type` values the project uses. If Changesets is wired, document `pnpm changeset` as the PR requirement for user-facing changes.
   - Optional but recommended: add `commitizen` + `cz-conventional-changelog` and a `commit: "cz"` script so contributors can run `npm run commit` for a guided prompt.
3. Verify the enforcement actually fires:
   - `echo "bad subject line" | npx commitlint` — MUST exit non-zero.
   - `echo "feat(api): add /healthz endpoint" | npx commitlint` — MUST exit zero.
   - `git commit --allow-empty -m "broken"` — MUST be blocked by the Husky hook (revert if it succeeds).
   - For Changesets: `pnpm changeset status --since=origin/main` — MUST report missing changesets if you add a workspace change without one.
   - Confirm the CI workflow appears in `gh workflow list` and runs on a draft PR.
4. Keep changes focused on this signal — do not retroactively rewrite git history, do not squash open branches, do not enable signed-commits or other unrelated hooks in the same PR.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** installing `commitlint` in `devDependencies` without writing the `.husky/commit-msg` hook — the package alone enforces nothing.
- **NO** `.husky/commit-msg` file that ships the hook script but skips `chmod +x` — Husky v9+ no longer needs the bit, but older Husky setups silently no-op without it. Verify the hook fires via `git commit -m "test"` before merging.
- **NO** `commitlint.config.cjs` that disables every rule (`rules: {"type-enum": [0]}`) — the rule set becomes ceremonial. Keep the `@commitlint/config-conventional` defaults and override only with reason.
- **NO** wiring the CI commitlint action on `push` to `main` only — by the time `main` sees a bad commit it is too late. Run on `pull_request` so the check blocks merge.
- **NO** PR title check via `semantic-pull-request` paired with squash-merge that uses the PR title as the commit subject AND a separate commitlint hook that allows different rules — the two MUST share the same ruleset (point both at `commitlint.config.cjs`).
- **NO** `.changeset/` directory with only `README.md` and `config.json` in a repo that has shipped 20 versions since — that means contributors stopped writing changesets months ago. Backfill or remove the directory.
- **NO** Changesets config (`config.json`) that lists every package under `ignore` — the tool becomes a no-op.
- **NO** committing the `prepare` script to `package.json` but failing to run `npm install` in CI before tests — the hook will not exist on the runner, and any downstream verification of the hook will pass vacuously.
- **NO** PR template asking "What type of change is this?" with no CI step that parses the answer — a template the bot does not read is decoration.
- **NO** stacking Changesets AND release-please AND semantic-release in the same repo. They will fight over `CHANGELOG.md` and version bumps. Pick one source of truth (Changesets for monorepos, release-please for single-package, semantic-release if you want fully automated tag-on-merge).

Examples of BAD fixes:
- Adding `@commitlint/cli` to `devDependencies` and a `commitlint.config.cjs` extending `config-conventional`, with no Husky hook and no CI step — nothing enforces it; the next `git commit -m "wip"` lands unchallenged.
- A `.husky/commit-msg` that runs `exit 0` "for now until the team agrees on rules" — the hook is a placebo.
- A `.changeset/README.md` recommending changesets in a repo whose last 50 PRs added zero changeset files — discipline never materialized.
- Adding `amannn/action-semantic-pull-request` with `validateSingleCommit: false` AND squash-merge AND no commitlint hook — devs commit `wip` 10 times, squash, and the PR title check passes on a polished subject while the underlying history is noise. Cover both surfaces.
- A `commitlint.config.cjs` with `rules: {"subject-case": [0], "body-max-line-length": [0], "type-enum": [0]}` — every rule muted, so the lint always passes.
- Setting `"husky": "^9"` in `devDependencies`, adding `prepare: "husky"`, but the `.husky/` directory is gitignored — fresh clones get no hooks.

Examples of GOOD fixes:
- For a single-package Node repo: commitlint v19 + Husky v9 wired correctly (see Working Example), plus `.github/workflows/commitlint.yml` running `wagoid/commitlint-github-action@v6` on `pull_request`. `CONTRIBUTING.md` gains an 8-line `## Commit conventions` block.
- For a pnpm monorepo: `pnpm add -Dw @changesets/cli @commitlint/cli @commitlint/config-conventional husky`, then `pnpm changeset init` (commits `.changeset/config.json` + `.changeset/README.md`), then the Husky hook for commits and `changesets/action@v1` for releases. PR template gains a `- [ ] I added a changeset (\`pnpm changeset\`) or this PR has no user-facing change` checkbox enforced by a custom `actions/github-script` step.
- A `.github/workflows/commitlint.yml` that checks out with `fetch-depth: 0`, runs `npx commitlint --from=${{ github.event.pull_request.base.sha }} --to=${{ github.event.pull_request.head.sha }}`, and fails the PR if any commit in the range violates the rules.
- An `AGENTS.md` section: `## Change tracking\n- Commits MUST follow Conventional Commits (https://www.conventionalcommits.org/en/v1.0.0/).\n- Allowed types: feat, fix, docs, refactor, perf, test, build, ci, chore, revert.\n- Scope is the package name in monorepos, omit otherwise.\n- Breaking changes: add \`!\` after the type (\`feat!:\`) AND a \`BREAKING CHANGE:\` footer.`

## Working Example

Minimum viable `commitlint.config.cjs` (single package or monorepo root):

```javascript
/** @type {import('@commitlint/types').UserConfig} */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert'],
    ],
    'subject-case': [2, 'never', ['upper-case', 'pascal-case', 'start-case']],
    'subject-max-length': [2, 'always', 100],
    'body-max-line-length': [1, 'always', 120],
    'footer-leading-blank': [2, 'always'],
  },
};
```

Paired `.husky/commit-msg` (Husky v9+). NOTE: the `#!/usr/bin/env sh` shebang line was deprecated in Husky v9.1.1 and is being removed in v10 — for v9.1.7+ omit it entirely; Husky runs the file directly:

```bash
npx --no-install commitlint --edit "$1"
```

Paired `package.json` additions:

```json
{
  "scripts": {
    "prepare": "husky",
    "commit": "cz"
  },
  "devDependencies": {
    "@commitlint/cli": "^19.5.0",
    "@commitlint/config-conventional": "^19.5.0",
    "commitizen": "^4.3.1",
    "cz-conventional-changelog": "^3.3.0",
    "husky": "^9.1.6"
  },
  "config": {
    "commitizen": { "path": "cz-conventional-changelog" }
  }
}
```

Paired `.github/workflows/commitlint.yml`:

```yaml
name: commitlint
on:
  pull_request:
    types: [opened, edited, synchronize, reopened]
permissions:
  contents: read
  pull-requests: read
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: wagoid/commitlint-github-action@v6
        with:
          configFile: commitlint.config.cjs
          failOnWarnings: false
          helpURL: https://www.conventionalcommits.org/en/v1.0.0/
```

For a monorepo, add `.changeset/config.json`:

```json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": ["@changesets/changelog-github", { "repo": "<owner>/<repo>" }],
  "commit": false,
  "fixed": [],
  "linked": [],
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": []
}
```

Paired `.github/workflows/release.yml` for Changesets:

```yaml
name: release
on:
  push:
    branches: [main]
permissions:
  contents: write
  pull-requests: write
  id-token: write
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - uses: changesets/action@v1
        with:
          publish: pnpm release
          version: pnpm changeset version
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

Example changeset file (`.changeset/quiet-pandas-dance.md`) authored by a contributor on each user-facing PR:

```markdown
---
"@scope/api": minor
"@scope/cli": patch
---

Add `/healthz` endpoint returning the deploy SHA and DB connectivity status. The CLI now surfaces the SHA in `mycli status`.
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Conventional Commits 1.0.0 spec: https://www.conventionalcommits.org/en/v1.0.0/
- commitlint (rules reference): https://commitlint.js.org/reference/rules.html
- `@commitlint/config-conventional`: https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional
- Husky v9 (commit-msg hook): https://typicode.github.io/husky/
- Lefthook (alternative to Husky, faster on large repos): https://github.com/evilmartians/lefthook
- Commitizen + cz-conventional-changelog (interactive prompt): https://github.com/commitizen/cz-cli
- Changesets (monorepo versioning): https://github.com/changesets/changesets
- Changesets config schema: https://github.com/changesets/changesets/blob/main/docs/config-file-options.md
- `changesets/action` GitHub Action: https://github.com/changesets/action
- `wagoid/commitlint-github-action` (CI enforcement): https://github.com/wagoid/commitlint-github-action
- `amannn/action-semantic-pull-request` (PR title linter): https://github.com/amannn/action-semantic-pull-request
- GitHub PR template docs: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
</system-reminder>
