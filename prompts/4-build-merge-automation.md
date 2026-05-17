[Readiness Fix] <REPO_NAME> Merge Automation

Fix the failing signal: Merge Automation ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Merge Automation
**Score**: [0/1]
**Description**: Merge queue, auto-merge, or merge bot — PRs land without a human babysitting the merge button once required checks and reviews pass
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Merge automation — check for at least one of the following, wired so it is actually load-bearing (not just toggled on with no enforcement underneath):

1. **GitHub merge queue** (GA): repository has a ruleset or classic branch protection on the default branch with "Require merge queue" enabled, AND every workflow that produces a required status check fires on `on: merge_group` (typically `types: [checks_requested]`) in addition to `pull_request`. A merge queue with zero `merge_group` triggers in CI means PRs sit in the queue forever waiting for checks that never run — this is a FAIL even though the toggle is on. Look for the trigger in `.github/workflows/*.yml`.
2. **GitHub auto-merge**: branch protection / ruleset has "Allow auto-merge" enabled AND the same branch requires at least one passing status check and one review. As of March 2026, GitHub blocks enabling auto-merge on a PR until all PR requirements are configured, so the toggle without requirements is meaningless. Look for `gh pr merge --auto` usage in scripts/CI, a `.github/auto_merge.yml` (if using a third-party action), or repo settings showing the toggle on. Bonus credit if a Dependabot/Renovate config uses auto-merge for patch/minor bumps with a non-empty allowlist (`automerge: true` scoped to `updateType: ["patch"]` or `packagePatterns`, not blanket).
3. **Mergify** (or Kodiak / Bors / Trunk Merge): a checked-in `.mergify.yml`, `.mergify/config.yml`, or `.github/mergify.yml` with `merge_protection_settings.auto_merge_conditions` (current API) or legacy `pull_request_rules[].conditions` + `actions.queue`/`actions.merge`. Conditions MUST include both a passing CI signal (`check-success=...`) and a human review signal (`#approved-reviews-by>=1`, or a CODEOWNERS-equivalent). A Mergify rule that only checks a label or only checks CI is a FAIL — it lets a bot or a single contributor merge unreviewed code.
4. **Bot account merge with review gating**: a GitHub App or bot user (Renovate, Dependabot, repo-specific app) is configured to merge PRs, AND branch protection still requires the same review/check set for that bot — i.e. the bot is not in a bypass list. Verify via the ruleset's `bypass_actors` array (should NOT contain the merge bot for review enforcement) and any `CODEOWNERS` entry the bot would need to satisfy.

A repo where humans click "Merge pull request" manually on every PR, even with green CI, FAILs this signal — the goal is that an agent can open a PR, satisfy the gates, and the merge happens without a second human action.

## Your Task

1. Explore the repo: list `.github/workflows/*.yml`, `.mergify.yml` / `.mergify/`, `.github/mergify.yml`, `.github/dependabot.yml`, `renovate.json` / `.renovaterc*`, and any branch protection / ruleset info reachable via `gh api repos/{owner}/{repo}/rulesets` and `gh api repos/{owner}/{repo}/branches/{default}/protection`. Identify which CI workflows produce **required** status checks.
2. Pick the lightest automation path that fits the repo:
   - If the repo already uses GitHub Actions for required checks and the team is small, enable **GitHub merge queue** (free, native, GA) and add the `merge_group` trigger to every required workflow.
   - If the repo wants per-PR opt-in instead of a global queue, enable **auto-merge** in repo settings and document `gh pr merge --auto --squash` in CONTRIBUTING.md / agent instructions, with required checks + reviews enforced via ruleset.
   - If the repo already runs Mergify or Renovate, extend the existing config — do not add a second merge mechanism on top.
3. Make the changes:
   - Update each required-check workflow with `on: { pull_request: {...}, merge_group: { types: [checks_requested] } }`.
   - Add or update the branch protection ruleset (`gh api -X POST repos/{owner}/{repo}/rulesets ...`) to require the merge queue OR allow auto-merge, with `required_status_checks` listing the exact check names and `pull_request.required_approving_review_count >= 1`.
   - For Mergify, write a real `.mergify.yml` with `queue_rules` + `merge_protection_settings.auto_merge_conditions` covering both `check-success` and `#approved-reviews-by>=1`.
   - For Dependabot/Renovate auto-merge, scope it (`updateType: ["patch", "minor"]` for `devDependencies` only, or a named package allowlist) — never blanket auto-merge of all updates.
4. Verify: open a throwaway PR (or use an existing open PR), confirm the merge queue accepts it / auto-merge enables / Mergify queues it, and that direct `git push` to the default branch is rejected. Capture the queue or `gh pr view <n> --json autoMergeRequest` output in the PR description.
5. Keep changes focused on this signal — do not retune unrelated workflow jobs or branch protection rules.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** enabling auto-merge on a branch with zero required status checks and zero required reviews — that is a one-click footgun. Anything pushed to the PR merges instantly.
- **NO** turning on the merge queue without adding `merge_group` to the CI workflow's `on:` block. The queue will park every PR forever; the team will disable the queue within a week and the toggle becomes worse-than-useless cargo cult config.
- **NO** Mergify rules whose only condition is a label (`label=automerge`) or only a check (`check-success=ci`). Both halves — green CI AND human review (or CODEOWNERS) — are mandatory. A label-only rule lets anyone with write access merge unreviewed code by clicking a button.
- **NO** adding the merge bot to `bypass_actors` on the ruleset so it can skip required reviews. The bot must satisfy the same gates as a human; bypass is for break-glass admins only.
- **NO** blanket Dependabot/Renovate auto-merge (`automerge: true` at the root, no `packageRules` scoping). One compromised transitive dep update lands in main while everyone is asleep. Scope by `updateType` and/or `packagePatterns`.
- **NO** concurrency-less merge queue workflows — without `concurrency: { group: merge-queue-${{ github.ref }}, cancel-in-progress: false }` on the `merge_group` job, queued PRs can race and waste minutes.
- **NO** committing a `.mergify.yml` that references queues, rules, or check names the repo does not actually have. Mergify will surface a config error on every PR and the team will revert.
- **NO** force-merge / admin-merge buttons left enabled alongside the automation — `enforce_admins: true` (classic) or omitting admins from ruleset `bypass_actors` keeps the gate honest.

Examples of BAD fixes:
- Flipping "Allow auto-merge" in repo settings, leaving "Require status checks before merging" empty, and calling the signal done. First PR with `gh pr merge --auto` lands in main with red CI.
- Adding `on: merge_group:` to one workflow out of six required ones. The merge queue waits for the other five forever; queued PRs time out after 60 minutes.
- A `.mergify.yml` with `pull_request_rules: [{ name: auto, conditions: [label=ship-it], actions: { merge: {} } }]`. Anyone with triage rights can apply the label; no review, no CI gate.
- `renovate.json` with `"automerge": true` at the root. Renovate will auto-merge a `lodash` major bump at 3 AM.

Examples of GOOD fixes:
- A repo with a single `ci.yml` workflow producing the required `test` check, fixed by:
  ```yaml
  # .github/workflows/ci.yml
  on:
    pull_request:
      branches: [main]
    merge_group:
      types: [checks_requested]

  concurrency:
    group: ci-${{ github.ref }}
    cancel-in-progress: ${{ github.event_name == 'pull_request' }}

  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - run: pnpm install --frozen-lockfile
        - run: pnpm run lint
        - run: pnpm run test
  ```
  Paired with a ruleset created via:
  ```bash
  gh api -X POST repos/<OWNER>/<REPO>/rulesets \
    -f name='main-merge-queue' \
    -f target='branch' \
    -F enforcement='active' \
    -F 'conditions[ref_name][include][]=~DEFAULT_BRANCH' \
    -F 'rules[][type]=required_status_checks' \
    -F 'rules[][parameters][required_status_checks][][context]=test' \
    -F 'rules[][type]=pull_request' \
    -F 'rules[][parameters][required_approving_review_count]=1' \
    -F 'rules[][type]=merge_queue'
  ```
- A Mergify config that gates on both CI and a review:
  ```yaml
  # .mergify.yml
  queue_rules:
    - name: default
      queue_conditions:
        - check-success=test
        - "#approved-reviews-by>=1"
        - label!=do-not-merge

  merge_protection_settings:
    auto_merge: true
    auto_merge_conditions:
      - check-success=test
      - "#approved-reviews-by>=1"
      - base=main
  ```
- A scoped Renovate auto-merge for low-risk updates only:
  ```json
  {
    "extends": ["config:recommended"],
    "packageRules": [
      {
        "matchUpdateTypes": ["patch"],
        "matchDepTypes": ["devDependencies"],
        "automerge": true,
        "platformAutomerge": true
      }
    ]
  }
  ```
- A `CONTRIBUTING.md` (or `AGENTS.md`) snippet telling agents: "After opening a PR and pushing the final commit, run `gh pr merge --auto --squash` — the merge fires once `test` is green and one approval lands. Do NOT use `gh pr merge --admin` to bypass."

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, which automation path you picked, and how you verified the gate actually fires

## References

- GitHub merge queue (GA) & `merge_group` trigger: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- GitHub auto-merge for pull requests: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request
- `gh pr merge` CLI reference (`--auto`, `--squash`, `--merge`, `--rebase`): https://cli.github.com/manual/gh_pr_merge
- GitHub rulesets API (create / update branch ruleset with merge queue + required checks): https://docs.github.com/en/rest/repos/rules
- Auto-merge behavior change requiring all PR requirements configured first (community discussion #190610): https://github.com/orgs/community/discussions/190610
- Mergify configuration file format: https://docs.mergify.com/configuration/file-format/
- Mergify `merge_protection_settings.auto_merge` + `auto_merge_conditions`: https://docs.mergify.com/changelog/2026-04-21-auto-merge-setting-in-merge-protections/
- Mergify merge action reference: https://docs.mergify.com/workflow/actions/merge/
- Renovate automerge configuration and gotchas: https://docs.renovatebot.com/key-concepts/automerge/
- Dependabot auto-merge pattern via GitHub Actions: https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions
- Neat GitHub Actions patterns for merge queues (concurrency, conditional jobs): https://boinkor.net/2023/11/neat-github-actions-patterns-for-github-merge-queues/
</system-reminder>
