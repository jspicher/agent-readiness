---
name: agent-readiness-report
description: Evaluate how well a codebase supports autonomous AI-assisted development. Analyzes repositories across seven pillars (Agent Instructions, Feedback Loops, Workflows & Automation, Policy & Governance, Build & Dev Environment, Observability, Agent-OS Readiness) covering 132 features tagged with maturity levels 1-5. Use when users want to assess how agent-ready a repository is. Triggers -- "agent-readiness-report", "readiness report".
---

# Agent Readiness Report

Evaluate how well a repository supports autonomous AI-assisted development.

## What this does

Assess a codebase across seven pillars that determine whether an AI agent can
work effectively AND safely in a repository.  The output is a structured report
identifying what's present, what's missing, and what's the next-most-valuable
investment.

## Seven Pillars

| Pillar | Question | Features |
|--------|----------|----------|
| 1. **Agent Instructions** | Does the agent know what to do? | 21 |
| 2. **Feedback Loops** | Does the agent know if it's right? | 28 |
| 3. **Workflows & Automation** | Does the process support agent work? | 22 |
| 4. **Policy & Governance** | Does the agent know the rules? | 19 |
| 5. **Build & Dev Environment** | Can the agent build and run the project? | 19 |
| 6. **Observability** | Can the agent verify production behavior? | 11 |
| 7. **Agent-OS Readiness** | Can the agent act safely and recoverably? | 12 |

132 features total.  See `references/criteria.md` for the full list with
descriptions, level tags (L1-L5), and evidence examples.

## Maturity levels

Each feature is tagged with a maturity level:

- **L1** Basic — language-agnostic essentials
- **L2** Intermediate — agent-friendly tooling
- **L3** Advanced — measurement and discipline
- **L4** Power-user — full automation and observability
- **L5** Self-improving — closed feedback loops

When reporting, compute three numbers (the first two are ours, the third is
ported from Factory.ai's `/readiness-report` for cross-comparison):

1. **Flat coverage** — % of applicable features passing.
2. **Max tier reached (hierarchical)** — the highest level L such that EVERY level from L1 through L has ≥80% of its applicable features passing. This is the authoritative metric and is deterministic. Computed by the following algorithm:
   - Start at L0.
   - For L in [1, 2, 3, 4, 5]: if ≥80% of applicable features at level L pass, set the result to L; else STOP and return the current result.
   - If L1 itself fails the 80% threshold, the result is **L0** (no level reached).
   - This guarantees you cannot claim L3 without first passing L1 AND L2; "skip-level" passes are not honored.
3. **Flat-bucket level (Factory-style)** — flat coverage % bucketed
   `0-20%→L1, 20-40%→L2, 40-60%→L3, 60-80%→L4, 80-100%→L5`.  Useful for
   benchmarking against Factory's report; can over-state readiness when
   high-tier features pass on a weak foundation. Reported as a comparison number, not the headline.

## Behavioral Guidelines

These rules govern every audit run.  They keep the report deterministic and
prevent false-positive passes.  Read them before running the steps below.

- **Be deterministic** — identical repo state must produce identical output.
  Don't infer signals that aren't directly observable.
- **If evidence is ambiguous, fail the item** — when you can't clearly verify
  a feature is genuinely in place, mark it ✗, not ✓.  False positives are
  worse than false negatives because they hide the gap.
- **Existence is necessary but not sufficient** — for features that name
  specific behavior (e.g., "README has build/run/test commands"), the file
  existing is not enough.  You must read it and confirm the behavior.
- **Rationale is mandatory for every ✗ feature** — say what's missing and
  what evidence you looked for.  ✓ rationale is recommended; `—` rationale
  must state the precondition that doesn't apply.
- **Cap rationales at ~500 characters** — terse, actionable, no padding.
- **Repository boundary** — stay inside the `.git` boundary of the target
  repo.  Ignore generated/vendor directories: `node_modules/`, `dist/`,
  `build/`, `.venv/`, `venv/`, `__pycache__/`, `.pytest_cache/`,
  `.next/`, `out/`, `.turbo/`, `.nuxt/`, `.svelte-kit/`, `target/`,
  `.gradle/`, `.idea/`, `.vscode/`, `.pnpm-store/`, `vendor/`, `coverage/`.
  Never traverse outside the repo root.
- **Use the default branch state** — whatever HEAD points to is what gets
  audited.  Don't speculate about uncommitted work.

## How to run

### Step 0: Profile the repository

Before discovering applications or scoring features, infer four repo-profile dimensions from observable evidence. The profile drives applicability gates on several criteria (Step 3) and is surfaced in the report header (Step 5).

**Each dimension MUST be evidence-grounded.** If you can't determine a value from observable repo state, record it as `unknown` -- never guess. When a profile dimension is `unknown`, all criteria gated on that dimension default to **strict** (the criterion applies; failing evidence still fails). `unknown` is not a free pass.

| Dimension | Values | Detection rules (in order) |
|---|---|---|
| `repo_kind` | app, library, sdk, cli, framework, monorepo, unknown | (a) `package.json` `"workspaces"` present OR multiple top-level `apps/`/`packages/` dirs with their own manifests → **monorepo**. (b) `package.json` `"bin"` field, `Cargo.toml` `[[bin]]`, Go `main` package in root → **cli**. (c) `package.json` `"main"`/`"exports"` AND not `"private": true` AND no `next.config.*`/`vite.config.*`/`app/` dir → **library** (or **sdk** if name/README declares "SDK"). (d) Next.js, Vite app, Django, Rails, Express server with deploy config → **app**. (e) `package.json` declares peer-dependency-heavy ecosystem hooks (e.g., Next.js, Vue, Astro plugins) and consumers extend it → **framework**. (f) None match → **unknown**. |
| `visibility` | public, private, unknown | (a) `package.json` `"private": true` → **private**. (b) Git remote URL + `gh api repos/{owner}/{repo} --jq .visibility` returns "public" → **public**. (c) GH API returns "private" → **private**. (d) No GitHub remote or API unavailable → **unknown**. |
| `accepts_external_contributors` | true, false, unknown | **true** if ALL hold: (a) `visibility=public`, (b) an OSS-style LICENSE file is present (MIT, Apache-2.0, BSD, GPL, MPL, ISC, etc. -- NOT "UNLICENSED"/"All Rights Reserved"), (c) `CONTRIBUTING.md` or a contributing section in README addresses outside contributors. **false** if `visibility=private` OR LICENSE is proprietary/UNLICENSED OR README says "internal use only" / "no external contributions". **unknown** when visibility is unknown. |
| `team_scale` | solo, small_team, multi_team, unknown | Run `git shortlog -sn --since="12 months ago" --no-merges --email` and **dedupe by email address** (not by name -- one human often commits under multiple display names with the same email). Count remaining distinct emails after excluding bots. **solo** = 1 email. **small_team** = 2-5 emails. **multi_team** = 6+ emails. **unknown** if git history shorter than 3 months OR shortlog fails. **Bot detection** — exclude any author whose email matches the regex `/(\[bot\]|noreply|bot@|@bots\.|@users\.noreply\.github\.com$)/i` OR whose name appears in this list: `dependabot`, `renovate`, `github-actions`, `semantic-release-bot`, `vibekanban`, `vercel`, `netlify`. Bots committing under a real human's email count as that human, not as a separate author. |

Record findings in the report header (Step 5) as:

```
REPOSITORY_PROFILE:

  repo_kind: <value>
    Evidence: <one-line citation, e.g., "package.json declares 'bin' field; Cargo.toml has [[bin]] section">
  visibility: <value>
    Evidence: <one-line citation, e.g., "package.json: \"private\": true">
  accepts_external_contributors: <value>
    Evidence: <one-line citation>
  team_scale: <value>
    Evidence: <one-line citation, e.g., "git shortlog --since='12 months ago' shows 3 distinct human authors">
```

These values are **fixed** for the rest of the audit. Use them when evaluating profile-gated criteria (#5, #13, #60, #76, #84, #85, #106, #108 -- see `references/criteria.md`). The profile is also embedded in the JSON sibling artifact (`<slug>-data.json`) under a top-level `repo_profile` object.

**Anti-gaming safeguard:** A profile-driven N/A still requires its rationale to cite the specific profile value that triggered it (e.g., "N/A: `accepts_external_contributors=false` per private visibility + UNLICENSED package.json"). Auditors reading the report can challenge a gate by checking the profile evidence trail. Don't N/A a criterion if the precondition is `unknown` -- score strictly.

### Step 1: Discover applications

Before scoring anything, catalog the applications the repository contains.
An *application* is a directory (not a file) representing an independently
deployable unit — it has its own deployment lifecycle, can be built and run
independently, and serves end users or other systems.

**Heuristic:** could this directory be lifted into its own repo and still
function?  If yes, it's likely an application.

Common patterns:
- Single-purpose repository → 1 application (the root, denoted `.`)
- Monorepo with service directories → count each independently deployable
  service (e.g., `apps/web`, `apps/api`, `services/billing`)
- Library repository → 1 application (the root), even if it's only a library
- Shared packages, utility libs imported by other code → NOT applications

If you find zero applications, treat the repo root as 1 application.

Record findings as:

```
APPLICATIONS_IDENTIFIED: N

Applications:
1. <path> — <one-line description from README/package.json>
2. ...
```

This count is **fixed** for the rest of the audit.  Use it when scoring any
feature whose evidence must hold across multiple apps (e.g., "every app has
a CI pipeline" in a monorepo).  For the rendering step, surface it as the
`# Applications` section of the report.

### Step 2: Run the scanner scripts

Seven shell scripts gather filesystem signals — file existence, config patterns,
directory structures.  They surface what's present so you don't have to run
dozens of `find` commands manually.

```bash
bash scripts/scan_agent_instructions.sh /path/to/repo
bash scripts/scan_feedback_loops.sh /path/to/repo
bash scripts/scan_workflows.sh /path/to/repo
bash scripts/scan_policy.sh /path/to/repo
bash scripts/scan_build_env.sh /path/to/repo
bash scripts/scan_observability.sh /path/to/repo
bash scripts/scan_agent_os.sh /path/to/repo
```

Or scan all seven at once:

```bash
for s in scripts/scan_*.sh; do bash "$s" /path/to/repo; echo; done
```

**Important**: The scripts are helpers, not scorers.  They find files and
patterns but do not evaluate quality.  Many features require judgment that only
reading the actual files can provide.

### Step 3: Evaluate each feature

Walk through `references/criteria.md` pillar by pillar.  For each feature:

1. Check the scanner output for relevant signals
2. For features the scanner can't fully evaluate, inspect the files yourself
   (stay within the repository boundary defined in Behavioral Guidelines)
3. Determine applicability — conditional features (DB-only, monorepo-only,
   etc.) should be marked `—` when the prerequisite is absent
4. Mark each feature: **✓** (present), **✗** (missing), or **—** (not applicable)
5. Write a one-line rationale (≤500 chars):
   - **Required for ✗** — what's missing, what evidence you looked for
   - **Recommended for ✓** — what evidence you found
   - **Required for —** — the precondition that doesn't apply

Features that require judgment (not fully covered by scanners):

- Does the README actually contain build/run/test commands? (not just exist)
- Is inline documentation systematic across the public API?
- Are examples actually runnable?
- Does the contributing guide include code standards?
- Is there a meaningful AI usage policy?
- Is the architecture documentation current?
- Are tests documented well enough for an agent to run them?
- Does the agent have a real sandbox or just a config that claims one?
- Is the SBOM up-to-date or stale?

### Step 4: Validate before writing

Before writing the report, run this self-check.  **If any item fails, fix it
before proceeding** — do not paper over an inconsistency.

1. **Feature accounting** — every feature in `criteria.md` got exactly one of
   ✓ / ✗ / —.  No duplicates, no omissions, no invented features.
2. **Applicability is consistent** — if you marked a conditional feature `—`
   in one place, you applied the same precondition logic everywhere similar.
3. **Failing features have rationale** — every ✗ has a one-line "what's
   missing" note.
4. **No silent passes** — for features that depend on file *contents* (not
   just file existence), you actually read the file before marking ✓.
5. **Application count is fixed** — the N from Step 1 didn't change mid-audit.

### Step 5: Write the report

Each audit produces **three sibling artifacts** in `docs/agent-readiness/`:

- `<slug>.md` -- human-readable Markdown (5a, existing behavior)
- `<slug>-data.json` -- canonical structured data (5b, NEW)
- `<slug>.html` -- self-contained Factory-style dashboard (5c, NEW)

The JSON is the source of truth: Markdown and HTML must both be derivable
from it. Write the JSON during the same pass, never as a post-hoc derivation.

#### 5a. Markdown report

Structure the output as:

```markdown
# Agent Readiness Report: {repo name}

## Summary

- Flat coverage: X / N applicable features (Y%)
- Max tier reached (hierarchical): **L{level}** — highest L where every level 1..L has ≥80% pass (use **L0** if L1 itself does not reach 80%)
- Flat-bucket level (Factory-style): **L{level}** — Y% → bucket
- Strongest pillar: {pillar} (Z%)
- Weakest pillar: {pillar} (W%)

## Applications

1. {path or `.`} — {one-line description}
2. ...

## Pass rate by pillar

| Pillar | Pass rate |
|--------|-----------|
| 1. Agent Instructions | xx% (n/m applicable) |
| 2. Feedback Loops | xx% |
| ... | ... |

## Pass rate by tier

| Tier | Pass rate |
|------|-----------|
| L1 Basic | xx% |
| L2 Intermediate | xx% |
| L3 Advanced | xx% |
| L4 Power-user | xx% |
| L5 Self-improving | xx% |

## Top 3 next actions

1. [highest-leverage failing feature] — {one-line why and rough effort}
2. ...
3. ...

## Pillar 1 · Agent Instructions (X / 21 applicable)

✓ #1 Agent instruction file (L2) — AGENTS.md at root
✓ #2 AI IDE configuration (L2) — .cursor/rules/ with 3 rule files
✗ #3 Multi-model support (L3) — only Cursor configured
<details><summary>📋 Remediation prompt — copy/paste into a fresh Claude Code session to fix this</summary>

{full inlined remediation prompt for feature #3 — see Step 7}

</details>

— #20 AGENTS.md freshness validation (L5) — N/A: no AGENTS.md present
...

## Pillar 2 · Feedback Loops (X / 28 applicable)
...

## Pillar 7 · Agent-OS Readiness (X / 12 applicable)
...
```

For each passing feature, briefly note what evidence you found.
For each `—` feature, note the precondition that doesn't apply.
For each FAILING feature, do TWO things:
1. Note what's missing (one-line rationale, evidence-grounded).
2. Inline the remediation prompt inside a `<details>` block immediately under the row — see Step 7 for the lookup-and-substitution algorithm.

The inlined prompts are the actionable payload of this report: a reader can copy the entire `<details>` content into a new Claude Code session and the agent has everything it needs to fix that one feature.

#### 5b. Audit data JSON

Emit `<slug>-data.json` alongside the Markdown. Schema is documented in
`references/audit-data-schema.md`. Key invariants:

- Every feature must have `description` (copied from the "What to look for"
  column in `references/criteria.md`).
- `rationale` is required for `pass` and `fail`. For `na`, state the
  precondition.
- `remediation_prompt` is the **fully substituted** prompt text (with
  `<REPO_NAME>` and `<WHY_IT_FAILED -- ...>` already resolved). Null when the
  feature passes, is N/A, or no prompt exists in `prompt-map.json`.
- `pillars` contains exactly 7 entries in id order (1..7).
- `tiers` contains exactly 5 entries in L1..L5 order.

Substitute placeholders ONCE during Step 7. The same fully-substituted
prompt text appears verbatim in both surfaces: the Markdown `<details>`
block AND the JSON's `remediation_prompt` field. They must be byte-identical.
Do not re-derive the substitution per surface; do not edit one without the
other.

#### 5c. Render HTML

Run:

```bash
bash ~/.claude/skills/agent-readiness-report/scripts/render_html.sh \
  docs/agent-readiness/<slug>-data.json \
  docs/agent-readiness/<slug>.html
```

The script embeds the JSON into the template at
`~/.claude/skills/agent-readiness-report/assets/report-template.html` and
writes a self-contained HTML report sibling to the Markdown. Open it in a
browser to verify it loads without console errors before closing the audit.

### Step 6: Quality boundary on remediation prompts

If the user asks for help fixing failing features, follow these rules in any
generated remediation prompt or PR (ported from Factory.ai's `/readiness-report`
remediation template):

> Your fix must **genuinely improve the codebase**.  Do NOT use workarounds:
>
> - **NO** empty placeholder files (e.g., empty test files, stub configs)
> - **NO** minimal implementations that technically pass but provide no real value
> - **NO** disabling checks or adding skip markers to pass validation
> - **NO** trivial changes that game the metric without improving quality
>
> Examples of BAD fixes: empty `test.js` to satisfy "has tests", `.eslintrc`
> with all rules disabled, `// @ts-nocheck` to satisfy strict typing.
>
> Examples of GOOD fixes: actual unit tests with meaningful assertions, ESLint
> configured with appropriate rules for the project's stack, proper TypeScript
> types added.

### Step 7: Inline remediation prompts in the report

For every failing feature in Step 5, inline its full remediation prompt inside the `<details>` block. The prompts are pre-authored and live in `docs/factory-ai-readiness/remediate-prompts/` (relative to the `.claudebot` workspace, not the audited repo). The mapping from feature number to prompt file lives in `references/prompt-map.json` next to this SKILL.md.

The same fully-substituted prompt text from this step is ALSO written verbatim into each failing feature's `remediation_prompt` field in `<slug>-data.json` (Step 5b). Substitute once, write to both surfaces in the same pass -- byte-identical.

#### Lookup algorithm

For each failing feature (status `✗`):

1. **Load the mapping.** Read `references/prompt-map.json` once at the start of Step 7. The file has a `features` array; each entry has `feature_num`, `prompt_path`, `prompt_status`, `proposed_filename`.

2. **Find the feature's row** by `feature_num`.

3. **Resolve the prompt file:**
   - If `prompt_status == "HAS_PROMPT"`: open `prompt_path` (relative to `C:/wamp64/www/.claudebot/`). This is a pre-authored Factory or Pillar 7 prompt.
   - If `prompt_status == "NEEDS_PROMPT"` AND a file exists at `docs/factory-ai-readiness/remediate-prompts/<proposed_filename>`: open that file. (Newly authored prompts land here as the project completes Phase 1.)
   - If `prompt_status == "NEEDS_PROMPT"` AND no file exists yet: emit a stub block (see "Stub format" below) — do NOT fail the audit.

4. **Substitute placeholders** in the loaded prompt:
   - Replace literal string `<REPO_NAME>` with the audited repository's name (e.g., `botw-nextjs`).
   - Replace literal string `<WHY_IT_FAILED -- populated from rationale in your readiness report>` with the one-line rationale from your audit for this feature (e.g., "AGENTS.md exists but has not been updated in 240 days; staleness exceeds the 180-day threshold").

5. **Wrap and inline.** Emit:
   ```markdown
   <details><summary>📋 Remediation prompt — copy/paste into a fresh Claude Code session to fix this</summary>

   {substituted prompt text, verbatim, including the [Readiness Fix] header line and the trailing </system-reminder> close}

   </details>
   ```

#### Stub format (when prompt file doesn't exist yet)

```markdown
<details><summary>📋 Remediation prompt — pending authorship</summary>

This feature is mapped in `references/prompt-map.json` (`feature_num: {N}`, `proposed_filename: <name>`) but the prompt file has not yet been authored. To fix this feature manually, refer to:
- `references/criteria.md` row #{N} for evidence patterns
- Step 6 (quality boundary rules) for what counts as a substantive fix

To author this prompt: see `~/.claude/projects/C--wamp64-www--claudebot/memory/project_agent_readiness_remediation.md` for the batch protocol.

</details>
```

#### Quality boundary

Every inlined prompt already contains its own quality-boundary block (the `## CRITICAL: Quality Standards` section). Step 6 above is the authoritative version Jeff uses to AUDIT new prompts; the inlined prompts conform to it.

#### Concrete example

For a failing feature #3 (Multi-model support) in a repo named `botw-nextjs`:

1. Mapping lookup finds `prompt_path: "docs/factory-ai-readiness/remediate-prompts/3-docs-multi-model-support.md"`, status `NEEDS_PROMPT`, but the file exists on disk (authored 2026-05-16).
2. Load the file, substitute `<REPO_NAME>` → `botw-nextjs` and `<WHY_IT_FAILED ...>` → "Only `.cursor/rules/` found; no AGENTS.md, no `.github/copilot-instructions.md`, no `.claude/settings.json` — single-vendor lock-in to Cursor."
3. Wrap in the `<details>` block and inline under the `✗ #3` row in Pillar 1.

#### Performance note

The full report can be ~50-200KB for a repo with many failures (each inlined prompt is ~5-10KB). The `<details>` blocks keep the report navigable in a Markdown viewer — sections collapse by default.

## What makes these features useful

Every feature answers: *if this is missing, what goes wrong for the AI agent?*

The 132-feature set spans two layers:

1. **Baseline engineering maturity** — pillars 1-5 — does the agent have what
   it needs to work effectively?
2. **Agent-OS readiness** — pillars 6-7 — can the agent verify its work in
   production AND act safely with bounded authority and recoverable failure
   modes?

A repo strong in pillars 1-5 is "AI-assisted-ready"; only repos strong in
pillars 6-7 are "autonomous-agent-ready."

## Lineage and limitations

- Pillars 1-5 originated from cluster analysis of 123 repositories.
- 2026 expansion borrowed selected criteria from Factory.ai's `/readiness-report`
  (see `docs/factory-ai-readiness/`) and added Pillar 7 (Agent-OS Readiness)
  drawn from industry research on autonomous-agent operating-system patterns
  (`_research-external.md`).
- Both source frameworks are opinionated curations rather than empirically
  validated benchmarks.  Treat the level tags as a reasoned opinion, not a
  mathematical truth.
- Some features (Backlog Health, Privacy Compliance specifics, Cost telemetry)
  have high false-positive risk for filesystem scanners and require human
  judgment.

## Multi-vendor assumption

The skill assumes a multi-vendor agent ecosystem (Claude / Cursor / Copilot /
Factory / etc.).  If you operate single-vendor, treat features #2-7 (multi-IDE
config, multi-model support, prompt libraries) as optional.
