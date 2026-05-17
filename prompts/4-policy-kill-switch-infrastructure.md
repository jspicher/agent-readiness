[Readiness Fix] <REPO_NAME> Kill-Switch Infrastructure

Fix the failing signal: Kill-Switch Infrastructure ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Kill-Switch Infrastructure
**Score**: [0/1]
**Description**: Mechanism to halt agent activity quickly when an agent is misbehaving, leaking data, or producing damage faster than humans can intervene through normal channels
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Kill-switch infrastructure — check for a checked-in mechanism that lets a human stop agent activity within minutes, without filing a PR, waiting on a deploy, or asking the agent to please stop. The mechanism MUST be enforceable from outside the agent's process (the agent cannot opt out of it) and MUST stop in-flight work, not just refuse new work. PASS requires at least one of the following, with concrete wiring (not just a doc page):

1. **Feature-flag gate at the agent invocation entry point** — a checked-in flag in a managed flag system (LaunchDarkly, Statsig, Unleash, GrowthBook, ConfigCat, Flagsmith, OpenFeature provider) named explicitly for agents (e.g. `agent_runs_enabled`, `agent_<name>_enabled`, `agents_killswitch`) that is evaluated BEFORE any LLM call, tool dispatch, or workflow step. The flag MUST default to "halt" on evaluation error/SDK timeout (fail-closed), and the evaluation MUST live at the entry point a human-attacker-bypass cannot skip (CI workflow guard or service-side gate — not "check a flag inside the prompt"). A flag named `new_dashboard_enabled` repurposed as the kill switch FAILs — operators won't find it under pressure.
2. **CI / repo-level circuit breaker** — `.github/workflows/agent.yml` (or equivalent) protected by a GitHub Environment with required reviewers AND a manual `workflow_dispatch` trigger, plus a top-level `concurrency: { group: agent-runs, cancel-in-progress: true }` so flipping the environment to "no approvers" both blocks new runs and lets an operator cancel in-flight runs by pushing a no-op dispatch. Branch protection on `main` requiring CODEOWNERS approval on agent-authored PRs counts as a secondary lane; it does NOT count alone because it only stops merges, not the agent's other side effects (issue comments, deploys, API writes).
3. **API-credential revocation runbook** — a one-command script (committed in `scripts/`, `Makefile`, `justfile`, or `.github/workflows/`) that revokes the agent's GitHub App installation token, OAuth grant, or Anthropic API key — e.g. `gh auth revoke`, `gh api -X DELETE /installation/token`, or a `curl` call to the Anthropic Console key endpoint paired with a documented manual step at `console.anthropic.com/settings/keys`. The runbook MUST live in `docs/runbooks/agent-killswitch.md` (or `SECURITY.md`) with the exact command, the on-call owner, and the expected propagation time. "Rotate the key" as prose is not a runbook.
4. **External sandbox session abort** — for agents that run in an ephemeral runtime (Vercel Sandbox, E2B, Daytona, Modal, Fly Machines), a documented `sandbox.stop()` / `Sandbox.kill(id)` / `flyctl machine stop` endpoint wired to a tagged identifier (e.g. all agent sessions launched with `metadata: { agent: true }`) so a single command terminates every live agent VM. The runbook MUST include the query that lists active agent sessions.

Also verify the switch actually halts work, not just future work:

- The flag check must run at every iteration of the agent loop, not once at boot. An agent that read `agent_runs_enabled` at startup and cached it for the next 4 hours has no kill switch.
- The CI concurrency cancel must be tested — push a no-op `workflow_dispatch` while a run is mid-flight and confirm GitHub cancels the prior run within seconds.
- The credential revocation must be verified end-to-end: revoke in a test env, then attempt a tool call and confirm the agent's next API request returns 401 within one polling interval.

A kill switch that the agent itself must voluntarily check (inside a prompt, in `CLAUDE.md`, as an `AGENTS.md` rule) is not a switch — it is a request. A sufficiently misbehaving or prompt-injected agent ignores it. The boundary must live where the agent's process cannot edit it: the runtime, the network, the credential, or the CI gate.

A README sentence saying "to stop the agent, contact the platform team" is not a kill switch and FAILs this signal. So does a Datadog dashboard with a "Pause Agent" button that posts to an endpoint nobody has wired up.

## Your Task

1. Explore the repository to understand the current state related to this signal — list every agent entry point (`.github/workflows/*.yml` jobs that run Claude Code / Factory droid / Cursor agent / custom Agent SDK, any `scripts/agent-*.sh`, any Node/Python service that calls `@anthropic-ai/sdk` or `anthropic` in a long-running loop), every feature-flag SDK already imported (`grep -r "launchdarkly\|statsig\|unleash\|growthbook\|configcat\|openfeature"`), and every `.github/environments/*` or environment-protection-rules reference. Note where the agent's credentials live (`ANTHROPIC_API_KEY`, GitHub App private key, OAuth client) so you know what a revocation runbook must target.
2. Make **substantive improvements** by wiring a real kill switch the operator can hit in under five minutes:
   - **Add a fail-closed flag check at the agent entry point.** Pick the flag SDK the repo already uses (or add OpenFeature with an in-process file-backed provider if none exists). Evaluate `agent_runs_enabled` at the top of the invocation, with `defaultValue: false` and a hard exit on SDK error. The check goes in the loop, not just at boot.
   - **Add a GitHub Environment + concurrency guard to the agent workflow.** Create an `agent-runs` environment with required reviewers, wire every agent job to `environment: agent-runs`, and add `concurrency: { group: agent-runs, cancel-in-progress: true }` at the workflow level. Document that removing the approver list halts new runs and pushing a no-op `workflow_dispatch` cancels in-flight runs.
   - **Commit a one-command revocation script.** Add `scripts/kill-agent.sh` (or `.github/workflows/kill-agent.yml` with `workflow_dispatch`) that (a) flips the LaunchDarkly/Statsig flag to off via the management API, (b) revokes the GitHub App installation token via `gh api -X DELETE /app/installations/<id>/access_tokens`, and (c) prints the manual link for Anthropic key revocation. Add it to `docs/runbooks/agent-killswitch.md` with the on-call owner and expected propagation time per step.
   - **If the agent runs in an ephemeral sandbox**, add `scripts/kill-agent-sandboxes.sh` that lists every active sandbox tagged `agent=true` and stops them in parallel.
3. Verify the switch genuinely halts work:
   - Flip the flag to `false` in your flag system's UI and confirm the next agent iteration exits with the expected log line within one evaluation interval (default: 30s for LaunchDarkly streaming, 60s for Statsig polling).
   - Trigger the `kill-agent` workflow against a test agent run and confirm GitHub cancels the in-flight job within 10s (check the run timeline for "cancelled" status).
   - Revoke the test installation token and confirm the agent's next `gh api` call returns 401, with the agent process exiting (not retrying in a loop).
4. Keep changes focused on this signal — do not refactor permissions, sandboxing, or unrelated CI plumbing.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** flag check that runs inside the model's prompt or in an `AGENTS.md` rule — the agent reads its own context and reasons around (or is prompt-injected past) such a rule. The check must live in the host process, evaluated before the LLM call.
- **NO** flag check that runs once at boot and is cached for the session — an in-flight agent that started at 09:00 will keep running with the old value all afternoon. Evaluate on every tool dispatch or every loop iteration.
- **NO** fail-open flag default. `defaultValue: true` (or `await client.getBooleanValue('agent_runs_enabled', true)`) means an SDK timeout / managed-flag outage silently re-enables the agent. Default MUST be `false`; on SDK error the entry point MUST exit, not proceed.
- **NO** kill switch that lives on a Datadog/Grafana dashboard with no on-call rotation watching it. If nobody is paged when it trips (or when somebody flips it), the lag between misbehavior and response is hours.
- **NO** kill switch that requires a deploy, a `terraform apply`, a `kubectl rollout`, or a PR merge to take effect — by the time CI runs, the agent has done another 20 turns. Propagation MUST be under 5 minutes end-to-end.
- **NO** GitHub Environment with reviewer protection but no `concurrency: cancel-in-progress: true` — removing reviewers blocks the next run but lets the current 45-minute run finish. That window is exactly when damage compounds.
- **NO** "kill switch" that only blocks new agent PRs from merging — the Replit incident was destructive API calls during a single session, not a series of PRs. Branch protection alone is a stale-data control, not a kill switch.
- **NO** credential rotation that takes effect at the next deploy (because the key is baked into a container image or a Vercel env var that requires a redeploy to refresh). Revocation MUST invalidate the live credential, not the future one.
- **NO** documentation-only "runbook" with no script. "Run the appropriate command to revoke the token" is not a runbook; the exact command, copy-pasteable, is.
- **NO** flag named `feature_x_v2` or `enable_new_sdk` repurposed as the kill switch — under pressure an on-call engineer searches for `agent`, `killswitch`, `pause`, `disable`. Name it for what it does.

Examples of BAD fixes:

- Adding to `CLAUDE.md`: "If the file `.agent-disabled` exists, stop work." — the agent reads `CLAUDE.md`, decides whether to comply, and a prompt-injected agent ignores it. Not enforceable.
- A LaunchDarkly flag `agent_runs_enabled` checked once in `main()`:
  ```ts
  const enabled = await ldClient.boolVariation('agent_runs_enabled', user, true); // BAD: defaults true, checked once
  if (!enabled) process.exit(0);
  while (true) { await agentLoop(); } // never re-checks
  ```
  This stops only future processes. A 4-hour-long agent run started before the flip continues unimpeded, and an SDK timeout silently keeps it running.
- A `.github/workflows/agent.yml` with `environment: production` and required reviewers but no `concurrency` block — removing approvers blocks the NEXT manual dispatch but the cron-scheduled run that started 12 minutes ago is unaffected.
- A `docs/agent-killswitch.md` that reads "To halt the agent, contact @platform-oncall on Slack and they will rotate the API key." — no command, no link, no expected propagation time, no test of the path.
- A `scripts/kill-agent.sh` that runs `git revert HEAD && git push` to "undo what the agent did" — that is remediation, not a kill switch. The agent process is still running and will react to the revert.
- A "circuit breaker" implemented as a Datadog Synthetic that alerts when agent error rate exceeds a threshold, with no automatic action — alerts are detection, not intervention.

Examples of GOOD fixes:

- **Fail-closed flag check at the agent loop (TypeScript, OpenFeature + LaunchDarkly provider):**
  ```ts
  // src/agent/killswitch.ts
  import { OpenFeature, EvaluationContext } from '@openfeature/server-sdk';

  const KILL_TIMEOUT_MS = 2000;
  const client = OpenFeature.getClient('agent-runner');

  export async function assertAgentEnabled(ctx: EvaluationContext): Promise<void> {
    const result = await Promise.race([
      client.getBooleanDetails('agent_runs_enabled', false, ctx),
      new Promise<{ value: false }>(r => setTimeout(() => r({ value: false }), KILL_TIMEOUT_MS)),
    ]);
    if (!result.value) {
      console.error('[killswitch] agent_runs_enabled=false — halting');
      process.exit(2);
    }
  }

  // src/agent/loop.ts
  while (true) {
    await assertAgentEnabled({ targetingKey: runId, repo: process.env.GITHUB_REPOSITORY });
    const turn = await runOneTurn();
    if (turn.done) break;
  }
  ```
  Default is `false`. The race with a 2-second timeout means a LaunchDarkly outage halts the agent rather than freezing it or proceeding. The flag is checked every turn.

- **CI workflow with environment + concurrency + manual dispatch kill (GitHub Actions YAML):**
  ```yaml
  # .github/workflows/agent.yml
  name: Agent run
  on:
    workflow_dispatch:
    schedule: [{ cron: '0 * * * *' }]

  concurrency:
    group: agent-runs
    cancel-in-progress: true   # pushing a no-op dispatch cancels the live run

  jobs:
    run:
      runs-on: ubuntu-latest
      environment: agent-runs   # required reviewers; remove all → halt new runs
      timeout-minutes: 30       # belt-and-suspenders hard ceiling
      steps:
        - uses: actions/checkout@v4
        - run: ./scripts/run-agent.sh
  ```
  Operator playbook:
  1. **Halt new runs:** Settings → Environments → `agent-runs` → remove every required reviewer. New runs block at "Waiting for approval" indefinitely.
  2. **Cancel in-flight run:** Actions → Agent run → "Run workflow" with a `noop=true` input → concurrency-cancel kills the prior run within seconds.

- **One-command revocation script with documented owner and propagation:**
  ```bash
  # scripts/kill-agent.sh
  #!/usr/bin/env bash
  set -euo pipefail

  : "${LD_API_TOKEN:?missing}"
  : "${LD_PROJECT:?missing}"
  : "${GH_APP_INSTALLATION_ID:?missing}"

  echo "[1/3] Flipping LaunchDarkly agent_runs_enabled → false (propagates ~30s via streaming)"
  curl -fsS -X PATCH \
    -H "Authorization: $LD_API_TOKEN" \
    -H "Content-Type: application/json" \
    "https://app.launchdarkly.com/api/v2/flags/$LD_PROJECT/agent_runs_enabled" \
    -d '[{"op":"replace","path":"/environments/production/on","value":false}]'

  echo "[2/3] Revoking GitHub App installation token (immediate)"
  gh api -X DELETE "/installation/token" \
    -H "Authorization: Bearer $(./scripts/mint-app-jwt.sh)"

  echo "[3/3] Anthropic API key — open the console and click Revoke"
  echo "      https://console.anthropic.com/settings/keys"
  echo "      Look for keys tagged 'agent-runner'. Revocation is immediate."
  ```
  Paired with `docs/runbooks/agent-killswitch.md`:
  ```
  # Agent kill switch
  On-call: @platform-oncall (PagerDuty schedule: AGENT-SRE)
  Expected propagation:
    - LaunchDarkly flag → 30s (streaming SDK) / 60s (polling SDK)
    - GitHub installation token → immediate (next API call returns 401)
    - Anthropic key revoke → immediate
  Test cadence: monthly game-day, last Friday, drill at 14:00 UTC.
  ```

- **Sandbox session abort (Vercel Sandbox example):**
  ```ts
  // scripts/kill-agent-sandboxes.ts
  import { Sandbox } from '@vercel/sandbox';
  const live = await Sandbox.list({ filter: { metadata: { agent: 'true' } } });
  console.log(`Found ${live.length} live agent sandboxes`);
  await Promise.all(live.map(s => Sandbox.stop({ sandboxId: s.id })));
  ```
  Runnable as `npx tsx scripts/kill-agent-sandboxes.ts`. Every agent launch must tag `metadata: { agent: 'true' }` so this query is exhaustive.

## Why this matters

Slow kill switches turned recoverable incidents into hours-long outages:

- **Replit agent (July 2025)** continued issuing destructive database operations for an extended window AFTER the team noticed and asked it to stop, ultimately deleting 1,200+ executive records. There was no out-of-band command to terminate the running session — the team had to wait for the next natural stopping point. A flag check evaluated each turn against a fail-closed `agent_runs_enabled` would have halted the loop on the next iteration.
- **Amazon Kiro agent** destroyed an AWS Cost Explorer environment in a 13-hour outage. Significant time was spent locating the right credential to revoke and the right service to restart; a checked-in `scripts/kill-agent.sh` with a documented on-call owner converts a 13-hour scramble into a 5-minute runbook execution.
- **Invariant Labs GitHub MCP prompt injection (May 2025)** showed an agent exfiltrating a private repo to a public issue. Even after detection, the exfiltration window is the lag between "operator notices" and "agent's credential stops working." A `gh api -X DELETE /installation/token` script measured in seconds is the difference between one leaked file and dozens.
- **Generic in-flight failures**: agents looping on a flaky tool, agents spending tokens on hallucinated work, agents that hit a billing-runaway condition. All resolve in minutes with a per-iteration flag check; all bleed for hours without one.

The pattern: detection latency is usually small; intervention latency is what kills you. A kill switch that takes 30 minutes to propagate (because it requires a deploy, a PR merge, or paging someone who pages someone else) is functionally absent during the window that matters. The signal is whether a single operator can stop a misbehaving agent within five minutes, from outside the agent's process, without the agent's cooperation.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- OpenFeature server SDK (provider-agnostic flag evaluation, fail-closed defaults): https://openfeature.dev/docs/reference/concepts/evaluation-api
- LaunchDarkly Node SDK — streaming evaluation & default values on SDK error: https://launchdarkly.com/docs/sdk/server-side/node-js
- LaunchDarkly REST API — patch flag environment state (used by `scripts/kill-agent.sh`): https://launchdarkly.com/docs/api/feature-flags/patch-feature-flag
- Statsig server SDK (polling interval, fail-open vs fail-closed configuration): https://docs.statsig.com/server/nodejsServerSDK
- Unleash kill-switch pattern documentation (operational toggle category): https://docs.getunleash.io/topics/feature-flags/toggle-configuration
- GrowthBook Node SDK & API-driven flag updates: https://docs.growthbook.io/lib/node
- GitHub Actions — using environments with required reviewers (gating + deployment hold): https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments
- GitHub Actions concurrency (`cancel-in-progress: true` for kill-via-dispatch): https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs
- GitHub Apps — delete an installation access token (immediate revocation): https://docs.github.com/en/rest/apps/installations
- `gh auth` (CLI revocation of stored tokens): https://cli.github.com/manual/gh_auth
- Anthropic Console API key management (revoke endpoint, console URL): https://console.anthropic.com/settings/keys
- Vercel Sandbox lifecycle (`Sandbox.stop`, listing live sessions by metadata): https://vercel.com/docs/vercel-sandbox
- E2B Sandbox lifecycle (`Sandbox.kill`, batch termination): https://e2b.dev/docs/sandbox/api/lifecycle
- StepSecurity guidance on agent runtime kill-switch patterns (CI-layer halt): https://www.stepsecurity.io/blog/securing-ai-agents-in-ci
- Real-world failures (Replit, Kiro, Invariant Labs) and intervention-latency analysis: https://policylayer.com/mcp-security
</system-reminder>
