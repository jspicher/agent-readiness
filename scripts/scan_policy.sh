#!/usr/bin/env bash
# Scan for Policy & Governance signals (Pillar 4)
# Helps the agent find relevant files — not a substitute for judgment.

REPO="${1:-.}"
. "$(dirname "$0")/_lib.sh"
cd "$REPO" 2>/dev/null || { echo "Cannot access $REPO"; exit 1; }

echo "=== Pillar 4: Policy & Governance ==="
echo ""

echo "-- .gitignore --"
if [ -f .gitignore ]; then
  lines=$(wc -l < .gitignore | tr -d ' ')
  echo "./.gitignore ($lines lines)"
  # Check for agent-aware entries
  agent_entries=$(grep -ci 'cursor\|claude\|copilot\|\.agent\|\.mcp' .gitignore 2>/dev/null)
  [ "$agent_entries" -gt 0 ] && echo "  ($agent_entries agent-related ignore entries)"
else
  echo "  (not found)"
fi

echo ""
echo "-- License --"
find . -maxdepth 1 -iname 'LICENSE*' -o -iname 'COPYING*' -o -iname 'MIT-LICENSE' 2>/dev/null | sort

echo ""
echo "-- Code ownership --"
find . -maxdepth 3 -name 'CODEOWNERS' 2>/dev/null | sort
if [ -f CODEOWNERS ] || [ -f .github/CODEOWNERS ] || [ -f docs/CODEOWNERS ]; then
  f=$(find . -maxdepth 3 -name 'CODEOWNERS' 2>/dev/null | head -1)
  rules=$(grep -c '^[^#]' "$f" 2>/dev/null | tr -d ' ')
  echo "  ($rules ownership rules)"
fi

echo ""
echo "-- Security policy --"
find . -maxdepth 3 -iname 'SECURITY*' 2>/dev/null | sort

echo ""
echo "-- Code of conduct --"
find . -maxdepth 2 -iname 'CODE_OF_CONDUCT*' -o -iname 'CONDUCT*' 2>/dev/null | sort

echo ""
echo "-- AI usage policy --"
# Check common locations for AI policy mentions
for f in AGENTS.md CLAUDE.md CONTRIBUTING.md; do
  if [ -f "$f" ]; then
    ai_mentions=$(grep -ci 'ai policy\|ai usage\|agent boundar\|ai contribut\|llm\|copilot' "$f" 2>/dev/null)
    [ "$ai_mentions" -gt 0 ] && echo "  $ai_mentions AI policy references in $f"
  fi
done

echo ""
echo "-- Secrets management --"
if [ -d .github/workflows ]; then
  secrets_refs=$(grep -roh '\${{ secrets\.[A-Z_]*' .github/workflows/ 2>/dev/null | sort -u | wc -l | tr -d ' ')
  echo "  $secrets_refs distinct secrets referenced in CI"
fi
find . -maxdepth 2 -name '.env.example' -o -name '.env.template' 2>/dev/null | sort
find . -maxdepth 2 -name 'vault.hcl' -o -name '.vault-token' 2>/dev/null | sort

echo ""
echo "-- Security scanning --"
if [ -d .github/workflows ]; then
  for scanner in codeql snyk trivy gosec semgrep; do
    grep -ril "$scanner" .github/workflows/ 2>/dev/null | while read f; do
      echo "  $scanner in $(basename "$f")"
    done
  done
fi
find . -maxdepth 2 -name '.snyk' -o -name '.trivyignore' 2>/dev/null | sort

echo ""
echo "-- Git attributes --"
if [ -f .gitattributes ]; then
  lines=$(wc -l < .gitattributes | tr -d ' ')
  echo "./.gitattributes ($lines lines)"
  linguist=$(grep -c 'linguist' .gitattributes 2>/dev/null)
  [ "$linguist" -gt 0 ] && echo "  ($linguist linguist overrides)"
  lfs=$(grep -c 'filter=lfs' .gitattributes 2>/dev/null)
  [ "$lfs" -gt 0 ] && echo "  ($lfs LFS-tracked patterns)"
else
  echo "  (not found)"
fi

echo ""
echo "-- Contributor agreement --"
find . -maxdepth 2 -iname 'DCO*' -o -iname 'CLA*' 2>/dev/null | sort
for f in CONTRIBUTING.md .github/workflows/*.yml; do
  [ -f "$f" ] && grep -qi 'signed-off-by\|DCO\|CLA\|contributor license' "$f" 2>/dev/null \
    && echo "  DCO/CLA reference in $(basename "$f")"
done

echo ""
echo "-- Governance model --"
find . -maxdepth 2 -iname 'GOVERNANCE*' -o -iname 'MAINTAINERS*' -o -iname 'OWNERS*' 2>/dev/null | sort

echo ""
echo "-- CI workflow validation --"
if [ -d .github/workflows ]; then
  grep -rl 'actionlint' .github/workflows/ 2>/dev/null | head -3
fi
if [ -f .pre-commit-config.yaml ]; then
  grep -q 'actionlint' .pre-commit-config.yaml 2>/dev/null && echo "  actionlint in pre-commit"
fi

echo ""
echo "-- Environment separation --"
find . -maxdepth 2 -name '.env.test' -o -name '.env.production' -o -name '.env.staging' \
  -o -name '.env.development' 2>/dev/null | sort
for d in config/environments environments; do
  [ -d "$d" ] && echo "./$d/ ($(ls "$d" | wc -l | tr -d ' ') environments)"
done

echo ""
echo "-- Secret scanning (continuous) --"
find_prune . -maxdepth 3 \( -name '.gitleaks.toml' -o -name 'gitleaks.toml' -o -name 'trufflehog*' \) -print 2>/dev/null | head -5
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='*.yml' --include='*.yaml' 'gitleaks\|trufflehog\|detect-secrets' .github/workflows/ 2>/dev/null | head -5

echo ""
echo "-- Sensitive data log scrubbing --"
grep -RIn "${EXCLUDE_GREP_ARGS[@]}" --include='*.ts' --include='*.js' --include='*.py' --include='*.go' \
  -E 'redact|scrub|sanitize|mask|filter.*pii' . 2>/dev/null | grep -i 'log\|logger' | head -5

echo ""
echo "-- Minimum dependency release age --"
[ -f renovate.json ] && grep -l 'minimumReleaseAge\|stabilityDays' renovate.json 2>/dev/null
[ -f .renovaterc.json ] && grep -l 'minimumReleaseAge\|stabilityDays' .renovaterc.json 2>/dev/null

echo ""
echo "-- DAST scanning --"
grep -RIl "${EXCLUDE_GREP_ARGS[@]}" --include='*.yml' --include='*.yaml' 'zaproxy\|owasp.zap\|nuclei\|burp' .github/workflows/ 2>/dev/null | head -3

echo ""
echo "-- Privacy compliance / cookie consent --"
grep -RIn "${EXCLUDE_GREP_ARGS[@]}" --include='*.tsx' --include='*.ts' --include='*.jsx' --include='*.js' \
  -E 'CookieConsent|CookieBanner|cookieconsent|gdpr|ccpa' . 2>/dev/null | head -5

echo ""
echo "-- AI usage policy --"
[ -f AGENTS.md ] && grep -l -i 'ai.usage\|ai.policy\|do not\|forbidden\|never' AGENTS.md 2>/dev/null
find . -maxdepth 2 -iname 'AI_POLICY*' -o -iname 'AGENT_POLICY*' 2>/dev/null | head -3
