[Readiness Fix] <REPO_NAME> Runnable Examples

Fix the failing signal: Runnable Examples ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Runnable Examples
**Score**: [0/1]
**Description**: Working example code the agent can study and imitate
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Runnable examples – check for an `examples/` directory (most common across JS, Python, Rust), `_examples/` (Go convention — underscore prefix prevents the Go toolchain from compiling them as part of the parent module), `cookbook/` (data/ML libraries — LangChain, Hugging Face), or `samples/` (Microsoft/Java ecosystems) at repo root. PASS requires ALL of:

1. **At least 2 example subdirectories**, each demonstrating a distinct, real-world usage scenario (not "hello world" + "hello world with comments"). A single example is a quickstart, not an example library.
2. **Per-example README** that states what the example does, prerequisites (Node/Python/etc. version), the exact install command, and the exact run command. The agent must be able to copy/paste two commands and see output.
3. **Self-contained dependencies** — each example either has its own `package.json`/`requirements.txt`/`Cargo.toml`/`go.mod`, OR the root README documents a single workspace install that covers every example. Examples that silently rely on the parent project being built first FAIL unless that prerequisite is spelled out.
4. **Actually runnable today** — run the install + run command for at least one example end-to-end. If `npm install` 404s, the lockfile is missing, an env var has no documented source, or the example imports a removed API from the parent library, the signal FAILs even if the directory exists.
5. **CI coverage** — a workflow (e.g. `.github/workflows/examples.yml`) that at minimum runs `install` + `build` (or `--dry-run`/`--check`) against each example on PRs that touch `examples/**` or the library source. Without CI, examples drift the first time the main API changes and become misinformation for the agent.

A `README.md` snippet that shows a 10-line code fragment is NOT an example — it cannot be executed in isolation, has no dependency manifest, and cannot be covered by CI. Inline snippets satisfy the README signal, not this one.

A `tests/` directory does NOT satisfy this signal. Tests assert behavior; examples demonstrate idiomatic use. The two have different audiences (maintainers vs. consumers) and an agent imitating test fixtures will produce code shaped like mocks, not like real applications.

## Your Task

1. Explore the repository to understand the current state — list every `examples/`, `_examples/`, `cookbook/`, `samples/`, `demo/`, `demos/` directory; check the root `README.md` for an "Examples" section; check `.github/workflows/` for any job that touches example paths. Identify the repo's package manager and primary language so the example layout matches the ecosystem (Go → `_examples/`, JS/Python/Rust → `examples/`).
2. Make **substantive improvements** by creating a real, runnable example library:
   - Add an `examples/` (or `_examples/` for Go) directory at the repo root with at least **two** subdirectories, each demonstrating a distinct real-world scenario the library actually supports (e.g. `examples/basic/`, `examples/with-auth/`, `examples/streaming/`, `examples/server-integration/`). Pick scenarios from the top issues / FAQ / docs — the agent will imitate these, so they must mirror real usage, not toy code.
   - Give every example its own `README.md` with: one-paragraph description, prerequisites (runtime version, env vars), install command, run command, expected output. Pin the runtime version (`.nvmrc`, `.python-version`, `rust-toolchain.toml`) where the ecosystem supports it.
   - Give every example its own dependency manifest (`package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`) so it can be installed and run in isolation from a fresh clone. For monorepos, use workspaces (`pnpm-workspace.yaml`, `cargo workspace`) and document the workspace install in the root README's "Examples" section.
   - Document any required env vars in an `examples/<name>/.env.example` (committed) with placeholder values; the example must load from `.env` and fail with a clear error if a required var is missing.
   - Add `.github/workflows/examples.yml` that, on PRs touching `examples/**` or library source, installs each example and runs at least `build` / `--dry-run` / `--check` (a full smoke run is better if it completes in < 5 min and needs no live credentials). Mock external services or use a smoke flag that exercises the code path without hitting the network.
   - Update the root `README.md` to link to the `examples/` index with a one-line description per example.
3. Verify by running the install + run command for one example end-to-end from a fresh shell. Confirm the CI workflow actually triggers on a touched example path (use `act` or push a draft PR).
4. Keep changes focused on this signal — do not refactor the library API to make examples easier to write.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** single example masquerading as a library — one `examples/basic/` directory is a quickstart, not an example collection. Ship at least two distinct scenarios.
- **NO** examples without their own `README.md`. An agent landing in `examples/foo/` with only an `index.ts` and no instructions cannot reproduce the run.
- **NO** examples that depend on the parent project being pre-built without saying so. `import { Foo } from "../../src"` in an example silently breaks the moment the agent tries to run it from a fresh clone.
- **NO** hardcoded credentials, API keys, or personal endpoints. Use `.env.example` + `process.env.X` with a clear "missing var" error. Committing a real key is worse than no example.
- **NO** examples copied verbatim from the test suite. Tests use mocks, fixtures, and assertion frameworks; examples should look like the code a consumer would actually write.
- **NO** examples that import a removed or renamed API from the main library. If the library refactored last month and the example still calls `client.oldMethod()`, the agent will write code that doesn't compile.
- **NO** examples committed once and never touched again. Without `.github/workflows/examples.yml` enforcing install + build on PRs, examples bit-rot within one release cycle.
- **NO** examples documented only in a top-level `README.md` code block. Inline snippets cannot be executed, cannot be lint-checked, and cannot be covered by CI.
- **NO** `examples/.gitkeep` or an empty directory with a `TODO` README. That FAILs the signal harder than no directory at all because it signals abandonment.

Examples of BAD fixes:
- Creating `examples/hello/index.js` containing `console.log("hello")` and calling it done. No real-world scenario, no README, no manifest.
- An `examples/basic/README.md` that says "see the main README for setup" — defeats the per-example self-containment requirement.
- An `examples/server/package.json` whose `"dependencies"` section pins the parent library to `"file:../.."` without documenting that the parent must be built first — fresh clone, fresh `npm install`, instant failure.
- A `.github/workflows/examples.yml` whose only step is `echo "examples ok"` — green checkmark, zero coverage.
- Copying `tests/integration/auth.test.ts` into `examples/with-auth/index.ts` with the assertions deleted. Still reads like a test, still uses `vi.fn()` imports.
- Adding `examples/streaming/` that requires `OPENAI_API_KEY` and `STRIPE_SECRET_KEY` but provides no `.env.example` and silently 401s on run.

Examples of GOOD fixes:
- For a Node/TypeScript library, an `examples/` tree like:
  ```
  examples/
    README.md                    # index + one-line description per example
    basic/
      README.md                  # what / prereqs / install / run / expected output
      package.json               # own deps, parent linked via workspace or "file:../.."
      .env.example
      src/index.ts
    with-auth/
      README.md
      package.json
      .env.example
      src/index.ts
    streaming/
      README.md
      package.json
      src/index.ts
  ```
  with `examples/basic/README.md` shaped like:
  ```markdown
  # Basic Example

  Minimal end-to-end usage of <LIB_NAME>: instantiate the client, fetch a record, print it.

  ## Prerequisites
  - Node 20+
  - Copy `.env.example` to `.env` and fill in `API_BASE_URL`

  ## Install
  ```bash
  cd examples/basic
  npm install
  ```

  ## Run
  ```bash
  npm start
  ```

  ## Expected output
  ```
  Fetched record: { id: "demo-1", name: "Example Record" }
  ```
  ```
- A `.github/workflows/examples.yml` that runs on PRs touching `examples/**` or `src/**`:
  ```yaml
  name: examples
  on:
    pull_request:
      paths: [ "examples/**", "src/**", "package.json" ]
  jobs:
    build-examples:
      runs-on: ubuntu-latest
      strategy:
        matrix:
          example: [ basic, with-auth, streaming ]
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with: { node-version: "20", cache: "npm" }
        - name: Build parent
          run: npm ci && npm run build
        - name: Install example
          working-directory: examples/${{ matrix.example }}
          run: npm install
        - name: Build example
          working-directory: examples/${{ matrix.example }}
          run: npm run build --if-present
        - name: Smoke run
          working-directory: examples/${{ matrix.example }}
          run: npm run smoke --if-present
          env:
            API_BASE_URL: http://localhost:0
  ```
- For Go, the same shape but at `_examples/basic/main.go` + `_examples/basic/go.mod` so `go build ./...` from the parent ignores them.
- For Python/uv, each example has its own `pyproject.toml` declaring the parent as a path dep: `[tool.uv.sources] mylib = { path = "../.." }`.
- For a data/ML library, a `cookbook/` of `.ipynb` notebooks paired with `nbmake` in CI (`pytest --nbmake cookbook/`) so notebook examples actually execute on every PR.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- npm workspaces (per-example `package.json` in a monorepo): https://docs.npmjs.com/cli/v10/using-npm/workspaces
- pnpm workspaces: https://pnpm.io/workspaces
- Go `_examples` convention (underscore-prefixed dirs ignored by build): https://pkg.go.dev/cmd/go#hdr-Package_lists_and_patterns
- Rust Cargo examples (`examples/` auto-discovered): https://doc.rust-lang.org/cargo/reference/cargo-targets.html#examples
- uv path dependencies for Python example projects: https://docs.astral.sh/uv/concepts/projects/dependencies/#path
- nbmake — execute Jupyter notebooks as pytest cases (CI for `cookbook/`): https://github.com/treebeardtech/nbmake
- GitHub Actions `paths` filter for example-only CI: https://docs.github.com/actions/using-workflows/triggering-a-workflow#using-filters
- Stripe `stripe-samples` org as a per-example-repo reference layout: https://github.com/stripe-samples
- LangChain cookbook (notebook-style examples with CI): https://github.com/langchain-ai/langchain/tree/master/cookbook
- Vercel `examples/` directory (canonical per-example README + manifest layout): https://github.com/vercel/next.js/tree/canary/examples
</system-reminder>
