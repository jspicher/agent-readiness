[Readiness Fix] <REPO_NAME> End-to-End Tests

Fix the failing signal: End-to-End Tests ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: End-to-End Tests
**Score**: [0/1]
**Description**: Full system/browser tests that drive the application the way a user does — HTTP in, rendered HTML / network responses out — with the real frontend, real backend, and real (or containerized) data stores.
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

End-to-end tests present — a checked-in E2E suite that drives the application through its real entry points (browser, CLI, public API). PASS requires ALL of:

1. **A real E2E runner is configured**, not just installed. Look for one of:
   - `playwright.config.ts` / `playwright.config.js` (Playwright 1.x — current line is 1.5x as of 2026) with `testDir` pointing at an `e2e/`, `tests/e2e/`, or `playwright/` directory, and `projects` enumerating at least one real browser (`chromium`, `firefox`, `webkit`).
   - `cypress.config.ts` / `cypress.config.js` (Cypress 14+) with `e2e.specPattern` resolving to actual spec files under `cypress/e2e/`.
   - WebdriverIO `wdio.conf.ts` with `specs` populated and a `services` list including a browser driver.
   - Selenium 4 suite under `tests/e2e/` or `e2e/` with a runner config (`pytest.ini` marker, `testng.xml`, etc.) that actually targets those files.
   - For non-browser apps: a black-box suite (e.g. `tests/e2e/` driving the CLI via subprocess, or hitting a deployed HTTP surface via `supertest`/`httpx`) — must boot the real app, not import internals.
2. **The directory has more than one real test.** A single `example.spec.ts` shipped by `npx playwright init` and never replaced does NOT count. There must be at least 2 spec files exercising actual product flows (login, checkout, primary CRUD, etc.) with assertions on rendered UI or HTTP responses.
3. **Tests are wired into CI**, not just runnable locally. There must be a workflow file (`.github/workflows/*.yml`, `.gitlab-ci.yml`, `.circleci/config.yml`, etc.) that invokes the runner on PR or push. A `package.json` script alone is not enough.
4. **Tests are distinct from integration tests (Feature #27).** Integration tests exercise service-to-service boundaries (API ↔ DB, service ↔ service) with internals still importable. E2E tests boot the deployed surface (real browser against real `next start` / `vite preview` / `docker compose up`, or HTTP client against the deployed URL) and never reach into the app's internals. If `tests/integration/` and `tests/e2e/` are the same files renamed, this signal FAILs.

Verify the suite is real: run the collector flag (`npx playwright test --list`, `npx cypress run --spec '**/*.cy.ts' --reporter min --no-runner-ui` then Ctrl-C after listing, or `pytest --collect-only tests/e2e/`) and confirm the framework finds the specs without import errors. Do NOT execute the full run — E2E suites can take 20+ minutes.

## Your Task

1. Explore the repository to understand the current state related to this signal — list every `playwright.config.*`, `cypress.config.*`, `wdio.conf.*`, `e2e/`, `tests/e2e/`, `cypress/`, `playwright/`, and CI workflow file. Identify the app's primary entry point (Next.js server, Vite dev server, FastAPI/Express HTTP API, CLI binary).
2. Make **substantive improvements** by adding a real E2E suite:
   - Pick the runner that matches the stack. Playwright is the 2026 default for browser apps (multi-browser support, built-in sharding, trace viewer); Cypress is acceptable for repos already using it; WebdriverIO/Selenium only if there is a pre-existing reason. For HTTP-only services without a UI, drive the deployed surface via `supertest` (Node) or `httpx` (Python).
   - Create the config at the repo root (`playwright.config.ts` etc.) with `testDir: './e2e'`, `fullyParallel: true`, `retries: process.env.CI ? 2 : 0`, `reporter: [['html'], ['blob']]` (blob is required for sharded CI merges), and `use: { trace: 'on-first-retry', screenshot: 'only-on-failure', video: 'retain-on-failure' }`.
   - Add a `webServer` block (Playwright) or `baseUrl` (Cypress) that boots the real app — `npm run build && npm run start`, NOT `npm run dev` (dev mode hides production-only bugs).
   - Write at least 3 specs covering: (a) the primary user happy path (landing → core action → success state), (b) an auth or session-bound flow if the app has accounts, (c) a destructive or stateful operation that must round-trip through the backend.
   - Add a `package.json` script: `"e2e": "playwright test"` (or equivalent).
   - Wire into CI with sharding: a matrix job that runs `--shard=${{ matrix.shard }}/${{ matrix.total }}` across at least 2 shards, uploads the `blob-report/` artifact per shard, then a final merge job that downloads all blob reports and runs `npx playwright merge-reports --reporter html ./all-blob-reports`.
3. Verify runnability: `npx playwright test --list` (or `cypress run --spec ... --reporter min` and abort after collection, or `pytest --collect-only tests/e2e/`) MUST exit zero and enumerate the new specs. Do NOT run the full suite to verify — collection is enough.
4. Keep changes focused on this signal — do not add unit/integration tests in the same PR, do not refactor product code.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** shipping the default `example.spec.ts` from `npx playwright init` or the bundled `cypress/e2e/spec.cy.js` — these are scaffolding, not tests. Delete them and write real specs against this repo's product.
- **NO** single-test "smoke" suite (`expect(page).toHaveTitle(/.+/)`) and calling it done — title assertion is not an E2E test, it is a liveness probe. The suite must exercise at least one full user flow with multi-step interaction and a backend round-trip.
- **NO** tests that only run locally because they require manual `npm run dev` first. The Playwright `webServer` block (or Cypress `baseUrl` + `start-server-and-test`) MUST boot the app inside CI.
- **NO** committing the runner config without wiring it into a CI workflow. A `playwright.config.ts` that no CI job invokes is dead infrastructure.
- **NO** `test.skip()` / `test.fixme()` on every spec to make a red suite "pass" — the suite must be green at merge time. If a flow is genuinely broken, fix the flow or omit the spec.
- **NO** disabling retries AND not capturing trace/video on failure — when a CI run fails six weeks from now, the agent debugging it needs the trace file. `trace: 'on-first-retry'` + `retries: 2` in CI is the minimum.
- **NO** importing app internals (`import { db } from '@/lib/db'`, `import { createUser } from '../src/services/users'`) inside E2E specs. If the spec reaches into the app, it is an integration test (Feature #27), not E2E. Drive the app through its real entry point only.
- **NO** running E2E against `npm run dev` in CI — dev-mode bundles, HMR injection, and lazy compilation hide bugs that ship to prod. Always boot the production build (`next start`, `vite preview`, `docker compose up`).
- **NO** hardcoded sleeps (`await page.waitForTimeout(3000)`) to "fix" flakes. Use Playwright's auto-waiting locators (`expect(locator).toBeVisible()`) or Cypress's retry-ability. A flaky test must be quarantined (`test.fixme`) with a tracking issue, not papered over with sleeps.
- **NO** running all tests in a single shard when the suite exceeds ~30 specs — shard from day one. Adding sharding later means rewriting CI under time pressure.

Examples of BAD fixes:
- Keeping the shipped `tests/example.spec.ts` that navigates to `playwright.dev` and asserts the title. The signal stays failed because the spec exercises Playwright's marketing site, not this repo's product.
- A `playwright.config.ts` with `testDir: './tests'` pointing at the same directory as the Jest unit tests, plus zero `.spec.ts` files actually using `@playwright/test`. The runner finds nothing.
- `e2e: "echo 'TODO write e2e tests'"` in `package.json`. Audit signal stays red.
- A CI step `- run: npx playwright test` with no browser install step before it (`- run: npx playwright install --with-deps chromium`). The job fails on first run, gets disabled, and the suite rots.
- A Cypress suite that depends on a seeded production database the developer set up by hand. CI runs have no DB, so the suite is `skipif(!process.env.LOCAL)`. Dead in CI = failed signal.
- One spec that opens `http://localhost:3000` and asserts the H1 text. Title/H1 smoke is a liveness check, not an E2E test.

Examples of GOOD fixes:
- A `playwright.config.ts` like:
  ```ts
  import { defineConfig, devices } from '@playwright/test';

  export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 4 : undefined,
    reporter: process.env.CI
      ? [['blob'], ['github']]
      : [['html', { open: 'never' }], ['list']],
    use: {
      baseURL: process.env.E2E_BASE_URL ?? 'http://127.0.0.1:3000',
      trace: 'on-first-retry',
      screenshot: 'only-on-failure',
      video: 'retain-on-failure',
    },
    projects: [
      { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
      { name: 'firefox',  use: { ...devices['Desktop Firefox'] } },
    ],
    webServer: {
      command: 'npm run build && npm run start',
      url: 'http://127.0.0.1:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 180_000,
    },
  });
  ```
- A `.github/workflows/e2e.yml` like:
  ```yaml
  name: e2e
  on:
    pull_request:
    push:
      branches: [main]
  jobs:
    test:
      timeout-minutes: 30
      runs-on: ubuntu-latest
      strategy:
        fail-fast: false
        matrix:
          shard: [1, 2, 3, 4]
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with: { node-version: '20', cache: 'npm' }
        - run: npm ci
        - run: npx playwright install --with-deps chromium firefox
        - run: npx playwright test --shard=${{ matrix.shard }}/4
          env:
            E2E_BASE_URL: http://127.0.0.1:3000
        - uses: actions/upload-artifact@v4
          if: always()
          with:
            name: blob-report-${{ matrix.shard }}
            path: blob-report
            retention-days: 14
    merge-reports:
      if: always()
      needs: [test]
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with: { node-version: '20', cache: 'npm' }
        - run: npm ci
        - uses: actions/download-artifact@v4
          with:
            path: all-blob-reports
            pattern: blob-report-*
            merge-multiple: true
        - run: npx playwright merge-reports --reporter html ./all-blob-reports
        - uses: actions/upload-artifact@v4
          with:
            name: html-report
            path: playwright-report
            retention-days: 14
  ```
- An `e2e/checkout.spec.ts` that signs in a seeded test user, adds an item to cart, completes checkout against a Stripe test key, and asserts the order confirmation page renders the correct order ID pulled from the response — exercising the real frontend, the real Next.js API route, and the real DB write.
- A `start-server-and-test` invocation for Cypress: `"e2e": "start-server-and-test 'npm run start' http://localhost:3000 'cypress run'"` so CI boots the app and runs the suite in one command, with the server torn down on exit.
- A flaky spec quarantined with `test.fixme(...)` and an inline link to a tracking issue (`// quarantined: FLAKY-123`), not deleted and not retried infinitely.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Playwright config & test runner: https://playwright.dev/docs/test-configuration
- Playwright sharding (`--shard`, `merge-reports`, blob reporter): https://playwright.dev/docs/test-sharding
- Playwright CI guide (GitHub Actions, GitLab, CircleCI): https://playwright.dev/docs/ci
- Playwright trace viewer & failure artifacts: https://playwright.dev/docs/trace-viewer
- Playwright `webServer` option (boot app under test): https://playwright.dev/docs/test-webserver
- Cypress 14 configuration reference: https://docs.cypress.io/app/references/configuration
- Cypress test retries (and the case against masking flakes): https://docs.cypress.io/app/guides/test-retries
- `start-server-and-test` (boot + test + teardown for Cypress in CI): https://github.com/bahmutov/start-server-and-test
- WebdriverIO config reference: https://webdriver.io/docs/configurationfile
- Selenium 4 Python pytest integration: https://www.selenium.dev/documentation/webdriver/getting_started/using_selenium/
- Cypress vs Playwright 2026 comparison (lean teams): https://getautonoma.com/blog/playwright-vs-cypress
- E2E flake taxonomy & quarantine patterns: https://playwright.dev/docs/test-retries#flaky-tests
</system-reminder>
