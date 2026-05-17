[Readiness Fix] <REPO_NAME> Multi-platform CI

Fix the failing signal: Multi-platform CI ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Multi-platform CI
**Score**: [0/1]
**Description**: CI matrix covering multiple OS, arch, or runtime versions
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Multi-platform CI — check `.github/workflows/*.yml` (or `.gitlab-ci.yml`, `.circleci/config.yml`, `azure-pipelines.yml`) for a job that declares `strategy.matrix` with **at least two distinct values across an OS, architecture, or runtime-version axis**. PASS requires the matrix to actually expand into >1 job at runtime — a `matrix` block with a single OS and a single runtime version (e.g. `os: [ubuntu-latest], node: [20]`) is decorative and FAILs the signal. The matched axis must be meaningful for the project type:

- **Published libraries / CLIs / SDKs**: matrix MUST cover both the current LTS and at least one neighbouring runtime version (Node N + N-2, Python 3.x + 3.(x-1), Ruby 3.y + 3.(y-1)), and SHOULD cover Linux + at least one of macOS/Windows if the package has native deps, file-system code, path handling, or installs binaries.
- **Native / compiled artifacts (Rust, Go, C/C++, Electron, Tauri)**: matrix MUST cover the OS/arch tuples the project actually ships (`ubuntu-latest`, `macos-latest`, `windows-latest`, and at least one ARM runner such as `ubuntu-22.04-arm` or `macos-14` if the release artifact targets ARM).
- **Pure deployed-on-Linux web apps (Next.js on Vercel, Rails on Heroku, Django on a single container)**: a single-OS matrix that varies only the runtime LTS is acceptable; cross-OS is not required. A repo of this shape that already runs on one Linux + one Node version legitimately PASSes only if the matrix has >1 entry on the runtime axis.

A workflow with `runs-on: ubuntu-latest` and no `strategy.matrix` block FAILs. A `strategy.matrix` block whose entries collapse via `exclude` to a single combination FAILs. A separate `release` workflow that builds per-platform binaries via repeated jobs (no `matrix:`) does NOT satisfy the signal — the criterion is matrix expansion in the PR-blocking workflow, because that is what protects agent-authored changes.

## Your Task

1. Inventory every workflow file (`.github/workflows/*.yml`, plus any other CI config). For each, record: trigger (`on:`), `runs-on`, presence of `strategy.matrix`, and whether the job is required for PR merge (branch protection or PR-blocking).
2. Classify the repo: published library/CLI/SDK, native artifact, or Linux-only web app. The classification dictates the required matrix shape (see criteria above). If you cannot tell, grep for `engines` in `package.json`, `python_requires` in `setup.py`/`pyproject.toml`, `rust-version` in `Cargo.toml`, or the `Dockerfile` `FROM` line.
3. Make **substantive improvements** by adding a real `strategy.matrix` to the primary PR-blocking workflow:
   - Add `strategy.matrix` with concrete OS values (`ubuntu-latest`, `macos-latest`, `windows-latest`) and/or runtime versions that the project actually claims to support.
   - Reference matrix values in steps via `${{ matrix.os }}`, `${{ matrix.node-version }}`, etc., not hard-coded constants.
   - Set `fail-fast: false` so a transient failure on one combination does not cancel the rest — otherwise an only-Windows bug gets hidden by a faster Ubuntu green.
   - Use `matrix.include` to add a single extra combination (e.g. one beta runtime) without exploding the cross-product.
   - Use `matrix.exclude` to carve out known-incompatible combinations (e.g. node 18 on macos-14 ARM if upstream support is missing) — exclusions must be commented with the reason.
4. Verify the matrix actually expands: run `gh workflow view <workflow>` after pushing, or check the Actions tab — the run should show one job per matrix combination, not a single collapsed job. Confirm at least one matrix axis change (e.g. dropping Node 18) reduces the job count.
5. Keep changes focused on this signal — do not refactor unrelated workflows, secrets, or job steps.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** single-entry matrices — `os: [ubuntu-latest]` with `node: [20]` expands to 1 job and is strictly worse than no matrix because it signals false coverage. The matrix MUST produce >1 job.
- **NO** matrices that cover platforms the project does not support. Adding `windows-latest` to a repo whose `Dockerfile` targets `linux/amd64` and whose deploy is Vercel-on-Linux burns CI minutes for zero signal. Match the matrix to the artefact.
- **NO** leaving `fail-fast: true` (the default) on a multi-OS matrix — a flaky Windows runner will cancel the Ubuntu job mid-run, hide the only failing platform, and train the agent to retry-until-green. Always set `fail-fast: false` on cross-platform matrices.
- **NO** combinatorial explosion. A naive `os: [ubuntu, macos, windows] × node: [18, 20, 22] × python: [3.10, 3.11, 3.12]` is 27 jobs per push. Use `matrix.include` to add only the combinations that matter and `matrix.exclude` to drop the rest, or split into separate jobs with smaller matrices.
- **NO** matrix on a workflow that is not PR-blocking. A `nightly.yml` matrix is nice-to-have; the signal evaluates the workflow that gates merge.
- **NO** runtime version sprawl. Two versions (current LTS + one neighbour) is the floor; five versions on three OSes is waste. The agent needs the matrix to catch real divergence, not to enumerate every release.
- **NO** copy-pasted matrices from an unrelated repo. A Python lib with a Node matrix, or an `actions/setup-node@v4` step on a Rust matrix, signals zero project knowledge and will be deleted on first edit.

Examples of BAD fixes:
- `strategy: { matrix: { os: [ubuntu-latest] } }` — expands to 1 job, no coverage gain, looks like a matrix.
- A Node library workflow that runs `os: [ubuntu, macos, windows]` but never calls `actions/setup-node`, so all three runs use whatever Node the runner image ships with (no version axis at all).
- Adding `windows-latest` to a repo that uses `bash` scripts with `set -euo pipefail` and `find . -name '*.ts'` in every step — the Windows job will fail on path separators or shell builtins, and the team will add `if: matrix.os != 'windows-latest'` to every step until the matrix is theatre.
- `strategy: { fail-fast: true, matrix: { os: [...] } }` — the first cross-platform regression cancels every other job and you lose the data you added the matrix to collect.
- A 36-job matrix (`3 OS × 4 Node × 3 Python`) on every push for a repo whose users run one OS and one runtime — drains the org's Actions minutes and slows PR feedback past the 10-minute bar.

Examples of GOOD fixes:
- For a published Node library (e.g. `@<scope>/<pkg>`):
  ```yaml
  # .github/workflows/ci.yml
  jobs:
    test:
      runs-on: ${{ matrix.os }}
      strategy:
        fail-fast: false
        matrix:
          os: [ubuntu-latest, macos-latest, windows-latest]
          node-version: [20, 22]          # current LTS + prior LTS
          include:
            - os: ubuntu-latest
              node-version: 23            # current release, soak only on Linux
          exclude:
            - os: windows-latest
              node-version: 20            # known shelljs path bug, tracked in #<ISSUE>
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with:
            node-version: ${{ matrix.node-version }}
            cache: npm
        - run: npm ci
        - run: npm test
  ```
  That matrix expands to 6 jobs (3 OS × 2 LTS = 6, plus 1 include, minus 1 exclude = 6), covers the supported OS surface, catches Node-version divergence, and the `exclude` is documented.
- For a Rust CLI that ships Linux + macOS + Windows binaries with an ARM Linux build:
  ```yaml
  jobs:
    test:
      runs-on: ${{ matrix.os }}
      strategy:
        fail-fast: false
        matrix:
          include:
            - { os: ubuntu-latest,    target: x86_64-unknown-linux-gnu }
            - { os: ubuntu-22.04-arm, target: aarch64-unknown-linux-gnu }
            - { os: macos-latest,     target: aarch64-apple-darwin }
            - { os: windows-latest,   target: x86_64-pc-windows-msvc }
      steps:
        - uses: actions/checkout@v4
        - uses: dtolnay/rust-toolchain@stable
          with: { targets: ${{ matrix.target }} }
        - run: cargo test --target ${{ matrix.target }}
  ```
- For a Python library supporting 3.10+:
  ```yaml
  strategy:
    fail-fast: false
    matrix:
      os: [ubuntu-latest, macos-latest, windows-latest]
      python-version: ["3.11", "3.12"]
  ```
- For a Linux-only Next.js web app: keep `runs-on: ubuntu-latest` and add a single-axis runtime matrix to catch Node-version drift before the Vercel deploy step:
  ```yaml
  strategy:
    fail-fast: false
    matrix:
      node-version: [20, 22]
  ```
  This expands to 2 jobs, costs ~2x minutes, and gates the deploy on the version Vercel will actually run.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- GitHub Actions matrix syntax (`strategy.matrix`, `include`, `exclude`, `fail-fast`): https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs
- GitHub-hosted runner images (Ubuntu, macOS, Windows, ARM): https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners
- Linux ARM64 hosted runners (`ubuntu-22.04-arm`, `ubuntu-24.04-arm`): https://github.blog/changelog/2025-01-16-linux-arm64-hosted-runners-now-available-for-free-in-public-repositories-public-preview/
- `actions/setup-node` version matrix patterns: https://github.com/actions/setup-node#usage
- `actions/setup-python` version matrix patterns: https://github.com/actions/setup-python#usage
- GitLab CI `parallel:matrix`: https://docs.gitlab.com/ee/ci/yaml/#parallelmatrix
- CircleCI matrix jobs: https://circleci.com/docs/using-matrix-jobs/
</system-reminder>
