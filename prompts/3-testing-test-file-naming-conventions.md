[Readiness Fix] <REPO_NAME> Test File Naming Conventions

Fix the failing signal: Test File Naming Conventions ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Test File Naming Conventions
**Score**: [0/1]
**Description**: Consistent test file naming enforcement
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Test naming conventions – Check for consistent test file naming enforcement in any language. PASS if ANY ONE of the following exists: 1) JS/TS: Jest testMatch/testRegex, Vitest include patterns, or Mocha test directory config. 2) Python: pytest naming conventions in pytest.ini or pyproject.toml (test_*.py pattern). 3) Go: *_test.go convention (built-in, check tests exist following pattern). 4) Java: Maven/Gradle test source directories with naming patterns. 5) Any test framework configured with explicit naming patterns. 6) Test naming conventions documented in AGENTS.md or CONTRIBUTING.md.

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
