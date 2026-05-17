[Readiness Fix] <REPO_NAME> Hooks for Context Preservation

Fix the failing signal: Hooks for Context Preservation ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Hooks for Context Preservation
**Score**: [0/1]
**Description**: Pre/post-action hooks that capture or persist agent state across compaction, session end, and tool execution boundaries so a long-running agent (or the next session) can resume without re-discovering everything from scratch
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Hooks for context preservation — check for a checked-in, runtime-registered hook that captures or persists agent state at one of the lifecycle boundaries where state would otherwise be lost. PASS requires at least one of the following, with a real script (not an empty stub) that writes to disk, a database, or stdout-injected-into-context:

1. **Claude Code `PreCompact` hook**: registered in `.claude/settings.json` under `hooks.PreCompact`, with a `command` that points to an executable script that reads the JSON event payload from stdin (`session_id`, `transcript_path`, `trigger` of `manual`/`auto`) and writes something durable — a handoff markdown file, a full-transcript SQLite dump, a session-state file, or a `save_memory` MCP call. A hook that only `echo`s to stderr without persisting anything FAILs.
2. **Claude Code `SessionStart` hook with `matcher: "compact"` or `matcher: "resume"`**: re-injects preserved context after compaction or resume. Whatever the script writes to stdout is appended to the conversation; an empty script or one that prints a static "welcome" string is not preservation.
3. **Claude Code `SessionEnd` hook**: persists a session log / observations / TODO carryover before the session terminates. The `reason` field (`clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`) should be honored — saving on `clear` and `logout` matters more than on `resume`.
4. **Factory droid `SessionStart` / `Stop` hooks**: registered in `.factory/settings.json` under `hooks.SessionStart` or `hooks.Stop`, with a `command` resolved via `$FACTORY_PROJECT_DIR` (or `$DROID_PROJECT_DIR` on older droid versions) that loads or saves context. Factory exposes `DROID_ENV_FILE` for persisting environment changes across the session — context-load hooks should use it when applicable.
5. **Project-level memory-persistence layer wired to one of the above**: a `save_memory` / `recall_memory` MCP server (or equivalent JSON/SQLite store) that the hook actually writes to. Bonus credit if `SessionStart` reads from it and injects recent memories into stdout.

Also verify the hook is actually loaded:
- The `command` path must be absolute or `$CLAUDE_PROJECT_DIR`/`$FACTORY_PROJECT_DIR`-relative (relative paths fail because hooks execute from the runtime's CWD, which is not necessarily the repo root).
- The script must be executable (`chmod +x` on Unix; `.bat`/`.cmd`/`.ps1` with proper invocation on Windows).
- The settings file must be at one of the documented paths: `.claude/settings.json` (project, committed), `~/.claude/settings.json` (user, not in repo), `.factory/settings.json` (project, committed). A hook block in `.claude/settings.local.json` is gitignored by convention and does NOT satisfy a team-level signal on its own.
- For Claude Code, run `/hooks` interactively to confirm the hook appears in the registered list, or trigger a compact (`/compact`) and confirm the script's side effects.

A README sentence saying "the agent should save state before compacting" is documentation, not a hook, and FAILs this signal. A hook that prints a banner but writes nothing also FAILs — the signal is about state *capture*, not lifecycle decoration.

## Your Task

1. Explore the repository to understand the current state related to this signal:
   - List every file under `.claude/hooks/`, `.factory/hooks/`, `.agent/hooks/`.
   - Open `.claude/settings.json`, `.claude/settings.local.json`, `.factory/settings.json` and enumerate every event already wired under `hooks.*`.
   - Identify which agent runtime the repo targets (Claude Code, Factory droid, or both — check for `.claude/` vs `.factory/` directories).
   - Note whether the repo already has a memory store (`mcp__memory__*` tools in `.mcp.json`, a `MEMORY.md`, a SQLite file, etc.) that hooks could persist into.
2. Make **substantive improvements** by wiring at least one real preservation hook for the runtime(s) the repo uses:
   - For Claude Code: add a `PreCompact` hook that writes a handoff file (e.g., `.claude/handoff.md` or a `pre-compact-<timestamp>.md` under `.claude/backups/`) capturing git branch, modified files, recent prompts, and a pointer to the transcript path. Pair it with a `SessionStart` hook (matcher `"compact"`) that reads that file back into stdout so context survives.
   - For Factory droid: add a `SessionStart` hook that loads project context (e.g., `AGENTS.md` snippets, current branch, recent commits) and a `Stop` or `SessionEnd`-equivalent hook that snapshots session state.
   - If the repo has a `save_memory` MCP tool wired in, the `PreCompact` hook should additionally call it (or print a `<system-reminder>`-style stdout block instructing the agent to call it).
3. Verify the hook is actually loaded and runs:
   - Claude Code: open the project, run `/hooks` and confirm the new entry appears; trigger `/compact` and verify the handoff file was written and the post-compact context includes the re-injected content.
   - Factory droid: run `droid` in the repo and confirm `SessionStart` output appears in the conversation; check that the script's stderr is visible in droid's hook log.
   - Tail the runtime's hook log (Claude Code: `~/.claude/logs/`; Factory: stderr) to confirm exit code 0 and no timeout.
4. Document the hook in `AGENTS.md` (or a new `docs/agent-hooks.md`) with a one-line description per hook and the path to its script — so a future maintainer doesn't delete it thinking it's dead code.
5. Keep changes focused on this signal — do not refactor unrelated config.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** empty hook scripts. A `#!/bin/bash\nexit 0` script that "registers" a hook without persisting anything is strictly worse than no hook because it makes the signal look addressed while preserving zero state.
- **NO** hooks that only `echo` to stderr. Stderr is not captured into Claude Code's context; only stdout is re-injected on `SessionStart`. A `PreCompact` hook that logs to stderr and writes nothing to disk is a no-op from a preservation standpoint.
- **NO** hooks that write to a path the runtime cannot find on resume. `/tmp/handoff.md` evaporates on reboot; `$TMPDIR/...` on Windows is subject to Storage Sense cleanup. Persist to `.claude/` or `.factory/` inside the repo (and gitignore the backup files if they contain transcripts), or to `~/.claude/sessions/`.
- **NO** registering the hook in `.claude/settings.local.json` only. That file is per-developer and typically gitignored; the team-level signal requires the hook to be in the committed `.claude/settings.json`. Per-developer overrides are fine as an addition, not a substitute.
- **NO** relative `command` paths like `"./hooks/save.sh"`. The runtime's CWD is unpredictable; use `"$CLAUDE_PROJECT_DIR/.claude/hooks/save.sh"` for Claude Code or `"$FACTORY_PROJECT_DIR/.factory/hooks/save.sh"` for Factory.
- **NO** hooks that block forever or take longer than the runtime's timeout (Factory's default is 60s; Claude Code hooks should complete in seconds). A `PreCompact` hook that runs `pytest` will time out and the compaction will proceed without the save.
- **NO** misspelled event names. `PreCompaction`, `PreCompactHook`, `pre_compact`, `precompact` are all wrong — the only accepted spelling is `PreCompact` (capital P, capital C). A misspelled key sits silently in settings and never fires.
- **NO** hooks in directories the runtime doesn't read. `.cursor/hooks/`, `.aider/hooks/`, `hooks/` at repo root are not Claude Code or Factory paths. They satisfy nothing.
- **NO** committing transcripts or memory dumps with secrets. The handoff file should redact env vars; if you dump the full transcript, gitignore the backup directory.

Examples of BAD fixes:
- `.claude/hooks/precompact.sh` containing only `echo "compacting..." >&2; exit 0` — registers a hook, persists nothing, fails the signal.
- A `PreCompact` entry whose `command` is `"node scripts/save.js"` with no absolute path — fails to run when the user invokes Claude Code from a subdirectory.
- Adding `{"hooks": {"PreCompact": []}}` (empty array) — schema-valid, behaviorally empty.
- Wiring a `SessionStart` hook that prints "Welcome to the repo!" with no dynamic content — that's a banner, not preservation.
- A hook that writes to `/tmp/claude-handoff.md` — gone after reboot, useless across sessions.
- Registering the hook in `~/.claude/settings.json` (user-global) instead of the project's `.claude/settings.json` — the signal evaluates the repo, not the developer's machine.
- A `Stop` hook on Factory that runs `git commit -am "auto-save"` — that's a destructive side effect, not state preservation, and will pollute git history.

Examples of GOOD fixes:

**Claude Code: `PreCompact` handoff + `SessionStart` re-injection**

`.claude/settings.json`:
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-compact-save.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-compact-restore.sh",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "resume",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-compact-restore.sh",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end-save.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/pre-compact-save.sh` (chmod +x, gitignore `.claude/backups/`):
```bash
#!/usr/bin/env bash
# PreCompact: snapshot enough state that the next session can resume.
# Reads JSON payload from stdin: {session_id, transcript_path, trigger}
set -euo pipefail
PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
TRANSCRIPT=$(echo "$PAYLOAD" | jq -r '.transcript_path // ""')
TRIGGER=$(echo "$PAYLOAD" | jq -r '.trigger // "auto"')
TS=$(date -u +"%Y%m%dT%H%M%SZ")

BACKUP_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/backups"
HANDOFF="${CLAUDE_PROJECT_DIR:-.}/.claude/handoff.md"
mkdir -p "$BACKUP_DIR"

BRANCH=$(git -C "${CLAUDE_PROJECT_DIR:-.}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
MODIFIED=$(git -C "${CLAUDE_PROJECT_DIR:-.}" status --porcelain 2>/dev/null | head -40)

{
  echo "# Handoff — $TS"
  echo "- session: $SESSION_ID"
  echo "- trigger: $TRIGGER"
  echo "- branch: $BRANCH"
  echo "- transcript: $TRANSCRIPT"
  echo ""
  echo "## Uncommitted changes"
  echo '```'
  echo "${MODIFIED:-(clean)}"
  echo '```'
  echo ""
  echo "## Last 5 commits"
  git -C "${CLAUDE_PROJECT_DIR:-.}" log --oneline -5 2>/dev/null || true
} > "$HANDOFF"

cp "$HANDOFF" "$BACKUP_DIR/handoff-$TS.md"

# stdout is injected into context after compaction
echo "Handoff written to .claude/handoff.md — read it to resume."
```

`.claude/hooks/post-compact-restore.sh`:
```bash
#!/usr/bin/env bash
HANDOFF="${CLAUDE_PROJECT_DIR:-.}/.claude/handoff.md"
[ -f "$HANDOFF" ] || exit 0
echo "<system-reminder>Prior session handoff (read before continuing):</system-reminder>"
cat "$HANDOFF"
```

**Factory droid: `SessionStart` context-load**

`.factory/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$FACTORY_PROJECT_DIR\"/.factory/hooks/load-context.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$FACTORY_PROJECT_DIR\"/.factory/hooks/save-stop-snapshot.sh",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

`.factory/hooks/load-context.sh` prints the active branch, recent commits, open PRs (via `gh pr list --json number,title,headRefName`), and any `.factory/handoff.md` from the prior session.

**Bonus: wire to a memory MCP server**

If `.mcp.json` registers a `memory` server with `save_memory` / `recall_memory` tools, the `PreCompact` hook can additionally print:
```
<system-reminder>
Before compaction completes, call save_memory with a one-paragraph summary of: (1) the current task, (2) decisions made this session, (3) the next concrete step. This is your last chance to persist before context is summarized.
</system-reminder>
```
This instructs the agent itself to call the MCP tool — the hook script doesn't need MCP access, just stdout.

## Why this matters

Context compaction is lossy by design: when the window fills, Claude Code summarizes the conversation and discards the originals. Several practitioner write-ups in early 2026 documented hours of work disappearing into bad summaries — debugging trails, file-edit rationale, and decision history that the summary collapsed into a one-line bullet. The fix that consistently worked was a `PreCompact` hook that wrote the full transcript to SQLite (or a structured handoff to disk) before summarization, paired with a `SessionStart` hook on the `compact` matcher to re-inject the critical anchors. Prompt-level instructions ("remember to save state before compacting") are unreliable — the model is mid-task and often misses the trigger; hooks fire deterministically. Without preservation hooks, every long-running agent session is one auto-compact away from losing its plan, and every `/clear` or crash dumps the entire session's reasoning.

The signal is at L3 because L1/L2 readiness assumes short, supervised sessions; L3 readiness assumes the agent runs long enough to hit compaction or crash boundaries, and the repo must catch state at those edges.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, which hook events you wired, and how you verified the hook fires (e.g., "ran `/compact` and confirmed `.claude/handoff.md` was written with current branch + 5 modified files")

## References

- Claude Code Hooks reference (event list, payload schema, matcher semantics): https://code.claude.com/docs/en/hooks
- Claude Code Hooks guide (worked examples incl. `SessionStart` matcher `"compact"` for context re-injection): https://code.claude.com/docs/en/hooks-guide
- Claude Code Agent SDK hooks (`PreCompact`, `SessionStart`, `SessionEnd` programmatic registration): https://code.claude.com/docs/en/agent-sdk/hooks
- Claude Code power-user hooks blog (PreCompact, SessionStart, UserPromptSubmit patterns): https://claude.com/blog/how-to-configure-hooks
- Factory droid Hooks reference (`SessionStart`, `Stop`, `PreToolUse`, `PostToolUse`, `$FACTORY_PROJECT_DIR`): https://docs.factory.ai/cli/configuration/hooks-reference
- Factory droid Session Automation cookbook (`SessionStart` patterns with `DROID_ENV_FILE`): https://docs.factory.ai/guides/hooks/session-automation
- Practitioner writeup — "Compaction Kept Destroying My Work. I Built Hooks That Fixed It." (PreCompact-to-SQLite pattern): https://dev.to/mikeadolan/claude-code-compaction-kept-destroying-my-work-i-built-hooks-that-fixed-it-2dgp
- Reference PreCompact handoff script (`.claude/handoff.md` pattern): https://github.com/anipotts/claude-code-tips/blob/main/hooks/context-save.sh
- Reference PreCompact memory-flush + anchor-state pattern: https://github.com/naman10parikh/claude-harness/blob/main/hooks/pre-compact-memory-flush.sh
</system-reminder>
