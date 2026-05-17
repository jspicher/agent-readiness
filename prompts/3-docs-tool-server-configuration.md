[Readiness Fix] <REPO_NAME> Tool Server Configuration

Fix the failing signal: Tool Server Configuration ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Tool Server Configuration
**Score**: [0/1]
**Description**: Checked-in configuration for agent tool protocols (Model Context Protocol / equivalent) so agents can discover and connect to the external tools the project depends on
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Tool server configuration – check for a checked-in, machine-readable manifest that registers the MCP (Model Context Protocol) servers an agent needs to do real work in this repo. PASS requires at least one of the following, with at least one real server entry (an empty `mcpServers: {}` is a FAIL):

1. **Claude Code / Cursor project-scoped MCP**: `.mcp.json` at the repo root (Claude Code) or `.cursor/mcp.json` (Cursor). Both follow the same shape: a top-level `mcpServers` object keyed by server name. Each entry MUST be one of:
   - **stdio** server: `{ "type": "stdio", "command": "...", "args": [...], "env": {...} }` (the `type` field is optional and defaults to `"stdio"` in Claude Code, but specify it explicitly for clarity)
   - **HTTP** server: `{ "type": "http", "url": "https://...", "headers": {...} }` — the current recommended remote transport per MCP spec 2025-06-18
   - **SSE** server: `{ "type": "sse", "url": "https://...", "headers": {...} }` — legacy; new servers should use `http`
2. **VS Code / GitHub Copilot MCP**: `.vscode/mcp.json` with the same `mcpServers` shape (Copilot reads this file as of the 1.99+ release).
3. **Plugin manifest with bundled servers**: a Claude Code plugin (`.claude-plugin/plugin.json` with an `mcpServers` field) or equivalent that registers servers transitively.

The file must (a) live at one of the paths above (the harness ignores arbitrarily-named files), (b) contain at least one server entry whose `command` or `url` actually resolves on a fresh checkout, and (c) be checked into version control — a `.mcp.json` listed in `.gitignore` does not count.

Note on environment variables: Claude Code and Cursor both expand `${VAR}` and `${VAR:-default}` inside `command`, `args`, `env`, `url`, and `headers` at connect time. Use this for any secret (API keys, tokens). A checked-in file with a hardcoded secret is both a security incident and a FAIL of this signal because rotating the secret breaks every clone.

This signal is about REGISTRATION (which servers exist, how to launch them). It is distinct from the ALLOWLIST signal (which tools inside those servers an agent may invoke) — see Pillar 4 / feature #121 (Tool Allowlist / Permission Policy) for that. A repo can PASS registration and still FAIL allowlist, and vice versa; both are required for a hardened agent setup.

A README sentence saying "the agent uses GitHub and Slack via MCP" is documentation, not configuration, and FAILs this signal.

## Your Task

1. Explore the repository to understand which external tools the project actually depends on — git/GitHub, databases (Postgres, Supabase, Neon), file-system access outside the repo, browser automation, Slack/Notion/Linear, deploy targets (Vercel, Cloudflare), observability (Sentry, PostHog). Note what's already in `.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`, and any plugin manifests. Check `.gitignore` to confirm the file you plan to edit is actually tracked.
2. Make **substantive improvements** by writing a real, project-tuned tool server manifest:
   - Create or extend `.mcp.json` at the repo root with one entry per server the project genuinely needs. For a typical web app this is usually a small set: a `filesystem` server scoped to the workspace, a `github` server for PR/issue access, and one or two project-specific servers (e.g. `postgres`, `sentry`, `posthog`, `slack`).
   - For every entry, use `${ENV_VAR}` interpolation for credentials. Document the required vars in `README.md` or `AGENTS.md` ("To use the MCP servers in `.mcp.json`, export `GITHUB_TOKEN`, `POSTGRES_URL`, ...").
   - On Windows-supporting repos, wrap `npx`/`uvx`/`python` invocations as `cmd /c npx ...` — bare `npx` works on macOS/Linux but fails on Windows because Claude Code's stdio launcher does not consult PATHEXT for `.cmd` shims.
   - Add a short section to `AGENTS.md` (or create one) listing each registered server, what it's for, and which env vars must be set. Registration without documentation leaves the next agent guessing.
3. Verify the manifest loads:
   - For Claude Code: `claude mcp list` should show every server as `connected` after `claude` is restarted in the project directory. `claude mcp get <name>` shows the resolved config for one server.
   - For Cursor: open Cursor in the repo, check Settings → MCP, every server should report a green dot.
   - Manually run one tool from each server in an agent session to confirm the env vars resolved and the command actually launched.
4. Keep changes focused on this signal — do not edit the permission allowlist (`.claude/settings.json` `permissions` block) or skill definitions; those are separate signals.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** empty `mcpServers: {}` — that's strictly worse than no file because tooling treats the file as authoritative and skips fallback discovery.
- **NO** hardcoded secrets in any `env`, `headers`, or `url` field. Use `${TOKEN}` interpolation and document the var. If the readiness report flagged a hardcoded secret as the failure reason, ROTATE it before committing the fix (the old value is in the git history forever).
- **NO** servers whose `command` references a binary that isn't on a standard PATH or installable via the documented setup (e.g. an absolute path to `/Users/you/.cargo/bin/my-server`). Use `npx`, `uvx`, `pipx`, or a documented install step.
- **NO** Windows-incompatible launchers on a cross-platform repo. Bare `npx` and `uvx` fail on Windows under Claude Code; wrap as `cmd /c npx ...` or document the platform limitation explicitly.
- **NO** registering servers the repo doesn't actually use ("might be handy later"). Each entry is a connection the agent attempts at startup; broken or noisy servers slow every session and train agents to ignore connection errors.
- **NO** checking in `.mcp.json` while it's also listed in `.gitignore` (the file exists locally but never reaches teammates) — the readiness scanner will not see the file in a fresh clone and the signal stays failed.
- **NO** putting `mcpServers` inside `.claude/settings.json` and calling it done. Claude Code does read `mcpServers` from `~/.claude.json` (user scope) and from `.mcp.json` (project scope), but project-scope team config MUST be in `.mcp.json` to be shared via git. Settings-file `mcpServers` is per-user and does not satisfy this signal.
- **NO** commented-out servers (JSON doesn't support comments; even JSONC-style stubs in `.mcp.json` will fail to parse and disable every server in the file).

Examples of BAD fixes:
- Creating `.mcp.json` with `{ "mcpServers": {} }` — passes the existence check, fails the "at least one real server" check.
- `{ "mcpServers": { "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"], "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_AbCdEf123..." } } } }` — leaked PAT, signal fails, security incident, token now permanently in git history.
- A `.mcp.json` listing 15 servers copy-pasted from a "best MCP servers 2026" blog post when the repo is a static marketing site that needs none of them.
- `{ "mcpServers": { "postgres": { "command": "/Users/alice/bin/pg-mcp", ... } } }` — unreproducible on any other machine.

Examples of GOOD fixes:
- For a Next.js + Postgres + GitHub project:
  ```json
  {
    "mcpServers": {
      "filesystem": {
        "type": "stdio",
        "command": "cmd",
        "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", "${WORKSPACE_ROOT}"],
        "env": {}
      },
      "github": {
        "type": "stdio",
        "command": "cmd",
        "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
        }
      },
      "postgres-readonly": {
        "type": "stdio",
        "command": "cmd",
        "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL_READONLY}"],
        "env": {}
      },
      "sentry": {
        "type": "http",
        "url": "https://mcp.sentry.dev/mcp",
        "headers": {
          "Authorization": "Bearer ${SENTRY_AUTH_TOKEN}"
        }
      }
    }
  }
  ```
  Paired with an `AGENTS.md` block:
  ```
  ## MCP servers (registered in .mcp.json)
  - filesystem — read/write under $WORKSPACE_ROOT; required env: WORKSPACE_ROOT
  - github — PR/issue read + commit; required env: GITHUB_TOKEN (repo scope)
  - postgres-readonly — read-only analytics queries; required env: DATABASE_URL_READONLY
  - sentry — issue triage + stack traces; required env: SENTRY_AUTH_TOKEN
  ```
- Same project, drop `.cursor/mcp.json` as a symlink (or duplicate) so Cursor users get the same servers without re-discovery.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Claude Code MCP setup & `.mcp.json` schema: https://code.claude.com/docs/en/mcp
- Cursor MCP configuration (`.cursor/mcp.json`): https://cursor.com/docs/mcp
- VS Code / GitHub Copilot MCP support (`.vscode/mcp.json`): https://code.visualstudio.com/docs/copilot/chat/mcp-servers
- MCP specification 2025-06-18 (current revision) — transports (stdio, Streamable HTTP): https://modelcontextprotocol.io/specification/2025-06-18/basic/transports
- MCP specification 2025-11-25 (latest): https://modelcontextprotocol.io/specification/2025-11-25
- Reference server registry: https://github.com/modelcontextprotocol/servers
- Server discovery: https://smithery.ai and https://mcp.so
- Environment variable expansion in `.mcp.json` (`${VAR}` / `${VAR:-default}`): https://code.claude.com/docs/en/mcp#environment-variable-expansion
- Related signal — permission policy (which tools an agent may invoke from a registered server): see feature #121 / Pillar 4 Tool Allowlist
</system-reminder>
