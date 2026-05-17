[Readiness Fix] <REPO_NAME> Cost Telemetry for Agent Runs

Fix the failing signal: Cost Telemetry for Agent Runs ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Cost Telemetry for Agent Runs
**Score**: [0/1]
**Description**: Token usage and run cost are tracked and attributable to a session, PR, or user
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Cost telemetry for agent runs — check for a checked-in mechanism that records, per agent invocation, (a) input tokens, (b) output tokens, (c) the model that was called, and (d) a cost figure in USD that aggregates to at least one durable rollup (per session, per PR, per user, or per day). PASS requires at least one of the following, with concrete evidence wired end-to-end (not just an empty config):

1. **OpenTelemetry GenAI metric/attribute capture**: the agent runtime emits the OTel GenAI conventions for usage — `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.system`, `gen_ai.operation.name` — and either the histogram metric `gen_ai.client.token.usage` (split by `gen_ai.token.type=input|output`) OR a custom `gen_ai.usage.cost_usd` metric/attribute computed from a checked-in pricing table. The exporter must point to a real backend (Langfuse, Phoenix Arize, Honeycomb, Datadog, Grafana Tempo/Mimir, Elastic, Helicone, Braintrust) — `localhost:4317` with no documented collector is theatre.
2. **Claude Code native cost telemetry**: `CLAUDE_CODE_ENABLE_TELEMETRY=1` is set in `.env.example` / `AGENTS.md` with `OTEL_METRICS_EXPORTER=otlp` and a documented endpoint. The `claude_code.cost.usage` metric (USD per session, labeled by `model`, `user.id`, `session.id`, `organization.id`) lands in a backend, and the runbook explains how to query "cost per session" and "cost per PR" (joined on `session.id` ↔ commit trailer; see Agent Audit Trail signal). A `.env.example` with only `CLAUDE_CODE_ENABLE_TELEMETRY=1` and no exporter or backend FAILs.
3. **Per-run cost log line**: every agent invocation appends an NDJSON / structured log record containing at minimum `{run_id, agent, model, input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens, cost_usd, started_at, ended_at}` to a durable sink (gitignored payload directory in the repo, `~/.claude/logs/`, S3/GCS bucket, or remote log backend). The log MUST include the model identifier — a row with token counts but no model cannot be priced and FAILs. A `console.log("tokens: 1234")` to stderr that nobody captures FAILs.
4. **Provider SDK usage capture inside the application**: for repos that call LLM SDKs directly (Anthropic SDK, OpenAI SDK, Vercel AI SDK), code reads the `usage` object from every response and persists it. For Anthropic, that is `response.usage.input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` (cache fields are billed at different rates — omitting them under-reports cost on cached workloads); the request-id is in the `request-id` response header / `_request_id` SDK accessor. For OpenAI, `response.usage.prompt_tokens`, `completion_tokens`, `total_tokens`. For Vercel AI SDK, the `onFinish({usage})` callback on `streamText`/`generateText` gives `inputTokens`, `outputTokens`, `totalTokens`. The capture must survive streaming (single-event `usage` on final chunk for Anthropic/OpenAI; `onFinish` for Vercel AI SDK — `onChunk` does NOT receive usage) and aborted requests (Vercel AI SDK's `onFinish` does not fire on abort — handle the `AbortError` path explicitly).
5. **Per-PR / per-session cost rollup**: a script, workflow, or dashboard that aggregates the raw per-call usage into a durable, queryable artifact at the granularity an incident responder cares about. Minimum bar: a Markdown comment on each agent-authored PR (e.g. `Agent cost: $0.42 across 17 calls — claude-sonnet-4.6 input 18,432 tok, output 4,108 tok, cache hits 412,800 tok`) OR a daily/weekly digest pushed to the team. A pile of NDJSON files with no rollup FAILs — nobody reviews raw logs after the fact.

Also verify the chain holds end-to-end:

- The pricing constants must be checked in (a `pricing.json` / `pricing.ts` / `pricing.yaml` keyed by `model` → `{input_per_mtok, output_per_mtok, cache_write_5m_per_mtok, cache_write_1h_per_mtok, cache_read_per_mtok}` in USD per 1M tokens). A cost number derived from hardcoded values buried in a function makes it impossible to spot when pricing drifts. Anthropic and OpenAI both publish updated rate cards; the file must be reviewed.
- Cost must be computed from BOTH input AND output tokens (and cache tokens, if the provider charges differently — Anthropic does). A row that only counts `input_tokens * input_rate` will under-bill by ~5x on a typical chat workload because output is priced at 5x input for Claude Sonnet 4.6 ($3 vs $15 per 1M).
- The model identifier must be persisted on every row. Without it, the rollup cannot price the call. `claude-3-5-sonnet` ($3/$15) and `claude-3-5-haiku` ($0.80/$4) differ by ~4x; mixing them and pricing at one rate makes the dashboard a lie.
- Streaming responses must not break capture. Anthropic / OpenAI SSE streams emit `usage` exactly once on the final `message_stop` / `[DONE]` event; if your wrapper drops it (e.g. it only forwards `content_block_delta` events) the row is unbilled. Test the streaming path explicitly.
- The rollup must be reviewed by a human on a routine cadence. A dashboard that nobody opens until the bill arrives is decoration. Wire a weekly digest to Slack/email, OR set a budget alert in the OTel backend (`claude_code.cost.usage` > threshold) that pages someone.
- Costs must be attributable. Aggregated "everyone ran $X this month" is unactionable; the runbook needs "which session/PR/user caused the spike". Tag every row with `session.id` (Claude Code), `gen_ai.conversation.id` (OTel), or the runtime's native session identifier so it joins back to the audit trail (see Agent Audit Trail signal).

A README sentence saying "we monitor agent costs in Datadog" without a metric name, dashboard URL, or alert rule FAILs this signal. A Helicone / Langfuse account that the team set up six months ago and nobody logs into is dead infrastructure; the runbook must point at it and someone must review it.

## Your Task

1. Explore the repository to understand the current state related to this signal:
   - List every `.env.example`, `.claude/settings*.json`, `.factory/settings*.json`, `AGENTS.md`, `docs/agent-*.md`, and any `pricing.{json,ts,yaml}` / `costs.{json,ts}` file.
   - Grep for existing usage capture: `git grep -nE "input_tokens|output_tokens|usage\.|onFinish|claude_code\.cost|gen_ai\.(usage|client)|CLAUDE_CODE_ENABLE_TELEMETRY"`.
   - Identify which LLM clients the repo actually calls (`@anthropic-ai/sdk`, `openai`, `ai` (Vercel AI SDK), LangChain, custom HTTP). That determines which capture path is available.
   - Check for an OTel collector / Langfuse / Helicone / Phoenix instance already wired in `docker-compose.yml`, `infra/`, `.env.example`, or the team's observability docs.
   - Confirm whether the repo runs Claude Code in CI (a `claude-code` GitHub Action job) — that's a natural place to attach `actions/upload-artifact` cost rollups.
2. Make **substantive improvements** by wiring at least one durable, attributable cost path end-to-end:
   - **Pricing table (always required)**: check in `pricing/llm-pricing.json` keyed by model ID with input / output / cache-write / cache-read rates per 1M tokens. Add a short note pointing to the provider rate cards and a `// Last verified: <date>` field so drift is visible.
   - **Application-side capture (if the repo calls LLM SDKs directly)**: wrap every Anthropic / OpenAI / Vercel AI SDK call so the response `usage` is logged with the model id and request id, then priced via the table. Cover streaming (`message_stop` for Anthropic, `[DONE]` for OpenAI, `onFinish` for Vercel AI SDK) AND the abort path.
   - **Claude Code native (if devs use Claude Code on the repo)**: set `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_METRICS_EXPORTER=otlp`, `OTEL_EXPORTER_OTLP_ENDPOINT=<real-backend>`, `OTEL_SERVICE_NAME=<REPO_NAME>-claude-code` in `.env.example` and document the backend in `AGENTS.md`. The `claude_code.cost.usage` metric (USD, counter) and `claude_code.token.usage` (counter, split by `type=input|output|cacheRead|cacheCreation`) will export automatically.
   - **Per-PR rollup**: add `.github/workflows/agent-cost-comment.yml` that, when an agent-authored PR is opened or synchronized, downloads the run-log artifact (or queries the OTel backend) and posts a sticky comment with total cost and per-model breakdown for the PR's session id.
   - **AGENTS.md cost section**: a `## Agent Cost Telemetry` block listing (a) the metric / log fields captured, (b) where the data lands, (c) the pricing table location and review cadence, (d) the budget alert threshold and who gets paged, (e) the runbook entry "given a spending spike, here's how to find the offending session / PR / user".
3. Verify the chain works end-to-end:
   - Run a trivial Claude Code session (or a small SDK script) with `CLAUDE_CODE_ENABLE_TELEMETRY=1` and confirm one `claude_code.cost.usage` data point lands in the configured backend, labeled with `session.id`, `model`, and `user.id`.
   - Trigger the per-PR rollup on a throwaway PR and confirm the comment renders with a non-zero cost and the correct model id.
   - Spike test: temporarily set the budget alert threshold to a very low value, run one call that exceeds it, and confirm the alert fires.
   - Pricing-table sanity check: pick one logged row, multiply by the rate card by hand, and confirm the persisted `cost_usd` matches within rounding.
4. Keep changes focused on this signal — do not refactor unrelated observability or CI config. Do not stand up a self-hosted Langfuse + Postgres just to pass this signal; a pricing table + per-call log + per-PR comment is sufficient for L3. Full OTel export is the bonus path.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** counting calls without counting cost. "We made 412 LLM calls this week" tells you nothing about the bill. The capture MUST persist token counts AND model AND a USD figure.
- **NO** counting input tokens only (or output tokens only). Output is 4-5x the input rate on Anthropic/OpenAI; either-side-only under-reports by ~5x on chat workloads.
- **NO** dropping cache token fields when the provider charges differently for them. Anthropic bills `cache_creation_input_tokens` at 1.25x base input (5m TTL) or 2x (1h TTL), and `cache_read_input_tokens` at 0.1x. A naive rollup that lumps everything into `input_tokens` mis-prices cached workloads by up to 12x in either direction.
- **NO** persisting tokens without the model id. `{input: 1832, output: 412}` is unbillable — you cannot price it. Always log `model` next to the counts.
- **NO** hardcoded pricing constants buried in a function. Put rates in a single checked-in file with a `last_verified` date so drift is reviewable.
- **NO** stale pricing. Anthropic and OpenAI rate cards change; if your `pricing.json` still has 2024 rates the dashboard is lying. Schedule a quarterly review and put it in `AGENTS.md`.
- **NO** logs to a path that disappears. `/tmp/cost.log`, `%TEMP%\usage.json`, stderr that nobody captures, a `console.log` that scrolls off — all useless after the session ends. Persist to a gitignored repo directory, `~/.claude/logs/`, an artifact upload, or a remote backend.
- **NO** streaming capture that listens to `content_block_delta` / `chunk` events but never reads the final `message_stop` / `[DONE]` / `onFinish` event. The `usage` object lands exactly once at the end; miss it and the row is unbilled.
- **NO** Vercel AI SDK capture that ignores aborted streams. `onFinish` does NOT fire when the request is aborted; wrap the call in a `try/catch` for `AbortError` and persist a partial-cost row with what you do know (input tokens are known up front from the request).
- **NO** "we have Helicone" / "we use Langfuse" without a runbook. The point is forensic recovery: if you cannot tell me "session `cc-7f3a-...` cost $14.20 across these 23 calls" inside two minutes, the dashboard is decoration.
- **NO** aggregated-only rollup. "$340 last week" is unactionable; you need per-session / per-PR / per-user attribution so you can find the runaway loop. Tag every row with `session.id` and join back to the commit/PR via the run-id trailer (see Agent Audit Trail signal).
- **NO** misspelled OTel attribute names. The convention is `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.system`, `gen_ai.token.type` — not `genai.tokens.input`, `gen_ai.input_tokens`, `ai.usage.in`. A misspelled attribute is unsearchable and breaks every dashboard downstream.
- **NO** budget alert that pages nobody. A threshold rule without a notification channel is a config file; wire it to a real on-call (Slack, PagerDuty, email distribution).
- **NO** committing raw NDJSON cost logs to git. Schema, directory layout, and `.gitkeep` are fine; per-run payloads bloat the repo and may leak prompts. Gitignore the payload directory and document retention separately.

Examples of BAD fixes:

- `console.log("Tokens used:", response.usage.totalTokens)` with no persistence, no model, no cost — gone the moment the terminal closes.
- A `pricing.json` with `{"claude-3-5-sonnet": 0.000003}` — single number, no input/output split, no cache rates, no `last_verified`. Mis-prices every call.
- Setting `CLAUDE_CODE_ENABLE_TELEMETRY=1` in `.env.example` with `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` and no docker-compose collector — exports go nowhere, dashboards never light up.
- A Langfuse / Helicone account configured once by the team lead, no AGENTS.md pointer, no rollup, no alert — discovered three months later when the bill lands.
- A PR comment that says "Agent cost: $0.42" with no per-model breakdown, no token counts, and no session id — useless for diagnosing a future spike.
- A weekly digest e-mail that says "total agent spend: $1,847" without per-user or per-session breakdown — nobody can act on it.
- Capturing `usage` from `generateText` but not from `streamText` — every streamed call is unbilled, and streaming is the default for chat UIs.
- Pricing input tokens at the base rate when the API response shows `cache_creation_input_tokens: 412800` — 1.25x or 2x under-counted, distorts the bill.

Examples of GOOD fixes:

**Minimum: pricing table + per-call log + per-PR comment**

`pricing/llm-pricing.json` (USD per 1M tokens; verify quarterly against provider rate cards):
```json
{
  "$schema": "./pricing.schema.json",
  "last_verified": "2026-05-15",
  "source": [
    "https://platform.claude.com/docs/en/about-claude/pricing",
    "https://openai.com/api/pricing/"
  ],
  "models": {
    "claude-sonnet-4-6": {
      "input_per_mtok": 3.00,
      "output_per_mtok": 15.00,
      "cache_write_5m_per_mtok": 3.75,
      "cache_write_1h_per_mtok": 6.00,
      "cache_read_per_mtok": 0.30
    },
    "claude-haiku-4-5": {
      "input_per_mtok": 1.00,
      "output_per_mtok": 5.00,
      "cache_write_5m_per_mtok": 1.25,
      "cache_write_1h_per_mtok": 2.00,
      "cache_read_per_mtok": 0.10
    },
    "claude-opus-4-1": {
      "input_per_mtok": 15.00,
      "output_per_mtok": 75.00,
      "cache_write_5m_per_mtok": 18.75,
      "cache_write_1h_per_mtok": 30.00,
      "cache_read_per_mtok": 1.50
    },
    "gpt-4o-2024-11-20": {
      "input_per_mtok": 2.50,
      "output_per_mtok": 10.00,
      "cache_read_per_mtok": 1.25
    }
  }
}
```

`lib/agent-cost.ts` — single point that prices any provider response and appends an NDJSON row:
```ts
import { readFileSync, appendFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { randomUUID } from "node:crypto";

type Pricing = { input_per_mtok: number; output_per_mtok: number;
                 cache_write_5m_per_mtok?: number; cache_write_1h_per_mtok?: number;
                 cache_read_per_mtok?: number };
const PRICES = JSON.parse(readFileSync("pricing/llm-pricing.json", "utf8")).models as Record<string, Pricing>;
const LOG_PATH = process.env.AGENT_COST_LOG ?? ".agent/cost/runs.ndjson";

export type CostRow = {
  run_id: string; session_id: string; agent: string; model: string;
  input_tokens: number; output_tokens: number;
  cache_creation_input_tokens: number; cache_read_input_tokens: number;
  cost_usd: number; request_id?: string;
  started_at: string; ended_at: string;
};

export function priceCall(model: string, usage: {
  input_tokens: number; output_tokens: number;
  cache_creation_input_tokens?: number; cache_read_input_tokens?: number;
  cache_write_ttl?: "5m" | "1h";
}): number {
  const p = PRICES[model];
  if (!p) throw new Error(`No pricing entry for model "${model}" — update pricing/llm-pricing.json`);
  const write = p[usage.cache_write_ttl === "1h" ? "cache_write_1h_per_mtok" : "cache_write_5m_per_mtok"] ?? p.input_per_mtok;
  const read = p.cache_read_per_mtok ?? p.input_per_mtok;
  return (
    (usage.input_tokens                 * p.input_per_mtok  +
     usage.output_tokens                * p.output_per_mtok +
     (usage.cache_creation_input_tokens ?? 0) * write       +
     (usage.cache_read_input_tokens     ?? 0) * read) / 1_000_000
  );
}

export function logCall(row: Omit<CostRow, "run_id" | "cost_usd"> & { cost_usd?: number }): void {
  const fullRow: CostRow = {
    ...row,
    run_id: randomUUID(),
    cost_usd: row.cost_usd ?? priceCall(row.model, row),
  };
  mkdirSync(dirname(LOG_PATH), { recursive: true });
  appendFileSync(LOG_PATH, JSON.stringify(fullRow) + "\n");
}
```

Anthropic SDK wrapper (covers streaming via `message_stop`):
```ts
import Anthropic from "@anthropic-ai/sdk";
import { logCall } from "./agent-cost";

const client = new Anthropic();
const started_at = new Date().toISOString();
const stream = client.messages.stream({ model: "claude-sonnet-4-6", max_tokens: 1024, messages });
let finalMessage: Anthropic.Message | null = null;

stream.on("message", (m) => { finalMessage = m; });
stream.on("end", () => {
  if (!finalMessage) return; // aborted before completion — handle separately
  logCall({
    session_id: process.env.CLAUDE_SESSION_ID ?? "local",
    agent: "anthropic-sdk",
    model: finalMessage.model,
    input_tokens: finalMessage.usage.input_tokens,
    output_tokens: finalMessage.usage.output_tokens,
    cache_creation_input_tokens: finalMessage.usage.cache_creation_input_tokens ?? 0,
    cache_read_input_tokens: finalMessage.usage.cache_read_input_tokens ?? 0,
    request_id: stream._request_id ?? undefined,
    started_at,
    ended_at: new Date().toISOString(),
  });
});
```

Vercel AI SDK wrapper (handles streaming `onFinish` AND `AbortError`):
```ts
import { streamText, APICallError } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { logCall } from "./agent-cost";

const started_at = new Date().toISOString();
try {
  const result = streamText({
    model: anthropic("claude-sonnet-4-6"),
    messages,
    onFinish: ({ usage, response }) => {
      logCall({
        session_id: process.env.CLAUDE_SESSION_ID ?? "local",
        agent: "vercel-ai-sdk",
        model: response.modelId,
        input_tokens: usage.inputTokens ?? 0,
        output_tokens: usage.outputTokens ?? 0,
        cache_creation_input_tokens: 0,
        cache_read_input_tokens: 0,
        request_id: response.id,
        started_at,
        ended_at: new Date().toISOString(),
      });
    },
  });
  return result;
} catch (err) {
  if (err instanceof DOMException && err.name === "AbortError") {
    // onFinish does not fire on abort — log a partial-cost row with what we know
    logCall({
      session_id: process.env.CLAUDE_SESSION_ID ?? "local",
      agent: "vercel-ai-sdk",
      model: "claude-sonnet-4-6",
      input_tokens: estimateInputTokensFromMessages(messages),
      output_tokens: 0,
      cache_creation_input_tokens: 0,
      cache_read_input_tokens: 0,
      started_at,
      ended_at: new Date().toISOString(),
    });
  }
  throw err;
}
```

`.github/workflows/agent-cost-comment.yml` — post per-PR rollup:
```yaml
name: Agent cost rollup
on:
  pull_request:
    types: [opened, synchronize]
permissions:
  pull-requests: write
  contents: read
jobs:
  rollup:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'ai:claude-code') ||
        contains(github.event.pull_request.labels.*.name, 'ai:factory') ||
        contains(github.event.pull_request.labels.*.name, 'ai:copilot')
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - name: Extract session id from commit trailer
        id: sid
        run: |
          SID=$(git log --pretty=format:%B "origin/${{ github.base_ref }}..HEAD" \
            | git interpret-trailers --parse \
            | awk -F': ' '/^Agent-Run-Id:/ { print $2; exit }')
          echo "session_id=${SID}" >> "$GITHUB_OUTPUT"
      - name: Roll up cost
        if: steps.sid.outputs.session_id != ''
        id: rollup
        env:
          SESSION_ID: ${{ steps.sid.outputs.session_id }}
        run: node scripts/rollup-cost.mjs "$SESSION_ID" > rollup.md
      - name: Sticky-comment the rollup
        if: steps.sid.outputs.session_id != ''
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: agent-cost
          path: rollup.md
```

`scripts/rollup-cost.mjs` (reads NDJSON or queries the OTel backend; emit per-model breakdown):
```js
import { readFileSync } from "node:fs";
const sid = process.argv[2];
const rows = readFileSync(".agent/cost/runs.ndjson", "utf8")
  .trim().split("\n").map((l) => JSON.parse(l))
  .filter((r) => r.session_id === sid);
const byModel = new Map();
let total = 0, calls = rows.length;
for (const r of rows) {
  const m = byModel.get(r.model) ?? { in: 0, out: 0, cw: 0, cr: 0, usd: 0 };
  m.in  += r.input_tokens;       m.out += r.output_tokens;
  m.cw  += r.cache_creation_input_tokens; m.cr += r.cache_read_input_tokens;
  m.usd += r.cost_usd;
  byModel.set(r.model, m);
  total += r.cost_usd;
}
console.log(`### Agent cost: $${total.toFixed(4)} across ${calls} calls\n`);
console.log(`| Model | Calls | Input | Output | Cache write | Cache read | Cost |`);
console.log(`|---|--:|--:|--:|--:|--:|--:|`);
for (const [model, m] of byModel) {
  const n = rows.filter((r) => r.model === model).length;
  console.log(`| \`${model}\` | ${n} | ${m.in.toLocaleString()} | ${m.out.toLocaleString()} | ${m.cw.toLocaleString()} | ${m.cr.toLocaleString()} | $${m.usd.toFixed(4)} |`);
}
console.log(`\nSession id: \`${sid}\` — pivot to prompt history via the \`Agent-Run-Id\` trailer.`);
```

`AGENTS.md` section:
```markdown
## Agent Cost Telemetry

Every LLM call routed through `lib/agent-cost.ts` appends an NDJSON row to `.agent/cost/runs.ndjson` (gitignored) with `{run_id, session_id, agent, model, input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens, cost_usd, request_id, started_at, ended_at}`.

Pricing: `pricing/llm-pricing.json` — USD per 1M tokens, sourced from Anthropic and OpenAI rate cards. **Review quarterly** (last verified 2026-05-15).

Rollup: `.github/workflows/agent-cost-comment.yml` posts a sticky comment on every agent-labeled PR with total cost and per-model breakdown for that PR's session.

Budget alert: configured in <BACKEND> at threshold $X/day; pages `<oncall>` via PagerDuty.

### Pivoting from a spending spike to the offending session

1. Query `.agent/cost/runs.ndjson` or the OTel backend for the top session by `sum(cost_usd) group by session_id` in the spike window.
2. The session id matches the `Agent-Run-Id` trailer in the commit log — `git log --grep "Agent-Run-Id: <session_id>"` finds the resulting commits / PRs.
3. From there, pivot to the prompt history via the Agent Audit Trail (see that section for backend details).
```

**Bonus: Claude Code native cost export via OpenTelemetry**

`.env.example`:
```bash
# Claude Code cost telemetry (opt-in). Exports per-session cost and token counts
# to an OTLP backend that the team actually monitors.
CLAUDE_CODE_ENABLE_TELEMETRY=1
OTEL_METRICS_EXPORTER=otlp
OTEL_LOGS_EXPORTER=otlp
OTEL_EXPORTER_OTLP_PROTOCOL=grpc
OTEL_EXPORTER_OTLP_ENDPOINT=https://<your-collector>.example.com:4317
OTEL_SERVICE_NAME=<REPO_NAME>-claude-code
OTEL_METRIC_EXPORT_INTERVAL=60000
# Prompts and tool args are REDACTED by default. Only enable after privacy review:
# OTEL_LOG_USER_PROMPTS=0
# OTEL_LOG_TOOL_DETAILS=0
```

Metrics that land in the backend, labeled with `session.id`, `user.id`, `organization.id`, `model`:
- `claude_code.cost.usage` — USD per session (Counter)
- `claude_code.token.usage` — token counts split by `type=input|output|cacheRead|cacheCreation` (Counter)
- `claude_code.session.count` — sessions started (Counter)
- `claude_code.code_edit_tool.decision` — tool acceptance rate (Counter)

Grafana / Datadog query for "cost per PR" joins `claude_code.cost.usage{session_id=$SID}` with the PR's `Agent-Run-Id` trailer.

**Bonus: SessionEnd hook for local-only sessions**

For developers running Claude Code locally without an OTel backend, drop a hook in `.claude/settings.json` that captures the per-session cost summary to `~/.claude/logs/cost.ndjson`:
```json
{
  "hooks": {
    "SessionEnd": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "node ${CLAUDE_PROJECT_DIR}/scripts/session-end-cost.mjs"
      }]
    }]
  }
}
```

`scripts/session-end-cost.mjs` reads stdin (Claude Code provides the session payload), looks up `total_cost_usd`, `total_tokens_in`, `total_tokens_out`, `model`, and appends one summary row. Now every local session is accounted for without a remote backend.

## Why this matters

Cost incidents from unbounded agent runs have hit teams hard and fast in 2025-2026, and the common thread is "we had no per-session attribution":

- **The $47,000 multi-agent loop (November 2025)**: a four-agent research pipeline entered an infinite Analyzer ↔ Verifier conversation for 11 days. Costs went $127 → $891 → ~$6,200 → ~$40,000 week over week. A rolling per-session cost anomaly alert would have caught it on Day 4; nothing was wired.
- **The $607 Replit bill**: a developer left an agent running unattended for hours and discovered the charge after the fact — no per-session rollup, no budget alert, no way to attribute the spend until the invoice arrived.
- **The $437 overnight loop**: an autonomous summarization agent entered a recursive tool-call loop and made ~14,000 redundant requests on a single document set. The session was tagged in the application logs but no cost metric was exported, so the spend was invisible until billing.

In every case the fix is the same: per-call usage capture (with model id), a checked-in pricing table, a per-session/per-PR rollup, and a budget alert that pages a human. The signal is at L3 because L1-L2 cover "we know there are LLM calls happening"; L3 readiness assumes the agent is autonomous enough that an overnight runaway is plausible, and the repo must guarantee the spend is attributable before that night arrives.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, which artifact carries the cost figure (NDJSON row / OTel metric / PR comment), how you verified the pricing math (manual spot-check of one row vs the rate card), and where the per-session/per-PR rollup lands (file path, dashboard URL, or Slack channel)

## References

- OpenTelemetry GenAI semantic conventions — attribute registry (`gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.system`, `gen_ai.operation.name`, `gen_ai.token.type`): https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/
- OpenTelemetry GenAI metrics (`gen_ai.client.token.usage` histogram, split by token type): https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/
- OpenTelemetry GenAI client spans: https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/
- Inside the LLM Call: GenAI Observability with OpenTelemetry: https://opentelemetry.io/blog/2026/genai-observability/
- Claude Code monitoring & telemetry (`CLAUDE_CODE_ENABLE_TELEMETRY`, `claude_code.cost.usage`, `claude_code.token.usage`, session/user/model labels, redaction defaults): https://code.claude.com/docs/en/monitoring-usage
- Claude Code OpenTelemetry reference implementation (Cole Murray): https://github.com/ColeMurray/claude-code-otel
- Claude Code + OpenTelemetry per-session cost and token tracking (Bindplane): https://bindplane.com/blog/claude-code-opentelemetry-per-session-cost-and-token-tracking
- Claude Code Metrics Grafana dashboard: https://grafana.com/grafana/dashboards/24993-claude-code-metrics/
- Anthropic API pricing & prompt-caching rates (input / output / cache write 5m & 1h / cache read): https://platform.claude.com/docs/en/about-claude/pricing
- Anthropic Messages API — `usage` object fields (`input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`) and `request-id` header: https://docs.anthropic.com/en/api/overview
- OpenAI API pricing: https://openai.com/api/pricing/
- Vercel AI SDK — `onFinish` callback usage capture for `streamText` / `generateText`: https://ai-sdk.dev/cookbook/rsc/stream-ui-record-token-usage
- Vercel AI SDK — known issue: `onFinish` does not fire on aborted streams: https://github.com/vercel/ai/issues/7805
- Helicone — LLM cost-tracking proxy: https://www.helicone.ai/blog/the-complete-guide-to-LLM-observability-platforms
- Langfuse OpenTelemetry integration (OTLP `/api/public/otel` endpoint, session/cost grouping): https://langfuse.com/integrations/native/opentelemetry
- Real incident: the $47,000 multi-agent loop (Nov 2025): https://techstartups.com/2025/11/14/ai-agents-horror-stories-how-a-47000-failure-exposed-the-hype-and-hidden-risks-of-multi-agent-systems/
- Real incident: the $607 Replit agent bill: https://blog.vibecoder.me/607-replit-bill-avoiding-runaway-ai-costs
- Real incident: the $437 overnight recursive-loop bill: https://earezki.com/ai-news/2026-04-29-i-let-my-ai-agent-run-overnight-it-cost-437/
</system-reminder>
