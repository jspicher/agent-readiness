[Readiness Fix] <REPO_NAME> Contributor Agreement

Fix the failing signal: Contributor Agreement ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Contributor Agreement
**Score**: [0/1]
**Description**: Repository enforces a DCO sign-off or CLA process so every contribution carries a verifiable IP / licensing assertion before merge
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Contributor agreement enforced – PASS requires a checked-in, automated check that blocks merge until every commit (or the PR author) has asserted the project's contribution terms. Accept any ONE of the following, but the check MUST be wired into branch protection / required status checks, not just installed:

1. **DCO sign-off** — every commit on the PR carries a `Signed-off-by: Name <email>` trailer matching the commit author, enforced by ONE of:
   - The DCO GitHub App (`https://github.com/apps/dco`, repo `dcoapp/app`) installed on the repo, with the `DCO` status check listed under required checks in branch protection / ruleset.
   - A GitHub Actions workflow that runs a DCO checker on `pull_request` (e.g. `tim-actions/dco@*`, `christophebedard/dco-check@*`, or the Probot DCO action) and is listed as a required status check.
   - GitLab's native `Require all commits to be signed off` project setting (Settings → Repository → Push rules).
   A `CONTRIBUTING.md` paragraph that *asks* contributors to sign off is documentation, not enforcement, and FAILs.
2. **CLA bot** — `cla-assistant.io` (`contributor-assistant/github-action`), CLA Bot (SAP `cla-assistant` self-hosted), or Linux Foundation EasyCLA (`communitybridge/easycla`) is configured against a checked-in CLA document, AND its status check (`license/cla`, `EasyCLA`, or equivalent) is required in branch protection. Verify the CLA file the bot points to actually exists in the repo (or in the configured remote location) and distinguishes individual vs corporate signers when the project accepts both.
3. **Foundation-managed equivalent** — Apache ICLA/CCLA on file with the ASF, CNCF EasyCLA, or Eclipse ECA, with the corresponding bot status check required on PRs.

Verify the check is *blocking*: run `gh api repos/{owner}/{repo}/branches/{default}/protection` (or `repos/{owner}/{repo}/rulesets`) and confirm the DCO/CLA check appears under `required_status_checks.contexts` (or the ruleset's `required_status_checks` rule). A check that runs and reports red but does not block merge is a FAIL — agents and humans will merge around it.

Also verify recent history matches the policy: `gh pr list --state merged --limit 20 --json number,commits` and spot-check that merged commits actually carry `Signed-off-by:` (DCO) or that the corresponding PR has the CLA bot's green check (CLA). A policy adopted yesterday with 200 prior unsigned commits in `main` is fine going forward; a policy that has been "enforced" for a year but half the recent merges bypassed it is a FAIL.

## Your Task

1. Explore the repository to understand the current state:
   - `ls -la .github/` and read every workflow in `.github/workflows/*.yml` — look for existing DCO/CLA actions.
   - Check for `.github/CONTRIBUTING.md`, `CONTRIBUTING.md`, `CLA.md`, `cla/`, `.clabot`, `.cla-signatures` — note what already exists vs. what is just prose.
   - `gh api repos/{owner}/{repo}/installations 2>/dev/null` or visit `https://github.com/{owner}/{repo}/settings/installations` to see if the DCO App or a CLA app is installed but unused.
   - `gh api repos/{owner}/{repo}/branches/{default}/protection --jq '.required_status_checks.contexts'` and `gh api repos/{owner}/{repo}/rulesets` to see what is currently required.
   - `gh pr list --state merged --limit 10 --json number,headRefOid` then `gh api repos/{owner}/{repo}/commits/{sha} --jq '.commit.message'` on a few to see whether recent commits carry `Signed-off-by:` trailers.
   - Pick DCO or CLA based on what fits the project: DCO is correct for almost every open-source repo (lightweight, no signed form, used by the Linux kernel, GitLab, Chef, GitHub itself); CLA is appropriate only when the project relicenses contributions, dual-licenses, or operates under a foundation (Apache, CNCF, Eclipse) that mandates one.
2. Make **substantive improvements** by wiring real enforcement:
   - **DCO path (preferred default):**
     - Install the DCO GitHub App on the repo: `https://github.com/apps/dco` → Configure → select the repo. (Alternatively, commit a workflow — see the Working Example below.)
     - Add `DCO` to required status checks: `gh api -X PUT repos/{owner}/{repo}/branches/{default}/protection/required_status_checks/contexts --input -` with `["DCO", ...existing]`, OR add a ruleset entry.
     - Add a `CONTRIBUTING.md` section that quotes the DCO 1.1 text verbatim (`https://developercertificate.org/`) and shows the `git commit -s` workflow.
     - Commit a `.gitmessage` template and a `prepare-commit-msg` hook in `.githooks/` that auto-appends `Signed-off-by:` so contributors using `git commit` without `-s` don't trip the check.
   - **CLA path (only when justified):**
     - Commit the CLA text (`CLA.md` or `legal/individual-cla.md` + `legal/corporate-cla.md`) — don't link to an external URL the bot won't validate.
     - Add `.github/workflows/cla.yml` using `contributor-assistant/github-action@v2` pointed at a signatures file in a private repo (never store signatures in the public source repo). Configure `path-to-signatures`, `path-to-document`, `branch`, `allowlist` for bots (`dependabot[bot],renovate[bot]`), and `remote-organization-name` / `remote-repository-name` for the signatures store.
     - Add the bot's status check (`license/cla` or `EasyCLA`) to required checks.
   - Either path: add bot-author exemptions so `dependabot[bot]`, `renovate[bot]`, and Claude/Factory agent commits (when they commit under a known service account) either auto-sign or are allowlisted — the goal is verifiable provenance, not friction.
3. Verify enforcement end-to-end:
   - Open a throwaway PR with one unsigned commit. The DCO/CLA check MUST report failure and the merge button MUST be greyed out. If merge is still available, branch protection is not wired correctly — fix the `required_status_checks.contexts` array.
   - Amend the commit with `git commit --amend -s` (or sign the CLA), push, and confirm the check turns green and merge unblocks.
   - `gh api repos/{owner}/{repo}/branches/{default}/protection --jq '.required_status_checks.contexts'` shows your new check in the list.
4. Keep changes focused on this signal — do not touch unrelated CI, lint, or release config.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** adding a DCO/CLA workflow without listing it under `required_status_checks.contexts`. A non-blocking check is theater — agents and humans will merge around it. The signal explicitly tests for blocking enforcement.
- **NO** installing the DCO App but leaving "Require status checks to pass before merging" off, or leaving `DCO` out of the contexts array. The App reports a status; branch protection is what blocks merge.
- **NO** committing a `CONTRIBUTING.md` paragraph ("please sign off your commits") as the entire fix. Prose is unenforceable — the next contributor will skip it and CI will not catch it.
- **NO** configuring `cla-assistant` to allow PR authors to self-sign in a comment without recording the signature anywhere — without a signatures store the bot cannot prove anyone agreed to anything.
- **NO** committing CLA signatures to the public source repo. Signatures contain real names + emails of every contributor; they belong in a separate (often private) repository configured via `remote-organization-name` / `remote-repository-name`.
- **NO** picking CLA over DCO "because it's stronger" for a project that has no relicensing, dual-license, or foundation requirement. CLA introduces real friction (every new contributor must sign a form before their first PR can merge); DCO is a git trailer and adds seconds. Pick CLA only when there is a concrete legal driver.
- **NO** writing a DCO check that only inspects the PR title or the merge commit. The DCO assertion is per-commit — the check MUST iterate every commit in the PR and verify each has `Signed-off-by:` matching the commit's `author.email`.
- **NO** wildcard allowlists (`allowlist: *`) on the CLA bot. Limit exemptions to specific bot accounts you can name.
- **NO** committing a corporate CLA flow with no path for individuals (or vice versa) if both contribute. EasyCLA distinguishes ICLA vs CCLA explicitly; cla-assistant supports both via separate documents.

Examples of BAD fixes:
- Adding `.github/workflows/dco.yml` that runs `tim-actions/dco@v1.1.0` on `pull_request`, then stopping. The check runs, fails red on unsigned commits, and the merge button is still green because nothing made it required.
- A `CONTRIBUTING.md` that says "All contributors must sign the DCO" with no bot, no workflow, no required check.
- `cla-assistant` workflow with `path-to-signatures: signatures/version1/cla.json` pointing at a file inside the public repo — exposes contributor PII and rewrites history every signing.
- A workflow that greps the PR body for the string "I agree to the CLA" — that is a checkbox, not a CLA, and provides no audit trail.
- DCO action with `allowlist: '*'` — defeats the entire purpose.

Examples of GOOD fixes:
- DCO via GitHub App + required status check + `CONTRIBUTING.md` quoting DCO 1.1 + `.githooks/prepare-commit-msg` that auto-signs. Verified by opening a PR without `-s` and watching the check go red.
- DCO via committed workflow (see Working Example below), added to branch protection contexts, with `dependabot[bot]` allowlisted so Dependabot PRs continue to merge.
- CLA Assistant pointed at a private signatures repo, with both individual and corporate CLA documents committed in the source repo as `legal/individual-cla.md` and `legal/corporate-cla.md`, status check `license/cla` listed under required contexts.

## Working Example: DCO via GitHub Actions + branch protection

`.github/workflows/dco.yml`:
```yaml
name: DCO
on:
  pull_request:
    types: [opened, synchronize, reopened]
permissions:
  contents: read
  pull-requests: read
jobs:
  dco:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          ref: ${{ github.event.pull_request.head.sha }}
      - uses: tim-actions/get-pr-commits@v1.3.1
        id: pr_commits
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      - uses: tim-actions/dco@2fd0504dc0d27b33f542867c300c60840c6dcb20  # v1.1.0
        with:
          commits: ${{ steps.pr_commits.outputs.commits }}  # MUST be the JSON array from get-pr-commits, NOT `github.event.pull_request.commits` (that's an integer count and silently no-ops the check)
```

Wire it into branch protection (one-shot):
```bash
gh api -X PATCH repos/<OWNER>/<REPO>/branches/main/protection/required_status_checks \
  -f strict=true \
  -F 'contexts[]=DCO'
```

Or, modern ruleset (preferred):
```bash
gh api -X POST repos/<OWNER>/<REPO>/rulesets \
  -f name='Require DCO on main' \
  -f target=branch \
  -f enforcement=active \
  -f 'conditions[ref_name][include][]=~DEFAULT_BRANCH' \
  -f 'rules[][type]=required_status_checks' \
  -F 'rules[0][parameters][required_status_checks][][context]=DCO'
```

Auto-sign hook (`.githooks/prepare-commit-msg`):
```bash
#!/usr/bin/env bash
# Auto-append Signed-off-by: trailer if missing.
COMMIT_MSG_FILE=$1
NAME=$(git config user.name)
EMAIL=$(git config user.email)
TRAILER="Signed-off-by: ${NAME} <${EMAIL}>"
grep -qF "$TRAILER" "$COMMIT_MSG_FILE" || \
  printf '\n%s\n' "$TRAILER" >> "$COMMIT_MSG_FILE"
```

Activate the hook directory in-repo:
```bash
git config --local core.hooksPath .githooks
chmod +x .githooks/prepare-commit-msg
```

`CONTRIBUTING.md` snippet:
```markdown
## Developer Certificate of Origin

Every commit must carry a `Signed-off-by:` trailer asserting the
[Developer Certificate of Origin v1.1](https://developercertificate.org/).

Sign off automatically with `git commit -s` (or enable the repo hook:
`git config --local core.hooksPath .githooks`). The DCO check on PRs
will reject any commit missing the trailer.
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, which path (DCO or CLA) you chose and why, and confirm the check appears under `required_status_checks.contexts`

## References

- Developer Certificate of Origin v1.1 (canonical text): https://developercertificate.org/
- DCO GitHub App (repo `dcoapp/app`): https://github.com/apps/dco
- `tim-actions/dco` GitHub Action: https://github.com/tim-actions/dco
- `christophebedard/dco-check` (per-commit Python checker): https://github.com/christophebedard/dco-check
- CLA Assistant (`contributor-assistant/github-action`): https://github.com/contributor-assistant/github-action
- CLA Assistant Lite (SAP, self-hosted): https://github.com/cla-assistant/cla-assistant
- Linux Foundation EasyCLA: https://docs.linuxfoundation.org/lfx/easycla
- Apache ICLA / CCLA: https://www.apache.org/licenses/contributor-agreements.html
- Eclipse Contributor Agreement: https://www.eclipse.org/legal/ECA.php
- GitHub branch protection required status checks API: https://docs.github.com/en/rest/branches/branch-protection#update-status-check-protection
- GitHub Rulesets (modern replacement for legacy branch protection): https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets
- Linux kernel DCO process (origin of the practice): https://www.kernel.org/doc/html/latest/process/submitting-patches.html#sign-your-work-the-developer-s-certificate-of-origin
</system-reminder>
