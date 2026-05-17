[Readiness Fix] <REPO_NAME> Build Caching

Fix the failing signal: Build Caching ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Build Caching
**Score**: [0/1]
**Description**: Caching for faster rebuilds
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Build caching — check for a checked-in, working cache configuration that survives across CI runs and/or local developer machines. PASS requires at least one of the following, with a real cache key that changes when inputs change AND a `restore-keys` (or equivalent) fallback for partial hits:

1. **CI dependency cache**: `actions/cache@v4` (or `actions/setup-node@v4` / `actions/setup-python@v5` with `cache:` enabled), GitLab CI `cache:` with `key: files:`, CircleCI `restore_cache` + `save_cache`. The `key` MUST hash a lockfile (`hashFiles('**/pnpm-lock.yaml')`, `hashFiles('**/poetry.lock')`, `hashFiles('**/Cargo.lock')`) — a static key like `key: deps` is FAIL because it never invalidates. `restore-keys` MUST be present so partial-hit fallbacks work.
2. **Monorepo task cache**: Turborepo (`turbo.json` with `tasks.build.outputs` + remote cache via `turbo login` / `TURBO_TOKEN` / self-hosted via `--api`), Nx (`nx.json` with `cacheableOperations` and Nx Cloud token or `nx-remotecache-*`), or Bazel remote cache (`build --remote_cache=` in `.bazelrc`). Local-only `node_modules/.cache/turbo` is half-credit; remote cache is the real win because CI and the next agent run both benefit.
3. **Compiler cache**: `ccache` / `sccache` configured for C/C++/Rust builds (`SCCACHE_GHA_ENABLED=true` + `mozilla-actions/sccache-action@v0.0.6` in CI, or `CC="ccache gcc"` in the Makefile). Must show evidence the cache directory is persisted between runs.
4. **Container build cache**: Docker BuildKit with `--cache-from type=gha` / `type=registry,ref=...` AND `--cache-to type=gha,mode=max` / `type=registry,ref=...,mode=max` via `docker/build-push-action@v6`. Inline cache (`BUILDKIT_INLINE_CACHE=1`) without `--cache-from` is FAIL — the cache is published but never consumed.

A README sentence saying "we use caching" without a workflow file or `turbo.json` is documentation, not configuration, and FAILs this signal. A cache step that runs **after** the build step that would consume it (common copy-paste error) also FAILs because the cache is populated but the build never restores from it.

## Your Task

1. Explore the repository to understand the current state — list every `.github/workflows/*.yml`, `.gitlab-ci.yml`, `turbo.json`, `nx.json`, `.bazelrc`, `Dockerfile`, and any `docker-compose*.yml`. Identify the package manager (`pnpm-lock.yaml` / `package-lock.json` / `yarn.lock` / `poetry.lock` / `Cargo.lock` / `go.sum`), the build orchestrator (single-package / Turborepo / Nx / Bazel / make), and whether the project ships container images.
2. Make **substantive improvements** by wiring a real cache into the chain that actually rebuilds today:
   - For Node CI, add `actions/setup-node@v4` with `cache: 'pnpm'` (or `npm` / `yarn`) AND a `cache-dependency-path: '**/pnpm-lock.yaml'`. If the project is a Turborepo, also add `actions/cache@v4` for `.turbo` keyed on `${{ runner.os }}-turbo-${{ github.sha }}` with `restore-keys: ${{ runner.os }}-turbo-`.
   - For Turborepo/Nx monorepos, enable **remote cache** — Vercel-hosted (`turbo login && turbo link`, then export `TURBO_TOKEN` + `TURBO_TEAM` in CI) or self-hosted (`ducktors/turborepo-remote-cache`, `dko-slapper/nx-remotecache-custom`). Document the token rotation procedure.
   - For Docker builds, switch the workflow to `docker/build-push-action@v6` with `cache-from: type=gha` and `cache-to: type=gha,mode=max` (or `type=registry,ref=ghcr.io/<org>/<image>:buildcache,mode=max` for cross-repo sharing).
   - For C/C++/Rust, add `mozilla-actions/sccache-action@v0.0.6` and export `SCCACHE_GHA_ENABLED=true RUSTC_WRAPPER=sccache` (or `CC="sccache cc"`). For Gradle/Maven, enable the Gradle build cache (`org.gradle.caching=true` in `gradle.properties`) and add `gradle/actions/setup-gradle@v4`.
3. Verify the cache actually works: push a no-op commit and confirm the second CI run logs a cache hit (`Cache restored successfully` for `actions/cache`, `>>> FULL TURBO` for Turborepo, `Compile requests executed: N, Cache hits: N` for sccache, `importing cache manifest from ...` for BuildKit). A cache that never reports a hit is dead config.
4. Keep changes focused on this signal — do not refactor build scripts unrelated to caching.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** static cache keys — `key: deps`, `key: node-modules`, `key: ${{ runner.os }}-build` without a hash of a lockfile. A key that never changes means the cache is eternally stale; the first run wins forever and dependency updates are silently ignored.
- **NO** caching the entire `node_modules` directory across OSes — `node_modules` contains OS-specific native binaries (`@esbuild/linux-x64`, `sharp`, `node-sass`). Either key on `${{ runner.os }}-...` AND cache the package-manager store (`~/.pnpm-store`, `~/.npm`, `~/.cache/yarn`) instead of `node_modules`, or accept the cache is OS-locked.
- **NO** missing `restore-keys` — without a fallback, every lockfile bump is a full cold cache. The fallback chain should be `${{ runner.os }}-pnpm-${{ hashFiles('**/pnpm-lock.yaml') }}` → `${{ runner.os }}-pnpm-`.
- **NO** hashing the wrong files — `hashFiles('**/package.json')` changes on every version bump even when the lockfile (and thus the actual resolved tree) is unchanged. Hash the lockfile, not the manifest.
- **NO** caching secrets — never include `.env`, `~/.npmrc` with auth tokens, `~/.docker/config.json`, or `~/.aws/credentials` in a cache path. GitHub Actions cache is readable by any workflow on any branch with `actions: read`, including fork PRs in some configs.
- **NO** cache step placed AFTER the consuming step. `actions/cache` restores at the step where it runs; if it's after `pnpm install`, the install was a cold install every time and the cache is write-only.
- **NO** `--cache-to` without `--cache-from` in BuildKit — the cache is published to the registry but the next build never reads it. Both flags are required.
- **NO** committing a `turbo.json` with `"tasks": { "build": { "cache": false } }` for the hot path — that explicitly disables caching for the task that needs it most.
- **NO** Nx Cloud / Turborepo remote cache tokens hardcoded in `turbo.json` or committed `.env` files. Use repo secrets (`${{ secrets.TURBO_TOKEN }}`).

Examples of BAD fixes:
- Adding `- uses: actions/cache@v4` with `key: cache` and no `restore-keys` — the literal string `cache` is the key forever; the second run hits, but `pnpm-lock.yaml` could change every day and the cache would never invalidate.
- A workflow that caches `node_modules` keyed on `hashFiles('package.json')` running on `ubuntu-latest` and a Mac developer who pulls the same lockfile gets `Error: Cannot find module '@esbuild/darwin-arm64'` because the cache is Linux binaries.
- `docker buildx build --cache-from type=gha .` with no `--cache-to` — first build is cold, second build is cold, every build is cold; the cache scope is never written.
- `turbo.json` with `"remoteCache": { "enabled": true }` but no `TURBO_TOKEN` / `TURBO_TEAM` exported in CI — turbo silently falls back to local cache, CI gets zero benefit.
- A cache step at the end of the job ("save cache after build") with no matching restore step at the start — the cache is populated but never consumed; this is the most common copy-paste failure.

Examples of GOOD fixes:
- For a pnpm + Turborepo + Docker repo on GitHub Actions:
  ```yaml
  - uses: actions/checkout@v4
  - uses: pnpm/action-setup@v4
    with: { version: 9 }
  - uses: actions/setup-node@v4
    with:
      node-version: 20
      cache: 'pnpm'
      cache-dependency-path: '**/pnpm-lock.yaml'
  - run: pnpm install --frozen-lockfile
  - uses: actions/cache@v4
    with:
      path: .turbo
      key: ${{ runner.os }}-turbo-${{ github.sha }}
      restore-keys: |
        ${{ runner.os }}-turbo-
  - run: pnpm turbo run build --cache-dir=.turbo
    env:
      TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
      TURBO_TEAM: ${{ vars.TURBO_TEAM }}
  - uses: docker/setup-buildx-action@v3
  - uses: docker/build-push-action@v6
    with:
      context: .
      push: true
      tags: ghcr.io/<ORG>/<IMAGE>:${{ github.sha }}
      cache-from: type=gha
      cache-to: type=gha,mode=max
  ```
- For a Rust workspace, add `mozilla-actions/sccache-action@v0.0.6`, then:
  ```yaml
  env:
    SCCACHE_GHA_ENABLED: "true"
    RUSTC_WRAPPER: "sccache"
  ```
  plus `actions/cache@v4` for `~/.cargo/registry` keyed on `hashFiles('**/Cargo.lock')` with `restore-keys: ${{ runner.os }}-cargo-`.
- For a Python + Poetry repo: `actions/setup-python@v5` with `cache: 'poetry'` and `cache-dependency-path: '**/poetry.lock'`. Confirm the install step shows `Successfully restored cache` on the second run.
- A `turbo.json` `tasks.build` entry that declares `outputs: ["dist/**", ".next/**", "!.next/cache/**"]` so the cache stores build artifacts (and excludes the inner Next.js cache that would balloon storage).

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- `actions/cache@v4` (key syntax, restore-keys, scope rules): https://github.com/actions/cache
- `actions/setup-node` built-in package-manager cache: https://github.com/actions/setup-node#caching-global-packages-data
- `actions/setup-python` built-in cache: https://github.com/actions/setup-python#caching-packages-dependencies
- Turborepo remote caching (Vercel-hosted + self-hosted protocol): https://turborepo.com/docs/core-concepts/remote-caching
- Turborepo self-hosted reference server (`ducktors/turborepo-remote-cache`): https://github.com/ducktors/turborepo-remote-cache
- Nx remote caching (Nx Cloud + self-hosted): https://nx.dev/ci/features/remote-cache
- Bazel remote caching: https://bazel.build/remote/caching
- sccache GitHub Actions integration: https://github.com/mozilla-actions/sccache-action
- ccache manual: https://ccache.dev/manual/latest.html
- Docker BuildKit GitHub Actions cache backend: https://docs.docker.com/build/cache/backends/gha/
- Docker BuildKit registry cache backend: https://docs.docker.com/build/cache/backends/registry/
- `docker/build-push-action@v6` cache examples: https://github.com/docker/build-push-action#examples
- Gradle build cache: https://docs.gradle.org/current/userguide/build_cache.html
</system-reminder>
