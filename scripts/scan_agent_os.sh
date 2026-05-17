#!/usr/bin/env bash
# Scan for Agent-OS Readiness signals (Pillar 7)
# The control plane an autonomous agent needs to act safely.
# Helpers, not scorers — judgment required for quality.

REPO="${1:-.}"
. "$(dirname "$0")/_lib.sh"
cd "$REPO" 2>/dev/null || { echo "Cannot access $REPO"; exit 1; }

echo "=== Pillar 7: Agent-OS Readiness ==="
echo ""

echo "-- Tool allowlist / permission policy --"
for f in .claude/settings.json .claude/settings.local.json \
         .factory/settings.json agent-policy.json .agent/policy.json \
         .agent/restricted-paths.md; do
  [ -e "$f" ] && echo "./$f"
done
grep -RIl --include='*.json' '"permissions"' .claude/ .factory/ 2>/dev/null | head -5

echo ""
echo "-- Sandboxing / blast-radius bounds --"
for f in .devcontainer/devcontainer.json; do
  [ -e "$f" ] && grep -l 'mounts\|forwardPorts\|workspaceFolder' "$f" 2>/dev/null
done
find_prune . -maxdepth 4 \( -name 'sandbox.*' -o -name 'agent-runner.*' \) -print 2>/dev/null | head -5
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='*.yml' --include='*.yaml' 'egress\|network.policy\|allowed.hosts' . 2>/dev/null | head -5

echo ""
echo "-- Hooks for context preservation --"
for d in .claude/hooks .factory/hooks .agent/hooks; do
  [ -d "$d" ] && echo "./$d/ ($(find "$d" -type f | wc -l | tr -d ' ') files)"
done
grep -l '"hooks"' .claude/settings*.json .factory/settings*.json 2>/dev/null | head -5

echo ""
echo "-- SBOM presence --"
find_prune . -maxdepth 3 \( -name 'sbom.json' -o -name 'sbom.xml' -o -name 'cyclonedx.json' \
  -o -name 'spdx.json' -o -name 'bom.json' \) -print 2>/dev/null | head -10
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='*.yml' --include='*.yaml' 'syft\|cyclonedx\|spdx-tools\|sbom-action' .github/ 2>/dev/null | head -5

echo ""
echo "-- Provenance attestations / signing --"
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='*.yml' --include='*.yaml' 'cosign\|sigstore\|attest-build-provenance\|in-toto\|slsa-' .github/ 2>/dev/null | head -5
find_prune . -maxdepth 3 \( -name '*.intoto.jsonl' -o -name 'provenance.*' \) -print 2>/dev/null | head -5

echo ""
echo "-- Agent audit trail / run IDs --"
find_prune . -maxdepth 3 -name 'agent-runs' -type d -print 2>/dev/null | head -3
find_prune . -maxdepth 4 -name '.scratch' -type d -print 2>/dev/null | head -3
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='*.md' -E 'run.id|session.id|agent.run' AGENTS.md CLAUDE.md 2>/dev/null | head -5

echo ""
echo "-- Replayable evaluation harness --"
for d in evals eval tests/evals tests/agent prompts/golden; do
  [ -d "$d" ] && echo "./$d/ ($(find "$d" -type f | wc -l | tr -d ' ') files)"
done
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='*.yml' --include='*.yaml' 'eval\|golden.test' .github/workflows/ 2>/dev/null | head -5

echo ""
echo "-- Kill-switch infrastructure --"
grep -RIn "${EXCLUDE_GREP_ARGS[@]}" --include='*.ts' --include='*.js' --include='*.py' --include='*.go' \
  -E '(disable|halt|kill)[-_]?agent|agent[-_]?(disabled|paused)' . 2>/dev/null | head -5
find_prune . -maxdepth 3 \( -name 'disable-agent*' -o -name 'pause-agent*' \) -print 2>/dev/null | head -5

echo ""
echo "-- Human escalation path --"
find_prune . -maxdepth 3 \( -iname 'ESCALATE*' -o -iname 'HANDOFF*' \) -print 2>/dev/null | head -5
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='*.md' -i 'escalate\|human.handoff\|when.to.escalate' AGENTS.md CONTRIBUTING.md docs/ 2>/dev/null | head -5

echo ""
echo "-- Agent registry / ownership metadata --"
for f in .agents/registry.yaml .agents/registry.json .factory/agents.yaml \
         AGENTS.md .github/CODEOWNERS; do
  [ -e "$f" ] && echo "./$f"
done

echo ""
echo "-- Per-repo policy visibility --"
for f in agent-policy.json .agent/restricted-paths.md .agent/policy.md \
         .factory/settings.json AGENTS.md; do
  [ -e "$f" ] && grep -l -i 'restricted\|forbidden\|off-limits\|requires.approval' "$f" 2>/dev/null
done

echo ""
echo "-- Cost telemetry for agent runs --"
grep -RIn "${EXCLUDE_GREP_ARGS[@]}" --include='*.ts' --include='*.js' --include='*.py' \
  -E 'token.usage|tokens.used|input.tokens|output.tokens|agent.cost|cost.per.run' . 2>/dev/null | head -5
find_prune . -maxdepth 4 -name '*cost*log*' -print 2>/dev/null | head -5
