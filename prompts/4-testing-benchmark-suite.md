[Readiness Fix] <REPO_NAME> Benchmark Suite

Fix the failing signal: Benchmark Suite ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Benchmark Suite
**Score**: [0/1]
**Description**: Performance tests the agent can run for regression checks
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Benchmark suite – check for a checked-in, runnable performance benchmark suite that the agent can execute and compare against a baseline. PASS requires all of:

1. **Benchmark files exist** under a conventional path: Go `*_bench_test.go` (anywhere in the tree), Rust `benches/*.rs` driven by Criterion.rs, Python `tests/benchmarks/test_*.py` using `pytest-benchmark` or an `asv.conf.json` + `benchmarks/` dir for airspeed velocity, JS/TS `*.bench.ts` using Vitest `bench()` or `bench/*.{js,ts,mjs}` using mitata/tinybench, browser perf via Tachometer config, CLI wall-time via `hyperfine` scripts, HTTP load via `k6` `.js` scripts or Artillery `.yml`, Python load via `locustfile.py`.
2. **A single documented command runs the suite** — `go test -bench=. -benchmem ./...`, `cargo bench`, `pytest --benchmark-only`, `asv run`, `vitest bench`, `node bench/run.mjs`, `k6 run bench/load.js`, etc. The command MUST be in `package.json` scripts, a `Makefile` / `justfile` target, `pyproject.toml` `[tool.poetry.scripts]`, or explicitly called out in `AGENTS.md` / `CONTRIBUTING.md` / `README.md`.
3. **Baseline + regression comparison** — at least one of: a committed baseline file (`benchstat` `old.txt`/`new.txt` flow, Criterion's `target/criterion/*/base/`, `pytest-benchmark` `--benchmark-compare` with a saved `.benchmarks/` JSON, `asv publish` HTML or `asv compare`), OR a CI job that posts the result to Bencher.dev, Codspeed, or an equivalent tracker that fails the build on regression beyond a threshold.
4. **Benchmarks actually measure work** — the hot loop's result is consumed (`b.ResultUsed`, `std::hint::black_box`, Criterion's `black_box`, Vitest `bench` callback that returns a value, JMH-style `Blackhole`). A loop whose result the compiler can fold to a constant measures nothing.

A `BENCHMARKING.md` describing how someone could benchmark, with no committed code, FAILs this signal. A single `_bench_test.go` that times `1+1` FAILs (no real workload). A `cargo bench` target that has never been run in CI and has no baseline FAILs criterion 3.

## Your Task

1. Explore the repository to identify the hottest path(s) worth benchmarking — the pure functions or service handlers on the critical request/render path, NOT incidental utilities. Read `README.md`, profile artifacts under `docs/perf/` if any, and look for existing `*_bench*`, `benches/`, `bench/`, `*.bench.*`, `locustfile.py`, `k6*.js`, `asv.conf.json`.
2. Make **substantive improvements** by adding a real benchmark suite:
   - Pick the right tool for the stack: Go → `testing.B`; Rust → Criterion.rs; Python lib → `pytest-benchmark`; Python long-horizon → `asv`; JS/TS lib → Vitest `bench()` (preferred) or `mitata`/`tinybench`; browser render → Tachometer; CLI wall-time → `hyperfine`; HTTP service → `k6` (preferred) or Artillery or `locust`.
   - Write 3-8 benchmarks covering the actual hot paths. Each one MUST consume its result via `black_box` / `b.ResultUsed` / a returned value so the optimizer cannot fold it away.
   - Add a single command (npm script, Makefile target, justfile recipe) that runs the suite locally with sensible iteration counts.
   - Wire a CI job (`.github/workflows/bench.yml`) that runs the suite on PR + main, uploads results to Bencher.dev (`bencherdev/bencher@main`) or Codspeed, and fails the PR if any benchmark regresses beyond a documented threshold (e.g. `--threshold-upper-boundary 0.99`).
   - Document the run command and the regression policy in `AGENTS.md` (or `CONTRIBUTING.md` if no `AGENTS.md` exists).
3. Verify the suite runs: execute the documented command locally with a small iteration count (Go `-benchtime=1x`, Vitest `--run`, k6 `--duration 5s`) and confirm it produces numeric results with units (ns/op, ops/sec, p95 ms). Confirm CI parses the output (check the workflow's `outputs` step).
4. Keep changes focused on this signal — do not refactor the code under benchmark, do not add unrelated tests.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** synthetic micro-benchmarks (`BenchmarkAdd` that times `1+2`, `bench('noop', () => {})`). The whole point is regression coverage of code that ships.
- **NO** benchmark whose result is discarded — `for i := 0; i < b.N; i++ { someFunc() }` lets the Go compiler dead-code-eliminate the call. Use `var sink T; sink = someFunc(); _ = sink` or `runtime.KeepAlive(sink)`. In Rust/Criterion, wrap inputs in `black_box(...)`. In Vitest `bench`, return the value from the callback.
- **NO** missing warmup. Criterion, Vitest `bench`, mitata, and `pytest-benchmark` warm up by default — do not pass flags that disable it (`--warmup-iterations 0`). For Go, the first iteration of `b.N` is the warmup; do NOT short-circuit on `b.N == 1`.
- **NO** running the suite once with no baseline. A number with no comparison cannot detect regression. Commit a baseline (`benchstat`, Criterion `--save-baseline main`, `pytest-benchmark --benchmark-save=main`) or push to a tracker that stores history.
- **NO** CI job that runs benchmarks and ignores the output. The job must fail the build on regression, or post a PR comment with delta vs main that a human review can gate on. Silent benchmarks rot in days.
- **NO** benchmarking on GitHub Actions `ubuntu-latest` without acknowledging noise — shared runners have ±10-30% variance. Either use `bencherdev/bencher` with statistical thresholds, Codspeed (instruction-count based, runner-agnostic), or pin to a self-hosted runner.
- **NO** load tests with 1 virtual user for 5 seconds called a "benchmark." k6/Artillery/locust runs need at least a ramp profile (`stages: [{duration: '30s', target: 50}, {duration: '1m', target: 50}]`) and an SLO threshold (`http_req_duration: ['p(95)<300']`).
- **NO** committing `target/criterion/`, `.benchmarks/`, `node_modules/.vitest/`, `results/` raw output dirs — add them to `.gitignore`. Only commit baseline summaries (the small `.json` or `.txt`).
- **NO** Python `time.time()` loops written by hand. Use `pytest-benchmark` so you get median/min/max/stddev and JSON output a tracker can consume.

Examples of BAD fixes:
- `bench/noop.bench.ts` with `bench('add', () => 1 + 1)` — measures nothing the project ships.
- `Makefile` target `bench: go test -bench=.` but zero `*_bench_test.go` files exist.
- `cargo bench` benches that use `let _ = my_fn(input);` — `input` is a constant literal, compiler precomputes everything; benchmark reports nanoseconds that are really cache-line fetch time.
- `.github/workflows/bench.yml` that runs `vitest bench` and uploads the JSON to artifacts but never compares against main. Two weeks in, a 3x regression ships unnoticed.
- One k6 script with `vus: 1, duration: '10s'` against `localhost` on the runner that boots the server in the same step — measures cold start + GC, not steady-state throughput.

Examples of GOOD fixes:
- **Go** — `internal/render/render_bench_test.go`:
  ```go
  package render

  import (
      "runtime"
      "testing"
  )

  var sink []byte

  func BenchmarkRenderHomepage(b *testing.B) {
      doc := mustLoadFixture(b, "testdata/homepage.json")
      b.ReportAllocs()
      b.ResetTimer()
      var out []byte
      for i := 0; i < b.N; i++ {
          out = Render(doc)
      }
      runtime.KeepAlive(out)
      sink = out
  }
  ```
  `Makefile`:
  ```make
  bench:
  	go test -bench=. -benchmem -count=10 -run=^$$ ./... | tee bench.txt
  bench-compare: bench
  	benchstat baseline.txt bench.txt
  ```
- **JS/TS** — `src/parser/parser.bench.ts`:
  ```ts
  import { bench, describe } from 'vitest';
  import { parse } from './parser';
  import fixture from './__fixtures__/large.json' with { type: 'json' };

  describe('parser', () => {
    bench('parse large doc', () => {
      return parse(fixture); // returned -> not dead-code-eliminated
    }, { time: 1000, warmupIterations: 50 });
  });
  ```
  `package.json`: `"bench": "vitest bench --run"`.
- **CI** — `.github/workflows/bench.yml` posting to Bencher.dev:
  ```yaml
  name: Benchmarks
  on:
    push: { branches: [main] }
    pull_request: {}
  jobs:
    benchmark:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with: { node-version: '20', cache: 'pnpm' }
        - uses: bencherdev/bencher@main
        - run: pnpm install --frozen-lockfile
        - name: Track main branch baseline
          if: github.event_name == 'push'
          run: |
            bencher run \
              --project <REPO_SLUG> \
              --token "${{ secrets.BENCHER_API_TOKEN }}" \
              --branch main \
              --testbed ubuntu-latest \
              --adapter js_benchmark \
              --err \
              'pnpm bench --outputJson bench-results.json && cat bench-results.json'   # vitest bench's --reporter only supports default/verbose; use --outputJson then pipe to stdout for Bencher's js_benchmark adapter (Vitest issue #5953)
        - name: Compare PR vs main
          if: github.event_name == 'pull_request'
          run: |
            bencher run \
              --project <REPO_SLUG> \
              --token "${{ secrets.BENCHER_API_TOKEN }}" \
              --branch '${{ github.head_ref }}' \
              --start-point main \
              --start-point-reset \
              --testbed ubuntu-latest \
              --adapter js_benchmark \
              --github-actions "${{ secrets.GITHUB_TOKEN }}" \
              --threshold-measure latency \
              --threshold-test t_test \
              --threshold-max-sample-size 64 \
              --threshold-upper-boundary 0.99 \
              --thresholds-reset \
              --err \
              'pnpm bench --outputJson bench-results.json && cat bench-results.json'   # vitest bench's --reporter only supports default/verbose; use --outputJson then pipe to stdout for Bencher's js_benchmark adapter (Vitest issue #5953)
  ```
- **Rust** — `benches/parser.rs` using Criterion with `black_box`:
  ```rust
  use criterion::{black_box, criterion_group, criterion_main, Criterion};
  use my_crate::parse;

  fn bench_parse(c: &mut Criterion) {
      let input = include_str!("../testdata/large.json");
      c.bench_function("parse_large", |b| b.iter(|| parse(black_box(input))));
  }
  criterion_group!(benches, bench_parse);
  criterion_main!(benches);
  ```
  Run: `cargo bench -- --save-baseline main`; compare PR: `cargo bench -- --baseline main`.
- **Python** — `tests/benchmarks/test_render.py`:
  ```python
  def test_render_homepage(benchmark, sample_doc):
      result = benchmark(render, sample_doc)
      assert result.status == "ok"
  ```
  Run: `pytest tests/benchmarks --benchmark-only --benchmark-autosave`; compare: `pytest-benchmark compare 0001 0002 --csv=delta.csv --fail=mean:10%`.
- **HTTP service** — `bench/load.js`:
  ```js
  import http from 'k6/http';
  import { check } from 'k6';
  export const options = {
    stages: [
      { duration: '30s', target: 50 },
      { duration: '2m',  target: 50 },
      { duration: '30s', target: 0  },
    ],
    thresholds: {
      http_req_duration: ['p(95)<300', 'p(99)<800'],
      http_req_failed:   ['rate<0.01'],
    },
  };
  export default function () {
      const res = http.get(`${__ENV.BASE_URL}/api/render`);
      check(res, { '200': r => r.status === 200 });
  }
  ```
  Run: `k6 run --env BASE_URL=http://localhost:3000 bench/load.js`.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Go `testing` package, `Benchmark` functions and `b.N` loop semantics: https://pkg.go.dev/testing#hdr-Benchmarks
- `benchstat` for comparing Go benchmark runs: https://pkg.go.dev/golang.org/x/perf/cmd/benchstat
- Criterion.rs user guide (baselines, `black_box`, regression detection): https://bheisler.github.io/criterion.rs/book/
- `pytest-benchmark` documentation: https://pytest-benchmark.readthedocs.io/
- `asv` (airspeed velocity) for long-horizon Python perf tracking: https://asv.readthedocs.io/
- Vitest `bench` API (Tinybench under the hood): https://vitest.dev/api/#bench
- mitata micro-benchmark runner: https://github.com/evanwashere/mitata
- tinybench: https://github.com/tinylibs/tinybench
- Tachometer for browser benchmarking: https://github.com/google/tachometer
- hyperfine CLI wall-time benchmarking: https://github.com/sharkdp/hyperfine
- k6 load testing thresholds & stages: https://grafana.com/docs/k6/latest/using-k6/thresholds/
- Artillery load testing: https://www.artillery.io/docs
- Locust for Python load tests: https://docs.locust.io/
- Bencher.dev continuous benchmarking + GitHub Action: https://bencher.dev/docs/how-to/github-actions/
- Codspeed (instruction-count based, runner-agnostic): https://codspeed.io/docs
- Why micro-benchmarks lie when results aren't consumed (Go FAQ): https://go.dev/doc/faq#benchmarks
</system-reminder>
