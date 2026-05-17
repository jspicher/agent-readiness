[Readiness Fix] <REPO_NAME> Error Tracking Contextualized

Fix the failing signal: Error Tracking Contextualized ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Error Tracking Contextualized
**Score**: [0/1]
**Description**: Sentry/Bugsnag with source maps and breadcrumbs
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Error tracking contextualized – Sentry, Bugsnag, or Rollbar is configured with source maps, breadcrumbs, and user context. Agents can trace production errors back to specific code paths with full stack traces.

**PII guardrails (REQUIRED).** Adding "user context" to an error tracker is a privacy decision, not just an observability one. Any PASS evidence for user context MUST be accompanied by PII safeguards: (a) `sendDefaultPii: false` (Sentry default since SDK 8.x; verify it's not flipped to `true`) or equivalent in Bugsnag/Rollbar; (b) explicit `setUser({ id })` with a stable internal user id ONLY — no email, name, phone, IP unless the data-protection notice covers it; (c) a `beforeSend` / `beforeBreadcrumb` scrubber that strips obvious PII patterns (emails, JWTs, auth headers, credit-card numbers) from the event payload before transmission; (d) attached source-map upload happens at build time via the vendor's wizard/CLI, not by committing source maps to the public bundle.

## Your Task

1. Explore the repository to understand the current state related to this signal
2. Make **substantive improvements** to the codebase that genuinely address the signal
3. Verify your fix addresses the issue (e.g., run linter if fixing lint_config, run tests if adding tests)
4. Keep changes focused on this signal - don't refactor unrelated code
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** empty placeholder files (e.g., empty test files, stub configs)
- **NO** minimal implementations that technically pass but provide no real value
- **NO** disabling checks or adding skip markers to pass validation
- **NO** trivial changes that game the metric without improving quality

Examples of BAD fixes:
- Adding an empty `test.js` file to satisfy "has tests" criterion
- Creating a `.eslintrc` that disables all rules
- Adding `// @ts-nocheck` to satisfy TypeScript requirements

Examples of GOOD fixes:
- Writing actual unit tests with meaningful assertions for existing code
- Configuring ESLint with appropriate rules for the project's language/framework
- Adding proper TypeScript types to improve type safety

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase
</system-reminder>
