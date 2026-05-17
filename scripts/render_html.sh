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
