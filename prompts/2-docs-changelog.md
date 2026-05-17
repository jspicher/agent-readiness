[Readiness Fix] <REPO_NAME> Changelog

Fix the failing signal: Changelog ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Changelog
**Score**: [0/1]
**Description**: History of what changed and how entries should be written, so an agent can scan recent releases for behavior shifts before editing code
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Changelog – check for a human-readable history of changes that an agent can scan before modifying related code. PASS requires one of the following:

1. **`CHANGELOG.md` (or `CHANGES.md`, `HISTORY.md`, `NEWS.md`) at repo root** that follows the Keep a Changelog 1.1.0 format: per-version sections headed `## [X.Y.Z] - YYYY-MM-DD`, grouped into `Added` / `Changed` / `Deprecated` / `Removed` / `Fixed` / `Security` subheads, with an `[Unreleased]` section at the top for in-flight work. The file MUST have at least one entry in the last 180 days (run `git log -1 --format=%cs -- CHANGELOG.md` and compare).
2. **GitHub Releases** published via the Releases tab with one release per tagged version. Each release MUST contain prose notes describing user-facing changes (not just an auto-generated commit list). Run `gh release list --limit 5` — PASS requires ≥1 release in the last 180 days AND release bodies that are not empty/`""`/auto-generated SHA dumps.
3. **Both** — a committed `CHANGELOG.md` plus mirrored GitHub Releases (recommended for libraries; the file lets agents grep history without network, Releases give consumers diff links).

Distinguish this signal from feature #59 (Automated release notes). #14 evaluates whether the SOURCE OF TRUTH document exists and is current. #59 evaluates whether an automation tool (release-please, changesets, git-cliff, conventional-changelog, release-it, auto-changelog) generates it. A repo can PASS #14 with a hand-written `CHANGELOG.md` and FAIL #59; conversely a repo can have release-please configured but FAIL #14 if the bot's release PR has been sitting open for 8 months with no merges.

A `CHANGELOG.md` that contains only `## [Unreleased]` with no shipped versions is a FAIL. A SHA list (`* abc123 fix bug`) is a FAIL — entries must be user-facing. A `git log` dump committed as `CHANGELOG.md` is a FAIL.

## Your Task

1. Explore the repository to understand the current state of release history:
   - `ls CHANGELOG.md CHANGES.md HISTORY.md NEWS.md 2>/dev/null`
   - `gh release list --limit 10` — see what's been published
   - `git tag --sort=-creatordate | head -20` — see version tags
   - `git log --oneline --since="180 days ago" | head -50` — gauge change volume
   - Check `package.json` / `pyproject.toml` / `Cargo.toml` for current version
   - Look for existing automation: `release-please-config.json`, `.changeset/`, `.github/workflows/release*.yml`, `cliff.toml`, `.release-it.json`
2. Make **substantive improvements**:
   - Create or repair `CHANGELOG.md` at repo root using the Keep a Changelog 1.1.0 skeleton (see Working Example below). The first line MUST link to https://keepachangelog.com/en/1.1.0/ so future contributors know the format.
   - Backfill at least the last 3 shipped versions (or all versions if fewer than 3 exist). Use `git log <prev-tag>..<tag> --no-merges --pretty="%s"` to harvest commits, then REWRITE each into a user-facing entry grouped under the correct heading. Do NOT paste raw `git log` output.
   - Add an `[Unreleased]` section at the top with any work merged since the last tag.
   - If the repo already publishes GitHub Releases but has no `CHANGELOG.md`, generate the file from the Release bodies (`gh release list --json tagName,publishedAt,body`) — do not lose that history.
   - If commit history follows Conventional Commits, wire up an automation tool so this never breaks again: drop a `release-please-config.json` + `.release-please-manifest.json` + `.github/workflows/release-please.yml` (single-package node/python repo), or `.changeset/config.json` + `pnpm changeset` workflow (monorepo), or `cliff.toml` (Rust / any repo without a JS toolchain). Pick ONE — do not stack two automations.
3. Document the contribution rule in `CONTRIBUTING.md` (or `AGENTS.md` if that's where the repo's process docs live): "Every PR with a user-facing change MUST add an entry under `## [Unreleased]` in `CHANGELOG.md` under the correct heading (`Added` / `Changed` / `Deprecated` / `Removed` / `Fixed` / `Security`)." If you wired up Changesets, replace that sentence with "Every PR with a user-facing change MUST include a changeset (`pnpm changeset`)."
4. Verify:
   - `npx keep-a-changelog --version` then `npx keep-a-changelog format CHANGELOG.md` — confirms it parses against the spec.
   - For release-please: `npx release-please release-pr --dry-run --repo-url=<owner>/<repo> --token=$GITHUB_TOKEN` — confirms config loads.
   - For Changesets: `pnpm changeset status` — confirms config is valid.
   - For git-cliff: `git-cliff --tag v0.0.0 --unreleased` — confirms `cliff.toml` parses and produces output.
5. Keep changes focused on this signal — do not bump versions, cut a release, or refactor unrelated config in the same PR.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** committing an empty `CHANGELOG.md` (or one containing only `# Changelog`) just to make the file exist. The signal checks for actual entries.
- **NO** `## [Unreleased]` that perpetually accumulates with no shipped version below it. The first version section ships when the next tag goes out — backfill the most recent tag at minimum so the file has a non-Unreleased section today.
- **NO** pasting raw `git log --oneline` output as the changelog body. Entries must be rewritten in user-facing prose ("Fixed crash when uploading PDFs > 10 MB" — not "fix: bump pdf-lib"). SHA lists are a FAIL.
- **NO** changelog grouped by author, month, or sprint. Group by Keep a Changelog headings (`Added` / `Changed` / `Deprecated` / `Removed` / `Fixed` / `Security`) — agents and humans both grep for these.
- **NO** format that breaks parsers: missing `## [X.Y.Z] - YYYY-MM-DD` header, dates in MM/DD/YYYY (use ISO 8601), version without brackets, headings other than h2 for versions and h3 for change types. The `keep-a-changelog` npm parser is the de facto validator — your file must round-trip through it.
- **NO** stacking automations. release-please AND changesets in the same repo will fight each other. Pick one.
- **NO** wiring up release-please without the `release-type` matching the repo (e.g. `release-type: "node"` on a Python repo). Check `pyproject.toml` / `package.json` / `Cargo.toml` first.
- **NO** GitHub-Releases-only solution for a library that consumers install offline or vendor. The CHANGELOG.md belongs in the repo so agents can read it without `gh` auth.
- **NO** deleting existing release history when migrating from one format to another. Preserve every shipped version.

Examples of BAD fixes:
- `CHANGELOG.md` containing only `# Changelog\n\n## [Unreleased]\n` — no shipped versions, fails the freshness check immediately.
- A "changelog" generated by `git log --oneline > CHANGELOG.md` — this is a SHA list, not a changelog.
- Adding release-please config but the repo's commits are not Conventional Commits — the next release PR will be empty.
- Backfilling the last 3 versions but inventing dates because git tags weren't dated — use `git log -1 --format=%cs <tag>` to get the real tag date.
- Committing release-please config AND a hand-edited `CHANGELOG.md` with manual `## [X.Y.Z]` entries — release-please will fight you on every release.

Examples of GOOD fixes:
- A fresh `CHANGELOG.md` with the Keep a Changelog header, an `[Unreleased]` section listing in-flight changes, and the last 3 tagged versions backfilled from `git log <prev>..<curr>` with each commit rewritten into a one-line user-facing entry under the right heading.
- Adding `release-please-config.json` + `.release-please-manifest.json` + `.github/workflows/release-please.yml` to a Node monorepo that already uses Conventional Commits, plus a sentence in `CONTRIBUTING.md` pointing contributors at https://www.conventionalcommits.org/en/v1.0.0/.
- For a Rust repo: `cliff.toml` generated from `git-cliff --init`, tuned to group `feat:` under Added, `fix:` under Fixed, `perf:` under Changed, with a CI job that runs `git-cliff --tag $NEW_TAG --prepend CHANGELOG.md` on tag push.
- An `AGENTS.md` block: `## Changelog policy\n- User-facing changes require a CHANGELOG entry in the same PR under [Unreleased].\n- Headings: Added / Changed / Deprecated / Removed / Fixed / Security.\n- Format: Keep a Changelog 1.1.0 (https://keepachangelog.com/en/1.1.0/).`

## Working Example

Minimum viable `CHANGELOG.md` skeleton:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New `--dry-run` flag on `mytool export` for previewing output without writing files.

### Fixed
- Race condition in `Worker.shutdown()` that occasionally left zombie processes.

## [1.4.0] - 2026-04-22

### Added
- OAuth2 device code flow for headless authentication.
- `MYTOOL_LOG_FORMAT=json` for structured logging.

### Changed
- Default request timeout raised from 30s to 60s for cold-start cloud functions.

### Deprecated
- `--legacy-auth` flag; use `--auth-method=oauth2` instead. Will be removed in 2.0.0.

### Fixed
- Crash when uploading files larger than 100 MB on Windows.

### Security
- Bumped `axios` to 1.7.4 to address CVE-2024-39338 (SSRF).

## [1.3.1] - 2026-02-14

### Fixed
- Config loader silently dropped values from `~/.mytoolrc` when a project-local
  config existed (regression from 1.3.0).

## [1.3.0] - 2026-01-08

### Added
- Initial public release of the plugin API (`mytool plugin install <name>`).

[Unreleased]: https://github.com/<owner>/<repo>/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/<owner>/<repo>/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/<owner>/<repo>/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/<owner>/<repo>/releases/tag/v1.3.0
```

Minimum viable `release-please-config.json` for a single Node package:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "release-type": "node",
  "packages": {
    ".": {
      "changelog-path": "CHANGELOG.md",
      "include-component-in-tag": false,
      "draft": false,
      "prerelease": false
    }
  },
  "changelog-sections": [
    {"type": "feat", "section": "Added"},
    {"type": "fix", "section": "Fixed"},
    {"type": "perf", "section": "Changed"},
    {"type": "revert", "section": "Removed"},
    {"type": "deps", "section": "Security", "hidden": false}
  ]
}
```

Paired `.release-please-manifest.json`:

```json
{ ".": "1.4.0" }
```

Paired `.github/workflows/release-please.yml`:

```yaml
name: release-please
on:
  push:
    branches: [main]
permissions:
  contents: write
  pull-requests: write
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Keep a Changelog 1.1.0 spec: https://keepachangelog.com/en/1.1.0/
- Semantic Versioning 2.0.0: https://semver.org/spec/v2.0.0.html
- Conventional Commits 1.0.0: https://www.conventionalcommits.org/en/v1.0.0/
- release-please (Google, recommended for repos using Conventional Commits): https://github.com/googleapis/release-please
- release-please GitHub Action: https://github.com/googleapis/release-please-action
- Changesets (recommended for JS/TS monorepos): https://github.com/changesets/changesets
- git-cliff (Rust + language-agnostic, generates from git history): https://git-cliff.org/docs/
- conventional-changelog (lower-level toolkit, used inside many of the above): https://github.com/conventional-changelog/conventional-changelog
- release-it (interactive release runner with changelog plugins): https://github.com/release-it/release-it
- auto-changelog (zero-config, parses git tags directly): https://github.com/CookPete/auto-changelog
- keep-a-changelog parser/formatter (validates the file): https://github.com/oscarotero/keep-a-changelog
- GitHub Releases API + `gh release` CLI: https://cli.github.com/manual/gh_release
</system-reminder>
