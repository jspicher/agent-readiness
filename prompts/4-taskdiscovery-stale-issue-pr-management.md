[Readiness Fix] <REPO_NAME> Stale Issue / PR Management

Fix the failing signal: Stale Issue / PR Management ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Stale Issue / PR Management
**Score**: [0/1]
**Description**: Automation to close or label stale items so the backlog reflects real, actionable work
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Stale issue / PR management – check for a checked-in, scheduled automation that labels and (optionally) closes inactive issues and pull requests, with explicit exemptions for tracked work. PASS requires at least one of the following, configured and actually wired up:

1. **GitHub Actions**: `.github/workflows/stale.yml` running `actions/stale@v9` (or newer) on a `schedule:` trigger, with non-default values for `days-before-issue-stale`, `days-before-pr-stale`, an `exempt-issue-labels` list that names the repo's actual tracked-work labels (e.g. `pinned`, `epic`, `roadmap`, `security`, `good-first-issue`), and `stale-issue-message` / `stale-pr-message` strings that are project-specific, not the action's empty default. `operations-per-run` raised above the default 30 if the backlog is large. A bare workflow file calling `actions/stale` with all defaults is a FAIL — defaults stale at 60 days, close at 7, no exemptions, and the generic template message is widely considered hostile.
2. **Probot Stale / stale-action**: `.github/stale.yml` (Probot Stale app) or `.github/workflows/stale.yml` (`probot/stale-action`) with `daysUntilStale`, `daysUntilClose`, `exemptLabels`, and a non-empty `markComment`. Probot Stale is deprecated upstream (the GitHub App was sunset), so net-new adoption should prefer `actions/stale@v9`; an existing Probot config still counts if it's actively scheduled.
3. **Mergify**: `.mergify.yml` with rules that match `updated-at<…days ago` and either apply a `stale` label, post a comment, or close — paired with `-label=pinned` / `-label=epic` style conditions so tracked work is exempt.
4. **GitLab / Bitbucket equivalent**: GitLab CI scheduled pipeline that calls the GitLab API to label or close inactive issues / MRs, with documented exemption rules. A README sentence describing the policy is documentation, not automation, and FAILs this signal.

Also verify the automation actually runs: the workflow must have a `schedule:` cron (and ideally `workflow_dispatch:` for manual runs), the cron must not be commented out, and the job must have `permissions: issues: write` and `pull-requests: write` or it will silently no-op on PRs raised from forks. A workflow on `push:` only does not count — stale management is by definition a time-based job.

## Your Task

1. Explore the repository to understand the current state — list every `.github/workflows/*.yml`, `.github/stale.yml`, `.mergify.yml`, and any existing labels (`gh label list`). Note the repo's actual tracked-work labels (`epic`, `roadmap`, `pinned`, `security`, `help-wanted`, `good-first-issue`, plus any project-specific equivalents like `needs-triage` or `blocked`).
2. Add a real, project-tuned `.github/workflows/stale.yml`:
   - Pin to `actions/stale@v9` (or the current major) by SHA or tag.
   - Use **different** day thresholds for issues vs. PRs (issues rot slower than review queues — typical: issues 60/14, PRs 30/7).
   - Populate `exempt-issue-labels` and `exempt-pr-labels` with the labels the repo actually uses for tracked work — never an empty string.
   - Write `stale-issue-message` and `stale-pr-message` that name the project and tell the reader what to do (comment, add an exempt label, request an extension) — not the generic "this has been automatically marked as stale" template.
   - Set `close-issue-message` / `close-pr-message` that explicitly invite reopening — closure is not a verdict.
   - Run on a humane cron (weekday mid-morning UTC; never weekends — see anti-patterns).
   - Add `workflow_dispatch:` so maintainers can dry-run.
   - Grant minimum `permissions:` block (`issues: write`, `pull-requests: write`, `contents: read`).
3. If the labels you reference do not exist yet, create them with `gh label create` so the exemption rules actually match something.
4. Dry-run the workflow with `debug-only: true` first to confirm it picks up the expected items and exempts the rest. Remove the flag before opening the PR.
5. Keep changes focused on this signal — do not edit unrelated workflows.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** unpinned `actions/stale@main` or floating `@v9` without a tag — pin to a tag the repo's other workflows use, or to a SHA.
- **NO** aggressive thresholds (`days-before-issue-stale: 7`). 7 days is hostile; valid bug reports get nuked over a long weekend. Issues: ≥45 days. PRs: ≥21 days.
- **NO** empty `exempt-issue-labels: ''` or omitting the key. Without exemptions, the bot will close `epic`, `roadmap`, `security`, and `good-first-issue` items. This is the single most common failure mode and the reason maintainers rip stale bots back out within a month.
- **NO** generic stale comment ("This issue has been automatically marked as stale because it has not had recent activity. It will be closed if no further activity occurs.") — that template has been documented as anti-user for years (see Tomlinson, "Most stale bots are anti-user and anti-contributor"). Write something that names the project and gives the reader a concrete way to keep it open.
- **NO** `close-issue-message: ''` — closing an issue with zero comment is the rudest possible interaction. Always leave a close message that invites reopening.
- **NO** running the schedule on Saturday/Sunday (`cron: '0 0 * * *'` will hit weekends). Use a weekday-only cron (`cron: '0 9 * * 1-5'`) — getting a "your issue is stale" notification on Sunday evening makes contributors quit.
- **NO** running every hour. `actions/stale` paginates via `operations-per-run` (default 30); a daily cron is the standard. Hourly will exhaust the API budget and rate-limit other workflows.
- **NO** omitting `permissions:` — leaving it implicit means the workflow inherits the repo default, which on hardened repos is read-only, and the action silently fails to label.
- **NO** copying a generic template verbatim. A Python repo with `exempt-issue-labels: 'frontend,backend'` signals zero project knowledge. Read the actual `gh label list` output and pick from it.
- **NO** combining stale with auto-close on PRs that are blocked on a reviewer. Use `exempt-pr-labels: 'awaiting-review,blocked-by-upstream'` or restrict stale-to-PRs to `only-pr-labels: 'needs-rebase,needs-author-response'` so the bot only chases the author, never the reviewer.

Examples of BAD fixes:
- A `stale.yml` that is `uses: actions/stale@v9` with no `with:` block — runs with all defaults, closes everything, generic message, zero exemptions.
- `days-before-issue-stale: 7, days-before-issue-close: 1` — closes a bug filed Monday by Wednesday.
- `exempt-issue-labels: 'pinned'` on a repo whose tracked-work label is `epic` — exemption matches nothing, epics get closed.
- Stale comment copy-pasted from a Node.js repo onto a Rust repo, mentioning `npm` commands.
- Schedule `cron: '0 * * * *'` (hourly) — burns the Actions minutes budget and trips secondary rate limits.
- Workflow with no `permissions:` block in a repo that defaults to read-only — bot reports success but never labels.

Examples of GOOD fixes:
- A `.github/workflows/stale.yml` like:
  ```yaml
  name: Mark and close stale issues and PRs
  on:
    schedule:
      - cron: '0 9 * * 1-5'  # 09:00 UTC, weekdays only
    workflow_dispatch:
  permissions:
    issues: write
    pull-requests: write
    contents: read
  jobs:
    stale:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/stale@v9
          with:
            days-before-issue-stale: 60
            days-before-issue-close: 14
            days-before-pr-stale: 30
            days-before-pr-close: 7
            stale-issue-label: 'stale'
            stale-pr-label: 'stale'
            exempt-issue-labels: 'pinned,epic,roadmap,security,good-first-issue,help-wanted,blocked'
            exempt-pr-labels: 'pinned,blocked,work-in-progress,awaiting-review,dependencies'
            exempt-all-milestones: true
            exempt-all-assignees: false
            stale-issue-message: >
              This issue has had no activity in 60 days. If it is still
              relevant to <REPO_NAME>, comment with new context or add the
              `pinned` label to keep it open. Otherwise it will close in 14
              days — reopening is welcome at any time.
            stale-pr-message: >
              This PR has had no activity in 30 days. If you are still
              working on it, push a commit or add `work-in-progress` to keep
              it open. Otherwise it will close in 7 days. Maintainers: if
              you are waiting on us, add `awaiting-review`.
            close-issue-message: >
              Closing for inactivity. This is not a judgment on the report —
              if it is still reproducible, please comment to reopen.
            close-pr-message: >
              Closing for inactivity. Push a new commit or comment to
              reopen; no need to file a new PR.
            operations-per-run: 100
            ascending: true
  ```
- A companion `gh label create` block (or `.github/labels.yml` synced via `crazy-max/ghaction-github-labeler`) that actually creates `pinned`, `epic`, `blocked`, `awaiting-review`, etc., so the exemption strings are not aspirational.
- A first-run with `debug-only: true` posted as a workflow log link in the PR description, showing exactly which issues would be staled and which would be exempt.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- `actions/stale` (canonical): https://github.com/actions/stale
- `actions/stale` action.yml (every supported input): https://github.com/actions/stale/blob/main/action.yml
- Marketplace listing with examples: https://github.com/marketplace/actions/close-stale-issues
- Probot Stale (deprecated app, still-valid YAML reference): https://github.com/probot/stale
- Probot stale-action (Actions-native port): https://github.com/probot/stale-action
- Mergify stale rules: https://docs.mergify.com/configuration/conditions/#updated-at
- "Most stale bots are anti-user and anti-contributor" (Jacob Tomlinson, the definitive critique): https://jacobtomlinson.dev/posts/2024/most-stale-bots-are-anti-user-and-anti-contributor-but-they-dont-have-to-be/
- "Please stop using Probot's stale bot" (pypa/virtualenv discussion of the failure modes): https://github.com/pypa/virtualenv/issues/1311
- Empirical study of stale-bot adoption ("Should I Stale or Should I Close?", Wiese et al.): https://igorwiese.com/images/papers/Paper_BotSE_19.pdf
- `crazy-max/ghaction-github-labeler` for syncing the exemption labels: https://github.com/crazy-max/ghaction-github-labeler
</system-reminder>
