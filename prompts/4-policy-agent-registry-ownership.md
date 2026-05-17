[Readiness Fix] <REPO_NAME> Agent Registry / Ownership Metadata

Fix the failing signal: Agent Registry / Ownership Metadata ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Agent Registry / Ownership Metadata
**Score**: [0/1]
**Description**: Documented map of which agent owns which scope of the repo, so when two or more autonomous agents are active you can answer "who is allowed to touch this path?" without guessing
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Agent registry / ownership metadata — check for a checked-in, machine-correlatable map from agent identity to repo scope. PASS requires at least one of the following, with concrete entries that bind a *stable agent identifier* to an *enforceable scope* (allow + deny), not just a prose list:

1. **`AGENTS.md` registry section**: an `## Agents` (or `## Agent Registry`) section enumerating every agent runtime that operates on the repo, with one row per agent containing (a) a stable identifier — bot login `claude[bot]`, GitHub App slug `factory-app`, OIDC `sub` claim prefix, or internal agent key — (b) the runtime/model, (c) the scope the agent OWNS (file globs, directories, labels, or task types), (d) explicit deny scopes ("MUST NOT touch `infra/terraform/prod/**`, `migrations/**`, `.github/workflows/release.yml`"), and (e) the human or team that approves its PRs. A vague description like "Claude handles backend stuff" FAILs — it's not a glob, not enforceable, and the next dev can't grep for it.

2. **`.agents/registry.yaml` (or `.agents/agents.toml`, `agents.json`)**: a machine-readable manifest that other tooling can parse. Minimum schema:
   ```yaml
   agents:
     - id: claude-code
       identity:
         github_login: claude[bot]
         github_app_slug: claude
         oidc_sub_prefix: "repo:<ORG>/<REPO>:ref:refs/heads/agent/claude/*"
       owns:
         paths: ["src/web/**", "tests/web/**"]
         labels: ["scope:web"]
       denies:
         paths: ["infra/**", "migrations/**", ".github/workflows/release.yml"]
       approvers: ["@<ORG>/web-leads"]
   ```
   The schema must be referenced from `AGENTS.md` (so humans find it) and from CI (so it's actually used — e.g. a workflow that fails the build when a PR from `claude[bot]` modifies a path outside its `owns:`).

3. **CODEOWNERS with bot identities**: `.github/CODEOWNERS` containing rules that name bot accounts as owners of specific globs (e.g. `/docs/api-generated/** @<ORG>/docs-bot`, `/src/web/** @claude-app`). Each bot listed in CODEOWNERS must (a) exist as a GitHub user / App / team — not a fictional handle — and (b) be cross-referenced from `AGENTS.md` so a human reviewer can map `@claude-app` back to "this is the Claude Code GitHub App, scope X, escalate to team Y". CODEOWNERS alone without the AGENTS.md cross-reference is partial credit — the identifier is enforceable but its meaning isn't documented.

4. **Per-agent identity binding**: at minimum one of:
   - **GitHub bot login**: `claude[bot]`, `github-actions[bot]`, `dependabot[bot]`, `devin-ai-integration[bot]`, `copilot-swe-agent[bot]`, `cursoragent[bot]`. The `[bot]` suffix and case must match exactly — `Dependabot` does not equal `dependabot[bot]` in `github.event.pull_request.user.login` checks.
   - **GitHub App slug**: the URL-safe slug from `https://github.com/apps/<slug>`; the slug becomes the bot's login as `<slug>[bot]` and is the only identifier guaranteed stable across token rotations.
   - **OIDC `sub` claim**: for agents that run in GitHub Actions, the JWT `sub` follows the format `repo:<ORG>/<REPO>:environment:<env>` or `repo:<ORG>/<REPO>:ref:refs/heads/<branch>`. A registry that binds an agent to an OIDC `sub` prefix (e.g. `repo:acme/web:ref:refs/heads/agent/claude/*`) gives you cryptographic, not advisory, identity.
   - Internal agent key (for agents that don't push commits — e.g. Slack-resident research agents): a stable id documented in the registry, used in audit trails.

Also verify the registry holds together end-to-end:
- Every agent identifier in the registry MUST resolve to a real account: `gh api users/<login>` (or `users/<slug>%5Bbot%5D`) returns 200, or the GitHub App exists at `https://github.com/apps/<slug>`. Fictional names like `claude-bot-1` that nobody created are dead config.
- The `owns:` and `denies:` scopes MUST be disjoint within a single agent and SHOULD be disjoint across agents (two agents both owning `src/web/**` with no precedence rule produces a race). If overlap is intentional (e.g. shared `tests/` directory), document the precedence ("Claude wins on `tests/web/**`, Factory wins on `tests/integration/**`").
- Scopes must be enforced somewhere. Possible enforcers: CODEOWNERS (blocks merge until owner reviews), a `.github/workflows/scope-guard.yml` that reads `.agents/registry.yaml` and fails on cross-scope edits, branch protection that requires a label matching the agent's owned label set. A registry with no enforcer is documentation, not policy.
- Bot identities MUST be filtered consistently in CI. If `.github/workflows/test.yml` runs on PRs from `claude[bot]` but the labeler in `.github/workflows/label-agent-prs.yml` skips `claude[bot]`, the chain is broken — pick a single filter list and reuse it (extract to a composite action or matrix include).

A `README.md` paragraph saying "Claude works on the frontend, Factory on the backend" with no identifier, no glob, and no enforcement is documentation theater and FAILs. A registry that lists agents by descriptive name ("Backend Agent") without binding them to a stable login/slug/sub-claim is unenforceable — there's no way for a workflow or branch protection rule to act on it.

## Your Task

1. Explore the repository to understand the current state related to this signal:
   - List `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.factory/`, `.cursor/`, `.devin/`, `.github/CODEOWNERS`, `.github/workflows/*.yml`, and any `docs/agent*.md`.
   - Identify every agent runtime that has actually committed to the repo: `git log --pretty=format:'%an <%ae>' | sort -u | grep -iE 'bot|claude|factory|copilot|cursor|devin|dependabot|renovate'`. This is your ground truth — any agent in your registry that has zero commits is aspirational; any committer not in the registry is unaccounted for.
   - Check whether agent identities are already filtered in CI: `grep -rE 'pull_request\.user\.login|github\.actor' .github/workflows/`.
   - Note the team structure on GitHub: `gh api orgs/<ORG>/teams --paginate` (the registry's `approvers:` field references these).

2. Make **substantive improvements** by wiring agent identity to scope end-to-end:

   - **Add an `## Agents` registry section to `AGENTS.md`** (create the file if absent). One subsection per active agent, with: stable identifier (bot login + App slug + OIDC sub prefix where applicable), runtime/model, owned scopes (concrete globs the agent has actually edited per `git log --author`), denied scopes (paths that have caused production incidents or contain secrets/infra), and the human/team approver. Cross-reference `.github/CODEOWNERS` and (if added) `.agents/registry.yaml`.

   - **Add `.agents/registry.yaml`** as the machine-readable source of truth. Schema above. Reference it from `AGENTS.md` and from any scope-enforcement workflow you add.

   - **Update `.github/CODEOWNERS`** so every glob in the registry's `owns:` field has a matching CODEOWNERS rule naming the bot's GitHub App team (or, if the App isn't installed as a team member, the human team that reviews that agent's PRs). Bots cannot be CODEOWNERS in their own right unless they're added to a team — the common pattern is `/src/web/** @<ORG>/claude-reviewers` where `@<ORG>/claude-reviewers` is a team of humans plus optionally the App.

   - **Add a scope-guard workflow** `.github/workflows/agent-scope-guard.yml` that loads `.agents/registry.yaml`, compares the PR's changed files (`gh pr diff --name-only`) against the author's `owns:` + `denies:`, and fails the check if (a) any file falls under the agent's `denies:`, or (b) any file falls outside the union of all agents' `owns:` and the agent isn't the one who owns it. Skip on human-authored PRs.

   - **Document the bot-identity allowlist** once, in `AGENTS.md`, then reference it from every workflow that filters by author. The list looks like:
     ```
     claude[bot]                  -> Claude Code GitHub App
     factory-app[bot]             -> Factory Droid GitHub App
     copilot-swe-agent[bot]       -> GitHub Copilot Workspace
     devin-ai-integration[bot]    -> Devin
     cursoragent[bot]             -> Cursor background agent
     dependabot[bot]              -> Dependabot
     renovate[bot]                -> Renovate
     github-actions[bot]          -> GitHub Actions default token
     ```
     Workflows that need to act on agent PRs should `source` (via composite action input) the canonical list, not redefine it inline.

3. Verify the registry holds end-to-end:
   - For each agent in `.agents/registry.yaml`: confirm the GitHub App exists (`curl -s https://api.github.com/apps/<slug>` or visit `https://github.com/apps/<slug>`); confirm the `[bot]` login actually appears in `git log`; confirm CODEOWNERS has a matching rule.
   - Open a draft PR that touches one file inside an agent's `owns:` and one file inside its `denies:`. Confirm `agent-scope-guard.yml` fails on the deny hit. (If you don't have a bot account to author the PR from, simulate by setting the workflow's author check to the current PR author for the test.)
   - Run `gh api repos/<ORG>/<REPO>/codeowners/errors` and confirm zero errors — CODEOWNERS rules referencing non-existent teams/users return as errors here.

4. Keep changes focused on this signal — do not refactor unrelated CI or split CODEOWNERS into something nobody asked for.

5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** registry entries with fictional or aspirational identifiers. `claude-bot-1`, `agent-alpha`, `our-backend-ai` are not real GitHub identities — `gh api users/<login>` returns 404. Every identifier in the registry MUST resolve to a real GitHub user, App, or team.
- **NO** descriptive-name-only entries. "Backend Agent" without a `github_login` / `github_app_slug` / `oidc_sub_prefix` is unenforceable — there's no field a workflow can match against.
- **NO** `[bot]`-suffix mistakes. The login is `claude[bot]` (lowercase, literal brackets), not `Claude[Bot]`, `claude-bot`, `claude_bot`, or `claude`. Workflow author checks are case-sensitive string equality.
- **NO** `owns: ["**"]` or `owns: ["*"]` — a wildcard owner is no owner. If an agent truly handles everything, document that fact and add explicit `denies:` for the dangerous paths (infra, migrations, release workflows, `.env*`, `secrets/**`).
- **NO** overlapping `owns:` across agents without a precedence rule. If both Claude and Factory list `src/api/**`, the next PR from either is ambiguous — pick a winner or split the scope.
- **NO** `denies:` lists that miss the production-critical paths. Every registry MUST deny at minimum: `infra/**` (or wherever Terraform/CDK/Pulumi lives), `migrations/**` (or the equivalent for your ORM), `.github/workflows/*release*`, `.github/workflows/*deploy*`, `**/.env*`, `secrets/**`, and any path containing signing keys or KMS material.
- **NO** registry stored in a path no tool reads. `agents.json` at repo root with no workflow that loads it, or a Notion page that nobody can grep — both invisible to CI. The registry must live at `.agents/registry.yaml` (or equivalent) AND be loaded by at least one workflow.
- **NO** CODEOWNERS rules naming bot accounts that aren't team members. GitHub silently drops CODEOWNERS entries for accounts without push access; `gh api repos/<ORG>/<REPO>/codeowners/errors` will flag them. Either add the bot to a team or own the path with the human team that reviews that bot's PRs.
- **NO** scope-guard workflow that uses `pull_request_target` with `write` permissions and no allowlist — that's a token-exfiltration vector via a malicious PR. Use `pull_request` and scope `permissions:` to the minimum (`pull-requests: read, contents: read`).
- **NO** "registry" that lists agents but no scopes. Identifier without ownership is half a registry — you can attribute a commit to an agent but you can't answer "was this agent allowed to make that commit?"
- **NO** registry that drifts from CODEOWNERS. If you list Claude as owning `src/web/**` in `.agents/registry.yaml` but CODEOWNERS routes `src/web/**` to `@<ORG>/web-leads` with no Claude reference, a reviewer reading either file in isolation gets a different answer. Add a CI check or pre-commit hook that diffs the two.

Examples of BAD fixes:

- `AGENTS.md` containing only: "We use Claude Code and Factory for development." — no identifiers, no scope, no enforcement.
- `.agents/registry.yaml` with:
  ```yaml
  agents:
    - name: "Backend"
      description: "Handles API stuff"
  ```
  No stable identifier (can't be matched in CI), no globs (can't be enforced), no approver (no escalation path).
- A `CODEOWNERS` line `* @ai-bot` where `@ai-bot` is a user that doesn't exist — `gh api repos/.../codeowners/errors` returns an error and the rule is ignored.
- A registry that lists `dependabot[bot]` as owning `package.json` but no workflow validates that PRs from `dependabot[bot]` only touch `package.json` and `package-lock.json` — registry exists, enforcement doesn't.
- `owns: ["src/**"]` and `denies: ["src/legacy/**"]` for one agent, while another agent has `owns: ["src/legacy/**"]` and `denies: ["src/**"]` with no documented handoff — every PR that touches `src/legacy/shared.ts` becomes a debate.
- A scope-guard workflow that runs only on `push` events — by the time it fails, the change has already merged.

Examples of GOOD fixes:

**`AGENTS.md` registry section:**

```markdown
## Agent Registry

Every autonomous agent that operates on this repo is enumerated below with a stable identifier, owned scope, denied scope, and human approver. The machine-readable source of truth is `.agents/registry.yaml`; this section is the human-readable mirror.

### claude-code
- **Identity**: `claude[bot]` (login) / `claude` (GitHub App slug, https://github.com/apps/claude) / OIDC sub prefix `repo:acme/web:ref:refs/heads/agent/claude/*`
- **Runtime**: Claude Code (model: claude-sonnet-4-5 and successors)
- **Owns**: `src/web/**`, `tests/web/**`, `docs/web/**`
- **Denies**: `infra/**`, `migrations/**`, `.github/workflows/release.yml`, `.github/workflows/deploy-*.yml`, `**/.env*`, `secrets/**`
- **Approvers**: `@acme/web-leads`

### factory-droid
- **Identity**: `factory-app[bot]` / GitHub App slug `factory-app` / OIDC sub prefix `repo:acme/web:ref:refs/heads/agent/factory/*`
- **Runtime**: Factory droid (Reflection / Code droid)
- **Owns**: `src/api/**`, `tests/api/**`, `db/queries/**`
- **Denies**: `infra/**`, `migrations/**`, `.github/workflows/release.yml`, `**/.env*`, `secrets/**`
- **Approvers**: `@acme/api-leads`

### dependabot
- **Identity**: `dependabot[bot]`
- **Runtime**: Dependabot (GitHub-managed)
- **Owns**: `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `requirements*.txt`, `poetry.lock`, `Gemfile.lock`, `.github/dependabot.yml`
- **Denies**: everything else
- **Approvers**: `@acme/platform`

### Precedence and overlap

- `tests/**` is co-owned: `tests/web/**` → claude-code; `tests/api/**` → factory-droid. Anything under `tests/integration/**` requires both team reviews.
- A PR from any agent that touches a denied path is auto-failed by `.github/workflows/agent-scope-guard.yml`. There is no override label — denied means denied. Humans must take over.

### Bot identity allowlist (canonical)

The strings below are the exact `github.event.pull_request.user.login` values workflows match on. Do not invent variants.

| Bot login                       | Runtime                       |
|---------------------------------|-------------------------------|
| `claude[bot]`                   | Claude Code GitHub App        |
| `factory-app[bot]`              | Factory droid GitHub App      |
| `copilot-swe-agent[bot]`        | GitHub Copilot Workspace      |
| `devin-ai-integration[bot]`     | Devin                         |
| `cursoragent[bot]`              | Cursor background agent       |
| `dependabot[bot]`               | Dependabot                    |
| `renovate[bot]`                 | Renovate                      |
| `github-actions[bot]`           | GitHub Actions default token  |
```

**`.agents/registry.yaml`:**

```yaml
# Machine-readable agent registry. Loaded by .github/workflows/agent-scope-guard.yml.
# Human-readable mirror lives in AGENTS.md § Agent Registry. Keep them in sync;
# .github/workflows/registry-drift-check.yml fails the build if they diverge.
$schema: ./registry.schema.json
version: 1
agents:
  - id: claude-code
    identity:
      github_login: "claude[bot]"
      github_app_slug: claude
      oidc_sub_prefix: "repo:acme/web:ref:refs/heads/agent/claude/*"
    runtime: claude-code
    owns:
      paths: ["src/web/**", "tests/web/**", "docs/web/**"]
      labels: ["scope:web"]
    denies:
      paths:
        - "infra/**"
        - "migrations/**"
        - ".github/workflows/release.yml"
        - ".github/workflows/deploy-*.yml"
        - "**/.env*"
        - "secrets/**"
    approvers: ["@acme/web-leads"]

  - id: factory-droid
    identity:
      github_login: "factory-app[bot]"
      github_app_slug: factory-app
      oidc_sub_prefix: "repo:acme/web:ref:refs/heads/agent/factory/*"
    runtime: factory-droid
    owns:
      paths: ["src/api/**", "tests/api/**", "db/queries/**"]
      labels: ["scope:api"]
    denies:
      paths:
        - "infra/**"
        - "migrations/**"
        - ".github/workflows/release.yml"
        - "**/.env*"
        - "secrets/**"
    approvers: ["@acme/api-leads"]

  - id: dependabot
    identity:
      github_login: "dependabot[bot]"
    runtime: dependabot
    owns:
      paths:
        - "package.json"
        - "package-lock.json"
        - "pnpm-lock.yaml"
        - "requirements*.txt"
        - "poetry.lock"
        - "Gemfile.lock"
        - ".github/dependabot.yml"
    denies:
      paths: ["**"]   # everything not in owns is denied
    approvers: ["@acme/platform"]
```

**`.github/CODEOWNERS` (excerpt):**

```
# Web frontend — Claude Code agent + human reviewers
/src/web/**             @acme/web-leads
/tests/web/**           @acme/web-leads
/docs/web/**            @acme/web-leads

# API — Factory droid + human reviewers
/src/api/**             @acme/api-leads
/tests/api/**           @acme/api-leads
/db/queries/**          @acme/api-leads

# Dependency updates — Dependabot owns lockfiles, platform reviews
/package.json           @acme/platform
/package-lock.json      @acme/platform
/pnpm-lock.yaml         @acme/platform
/.github/dependabot.yml @acme/platform

# Off-limits to all agents — humans only
/infra/**               @acme/sre
/migrations/**          @acme/data-leads
/.github/workflows/release.yml   @acme/sre
/.github/workflows/deploy-*.yml  @acme/sre
/secrets/**             @acme/security
```

(Note: bot accounts are not direct CODEOWNERS; the human team that reviews each agent's PRs is. The registry binds bot → scope; CODEOWNERS binds scope → human reviewer. Together they answer "which agent can write this, who must approve.")

**`.github/workflows/agent-scope-guard.yml`:**

```yaml
name: Agent scope guard
on:
  pull_request:
    types: [opened, synchronize, reopened]
permissions:
  pull-requests: read
  contents: read
jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Resolve agent identity
        id: who
        run: |
          AUTHOR="${{ github.event.pull_request.user.login }}"
          # Match the PR author against the registry's github_login fields.
          AGENT_ID=$(yq -r ".agents[] | select(.identity.github_login == \"$AUTHOR\") | .id" .agents/registry.yaml || true)
          echo "author=$AUTHOR"   >> "$GITHUB_OUTPUT"
          echo "agent_id=$AGENT_ID" >> "$GITHUB_OUTPUT"
      - name: Skip on human-authored PRs
        if: steps.who.outputs.agent_id == ''
        run: echo "Human author ($AUTHOR) — scope guard does not apply."
      - name: Enforce owns / denies
        if: steps.who.outputs.agent_id != ''
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          AGENT_ID="${{ steps.who.outputs.agent_id }}"
          mapfile -t CHANGED < <(gh pr diff "${{ github.event.pull_request.number }}" --name-only)
          mapfile -t OWNS    < <(yq -r ".agents[] | select(.id == \"$AGENT_ID\") | .owns.paths[]"   .agents/registry.yaml)
          mapfile -t DENIES  < <(yq -r ".agents[] | select(.id == \"$AGENT_ID\") | .denies.paths[]" .agents/registry.yaml)
          fail=0
          for f in "${CHANGED[@]}"; do
            for d in "${DENIES[@]}"; do
              if [[ "$f" == $d ]]; then
                echo "::error file=$f::Agent '$AGENT_ID' denied path '$d' matched '$f'"
                fail=1
              fi
            done
            in_scope=0
            for o in "${OWNS[@]}"; do
              [[ "$f" == $o ]] && in_scope=1 && break
            done
            if [ $in_scope -eq 0 ]; then
              echo "::error file=$f::Agent '$AGENT_ID' has no owns:-rule covering '$f'"
              fail=1
            fi
          done
          exit $fail
```

## Why this matters

In a single-agent repo you can hand-wave ownership — "Claude wrote it, Jeff reviewed it, done." Add a second agent (Factory, Devin, Copilot Workspace, a custom Slack agent) and ownership collapses into ambiguity within a week: two agents race-edit the same file, neither knowing the other exists; a PR from `claude[bot]` rewrites a Terraform module nobody told it was off-limits; a deploy workflow gets quietly modified by an agent whose human approvers don't watch infra changes. The forensic question after the incident — "which agent was allowed to touch this path?" — has no answer because the policy was implicit. A registry that binds *stable identifier* to *enforceable scope* is the only way to keep multi-agent repos auditable. Without it, every multi-agent setup eventually has its own version of the Replit and Kiro incidents — not because the agents misbehaved, but because nobody could prove which one was responsible until the damage was done.

The signal is at L4 because L1-L3 cover single-agent existence-of-instructions; L4 readiness assumes multiple autonomous agents will share the repo and the team needs deterministic answers to "who owns this" before agents start stepping on each other.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of (a) which agents you registered, (b) the identifier type used for each (login / App slug / OIDC sub), (c) where the registry is enforced (CODEOWNERS, scope-guard workflow, or both), and (d) the verification step you ran (e.g. "ran `gh api repos/<ORG>/<REPO>/codeowners/errors` — zero errors; opened draft PR touching `infra/foo.tf` as `claude[bot]` simulated author — scope guard failed as expected")

## References

- AGENTS.md open spec (Agentic AI Foundation, Linux Foundation): https://agents.md/
- AGENTS.md format and hierarchical scope: https://www.augmentcode.com/guides/how-to-build-agents-md
- AGENTS.md monorepo & multi-agent patterns: https://www.morphllm.com/agents-md-guide
- Claude Code CLAUDE.md (sibling to AGENTS.md): https://code.claude.com/docs/en/memory
- Factory droid AGENTS.md support: https://docs.factory.ai/cli/configuration/agents-md
- GitHub CODEOWNERS syntax & errors API: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-configuration/customizing-your-repository/about-code-owners
- `gh api repos/<owner>/<repo>/codeowners/errors`: https://docs.github.com/en/rest/repos/repos#list-codeowners-errors
- GitHub App slug & `[bot]` login convention: https://docs.github.com/en/apps/creating-github-apps/setting-up-a-github-app/about-github-apps
- GitHub Actions OIDC `sub` claim format: https://docs.github.com/en/actions/concepts/security/openid-connect
- OIDC reference (customizing `sub` claim): https://docs.github.com/en/actions/reference/openid-connect-reference
- Per-agent GitHub App identity pattern (one `[bot]` per agent): https://dev.to/agent_paaru/each-ai-agent-gets-its-own-github-identity-how-we-gave-every-bot-its-own-bot-commit-signature-1197
- Dependabot reviewers replaced by CODEOWNERS: https://github.blog/changelog/2025-08-08-dependabot-reviewers-configuration-option-is-replaced-by-code-owners/
- Filtering bot authors in workflows (`github.event.pull_request.user.login == 'dependabot[bot]'`): https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions
- Claude Code Action security (bot author handling): https://github.com/anthropics/claude-code-action/blob/main/docs/security.md
- Multi-agent coordination & non-overlapping ownership: https://www.mindstudio.ai/blog/claude-code-agent-teams-parallel-workflows
- AWS Agent Registry (registry-as-control-plane pattern): https://aws.amazon.com/blogs/machine-learning/the-future-of-managing-agents-at-scale-aws-agent-registry-now-in-preview/
</system-reminder>
