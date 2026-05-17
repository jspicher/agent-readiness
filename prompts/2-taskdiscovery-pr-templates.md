[Readiness Fix] <REPO_NAME> PR Templates

Fix the failing signal: PR Templates ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: PR Templates
**Score**: [0/1]
**Description**: Pull request templates exist with structured sections that guide agent + human contributors toward reviewable, recoverable changes.
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

PR templates -- `.github/pull_request_template.md` (GitHub) or merge request templates (GitLab) exist with sections for description, testing done, breaking changes, risk/rollback, and relevant context. Ensures agent PRs include the information reviewers need AND the rollback information operators need.

## Your Task

1. Read the project's existing conventions: README, AGENTS.md, CONTRIBUTING.md, any prior PR descriptions. Identify the project's lint/typecheck/test/build commands (`package.json` scripts, `Makefile`, `Justfile`, `pyproject.toml`, `Cargo.toml`, etc.).
2. Create `.github/pull_request_template.md` (or the GitLab equivalent) using the **recommended template below** as a starting point. Adapt the testing checklist commands to match the project's actual pre-push gate. Keep the structure; tune the content.
3. Verify by opening a draft PR with the new template and confirming the sections render correctly in GitHub's PR composer.
4. Keep changes focused on this signal -- don't refactor unrelated code.
5. When done, open a PULL REQUEST with the changes and return the PR URL.

## Recommended Template

Start from this structure. The blockquote preamble + section headings are universal. The `<!-- Delete if not applicable -->` sub-blocks under Details let contributors trim noise. The Testing checklist commands MUST be replaced with the project's actual pre-push gate commands -- do not leave the example placeholders.

````markdown
> Fill in every required section below. Empty required sections will delay
> review. The "Risk / Rollback" section is required even for trivial PRs.

## Summary

<!-- One paragraph: what this PR does and why a reviewer should care. -->

## Details

<!--
Optional typed breakdown. Delete any sub-block that doesn't apply to this PR.
Skip the whole section if the Summary already covers everything.
-->

<!-- Delete this block if not applicable -->
### New Features

- **Feature name**: what was added and where to look

<!-- Delete this block if not applicable -->
### Bug Fixes

- Fixed issue where ...
- Resolved problem with ...

<!-- Delete this block if not applicable -->
### Technical Improvements

- **Refactor / architecture**: structural changes
- **Type safety / lint**: improvements

<!-- Delete this block if not applicable -->
### UI / UX Changes

- **Visual**: what changed on screen
- **Responsive / a11y**: mobile, keyboard, screen reader notes

## Context / Motivation

<!--
What problem is this PR solving? Link related issues, design docs, readiness
reports, ADRs, or prior PRs. If this is part of a multi-PR effort, note the
sequence number and the overall plan.
-->

- Closes #
- Related:

## Testing

<!--
List the local quality gates you ran and any feature-specific verification.
Replace the commands below with your project's actual pre-push gate.
-->

- [ ] `<lint command>` -- e.g. `npm run lint`, `ruff check`, `cargo clippy`
- [ ] `<typecheck command>` -- e.g. `npx tsc --noEmit`, `mypy .`, `go vet ./...`
- [ ] `<test command>` -- e.g. `npm run test:ci`, `pytest -q`, `cargo test`
- [ ] `<build command>` -- e.g. `npm run build`, `cargo build --release`
- [ ] Feature-specific verification (commands + observed output below)

```
<!-- paste relevant command output here -->
```

## Breaking Changes

<!--
List any breaking changes and the migration path for downstream consumers.
Delete this section if the PR has none.
-->

-

## Risk / Rollback

<!--
Honest assessment of blast radius:
  - What could regress if this PR is wrong?
  - Is the change behind a flag, isolated to a route, or wide-ranging?
  - How do we revert? (Usually: `git revert <merge-commit>`. Note any data
    migrations or external-system effects that revert won't undo.)
-->

**Risk level:** low / medium / high

**Rollback plan:**

## Additional Notes

<!--
Anything reviewers should know that doesn't fit above: design decisions,
known follow-ups, deferred scope.
-->

## Checklist

- [ ] Conventional-commit style used in commits (`feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `perf`, `ci`).
- [ ] No secrets committed (`.env*`, `*.pem`, tokens).
- [ ] Scope is limited to the stated motivation; out-of-scope changes filed as follow-up issues.
````

### Adaptation guidance

- **Single-language / single-stack repos**: replace the four `<...command>` placeholders with the actual commands. Delete the `e.g.` examples after substituting.
- **Monorepo with multiple stacks**: keep the placeholders generic OR list the commands per workspace (`- [ ] frontend: \`pnpm --filter web lint\``).
- **Repos with no UI**: delete the `UI / UX Changes` sub-block from the template; agents and contributors won't have an empty section staring at them.
- **Repos with strict commit message linting**: extend the Checklist to call out the lint command (`commitlint`, `gitlint`, etc.).
- **Repos with bespoke project-wide pre-merge gates** (e.g., `validate-agents-md`, `check-migrations`, RFC link required): add those as additional checklist items in the Testing or Checklist sections.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** empty placeholder files (e.g., a `pull_request_template.md` with only `# Summary` and nothing else)
- **NO** minimal implementations that technically pass but provide no real value (e.g., copying the template verbatim without substituting the project's actual lint/test/build commands)
- **NO** disabling checks or adding skip markers to pass validation
- **NO** trivial changes that game the metric without improving quality

Examples of BAD fixes:
- Committing the recommended template verbatim with `<lint command>` / `<test command>` placeholders unsubstituted
- Adding a one-line `## Summary` template that omits Risk/Rollback and Testing
- Creating both `.github/pull_request_template.md` AND `.github/PULL_REQUEST_TEMPLATE.md` (case-sensitive duplicates that confuse GitHub)
- Adding a "No AI attribution" or "No Co-Authored-By" line unless that genuinely matches the team's stated convention -- don't impose authorship norms a maintainer hasn't endorsed

Examples of GOOD fixes:
- Adapting the recommended template with the project's real commands substituted (e.g., `[ ] \`npx tsc --noEmit\`` instead of `[ ] <typecheck command>`)
- Trimming sub-blocks that don't apply to the project (e.g., delete `UI / UX Changes` for a backend-only repo)
- Adding project-specific checklist items (validate-agents-md, RFC link, etc.) that reflect actual conventions in CONTRIBUTING.md or AGENTS.md
- Opening a draft PR using the new template to verify it renders correctly before merging

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- The PR should ITSELF use the new template (eat your own dog food -- demonstrates the template works end-to-end)
- Provide a succinct summary of what you changed and why it genuinely improves the codebase
</system-reminder>
