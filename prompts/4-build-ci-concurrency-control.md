[Readiness Fix] <REPO_NAME> CI Concurrency Control

Fix the failing signal: CI Concurrency Control ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: CI Concurrency Control
**Score**: [0/1]
**Description**: CI workflows cancel superseded runs and serialize resource-bound jobs via concurrency groups so a fresh push does not queue behind a stale run
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

CI concurrency control – check for cancel-in-progress and concurrency groups on the primary PR / branch workflows. PASS requires at least one of the following, scoped to a per-ref group (not a global string):

1. **GitHub Actions**: a workflow-level `concurrency:` block with a `group:` expression that includes `${{ github.workflow }}` AND `${{ github.ref }}` (or `github.head_ref` for PRs), and `cancel-in-progress: true` on workflows that run on `pull_request` / non-default branch `push`. A job-level `concurrency:` is allowed for serializing a single resource-bound job (e.g. integration tests against a shared DB) but does NOT substitute for the workflow-level block on PR feedback workflows.
2. **GitLab CI**: `interruptible: true` set on jobs in the merge-request pipeline (workflow-level or per-job), combined with a project setting that enables auto-cancel of redundant pipelines, OR a `workflow:auto_cancel:on_new_commit: interruptible` block in `.gitlab-ci.yml`.
3. **CircleCI**: auto-cancel-redundant-workflows enabled at the project level (Project Settings → Advanced) AND a comment / docs reference in `.circleci/config.yml` confirming the setting, since the toggle itself is not in-repo.
4. **Buildkite / other**: explicit `concurrency_group` + `concurrency: 1` (or `cancel_intermediate_builds: true` on the pipeline) for ref-scoped serialization.

Deploy / release / publish workflows MUST be excluded from cancel-in-progress (a half-cancelled `npm publish` or `terraform apply` corrupts state). Those workflows should still have a `concurrency:` group (so two deploys can't race), but with `cancel-in-progress: false` — i.e. queue, never cancel.

A `concurrency: ci` string (no `github.ref` interpolation) on a PR workflow is a FAIL: every branch shares one slot and pushes to PR #42 cancel PR #41. A `cancel-in-progress: true` block on a `deploy.yml` that publishes to npm or pushes Docker tags is a FAIL: it can leave the registry in a partial state.

## Your Task

1. Enumerate every workflow file (`.github/workflows/*.yml`, `.gitlab-ci.yml`, `.circleci/config.yml`, `.buildkite/*.yml`). For each, classify it as: PR-feedback (cancellable), deploy/release (queue-only), or scheduled/maintenance (usually leave alone).
2. Make **substantive improvements**:
   - On every PR-feedback workflow, add a workflow-level `concurrency:` block keyed by workflow + ref, with `cancel-in-progress: true`.
   - On every deploy / release / publish workflow, add a workflow-level `concurrency:` block keyed by the deploy target (e.g. environment name), with `cancel-in-progress: false`.
   - For any single resource-bound job (shared staging DB, single Cloudflare zone, one Stripe test account), add a job-level `concurrency:` with `cancel-in-progress: false` so runs queue instead of clobbering each other.
3. Verify the change works: push a no-op commit to a branch, then push a second commit within ~30s. Confirm in the Actions UI that the first run shows "Cancelled" and only the second completes. For deploy workflows, confirm two simulated deploy triggers queue (run sequentially) rather than cancelling.
4. Keep changes focused on this signal — do not retune triggers, matrices, or runner sizes.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** global string groups (`concurrency: ci`, `concurrency: build`) on PR workflows — every branch collides and active PRs cancel each other.
- **NO** `cancel-in-progress: true` on deploy / publish / release / migration workflows — a cancelled `npm publish`, `docker push`, `terraform apply`, `flyway migrate`, or `gh release create` leaves the artifact registry, infra, or DB in a partial state.
- **NO** job-level `concurrency:` as a substitute for the workflow-level block on PR feedback — only a workflow-level group dedupes the whole run; job-level only serializes that one job.
- **NO** omitting `${{ github.workflow }}` from the group expression — multiple workflows on the same ref will fight for the same slot and cancel unrelated runs.
- **NO** adding `concurrency:` only to the lint workflow and leaving the slow test workflow untouched — the slow one is the whole reason this signal exists.
- **NO** copy-pasting a generic block without checking what the workflow actually does. Read each file before editing.

Examples of BAD fixes:
- `concurrency: ci` at workflow level on `pr.yml` — kills cross-PR runs.
- `concurrency: { group: ${{ github.ref }}, cancel-in-progress: true }` on `release.yml` — corrupts releases when a maintainer pushes a tag fix 10s after the first tag.
- Job-level `concurrency:` on `test` job only, while `build`, `lint`, and `e2e` jobs in the same workflow still pile up.
- A `group:` expression that interpolates `${{ github.sha }}` — every commit has a unique SHA so nothing ever dedupes.
- Adding the block to `.github/workflows/codeql.yml` and skipping the actual PR test workflow because "CodeQL was easier to edit".

Examples of GOOD fixes:

PR-feedback workflow (`.github/workflows/pr.yml`):

```yaml
name: PR Checks
on:
  pull_request:
  push:
    branches-ignore: [main, master, release/*]

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm run lint
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm run test
```

Deploy workflow with serialized, non-cancellable group (`.github/workflows/deploy.yml`):

```yaml
name: Deploy
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]

concurrency:
  group: deploy-${{ inputs.environment || 'production' }}
  cancel-in-progress: false   # queue, never cancel — protects npm publish / terraform apply atomicity

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment || 'production' }}
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm run build
      - run: pnpm run deploy
```

Resource-bound job that serializes inside an otherwise-cancellable workflow:

```yaml
jobs:
  e2e-shared-db:
    # Workflow-level concurrency above still applies; this nested group only
    # serializes the e2e job across all refs because there is one staging DB.
    concurrency:
      group: e2e-staging-db
      cancel-in-progress: false
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm run test:e2e
```

GitLab equivalent (`.gitlab-ci.yml`):

```yaml
workflow:
  auto_cancel:
    on_new_commit: interruptible

test:
  interruptible: true
  script: pnpm run test

deploy:production:
  interruptible: false      # protect atomic deploys
  resource_group: production
  script: pnpm run deploy
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- GitHub Actions `concurrency` (workflow + job, group expression, cancel-in-progress): https://docs.github.com/en/actions/using-jobs/using-concurrency
- GitHub Actions concurrency context (`github.workflow`, `github.head_ref`, `github.ref`): https://docs.github.com/en/actions/learn-github-actions/contexts#github-context
- GitHub Actions `concurrency.cancel-in-progress` semantics for queued vs running: https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs
- GitLab `interruptible` keyword: https://docs.gitlab.com/ee/ci/yaml/#interruptible
- GitLab `workflow:auto_cancel:on_new_commit`: https://docs.gitlab.com/ee/ci/yaml/#workflowauto_cancelon_new_commit
- GitLab `resource_group` (serialize deploys to one environment): https://docs.gitlab.com/ee/ci/resource_groups/
- CircleCI auto-cancel-redundant-workflows: https://circleci.com/docs/skip-build/#auto-cancelling
- Buildkite `cancel_intermediate_builds` and `concurrency_group`: https://buildkite.com/docs/pipelines/controlling-concurrency
- Why deploy jobs must not cancel (npm publish atomicity, Terraform state lock): https://github.blog/changelog/2021-04-19-github-actions-limit-workflow-run-or-job-concurrency/
</system-reminder>
