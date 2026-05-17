[Readiness Fix] <REPO_NAME> Automated Code Review Checks

Fix the failing signal: Automated Code Review Checks ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Automated Code Review Checks
**Score**: [0/1]
**Description**: Bot-driven review checks beyond CI — rule-based assertions on the diff, ownership-driven required reviewers, or quality-gate bots that comment and block on PRs
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Automated review checks beyond CI – check for bot-driven review enforcement on PRs that goes past "tests pass / lint passes". PASS requires at least one of the following, wired to actually block or visibly comment on PRs:

1. **Danger.js / Danger Swift / Danger Python** – a checked-in `dangerfile.js` / `Dangerfile.ts` / `Dangerfile` at repo root or `.danger/`, invoked from CI (`.github/workflows/*.yml`, `.gitlab-ci.yml`, `bitrise.yml`) via `npx danger ci` or equivalent. Rules MUST make real assertions on the diff (added lines, changed files, PR metadata), e.g. `fail("PR has no description")`, `warn("Tests missing for changes to src/api/*")`, `fail("Migration added without rollback")`. An empty Dangerfile with only `markdown("Thanks!")` is a FAIL.
2. **CODEOWNERS + branch protection** – `.github/CODEOWNERS` (or `CODEOWNERS` at root / `docs/CODEOWNERS`) with concrete path-to-owner mappings, AND branch protection on the default branch with "Require review from Code Owners" enabled. Verify via `gh api repos/<owner>/<repo>/branches/<default>/protection` and look for `required_pull_request_reviews.require_code_owner_reviews: true`. A CODEOWNERS file alone, without the branch-protection toggle, is a FAIL — the check is unenforced.
3. **SonarCloud / SonarQube quality-gate bot** – `sonar-project.properties` or `.github/workflows/sonarcloud.yml` configured with a non-default quality gate that has real conditions (new code coverage ≥ N%, no new blocker issues, duplicated lines ≤ N%) AND the SonarCloud GitHub app installed so it posts an inline check + comment. A workflow that runs the scanner but uses the built-in "Sonar way" gate with `coverage: > 0%` is effectively permissive — flag as weak unless the project deliberately set it.
4. **Reviewable / ReviewBot / Graphite / Reviewdog / PullApprove / Mergify rules** – a config file (`.reviewable.json`, `pullapprove.yml`, `.mergify.yml`, `.reviewdog.yml`) with policy rules that gate merge, e.g. Mergify `queue_rules` requiring `#approved-reviews-by>=2` AND `check-success=danger`, or PullApprove groups with `required: true`.

Verify the check actually runs AND can fail: open the most recent 5 merged PRs (`gh pr list --state merged --limit 5 --json number,reviews,comments,statusCheckRollup`) and confirm at least one shows a bot-posted review comment, a CODEOWNERS-attributed required reviewer, or a quality-gate check on the rollup. A bot that posts on every PR but whose check is "neutral" / non-blocking does NOT count — distinguish a `success/failure` check run from an `informational` comment.

This signal is distinct from **Automated PR Review Generation (#65)**. #65 covers bots that GENERATE new prose review content (AI summaries, line-by-line suggestions from an LLM). #64 covers POLICY-BASED checks that assert known rules against the diff (Danger rules, CODEOWNERS routing, Sonar gate thresholds). Both can coexist; they are scored separately.

## Your Task

1. Explore the repository to understand the current state — list every `.github/workflows/*.yml`, `Dangerfile*`, `dangerfile*`, `CODEOWNERS`, `sonar-project.properties`, `.mergify.yml`, `pullapprove.yml`, `.reviewdog.yml`. Note the languages/frameworks the repo uses so the rules are project-tuned.
2. Check current branch protection: `gh api repos/<owner>/<repo>/branches/<default>/protection 2>/dev/null | jq '.required_pull_request_reviews'`. If the call 404s, branch protection is off entirely — that is the first fix.
3. Make **substantive improvements** by adding at least one policy-based check, wired end to end:
   - Add `dangerfile.js` (or `.ts` / `.py`) with at minimum 3 real assertions tuned to the repo: missing PR description, missing tests for changed source files, oversized diff, missing changelog entry, lockfile-without-package-json edits, migration-without-rollback, etc.
   - Add a GitHub Actions step that runs `npx danger ci` (or `bundle exec danger`, `danger-python ci`) on `pull_request` events with a `DANGER_GITHUB_API_TOKEN` set from `secrets.GITHUB_TOKEN`.
   - Add `.github/CODEOWNERS` with real path mappings to existing GitHub users/teams. Verify every handle resolves: `gh api users/<handle>` for each individual; `gh api orgs/<org>/teams/<team>` for each team. A CODEOWNERS entry pointing to `@former-employee` or `@org/ghost-team` silently disables review routing for that path.
   - Enable branch protection with code-owner review required: `gh api -X PUT repos/<owner>/<repo>/branches/<default>/protection --input protection.json` where the JSON sets `required_pull_request_reviews.require_code_owner_reviews=true` and `required_status_checks.contexts` includes the Danger job name.
   - If the project already uses Sonar, tighten the quality gate (or wire one up) so new-code coverage and new-blocker thresholds actually fail the check.
4. Verify the check fires AND can fail: open a throwaway PR that intentionally trips one rule (e.g. empty PR description) and confirm Danger posts a failing comment and the merge button is blocked. Screenshot or link the run in the PR description.
5. Keep changes focused on this signal — do not refactor unrelated workflows.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** Dangerfile that contains only `message()` / `markdown()` calls and never `fail()`s. A check that cannot fail is decoration. At minimum one rule must call `fail(...)` under a realistic condition.
- **NO** Dangerfile rules with conditions that are always false (`if (false)`, `if (danger.github.pr.title === "NEVER_MATCH")`). Reviewers see a green check and assume coverage exists.
- **NO** CODEOWNERS pointing to non-existent users, archived teams, or `@org/everyone`-style catch-alls that route to nobody actionable. Run `gh api users/<handle>` for every `@user` and `gh api orgs/<org>/teams/<team>` for every `@org/team` entry before committing.
- **NO** CODEOWNERS file without the matching branch-protection toggle. Without `require_code_owner_reviews: true` on the protected branch, GitHub treats CODEOWNERS as suggestions and any reviewer can satisfy the requirement.
- **NO** branch protection where the Danger / Sonar / review-bot job is listed as a context but `strict: false` and `enforce_admins: false` — admins (and any agent acting with an admin token) can merge around the gate. Set `enforce_admins: true` unless there is a documented break-glass.
- **NO** Sonar quality gate left at the default "Sonar way" with `new_coverage > 0%` — that passes any PR that adds a single covered line. Replace with project-realistic thresholds (e.g. `new_coverage >= 70`, `new_blocker_violations = 0`, `new_security_hotspots_reviewed >= 100`).
- **NO** review-bot config (Mergify, PullApprove) with `required: false` on every group, or rules that auto-approve PRs from a `bot` author — that re-enables the gap the signal is supposed to close.
- **NO** running Danger / Sonar in `continue-on-error: true` mode in the workflow. The check posts a comment but the job stays green, so branch protection never blocks.
- **NO** putting the policy in prose ("reviewers should check for missing tests") instead of a machine-enforced rule.

Examples of BAD fixes:
- `dangerfile.js` containing only `markdown("Thanks for the PR!")` — never asserts, never fails, signal stays broken.
- A `.github/CODEOWNERS` with `* @octocat` where `@octocat` is the placeholder user from a tutorial. PRs request a review from a non-team member; nobody is notified.
- Wiring SonarCloud but leaving the gate at "Sonar way" defaults — the gate passes a PR that adds 500 lines of uncovered code as long as the one new test covers itself.
- Mergify rule `actions: { merge: { method: squash } }` triggered by `label=automerge` with no review requirement — agents can label their own PRs and merge.
- A GitHub Action that runs `npx danger ci || true` — Danger comments fail, check stays green.
- Branch protection with `required_pull_request_reviews.required_approving_review_count: 0` and `require_code_owner_reviews: true` — code owners are requested but zero approvals are required, so the PR can merge with the CODEOWNERS request still open.

Examples of GOOD fixes:
- A `dangerfile.js` like:
  ```js
  // dangerfile.js
  const { danger, fail, warn, message } = require("danger");

  const pr = danger.github.pr;
  const modified = danger.git.modified_files;
  const created = danger.git.created_files;
  const all = modified.concat(created);

  // 1. PR description present and substantive
  if (!pr.body || pr.body.trim().length < 40) {
    fail("PR description is missing or under 40 chars. Explain the why, not just the what.");
  }

  // 2. Source changes must include tests (or explicit opt-out via "skip-tests" label)
  const sourceTouched = all.some(f => f.startsWith("src/") && !f.endsWith(".d.ts"));
  const testsTouched  = all.some(f => /(\.test\.|\.spec\.|__tests__\/)/.test(f));
  const skipTests     = pr.labels.some(l => l.name === "skip-tests");
  if (sourceTouched && !testsTouched && !skipTests) {
    fail("Source files changed under `src/` but no test files were modified. Add a test or apply the `skip-tests` label with justification.");
  }

  // 3. Lockfile drift without package.json change
  const lockTouched = all.includes("package-lock.json") || all.includes("pnpm-lock.yaml");
  const pkgTouched  = all.includes("package.json");
  if (lockTouched && !pkgTouched) {
    fail("Lockfile changed without a corresponding `package.json` edit. Likely accidental — rerun the install on a clean tree.");
  }

  // 4. Migration safety
  const migrationAdded = created.some(f => f.startsWith("migrations/") || f.startsWith("prisma/migrations/"));
  if (migrationAdded && !pr.body.match(/rollback/i)) {
    fail("Migration added but PR description does not mention a rollback plan.");
  }

  // 5. Soft warning on big diffs
  if (pr.additions + pr.deletions > 800) {
    warn(`PR is ${pr.additions + pr.deletions} lines. Consider splitting for reviewability.`);
  }
  ```
- A `.github/workflows/danger.yml`:
  ```yaml
  name: Danger
  on: pull_request
  jobs:
    danger:
      runs-on: ubuntu-latest
      permissions:
        pull-requests: write
        contents: read
      steps:
        - uses: actions/checkout@v4
          with: { fetch-depth: 0 }
        - uses: actions/setup-node@v4
          with: { node-version: 20 }
        - run: npm ci
        - name: Danger
          run: npx danger ci --failOnErrors
          env:
            DANGER_GITHUB_API_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```
  (`--failOnErrors` makes the job exit non-zero so branch protection can require it.)
- A `.github/CODEOWNERS`:
  ```
  # Default owners for everything
  *                       @acme/platform-leads

  # Frontend
  /apps/web/              @acme/web-team
  /packages/ui/           @acme/web-team @sara-frontend

  # Backend services
  /services/api/          @acme/backend-team
  /services/billing/      @acme/billing-team @acme/security-reviewers

  # Infra & deploy — require infra review
  /.github/workflows/     @acme/devex
  /terraform/             @acme/infra @acme/security-reviewers
  /Dockerfile             @acme/infra

  # Schema changes need DBA sign-off
  /prisma/schema.prisma   @acme/backend-team @acme/dba
  /migrations/            @acme/backend-team @acme/dba
  ```
- Branch protection `protection.json` applied via `gh api -X PUT repos/<owner>/<repo>/branches/main/protection --input protection.json`:
  ```json
  {
    "required_status_checks": {
      "strict": true,
      "contexts": ["Danger", "build", "test"]
    },
    "enforce_admins": true,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "require_code_owner_reviews": true,
      "dismiss_stale_reviews": true,
      "require_last_push_approval": true
    },
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false
  }
  ```
- For a Sonar-using repo, a `sonar-project.properties` with a custom gate referenced and `.github/workflows/sonarcloud.yml` running on `pull_request`, with the SonarCloud GitHub app installed so the gate check appears on the PR rollup and can block merge.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, which rules now block merge, and which existing PR (if any) you used to confirm the check fires

## References

- Danger.js docs & rule cookbook: https://danger.systems/js/
- Danger CI integration (`danger ci`, `--failOnErrors`): https://danger.systems/js/usage/culture.html
- GitHub CODEOWNERS syntax & resolution rules: https://docs.github.com/en/repositories/managing-your-repositories-settings-and-features/customizing-your-repository/about-code-owners
- GitHub branch protection API (`require_code_owner_reviews`, `enforce_admins`): https://docs.github.com/en/rest/branches/branch-protection
- SonarCloud quality gates & PR decoration: https://docs.sonarsource.com/sonarcloud/improving/quality-gates/
- SonarCloud GitHub integration (PR comment + check): https://docs.sonarsource.com/sonarcloud/getting-started/github/
- Mergify queue & merge protections: https://docs.mergify.com/configuration/file-format/
- PullApprove group rules: https://docs.pullapprove.com/config/groups/
- Reviewdog (line-level annotations from linters): https://github.com/reviewdog/reviewdog
</system-reminder>
