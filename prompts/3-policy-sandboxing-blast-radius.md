[Readiness Fix] <REPO_NAME> Sandboxing / Blast-Radius Bounds

Fix the failing signal: Sandboxing / Blast-Radius Bounds ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Sandboxing / Blast-Radius Bounds
**Score**: [0/1]
**Description**: Agent runs in a constrained environment with limited filesystem and network access, so a mistake or prompt injection cannot reach production credentials, the host filesystem, or arbitrary internet destinations
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Sandboxing / blast-radius bounds — check for a checked-in mechanism that confines the agent's bash/tool execution to a bounded filesystem and network reachability set. The mechanism MUST be enforced at the OS/runtime layer, not at the prompt/policy layer alone. PASS requires at least one of the following, with concrete bounds (not just an empty config block):

1. **Claude Code OS sandbox**: `.claude/settings.json` with a `sandbox` block containing `"enabled": true` AND a populated `network.allowedDomains` array (default-deny egress, explicit allowlist). On Linux the sandbox uses user namespaces + nftables; on macOS it uses `sandbox-exec` profiles. A bare `{"sandbox": {"enabled": true}}` with no `network.allowedDomains` is a FAIL — egress is unbounded. A `dangerouslyDisableSandbox: true` anywhere in the merged settings is a FAIL.
2. **Devcontainer with restricted mounts and network egress allowlist**: `.devcontainer/devcontainer.json` (or `.devcontainer.json`) that (a) does NOT bind-mount the host home directory, SSH socket, or Docker socket, (b) declares explicit `mounts` rather than relying on default workspace mount only, AND (c) ships an `init-firewall.sh` (or equivalent iptables/nftables script) that drops outbound traffic by default and resolves a finite allowlist (npm registry, GitHub API, Anthropic/model endpoints). `runArgs` should include `--cap-drop=ALL` plus selective `--cap-add=NET_ADMIN,NET_RAW` only for the firewall init, and `--security-opt=no-new-privileges`. A devcontainer that runs `--privileged`, mounts `/var/run/docker.sock`, or bind-mounts `${HOME}` is a FAIL — it has no meaningful blast radius bound.
3. **CI agent-runner sandbox**: For agents that run in GitHub Actions / GitLab CI, a `step-security/harden-runner@v2` step at the top of every job that calls the agent, with `egress-policy: block` AND a non-empty `allowed-endpoints` list. `egress-policy: audit` alone is monitoring, not enforcement — FAIL. The harden-runner step must come BEFORE `actions/checkout` so the policy is in place before any third-party code executes.
4. **Microvm / external sandbox runtime**: agent invocation routed through a documented sandbox runtime — Vercel Sandbox (`sandbox.run({...})`), E2B (`Sandbox.create()`), Daytona workspace, gVisor `runsc`, Firecracker VM, or Anthropic's Claude Agent SDK with `sandbox: true` and explicit `allowedHosts`. The repo must contain code or workflow YAML that actually invokes the sandbox — a README mention does not count.

Also verify the sandbox config is actually loaded by the agent runtime. For Claude Code, `sandbox` must live at one of the documented paths (`~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, or enterprise managed) and pass `/config` validation; a `sandbox` block buried in another JSON file is dead config. For devcontainers, the firewall script must be invoked from `postCreateCommand` or `postStartCommand` — a script that exists but is never executed is a FAIL.

A README sentence saying "we recommend running the agent in a container" is documentation, not enforcement, and FAILs this signal. So does a CI workflow whose only sandbox claim is `runs-on: ubuntu-latest` — a GitHub-hosted runner is multi-tenant compute, not an agent sandbox.

## Your Task

1. Explore the repository to understand the current state related to this signal — list every `.claude/settings*.json` (check the `sandbox` block), `.devcontainer/` directory (note `runArgs`, `mounts`, `postCreateCommand`, and any `init-firewall.sh`), every `.github/workflows/*.yml` (search for `step-security/harden-runner`), and any sandbox-runtime invocations (`@vercel/sandbox`, `@e2b/sdk`, `daytona`, `runsc`, `firecracker`). Note which agent runtimes the repo actually targets (Claude Code, Factory droid, Cursor, Copilot, custom Agent SDK).
2. Make **substantive improvements** by adding real, project-tuned enforcement:
   - For a repo that runs Claude Code locally, add a `sandbox` block to `.claude/settings.json` with `enabled: true`, `autoAllowBashIfSandboxed: false` (or `true` only after confirming the deny rules are tight), and a `network.allowedDomains` array enumerating the exact hosts the project's build/test chain reaches (registry, source-control, CDN, model API). Verify with `/config` in Claude Code that the Sandbox tab shows your domains.
   - For a repo where contributors use a devcontainer, harden `.devcontainer/devcontainer.json`: add `runArgs: ["--cap-drop=ALL", "--cap-add=NET_ADMIN", "--cap-add=NET_RAW", "--security-opt=no-new-privileges"]`, remove any bind mount of the host home directory or Docker socket, and ship an `init-firewall.sh` modeled on the `anthropics/claude-code` reference container (default-DROP `OUTPUT` chain, then resolve a finite allowlist and `ACCEPT` those IPs). Wire it via `postStartCommand`.
   - For agents that run in CI, prepend `step-security/harden-runner@v2` (with `egress-policy: block` and an `allowed-endpoints` list derived from a prior audit-mode run) to every job that invokes the agent. Pin the action by full commit SHA.
   - If the agent runs in an ephemeral microvm (Vercel Sandbox, E2B, Daytona), wire the invocation into the actual entry script — not a doc snippet.
3. Verify the bound is enforced, not just configured:
   - Claude Code: from inside an agent session, run `curl https://example.com` (or any non-allowlisted host) and confirm it fails. Run `cat /etc/passwd` from a sandboxed Bash and confirm only the sandbox's view is returned.
   - Devcontainer: after rebuild, exec into the container and run the same two checks. The firewall script's own self-test (the reference script tries `https://example.com` and expects failure) MUST pass.
   - CI harden-runner: trigger a workflow run; in the StepSecurity Insights tab confirm `egress-policy: block` is active and that any deliberate disallowed call is recorded as Blocked.
4. Keep changes focused on this signal — do not refactor the build, swap base images, or add unrelated permissions rules.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** `"sandbox": {"enabled": true}` with no `network.allowedDomains` — the sandbox is up but egress is wide open, which is strictly worse than no sandbox because the team will believe they are protected.
- **NO** `"sandbox": {"enabled": true, "network": {"allowedDomains": ["*"]}}` or `["*.com"]` — wildcard everything defeats the bound. (`*.example.com` is a legitimate suffix wildcard; `*` alone or `*.com` is gaming the metric.)
- **NO** `dangerouslyDisableSandbox: true` or `allowUnsandboxedCommands: true` paired with `enabled: true` — the escape hatch nullifies the boundary.
- **NO** committing `bypassPermissions` mode as the default permission mode while claiming the sandbox compensates — `bypassPermissions` disables the prompts the sandbox relies on for the unsandboxable commands.
- **NO** devcontainer with `runArgs: ["--privileged"]`, `--network=host`, `--pid=host`, or a bind mount of `/var/run/docker.sock`, `${HOME}`, `${HOME}/.ssh`, or `${HOME}/.aws` — any one of these gives the container host-level reach and the "sandbox" is theater.
- **NO** `init-firewall.sh` that exists in the repo but is not invoked from `postCreateCommand` / `postStartCommand` / `ENTRYPOINT` — orphan scripts do nothing. Run `grep -r init-firewall` and verify it's wired.
- **NO** `step-security/harden-runner` step with `egress-policy: audit` while claiming block-mode enforcement. Audit logs; it does not block.
- **NO** harden-runner step placed AFTER `actions/checkout` or after `npm install` / `pip install` — every step before harden-runner runs with unrestricted egress, which is the exact window a poisoned dependency exploits.
- **NO** `allowed-endpoints` list that includes `*.com`, `0.0.0.0:443`, or every public CDN under the sun — derive the list from an actual audit-mode run of the workflow, not from copy/paste.
- **NO** documenting the sandbox in `SECURITY.md` ("agents must run in a devcontainer") with no enforcement file. Prose is unenforceable.
- **NO** copy-pasting a generic devcontainer from a template without removing the parts the repo doesn't use. A Python repo whose firewall allowlists `registry.npmjs.org` and not `pypi.org` is a stub.

Examples of BAD fixes:
- `.claude/settings.json` containing `{"sandbox": {"enabled": true, "autoAllowBashIfSandboxed": true}}` and nothing else — `autoAllowBashIfSandboxed: true` is the default; with no `network.allowedDomains` the sandbox lets every domain through. You have suppressed the bash prompt and added zero network bound.
- A `.devcontainer/devcontainer.json` whose `runArgs` includes `--cap-drop=ALL` but whose `mounts` line is `"source=${env:HOME}/.ssh,target=/home/node/.ssh,type=bind"` — the agent can read the user's private keys, sign as them, and push to any repo. Cap-drop is irrelevant against a credential leak.
- An `init-firewall.sh` that runs `iptables -P OUTPUT DROP` then `iptables -A OUTPUT -j ACCEPT` two lines later — the second rule re-allows everything. Test the script (the Anthropic reference includes a `curl https://example.com` self-test that MUST fail at the end).
- `step-security/harden-runner@v2` added to a CI job with `allowed-endpoints: > github.com:443 api.github.com:443` and nothing else, while the job's `npm install` step pulls from `registry.npmjs.org` — the install will fail and someone will quietly switch the policy to `audit`. Derive the allowlist from a real audit-mode run.
- Adding `runArgs: ["--network=host"]` to "make the dev experience easier" — `--network=host` defeats every other network control. The container shares the host's network namespace, so firewall rules inside the container do nothing.

Examples of GOOD fixes:

- For a TypeScript/Node repo using Claude Code locally — add to `.claude/settings.json`:
  ```json
  {
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "sandbox": {
      "enabled": true,
      "autoAllowBashIfSandboxed": false,
      "allowUnsandboxedCommands": false,
      "excludedCommands": [],
      "filesystem": {
        "denyRead": ["~/.ssh", "~/.aws", "~/.config/gh", "~/.npmrc"],
        "denyWrite": ["~/", "/etc", "/usr"]
      },
      "network": {
        "allowLocalBinding": false,
        "allowAllUnixSockets": false,
        "allowedDomains": [
          "api.anthropic.com",
          "registry.npmjs.org",
          "*.npmjs.org",
          "github.com",
          "api.github.com",
          "objects.githubusercontent.com",
          "raw.githubusercontent.com"
        ]
      }
    }
  }
  ```

- For a repo whose contributors use a devcontainer — add `.devcontainer/devcontainer.json`:
  ```json
  {
    "name": "<REPO_NAME> agent sandbox",
    "image": "mcr.microsoft.com/devcontainers/typescript-node:20",
    "runArgs": [
      "--cap-drop=ALL",
      "--cap-add=NET_ADMIN",
      "--cap-add=NET_RAW",
      "--security-opt=no-new-privileges"
    ],
    "mounts": [
      "source=${localWorkspaceFolderBasename}-node-modules,target=${containerWorkspaceFolder}/node_modules,type=volume",
      "source=claude-code-config,target=/home/node/.claude,type=volume"
    ],
    "containerEnv": {
      "GIT_TERMINAL_PROMPT": "0",
      "SSH_AUTH_SOCK": ""
    },
    "remoteUser": "node",
    "postStartCommand": "sudo /usr/local/bin/init-firewall.sh"
  }
  ```
  Paired with `.devcontainer/init-firewall.sh` modeled on the `anthropics/claude-code` reference (default-DROP `OUTPUT`, resolve allowed domains via `dig`, `ACCEPT` those IPs, end with a `curl https://example.com` self-test that MUST fail).

- For a GitHub Actions workflow that runs the agent in CI — top of every job:
  ```yaml
  steps:
    - name: Harden runner
      uses: step-security/harden-runner@0634a2670c59f64b4a01f0f96f84700a4088b9f0  # v2.10.3
      with:
        egress-policy: block
        disable-sudo: true
        allowed-endpoints: >
          api.github.com:443
          github.com:443
          objects.githubusercontent.com:443
          registry.npmjs.org:443
          api.anthropic.com:443

    - uses: actions/checkout@v4
    # ... rest of job
  ```
  Derive the `allowed-endpoints` list by first running the workflow with `egress-policy: audit` and copying from the Recommended Policy tab on the StepSecurity Insights page.

- For agents launched via the Claude Agent SDK or Vercel Sandbox — wire the invocation into the entry script, e.g.:
  ```ts
  import { Sandbox } from '@vercel/sandbox';

  const sandbox = await Sandbox.create({
    timeout: 10 * 60 * 1000,
    resources: { vcpus: 2 },
    runtime: 'node22',
  });
  await sandbox.runCommand({ cmd: 'pnpm', args: ['test'] });
  await sandbox.stop();
  ```
  The microVM ends with the session — no persistent blast radius.

## Why this matters

Unsandboxed agents have caused production damage that a 5-line config change would have prevented:

- **Replit agent (July 2025)** deleted a production database containing 1,200+ executive records mid-session — the agent had direct network reach to the prod DSN with no egress allowlist between it and the database.
- **Amazon Kiro agent** destroyed an AWS Cost Explorer environment during what should have been a read-only analysis, causing a 13-hour outage. The agent ran with the developer's full AWS credentials and no network bound separating "read prod metrics" from "delete prod resources."
- **Invariant Labs (May 2025)** demonstrated GitHub MCP prompt-injection: a poisoned GitHub issue caused an agent to read a private repository and post its contents to a public issue. A network egress allowlist that excluded `api.github.com` writes (or scoped to read-only endpoints) would have blocked the exfiltration even after the prompt-level guardrails failed.
- **`shai-hulud` npm supply-chain worm (Sep 2025, 500+ packages)**: malicious post-install scripts ran during `npm install` and exfiltrated developer secrets. Repos with `step-security/harden-runner` in `egress-policy: block` mode at the top of their CI jobs reported zero exfiltration — the worm's outbound calls hit the deny list and failed.
- **`tj-actions/changed-files` compromise (March 2025)**: thousands of repos ran a poisoned action that dumped CI secrets to job logs. Again, harden-runner customers in block mode saw the exfil attempts blocked at the network layer.

The pattern is consistent: prompt-level guardrails ("don't touch prod", "only call approved tools") live in the model's context and a sufficiently capable adversary — including the model itself reasoning around them — bypasses them. The only deterministic boundary is one the OS or runtime enforces, where the agent's syscall or network connect actually fails. That is what this signal measures.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Claude Code Sandboxing (modes, filesystem, network): https://code.claude.com/docs/en/sandboxing
- Claude Code settings.json sandbox reference (full schema): https://code.claude.com/docs/en/settings#sandbox-settings
- Claude Code permissions × sandbox interaction (defense-in-depth model): https://docs.anthropic.com/en/docs/claude-code/permissions
- Claude Code development containers (reference devcontainer + init-firewall.sh): https://code.claude.com/docs/en/devcontainer
- Anthropic reference `init-firewall.sh` (canonical default-deny + allowlist + self-test): https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh
- Dev Container metadata reference (`runArgs`, `mounts`, `postStartCommand`): https://containers.dev/implementors/json_reference
- StepSecurity Harden-Runner (egress block mode, allowed-endpoints, Policy Store): https://docs.stepsecurity.io/github-actions/harden-runner
- StepSecurity guide — fixing a blocked endpoint (audit-then-block workflow): https://docs.stepsecurity.io/guides/how-to-fix-a-blocked-endpoint-in-your-workflow
- Factory droid sandboxing recommendations (containers/VMs, environment-aware policy): https://docs.factory.ai/enterprise/llm-safety-and-agent-controls
- Factory droid security model (built-in protections vs. OS isolation gap): https://docs.factory.ai/cli/account/security
- Independent analysis of droid sandbox gaps (agent-enforced ≠ OS-enforced): https://www.agent-safehouse.dev/docs/agent-investigations/droid
- HMCTS reference agent devcontainer (cap-drop + seccomp + AppArmor + iptables): https://github.com/hmcts/ai-agent-devcontainer-example
- Community-built sandboxed coding-agent container (iptables default-deny pattern): https://mfyz.com/ai-coding-agent-sandbox-container/
- Real-world failures and supply-chain incidents (Replit, Kiro, Invariant, shai-hulud, tj-actions): https://policylayer.com/mcp-security
</system-reminder>