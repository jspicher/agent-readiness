[Readiness Fix] <REPO_NAME> Decision Records

Fix the failing signal: Decision Records ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Decision Records
**Score**: [0/1]
**Description**: Documented reasoning behind past architectural choices
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Decision records – check for a checked-in directory of architecture decision records (ADRs) or RFCs that capture the *reasoning* behind past architectural choices, not just the choices themselves. PASS requires ALL of the following:

1. **Discoverable location**: a directory at one of the conventional paths — `doc/adr/`, `docs/adr/`, `docs/architecture/decisions/`, `decisions/`, `rfcs/`, `docs/rfcs/`, or `adr/`. A single ADR file scattered loose in `docs/` does not count.
2. **Conventional naming**: zero-padded sequential prefix + kebab-case title, e.g. `0001-record-architecture-decisions.md`, `0007-use-postgres-not-mysql.md`. MADR (Markdown Architecture Decision Record) and Nygard formats both use this convention. Files named `decision.md`, `adr-cors.md`, or `architecture-notes.md` fail.
3. **Substantive content per record**: each ADR must contain — at minimum — Context (the problem and forces in play), Decision (what was chosen, stated in active voice), Consequences (positive AND negative — tradeoffs accepted), and Status. A "Considered Options" / "Alternatives" section is required for any non-trivial decision. A record that lists only the decision with no context is a stub.
4. **Status field with a real enum value**: `Proposed | Accepted | Deprecated | Superseded by ADR-NNNN`. A missing status field or a free-text status like "current" fails. Superseded records MUST link forward to the record that replaced them, and the superseding record MUST link back.
5. **Real coverage (not 1-ADR theater)**: the index must contain at least 3 substantive decisions that reflect actual choices in the codebase (database, auth, deployment target, language/runtime version, framework selection, monorepo vs polyrepo, etc.). A single ADR titled "Record architecture decisions" (the meta-ADR that ships with `adr-tools init`) with no follow-up records FAILS — it proves the tooling exists but captures zero actual reasoning.

Also verify the records are wired into discovery: an `index.md` or `README.md` in the ADR directory listing every record with title + status, AND a link from the top-level repo README or `docs/` index pointing to the ADR folder. ADRs nobody can find are dead documentation.

## Your Task

1. Explore the repository to identify decisions that have *already been made* but never written down — read the top-level `README.md`, `package.json`/`pyproject.toml`/`go.mod` for stack choices, `docker-compose.yml`/`Dockerfile` for runtime/db choices, `.github/workflows/` for CI choices, `Procfile`/IaC for deploy targets, and skim recent git log for commits with messages like "switch to X", "migrate from Y", "replace Z". These are your ADR backlog.
2. Pick the conventional directory for this repo's stack. Default to `docs/adr/` unless the repo already uses `doc/`, `decisions/`, or `rfcs/` elsewhere.
3. Create at least **4 substantive ADRs**: one meta-record (ADR-0001 "Record architecture decisions") plus a minimum of 3 records documenting actual past decisions you uncovered. Each non-meta ADR MUST cover Context → Considered Options → Decision → Consequences → Status, and cite the file/line/commit that proves the decision is in effect.
4. Add an `index.md` listing every ADR with `NNNN | Title | Status | Date`. Link to it from the repo `README.md` under a "Decisions" or "Architecture" heading.
5. Optionally drop in a tiny helper script (e.g. `tools/adr-new.sh`) so the next decision is one command away — this reduces the chance the directory stays at 4 records forever.
6. Keep changes focused on this signal — do not refactor unrelated code.
7. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** single-ADR repos. Shipping only `0001-record-architecture-decisions.md` is the canonical anti-pattern — it proves `adr-tools init` was run and nothing else. The signal stays failed because zero actual reasoning is captured.
- **NO** ADRs documenting trivial or obvious choices ("Use Git for version control", "Use UTF-8 encoding", "Write code in the chosen language"). ADRs exist for decisions where a future maintainer would otherwise reasonably ask "why didn't we just do X instead?".
- **NO** missing Status field, or a free-text status like "current", "live", "in use". The enum is `Proposed | Accepted | Deprecated | Superseded by ADR-NNNN` — pick one.
- **NO** ADR that contradicts the current code with no superseding record. If ADR-0003 says "we use MySQL" and the repo runs on Postgres, ADR-0003 must be marked `Superseded by ADR-0009` and ADR-0009 must exist and link back.
- **NO** decision-without-consequences. An ADR that lists only positives is marketing copy, not a decision record. Every accepted tradeoff must name the cost (vendor lock-in, operational complexity, learning curve, perf ceiling, etc.).
- **NO** ADRs hidden in a path the team won't find — `archive/old-notes/decisions/` or a Notion page linked from nowhere. The directory must be in-repo at a conventional path AND linked from `README.md`.
- **NO** wall-of-text ADRs that bury the decision in 4 pages of background. Keep records to one screen where possible; long-form belongs in an RFC, not an ADR.
- **NO** retroactively backdated ADRs that pretend a decision was deliberate when the git log shows it was accidental. Be honest — "Decision: we ended up on Express because the original prototype used it and migration cost now exceeds switching benefit" is a valid, useful ADR.

Examples of BAD fixes:
- `docs/adr/0001-record-architecture-decisions.md` and nothing else.
- `decisions/database.md` with body `We use Postgres.` — no context, no alternatives, no consequences, no status, non-conventional filename.
- An ADR titled "Use TypeScript" on a TypeScript-only repo where the question was never live — captures no reasoning.
- `docs/adr/0003-switch-to-graphql.md` marked `Status: Accepted` while the codebase ships REST controllers and zero GraphQL schema — stale ADR, no `Superseded by` link.
- A 2000-word ADR whose Decision section reads "We will think about this further" — that's a Proposed RFC, not an Accepted ADR.

Examples of GOOD fixes:
- Full ADR using the Nygard / MADR hybrid template:
  ```markdown
  # ADR-0004: Use PostgreSQL for primary data store

  - Status: Accepted
  - Date: 2025-09-12
  - Deciders: @alice, @bob
  - Supersedes: ADR-0002

  ## Context

  The MVP shipped on SQLite (see ADR-0002). We now have multi-tenant
  writes, a read replica requirement for the analytics dashboard, and
  one production incident caused by SQLite's single-writer lock under
  burst traffic (incident #142, 2025-08-30).

  ## Considered Options

  1. Stay on SQLite + Litestream replication
  2. Migrate to PostgreSQL (managed RDS)
  3. Migrate to MySQL (managed RDS)
  4. Move to a serverless KV store (DynamoDB)

  ## Decision

  We will migrate the primary store to PostgreSQL on AWS RDS, single
  writer + one read replica, behind PgBouncer.

  ## Consequences

  Positive:
  - Removes single-writer bottleneck; read replica unblocks the analytics dashboard.
  - PostGIS available if we add geo features (option value).
  - Team already operates two Postgres instances for other services.

  Negative:
  - Adds an always-on RDS bill (~$X/mo) the SQLite stack did not have.
  - Migration requires a dual-write window and a backfill job (est. 2 weeks engineering).
  - Local-dev setup now requires Docker Compose; contributors lose the "git clone && run" experience documented in README.

  ## Links

  - Supersedes: [ADR-0002](./0002-use-sqlite-for-mvp.md)
  - Migration plan: [docs/migrations/sqlite-to-postgres.md](../migrations/sqlite-to-postgres.md)
  - Incident #142 post-mortem: [docs/incidents/2025-08-30.md](../incidents/2025-08-30.md)
  ```
- A `docs/adr/index.md`:
  ```markdown
  # Architecture Decision Records

  | #    | Title                                  | Status      | Date       |
  | ---- | -------------------------------------- | ----------- | ---------- |
  | 0001 | Record architecture decisions          | Accepted    | 2025-06-01 |
  | 0002 | Use SQLite for MVP                     | Superseded by 0004 | 2025-06-14 |
  | 0003 | Adopt pnpm workspaces over Nx          | Accepted    | 2025-07-22 |
  | 0004 | Use PostgreSQL for primary data store  | Accepted    | 2025-09-12 |
  ```
- A `tools/adr-new.sh` so the next record is friction-free:
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  ADR_DIR="docs/adr"
  next=$(printf "%04d" $(( $(ls "$ADR_DIR" | grep -Eo '^[0-9]{4}' | sort -n | tail -1) + 1 )))
  slug=$(echo "$*" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-')
  file="$ADR_DIR/${next}-${slug}.md"
  cat > "$file" <<EOF
  # ADR-${next}: $*

  - Status: Proposed
  - Date: $(date +%Y-%m-%d)
  - Deciders:

  ## Context

  ## Considered Options

  ## Decision

  ## Consequences

  ### Positive

  ### Negative

  ## Links
  EOF
  echo "Created $file"
  ```
- A `README.md` patch with a "Decisions" section linking to `docs/adr/index.md` so the records are discoverable on the repo landing page.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Michael Nygard, "Documenting Architecture Decisions" (2011, the original ADR essay): https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- MADR (Markdown Architecture Decision Records) — current template & rationale: https://adr.github.io/madr/
- adr.github.io — community index of ADR templates, tools, and examples: https://adr.github.io/
- `adr-tools` CLI (npryce) — `adr init`, `adr new`, `adr link`, supersede semantics: https://github.com/npryce/adr-tools
- `log4brains` — web UI + static-site generator for ADR archives: https://github.com/thomvaill/log4brains
- ThoughtWorks Tech Radar on Lightweight Architecture Decision Records (Adopt ring): https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records
- GitHub `adr/madr` template repo (drop-in starter): https://github.com/adr/madr
- Joel Parker Henderson's ADR examples catalog (good/bad samples across stacks): https://github.com/joelparkerhenderson/architecture-decision-record
</system-reminder>
