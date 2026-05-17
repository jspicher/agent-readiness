# Agent Readiness Criteria

Features that make a codebase ready for AI-assisted development, organized into
seven pillars.  Each feature is tagged with a maturity level (1-5) so coverage
can be summarized as both a flat percentage and a tier.

Lineage: pillars 1-5 originated from cluster analysis of 123 repositories; the
2026 expansion added an Agent-OS Readiness pillar derived from industry
research synthesis on autonomous-agent operating-system patterns.

Every feature answers one question: *if this is missing, what goes wrong for
the agent?*  Features marked **conditional** apply only when the codebase has
the relevant subsystem (DB, monorepo, multi-service, web frontend, etc.) and
should be marked `—` (not applicable) when the prerequisite is absent.

Levels:
- **L1** Basic — language-agnostic essentials
- **L2** Intermediate — agent-friendly tooling
- **L3** Advanced — measurement and discipline
- **L4** Power-user — full automation and observability
- **L5** Self-improving — closed feedback loops

---

## Pillar 1 · Agent Instructions

How the repo tells AI agents what to do, what to avoid, and how the codebase
works.  This is the highest-signal pillar — it's the difference between an
agent that understands the project and one that's guessing.

| # | L | Feature | What to look for | Evidence |
|---|---|---------|------------------|----------|
| 1 | L2 | **Agent instruction file** | A dedicated file telling agents how to work in this repo | `AGENTS.md`, `CLAUDE.md`, `COPILOT.md`, `CONVENTIONS.md` at root |
| 2 | L2 | **AI IDE configuration** | Settings or rules for AI-powered editors/IDEs | `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`, `.github/instructions/`, `.claude/settings.json` |
| 3 | L3 | **Multi-model support** | Instructions across different AI models/tools, not locked to one vendor | 2+ distinct agent config types from features 1–2 present in same repo |
| 4 | L3 | **Agent skills or capabilities** | Packaged, reusable abilities the agent can invoke | `.claude/skills/`, `.factory/skills/`, `skill.md` files, tool definition files |
| 5 | L3 | **Agent tool integration manifest** *(profile-aware)* | Machine-readable declaration of the agent's tool surface (which CLIs/APIs/MCP servers the agent is allowed to use). PASS via any of: (a) MCP manifest with at least one server entry; (b) `.claude/settings.json` with non-empty `permissions.allow` or `permissions.deny`; (c) `.factory/settings.json` with `commandAllowlist`/`commandDenylist`; (d) Codex agent-runner config; (e) repo-local agent-tool-policy doc cross-referenced from AGENTS.md; (f) **explicit opt-out**: a manifest file (`.claude/settings.json`, `.mcp.json`, etc.) that contains a `"policy": "intentionally-unscoped"` field OR a `"_comment"` explaining the choice (e.g., `"_comment": "Solo private repo, agent has unrestricted local access by design"`). Mark `—` (N/A) when `team_scale=solo AND visibility=private AND no manifest file exists at all` (the criterion is structurally premature for a single-developer prototype). FAIL only when: a manifest file exists with truly empty/default scoping AND there is no explicit opt-out AND the repo is not solo-private. Stub configs without rationale on multi-contributor or public repos still fail -- that's where the agent's tool surface ambiguity actually causes problems. | MCP manifest, `.claude/settings.json` with non-empty `permissions`, `.factory/settings.json` with `commandAllowlist`, agent-tool-policy doc, OR explicit `"policy": "intentionally-unscoped"` / `"_comment"` rationale in the manifest |
| 6 | L4 | **Agent prompt library** | Pre-built prompts for common tasks in this repo | `.github/prompts/`, `prompts/` directory, prompt template files |
| 7 | L4 | **Component-level agent guidance** | Different parts of the codebase have their own agent instructions | `AGENTS.md` or instruction files in subdirectories |
| 8 | L1 | **README with build/run/test** | README includes the commands to build, run, and test | `README.md` containing code blocks with build/install/test commands |
| 9 | L2 | **Contributing guide** | How to contribute — code style, PR process, commit conventions | `CONTRIBUTING.md`, `docs/contributing.md`, contributing section in README |
| 10 | L2 | **Architecture documentation** | High-level overview of how the system is structured and why | `ARCHITECTURE.md`, `docs/architecture/`, Mermaid/PlantUML diagrams |
| 11 | L3 | **API documentation** | Reference docs for the project's interfaces | `openapi.yaml`, generated HTML docs, `doc.go` files, Swagger UI |
| 12 | L2 | **Inline code documentation** | Doc comments, docstrings — agents read these to understand intent | JSDoc `/** */` blocks, Python docstrings, GoDoc, Rust `///` |
| 13 | L3 | **Runnable examples** *(evidence varies by `repo_kind`)* | Working example code the agent can study and imitate. **Libraries / SDKs / CLIs / frameworks**: strict -- require `examples/`, `_examples/`, or example apps with READMEs that exercise the public API. **Apps**: broaden -- accept tested recipes (`docs/recipes/`), pattern docs (`docs/patterns/`), playbooks (`docs/playbooks/`), or curated route/component reference implementations that are explicitly referenced from AGENTS.md/README as imitation targets. Tests alone do NOT pass; empty/unreferenced directories do NOT pass. **Monorepos**: apply per-package (strict for published packages, app rule for contained apps). | Libraries: `examples/`, `_examples/`, example apps with READMEs. Apps: `docs/recipes/`, `docs/patterns/`, `docs/playbooks/` cross-linked from AGENTS.md/README |
| 14 | L2 | **Changelog** | History of what changed and how entries should be written | `CHANGELOG.md`, `CHANGES.md`, GitHub Releases |
| 15 | L1 | **Environment variable documentation** | Template or docs for required env vars | `.env.example`, `.env.template`, env var table in README |
| 16 | L3 | **Documentation site or directory** | Organized docs beyond the README | `docs/`, Docusaurus/Sphinx/MkDocs/VitePress config |
| 17 | L4 | **Decision records** | Documented reasoning behind past architectural choices | `doc/adr/`, `decisions/`, `rfcs/`, numbered ADR files |
| 18 | L3 | **Module-level READMEs** | Individual packages/modules have their own READMEs | `packages/*/README.md`, per-crate/per-module READMEs |
| 19 | L3 | **Documentation freshness** | Docs updated within ~180 days of latest code change | `git log` recency on AGENTS.md / README / docs/ vs main |
| 20 | L5 | **AGENTS.md freshness validation** | CI check that AGENTS.md stays consistent with code | CI workflow runs a script that validates AGENTS.md (e.g. `validate-agents-md.mjs`) |
| 21 | L4 | **Automated documentation generation** | Build step that regenerates docs from code | JSDoc/TypeDoc/Sphinx/Swagger autogen pipeline; docs auto-update workflow |

---

## Pillar 2 · Feedback Loops

How quickly and clearly the agent learns whether its changes are correct.
Fast, clear feedback is the difference between an agent that converges and one
that spirals.

| # | L | Feature | What to look for | Evidence |
|---|---|---------|------------------|----------|
| 22 | L1 | **Linter** | Static analysis catching bugs and style issues | `.eslintrc.*`, `ruff.toml`, `.golangci.yml`, `clippy.toml`, `pylintrc` |
| 23 | L1 | **Formatter** | Auto-formatter enforcing consistent style | `.prettierrc`, `rustfmt.toml`, `[tool.black]`, `gofmt`/`goimports` in CI |
| 24 | L1 | **Type checking** | Static type system or type checker | `tsconfig.json strict`, `mypy.ini`, `[tool.mypy]`, `py.typed` |
| 25 | L2 | **Pre-commit hooks** | Checks that run before commit | `.pre-commit-config.yaml`, `.husky/`, `lefthook.yml`, `lint-staged` |
| 26 | L1 | **Unit tests** | Tests for individual components | `*_test.go`, `*_test.py`, `*.spec.ts`, `test/`, `__tests__/` |
| 27 | L3 | **Integration tests** | Tests verifying components work together | `test/integration/`, `tests/e2e/`, API test suites |
| 28 | L4 | **End-to-end tests** | Full system/browser tests | Playwright config, Cypress config, Selenium tests, `e2e/` |
| 29 | L2 | **Test coverage measurement** | Coverage tracking with thresholds enforced in CI | `.codecov.yml`, `coverageThreshold` in jest, `--cov` in pytest, Go cover profile |
| 30 | L1 | **CI pipeline** | Automated checks on every push or PR | `.github/workflows/ci.yml`, `.circleci/config.yml`, `.gitlab-ci.yml`, `Jenkinsfile` |
| 31 | L4 | **Fast CI feedback** | CI completes quickly enough for agent iteration | CI under 10 min documented or measurable; parallel jobs; test splitting |
| 32 | L1 | **Test run documentation** | Agent knows exactly how to run which tests | Test commands in README, AGENTS.md, CONTRIBUTING.md, or Makefile help |
| 33 | L3 | **Config/schema validation** | YAML, JSON, config files validated automatically | `yamllint`, JSON `$schema` refs, `actionlint` in CI, `taplo` for TOML |
| 34 | L4 | **Snapshot or golden-file tests** | Tests that detect unexpected output changes | `__snapshots__/`, `.snap` files, `testdata/` golden files, VCR cassettes |
| 35 | L4 | **Benchmark suite** | Performance tests the agent can run for regression checks | `bench/`, `*_bench_test.go`, pytest-benchmark, Criterion.rs |
| 36 | L3 | **Warnings-as-errors** | Compiler/runtime warnings treated as failures | `-Werror`, `warningsAsErrors` in build config, `filterwarnings = error` |
| 37 | L4 | **Spell/typo checking** | Automated spelling checks in CI or hooks | `.cspell.json`, `codespell` in pre-commit, `typos.toml` |
| 38 | L3 | **Test isolation** | Tests are configured for parallel-safe execution | Test runner config (vitest, jest) with parallel workers; isolated DB/env per test |
| 39 | L4 | **Flaky test detection** | System identifies and tracks unstable tests | jest-retry, pytest-rerunfailures, BuildPulse, CI quarantine mechanism |
| 40 | L4 | **Test performance tracking** | Test suite duration measured and monitored | `--reporter=verbose` with timing, test analytics platform, slow-test alerts |
| 41 | L2 | **Test file naming conventions** | Consistent naming enforced by test runner config | vitest `include` pattern, jest `testMatch`, pytest `python_files` |
| 42 | L3 | **Strict typing enforcement** | Strict mode is non-optional, enforced in CI | `tsconfig.json strict: true`, `[tool.mypy] strict = true`, CI fails on missing types |
| 43 | L3 | **Dead code detection** | Static analysis flags unused exports/functions | `knip`, `ts-prune`, `vulture`, `unimport`, `deadcode` (Go), Sonar |
| 44 | L4 | **Duplicate code detection** | DRY scanning configured | jscpd, simian, Sonar duplications, `--check-duplication` in CI |
| 45 | L3 | **Large file detection** | Tooling detects/prevents overly large files | LFS attributes, eslint `max-lines`, file-size pre-commit hook, CI size check |
| 46 | L4 | **Code modularization enforcement** | Architectural boundaries enforced | `eslint-plugin-boundaries`, `dependency-cruiser`, `import-linter`, ts-arch |
| 47 | L3 | **Technical debt markers tracking** | TODO/FIXME/HACK comments inventoried | TODO-tracker bot, ESLint `no-warning-comments`, Sonar SQALE, `todocheck` in CI |
| 48 | L5 | **Cyclomatic complexity tracking** | Complexity thresholds enforced | Sonar quality gate, ESLint `complexity`, radon (Py), gocyclo |
| 49 | L4 | **N+1 query detection** *(conditional: DB-using app)* | DB-aware lint or runtime detection | Bullet (Rails), `query-counter` middleware, `pyproject` plugins, ORM warnings |

---

## Pillar 3 · Workflows & Automation

The processes that support agent-driven development — how work is structured,
tracked, and shipped.

| # | L | Feature | What to look for | Evidence |
|---|---|---------|------------------|----------|
| 50 | L2 | **Issue templates** | Structured templates for bug reports, feature requests | `.github/ISSUE_TEMPLATE/` with `bug_report.md`, `feature_request.md` |
| 51 | L2 | **PR template** | Template that guides PR descriptions toward reviewable AND recoverable changes. File existence is necessary but NOT sufficient. PASS requires the template to include at minimum: (a) a **Summary** or **Description** section; (b) a **Testing** section -- either a checklist with concrete commands the reviewer can verify, OR a free-form section that names what was tested; (c) a **Risk / Rollback** section (or equivalent: "How to revert", "Blast radius", "Recovery plan") -- this is the recoverability signal Pillar 7 cares about, and the criterion now enforces it even for L2. Optional but encouraged: Breaking Changes section, Related Issues / Closes, Checklist (secrets, conventional commits, scope). FAIL when the file exists but is missing any of the three required sections, OR when it contains only a `## Summary` heading with no other guidance. See the recommended template in `docs/factory-ai-readiness/remediate-prompts/2-taskdiscovery-pr-templates.md`. | `.github/pull_request_template.md` (or `.github/PULL_REQUEST_TEMPLATE.md`, or GitLab `.gitlab/merge_request_templates/`) containing Summary + Testing + Risk/Rollback sections |
| 52 | L2 | **Dependency update automation** | Automated PRs for dependency updates | `.github/dependabot.yml`, `renovate.json`, `.renovaterc` |
| 53 | L3 | **Release automation** | Automated release pipeline (build, tag, publish) | Release workflow in CI, `semantic-release`, GoReleaser, `release-please` |
| 54 | L2 | **Branch protection** *(conditional: GitHub plan supports protection rules / rulesets)* | Protected main with required checks | Branch protection rules, merge queue config, required status checks. Mark `—` (N/A) if `gh api repos/{owner}/{repo}/rules/branches/main` returns HTTP 403 "Upgrade to GitHub Pro" -- private repos on GitHub Free cannot enable rulesets and the criterion is structurally unsatisfiable on that plan. |
| 55 | L4 | **Merge automation** | Merge queue, auto-merge, or merge bot | `merge_group` trigger, Mergify, auto-merge labels, `gh pr merge --auto` |
| 56 | L1 | **Task runner** | Single entry point for common commands | `Makefile`, `Justfile`, `Taskfile.yml`, `package.json` scripts, `Rakefile` |
| 57 | L3 | **Structured change tracking** | Changesets, conventional commits, or similar discipline | `.changeset/`, `commitlint`, conventional commit enforcement |
| 58 | L4 | **CI concurrency control** | Cancel-in-progress, concurrency groups | `concurrency:` blocks in GitHub Actions, `cancel-in-progress: true` |
| 59 | L3 | **Automated release notes** | Changelog/release notes from commits or PRs | `release-please`, `auto-changelog`, `git-cliff`, `conventional-changelog` |
| 60 | L4 | **Stale issue/PR management** *(conditional: not solo+private)* | Automation to close or label stale items. Mark `—` (N/A) when `team_scale=solo AND visibility=private` -- a single maintainer on a closed repo has no stale-bot use case and flagging this becomes checklist theater. Still applies (and should fail) when the repo has multiple contributors OR accepts outside contributions. | `.github/workflows/stale.yml`, stale bot config, lifecycle labels |
| 61 | L4 | **Label automation** | Automatic PR/issue labeling based on paths or content | `.github/labeler.yml`, label-sync, auto-label workflows |
| 62 | L4 | **Multi-platform CI** | CI matrix covering multiple OS, arch, or runtime versions | `matrix:` with multiple OS or language versions |
| 63 | L3 | **Deployment automation** | Automated deployment pipeline | Deploy workflow on merge/tag, staging + production environments |
| 64 | L3 | **Automated code review checks** | Bot-driven review checks beyond CI | Danger.js, review bot, CODEOWNERS-required reviews, SonarCloud bot |
| 65 | L4 | **Automated PR review generation** | LLM/static-tool comments on PRs | SonarCloud quality-gate comments, CodeRabbit, Greptile, Codiumate |
| 66 | L4 | **Automated security review generation** | Security findings posted automatically on PRs | gitleaks workflow, CodeQL bot, Snyk PR comments, Trivy reports in CI |
| 67 | L4 | **Feature flag infrastructure** | Flag system configured for safe rollouts | LaunchDarkly/Statsig/Unleash/GrowthBook SDK, custom flag system |
| 68 | L5 | **Dead feature flag detection** *(conditional: flag system present)* | Tooling OR documented retirement process detects stale/dead flags | LaunchDarkly Insights, Unleash dashboard, custom flag-age script in CI. Also passes when a documented flag-retirement lifecycle (e.g. `docs/operations/feature-flags.md` describing how to ripgrep references, inline the truthful branch, and remove the env entry) is committed -- a documented manual process beats no process. |
| 69 | L4 | **Deployment frequency** | Multiple deploys per week with automation | Vercel/Render/Fly auto-deploy on push, frequent successful CI on main |
| 70 | L5 | **Progressive rollout** *(conditional: production system)* | Canary or percentage-based deployments | Argo Rollouts, Flagger, Vercel rolling deploys, Cloudflare gradual deploy |
| 71 | L5 | **Rollback automation** *(conditional: production system)* | One-click or automated rollback capability | Vercel rollback, Argo Rollouts revert, GitHub Actions rollback workflow |

---

## Pillar 4 · Policy & Governance

Rules, ownership, and constraints the agent must know about and respect.

| # | L | Feature | What to look for | Evidence |
|---|---|---------|------------------|----------|
| 72 | L1 | **Comprehensive .gitignore** | Covers secrets, build artifacts, IDE files, agent artifacts | `.gitignore` with `.env`, `node_modules/`, build dirs, `.cursor/`, `.claude/` |
| 73 | L2 | **License** | The agent unambiguously knows the licensing posture. Accepts any of: (a) a LICENSE/MIT-LICENSE/COPYING/LICENSE.md file; (b) a clear proprietary-copyright statement at the top of README ("All Rights Reserved", "Proprietary - © {Company}") combined with a `package.json` signal (`"license": "UNLICENSED"` or `"private": true`); (c) a dedicated COPYRIGHT file with a proprietary notice. Vague statements ("This is a private project") do NOT pass. **For published OSS packages** (`package.json` has `publishConfig` or `"private": false`), require an SPDX-compliant LICENSE file -- README mention alone is insufficient. | `LICENSE`, `MIT-LICENSE`, `COPYING`, `LICENSE.md`, `COPYRIGHT`, OR README "All Rights Reserved" + package.json proprietary signal |
| 74 | L2 | **Code ownership** | File/directory ownership mapping | `CODEOWNERS`, `.github/CODEOWNERS`, area-owners docs |
| 75 | L2 | **Security policy** | How to report vulnerabilities | `SECURITY.md`, `.github/security.md`, security reporting instructions |
| 76 | L2 | **Code of conduct** *(conditional: accepts_external_contributors)* | Community standards. Mark `—` (N/A) when `accepts_external_contributors=false` -- CoC governs outside-contributor interactions; for private repos with no external contribution model, the criterion is structurally inapplicable. Required when the repo is public + OSS-licensed + has CONTRIBUTING.md targeting outsiders. | `CODE_OF_CONDUCT.md`, conduct link in contributing guide |
| 77 | L3 | **AI usage policy** | Documented guidelines for AI/agent contributions | AI policy in AGENTS.md, CONTRIBUTING.md, or standalone doc |
| 78 | L2 | **Secrets management** | Secrets via environment/vault, not hardcoded | `${{ secrets.* }}` in CI, vault config, `.env.example` without values |
| 79 | L3 | **Vulnerability scanning** | Automated CVE scanning in CI | `.github/workflows/codeql.yml`, Snyk, `gosec`, Trivy, Dependabot security alerts |
| 80 | L3 | **Secret scanning** | Continuous scanning for accidentally committed secrets | gitleaks workflow on push/PR, GitHub secret scanning enabled, trufflehog in CI |
| 81 | L3 | **Sensitive data log scrubbing** | Logger redacts/masks PII, tokens, credentials | Logger config with redact lists; structured logger middleware; explicit scrub patterns |
| 82 | L3 | **Minimum dependency release age** | Policy delays adopting brand-new releases (supply-chain mitigation) | Renovate `minimumReleaseAge` / `stabilityDays`; documented policy; CI gate |
| 83 | L2 | **Git attributes** | Line endings, diff drivers, LFS, linguist overrides | `.gitattributes` with `text=auto`, `linguist-generated`, LFS tracking |
| 84 | L3 | **Contributor agreement** *(conditional: accepts_external_contributors)* | DCO sign-off or CLA process. Mark `—` (N/A) when `accepts_external_contributors=false` -- DCO/CLA exists to handle IP from outside contributors; it has no function on repos with a closed contribution model. Required when the repo is public + OSS-licensed + has CONTRIBUTING.md targeting outsiders. | DCO bot config, `Signed-off-by` requirement, CLA-assistant config |
| 85 | L4 | **Governance model** *(conditional: not solo+private)* | Documented ownership, decision-making, and escalation paths. Evidence varies by repo profile: **public OSS / external-contributor repos** require formal `GOVERNANCE.md` / `MAINTAINERS.md` with maintainer roles + decision process. **Internal multi-team repos** can satisfy via `CODEOWNERS` + escalation docs (e.g., `docs/operations/escalation.md`, team-ownership table in AGENTS.md, on-call rotation doc). Mark `—` (N/A) only when `team_scale=solo AND visibility=private`. | `GOVERNANCE.md`, `MAINTAINERS.md`, OR `CODEOWNERS` + escalation docs for internal multi-team |
| 86 | L3 | **CI workflow validation** | CI config itself is linted/validated | `actionlint` step, `circleci config validate`, CI schema validation |
| 87 | L2 | **Environment separation** | Distinct configs for dev/test/prod | `.env.test`, `.env.production`, environment-specific config dirs |
| 88 | L4 | **DAST scanning** *(conditional: web-facing app with meaningful attack surface)* | Dynamic security testing in CI | OWASP ZAP, Burp, Nuclei, Probely workflow on staging. Mark `—` (N/A) for small static/SSG sites, marketing pages, or directory listings with no user input beyond contact forms -- the cost of standing up a DAST pipeline outweighs the threat. Apps with auth, multi-tenant data, payment flows, or APIs accepting untrusted input should still fail this if no DAST is configured. |
| 89 | L4 | **PII handling** *(conditional: user-data app)* | PII detection and handling tooling | Presidio, ScrubadubScrubber, regex-based redaction in CI; documented PII policy |
| 90 | L4 | **Privacy compliance infrastructure** *(conditional: user-data app + jurisdiction)* | GDPR/CCPA infrastructure | Cookie banner component, data-retention policy doc, DPIA records, consent management |

---

## Pillar 5 · Build & Dev Environment

Can the agent actually build, run, and iterate on the project?  Reproducibility
and speed matter — an agent that can't build can't do anything.

| # | L | Feature | What to look for | Evidence |
|---|---|---------|------------------|----------|
| 91 | L1 | **Dependency lockfile** | Pinned dependency versions for reproducible installs | `package-lock.json`, `pnpm-lock.yaml`, `uv.lock`, `Cargo.lock`, `go.sum` |
| 92 | L1 | **Single-command build** | One documented command to build the entire project | `make build`, `npm run build`, `cargo build` documented in README |
| 93 | L1 | **Single-command dev setup** | One command to bootstrap a working dev environment | `bin/setup`, `make dev`, `scripts/bootstrap.sh`, `just setup` |
| 94 | L2 | **Dev container** | Containerized dev environment definition | `.devcontainer/devcontainer.json` |
| 95 | L3 | **Devcontainer runnable** *(conditional: devcontainer present)* | Devcontainer actually builds and starts | CI workflow that exercises devcontainer; documentation of last-known-good build |
| 96 | L2 | **Containerized services** | Docker-based local development stack | `Dockerfile`, `docker-compose.yml`, `compose.yaml` with dev services |
| 97 | L3 | **Local services setup documented** | docker-compose OR docs describing how to run dependencies | docker-compose.yml; local-setup section in README/AGENTS.md |
| 98 | L4 | **Reproducible environment** | Declarative, hermetic dev environment | `flake.nix`, `shell.nix`, `devbox.json` |
| 99 | L2 | **Tool version pinning** | Runtime/tool versions pinned to a file | `.tool-versions`, `mise.toml`, `.node-version`, `.python-version` |
| 100 | L3 | **Monorepo orchestration** *(conditional: monorepo)* | Tooling for multi-package repositories | Workspace config, Turborepo, Nx, Bazel, Cargo workspace |
| 101 | L4 | **Version drift detection** *(conditional: monorepo)* | Tooling detects cross-package version drift | syncpack, depsync, Nx version generator, custom drift script in CI |
| 102 | L3 | **Build caching** | Caching for faster rebuilds | CI cache steps (`actions/cache`), Turborepo remote cache, ccache/sccache |
| 103 | L4 | **Build performance tracking** | Build duration measured and trended | Build-time metrics export, build-cache hit rate dashboard, CI duration trend |
| 104 | L3 | **Heavy dependency / bundle analysis** | Bundle size or dependency-weight analysis | `@next/bundle-analyzer`, webpack-bundle-analyzer, source-map-explorer, depscloud |
| 105 | L3 | **Unused dependencies detection** | Tooling detects unused deps | depcheck, knip, npm-check, deptry (Py), cargo-machete |
| 106 | L4 | **Cross-platform support** *(evidence varies by `repo_kind`)* | **Libraries / SDKs / CLIs / frameworks**: strict -- require multi-OS CI matrix, cross-compilation, or multi-arch Docker. A library failing to test on macOS/Windows ships brittle artifacts. **Apps (hosted)**: evaluate dev-loop portability instead of artifact portability. PASS when local task runners (npm scripts, Makefile, Justfile) normalize paths/configs across darwin/linux/win -- e.g., `cross-env` usage, no hard-coded `/bin/sh`-only or `cmd.exe`-only invocations, no unnormalized path separators, or a documented "Windows users: use WSL" policy with WSL setup steps. FAIL when scripts demonstrably break on a major dev platform with no documented workaround. The deploy target (Vercel Linux, Fly, Render, etc.) being single-OS is NOT itself a failure for apps. **Monorepos**: apply per-package. | Libraries: CI matrix with multiple OS, cross-compilation, multi-arch Docker. Apps: cross-env usage, portable scripts, OR documented single-OS-dev policy with WSL/devcontainer escape hatch |
| 107 | L4 | **Cloud dev environment** | Cloud-based workspace configuration | `.devcontainer/` with Codespaces features, `.gitpod.yml`, GitHub Codespaces ready |
| 108 | L3 | **Package manager determinism** | The agent can reproduce the same dependency tree across machines. Accepts any of: `.npmrc`/`.yarnrc.yml`/`.pnpmfile.cjs` with `engine-strict` / frozen-lockfile / registry pinning; `"packageManager"` field in `package.json` (Corepack pin); `"engines"` enforced in CI (e.g., `npm ci --engine-strict`); `.tool-versions` / `mise.toml` / `.node-version` runtime pin; CI workflow uses `npm ci` / `pnpm install --frozen-lockfile` / `yarn install --immutable`; equivalents for `pip.conf`, `.cargo/config.toml`. Lockfile alone is NOT sufficient (already covered by #91). Fails only when installation is genuinely ambiguous: no lockfile pin + no runtime pin + no CI-frozen-install discipline. | `.npmrc`, `.yarnrc.yml`, `"packageManager"` field, Corepack, `engines` enforced in CI, `.tool-versions`, `mise.toml`, `pip.conf`, `.cargo/config.toml` |
| 109 | L3 | **Database schema definition** *(conditional: DB-using app)* | Schema files for the application database | `migrations/` directory, `schema.sql`, Prisma `schema.prisma`, Alembic versions |

---

## Pillar 6 · Observability *(NEW)*

Production runtime observability that an agent uses to verify its changes,
debug regressions, and reason about real behavior.  Filtered for agent-relevance
per the adversarial review (industry research downgraded operator-only criteria
like profiling and circuit breakers to "moderate hygiene").

| # | L | Feature | What to look for | Evidence |
|---|---|---------|------------------|----------|
| 110 | L2 | **Structured logging** | Logs use structured format the agent can parse | JSON logs, structured logger lib (pino, structlog, zap, slog), log middleware |
| 111 | L2 | **Error tracking with context** | Sentry/Bugsnag with source maps + breadcrumbs | `@sentry/*` SDK, source-map upload step, instrumentation files, contextualized capture |
| 112 | L3 | **Health check endpoints** | Liveness/readiness probes the agent can hit | `/health`, `/healthz`, `/ready` route in app code |
| 113 | L3 | **Metrics collection** *(conditional: production system)* | Engineering telemetry for performance | OTel SDK, Prometheus scraping, Datadog/New Relic agent, custom metrics |
| 114 | L4 | **Distributed tracing** *(conditional: any production system that emits requests, single-service included)* | Request tracing within or across services | OTel tracing SDK, Jaeger/Tempo backend, trace propagation middleware. Single-service apps PASS when an APM/tracing SDK is wired (e.g. `@sentry/nextjs` with `instrumentation.ts` / `instrumentation-client.ts`, or `@opentelemetry/*` deps with an exporter configured) -- per-request trace IDs and breadcrumb context still produce the diagnostic value the criterion measures. |
| 115 | L3 | **Alerting configured** *(conditional: production system)* | Paging integration, alert rules, OR an error->issue pipeline that routes signals to humans | Alert rules in CI/CD, PagerDuty/OpsGenie/Slack integration, on-call rotation. Also passes when an automated pipeline turns errors into actionable work items -- e.g. a `.github/workflows/sentry-issue.yml` + `src/app/api/sentry-webhook/route.ts` that creates a labeled GitHub issue per Sentry alert. The bar is "someone notices and can act", not "PagerDuty specifically". |
| 116 | L2 | **Runbooks documented** *(conditional: production system)* | Incident response playbooks | `docs/runbooks/`, `docs/operations/`, runbook section in repo |
| 117 | L4 | **Code quality metrics dashboard** | Coverage/complexity/maintainability monitored | SonarCloud, Codacy, Code Climate, custom dashboards |
| 118 | L4 | **Profiling instrumentation** *(conditional: perf-sensitive app)* | Continuous or on-demand profiling | py-spy, pprof, Node `--prof`, async-profiler, Datadog continuous profiler |
| 119 | L4 | **Circuit breakers** *(conditional: external-dependency-heavy)* | Resilience pattern around remote calls | Hystrix, Resilience4j, opossum, polly, custom retry/timeout middleware |
| 120 | L5 | **Error → insight pipeline** | Errors flow from tracking to actionable issues | Sentry-GitHub integration, webhook → issue/ticket, error-grouping → PR draft |

---

## Pillar 7 · Agent-OS Readiness *(NEW)*

The control plane an autonomous agent needs to act safely.  This pillar
addresses the gap external research identified as the dividing line between
"AI-assisted-ready" and "autonomous-agent-ready" — bounded authority,
observability of agent actions, reproducible execution, recoverable failures.

Sourced from `docs/factory-ai-readiness/_research-external.md` synthesis of
industry consensus on agent operating systems (2025-2026).

| # | L | Feature | What to look for | Evidence |
|---|---|---------|------------------|----------|
| 121 | L2 | **Tool allowlist / permission policy** | Documented or enforced list of CLIs/APIs/destinations the agent may use | `.claude/settings.json` `permissions` block, `.factory/settings.json` `commandAllowlist`/`commandDenylist`, agent-tool allowlist file (note: `.factory/policy.json` does NOT exist — Factory's real path is `settings.json`) |
| 122 | L3 | **Sandboxing / blast-radius bounds** | Agent runs in a constrained environment with limited filesystem/network access | Devcontainer with restricted mounts, agent-runner sandbox script, network egress allowlist |
| 123 | L3 | **Hooks for context preservation** | Pre/post-action hooks that capture or persist agent state | `.claude/hooks/`, `.factory/hooks/`, PreCompact / SessionEnd / PreCommit agent hooks |
| 124 | L3 | **SBOM presence** | Software Bill of Materials generated or committed | `sbom.json`, `cyclonedx.json`, syft/grype output, SBOM upload in release workflow |
| 125 | L4 | **Provenance attestations** | Cryptographic attestations on builds/commits | `sigstore` / `cosign` signing, in-toto attestations, GitHub `actions/attest-build-provenance` |
| 126 | L4 | **Agent audit trail with stable run IDs** | Every agent action is logged with a run ID linkable to commit/PR/deploy | Run-ID convention in commit messages or PR labels, agent-run log dir, telemetry hooks |
| 127 | L4 | **Replayable evaluation harness** | Agent behavior tested against fixed scenarios | `evals/` directory, golden-prompt fixtures, agent regression-test workflow in CI |
| 128 | L4 | **Kill-switch infrastructure** | Mechanism to halt agent activity quickly | Feature flag scoped to "agent runs," disable-agent script, repo-level circuit breaker |
| 129 | L3 | **Human escalation path** | Documented handoff with sufficient context for a human to take over | Agent leaves a status note, `escalate-to-human.md` template, PR description includes context |
| 130 | L4 | **Agent registry / ownership metadata** | Documented map of which agent owns which scope | `.agents/registry.yaml`, agent-ownership table in AGENTS.md, agent identity in CODEOWNERS |
| 131 | L3 | **Per-repo policy visibility** | Agent can read its constraints (off-limits paths, approval-required actions) | Machine-readable policy file (`agent-policy.json`, `.agent/restricted-paths.md`), referenced from AGENTS.md |
| 132 | L3 | **Cost telemetry for agent runs** | Token usage / run cost is tracked and attributable | OTel attributes for agent ops, agent-cost log line per run, cost-per-PR dashboard |

---

## Summary

| Pillar | Features | Question answered |
|--------|---------:|-------------------|
| 1. Agent Instructions | 21 | Does the agent know what to do? |
| 2. Feedback Loops | 28 | Does the agent know if it's right? |
| 3. Workflows & Automation | 22 | Does the process support agent work? |
| 4. Policy & Governance | 19 | Does the agent know the rules? |
| 5. Build & Dev Environment | 19 | Can the agent build and run the project? |
| 6. Observability | 11 | Can the agent verify production behavior? |
| 7. Agent-OS Readiness | 12 | Can the agent act safely and recoverably? |
| **Total** | **132** | |

### Conditional features

Conditional features apply only when the corresponding subsystem is present.
Mark as `—` (not applicable) and note the reason rather than failing.

| Condition | Features |
|-----------|----------|
| Database-using app | #49 N+1, #109 DB schema |
| Monorepo | #100 Monorepo orch, #101 Version drift |
| Multi-service / microservices | #114 Distributed tracing |
| Production system (deployed, not lib) | #70 Progressive rollout, #71 Rollback, #113 Metrics, #115 Alerting, #116 Runbooks |
| Web-facing app | #88 DAST |
| User-data / PII-handling app | #89 PII handling, #90 Privacy compliance |
| Devcontainer present | #95 Devcontainer runnable |
| Feature flag system present | #68 Dead flag detection |
| External-dependency-heavy | #119 Circuit breakers |
| Perf-sensitive app | #118 Profiling |

### Profile-driven gates (Step 0 dimensions)

Set by the repo profile in Step 0 of SKILL.md. When a profile dimension is `unknown`, the criterion defaults to **strict** (it applies; N/A is not granted).

| Profile dimension | Value triggering N/A or evidence shift | Features affected |
|---|---|---|
| `accepts_external_contributors=false` | N/A | #76 Code of conduct, #84 Contributor agreement |
| `team_scale=solo AND visibility=private` | N/A | #60 Stale issue/PR management, #85 Governance model |
| `repo_kind` (varies by value) | Evidence surface shifts (not N/A) | #13 Runnable examples, #106 Cross-platform support |
| Repo declares no agent tool surface | N/A | #5 Agent tool integration manifest |
| (No gate; evidence list broadened) | -- | #73 License, #108 Package manager determinism |

### Maturity-level rollup

When reporting, group features by level for a tier summary:

- **Basic (L1)** — language-agnostic essentials; failing here is alarming
- **Intermediate (L2)** — agent-friendly tooling; expected of a healthy repo
- **Advanced (L3)** — measurement & discipline; differentiator
- **Power-user (L4)** — full automation & observability
- **Self-improving (L5)** — closed feedback loops

Compute "max level reached" as the highest level where ≥80% of applicable
features pass.  Quote both flat coverage (% of all applicable) AND tier reached.
