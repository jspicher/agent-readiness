[Readiness Fix] <REPO_NAME> Tool Allowlist / Permission Policy

Fix the failing signal: Tool Allowlist / Permission Policy ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Tool Allowlist / Permission Policy
**Score**: [0/1]
**Description**: Documented or enforced list of CLIs, APIs, and destinations the agent may use, with destructive operations gated by deny rules or human approval
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Tool allowlist / permission policy – check for a checked-in, machine-readable policy that bounds what the coding agent may execute. PASS requires at least one of the following, with concrete allow AND deny entries (not just empty arrays or wildcards):

1. **Claude Code**: `.claude/settings.json` (or `.claude/settings.local.json`) with a `permissions` block containing at minimum a non-empty `deny` array. Look for rule syntax like `Bash(npm run test *)`, `Read(./.env)`, `WebFetch`, `mcp__<server>__<tool>`. A bare `"permissions": {}` or `"allow": ["*"]` is a FAIL. Deny rules MUST cover credential reads (`Read(./.env)`, `Read(./.env.*)`, `Read(./secrets/**)`) and destructive shell patterns relevant to the stack (e.g. `Bash(rm -rf *)`, `Bash(curl * | sh)`, `Bash(git push --force *)`).
2. **Factory droid**: `.factory/settings.json` with non-empty `commandAllowlist` and `commandDenylist` arrays. `commandAllowlist` should enumerate low-risk utilities the repo actually uses (e.g. `["npm *", "pnpm *", "make *", "git status", "git diff *"]`); `commandDenylist` MUST include destructive patterns (`rm -rf /`, `sudo *`, `mkfs *`, `git push --force *`). Note: Factory does not ship a `policy.json` file — settings live in `.factory/settings.json` (project) and `~/.factory/settings.json` (user). An enterprise-managed policy alone (server-side) is not visible in the repo and does not count for this signal.
3. **MCP scope manifest**: a checked-in document (e.g. `AGENTS.md`, `docs/agent-policy.md`, `.mcp/allowlist.yaml`) that names every MCP server the agent is permitted to call and the specific tools within each server (least-privilege per role). A bare `.mcp.json` that registers servers is NOT sufficient on its own — registration ≠ policy.
4. **CI / sandbox enforcement**: a network egress allowlist (Dockerfile `--network`, k8s `NetworkPolicy`, GitHub Actions `egress-policy: block` via step-security/harden-runner) AND a documented list of permitted destinations. This counts when (1) and (2) are absent but the agent runs only inside the sandbox.

Also verify the policy is actually loaded: for Claude Code, `permissions` must live under one of the documented paths (`~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, or enterprise managed); a `permissions` block buried in some other JSON file is dead config. For Factory, the file must be at `.factory/settings.json` (project) — `settings.local.json` is gitignored by convention and does not satisfy the signal on its own.

A README sentence saying "the agent should not run `rm -rf`" is documentation, not policy, and FAILs this signal.

## Your Task

1. Explore the repository to understand the current state related to this signal — list every `.claude/`, `.factory/`, `.cursor/`, `.mcp.json`, `AGENTS.md`, and `.github/workflows/*.yml` file. Note which agent tools the repo actually uses.
2. Make **substantive improvements** by writing a real, project-tuned policy:
   - For Claude Code, add a `permissions` block to `.claude/settings.json` with (a) an `allow` list of the repo's actual build/test/lint commands, (b) an `ask` list for state-changing operations that need a human (deploys, pushes, migrations), and (c) a `deny` list covering credential reads and destructive shell patterns.
   - For Factory droid, populate `commandAllowlist` and `commandDenylist` in `.factory/settings.json`.
   - If MCP servers are configured, add a short `AGENTS.md` (or extend the existing one) listing each permitted server, the specific tools the agent may call from it, and which roles can invoke them.
3. Verify the policy parses: open the project in Claude Code (or run `droid` for Factory) and confirm the settings file validates against `https://json.schemastore.org/claude-code-settings.json` (add the `$schema` line). Confirm at least one denied command actually gets blocked when attempted.
4. Keep changes focused on this signal — do not refactor unrelated config.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** wildcard allow rules — `"allow": ["*"]`, `"allow": ["Bash"]`, `"allow": ["Bash(*)"]`, or `commandAllowlist: ["*"]` defeat the entire point of the policy.
- **NO** empty `deny`/`commandDenylist` arrays. Every policy file MUST block credential reads and at least one destructive shell pattern, or it is a stub.
- **NO** `permissions.deny` rules that the matching `allow` rule re-enables — remember deny is checked first, but a permissive `Bash(*)` allow with a narrow `Bash(rm -rf /)` deny is a false sense of security (`rm -rf .` and `rm -rf $HOME` slip through).
- **NO** copying a generic template verbatim without removing rules for tools the repo doesn't use or adding rules for tools it does. A Python repo with `Bash(npm run test *)` in its allowlist signals zero project knowledge.
- **NO** putting the policy in a path Claude Code or Factory does not read (e.g. `policy.json` at repo root, `.agentrc`, a comment in `README.md`). The harness ignores it and the signal stays failed.
- **NO** documenting the policy in prose ("agents must not run destructive commands") without a machine-readable enforcement file. Prose is unenforceable.
- **NO** committing `.claude/settings.local.json` as the only artifact — that file is intended to be gitignored per-developer overrides; the team policy belongs in `.claude/settings.json`.

Examples of BAD fixes:
- Creating `.claude/settings.json` containing `{"permissions": {"allow": ["*"]}}` — this is strictly worse than no file because it suppresses prompts on dangerous commands.
- Adding `{"commandDenylist": ["rm -rf /"]}` and nothing else — `rm -rf /` is not a realistic agent failure mode; the real risks are `rm -rf node_modules/..`, `rm -rf $VAR/` where `$VAR` is empty, and recursive deletes inside the repo. The deny list must be substantive.
- A `deny: ["Bash(curl *)"]` block on a repo whose deploy script literally uses `curl` to ping a webhook — the policy will be disabled within a week. Tune the rules to the repo.
- Adding `AGENTS.md` that says "the agent can use any MCP server in `.mcp.json`" — that is registration, not a policy.
- Setting `"$schema"` but leaving `permissions` empty — the file validates but enforces nothing.

Examples of GOOD fixes:
- For a Node/TypeScript repo:
  ```json
  {
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "permissions": {
      "allow": [
        "Bash(pnpm install)", "Bash(pnpm run lint)", "Bash(pnpm run test *)",
        "Bash(pnpm run build)", "Bash(git status)", "Bash(git diff *)",
        "Bash(git log *)", "Bash(gh pr view *)", "Bash(gh pr diff *)",
        "Read(./src/**)", "Read(./tests/**)"
      ],
      "ask": [
        "Bash(git push *)", "Bash(gh pr create *)", "Bash(pnpm publish *)",
        "Bash(npx prisma migrate *)"
      ],
      "deny": [
        "Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)",
        "Read(./config/credentials*)",
        "Bash(curl * | sh)", "Bash(wget * | sh)",
        "Bash(rm -rf *)", "Bash(git push --force *)", "Bash(git push -f *)",
        "Bash(sudo *)", "WebFetch"
      ]
    }
  }
  ```
- For a Factory droid repo, a `.factory/settings.json` with `commandAllowlist` enumerating the actual build chain (`["pnpm *", "make *", "pytest *"]`) and `commandDenylist` extending the built-in denies with project-specific danger zones (`["rm -rf node_modules/..", "terraform destroy *", "kubectl delete ns prod*"]`).
- An `AGENTS.md` block like:
  ```
  ## MCP tool policy
  - mcp__github: read-only — allowed tools: get_file_contents, list_commits, search_issues. Denied: create_or_update_file, delete_file, merge_pull_request.
  - mcp__filesystem: scoped to ./workspace only (root configured at server startup).
  - mcp__slack: disabled in CI; available only in interactive sessions.
  ```
- A `.github/workflows/agent.yml` step that pins `step-security/harden-runner@v2` with `egress-policy: block` and an explicit allowed-endpoints list, paired with a comment pointing to `AGENTS.md` for the policy source of truth.

## Why this matters

Unbounded agent tool access has caused production outages: Replit's agent deleted 1,200+ production records in July 2025 despite explicit instructions not to; Amazon's Kiro agent destroyed an AWS Cost Explorer environment (13-hour outage); Invariant Labs demonstrated GitHub MCP agents chaining a private repo read with a public issue post via prompt injection. Prompt-level guardrails ("don't touch prod") are not enforcement — they live in the model's context and a sufficiently capable agent will reason around them. A checked-in deny list is the only deterministic boundary.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Claude Code settings & permission rule syntax: https://code.claude.com/docs/en/configuration
- Claude Code Agent SDK permissions evaluation order: https://code.claude.com/docs/en/agent-sdk/permissions
- Factory droid settings (`commandAllowlist`/`commandDenylist`): https://docs.factory.ai/cli/configuration/settings
- Factory hierarchical settings & org control: https://docs.factory.ai/enterprise/hierarchical-settings-and-org-control
- Factory LLM safety & agent controls: https://docs.factory.ai/enterprise/llm-safety-and-agent-controls
- COMPEL MCP security baseline, Control 3 (tool scope isolation & allowlisting): https://www.compelframework.org/articles/model-context-protocol-security-standards
- Microsoft Agent Governance Toolkit (control plane for MCP tool execution): https://developer.microsoft.com/blog/securing-mcp-a-control-plane-for-agent-tool-execution
- Real-world failures (Replit, Kiro, Invariant Labs GitHub MCP): https://policylayer.com/mcp-security
</system-reminder>
