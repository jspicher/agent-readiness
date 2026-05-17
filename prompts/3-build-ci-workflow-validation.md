[Readiness Fix] <REPO_NAME> CI Workflow Validation

Fix the failing signal: CI Workflow Validation ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: CI Workflow Validation
**Score**: [0/1]
**Description**: The CI configuration itself is linted and validated — typo'd action refs, undefined env vars, shellcheck violations in `run:` blocks, and invalid pipeline schemas fail fast on the branch that introduced them, not on the next push to `main`
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

CI workflow validation — the pipeline definitions in `.github/workflows/`, `.circleci/config.yml`, `.gitlab-ci.yml`, `.drone.yml`, `.buildkite/pipeline.yml`, `azure-pipelines.yml`, etc. must themselves be validated by a tool that understands the platform's schema and semantics. This is distinct from generic YAML / JSON-Schema validation (signal #33) — that catches malformed YAML and unknown top-level keys; THIS signal catches platform-specific bugs (typo'd `uses: actiosn/checkout@v4`, `${{ env.UNDEFINED }}`, deprecated `set-output`, `if:` expressions that always evaluate true, shellcheck issues inside `run:` blocks, jobs that reference nonexistent `needs:` targets, matrix expansions that produce zero combinations). PASS requires a platform-appropriate validator wired into CI or pre-commit-run-in-CI:

1. **GitHub Actions**: `actionlint` (https://github.com/rhysd/actionlint) by rhysd. Either the official Action (`uses: reviewdog/action-actionlint@v1` or a direct `actionlint` install step) or the pre-commit hook (`repo: https://github.com/rhysd/actionlint`). actionlint embeds `shellcheck` for `run:` blocks and `pyflakes` for inline Python — both must be on PATH or the lint silently skips those checks. Pin a real version (`@v1.7.7`), not `@main`.
2. **CircleCI**: `circleci config validate` (`.circleci/config.yml`) via the CircleCI CLI (https://circleci.com/docs/local-cli/). Runs against the platform schema and catches orb version errors, undefined parameters, and bad workflow `requires:` graphs. For packed configs (multi-file via `circleci config pack`), validate the packed output, not the source.
3. **GitLab CI**: server-side lint via `glab ci lint .gitlab-ci.yml` (recommended — uses your project context and `include:` resolution) or `POST /api/v4/projects/:id/ci/lint`. The unauthenticated `gitlab-ci-validate` npm package only validates schema, not `include:` chains or `extends:` inheritance, so it misses the most common breakage. Run `glab ci lint` in CI itself with a project token.
4. **Drone**: `drone lint .drone.yml` (and `drone exec --dry-run` for trust/secret resolution). The `drone` CLI is the only validator that understands signing requirements and trusted-step semantics.
5. **Buildkite**: `buildkite-agent pipeline upload --dry-run` for dynamic pipelines; for static `.buildkite/pipeline.yml`, the community `buildkite/plugin-linter` plus `buildkite/lint` plugin (https://github.com/buildkite-plugins/buildkite-plugin-linter). Plugin pins should be SHA-pinned and lint-checked.
6. **Azure Pipelines**: `az pipelines runs list --validate-only` against the pipeline definition, or the `Microsoft.AzurePipelines` VS Code extension's schema (https://github.com/microsoft/azure-pipelines-vscode/blob/main/service-schema.json) consumed by `check-jsonschema --schemafile <url>`.
7. **Jenkins**: `Declarative Linter` via `curl -X POST -F "jenkinsfile=<Jenkinsfile" $JENKINS_URL/pipeline-model-converter/validate` (requires a running Jenkins instance) or the `jenkins-jflint` container for offline lint.

Also verify the validator is **invoked AND blocking**:
- grep the validator name in `.github/workflows/`, `.pre-commit-config.yaml`, `Makefile`, `package.json`, `noxfile.py`, `tox.ini`, `.circleci/config.yml`, `.gitlab-ci.yml` etc.
- confirm the job is NOT `continue-on-error: true` and NOT gated behind a `paths:` filter that only triggers on workflow-file changes (composite actions, reusable workflows, and referenced scripts can break the parent workflow without the workflow file itself changing — the lint must run on every PR).
- if the only invocation is a pre-commit hook with no CI mirror, that's a FAIL — `--no-verify`, web-UI commits, and `gh api` commits bypass it.

A README sentence saying "please run actionlint before pushing" is documentation, not validation, and FAILs this signal.

## Your Task

1. Identify which CI platform(s) the repo uses — list every `.github/workflows/*.yml`, `.circleci/config.yml`, `.gitlab-ci.yml`, `.drone.yml`, `.buildkite/pipeline.yml`, `azure-pipelines.yml`, `Jenkinsfile`, etc. If multiple, validate each — a repo with `.github/workflows/` AND `.gitlab-ci.yml` needs both validators.
2. Pick the platform-appropriate validator from the list above. Do NOT just add generic YAML lint and call it CI validation — `yamllint` will not catch `uses: actiosn/checkout@v4` or an undefined `${{ env.FOO }}`.
3. Make **substantive improvements**:
   - **GitHub Actions**: add a workflow step `uses: reviewdog/action-actionlint@v1` (pinned), or install `actionlint` directly via the official installer (`bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash) 1.7.7`) and run `./actionlint -color`. Also install `shellcheck` and `pyflakes` in the runner (`sudo apt-get install -y shellcheck` — runner already has it on `ubuntu-latest`; `pip install pyflakes`) so actionlint's embedded checks actually fire. Mirror the same checks in `.pre-commit-config.yaml` via the actionlint pre-commit repo. The CI job MUST NOT be filtered by `paths: ['.github/workflows/**']` — composite actions in `.github/actions/` and referenced reusable workflows can break a parent workflow without the parent file changing.
   - **CircleCI**: install the CLI in CI (`curl -fLSs https://raw.githubusercontent.com/CircleCI-Public/circleci-cli/main/install.sh | bash`) and run `circleci config validate .circleci/config.yml` (or `circleci config pack .circleci/src | circleci config validate -` for packed configs). For org-scoped orbs, set `CIRCLECI_CLI_TOKEN` so private-orb resolution works.
   - **GitLab**: add a `lint` job that runs `glab ci lint --gitlab-host $CI_SERVER_URL` with a project access token, or POST to `/api/v4/projects/:id/ci/lint` and assert `valid: true` in the response. Schema-only npm validators are insufficient — they don't resolve `include:` or `extends:`.
   - **Drone**: add a `drone lint .drone.yml` step in a separate CI workflow (or as the first step of the drone pipeline itself if you have a dogfooding setup).
   - **Buildkite**: add `buildkite-agent pipeline upload --dry-run` for any dynamic pipeline; lint plugin pins with the community plugin-linter.
   - **Azure Pipelines**: add `check-jsonschema --schemafile https://raw.githubusercontent.com/microsoft/azure-pipelines-vscode/main/service-schema.json azure-pipelines.yml` (or use `az pipelines` if you have an Azure DevOps service connection in CI).
4. Verify the fix: run the validator locally first and fix every issue it surfaces — do not commit a workflow that already fails the new lint and `continue-on-error: true` your way around it. Push to a branch, introduce a deliberate typo (`uses: actiosn/checkout@v4`), and confirm CI blocks merge.
5. Pin the validator version. `actionlint@main`, `circleci/cli:latest`, and `glab:latest` all break CI on upstream changes. Use a SHA or semver tag (`actionlint@v1.7.7`, `circleci/circleci-cli:0.1.30431`).
6. If a pre-commit hook is added, also run pre-commit in CI (`uses: pre-commit/action@v3.0.1`) so `--no-verify`, web-UI commits, and `gh api` commits don't bypass it.
7. Keep changes focused on this signal — do not refactor unrelated workflow logic.
8. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** generic YAML lint (`yamllint`, `prettier --check`) as the only validator. That covers signal #33 (config schema), not THIS signal. A workflow can pass `yamllint --strict` and still reference `uses: actiosn/checkout@v4`. Platform-aware lint is the bar.
- **NO** `continue-on-error: true` or `|| true` on the lint job. A non-blocking lint is theatre — agents and humans will both ignore the warning.
- **NO** pinning the validator to `@main`, `@latest`, or a moving tag. `actionlint@main` pulls untrusted code on every CI run and breaks CI when rhysd ships a new rule that flags your existing workflows.
- **NO** `paths:` filter restricting the lint to `.github/workflows/**`. A typo in `.github/actions/my-composite/action.yml`, in a reusable workflow `uses:` ref, or in a script the workflow `run:`s will not change the workflow file itself but will still break it. Lint on every PR.
- **NO** pre-commit-only enforcement with no CI job. Pre-commit is skipped by `git commit --no-verify`, by GitHub's web UI, by every `gh api repos/...` commit, and by every agent committing through the REST API. CI is the actual enforcement layer.
- **NO** installing actionlint without `shellcheck` and `pyflakes` on PATH. actionlint silently skips its embedded shell and Python checks if those binaries are missing — you get a green lint that misses the `run: bash -c "rm -rf $UNSET_VAR/"` bug it was supposed to catch. Verify by running `actionlint -version` and confirming `shellcheck` resolves on the runner.
- **NO** ignoring the lint output. If actionlint reports 40 violations across existing workflows, fix them (or document each suppression with a `# actionlint-ignore` comment and a reason). Do not blanket-ignore `.github/workflows/old-stuff/` to hide problems.
- **NO** copy-pasting the same lint into every workflow file. Use one dedicated `validate-ci.yml` workflow (or a reusable workflow) that lints all CI configs on every PR — duplication drifts.

Examples of BAD fixes:
- Adding `yamllint` to CI and claiming "the workflows are validated" — yamllint does not understand GitHub Actions semantics, won't catch typo'd `uses:` refs, won't catch `${{ env.FOO }}` referencing an unset env, won't catch deprecated `::set-output::`.
- `uses: rhysd/actionlint@main` — pulls floating HEAD on every run; one rhysd commit can break every PR in the repo.
- An actionlint job gated `on: pull_request: paths: ['.github/workflows/**']` — a typo in `.github/actions/build/action.yml` (composite action) never triggers the lint, ships to `main`, blows up the next deploy.
- Installing `actionlint` via `go install ...` without confirming `shellcheck` is on PATH — silent skip, the inline shell bugs ship.
- An actionlint pre-commit hook with no CI mirror — agent commits via `gh api repos/.../contents/...` bypass the hook, untrusted workflow changes land on `main`.
- A `lint:` job with `continue-on-error: true` "until we clean up the warnings" — six months later the warnings are unread noise.
- A `gitlab-ci-validate` npm step that schema-checks `.gitlab-ci.yml` but never resolves the `include:` chain — the failure mode this catches (missing remote template) ships to production.

Examples of GOOD fixes:
- A dedicated `validate-ci.yml` workflow for a GitHub Actions repo:
  ```yaml
  # .github/workflows/validate-ci.yml
  name: validate-ci
  on:
    pull_request:
    push:
      branches: [main]
  permissions:
    contents: read
  jobs:
    actionlint:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: install shellcheck (for actionlint embedded checks)
          run: sudo apt-get update && sudo apt-get install -y shellcheck
        - name: install pyflakes (for actionlint embedded checks)
          run: pip install pyflakes==3.2.0
        - name: install actionlint
          run: |
            bash <(curl -fsSL https://raw.githubusercontent.com/rhysd/actionlint/v1.7.7/scripts/download-actionlint.bash) 1.7.7
            echo "$PWD" >> "$GITHUB_PATH"
        - name: actionlint
          run: actionlint -color
  ```
- A `.pre-commit-config.yaml` block mirrored by a CI `pre-commit run --all-files` step:
  ```yaml
  repos:
    - repo: https://github.com/rhysd/actionlint
      rev: v1.7.7
      hooks:
        - id: actionlint
          additional_dependencies: []   # shellcheck/pyflakes assumed on PATH
  ```
- For a CircleCI repo:
  ```yaml
  # .circleci/config.yml (excerpt — lint job runs first, blocks workflow)
  version: 2.1
  jobs:
    validate:
      docker:
        - image: cimg/base:stable
      steps:
        - checkout
        - run:
            name: install circleci CLI
            command: |
              curl -fLSs https://raw.githubusercontent.com/CircleCI-Public/circleci-cli/v0.1.30431/install.sh | sudo bash
        - run:
            name: validate config
            command: circleci config validate .circleci/config.yml
  workflows:
    build:
      jobs:
        - validate
        - test:
            requires: [validate]
  ```
- For a GitLab repo, a `validate-ci` job using `glab` with a project token:
  ```yaml
  # .gitlab-ci.yml (excerpt)
  validate-ci:
    image: registry.gitlab.com/gitlab-org/cli:latest
    stage: .pre
    script:
      - glab auth login --token "$GITLAB_PROJECT_TOKEN" --hostname "$CI_SERVER_HOST"
      - glab ci lint --path .gitlab-ci.yml
    rules:
      - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  ```
- For a Drone repo, a separate GitHub Actions workflow that lints `.drone.yml` on every PR (so you don't depend on Drone itself to validate Drone):
  ```yaml
  - name: drone lint
    run: |
      curl -fsSL -o drone https://github.com/harness/drone-cli/releases/download/v1.7.0/drone_linux_amd64
      chmod +x drone
      ./drone lint .drone.yml --trusted
  ```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- actionlint (rhysd) — GitHub Actions linter with embedded shellcheck + pyflakes: https://github.com/rhysd/actionlint
- actionlint usage + CI integration: https://github.com/rhysd/actionlint/blob/main/docs/usage.md
- actionlint pre-commit hook: https://github.com/rhysd/actionlint/blob/main/docs/usage.md#pre-commit
- reviewdog/action-actionlint (annotates PRs with violations): https://github.com/reviewdog/action-actionlint
- CircleCI CLI — `circleci config validate`: https://circleci.com/docs/local-cli/
- CircleCI config packing (validate the packed output): https://circleci.com/docs/local-cli/#packing-a-config
- GitLab CI Lint API: https://docs.gitlab.com/ee/api/lint.html
- glab CLI (`glab ci lint`): https://gitlab.com/gitlab-org/cli/-/blob/main/docs/source/ci/lint.md
- Drone CLI lint: https://docs.drone.io/cli/drone-lint/
- Buildkite plugin linter: https://github.com/buildkite-plugins/buildkite-plugin-linter
- Buildkite dynamic pipeline dry-run: https://buildkite.com/docs/agent/v3/cli-pipeline
- Azure Pipelines VS Code service schema (consumable by check-jsonschema): https://github.com/microsoft/azure-pipelines-vscode/blob/main/service-schema.json
- Jenkins Declarative Linter: https://www.jenkins.io/doc/book/pipeline/development/#linter
- pre-commit GitHub Action (run hooks in CI so `--no-verify` doesn't bypass): https://github.com/pre-commit/action
- step-security/harden-runner (pair with actionlint for defence-in-depth on workflow trust): https://github.com/step-security/harden-runner
</system-reminder>
