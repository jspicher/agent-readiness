#!/usr/bin/env bash
# render_html.sh <audit-data.json> <output.html>
# Embeds the JSON into the template by replacing the placeholder line
# (containing `<!--AUDIT_DATA_JSON-->`) with the JSON file's contents.
# No transform, no validation -- Claude is responsible for producing well-formed JSON.

set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <audit-data.json> <output.html>" >&2
  exit 1
fi

data_file="$1"
output="$2"
template="$(dirname "$0")/../assets/report-template.html"

if [ ! -f "$template" ]; then
  echo "Template not found at $template" >&2
  exit 2
fi
if [ ! -f "$data_file" ]; then
  echo "Audit data not found at $data_file" >&2
  exit 3
fi

# Pre-check: validate the audit JSON's `top_actions` shape. The HTML renderer
# reads `act.title`, `act.body`, and `act.feature_refs`; if those keys are
# missing the report renders three blank rows with no visible warning. Fail
# loudly here instead. See ERR-20260517-008.
#
# We accept either Python or jq for the validation step. If neither is
# available we skip with a soft warning -- the renderer will still run, but
# silent-empty top_actions is a known footgun.
if command -v python3 >/dev/null 2>&1; then
  python3 - "$data_file" <<'PY'
import json, sys
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)
actions = d.get('top_actions')
if actions is None:
    sys.exit(0)
if not isinstance(actions, list):
    print(f"render_html.sh: top_actions must be a list, got {type(actions).__name__}", file=sys.stderr)
    sys.exit(7)
required = {'title', 'body'}
for i, a in enumerate(actions):
    if not isinstance(a, dict):
        print(f"render_html.sh: top_actions[{i}] must be an object", file=sys.stderr)
        sys.exit(7)
    missing = required - a.keys()
    if missing:
        print(f"render_html.sh: top_actions[{i}] is missing required keys {sorted(missing)}; the renderer reads .title/.body/.feature_refs and silently renders blank rows otherwise. Have: {sorted(a.keys())}", file=sys.stderr)
        sys.exit(7)
    if not a['title'] or not a['body']:
        print(f"render_html.sh: top_actions[{i}] has empty title or body", file=sys.stderr)
        sys.exit(7)
    refs = a.get('feature_refs')
    if refs is not None and not isinstance(refs, list):
        print(f"render_html.sh: top_actions[{i}].feature_refs must be a list when present", file=sys.stderr)
        sys.exit(7)
PY
elif command -v jq >/dev/null 2>&1; then
  jq -e '
    (.top_actions // []) as $a
    | if ($a | type) != "array" then "top_actions must be a list" | halt_error(7) else . end
    | $a | to_entries | map(
        if (.value | type) != "object" then "top_actions[\(.key)] must be an object" | halt_error(7)
        elif (.value.title // "") == "" then "top_actions[\(.key)] missing/empty title" | halt_error(7)
        elif (.value.body // "") == "" then "top_actions[\(.key)] missing/empty body" | halt_error(7)
        else . end
      )
  ' "$data_file" >/dev/null || exit $?
else
  echo "render_html.sh: warning -- neither python3 nor jq found; skipping top_actions schema check" >&2
fi

# Pre-check: template must contain exactly one placeholder line, or the substitution is a no-op.
placeholder_count="$(grep -c '<!--AUDIT_DATA_JSON-->' "$template" || true)"
if [ "$placeholder_count" -lt 1 ]; then
  echo "Template at $template is missing the <!--AUDIT_DATA_JSON--> placeholder" >&2
  exit 4
fi

# Escape `</script` so the JSON cannot break out of its <script type="application/json"> block.
# (Per HTML5, the only sequence that ends such a block is `</script`.)
tmp_safe="$(mktemp -t agent-readiness-data.XXXXXX)"
trap 'rm -f "$tmp_safe"' EXIT
sed -e 's,</script,<\\/script,g' "$data_file" > "$tmp_safe"

# Use sed's `r` (read-and-insert) + `d` (delete) to swap the placeholder line for the
# file contents. This avoids interpreting any character in the JSON as regex metasyntax,
# which is fatal with `awk` (gsub treats `&` and `\` specially) and with `sed s,A,B,`.
# The placeholder MUST be on its own line in the template.
sed -e "/<!--AUDIT_DATA_JSON-->/{
  r $tmp_safe
  d
}" "$template" > "$output"

# Post-check: substitution must have happened. If the placeholder still appears in the
# output, OR if the output is no larger than the template, something is wrong.
if grep -q '<!--AUDIT_DATA_JSON-->' "$output"; then
  echo "Substitution failed: placeholder still present in $output" >&2
  exit 5
fi
out_bytes="$(wc -c < "$output")"
tpl_bytes="$(wc -c < "$template")"
if [ "$out_bytes" -le "$tpl_bytes" ]; then
  echo "Substitution failed: output ($out_bytes B) is not larger than template ($tpl_bytes B)" >&2
  exit 6
fi

echo "Wrote $output ($out_bytes bytes)"
