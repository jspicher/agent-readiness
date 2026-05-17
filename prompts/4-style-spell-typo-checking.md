[Readiness Fix] <REPO_NAME> Spell/Typo Checking

Fix the failing signal: Spell/Typo Checking ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Spell/Typo Checking
**Score**: [0/1]
**Description**: Automated spelling checks run in CI or via pre-commit hooks against source, docs, and identifiers
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Spell / typo checking – check for a configured, automatically invoked spell checker. PASS requires at least one of the following with the checker actually wired into CI or a pre-commit hook (not just installed as a dependency):

1. **`typos`** (Rust, fast, 2026 default for mixed code/prose repos): `typos.toml` or `_typos.toml` at repo root with `[default.extend-words]` and/or `[files] extend-exclude` tuned to the project, AND either (a) a `.pre-commit-config.yaml` entry using `crate-ci/typos`, or (b) a `.github/workflows/*.yml` step invoking `crate-ci/typos-action@v1` or `typos --format brief` (failing the job on non-zero exit).
2. **`cspell`** (Node, integrates with VS Code spell-checker): `.cspell.json` / `cspell.config.yaml` at repo root with a populated `words` array (project dictionary) and a non-empty `ignorePaths` list, AND a CI step or `lint-staged` entry running `cspell "**/*.{md,ts,tsx,js,jsx,py}"` or `cspell-cli`. A `cspell` dev dependency without an invocation is FAIL.
3. **`codespell`** (Python, common misspellings only, fast): `pyproject.toml`/`setup.cfg` `[codespell]` section OR `.codespellrc` with `skip = ...` and `ignore-words-list = ...`, AND a pre-commit hook (`codespell-project/codespell`) or CI step. Running `codespell` with default args on a code repo without a skip list will drown in false positives — an unconfigured invocation is FAIL.
4. **`aspell`/`hunspell`** (legacy, prose-only): acceptable only when invoked from a Makefile or CI step against `docs/**/*.md` with a project dictionary file checked in.

Verify the checker is actually invoked: grep `.github/workflows/`, `.gitlab-ci.yml`, `.pre-commit-config.yaml`, `lefthook.yml`, `husky/*`, `package.json` `scripts`, and `Makefile` for the binary name. A config file with no invocation is dead config and FAILs. A CI step that uses `continue-on-error: true` or `|| true` to swallow the exit code also FAILs — the checker must be able to block a merge.

## Your Task

1. Explore the repo. Note: language mix (Markdown ratio vs. source), existing CI runner (GH Actions / GitLab / CircleCI), whether `pre-commit` / `husky` / `lefthook` is already wired up, and which spell-checker (if any) is already a dev dep.
2. Pick the right tool:
   - Mixed code + prose, no strong preference → `typos` (fastest, lowest false-positive rate, single binary).
   - Already on `pre-commit` with a Python stack → `codespell`.
   - Node/TS monorepo where contributors use the VS Code Code Spell Checker extension → `cspell` (config is shared).
3. Add the config file with project-tuned ignore patterns AND a starter dictionary seeded from real terms in the repo (product names, vendors, CLI flags, acronyms). Do not paste a generic template.
4. Wire the checker into either (a) a pre-commit hook that runs on `git commit`, or (b) a CI job that fails the build on typos. Both is better. The CI job must NOT use `continue-on-error: true`.
5. Run the checker once locally, accept the legitimate findings into the project dictionary, fix the real typos in a separate commit, and confirm the second run exits 0.
6. When done, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** installing the checker as a dev dependency without invoking it. A `package.json` line `"cspell": "^8.0.0"` that no script ever runs is dead weight.
- **NO** `continue-on-error: true`, `|| true`, `|| exit 0`, or `set +e` around the checker in CI — that turns the gate into a status badge.
- **NO** ignore patterns that swallow the bulk of the repo to "make it pass". A `typos.toml` with `extend-exclude = ["**/*.md", "src/**", "docs/**"]` is a checker that runs on nothing.
- **NO** auto-populated project dictionary. Do not pipe `cspell --unique --words-only` into `.cspell.json` `words` until it's silent — that turns the dictionary into a junk drawer and the next real typo lands inside it. Curate by hand.
- **NO** running the spell checker only against prose (`docs/**/*.md`) when the repo is 80% code. Variable names, log strings, and comments are where embarrassing typos live (`recieve`, `seperator`, `occured`, `pubic` for `public`).
- **NO** committing a `.cspell.json` that points at a missing `dictionaries/project.txt` file — the action will hard-fail before checking anything.
- **NO** running `codespell` with no `--skip` on a repo containing `node_modules/`, `vendor/`, lock files, minified JS, or binary fixtures. The job will take 20 minutes and surface thousands of false positives in third-party code.
- **NO** picking `aspell`/`hunspell` for a code repo. They tokenize on whitespace, do not understand `camelCase`/`snake_case`, and will flag every identifier.

Examples of BAD fixes:
- Adding `"spellcheck": "cspell '**/*.md'"` to `package.json` `scripts` with no CI step that calls `npm run spellcheck`. Local-only opt-in scripts do not count.
- A `.codespellrc` containing only `skip = *` — checks zero files.
- A `typos.toml` with a 400-line `extend-words` block copy-pasted from another project, mostly irrelevant terms, drowning the actual project dictionary.
- A GH Actions step `run: typos || true` — exit code thrown away.
- Adding `cspell` to `husky/pre-commit` but pointing it at `git diff --name-only --cached | xargs cspell` without `--no-must-find-files`, so empty diffs hard-fail and developers learn to `--no-verify` past it.

Examples of GOOD fixes:

### `typos` + GitHub Actions (recommended default)

`typos.toml`:
```toml
# https://github.com/crate-ci/typos
[default]
locale = "en-us"

[default.extend-words]
# Project-specific terms typos should NOT "correct"
# Format: "<what typos sees>" = "<what it is>"
hda     = "hda"      # disk identifier, not "had"
ot      = "ot"       # CLI short flag in this repo
serde   = "serde"    # Rust crate
crate   = "crate"
upsert  = "upsert"
clippy  = "clippy"

[default.extend-identifiers]
# Identifiers (camelCase / snake_case) that look like typos but are real
HashSetExt = "HashSetExt"

[files]
extend-exclude = [
  "CHANGELOG.md",
  "*.lock",
  "*.min.js",
  "*.min.css",
  "vendor/**",
  "node_modules/**",
  "target/**",
  "dist/**",
  "build/**",
  "tests/fixtures/**",
  "**/*.snap",
]
```

`.github/workflows/typos.yml`:
```yaml
name: typos
on:
  pull_request:
  push:
    branches: [main]
jobs:
  typos:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: crate-ci/typos@v1.24.6
        with:
          config: ./typos.toml
```

### `cspell` for a Node/TS monorepo

`.cspell.json`:
```json
{
  "$schema": "https://raw.githubusercontent.com/streetsidesoftware/cspell/main/cspell.schema.json",
  "version": "0.2",
  "language": "en",
  "dictionaryDefinitions": [
    { "name": "project", "path": "./dictionaries/project.txt", "addWords": true }
  ],
  "dictionaries": ["project", "typescript", "node", "npm", "html", "css"],
  "words": [
    "pnpm", "tsconfig", "vite", "vitest", "rollup", "esbuild",
    "<PRODUCT_NAME>", "<VENDOR_NAME>"
  ],
  "ignorePaths": [
    "node_modules/**", "dist/**", "build/**", "coverage/**",
    "pnpm-lock.yaml", "package-lock.json", "*.min.*",
    "**/*.snap", "**/__snapshots__/**", ".next/**"
  ],
  "ignoreRegExpList": [
    "/0x[0-9a-fA-F]+/",
    "/[A-Za-z0-9+/=]{40,}/"
  ]
}
```

`.husky/pre-commit` (with `lint-staged`):
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"
pnpm exec lint-staged
```

`package.json`:
```json
{
  "lint-staged": {
    "*.{md,mdx,ts,tsx,js,jsx,json}": "cspell --no-must-find-files --no-progress"
  },
  "scripts": {
    "spell": "cspell '**/*.{md,mdx,ts,tsx,js,jsx}' --no-progress"
  }
}
```

`.github/workflows/spell.yml`:
```yaml
name: spell
on: [pull_request]
jobs:
  cspell:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm run spell
```

### `codespell` via `pre-commit` (Python repo)

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/codespell-project/codespell
    rev: v2.3.0
    hooks:
      - id: codespell
        additional_dependencies: ["tomli"]
```

`pyproject.toml`:
```toml
[tool.codespell]
skip = "*.lock,*.po,*.svg,*.min.js,./.git,./.venv,./build,./dist,./node_modules,./tests/fixtures"
ignore-words-list = "crate,nd,fo,te,ot,<PROJECT_TERM>"
check-filenames = true
check-hidden = true
```

`.github/workflows/codespell.yml`:
```yaml
name: codespell
on: [pull_request]
jobs:
  codespell:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: codespell-project/actions-codespell@v2
        with:
          skip: "*.lock,*.po,./tests/fixtures"
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- `typos` (crate-ci): https://github.com/crate-ci/typos
- `typos-action` GH Actions: https://github.com/crate-ci/typos-action
- `typos` config reference: https://github.com/crate-ci/typos/blob/master/docs/reference.md
- `cspell` docs: https://cspell.org/
- `cspell` configuration: https://cspell.org/configuration/
- `cspell-cli` (GH Action): https://github.com/streetsidesoftware/cspell-action
- `codespell`: https://github.com/codespell-project/codespell
- `codespell` pre-commit hook: https://github.com/codespell-project/codespell#pre-commit-hook
- `actions-codespell` GH Action: https://github.com/codespell-project/actions-codespell
- `pre-commit` framework: https://pre-commit.com/
- `lint-staged`: https://github.com/lint-staged/lint-staged
- `husky`: https://typicode.github.io/husky/
</system-reminder>
