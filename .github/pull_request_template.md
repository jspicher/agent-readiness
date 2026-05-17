> **No AI attribution.** Do not add "Co-Authored-By", "Generated with Claude",
> or similar lines in the PR body or commit messages. Write as if you authored
> the change yourself.
>
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
- **Scanner / criteria / renderer**: signal changes

<!-- Delete this block if not applicable -->
### Criteria / Pillar Changes

- **New criterion**: pillar, level, evidence pattern, why it matters
- **Tightened criterion**: criterion #, what changed, why ambiguous-pass closed

## Context / Motivation

<!--
What problem is this PR solving? Link related issues, design docs, prior
readiness reports, or external feedback that motivated the change. If this is
part of a multi-PR effort, note the sequence number and the overall plan.
-->

- Closes #
- Related:

## Testing

<!--
List the local quality gates you ran and any feature-specific verification.
This repo has no build/lint/test tooling; verification is hand-run.
-->

- [ ] `bash scripts/scan_<changed>.sh .` runs without shell errors against this repo
- [ ] Rendered HTML opens cleanly (`bash scripts/render_html.sh <data.json> <out.html>`) if the renderer or schema changed
- [ ] `references/criteria.md` row count matches the SKILL.md pillar table totals if criteria were added/removed
- [ ] Feature-specific verification (commands + observed output below)

```
<!-- paste relevant command output here -->
```

## Breaking Changes

<!--
List any breaking changes for downstream consumers (people who have already
installed this skill or depend on the JSON data schema). Delete this section
if the PR has none.

Common breakages:
  - Renamed criterion IDs (anyone tracking by ID will need to remap)
  - JSON schema field renames in audit-data-schema.md
  - Renderer changes that invalidate prior HTML reports
-->

-

## Risk / Rollback

<!--
Honest assessment of blast radius:
  - What could regress if this PR is wrong?
  - Does this change a scoring formula or applicability gate? (those affect
    every future audit)
  - How do we revert? (Usually: `git revert <merge-commit>`. Note any data
    schema changes that affect previously generated audits.)
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
- [ ] If criteria were added or modified, `references/audit-data-schema.md` and `assets/report-template.html` were checked for downstream impact.
