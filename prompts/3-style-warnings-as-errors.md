[Readiness Fix] <REPO_NAME> Warnings-as-Errors

Fix the failing signal: Warnings-as-Errors ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Warnings-as-Errors
**Score**: [0/1]
**Description**: Compiler/runtime warnings treated as failures
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Warnings-as-errors – check that compiler, linter, and runtime warnings cause the build/test to fail rather than scrolling past in logs. PASS requires a checked-in, enforced setting in the build pipeline AND in local dev — not a CI-only flag, because a CI-only enforcement allows warnings to accumulate on developer machines and breaks the agent's local feedback loop. Acceptable evidence per ecosystem:

1. **TypeScript / Node**: `tsconfig.json` with `"strict": true` AND at minimum `"noUnusedLocals": true`, `"noUnusedParameters": true`, `"noImplicitReturns": true`, `"noFallthroughCasesInSwitch": true`. Lint step uses `eslint . --max-warnings 0` (or `biome ci` / `biome check --error-on-warnings`) in the package script that CI calls. Node runtime invocations that matter (build scripts, test runners) use `--throw-deprecation` or `NODE_OPTIONS=--throw-deprecation` in CI. A `tsc --noEmit` step with strict mode but `--max-warnings 100` (or no `--max-warnings` flag at all) is a FAIL — ESLint defaults to warnings being non-fatal.
2. **Python**: `pyproject.toml` `[tool.pytest.ini_options]` (or `pytest.ini`) contains `filterwarnings = ["error"]` (or `-W error` baked into the default `addopts`). Ruff/flake8 configured with `--exit-non-zero-on-fix` or warnings promoted via rule config. `python -W error` used for any CLI entrypoints invoked in CI. A `filterwarnings` block that lists every warning as `ignore` is a FAIL.
3. **Rust**: `RUSTFLAGS="-D warnings"` set in CI (`.cargo/config.toml` `[build] rustflags = ["-D", "warnings"]` makes this local too), `#![deny(warnings)]` in crate root, OR `cargo clippy -- -D warnings -D clippy::all` wired into the lint script. Cargo's default warn-only behavior is a FAIL.
4. **Go**: `go vet ./...` invoked as a required step (non-zero exit on any finding) AND `golangci-lint run` with `issues.max-issues-per-linter: 0` and `issues.max-same-issues: 0` in `.golangci.yml`. A `go build` step alone does not satisfy — `go build` does not surface vet findings.
5. **C/C++**: `-Werror -Wall -Wextra` in `CMakeLists.txt` (`add_compile_options(-Werror -Wall -Wextra -Wpedantic)`) or in the top-level `Makefile`/`meson.build`. MSVC equivalents: `/W4 /WX`. A `-Wno-error=...` opt-out list is acceptable only if it is short, commented, and bounded — a blanket `-Wno-error` is a FAIL.

Also verify the enforcement actually runs: the strict flag must be present in the script CI invokes (e.g. `npm run lint`, `make ci`, `cargo test`), not in a one-off `scripts/strict-check.sh` that no workflow calls. A flag wired into `.github/workflows/strict.yml` but absent from `package.json` / `Makefile` means local agents get green output while CI fails — the worst possible feedback loop.

## Your Task

1. Explore the repository to understand the current state related to this signal — identify the language(s), inspect `tsconfig.json`, `pyproject.toml` / `pytest.ini` / `setup.cfg`, `.eslintrc*` / `biome.json`, `.golangci.yml`, `Cargo.toml` / `.cargo/config.toml`, `Makefile` / `CMakeLists.txt`, and every script referenced by CI workflows. Note which warnings the build currently emits.
2. Make **substantive improvements** by enforcing warnings-as-errors in the canonical local-dev entrypoint (the script CI actually runs):
   - For TypeScript repos, add `--max-warnings 0` to the lint script in `package.json`, enable `noUnusedLocals` / `noUnusedParameters` / `noImplicitReturns` / `noFallthroughCasesInSwitch` in `tsconfig.json`, and add `NODE_OPTIONS: --throw-deprecation` to the test job's env.
   - For Python repos, add `filterwarnings = ["error"]` under `[tool.pytest.ini_options]` in `pyproject.toml` (or `[pytest]` in `pytest.ini`). If the test suite has pre-existing legitimate deprecation noise from a pinned dependency, add narrowly-scoped `"ignore::DeprecationWarning:<pinned_package>"` entries below the `"error"` default — never a blanket ignore.
   - For Rust, add `[build] rustflags = ["-D", "warnings"]` to `.cargo/config.toml` AND wire `cargo clippy -- -D warnings` into the lint/CI script.
   - For Go, add `golangci-lint run` to the make target CI calls, and set `max-issues-per-linter: 0`, `max-same-issues: 0` in `.golangci.yml`.
   - For C/C++, add `-Werror -Wall -Wextra` to the project's compile options (CMake `add_compile_options` or Makefile `CFLAGS`).
3. Fix the warnings the new strict mode surfaces, in the same PR. Suppressing them with broad rule-level disables (`// eslint-disable-next-line`, `# noqa`, `#[allow(warnings)]`, `-Wno-error=...`) defeats the purpose. Narrow per-line suppressions with a comment explaining why are acceptable but should be rare.
4. Verify locally: run the script CI invokes (`npm run lint`, `pytest --collect-only` then `pytest -W error::DeprecationWarning -x`, `cargo clippy`, `go vet ./... && golangci-lint run`, `make`) and confirm it exits 0 with the strict flags enabled.
5. Keep changes focused on this signal — do not refactor unrelated config.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** CI-only enforcement. A `.github/workflows/strict.yml` with `--max-warnings 0` while `npm run lint` locally has no such flag creates dev/CI drift: every developer (and every agent) gets green output locally, then CI fails on push. The strict flag MUST live in the script the developer runs (`package.json` `scripts.lint`, `Makefile` target, `pyproject.toml` `addopts`), and CI invokes that script — single source of truth.
- **NO** broad suppressions to silence the surfaced warnings. `// eslint-disable-next-line` on every line, `#[allow(warnings)]` at the crate root, `# type: ignore` blanketed across a file, `-Wno-error` without a specific warning name, `filterwarnings = ["ignore"]` — all of these are "passed the gate, removed the gate." Fix the warning or scope the suppression to one line with a justification comment.
- **NO** removing warnings-as-errors "temporarily" to ship a deadline feature without a tracking issue and a reversion deadline. This is how every codebase loses its strict mode: it never gets restored.
- **NO** `--no-warnings`, `--silent`, `2>/dev/null` flags that swallow output instead of fixing it. If `pip install` is noisy, fix the source; do not hide it.
- **NO** new top-level `eslint-disable` / `# pylint: disable-all` / `#[allow(dead_code)]` to make the build pass. If the surfaced warnings are too many to fix in this PR, fix them per-module and open follow-up issues for the rest — do not blanket-disable.
- **NO** wiring the strict flag into a separate script (`scripts/strict-lint.sh`) that nothing calls. CI must invoke the same entrypoint as local dev.
- **NO** enabling `tsc --strict` without also enforcing the lint step — TypeScript warnings come from both `tsc` AND ESLint, and `tsc` alone does not catch unused imports, `no-explicit-any`, etc.

Examples of BAD fixes:
- Adding `eslint . --max-warnings 0` to `.github/workflows/ci.yml` but leaving `package.json` `"lint": "eslint ."` unchanged — local agents will run `npm run lint`, see zero exit, and push code that CI rejects.
- Setting `filterwarnings = ["error"]` then immediately adding `"ignore::DeprecationWarning"` as the second entry — Python honors the most-specific match, but a broad ignore right under the error rule defeats it for most call paths.
- Adding `-Werror` to `CMakeLists.txt` then sprinkling `#pragma GCC diagnostic ignored "-Wunused-variable"` across the codebase to silence the surfaced warnings.
- Adding `RUSTFLAGS="-D warnings"` to `.github/workflows/rust.yml` but not to `.cargo/config.toml` — `cargo build` locally stays warn-only.
- A `package.json` lint script of `"lint": "eslint . --max-warnings 0 || true"` — the `|| true` makes the exit code always zero and the flag does nothing.

Examples of GOOD fixes:
- TypeScript (`package.json` + `tsconfig.json`):
  ```json
  // package.json
  {
    "scripts": {
      "lint": "eslint . --max-warnings 0 && tsc --noEmit",
      "test": "NODE_OPTIONS='--throw-deprecation' vitest run",
      "ci": "pnpm run lint && pnpm run test"
    }
  }
  ```
  ```json
  // tsconfig.json
  {
    "compilerOptions": {
      "strict": true,
      "noUnusedLocals": true,
      "noUnusedParameters": true,
      "noImplicitReturns": true,
      "noFallthroughCasesInSwitch": true,
      "noUncheckedIndexedAccess": true
    }
  }
  ```
- Python (`pyproject.toml`):
  ```toml
  [tool.pytest.ini_options]
  filterwarnings = [
      "error",
      # legitimate: urllib3 1.x noise from pinned `requests<2.32` (see #1234)
      "ignore::DeprecationWarning:urllib3",
  ]
  addopts = "-W error::DeprecationWarning -ra"

  [tool.ruff]
  # ruff reports findings as errors by default; ensure no `--exit-zero` anywhere
  ```
- Go (`Makefile` + `.golangci.yml`):
  ```makefile
  # Makefile
  lint:
  	go vet ./...
  	golangci-lint run

  ci: lint test
  ```
  ```yaml
  # .golangci.yml
  issues:
    max-issues-per-linter: 0
    max-same-issues: 0
  ```
- Rust (`.cargo/config.toml`):
  ```toml
  [build]
  rustflags = ["-D", "warnings"]
  ```
  Plus a `make lint` or `just lint` target that runs `cargo clippy --all-targets --all-features -- -D warnings -D clippy::all`.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- TypeScript compiler strict-family flags: https://www.typescriptlang.org/tsconfig/#strict
- ESLint `--max-warnings`: https://eslint.org/docs/latest/use/command-line-interface#--max-warnings
- Biome `--error-on-warnings` / `biome ci`: https://biomejs.dev/reference/cli/
- Node.js `--throw-deprecation`: https://nodejs.org/api/cli.html#--throw-deprecation
- pytest `filterwarnings`: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
- Python `-W` warning control: https://docs.python.org/3/using/cmdline.html#cmdoption-W
- Rust `-D warnings` and `.cargo/config.toml`: https://doc.rust-lang.org/cargo/reference/config.html#buildrustflags
- Clippy lint level configuration: https://doc.rust-lang.org/clippy/configuration.html
- golangci-lint config (`issues.max-issues-per-linter`): https://golangci-lint.run/usage/configuration/
- GCC `-Werror`, `-Wall`, `-Wextra`: https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html
- MSVC `/WX` and `/W4`: https://learn.microsoft.com/cpp/build/reference/compiler-option-warning-level
</system-reminder>
