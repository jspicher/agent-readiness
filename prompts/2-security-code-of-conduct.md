[Readiness Fix] <REPO_NAME> Code of Conduct

Fix the failing signal: Code of Conduct ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Code of Conduct
**Score**: [0/1]
**Description**: Community standards document published in the repo with an enforceable reporting path
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Code of conduct – a checked-in `CODE_OF_CONDUCT.md` at one of GitHub's auto-detected paths (`./CODE_OF_CONDUCT.md`, `./docs/CODE_OF_CONDUCT.md`, or `./.github/CODE_OF_CONDUCT.md`) with all required sections populated AND a working reporting channel. PASS requires:

1. **File exists at a GitHub-recognized path** so it surfaces in the Community Standards checklist and in the "Code of conduct" tab on the repo home page. A `CONDUCT.md`, `CODE-OF-CONDUCT.md`, or a copy buried in `docs/policies/` is not auto-detected and FAILs.
2. **Real adopted standard, not a stub.** Use Contributor Covenant 2.1 (https://www.contributor-covenant.org/version/2/1/code_of_conduct/), Citizen Code of Conduct (https://github.com/stumpsyn/policies/blob/master/citizen_code_of_conduct.md), or Django's CoC (https://www.djangoproject.com/conduct/) verbatim with placeholders filled. A 3-paragraph "be nice" file FAILs — it provides no enforcement guidelines and no reporting workflow.
3. **Enforcement contact populated.** Contributor Covenant 2.1 ships with the literal token `[INSERT CONTACT METHOD]` inside the Enforcement section. A file shipping with that placeholder unfilled is a FAIL — it advertises a reporting path that goes nowhere. The contact MUST be a monitored mailbox, form, or alias (`conduct@<org>.com`, a Google Form, a Linear/Jira intake) that a maintainer or trust-and-safety owner actually reads.
4. **Enforcement Guidelines retained.** Contributor Covenant 2.1's "Enforcement Guidelines" section (Correction → Warning → Temporary Ban → Permanent Ban) MUST remain in the file. Deleting it strips the document of the consequence ladder that makes reports actionable.
5. **CONTRIBUTING.md cross-link** if a contributing guide exists. The contributing guide's opening paragraph should link to `CODE_OF_CONDUCT.md` so first-time contributors see the standard before they open a PR.
6. **Attribution intact.** The Attribution section at the bottom of Contributor Covenant must remain (CC BY 4.0 requires it). Stripping attribution is a license violation, not a polish improvement.

A file that exists but ships with `[INSERT CONTACT METHOD]`, `[INSERT EMAIL]`, `conduct@example.com`, or a bounced address is treated as a stub and FAILs this signal — the harness greps for those tokens.

## Your Task

1. Check the three GitHub-recognized paths (`./CODE_OF_CONDUCT.md`, `./docs/CODE_OF_CONDUCT.md`, `./.github/CODE_OF_CONDUCT.md`) and the repo's Community Standards page (`gh api repos/<owner>/<repo>/community/profile`) to confirm the signal is actually missing — not just misplaced.
2. Copy the full text of Contributor Covenant 2.1 from https://www.contributor-covenant.org/version/2/1/code_of_conduct.txt into `./CODE_OF_CONDUCT.md` (root path is the most discoverable).
3. Replace the literal `[INSERT CONTACT METHOD]` in the Enforcement section with a real, monitored contact. Order of preference:
   - A dedicated alias the project owns (`conduct@<project-domain>` or `<project>-conduct@<org>`).
   - The maintainer team's existing security/abuse alias (`security@…`) if no conduct alias exists yet — note in the PR that a dedicated alias should be created.
   - A private reporting form (Google Form, GitHub private issue, Linear intake URL) when email is not appropriate.
   - Last resort: a named maintainer's work email — never a personal Gmail, never a Slack channel link (channels rotate, emails persist).
4. Verify the contact actually resolves: send a test message and confirm a maintainer receives it. A bounced address is worse than no policy because it signals neglect.
5. If `CONTRIBUTING.md` exists, add a one-line link near the top: `Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) before contributing.` If it does not exist, skip this — do not create one in this PR.
6. Confirm the Community Standards checklist now shows Code of conduct as complete: `gh api repos/<owner>/<repo>/community/profile --jq '.files.code_of_conduct'` should return a non-null object.
7. Keep changes focused on this signal — do not refactor CONTRIBUTING.md, SECURITY.md, or issue templates in the same PR.
8. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** shipping the file with `[INSERT CONTACT METHOD]`, `[INSERT EMAIL]`, `[email@example.com]`, `conduct@example.com`, or any other placeholder. The harness greps for these tokens and the signal stays failed.
- **NO** pointing the contact at an unmonitored mailbox (`noreply@`, a forwarder nobody owns, a personal address that will lapse when the maintainer leaves).
- **NO** stripping the Enforcement Guidelines section ("Correction / Warning / Temporary Ban / Permanent Ban") to shorten the file. That ladder is the operational core of the document.
- **NO** stripping the Attribution section. Contributor Covenant is CC BY 4.0; removing attribution is a license violation.
- **NO** writing a custom 5-line "be respectful" CoC instead of adopting an established standard. Custom CoCs lack the enforcement guidelines reviewers and reporters expect, and they signal the project hasn't thought through what to do when a report arrives.
- **NO** committing a CoC with a stale year in the footer or copyright line (e.g., `Copyright 2019`). Update to the current year.
- **NO** putting the file at `./CONDUCT.md`, `./docs/policies/code-of-conduct.md`, or `./meta/CoC.md` — GitHub's Community Standards checklist will not detect it.
- **NO** linking to an external CoC ("see our website") instead of checking in the file. External pages move, change, or 404; a checked-in file is the audit trail.

Examples of BAD fixes:
- A `CODE_OF_CONDUCT.md` containing Contributor Covenant 2.1 verbatim with the Enforcement section still reading `reported to the community leaders responsible for enforcement at [INSERT CONTACT METHOD]`. The file looks complete to a skimmer; the reporting workflow is broken.
- A custom 4-paragraph CoC that says "harassment will not be tolerated, contact the maintainers" with no enforcement steps and no contact address. Unenforceable.
- `conduct@example.com` left in as the contact — GitHub's community-profile API still marks the file as present, but anyone trying to report an incident hits the bounce.
- A `CODE_OF_CONDUCT.md` placed at `./docs/community/CODE_OF_CONDUCT.md`. Not auto-detected; the Community Standards checklist stays unchecked.
- Adopting Contributor Covenant 1.4 (the pre-2020 version that lacks Enforcement Guidelines). Use 2.1.
- Deleting the Attribution paragraph because "it looks cluttered". License violation.

Examples of GOOD fixes:
- `./CODE_OF_CONDUCT.md` containing the full Contributor Covenant 2.1 text, with the Enforcement section reading:

  ```markdown
  ## Enforcement

  Instances of abusive, harassing, or otherwise unacceptable behavior may be
  reported to the community leaders responsible for enforcement at
  conduct@acme-corp.com. All complaints will be reviewed and investigated
  promptly and fairly.

  All community leaders are obligated to respect the privacy and security of
  the reporter of any incident.
  ```

  with `conduct@acme-corp.com` being a real alias that forwards to two maintainers, the Enforcement Guidelines and Attribution sections fully intact, and a corresponding line added to `CONTRIBUTING.md`:

  ```markdown
  This project follows the [Contributor Covenant](./CODE_OF_CONDUCT.md).
  By participating, you are expected to uphold this code. Report unacceptable
  behavior to conduct@acme-corp.com.
  ```

- For a project without a dedicated conduct alias, using the existing `security@acme-corp.com` mailbox with a PR note: "Used security@ as interim contact; ticket filed to provision a dedicated conduct@ alias by EOQ."

- A PR description that includes: "Verified contact: sent test report to conduct@acme-corp.com on 2026-05-16, received maintainer acknowledgement within 4 hours. `gh api repos/acme/widget/community/profile --jq '.files.code_of_conduct.url'` now returns the file URL."

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, the contact method you chose, and proof the contact resolves (test message acknowledgement)

## References

- Contributor Covenant 2.1 (canonical): https://www.contributor-covenant.org/version/2/1/code_of_conduct/
- Contributor Covenant 2.1 plain-text source: https://www.contributor-covenant.org/version/2/1/code_of_conduct.txt
- Contributor Covenant FAQ (adoption + enforcement guidance): https://www.contributor-covenant.org/faq/
- Citizen Code of Conduct: https://github.com/stumpsyn/policies/blob/master/citizen_code_of_conduct.md
- Django Code of Conduct (alternative with reporting workflow): https://www.djangoproject.com/conduct/
- GitHub: Adding a code of conduct to your project (auto-detected paths): https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-code-of-conduct-to-your-project
- GitHub Community Standards API: https://docs.github.com/en/rest/metrics/community
- Open Source Guides — Your Code of Conduct: https://opensource.guide/code-of-conduct/
</system-reminder>
