[Readiness Fix] <REPO_NAME> Tool Version Pinning

Fix the failing signal: Tool Version Pinning ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Tool Version Pinning
**Score**: [0/1]
**Description**: Runtime and tool versions pinned to a checked-in file so every contributor (human or agent) resolves to the same `node`, `python`, `ruby`, `go`, etc.
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Tool version pinning – check for a checked-in, version-manager-readable file that locks the runtime(s) the project depends on to an EXACT version (major.minor.patch). PASS requires at least one of the following, and the pin must be specific enough that two contributors invoking the version manager land on byte-identical interpreters:

1. **`.tool-versions`** at repo root (asdf/mise compatible). Format is one line per tool: `<plugin> <version>`, e.g. `nodejs 22.11.0`. A line like `nodejs 22` (major-only) is a FAIL — it resolves to whatever 22.x is latest at install time. asdf docs: https://asdf-vm.com/manage/configuration.html; mise docs: https://mise.jdx.dev/configuration.html#tool-versions.
2. **`mise.toml`** (or `.mise.toml`, or `.config/mise/config.toml`) with a `[tools]` table, e.g. `node = "22.11.0"`. mise also accepts arrays for fallback (`python = ["3.12.7", "3.11.10"]`) — the first entry is the active version and must be exact. mise reference: https://mise.jdx.dev/configuration.html.
3. **Tool-specific fallback files**: `.node-version` (nvm, fnm, Volta read this), `.python-version` (pyenv), `.ruby-version` (rbenv), `.terraform-version` (tfenv), `.java-version` (jenv). Each contains a single exact-version string. These are weaker than `.tool-versions` (they pin one runtime each, no single source of truth) but they PASS this signal.
4. **`package.json` `volta`** block, e.g. `"volta": {"node": "22.11.0", "pnpm": "9.12.3"}`. Volta is Node-ecosystem only; if the repo also has Python or Ruby this alone is insufficient.

Also verify the pin is actually honored in CI: the project's CI workflow MUST read the pinned version (e.g. `jdx/mise-action@v2`, `actions/setup-node@v4` with `node-version-file: .nvmrc`, `actions/setup-python@v5` with `python-version-file: .python-version`). A CI job that hardcodes `node-version: 20` while `.tool-versions` says `nodejs 22.11.0` is a FAIL — the version pin is decorative because the agent's CI feedback loop runs on a different runtime than local.

A README sentence saying "we use Node 22" is documentation, not a pin, and FAILs this signal. A `package.json` `engines: { "node": ">=20" }` is a range, not a pin, and FAILs.

## Your Task

1. Explore the repository to identify every runtime the project depends on. Check `package.json` (engines + scripts), `pyproject.toml` / `requirements.txt`, `Gemfile`, `go.mod`, `Cargo.toml`, `Dockerfile` (`FROM` tags), `.github/workflows/*.yml` (`setup-*` actions), and any `README` install instructions. Note which runtimes have NO pin file today.
2. Pick ONE primary pinning mechanism — prefer `mise.toml` (modern, polyglot, fast) or `.tool-versions` (broadest compatibility — asdf, mise, and mise's predecessor rtx all read it). Tool-specific files (`.node-version`, `.python-version`) are acceptable only for single-runtime repos.
3. Make **substantive improvements**:
   - Create the pin file at repo root with EXACT versions (major.minor.patch) for every runtime the project actually uses. Resolve the version from the lockfile/CI logs/Dockerfile so the pin matches what the team is currently running, not the latest release.
   - Reconcile any `engines` field in `package.json` with the pin — either widen `engines` to a range that includes the pinned version, or remove `engines` if the pin is the new source of truth. Contradiction = silent bugs.
   - If a `volta` block exists in `package.json` and you are pinning via `.tool-versions` or `mise.toml`, remove the `volta` block (two pin systems WILL drift). If the repo is Node-only and the team already uses Volta, keep `volta` and document that choice — do not add a second mechanism.
   - Update CI to honor the pin. For mise: add a `jdx/mise-action@v2` step BEFORE any `setup-*` step. For asdf-only `.tool-versions`: use `asdf-vm/actions/install@v3`. For `.node-version` / `.python-version`: pass `node-version-file:` / `python-version-file:` to the `setup-*` action instead of hardcoding a `node-version:` string.
   - Add a one-line install hint to `README.md` (`mise install` or `asdf install`) so new contributors and agent onboarding scripts know how to materialize the pin.
4. Verify: run `mise current` (or `asdf current`) locally and confirm it resolves the pinned version without prompting for installation. Push to a branch and confirm the CI workflow's setup step logs the same exact version string.
5. Keep changes focused on this signal — do not bump dependencies, change lockfiles, or touch Dockerfiles unless the Dockerfile `FROM` tag contradicts the pin (in which case align it).
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** major-only pins. `nodejs 22`, `python 3.12`, `ruby 3` all FAIL — they drift the moment a new patch ships. Resolve to `22.11.0`, `3.12.7`, `3.3.5`.
- **NO** wildcard / range syntax in the pin file. `.tool-versions` does not support ranges; `nodejs latest` and `nodejs lts` defeat the entire signal.
- **NO** committing a `.tool-versions` that contradicts a `package.json` `engines` field, a `volta` block, or a `Dockerfile FROM node:20-alpine`. Pick one source of truth and align the rest.
- **NO** pinning runtimes the repo does not actually use (don't add `ruby 3.3.5` to a TypeScript-only repo just to look thorough). Every pin must trace to an actual `require`/`import`/build step.
- **NO** committing the pin file but leaving CI hardcoded to a different version. The agent's iteration loop runs in CI; if CI ignores the pin, the agent's feedback signal is poisoned.
- **NO** mixing two version managers (Volta + mise, asdf + `.python-version` consumed by pyenv) without making one authoritative. Two systems will silently disagree under stress.
- **NO** pinning to a version that is not actually installed anywhere — verify the version against `node --version`, `python --version`, or the lockfile's recorded engine before committing.

Examples of BAD fixes:
- `.tool-versions` containing `nodejs 22` (major-only — resolves to whatever 22.x mise has cached).
- `mise.toml` with `node = "latest"` — the entire point of pinning is to NOT be `latest`.
- Adding `.node-version` with `22.11.0` while `package.json` still says `"engines": {"node": ">=18"}` AND `.github/workflows/ci.yml` hardcodes `node-version: 20`. Three sources, three answers.
- A `.tool-versions` listing `nodejs 22.11.0\npython 3.12.7\nruby 3.3.5\ngo 1.23.4` on a repo that only imports Node — the extra pins are noise that will rot.
- Pinning via `package.json` `volta` block AND adding `mise.toml` "for redundancy" — the redundancy is the bug.

Examples of GOOD fixes:
- Polyglot repo with `mise.toml`:
  ```toml
  [tools]
  node = "22.11.0"
  python = "3.12.7"
  rust = "1.82.0"
  pnpm = "9.12.3"
  ```
  paired with a `.github/workflows/ci.yml` step:
  ```yaml
  - uses: jdx/mise-action@v2
    with:
      version: 2024.11.8
      install: true
      cache: true
  - run: pnpm install --frozen-lockfile
  - run: pnpm test
  ```
  and a README line: `Install runtimes: \`mise install\` (or \`asdf install\` if you prefer asdf — \`.tool-versions\` is also committed).`
- Node-only repo using Volta exclusively: `package.json` with `"volta": {"node": "22.11.0", "pnpm": "9.12.3"}`, no `engines` field, CI uses `actions/setup-node@v4` with `node-version-file: package.json`. Remove any `.nvmrc` / `.tool-versions` to avoid drift.
- Python-only repo: `.python-version` containing `3.12.7`, `pyproject.toml`'s `requires-python = "==3.12.7"` matches, CI uses `actions/setup-python@v5` with `python-version-file: .python-version`.

## Related signals (different concerns — don't conflate)

- **#98 Reproducible dev environment** is the heavier solution: devcontainer / nix / docker-compose dev image. Tool version pinning is the lightweight prerequisite. Doing #99 does not satisfy #98; #98 should consume the pin file inside its container build.
- **#91 Dependency lockfile** pins library versions (`package-lock.json`, `poetry.lock`). Tool version pinning pins the INTERPRETER that reads the lockfile. Both are required; one does not substitute for the other.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- mise configuration & `.tool-versions` / `mise.toml`: https://mise.jdx.dev/configuration.html
- mise GitHub Action (`jdx/mise-action`): https://github.com/jdx/mise-action
- asdf `.tool-versions` reference: https://asdf-vm.com/manage/configuration.html
- asdf GitHub Action: https://github.com/asdf-vm/actions
- Volta (Node-ecosystem pinning via `package.json`): https://docs.volta.sh/advanced/pnp
- pyenv `.python-version`: https://github.com/pyenv/pyenv#choosing-the-python-version
- `actions/setup-node` `node-version-file`: https://github.com/actions/setup-node#node-version-file
- `actions/setup-python` `python-version-file`: https://github.com/actions/setup-python#using-the-python-version-file-input
- step-security analysis of CI runtime drift: https://www.stepsecurity.io/blog/pinning-actions-and-runtimes
</system-reminder>
