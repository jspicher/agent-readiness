# Shared helpers for the agent-readiness scanner scripts.
#
# Source this file with `. "$(dirname "$0")/_lib.sh"` at the top of each scanner.
# Provides one canonical exclude list -- mirrored from SKILL.md "Behavioral
# Guidelines: Repository boundary" -- so scanners stop recursing into
# node_modules, dist, build, etc.
#
# Without this, a typical Node-app scan enumerates ~50,000 vendored files and
# stalls or floods the output with irrelevant matches. See ERR-20260517-007.

# Directories to skip during scans. Keep in sync with SKILL.md Behavioral Guidelines.
EXCLUDE_DIRS=(
  node_modules
  dist
  build
  .next
  out
  .turbo
  .nuxt
  .svelte-kit
  .venv
  venv
  __pycache__
  .pytest_cache
  target
  .gradle
  .idea
  .vscode
  .pnpm-store
  vendor
  coverage
  .git
)

# Pre-built grep --exclude-dir arguments.
EXCLUDE_GREP_ARGS=()
for d in "${EXCLUDE_DIRS[@]}"; do
  EXCLUDE_GREP_ARGS+=("--exclude-dir=$d")
done

# find_prune <root> <find-args...>
#
# Prepends a -prune clause for every entry in EXCLUDE_DIRS before the rest of
# the find expression. The caller is responsible for ending the expression
# with `-print` (or another action) -- once you mix -prune with -o, find no
# longer defaults to -print.
#
# Example:
#   find_prune . -maxdepth 3 -iname 'AGENTS.md' -print
find_prune() {
  local root="$1"; shift
  local prune_expr=()
  local first=1
  for d in "${EXCLUDE_DIRS[@]}"; do
    if [ $first -eq 1 ]; then
      prune_expr+=( -name "$d" )
      first=0
    else
      prune_expr+=( -o -name "$d" )
    fi
  done
  find "$root" \( "${prune_expr[@]}" \) -prune -o "$@"
}
