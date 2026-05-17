#!/usr/bin/env bash
# capture_audit_context.sh -- emit a JSON object describing the working tree state.
#
# Usage:
#   bash scripts/capture_audit_context.sh [repo_path]   (default: .)
#
# Emits one JSON object to stdout:
#   {
#     "head_sha": "<full-sha>",
#     "branch": "<branch>",
#     "worktree_dirty": true|false,
#     "dirty_files_count": <int>,
#     "dirty_diff_sha256": "<64-hex>" | null,
#     "captured_at": "<ISO-8601 UTC with Z suffix>"
#   }
#
# Exit codes:
#   0  success
#   1  not a git repo at the given path

set -euo pipefail

repo="${1:-.}"

if ! git -C "$repo" rev-parse --git-dir >/dev/null 2>&1; then
  echo "capture_audit_context.sh: $repo is not a git repository" >&2
  exit 1
fi

head_sha="$(git -C "$repo" rev-parse HEAD)"

branch="$(git -C "$repo" branch --show-current)"
if [ -z "$branch" ]; then
  short="$(git -C "$repo" rev-parse --short HEAD)"
  branch="detached@${short}"
fi

# `git status --porcelain` lists one entry per modified path. wc -l on an empty
# input yields 0 (or whitespace-padded 0); trim defensively.
dirty_files_count="$(git -C "$repo" status --porcelain | wc -l | tr -d ' ')"

if [ "$dirty_files_count" -gt 0 ]; then
  worktree_dirty="true"
  dirty_diff_sha256="$(git -C "$repo" diff HEAD | sha256sum | awk '{print $1}')"
  dirty_diff_field="\"${dirty_diff_sha256}\""
else
  worktree_dirty="false"
  dirty_diff_field="null"
fi

captured_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Hand-rolled JSON (no jq dependency). Values are simple types so straight
# string interpolation is safe; branch names contain shell-friendly chars per
# git refname rules. printf %s preserves backslashes if present.
printf '{"head_sha":"%s","branch":"%s","worktree_dirty":%s,"dirty_files_count":%s,"dirty_diff_sha256":%s,"captured_at":"%s"}\n' \
  "$head_sha" \
  "$branch" \
  "$worktree_dirty" \
  "$dirty_files_count" \
  "$dirty_diff_field" \
  "$captured_at"
