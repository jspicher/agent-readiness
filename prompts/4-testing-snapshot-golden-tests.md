[Readiness Fix] <REPO_NAME> Snapshot or Golden-File Tests

Fix the failing signal: Snapshot or Golden-File Tests ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Snapshot or Golden-File Tests
**Score**: [0/1]
**Description**: Tests that detect unexpected output changes by diffing live output against a checked-in reference (snapshot, golden file, recorded HTTP cassette, image baseline)
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Snapshot or golden-file tests – check for a checked-in directory of reference outputs that a test run diffs against on every invocation. PASS requires BOTH (a) at least one populated reference artifact AND (b) test code that loads and asserts against it. Look for at least one of:

1. **JS/TS inline or file snapshots**: `__snapshots__/*.snap` directories (Jest, Vitest) OR `toMatchInlineSnapshot(\`…\`)` calls with non-empty payloads in test files. A `__snapshots__/` directory containing only stale single-line `exports[…] = \`[]\`` entries is a stub; require at least one snapshot with meaningful structure (object trees, rendered markup, formatted text).
2. **Component / visual snapshots**: Storybook `.storybook/test-runner.ts` running `@storybook/test-runner` with `toMatchImageSnapshot`, OR Playwright `expect(page).toHaveScreenshot()` with baselines committed under `**/*-snapshots/`, OR a Chromatic / Percy / Loki project ID wired into CI.
3. **Go golden files**: `testdata/` directories containing `*.golden` / `*.golden.json` files paired with test code reading them — typically via `os.ReadFile` plus `cmp.Diff` (`github.com/google/go-cmp/cmp`) or `cupaloy` (`github.com/bradleyjkemp/cupaloy`). A `-update` flag on the test binary is a strong positive signal.
4. **Python snapshots**: `syrupy` (`__snapshots__/*.ambr` or `*.json`), `pytest-snapshot` (`snapshots/` dir), or `pytest-regressions` (`*.regression.txt`, `*.regression.yml`). Look for `assert x == snapshot` patterns and a populated reference dir.
5. **Rust snapshots**: `insta` crate with `*.snap` files under `tests/snapshots/` or `src/snapshots/`, asserted via `insta::assert_snapshot!` / `assert_yaml_snapshot!` / `assert_json_snapshot!`. `cargo insta review` workflow documented in README is a bonus.
6. **HTTP cassettes**: `vcrpy` (`cassettes/*.yaml`), Ruby `vcr` (`spec/cassettes/*.yml`), `pollyjs` (`recordings/*.har`), or `nock` recordings (`fixtures/*.json` referenced via `nock.back`). Cassettes must be committed AND loaded by tests — a `cassettes/` dir with one stale recording from 3 years ago and no test references is a FAIL.

A test that calls `JSON.stringify(result)` and `console.log`s it without asserting against a checked-in fixture is NOT a snapshot test. The defining property is: **the reference output lives on disk, the test diffs against it, and an unexpected change fails CI**.

## Your Task

1. Explore the repository to identify the test framework(s) in use, the languages, and any existing fixture/snapshot infrastructure (search for `__snapshots__`, `testdata/`, `snapshots/`, `cassettes/`, `*.snap`, `*.golden`, `*.ambr`, `toMatchSnapshot`, `toMatchInlineSnapshot`, `assert_snapshot`, `cmp.Diff`).
2. Identify 2–5 functions or components in the codebase whose output is **stable, structured, and worth protecting from regression** — good candidates: pure formatters, serializers, API response builders, rendered components, CLI output, query planners, prompt templates, generated SQL/HTML/Markdown.
3. Make **substantive improvements** by adding real snapshot/golden tests:
   - **JS/TS (Jest/Vitest)**: add `*.test.ts` files that call `toMatchSnapshot()` or `toMatchInlineSnapshot()` on rendered component output, serialized state, or formatter results. Run the suite once to populate `__snapshots__/`. Commit both the test and the generated snapshot file.
   - **JS/TS (React components)**: prefer `@testing-library/react` + `toMatchSnapshot` on `container.firstChild`, OR set up Storybook with `@storybook/test-runner` and commit image baselines.
   - **Go**: create a `testdata/` directory next to the test, write golden files (`expected.json`, `expected.golden`), and have the test read them via `os.ReadFile` + `cmp.Diff(want, got)`. Implement an `update` flag (`var update = flag.Bool("update", false, "update golden files")`) and document `go test ./... -update` in CONTRIBUTING.
   - **Python**: add `syrupy` (`pip install syrupy`) and write tests using `assert result == snapshot`. Run `pytest --snapshot-update` once, then commit `__snapshots__/*.ambr`.
   - **Rust**: add `insta` to `[dev-dependencies]`, write `insta::assert_yaml_snapshot!(result)`, run `cargo insta review` to accept, commit `tests/snapshots/*.snap`.
   - **HTTP-heavy code**: record real responses with `vcrpy` / `pollyjs` / `nock.back` once, commit the cassette, and ensure subsequent runs replay (no live network).
4. Document the snapshot review workflow in the repo's testing docs (or CONTRIBUTING.md): how to update snapshots intentionally (`vitest -u`, `pytest --snapshot-update`, `cargo insta review`, `playwright test --update-snapshots`, `go test ./... -update`), and the rule that snapshot diffs in PRs MUST be human-reviewed, not blanket-accepted.
5. Verify the tests actually run and fail on change: run the suite, mutate the source by one character, run again, and confirm the snapshot test reports a diff. Revert the mutation.
6. Keep changes focused on this signal — do not refactor unrelated code or add non-snapshot tests.
7. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** empty snapshot files. A `*.snap` file containing only `// Jest Snapshot v1, https://goo.gl/fbAQLP` with zero exports is a stub — it satisfies the file-existence check but asserts nothing.
- **NO** snapshots containing placeholder content (`exports[\`foo 1\`] = \`TODO\`;`, `expected: "fill me in"`). The golden value must be the real, current output of the function under test.
- **NO** auto-update on every CI run. CI MUST run snapshots in assertion mode, not update mode. A `package.json` script like `"test:ci": "vitest -u"` or a GitHub Action that runs `pytest --snapshot-update` and commits the result silently destroys the entire point of the signal — the snapshot will always match because it was just regenerated.
- **NO** ignored snapshot diffs in CI. If you wire `continue-on-error: true` around the snapshot step, the regression detector cannot detect regressions.
- **NO** mega-snapshots that hide real changes. A 5,000-line snapshot of an entire page's HTML will diff on every whitespace tweak, train reviewers to rubber-stamp `-u`, and the test stops catching anything. Prefer many small focused snapshots (per component, per function) over one giant one.
- **NO** snapshotting timestamps, UUIDs, random values, or absolute file paths without scrubbing. Use serializers (`expect.addSnapshotSerializer`, syrupy `extension_class`, insta `Settings::with_redactions`) or a property-replacement step before assertion. A flaky snapshot will be `-u`'d into uselessness within a week.
- **NO** committing HTTP cassettes that contain real API keys, bearer tokens, cookies, or PII. Configure the recorder to filter sensitive headers (`vcrpy` `filter_headers=['authorization']`, `nock.back` `afterRecord`) before the recording lands on disk.
- **NO** marking the signal "fixed" by adding `__snapshots__/` to `.gitignore`. Snapshots are checked-in source-of-truth artifacts; if they're gitignored, there is no reference for the test to diff against.
- **NO** adding a snapshot test for a function whose output is `undefined`, `null`, `{}`, or `""`. Test something with real shape.

Examples of BAD fixes:
- Creating `src/__snapshots__/formatter.test.ts.snap` with `exports[\`formatter renders 1\`] = \`""\`;` — empty payload, asserts nothing.
- Adding a Vitest test `expect(JSON.stringify(getUser())).toMatchSnapshot()` where `getUser()` returns a row containing `created_at: new Date()` and `id: crypto.randomUUID()` — every run produces a new snapshot diff, devs `-u` reflexively, and a real regression hides in the noise.
- Wiring `pytest --snapshot-update` into `.github/workflows/test.yml` with `git config user.email …; git commit -am "update snapshots"; git push` — CI becomes a rubber stamp.
- Committing `cassettes/login.yaml` containing `Authorization: Bearer sk-live-abc123…` and the user's real email in the response body.
- Adding one Go `testdata/expected.json` with `{}` and a test that asserts `string(got) == "{}"` — passes trivially, catches nothing.
- A `__snapshots__/` directory with three real snapshot files plus a comment in the test runner config that says `// TODO: re-enable snapshot diff` — disabled assertions are not assertions.

Examples of GOOD fixes:

**Vitest snapshot test** (`src/formatters/currency.test.ts`):
```ts
import { describe, it, expect } from "vitest";
import { formatInvoice } from "./currency";

describe("formatInvoice", () => {
  it("renders a multi-line USD invoice with tax + discount", () => {
    const result = formatInvoice({
      currency: "USD",
      lines: [
        { sku: "A-100", qty: 2, unit: 19.99 },
        { sku: "B-200", qty: 1, unit: 5.5 },
      ],
      taxRate: 0.0875,
      discountPct: 10,
    });
    expect(result).toMatchInlineSnapshot(`
      "A-100  x2  @ $19.99   $39.98
      B-200  x1  @ $5.50      $5.50
      ----------------------------
      Subtotal                $45.48
      Discount (10%)          -$4.55
      Tax (8.75%)              $3.58
      Total                   $44.51"
    `);
  });
});
```

**Storybook visual regression** (`.storybook/test-runner.ts`):
```ts
import type { TestRunnerConfig } from "@storybook/test-runner";
import { toMatchImageSnapshot } from "jest-image-snapshot";

const config: TestRunnerConfig = {
  setup() {
    expect.extend({ toMatchImageSnapshot });
  },
  async postVisit(page, context) {
    const image = await page.screenshot({ fullPage: true });
    expect(image).toMatchImageSnapshot({
      customSnapshotsDir: `${process.cwd()}/__image_snapshots__`,
      customSnapshotIdentifier: context.id,
      failureThreshold: 0.01,
      failureThresholdType: "percent",
    });
  },
};
export default config;
```
Paired with a `.github/workflows/visual.yml` step that runs `pnpm storybook:build && pnpm test-storybook --url file://$PWD/storybook-static` and uploads any diff PNG as an artifact for human review.

**Go golden file** (`internal/render/render_test.go`):
```go
var update = flag.Bool("update", false, "update golden files")

func TestRenderManifest(t *testing.T) {
  got, err := RenderManifest(testFixture())
  if err != nil { t.Fatal(err) }
  goldenPath := filepath.Join("testdata", "manifest.golden.json")
  if *update {
    os.WriteFile(goldenPath, got, 0o644)
  }
  want, err := os.ReadFile(goldenPath)
  if err != nil { t.Fatal(err) }
  if diff := cmp.Diff(string(want), string(got)); diff != "" {
    t.Errorf("manifest mismatch (-want +got):\n%s", diff)
  }
}
```

**Python syrupy** (`tests/test_planner.py`):
```python
def test_plan_serialization(snapshot):
    plan = build_plan(spec=load_spec("fixtures/spec.yaml"))
    assert plan.to_dict() == snapshot
```
Run once with `pytest --snapshot-update`, commit `__snapshots__/test_planner.ambr`.

**Rust insta** (`src/query.rs`):
```rust
#[test]
fn compiles_select_with_joins() {
    let sql = compile(&parse("FROM users JOIN orders ON users.id = orders.user_id"));
    insta::assert_snapshot!(sql);
}
```
Accept via `cargo insta review`, commit `src/snapshots/query__compiles_select_with_joins.snap`.

**HTTP cassette** (`tests/test_github_client.py`):
```python
@pytest.mark.vcr(filter_headers=["authorization", "cookie"])
def test_fetch_repo_metadata():
    repo = client.get_repo("octocat/Hello-World")
    assert repo.default_branch == "master"
    assert repo.stargazers_count > 0
```
Record once against the live API, commit `tests/cassettes/test_fetch_repo_metadata.yaml` with `Authorization` redacted to `DUMMY`.

**Snapshot review workflow** (add to CONTRIBUTING.md):
```
## Updating snapshots

Snapshot diffs are intentional only when the underlying behavior changed. Never
blanket-update. To accept:
- JS/TS:    pnpm vitest -u path/to/file.test.ts
- Python:   pytest --snapshot-update tests/test_x.py
- Rust:     cargo insta review
- Go:       go test ./pkg/... -update
- Playwright: pnpm playwright test --update-snapshots path/to/spec.ts

Review the diff in your PR. If you cannot explain every line that changed,
revert and investigate. CI runs snapshots in assertion mode; --update is never
run automatically.
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Jest snapshot testing (file + inline): https://jestjs.io/docs/snapshot-testing
- Vitest snapshots: https://vitest.dev/guide/snapshot
- Storybook test-runner (visual + interaction): https://storybook.js.org/docs/writing-tests/test-runner
- jest-image-snapshot (pixel-diff): https://github.com/americanexpress/jest-image-snapshot
- Playwright visual comparisons (`toHaveScreenshot`): https://playwright.dev/docs/test-snapshots
- Chromatic visual regression: https://www.chromatic.com/docs/visual-tests/
- Percy visual testing: https://docs.percy.io/docs/visual-testing-basics
- Go golden files + `go-cmp`: https://github.com/google/go-cmp ; pattern guide https://ieftimov.com/posts/testing-in-go-golden-files/
- cupaloy (Go snapshot library): https://github.com/bradleyjkemp/cupaloy
- syrupy (Python pytest snapshots): https://github.com/syrupy-project/syrupy
- pytest-snapshot: https://github.com/joseph-roitman/pytest-snapshot
- pytest-regressions: https://pytest-regressions.readthedocs.io
- insta (Rust): https://insta.rs ; `cargo insta review` workflow https://insta.rs/docs/cli/
- vcrpy (Python HTTP cassettes): https://vcrpy.readthedocs.io/en/latest/usage.html
- VCR (Ruby): https://benoittgt.github.io/vcr/
- PollyJS (browser/Node HTTP recording): https://netflix.github.io/pollyjs/
- nock recorder (Node HTTP mocking + record): https://github.com/nock/nock#recording
- Kent C. Dodds, "Effective Snapshot Testing" (small-snapshot principle): https://kentcdodds.com/blog/effective-snapshot-testing
</system-reminder>
