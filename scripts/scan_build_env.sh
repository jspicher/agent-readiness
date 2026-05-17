#!/usr/bin/env bash
# Scan for Build & Dev Environment signals (Pillar 5)
# Helps the agent find relevant files — not a substitute for judgment.

REPO="${1:-.}"
. "$(dirname "$0")/_lib.sh"
cd "$REPO" 2>/dev/null || { echo "Cannot access $REPO"; exit 1; }

echo "=== Pillar 5: Build & Dev Environment ==="
echo ""

echo "-- Dependency lockfiles --"
for f in package-lock.json yarn.lock pnpm-lock.yaml bun.lockb \
         Cargo.lock go.sum Gemfile.lock poetry.lock uv.lock \
         Pipfile.lock composer.lock pubspec.lock; do
  [ -f "$f" ] && echo "./$f"
done

echo ""
echo "-- Build commands --"
# Check for documented build commands in common files
for f in README.md AGENTS.md CONTRIBUTING.md Makefile Justfile; do
  if [ -f "$f" ]; then
    build_refs=$(grep -ci 'make build\|npm run build\|cargo build\|go build\|gradle build\|mvn.*package\|bundle exec' "$f" 2>/dev/null)
    [ "$build_refs" -gt 0 ] && echo "  $build_refs build command references in $f"
  fi
done

echo ""
echo "-- Setup scripts --"
for f in bin/setup script/setup scripts/setup.sh scripts/bootstrap.sh \
         script/bootstrap Makefile Justfile; do
  [ -f "$f" ] && echo "./$f"
done

echo ""
echo "-- Dev container --"
if [ -d .devcontainer ]; then
  echo ".devcontainer/:"
  ls -1 .devcontainer/ 2>/dev/null | while read f; do echo "  $f"; done
elif [ -f devcontainer.json ]; then
  echo "./devcontainer.json"
else
  echo "  (not found)"
fi

echo ""
echo "-- Containerized services --"
find . -maxdepth 2 -name 'Dockerfile*' -o -name 'docker-compose*.yml' \
  -o -name 'docker-compose*.yaml' -o -name 'compose.yml' -o -name 'compose.yaml' 2>/dev/null | sort

echo ""
echo "-- Reproducible environment --"
for f in flake.nix shell.nix default.nix devbox.json devbox.lock; do
  [ -f "$f" ] && echo "./$f"
done

echo ""
echo "-- Tool version pinning --"
for f in .tool-versions mise.toml .mise.toml .node-version .nvmrc \
         .python-version .ruby-version .go-version rust-toolchain.toml \
         rust-toolchain .java-version .sdkmanrc; do
  [ -f "$f" ] && echo "./$f"
done

echo ""
echo "-- Monorepo orchestration --"
# Check for workspace configs
if [ -f package.json ]; then
  grep -q '"workspaces"' package.json 2>/dev/null && echo "  workspaces in package.json"
fi
for f in pnpm-workspace.yaml lerna.json nx.json turbo.json rush.json; do
  [ -f "$f" ] && echo "./$f"
done
if [ -f Cargo.toml ]; then
  grep -q '\[workspace\]' Cargo.toml 2>/dev/null && echo "  Cargo workspace in Cargo.toml"
fi
if [ -f go.work ]; then
  echo "./go.work"
fi

echo ""
echo "-- Build caching --"
if [ -d .github/workflows ]; then
  cache_count=$(grep -rl 'actions/cache\|buildx.*cache\|turbo.*cache\|ccache\|sccache' .github/workflows/ 2>/dev/null | wc -l | tr -d ' ')
  echo "  $cache_count workflows with cache configuration"
fi
[ -f turbo.json ] && grep -q 'cache' turbo.json 2>/dev/null && echo "  Turborepo cache config"

echo ""
echo "-- Cross-platform support --"
if [ -d .github/workflows ]; then
  for f in .github/workflows/*.yml .github/workflows/*.yaml; do
    [ -f "$f" ] || continue
    if grep -q 'matrix:' "$f" 2>/dev/null; then
      os_line=$(grep -A10 'matrix:' "$f" | grep -i 'os:' | head -1 | tr -d ' ')
      [ -n "$os_line" ] && echo "  $(basename "$f"): $os_line"
    fi
  done
fi
# Phase 2.y.1 -- app dev-loop portability signals for #106.
# For repo_kind=app, the gate is "do task runners normalize across darwin/linux/win?"
# These greps inform the auditor's judgment; they don't auto-pass or auto-fail.
echo "  app dev-loop signals:"
if [ -f package.json ]; then
  cross_env=$(grep -c '"cross-env\|cross-env ' package.json 2>/dev/null)
  [ "$cross_env" -gt 0 ] 2>/dev/null && echo "    cross-env: $cross_env references in package.json"
  rimraf=$(grep -c 'rimraf' package.json 2>/dev/null)
  [ "$rimraf" -gt 0 ] 2>/dev/null && echo "    rimraf: $rimraf references in package.json (portable rm -rf)"
fi
# Non-portable patterns in package.json scripts and shell scripts (informational).
np_scripts=$(grep -RIn "${EXCLUDE_GREP_ARGS[@]}" --include='package.json' -E '"[a-z:]+":[[:space:]]*"[^"]*(/dev/null|\bsource[[:space:]]\+\.|\bexport[[:space:]]\+[A-Z_]+=|`[^`]+`|&&[[:space:]]*\[)' . 2>/dev/null | head -5)
[ -n "$np_scripts" ] && echo "    non-portable patterns in package.json scripts (manual review):" && echo "$np_scripts" | sed 's/^/      /'
sh_bang_only=$(grep -RIl --include='*.sh' '^#!/bin/sh\b' scripts/ bin/ tools/ 2>/dev/null | head -3)
[ -n "$sh_bang_only" ] && echo "    /bin/sh shebangs (manual review for cmd.exe compat):" && echo "$sh_bang_only" | sed 's/^/      /'
# Documented WSL/devcontainer escape hatch for Windows users.
if [ -f README.md ] || [ -f AGENTS.md ] || [ -f CONTRIBUTING.md ]; then
  wsl_docs=$(grep -liE 'wsl|windows subsystem|devcontainer.*windows' README.md AGENTS.md CONTRIBUTING.md 2>/dev/null | head -3)
  [ -n "$wsl_docs" ] && echo "    WSL/devcontainer escape hatch documented:" && echo "$wsl_docs" | sed 's/^/      /'
fi

echo ""
echo "-- Cloud dev environment --"
[ -f .gitpod.yml ] && echo "./.gitpod.yml"
if [ -d .devcontainer ]; then
  grep -q 'codespaces\|ghcr.io' .devcontainer/devcontainer.json 2>/dev/null \
    && echo "  Codespaces support in devcontainer.json"
fi

echo ""
echo "-- Package manager configuration --"
for f in .npmrc .yarnrc .yarnrc.yml .pnpmrc pip.conf .cargo/config.toml \
         .cargo/config gradle.properties; do
  [ -f "$f" ] && echo "./$f"
done

echo ""
echo "-- Heavy dependency / bundle analysis --"
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='package.json' \
  -E '@next/bundle-analyzer|webpack-bundle-analyzer|source-map-explorer|rollup-plugin-visualizer' . 2>/dev/null | head -5
grep -RIn "${EXCLUDE_GREP_ARGS[@]}" --include='package.json' '"analyze"' . 2>/dev/null | head -3

echo ""
echo "-- Unused dependencies detection --"
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='package.json' --include='requirements*.txt' --include='pyproject.toml' \
  -E 'depcheck|knip|npm-check|deptry|cargo-machete' . 2>/dev/null | head -5

echo ""
echo "-- Build performance tracking --"
grep -RIn --include='*.yml' --include='*.yaml' -E 'build.duration|build.time|--profile|TURBO_REMOTE_CACHE|nx-cloud' .github/workflows/ 2>/dev/null | head -5

echo ""
echo "-- Database schema (conditional) --"
for d in migrations migration db/migrate prisma supabase/migrations alembic/versions; do
  [ -d "$d" ] && echo "./$d/ ($(find "$d" -type f | wc -l | tr -d ' ') files)"
done
find_prune . -maxdepth 3 \( -name 'schema.prisma' -o -name 'schema.sql' \) -print 2>/dev/null | head -5

echo ""
echo "-- Devcontainer runnable / CI'd --"
if [ -f .devcontainer/devcontainer.json ]; then
  grep -RIl --include='*.yml' --include='*.yaml' 'devcontainer.*build\|devcontainers/ci' .github/workflows/ 2>/dev/null | head -3
fi
