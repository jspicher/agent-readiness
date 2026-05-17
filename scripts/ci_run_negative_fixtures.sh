#!/usr/bin/env bash
# ci_run_negative_fixtures.sh -- assert each negative fixture trips exactly the V## it advertises.
#
# Walks fixtures/negative/bad-vNN-*.json, runs the validator, and verifies that
# exactly the expected [V##] code shows up in stderr (and no other [V##] codes).
# This protects against a refactor accidentally relaxing a check or a fixture
# accidentally drifting into double-tripping.

# Intentional: no `set -e`. We want to iterate every fixture and aggregate
# results; an early exit on the first failure would hide later regressions.
set -uo pipefail

dir="fixtures/negative"
if [ ! -d "$dir" ]; then
  echo "ci_run_negative_fixtures.sh: $dir not found" >&2
  exit 1
fi

shopt -s nullglob
fixtures=("$dir"/bad-v*-*.json)
shopt -u nullglob

if [ "${#fixtures[@]}" -eq 0 ]; then
  echo "ci_run_negative_fixtures.sh: no fixtures matched $dir/bad-v*-*.json" >&2
  exit 1
fi

overall=0

for fixture in "${fixtures[@]}"; do
  base="$(basename "$fixture")"
  if [[ "$base" =~ ^bad-v([0-9]+)- ]]; then
    expected="${BASH_REMATCH[1]}"
  else
    echo "FIXTURE BUG: cannot parse expected V## from filename: $base" >&2
    overall=1
    continue
  fi

  # Run validator. Discard stdout, capture stderr.
  stderr="$(python3 scripts/validate_audit_data.py "$fixture" 2>&1 > /dev/null)"
  exitcode=$?

  if [ "$exitcode" -eq 0 ]; then
    echo "FAIL [V${expected}] $base: validator exited 0 (expected nonzero)" >&2
    overall=1
    continue
  fi
  if [ "$exitcode" -ne 7 ]; then
    echo "WARN [V${expected}] $base: validator exited ${exitcode}, expected 7" >&2
  fi

  expected_token="[V${expected}]"
  if ! printf '%s\n' "$stderr" | grep -qF "$expected_token"; then
    echo "FAIL [V${expected}] $base: stderr did not contain $expected_token" >&2
    echo "    stderr was: $stderr" >&2
    overall=1
    continue
  fi

  # Collect all distinct [V##] codes that fired. Fail if any other than expected.
  # grep -F here matches the bracketed token literally; we filter the expected
  # token out of the distinct list and report anything that remains.
  others="$(printf '%s\n' "$stderr" | grep -oE '\[V[0-9]+\]' | sort -u | grep -vxF "$expected_token" || true)"
  if [ -n "$others" ]; then
    echo "FIXTURE BUG: $base trips additional codes: $(printf '%s' "$others" | tr '\n' ' ')" >&2
    echo "    full stderr:" >&2
    printf '%s\n' "$stderr" | sed 's/^/      /' >&2
    overall=1
    continue
  fi

  echo "OK [V${expected}] tripped on $base"
done

exit "$overall"
