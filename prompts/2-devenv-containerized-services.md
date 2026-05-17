[Readiness Fix] <REPO_NAME> Containerized Services

Fix the failing signal: Containerized Services ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Containerized Services
**Score**: [0/1]
**Description**: Docker-based local development stack
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Containerized services — check for a checked-in Compose file that actually defines the repo's runtime dependencies as services. PASS requires ALL of the following:

1. **A Compose file at a recognized path**: `compose.yaml` (canonical, preferred), `compose.yml`, `docker-compose.yaml`, or `docker-compose.yml` at the repo root or under a clearly named directory (`docker/`, `infra/compose/`). Per the Compose Specification, `compose.yaml` is the canonical name as of Compose v2; `docker-compose.yml` is supported only for backwards compatibility. A bare `Dockerfile` with no compose file FAILs — `Dockerfile` builds an image, it does not orchestrate a dev stack.
2. **Real services, not a stub**: at least one service that the app actually needs to run locally (e.g. `postgres`, `mysql`, `redis`, `mongodb`, `rabbitmq`, `minio`, `mailhog`, `kafka`, the app itself). A compose file with only `app:` and no dependencies on a repo that clearly uses Postgres is a FAIL.
3. **Pinned images**: every `image:` reference uses an explicit tag (`postgres:16.4-alpine`, `redis:7.4-alpine`) — `:latest` or untagged `image: postgres` is a FAIL. Pinning is what makes the dev stack reproducible for an agent across runs.
4. **Named volumes for stateful services**: any service that holds data (Postgres, MySQL, Mongo, Redis with persistence, MinIO) MUST mount a named volume to its data dir. A compose file that runs Postgres with no `volumes:` entry loses every row on `docker compose down` and is a daily footgun for agents.
5. **Healthchecks where downstream services depend on readiness**: if service B `depends_on` service A and A is a database/queue, A MUST declare a `healthcheck:` and B MUST use `depends_on: { A: { condition: service_healthy } }`. `depends_on` without a condition only waits for container start, not for the DB to accept connections, and agents will hit "connection refused" loops on first run.

Also verify the file actually parses: run `docker compose -f <file> config` (or `docker compose config` if at root) and confirm it exits 0. A compose file that fails `config` is dead config.

A README that says "run `docker run postgres` then `docker run redis`" is documentation, not orchestration, and FAILs this signal. So does a `Makefile` target that shells out to `docker run` — the signal is specifically about a declarative Compose stack.

This signal is distinct from:
- **#97 Local services setup** (documentation describing how to run dependencies — prose, README sections)
- **#94 Dev container** (`.devcontainer/devcontainer.json` — an editor-bound containerized IDE environment)

#96 is the actual Compose file with running dev services.

## Your Task

1. Explore the repository to understand what services the app actually needs — grep for `DATABASE_URL`, `REDIS_URL`, connection strings, ORM configs (`prisma/schema.prisma`, `alembic.ini`, `ormconfig`), and queue clients. Note the exact versions used in production or pinned in code.
2. Make **substantive improvements** by writing a real, project-tuned `compose.yaml`:
   - Place the file at the repo root as `compose.yaml` (canonical) unless the repo already has a Compose directory convention.
   - Define every external service the app talks to in development, pinned to a specific minor version, with a named volume for any stateful service.
   - Add a `healthcheck:` block to each database/queue service and wire `depends_on: { ...: { condition: service_healthy } }` on consumers.
   - Bind ports to `127.0.0.1:<port>` (loopback), not `0.0.0.0` or the bare-port shorthand `"5432:5432"` which binds all interfaces and exposes the dev DB on the LAN.
   - Pull credentials from `.env` via `${VAR:?err}` (fail-fast) for required values; never hardcode `POSTGRES_PASSWORD: postgres` in the committed file.
   - Add a top-level `name:` so multiple checkouts of the same repo don't collide on the default project name.
3. Verify the file parses and boots:
   - `docker compose config` — must exit 0.
   - `docker compose up -d` then `docker compose ps` — every service eventually reaches `(healthy)`.
   - Run the app's existing migration / integration-test command against the stack and confirm it connects.
4. Update the repo's onboarding doc (README quickstart section) to reference `docker compose up -d` as the single setup command. Do NOT replace #97's local-services-setup doc — that signal is separate.
5. Keep changes focused on this signal — do not refactor unrelated config.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** `:latest` tags, untagged images, or floating major-only tags (`postgres:16` is acceptable; `postgres` is not). The Compose Specification treats reproducibility as a first-class concern and `latest` defeats it.
- **NO** stateful services without a named volume. A `postgres` service with no `volumes:` entry is a FAIL — first `docker compose down` wipes the dev DB.
- **NO** missing healthchecks on services that other services `depends_on`. `depends_on` alone waits for container start, not for readiness; the dependent service will race the DB on first boot.
- **NO** services bound to `0.0.0.0` or the shorthand `"5432:5432"`. Use `"127.0.0.1:5432:5432"` to keep the dev DB off the LAN. (Anyone on the same Wi-Fi can otherwise reach the agent's Postgres.)
- **NO** hardcoded credentials in the committed file. Use `${POSTGRES_PASSWORD:?set in .env}` and ship a `.env.example`. Committed `POSTGRES_PASSWORD: postgres` becomes the production password three months later.
- **NO** legacy `version: "3.8"` (or any `version:` key) at the top. The Compose Specification deprecated the `version` field in 2023 — it is ignored by Compose v2 and signals a stale template.
- **NO** legacy hyphenated `docker-compose` CLI invocations in scripts. The canonical CLI is `docker compose` (subcommand of `docker`); `docker-compose` is a separate Python binary that ships outdated behavior.
- **NO** mixing `links:` (deprecated) or `network_mode: host` (Linux-only, breaks Docker Desktop). Use the default project network — services reach each other by service name.
- **NO** committing the compose file in a path Compose does not auto-discover (e.g. `infra/compose-dev.yaml`) without also documenting `docker compose -f infra/compose-dev.yaml up` in the README — otherwise agents run `docker compose up` and get "no configuration file provided".

Examples of BAD fixes:

- Adding a `compose.yaml` containing only `services: { app: { build: . } }` on a repo that clearly needs Postgres and Redis — the file orchestrates nothing the agent doesn't already have.
- Pinning `image: postgres:latest` — every `docker compose pull` is a new major version and a fresh round of migration breakage.
- A Postgres service with `ports: ["5432:5432"]` and no `volumes:` — exposes the DB on the LAN AND loses data on every restart.
- `depends_on: [postgres]` (list form, no condition) on the app service — app starts in 200ms, Postgres takes 4s to accept connections, app crash-loops until you `docker compose restart app`.
- Hardcoding `POSTGRES_PASSWORD: postgres` "just for dev" — the same string ends up in CI, then staging, then prod.
- Committing `version: "3.8"` at the top "because the template had it" — Compose v2 prints a deprecation warning and the line carries zero meaning.

Examples of GOOD fixes:

- A `compose.yaml` at the repo root:
  ```yaml
  name: <REPO_NAME>-dev

  services:
    postgres:
      image: postgres:16.4-alpine
      restart: unless-stopped
      environment:
        POSTGRES_USER: ${POSTGRES_USER:-app}
        POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD in .env}
        POSTGRES_DB: ${POSTGRES_DB:-app}
      ports:
        - "127.0.0.1:5432:5432"
      volumes:
        - postgres-data:/var/lib/postgresql/data
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-app} -d ${POSTGRES_DB:-app}"]
        interval: 5s
        timeout: 5s
        retries: 10
        start_period: 10s

    redis:
      image: redis:7.4-alpine
      restart: unless-stopped
      command: ["redis-server", "--appendonly", "yes"]
      ports:
        - "127.0.0.1:6379:6379"
      volumes:
        - redis-data:/data
      healthcheck:
        test: ["CMD", "redis-cli", "ping"]
        interval: 5s
        timeout: 3s
        retries: 10

    app:
      build:
        context: .
        dockerfile: Dockerfile
      environment:
        DATABASE_URL: postgres://${POSTGRES_USER:-app}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-app}
        REDIS_URL: redis://redis:6379/0
      ports:
        - "127.0.0.1:3000:3000"
      depends_on:
        postgres:
          condition: service_healthy
        redis:
          condition: service_healthy

  volumes:
    postgres-data:
    redis-data:
  ```
- A matching `.env.example` at the repo root listing `POSTGRES_PASSWORD=`, `POSTGRES_USER=app`, `POSTGRES_DB=app` with a comment pointing agents at `cp .env.example .env`.
- A README "Local development" section that reads, in full: "`cp .env.example .env && docker compose up -d && pnpm dev`. Stop the stack with `docker compose down`; reset state with `docker compose down -v`."
- A `Makefile` target `make services` that runs `docker compose up -d --wait` (Compose v2.17+ blocks until healthchecks pass), so agents get a deterministic ready signal instead of polling.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Compose Specification (current): https://github.com/compose-spec/compose-spec/blob/main/spec.md
- Compose file reference (services, volumes, networks): https://docs.docker.com/reference/compose-file/
- Healthcheck attribute: https://docs.docker.com/reference/compose-file/services/#healthcheck
- `depends_on` with `condition: service_healthy`: https://docs.docker.com/compose/how-tos/startup-order/
- `compose.yaml` is the canonical filename (Compose v2): https://docs.docker.com/compose/intro/compose-application-model/
- `version` top-level element is deprecated: https://docs.docker.com/reference/compose-file/version-and-name/
- `docker compose up --wait` (block until healthy): https://docs.docker.com/reference/cli/docker/compose/up/
- Podman Compose (drop-in alternative): https://docs.podman.io/en/latest/markdown/podman-compose.1.html
</system-reminder>
