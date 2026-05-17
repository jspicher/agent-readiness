[Readiness Fix] <REPO_NAME> Environment Separation

Fix the failing signal: Environment Separation ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Environment Separation
**Score**: [0/1]
**Description**: Distinct configs for dev/test/prod
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Environment separation — check that the repo distinguishes development, test, and production configuration as **separate, checked-in artifacts**, not a single shared `.env` that gets edited per machine. PASS requires at least one of:

1. **Per-environment dotfiles** following the framework's documented loading order:
   - Next.js: `.env`, `.env.development`, `.env.test`, `.env.production`, with `.env.development.local` / `.env.production.local` for machine overrides. `.env.test` is NOT loaded by `.local` overrides by design (https://nextjs.org/docs/app/guides/environment-variables#test-environment-variables).
   - Vite: `.env`, `.env.development`, `.env.production`, plus optional `.env.[mode]` for custom modes (`vite build --mode staging` → `.env.staging`). `VITE_` prefix required to expose to client (https://vite.dev/guide/env-and-mode).
   - Rails: `config/environments/development.rb`, `test.rb`, `production.rb` + `config/credentials/{development,test,production}.yml.enc` encrypted per env (https://guides.rubyonrails.org/configuring.html).
   - Node generic / dotenv-flow: `.env`, `.env.local`, `.env.{NODE_ENV}`, `.env.{NODE_ENV}.local` (https://github.com/kerimdzhanov/dotenv-flow).
2. **Per-environment config directory**: `config/development.{js,ts,yaml}`, `config/test.*`, `config/production.*` loaded by env (e.g. node-config, Python `settings/{dev,test,prod}.py`). Files must contain real environment-specific values (different DB URLs, log levels, feature flags), not be identical stubs.
3. **Platform-managed env separation** with a checked-in manifest: Vercel `vercel.json` + `vercel env pull --environment={development,preview,production}` documented in README; Netlify `netlify.toml` `[context.production]` / `[context.deploy-preview]` / `[context.branch-deploy]` blocks (https://docs.netlify.com/build/configure-builds/file-based-configuration/#deploy-contexts); GitHub Environments referenced by `.github/workflows/*.yml` `environment:` keys (cross-references signal #63 GitHub Environments).
4. **Container/orchestration overlays**: `docker-compose.yml` + `docker-compose.override.yml` (dev) + `docker-compose.prod.yml`, or Kubernetes Kustomize `overlays/{dev,staging,prod}/`. Overlays must change real values, not just labels.

This signal verifies the **structure exists and is loaded correctly**, not that secrets are filled in. Real secret values belong in `.env.*.local` (gitignored) or a secret manager — see signal #88 Secrets Management.

Also verify:
- `.gitignore` excludes `.env`, `.env.local`, `.env.*.local`, `.env.production` (if it contains real secrets) — but does NOT exclude `.env.example`, `.env.test`, `.env.production.example`, or `.env.development.example` (these are templates and MUST be committed).
- The framework's actual loading order matches what's on disk. A `.env.production` file in a Vite repo without `mode=production` build flag is dead config.
- At least one variable differs between dev and prod (DB URL, API host, log level, NEXT_PUBLIC_ENV) — identical files across environments is a stub.

A README sentence saying "set NODE_ENV=production for prod" with no per-env files is documentation, not separation, and FAILs this signal.

## Your Task

1. Explore the repository to identify the framework (Next.js, Vite, Rails, Express, etc.), the current dotenv files, and any `config/` directory. List every `.env*`, `config/*.{js,ts,yaml,rb}`, `docker-compose*.yml`, `vercel.json`, `netlify.toml`, and `.github/workflows/*.yml` referencing `environment:`.
2. Identify which environments the repo actually needs — at minimum development + test + production. CI workflows that run `npm test` need a `.env.test` so tests don't hit the dev DB.
3. Make **substantive improvements** by creating the per-env structure the framework expects:
   - Add `.env.example` (root template, every variable listed with safe placeholder values and a one-line comment).
   - Add `.env.test` (committed, contains test-safe values: in-memory or test-DB URLs, fake API keys, `LOG_LEVEL=error`, feature flags fixed for deterministic tests).
   - Add `.env.production.example` (committed, documents every prod variable; real values live in the secret manager or platform env, never here).
   - If the repo uses `.env.development`, ensure it loads only safe defaults (local DB, mock API endpoints) and create `.env.development.example` if developers need to customize.
4. Update `.gitignore` to ignore `.env`, `.env.local`, `.env.*.local`, and `.env.production` (the file with real secrets), but explicitly UN-ignore `.env.example`, `.env.test`, `.env.production.example` with `!` rules if a broader pattern would catch them.
5. Verify loading order: for Next.js run `next info` and confirm the `.env` chain resolves; for Vite run `vite --mode test` and confirm it reads `.env.test`; for Rails run `RAILS_ENV=test bin/rails runner 'puts Rails.env'`. Confirm at least one var differs between envs (e.g. `DATABASE_URL` in `.env.test` points to `test_db`, in `.env.production.example` points to `${PROD_DATABASE_URL}`).
6. Document the env strategy in `README.md` or `AGENTS.md`: which file loads when, where real secrets come from, how to add a new variable (add to `.env.example` + `.env.test` + `.env.production.example` in the same PR).
7. Keep changes focused on this signal — do not refactor unrelated config.
8. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** identical files across environments. If `.env.development`, `.env.test`, and `.env.production` have the same values, you have one environment with three filenames. The `DATABASE_URL`, API base URL, log level, or at least one feature flag MUST differ.
- **NO** committing `.env.production` with real secrets. Real production values belong in the platform secret store (Vercel env vars, AWS Secrets Manager, GitHub Environment secrets) or an encrypted file (`.env.production.gpg`, Rails encrypted credentials). The committed artifact is `.env.production.example` — placeholders only.
- **NO** committing `.env` (the unscoped default) with real values. It loads in every environment and overrides nothing; secrets there leak into CI logs, test snapshots, and prod accidentally.
- **NO** silent prod fallback to dev defaults. Code like `const url = process.env.STRIPE_KEY ?? "sk_test_..."` is a footgun: a missing prod variable charges test cards to test accounts and the bug surfaces only after the first real customer. Fail loud — throw at startup if a required prod var is missing (use `zod`/`envalid`/`@t3-oss/env-nextjs` to validate at boot).
- **NO** missing `.env.test`. Tests inheriting dev env vars hit the dev DB, corrupt fixtures, drain rate-limited API quotas, and produce flaky results that pass locally and fail in CI (or vice versa). Every test framework run (`jest`, `vitest`, `pytest`, `rspec`) MUST load `.env.test` before importing application code.
- **NO** single `.env` shared across all environments with comments like `# uncomment for prod`. Manual file editing is not separation — one developer forgets to re-comment a line and prod gets the wrong DB URL.
- **NO** putting `NEXT_PUBLIC_*` / `VITE_*` secrets in any env file. Client-exposed variables are bundled into the JS and shipped to every browser; they MUST be public-safe (analytics IDs, feature flags), never API keys.
- **NO** `.gitignore` rules that accidentally exclude templates. `*.env*` ignores `.env.example` too. Use specific rules (`.env`, `.env.local`, `.env.*.local`) or explicit allow patterns (`!.env.example`).

Examples of BAD fixes:
- Creating `.env.test` as a copy of `.env.development` — tests now share dev DB; first parallel test run corrupts dev data.
- Committing `.env.production` containing `STRIPE_SECRET_KEY=sk_live_abc123...` — credential leak the moment the repo is cloned, mirrored, or scraped by a leaked-secrets bot. Recovery requires key rotation across every consumer.
- Adding `.env.production.example` with the same values as `.env.example` — no signal to the next developer about which variables are prod-only or have different shapes (e.g. `LOG_LEVEL=debug` in dev vs `LOG_LEVEL=warn` in prod).
- A Next.js repo with `.env.production` but the build runs `next build` without `NODE_ENV=production` set — Next.js defaults `NODE_ENV` to `production` for `next build`, but custom server invocations don't, so `.env.development` wins silently. Verify with `console.log(process.env.NODE_ENV)` in the build output.
- Adding a `config/` directory with `development.js`, `test.js`, `production.js` that all `module.exports = require('./default')` — three pointers to the same config.

Examples of GOOD fixes:

**`.env.example`** (committed, root template — every var, safe placeholders, comments):
```bash
# === Application ===
NODE_ENV=development
PORT=3000
LOG_LEVEL=debug                       # debug | info | warn | error

# === Database ===
# Local Postgres via docker-compose. Use 127.0.0.1, NOT localhost, on Windows.
DATABASE_URL=postgres://app:app@127.0.0.1:5432/app_dev

# === Auth ===
# Generate with: openssl rand -base64 32
NEXTAUTH_SECRET=replace-me-with-openssl-rand
NEXTAUTH_URL=http://localhost:3000

# === Third-party APIs ===
# Get a test key at https://dashboard.stripe.com/test/apikeys
STRIPE_SECRET_KEY=sk_test_replace_me
STRIPE_WEBHOOK_SECRET=whsec_replace_me

# === Public (bundled into client JS — must be safe to expose) ===
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_POSTHOG_KEY=phc_replace_me
```

**`.env.test`** (committed — deterministic, isolated, no real services):
```bash
NODE_ENV=test
PORT=0                                # let the test server pick a free port
LOG_LEVEL=error                       # silence logs in test output

# Isolated test DB — CI provisions this; locally use docker-compose service `postgres-test`
DATABASE_URL=postgres://test:test@127.0.0.1:5433/app_test

# Test-only secrets — never used in any real environment, safe to commit
NEXTAUTH_SECRET=test-secret-do-not-use-anywhere-else-32-chars
NEXTAUTH_URL=http://localhost:3000

# Stripe test-mode keys for fixtures (rotate if leaked, but no $ impact)
STRIPE_SECRET_KEY=sk_test_FAKE_FIXTURE_KEY_FOR_CI
STRIPE_WEBHOOK_SECRET=whsec_test_fixture

NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_POSTHOG_KEY=phc_test_disabled
```

**`.env.production.example`** (committed — documents shape, NO real values):
```bash
NODE_ENV=production
PORT=${PORT:-3000}                    # platform usually injects PORT
LOG_LEVEL=warn

# Real value lives in: Vercel Project Settings → Environment Variables → Production
# Pull locally with: vercel env pull --environment=production .env.production.local
DATABASE_URL=                         # postgres://USER:PASS@HOST:5432/DB?sslmode=require
DATABASE_POOL_MAX=20                  # prod-specific; not in dev

NEXTAUTH_SECRET=                      # openssl rand -base64 32 (different from dev!)
NEXTAUTH_URL=https://app.example.com

STRIPE_SECRET_KEY=                    # sk_live_... — Stripe Dashboard → Live mode → API keys
STRIPE_WEBHOOK_SECRET=                # whsec_... — Stripe Dashboard → Webhooks → Signing secret

NEXT_PUBLIC_APP_URL=https://app.example.com
NEXT_PUBLIC_POSTHOG_KEY=              # phc_... — PostHog Project → API key
NEXT_PUBLIC_SENTRY_DSN=               # prod-only — error reporting
```

**`.gitignore`** (the exact lines that matter):
```gitignore
# dotenv: ignore real values, keep templates
.env
.env.local
.env.*.local
.env.production
.env.development

# explicitly track templates and the test fixture
!.env.example
!.env.test
!.env.production.example
!.env.development.example
```

**Next.js loading order** (document in `README.md` or `AGENTS.md`):
```
next dev    → .env.development.local  → .env.local → .env.development → .env
next build  → .env.production.local   → .env.local → .env.production  → .env
next start  → (same as next build)
jest/vitest → .env.test.local         →           → .env.test         → .env
              ↑ NODE_ENV=test skips .env.local on purpose (test isolation)
```

**Runtime validation** (`src/env.ts`, validated at boot — fails loud if a prod var is missing):
```ts
import { z } from "zod";

const Env = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]),
  DATABASE_URL: z.string().url(),
  NEXTAUTH_SECRET: z.string().min(32),
  STRIPE_SECRET_KEY: z.string().startsWith(
    process.env.NODE_ENV === "production" ? "sk_live_" : "sk_test_",
  ),
});

export const env = Env.parse(process.env);  // throws at boot if invalid
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Next.js environment variables (loading order, test isolation): https://nextjs.org/docs/app/guides/environment-variables
- Vite env and modes (`--mode`, `VITE_` prefix, `.env.[mode]`): https://vite.dev/guide/env-and-mode
- Rails configuring environments (`config/environments/*.rb`, encrypted credentials per env): https://guides.rubyonrails.org/configuring.html
- Vercel environments (development / preview / production + `vercel env pull`): https://vercel.com/docs/environment-variables
- Netlify deploy contexts (`[context.production]`, `[context.deploy-preview]`, `[context.branch-deploy]`): https://docs.netlify.com/build/configure-builds/file-based-configuration/#deploy-contexts
- GitHub Environments (cross-link signal #63): https://docs.github.com/en/actions/deployment/targeting-different-environments/managing-environments-for-deployment
- 12-Factor App, Config: https://12factor.net/config
- dotenv-flow (per-env loading for plain Node): https://github.com/kerimdzhanov/dotenv-flow
- t3-oss `@t3-oss/env-nextjs` (typed env validation at boot): https://env.t3.gg
- envalid (runtime env validation, fail-loud): https://github.com/af/envalid
- Kustomize overlays per env: https://kubectl.docs.kubernetes.io/guides/config_management/components/
</system-reminder>
