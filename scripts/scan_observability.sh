#!/usr/bin/env bash
# Scan for Observability signals (Pillar 6)
# Helps the agent find runtime/production observability config — not a substitute for judgment.

REPO="${1:-.}"
cd "$REPO" 2>/dev/null || { echo "Cannot access $REPO"; exit 1; }

echo "=== Pillar 6: Observability ==="
echo ""

echo "-- Structured logging --"
grep -RIl --include='package.json' --include='requirements*.txt' --include='pyproject.toml' --include='go.mod' --include='Cargo.toml' \
  -E 'pino|winston|bunyan|structlog|loguru|serilog|zap|slog|zerolog|tracing-subscriber' . 2>/dev/null | head -10
find . -maxdepth 4 -name 'logger.*' -o -name 'logging.*' 2>/dev/null | grep -v node_modules | head -10

echo ""
echo "-- Error tracking (Sentry/Bugsnag/Rollbar) --"
grep -RIl --include='package.json' --include='requirements*.txt' --include='pyproject.toml' --include='go.mod' \
  -E '@sentry/|sentry-sdk|@bugsnag/|rollbar|raygun' . 2>/dev/null | head -5
find . -maxdepth 4 -name 'sentry.*.config.*' -o -name 'instrumentation.*' -o -name '.sentryclirc' 2>/dev/null | grep -v node_modules | head -10

echo ""
echo "-- Health check endpoints --"
grep -RIn --include='*.ts' --include='*.tsx' --include='*.js' --include='*.py' --include='*.go' --include='*.rs' \
  -E '/health(z|check)?|/ready(z)?|/livez' . 2>/dev/null | grep -v node_modules | grep -v '\.test\.' | head -10

echo ""
echo "-- Metrics collection (OTel/Prometheus/DD) --"
grep -RIl --include='package.json' --include='requirements*.txt' --include='pyproject.toml' --include='go.mod' \
  -E '@opentelemetry|prom-client|prometheus_client|datadog|dd-trace|newrelic|statsd' . 2>/dev/null | head -5
find . -maxdepth 4 -name 'otel.config.*' -o -name 'prometheus.yml' 2>/dev/null | head -5

echo ""
echo "-- Distributed tracing --"
grep -RIl --include='package.json' --include='requirements*.txt' --include='go.mod' \
  -E '@opentelemetry/api|opentelemetry-api|jaeger|zipkin' . 2>/dev/null | head -5

echo ""
echo "-- Alerting configuration --"
find . -maxdepth 4 -name 'alerts.yml' -o -name 'alerts.yaml' -o -name '*alert-rules*' 2>/dev/null | head -5
grep -RIl --include='*.tf' -E 'pagerduty|opsgenie|datadog_monitor' . 2>/dev/null | head -5

echo ""
echo "-- Runbooks documented --"
for d in docs/runbooks docs/operations runbooks ops/runbooks; do
  [ -d "$d" ] && echo "./$d/ ($(find "$d" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ') files)"
done
find . -maxdepth 3 -iname 'RUNBOOK*' 2>/dev/null | head -5

echo ""
echo "-- Code quality dashboard --"
find . -maxdepth 2 -name 'sonar-project.properties' -o -name '.codeclimate.yml' -o -name '.codacy.yml' 2>/dev/null
grep -RIl --include='*.yml' --include='*.yaml' 'sonarcloud\|sonar-scanner\|codeclimate\|codacy' .github/ 2>/dev/null | head -5

echo ""
echo "-- Profiling instrumentation --"
grep -RIl --include='package.json' --include='requirements*.txt' --include='go.mod' \
  -E 'py-spy|austin-tui|pprof|clinic|0x|@datadog/pprof' . 2>/dev/null | head -5

echo ""
echo "-- Circuit breakers --"
grep -RIl --include='package.json' --include='requirements*.txt' --include='go.mod' --include='pom.xml' \
  -E 'opossum|resilience4j|hystrix|polly|gobreaker|tenacity' . 2>/dev/null | head -5

echo ""
echo "-- Error → insight pipeline (Sentry → tracker) --"
grep -RIl --include='*.yml' --include='*.yaml' -E 'sentry.*webhook|sentry-issue|on:.*workflow_dispatch.*sentry' .github/ 2>/dev/null | head -5
find . -maxdepth 4 -name 'sentry-webhook*' 2>/dev/null | grep -v node_modules | head -5
