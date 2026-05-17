# Prompt graveyard

This directory holds remediation prompts that were authored against an earlier
taxonomy but no longer map to any row in `references/criteria.md`. They live
here -- not deleted -- because the concepts may resurface as new criteria in
a later revision, and resurrecting the prose is cheaper than rewriting it.

**The validator excludes this directory from `[V11]` drift checks.**
`scripts/validate_audit_data.py check_v11_prompt_drift()` enumerates only
top-level `prompts/*.md`. Anything under `prompts/_graveyard/` is invisible to
the drift check and to `references/prompt-map.json`.

**To restore a prompt:** `git mv prompts/_graveyard/<file>.md prompts/<file>.md`
and add a `HAS_PROMPT` entry in `references/prompt-map.json` pointing at the
new path. Then re-run `python3 scripts/validate_audit_data.py
fixtures/test-data-minimal-v2.json` to confirm no drift.

## Contents

| Filename | Original heading line | Date moved | Reason |
|---|---|---|---|
| `2-build-vcs-cli-tools.md` | `[Readiness Fix] <REPO_NAME> VCS CLI Tools` | 2026-05-17 | Legacy taxonomy carry-over; no matching row in `references/criteria.md`. Preserved here in case a future criterion adopts the concept; restore via `git mv ../<file>.md ../`. |
| `3-build-agentic-development.md` | `[Readiness Fix] <REPO_NAME> Agentic Development` | 2026-05-17 | Legacy taxonomy carry-over; no matching row in `references/criteria.md`. Preserved here in case a future criterion adopts the concept; restore via `git mv ../<file>.md ../`. |
| `3-product-product-analytics-instrumentation.md` | `[Readiness Fix] <REPO_NAME> Product Analytics Instrumentation` | 2026-05-17 | Legacy taxonomy carry-over; no matching row in `references/criteria.md`. Preserved here in case a future criterion adopts the concept; restore via `git mv ../<file>.md ../`. |
| `3-style-naming-consistency.md` | `[Readiness Fix] <REPO_NAME> Naming Consistency` | 2026-05-17 | Legacy taxonomy carry-over; no matching row in `references/criteria.md`. Preserved here in case a future criterion adopts the concept; restore via `git mv ../<file>.md ../`. |
| `4-debugging-deployment-observability.md` | `[Readiness Fix] <REPO_NAME> Deployment Observability` | 2026-05-17 | Legacy taxonomy carry-over; no matching row in `references/criteria.md`. Preserved here in case a future criterion adopts the concept; restore via `git mv ../<file>.md ../`. |
| `4-taskdiscovery-backlog-health.md` | `[Readiness Fix] <REPO_NAME> Backlog Health` | 2026-05-17 | Legacy taxonomy carry-over; no matching row in `references/criteria.md`. Preserved here in case a future criterion adopts the concept; restore via `git mv ../<file>.md ../`. |
