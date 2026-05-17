[Readiness Fix] <REPO_NAME> CI Pipeline

Fix the failing signal: CI Pipeline ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: CI Pipeline
**Score**: [0/1]
**Description**: Automated checks on every push or PR
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

CI pipeline – check for a checked-in pipeline definition that actually runs on every push and pull request. PASS requires a workflow file at one of the canonical paths AND at least one job that executes a real check (lint, test, build, or type-check). Acceptable artifacts:

1. **GitHub Actions**: `.github/workflows/*.yml` with both `on: push` (or `on: push: branches: [main, master]`) AND `on: pull_request`. The workflow must contain at least one `job` with `steps` that run something beyond `actions/checkout`. A workflow that only checks out the repo or only runs `echo "hello"` is a FAIL.
2. **GitLab CI**: `.gitlab-ci.yml` with at least one defined `stage` and one job that runs a script. The default `workflow:rules` (or absence thereof) must trigger on merge requests and pushes to the default branch.
3. **CircleCI**: `.circleci/config.yml` with a `workflows` block referencing at least one job whose `steps` include a real command. The job must be wired to run on PRs (CircleCI runs on every push by default; verify branch filters do not exclude PRs).
4. **Jenkins**: `Jenkinsfile` (declarative or scripted) with at least one `stage` containing a real `sh`/`bat` step. A multibranch pipeline configuration is implied — note this in the PR description.
5. **Buildkite / Drone / Azure Pipelines / Bitbucket Pipelines**: `.buildkite/pipeline.yml`, `.drone.yml`, `azure-pipelines.yml`, or `bitbucket-pipelines.yml` with equivalent structure — defined jobs, real commands, PR + push triggers.

Also verify the pipeline is wired to fail on errors: shell steps must not swallow exit codes (`|| true`, `set +e` without re-enabling, `continue-on-error: true` on every step). A workflow that always reports green regardless of test outcome FAILs this signal.

A README sentence saying "we run CI on Jenkins" without a checked-in pipeline file is documentation, not infrastructure, and FAILs this signal.

## Your Task

1. Explore the repository to understand the current state related to this signal — list every file under `.github/workflows/`, `.circleci/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.buildkite/`, `.drone.yml`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`. Identify the repo's language/package manager and the commands it uses for lint, test, and build (check `package.json` scripts, `Makefile`, `pyproject.toml`, `Cargo.toml`, `go.mod`).
2. Make **substantive improvements** by adding a real, project-tuned pipeline:
   - Pick the CI provider matching the repo's host (GitHub → Actions, GitLab → GitLab CI, etc.). If unclear, default to GitHub Actions.
   - Create the workflow file at the canonical path.
   - Wire triggers: `on: push: branches: [main, master]` AND `on: pull_request`.
   - Add jobs that run the repo's actual lint, test, and build commands — not generic `echo` placeholders. For Node: `npm ci && npm run lint && npm test && npm run build`. For Python: `pip install -e . && ruff check && pytest --collect-only` (or full `pytest` if the suite is fast).
   - Pin action versions (e.g. `actions/checkout@v4`, `actions/setup-node@v4`) — do not use `@main` or `@master`.
   - Cache dependencies (`actions/setup-node` with `cache: npm`, `actions/setup-python` with `cache: pip`) so feedback stays under 10 minutes (links to feature #4 fast CI feedback).
3. Verify the pipeline runs: push to a branch, open a PR, confirm the workflow triggers and at least one job completes (pass or fail — runnability is the signal, not green). Add a status badge to the top of `README.md` pointing at the workflow.
4. If branch protection is configured (links to feature #54), mark the new workflow jobs as required status checks — but DO NOT do this if the repo has no existing protection rules; that is a separate signal.
5. Keep changes focused on this signal — do not refactor unrelated code.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** workflow files containing only `actions/checkout@v4` and nothing else — that proves nothing runs.
- **NO** `on: workflow_dispatch` as the only trigger — manual-only workflows do not gate PRs and fail this signal.
- **NO** workflows that trigger on `push` to `main` but omit `pull_request` — agents merge via PR, so pre-merge feedback is mandatory.
- **NO** `continue-on-error: true` on the lint/test/build steps themselves — the workflow will always be green and the signal becomes meaningless. (Acceptable on optional matrix legs or experimental jobs only.)
- **NO** swallowed exit codes via `run: npm test || true`, `run: pytest; exit 0`, or `set +e` without re-enabling.
- **NO** floating action versions (`actions/checkout@main`, `@master`, `@v4-beta`) — pin to a released tag or SHA.
- **NO** secrets pasted in plain text into the workflow YAML — use `${{ secrets.NAME }}` and document required secrets in `README.md` or `AGENTS.md`.
- **NO** copying a generic template verbatim — a Python repo with `npm ci` in its workflow signals zero project knowledge.
- **NO** putting the workflow in a path GitHub Actions does not read (`.workflows/`, `ci/github.yml`, `.github/ci.yml`) — only `.github/workflows/*.yml` is honored.

Examples of BAD fixes:
- A `.github/workflows/ci.yml` containing one job with a single `- run: echo "CI placeholder"` step — passes the file-exists check but enforces nothing.
- `on: push: branches: [main]` with no `pull_request` trigger — agents open PRs from feature branches and get zero pre-merge signal.
- Adding `continue-on-error: true` at the job level so red tests still report green — strictly worse than no CI because the green badge lies.
- A workflow that runs `npm install` (non-deterministic) instead of `npm ci` — agents get flaky CI from lockfile drift.
- `runs-on: self-hosted` without a documented runner — workflow queues forever on PRs from forks or new contributors.

Examples of GOOD fixes:
- For a Node/TypeScript repo, `.github/workflows/ci.yml`:
  ```yaml
  name: CI
  on:
    push:
      branches: [main]
    pull_request:
  jobs:
    lint-test-build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with:
            node-version: '20'
            cache: 'npm'
        - run: npm ci
        - run: npm run lint
        - run: npm test
        - run: npm run build
  ```
- For a Python repo with `pyproject.toml`:
  ```yaml
  name: CI
  on:
    push:
      branches: [main]
    pull_request:
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: '3.12'
            cache: 'pip'
        - run: pip install -e ".[dev]"
        - run: ruff check .
        - run: pytest -x
  ```
- For GitLab, `.gitlab-ci.yml`:
  ```yaml
  stages: [test]
  test:
    stage: test
    image: node:20-alpine
    cache:
      paths: [node_modules/]
    script:
      - npm ci
      - npm run lint
      - npm test
    rules:
      - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  ```
- A status badge appended to `README.md`:
  ```markdown
  [![CI](https://github.com/<ORG>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<ORG>/<REPO>/actions/workflows/ci.yml)
  ```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- GitHub Actions workflow syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- GitHub Actions events that trigger workflows (`push`, `pull_request`): https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows
- GitHub Actions security hardening (pinning, secrets): https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions
- Adding a workflow status badge: https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge
- GitLab CI `.gitlab-ci.yml` reference: https://docs.gitlab.com/ee/ci/yaml/
- GitLab CI `workflow:rules` for MR + branch triggers: https://docs.gitlab.com/ee/ci/yaml/workflow.html
- CircleCI configuration reference: https://circleci.com/docs/configuration-reference/
- Jenkins declarative pipeline syntax: https://www.jenkins.io/doc/book/pipeline/syntax/
- Buildkite pipeline definition: https://buildkite.com/docs/pipelines/defining-steps
- Bitbucket Pipelines configuration: https://support.atlassian.com/bitbucket-cloud/docs/configure-bitbucketpipelinesyml/
</system-reminder>
