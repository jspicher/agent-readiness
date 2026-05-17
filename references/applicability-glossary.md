# Applicability Glossary

## Purpose

Several criteria in `references/criteria.md` are **conditional** -- they apply
only when the target repo has a corresponding subsystem (a database, a
production deployment, a flag system, etc.). When the subsystem is absent,
the criterion is marked `—` (N/A) rather than failed.

SKILL.md Step 3 step 5 requires every N/A row to carry a `rationale_kind`
drawn from a fixed enum, and `references/audit-data-schema.md` enforces this
on the JSON sibling. The validator's `[V07]` check fails the audit if an N/A
row lacks a `rationale_kind`.

This glossary defines:

1. The three `rationale_kind` values for N/A rows.
2. For the most common `subsystem_absence` triggers, **a specific detection
   command** so the auditor can prove the subsystem really is absent.
3. A rationale template the auditor can paste in (after substituting the
   evidence string).

The three N/A kinds:

| `rationale_kind` | Meaning | Examples |
|---|---|---|
| `profile_gate` | N/A because Step 0 inferred a profile dimension that excludes the criterion | #76 Code of conduct (`accepts_external_contributors=false`); #60 Stale issue/PR (`team_scale=solo AND visibility=private`) |
| `missing_precondition` | N/A because of a non-evidence, **process-level** constraint that's unsatisfiable on this repo's platform/plan | #54 Branch protection on a GitHub Free private repo (returns 403) |
| `subsystem_absence` | N/A because the repo demonstrably has no instance of the gated subsystem | #49 N+1 detection (no DB); #100 Monorepo orch (single-package repo); #118 Profiling (no perf-sensitive code path) |

## `profile_gate`

Used when a Step 0 profile dimension excludes the criterion. The auditor must
cite the specific profile value that triggered the gate. See SKILL.md L112 for
the full list of profile-gated criteria (#5, #13, #60, #76, #84, #85, #106,
#108).

Rationale template:

> `N/A: profile_gate. {dimension}={value} per Step 0 ({evidence cited there}).`

Example for #76 Code of conduct:

> `N/A: profile_gate. accepts_external_contributors=false per Step 0 (visibility=private + LICENSE absent).`

## `missing_precondition`

Used for **non-evidence-based** preconditions -- a platform or plan limitation
that the criterion itself cannot fix. The canonical case today is:

- **#54 Branch protection on GitHub Free private repos.** `gh api
  repos/{owner}/{repo}/rules/branches/main` returns HTTP 403 ("Upgrade to
  GitHub Pro"). The repo physically cannot satisfy the criterion until the
  plan changes; failing it would be checklist theater.

Rationale template:

> `N/A: missing_precondition. {one-line description of the platform/plan limit}. {command output or doc link proving the limit}.`

## `subsystem_absence`

The big one. Use when the repo has no instance of the gated subsystem.
**Every `subsystem_absence` rationale must cite a concrete detection
command** -- otherwise it's indistinguishable from "I didn't look."

The detection commands below assume `rg` (ripgrep) is available. If only
`grep -R` is available, swap in `grep -RIl --exclude-dir={node_modules,dist,build,.next,coverage,.git,vendor,target}`.

Cross-reference: `references/criteria.md` (per-criterion evidence patterns),
`references/audit-data-schema.md` (rationale_kind enum spec).

### DB-using app  (criteria #49, #109)

An application that owns and reads/writes data in a relational or document
database. The agent uses this dimension to know whether N+1 detection,
schema migrations, and ORM scrubbing apply.

**Detection command:**

```bash
rg -l --type-add 'cfg:*.{toml,json,yml,yaml,env,prisma}' --type cfg \
  -e 'postgres|prisma|sequelize|knex|drizzle|sqlalchemy|mongoose|mysql|sqlite|redis|DATABASE_URL' .
```

Or look for: a `migrations/` directory, a `schema.prisma` file, an
`alembic.ini`, a `DATABASE_URL` env var in `.env*`, a `database.yml` config.

**Rationale template:**

> `N/A: subsystem_absence. Ran <command> and found no DB integration: no migrations/, no DATABASE_URL, no ORM dependency in package.json/requirements.txt.`

### Monorepo  (criteria #100, #101)

A repository containing multiple independently-versioned packages or apps
that share tooling. Monorepo orchestration and version-drift detection only
make sense when there are multiple things to keep in sync.

**Detection command:**

```bash
# (a) workspace declarations
jq -r '.workspaces' package.json 2>/dev/null
# (b) packages/ or apps/ with their own manifests
find packages apps -maxdepth 2 -name 'package.json' -not -path '*/node_modules/*' 2>/dev/null
# (c) Cargo/Go workspace
grep -l '\[workspace\]' Cargo.toml 2>/dev/null
test -f go.work && echo 'go workspace'
```

A "no" on all four means single-package.

**Rationale template:**

> `N/A: subsystem_absence. No workspace config (package.json workspaces, Cargo [workspace], go.work) and no packages/ or apps/ subdirs with their own manifests. Single-package repo.`

### Multi-service / production system  (criteria #70, #71, #113, #114, #115, #116)

The dimensions group: a production-deployed application that emits requests
or runs as more than one process. Distributed tracing, metrics, alerting,
runbooks, progressive rollout, and rollback automation all assume there's
something in production to observe and recover.

**Detection command:**

```bash
# Deploy targets
ls -1 vercel.json fly.toml render.yaml netlify.toml .platform/ \
       Dockerfile docker-compose.yml docker-compose.prod.yml \
       k8s/ helm/ 2>/dev/null
# CI deploy workflows
rg -l 'deploy|release|prod' .github/workflows/ 2>/dev/null
# Observability dependencies
rg -l 'sentry|opentelemetry|datadog|newrelic|prometheus|pino|winston' \
   package.json requirements.txt go.mod Cargo.toml 2>/dev/null
```

If **none** of: deploy config + CI deploy workflow + observability SDK -- it's
not a production system. (A `Dockerfile` alone is not enough; lots of libs
ship a Dockerfile for dev convenience.)

**Rationale template:**

> `N/A: subsystem_absence. No deploy config (vercel.json/fly.toml/k8s), no CI deploy workflow, no observability SDK. Repo appears to be a library/CLI/tool with no production runtime.`

### Web-facing app  (criterion #88 DAST)

An app accepting requests over HTTP from untrusted sources with a meaningful
attack surface (auth, multi-tenant data, payment flows, APIs accepting
arbitrary input). DAST scanning is N/A for static SSG sites, marketing
pages, or directory listings with no input beyond a contact form.

**Detection command:**

```bash
# Web framework + meaningful surface area
rg -l 'NextAuth|next-auth|@auth/|passport|express-session|fastify-secure-session|django.contrib.auth|devise' . 2>/dev/null
# Payment SDKs
rg -l 'stripe|braintree|paypal-sdk|plaid' package.json requirements.txt go.mod 2>/dev/null
# API surface
rg -l '/api/|app/api|/v1/|/graphql' . 2>/dev/null
```

If the repo has a deploy target but **none** of the three above (no auth, no
payments, no API surface), DAST is N/A.

**Rationale template:**

> `N/A: subsystem_absence. Web app but no auth SDK (NextAuth/passport/devise), no payment SDK, no /api routes. Static-marketing surface; DAST cost outweighs threat.`

### User-data / PII-handling app  (criteria #89, #90)

An app that stores or processes personally identifiable information about
end users (not internal team members).

**Detection command:**

```bash
# Auth + user model (a hint that users exist)
rg -l 'user.id|userId|email.*@|hash.*password|bcrypt|argon2' src/ app/ 2>/dev/null
# User-data schema
rg -l 'first_name|last_name|date_of_birth|phone|address|ssn|tax_id' \
   migrations/ schema.prisma db/schema.rb 2>/dev/null
# Privacy infrastructure (its presence is positive evidence, not absence)
rg -l 'gdpr|ccpa|privacy|cookie-banner|consent' . 2>/dev/null
```

A repo with auth + user model + schema columns for PII is a user-data app.
A repo with **none** of these is not.

**Rationale template:**

> `N/A: subsystem_absence. No auth SDK, no user model in migrations, no PII columns (name/email/phone/address). Not a user-data app.`

### Feature flag system present  (criterion #68 Dead flag detection)

A configured flag system the agent could be checking for dead flags.

**Detection command:**

```bash
rg -l 'LaunchDarkly|launchdarkly|statsig|unleash|growthbook|posthog.*feature_flag' \
   package.json requirements.txt go.mod 2>/dev/null
# Or a custom flag registry
find . -maxdepth 4 \( -name 'flags.json' -o -name 'feature-flags.*' -o -path '*config/flags*' \) -not -path '*/node_modules/*' 2>/dev/null
```

**Rationale template:**

> `N/A: subsystem_absence. No flag SDK (LaunchDarkly, Statsig, Unleash, GrowthBook, PostHog flags) and no flags.json / feature-flags.* registry. No flag system to inventory.`

### External-dependency-heavy  (criterion #119 Circuit breakers)

An app that makes synchronous calls to many remote services and would
benefit from resilience patterns (retries, timeouts, circuit breakers).

**Detection command:**

```bash
# HTTP client usage at scale
rg -c 'fetch\(|axios\.|http\.Client|requests\.get|httpx\.|got\.|grpc' src/ app/ 2>/dev/null \
  | awk -F: '{s+=$2} END {print "client calls:", s+0}'
# Resilience deps (their presence is positive evidence)
rg -l 'opossum|polly|resilience4j|hystrix|tenacity|cockatiel' package.json pom.xml build.gradle 2>/dev/null
```

If the count of HTTP client calls is small (< ~20) and there are no resilience
deps, circuit breakers are N/A.

**Rationale template:**

> `N/A: subsystem_absence. {N} HTTP client call sites found, none to external paid APIs; no opossum/polly/resilience4j in deps. Not external-dependency-heavy.`

### Perf-sensitive app  (criterion #118 Profiling)

An app where latency or throughput is on the critical path (real-time
systems, ad serving, search, high-traffic APIs).

**Detection command:**

```bash
# Benchmarks or perf budgets (positive evidence)
find . -maxdepth 4 \( -name 'bench' -o -name 'benchmarks' -o -name '*_bench_test.go' \) -not -path '*/node_modules/*' 2>/dev/null
rg -l 'lighthouse-ci|web-vitals|core-web-vitals|perf-budget' . 2>/dev/null
# Profilers in deps (positive evidence)
rg -l 'py-spy|pprof|--prof|async-profiler|dd-trace.*profiling' . 2>/dev/null
```

If no benchmarks exist, no perf budget is enforced, and there's no real-time
constraint documented in README/AGENTS.md, the app is not perf-sensitive.

**Rationale template:**

> `N/A: subsystem_absence. No bench/ dir, no lighthouse-ci or web-vitals config, no profiler deps. App is not on a latency-critical path per README/AGENTS.md.`

### Devcontainer present  (criterion #95 Devcontainer runnable)

The devcontainer-runnable criterion only fires when a devcontainer exists at
all. Without one, #95 has nothing to verify.

**Detection command:**

```bash
test -f .devcontainer/devcontainer.json && echo present || echo absent
```

**Rationale template:**

> `N/A: subsystem_absence. No .devcontainer/devcontainer.json. Nothing to verify.`

### Jurisdiction  (criterion #90 Privacy compliance)

Even when an app handles user data, the privacy-compliance criterion
specifically asks about GDPR/CCPA infrastructure. A repo that has user data
but operates outside those jurisdictions (or hasn't yet been deployed to
serve users in them) may legitimately N/A this.

**Detection rule:** the auditor should look at the repo's README, deploy
config (target regions), and any privacy policy doc for a declared
jurisdiction. If the repo is pre-launch or explicitly scoped to a
non-GDPR/non-CCPA region, mark N/A.

**Rationale template:**

> `N/A: subsystem_absence. README declares "{region}-only" scope; no EU/CA deployment configured. GDPR/CCPA infrastructure not yet in scope.`

(This is the weakest of the dimensions -- the auditor relies on declarative
evidence rather than code structure. Default to **strict** if the
jurisdiction is unknown.)

---

## See also

- `SKILL.md` Step 0 -- profile dimensions and detection rules.
- `SKILL.md` Step 3 step 5 -- rationale required for every status.
- `references/criteria.md` -- per-criterion evidence patterns and the
  "Conditional features" + "Profile-driven gates" tables.
- `references/audit-data-schema.md` -- `rationale_kind` enum + JSON shape.
- `scripts/validate_audit_data.py` `[V07]` -- the validator check that
  enforces a `rationale_kind` on every N/A row.
