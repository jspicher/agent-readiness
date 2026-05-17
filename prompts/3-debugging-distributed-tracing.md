[Readiness Fix] <REPO_NAME> Distributed Tracing

Fix the failing signal: Distributed Tracing ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Distributed Tracing
**Score**: [0/1]
**Description**: Application implements request tracing
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Check for distributed tracing instrumentation that allows following a request through multiple services. Acceptable evidence (in descending order of strength): 1) **W3C Trace Context** propagation (`traceparent` and `tracestate` headers) via OpenTelemetry SDK, with spans exported to a backend (Jaeger, Tempo, Honeycomb, Datadog APM, X-Ray); 2) vendor-specific distributed tracing (Datadog APM tags, New Relic distributed tracing); 3) cross-service trace ID propagation via custom headers if there is a documented span backend that joins them. NOTE: `X-Request-ID` headers alone are **single-service log correlation**, NOT distributed tracing — they propagate a request id but do not produce a span tree. A repo with only `X-Request-ID` middleware does NOT satisfy this signal.

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
