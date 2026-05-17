[Readiness Fix] <REPO_NAME> Package Manager Configuration

Fix the failing signal: Package Manager Configuration ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Package Manager Configuration
**Score**: [0/1]
**Description**: Custom registry, auth, and resolution settings are checked in so an agent (or a fresh clone) can install dependencies deterministically without hand-tweaking local config
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Package manager configuration — check for a checked-in, machine-readable config that tells the package manager (a) which registries to use, (b) how to authenticate to private registries without committing secrets, and (c) any resolution / engine constraints the install must obey. PASS requires at least one of the following, populated with real entries (not just an empty file or all defaults):

1. **Node (npm / pnpm / yarn)**: a checked-in `.npmrc` at the repo root with at minimum `registry=` (if non-default) or one or more scoped `@scope:registry=` lines for private packages, `engine-strict=true` (if `engines` is set in `package.json`), and `save-exact=true` or `save-prefix=` set deliberately. Auth tokens MUST be referenced via env var interpolation (`//registry.example.com/:_authToken=${NPM_TOKEN}`) — never committed raw. For pnpm, a `.npmrc` plus `packageManager` field in `package.json` (e.g. `"packageManager": "pnpm@9.12.0"`) is required so Corepack pins the tool version. For yarn berry, `.yarnrc.yml` with `npmRegistryServer`, `npmScopes`, and `nodeLinker` set.
2. **Python (pip / uv / poetry)**: `pyproject.toml` with `[tool.uv]` (`index-url`, `extra-index-url`, `index-strategy`) or `[[tool.poetry.source]]` blocks naming each source with `priority = "primary"|"supplemental"|"explicit"`. For pip, a checked-in `pip.conf` (under `.pip/pip.conf` or referenced via `PIP_CONFIG_FILE` in the repo's dev setup docs) with `index-url` and `extra-index-url`. Credentials MUST come from a keyring backend or env var, never plaintext in the file.
3. **Rust**: `.cargo/config.toml` at the repo root with `[registries]` defining each non-crates.io registry, `[source.<name>]` with `replace-with = "<mirror>"` if a mirror is used, and any `[net]` retry / git-fetch-with-cli settings the project depends on. Tokens live in `~/.cargo/credentials.toml` (per-user) or are injected via `CARGO_REGISTRIES_<NAME>_TOKEN` env var.
4. **Go**: a documented `GOPROXY` (e.g. `GOPROXY=https://proxy.example.com,https://proxy.golang.org,direct`) and `GOPRIVATE` (e.g. `GOPRIVATE=github.com/<org>/*`) set in a checked-in `Makefile`, `mise.toml`, `direnv` `.envrc`, or `go.env` so a fresh clone resolves private modules without manual setup. `GONOSUMDB` / `GOSUMDB=off` (the real Go env vars) configured only if the repo genuinely needs to bypass the public checksum database — note `GONOSUMCHECK` is NOT a Go env var.
5. **Ruby**: `Gemfile` with explicit `source` blocks (`source "https://rubygems.example.com" do ... end`) and a checked-in `.bundle/config` referencing private gem credentials via `BUNDLE_<HOST>__<PATH>` env vars (never raw passwords).

A `package.json` with no `.npmrc` and a non-default private registry is a FAIL — every contributor and every agent has to hand-edit their local config. An `.npmrc` that hardcodes `_authToken=npm_aBc123...` is a FAIL (and a credential leak — rotate it immediately). A repo that uses both pnpm and npm with no `packageManager` field is a FAIL: Corepack and the agent will pick different tools and produce conflicting lockfiles.

Also verify the config is actually read by the tool. Run `npm config ls -l` (or `pnpm config list`, `uv tool dir` plus inspecting `uv.toml` / `pyproject.toml` for `[tool.uv]`, `cargo config get` from cargo 1.84+ or inspect `.cargo/config.toml`) and confirm the project's settings appear with the expected source path. A `.npmrc` that lives in a subdirectory the install isn't run from is dead config. Note: `uv pip config list` is not a uv command — uv reads from `uv.toml` / `pyproject.toml [tool.uv]` / env vars (`UV_*`); `cargo --list` lists subcommands, not config.

A README sentence saying "set NPM_TOKEN before installing" without an `.npmrc` that consumes it is documentation, not configuration, and FAILs this signal.

## Your Task

1. Explore the repository to understand the current state related to this signal — list every `package.json`, `.npmrc`, `.yarnrc.yml`, `pyproject.toml`, `pip.conf`, `poetry.toml`, `.cargo/config.toml`, `Gemfile`, `.bundle/config`, `mise.toml`, `.envrc`, and `Dockerfile` (RUN install steps reveal what the install actually expects).
2. Identify the package manager(s) in use and any private registries the repo currently depends on (look for `@<scope>/` imports without a matching scoped registry, `pip install` from internal URLs in CI, `cargo` deps pointing at git URLs that should be a registry).
3. Make **substantive improvements** by writing a real, project-tuned config:
   - For Node, create or update `.npmrc` with the registry settings the repo actually needs, env-var-interpolated auth for any private scope, `engine-strict=true` when `package.json` declares `engines`, and `save-exact=true` (or a deliberate `save-prefix`). Pin the package manager via the `packageManager` field in `package.json`.
   - For Python, add `[tool.uv]` or `[[tool.poetry.source]]` blocks naming each index with explicit priority. Document the env var that supplies the token.
   - For Rust, add `.cargo/config.toml` with `[registries]` and (if applicable) `[source.crates-io] replace-with = "<mirror>"`.
   - For Go, codify `GOPROXY` and `GOPRIVATE` in a checked-in `Makefile` target, `mise.toml`, or `.envrc` so `direnv allow` (or `mise trust`) sets them automatically.
4. Verify the config loads: run the tool's config-dump command (`npm config ls -l`, `pnpm config list`, `cargo config get` from cargo 1.84+) and confirm each setting shows up with the repo's `.npmrc` (or equivalent) as the source. For uv, inspect `uv.toml` / `pyproject.toml [tool.uv]` directly and verify env vars via `env | grep UV_`.
5. Add a short note in the repo's setup docs (`README.md` or `CONTRIBUTING.md`) naming each env var the install requires (`NPM_TOKEN`, `UV_INDEX_INTERNAL_PASSWORD`, `CARGO_REGISTRIES_INTERNAL_TOKEN`, etc.) and where to obtain it. Do NOT commit the token values themselves.
6. Keep changes focused on this signal — do not bump dependencies, do not refactor build scripts beyond what's needed to load the config.
7. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** committed auth tokens. An `.npmrc` line like `//npm.pkg.github.com/:_authToken=ghp_aBc123...` is a credential leak — use `${NPM_TOKEN}` and rotate the exposed token. Same for `pip.conf` (`password=...`), `.cargo/credentials.toml`, and `.bundle/config` (`BUNDLE_<HOST>="user:pass"`).
- **NO** empty `.npmrc` (or `.yarnrc.yml`, `pip.conf`, etc.) committed just to satisfy the check. Every config file MUST contain at least one real setting the project actually needs.
- **NO** `engine-strict=false` when `package.json` declares `engines` — that defeats the point of pinning the runtime. If the repo can't honor the engine range, fix `engines` instead of disabling enforcement.
- **NO** registry override without the matching auth line. `@myorg:registry=https://npm.pkg.github.com` with no `//npm.pkg.github.com/:_authToken=${...}` will break `npm install` for every agent and every fresh clone.
- **NO** mismatched scoped vs default registry — if `registry=https://internal.example.com` is set globally and `@myorg:registry=https://npm.pkg.github.com` is set per-scope, confirm the install actually resolves `@myorg/*` from GitHub and everything else from internal. A typo here silently routes private packages to the wrong host.
- **NO** dual package manager configs (`pnpm-lock.yaml` + `package-lock.json` both committed, or `.yarnrc.yml` alongside `.npmrc` with different registries). Pick one, delete the other, set `packageManager` in `package.json` so Corepack enforces it.
- **NO** putting the config in a path the tool doesn't read. `.npmrc` MUST be at the repo root (or `~/.npmrc` for user-level, which doesn't count for this signal). A `config/npmrc` file is dead config — `npm` will not find it.
- **NO** legacy user-level `~/.npmrc` that overrides the repo config silently. If the readiness report flags the agent box, check `npm config get registry --location user` and document a `npm config delete registry --location user` step if needed.
- **NO** committing `.npmrc` with `unsafe-perm=true`, `ignore-scripts=false` for a repo that doesn't actually need install scripts, or any other security-loosening flag added to "just make it work".

Examples of BAD fixes:
- `.npmrc` containing only `registry=https://registry.npmjs.org/` — that's the default, the file adds zero value.
- An `.npmrc` with `//npm.pkg.github.com/:_authToken=ghp_realTokenCommittedToGit` — the token is now in git history forever; rotate it and use `${NPM_TOKEN}`.
- Adding `[[tool.poetry.source]]` with `url = "https://internal.example.com/simple"` but no `priority` set — Poetry's default changed between versions and the resolution order is now implementation-dependent.
- A `.cargo/config.toml` registering `[registries.internal]` with no `index = "sparse+https://..."` entry — `cargo` will fail to resolve any crate from it.
- Setting `GOPROXY` in a developer's shell rc file and calling that "configured" — the agent and CI don't inherit it; codify it in `Makefile`, `mise.toml`, or `.envrc`.

Examples of GOOD fixes:
- For a Node repo publishing private packages to GitHub Packages and consuming a mix of public + private:
  ```
  # .npmrc
  registry=https://registry.npmjs.org/
  @myorg:registry=https://npm.pkg.github.com
  //npm.pkg.github.com/:_authToken=${GITHUB_PACKAGES_TOKEN}
  engine-strict=true
  save-exact=true
  fund=false
  audit=false
  ```
  Paired with `"packageManager": "pnpm@9.12.0"` in `package.json` and a `CONTRIBUTING.md` line: `Set GITHUB_PACKAGES_TOKEN (scope: read:packages) before running pnpm install — see https://github.com/<org>/<repo>/settings/tokens.`
- For a uv-managed Python repo with a private PyPI mirror:
  ```toml
  # pyproject.toml
  [tool.uv]
  index-url = "https://pypi.org/simple"
  extra-index-url = ["https://pypi.internal.example.com/simple"]
  index-strategy = "unsafe-best-match"
  ```
  With `UV_INDEX_INTERNAL_USERNAME` / `UV_INDEX_INTERNAL_PASSWORD` documented in the README, sourced from the team password manager.
- For a Rust repo using a Cloudsmith private registry:
  ```toml
  # .cargo/config.toml
  [registries.internal]
  index = "sparse+https://cargo.cloudsmith.io/myorg/internal/"

  [net]
  git-fetch-with-cli = true
  ```
  With `CARGO_REGISTRIES_INTERNAL_TOKEN` set via the contributor's shell or CI secret.
- For a Go monorepo with private modules:
  ```makefile
  # Makefile
  export GOPROXY=https://proxy.golang.org,direct
  export GOPRIVATE=github.com/myorg/*
  export GONOSUMDB=github.com/myorg/*    # NOT GONOSUMCHECK -- that env var does not exist
  ```
  Plus a `mise.toml` env block so `mise trust` exports the same values for interactive shells.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- npm `.npmrc` reference (registry, scoped registries, auth, engine-strict, save-exact): https://docs.npmjs.com/cli/v10/configuring-npm/npmrc
- npm auth token interpolation via env vars: https://docs.npmjs.com/cli/v10/configuring-npm/npmrc#auth-related-configuration
- pnpm settings & `.npmrc` resolution: https://pnpm.io/npmrc
- pnpm `packageManager` field + Corepack pinning: https://nodejs.org/api/corepack.html
- Yarn berry `.yarnrc.yml` (`npmRegistryServer`, `npmScopes`, `nodeLinker`): https://yarnpkg.com/configuration/yarnrc
- uv index configuration (`[tool.uv]`, `index-url`, `extra-index-url`, `index-strategy`): https://docs.astral.sh/uv/configuration/indexes/
- Poetry repository sources & priority levels: https://python-poetry.org/docs/repositories/#package-sources
- pip `pip.conf` reference (`PIP_CONFIG_FILE`, `index-url`, `extra-index-url`): https://pip.pypa.io/en/stable/topics/configuration/
- Cargo `config.toml` reference (`[registries]`, `[source]`, `replace-with`, `[net]`): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo registry authentication: https://doc.rust-lang.org/cargo/reference/registry-authentication.html
- Go module proxy & `GOPRIVATE`: https://go.dev/ref/mod#module-proxy
- Bundler config & private gem auth (`BUNDLE_<HOST>__<PATH>`): https://bundler.io/v2.5/man/bundle-config.1.html
- Renovate / Dependabot interaction with private registries (hostRules / configuration-variables): https://docs.renovatebot.com/getting-started/private-packages/ and https://docs.github.com/en/code-security/dependabot/working-with-dependabot/configuration-options-for-the-dependabot.yml-file#registries
</system-reminder>
