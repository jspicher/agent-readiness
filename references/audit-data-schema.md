# audit-data.json -- Schema Reference

Schema for the JSON sidecar emitted alongside the Markdown audit report. The
HTML renderer (`assets/report-template.html` + `scripts/render_html.sh`)
consumes this. The Markdown report is derivable from the same data and must
stay consistent with it.

## Top-level shape

```json
{
  "schema_version": 1,
  "repo_name": "string",
  "generated_at": "ISO-8601 UTC string",
  "audit_context": { /* required when schema_version >= 2 (see below) */ },
  "repo_profile": { /* from Step 0 -- optional in v1, recommended */ },
  "applications": [{"path": "string", "description": "string"}],
  "summary": { ... },
  "tiers": [ /* 5 entries, L1..L5 */ ],
  "pillars": [ /* 7 entries, P1..P7 */ ],
  "top_actions": [ /* up to 3 */ ]
}
```

`schema_version` is `1` (legacy, `audit_context` optional) or `2`
(`audit_context` required and well-formed).

## repo_profile (recommended; renderer falls back when missing)

Output of SKILL.md Step 0. Drives applicability gates on #5, #13, #60, #76, #84, #85, #106. Each dimension carries the evidence string so a reader can validate the gate.

When `repo_profile` is absent (e.g., pre-Phase-2.y audits like v4 backfilled JSON), the HTML renderer skips profile-driven UI (the profile summary block, profile-gate badges on N/A tiles, tooltip cross-references) but otherwise renders the report normally. The dual-headline `readiness_tracks` is still computed from `pillars` if the auditor doesn't supply it.

```json
{
  "repo_kind": "app" | "library" | "sdk" | "cli" | "framework" | "monorepo" | "unknown",
  "repo_kind_evidence": "one-line citation",
  "visibility": "public" | "private" | "unknown",
  "visibility_evidence": "one-line citation",
  "accepts_external_contributors": true | false | null /* null means unknown */,
  "accepts_external_contributors_evidence": "one-line citation",
  "team_scale": "solo" | "small_team" | "multi_team" | "unknown",
  "team_scale_evidence": "one-line citation"
}
```

When a dimension is `unknown` (or `accepts_external_contributors=null`), criteria gated on that dimension default to **strict** -- the criterion applies and may still fail.

## audit_context (required when schema_version >= 2)

Captures the state of the target repository's working tree at audit time.
Populated by `bash scripts/capture_audit_context.sh <repo>` and merged into
the data file before `validate_audit_data.py` is run (see SKILL.md Step 0).
This block lets a reader confirm that a report describes a specific commit,
or warns them when the audit was run against uncommitted changes.

```json
{
  "head_sha": "string -- full git SHA (>=7 hex chars)",
  "branch": "string -- branch name; \"detached@<short_sha>\" when detached",
  "worktree_dirty": true | false,
  "dirty_files_count": "int >= 0",
  "dirty_diff_sha256": "string (64 hex chars) when dirty | null when clean",
  "captured_at": "ISO-8601 UTC string (prefer Z suffix)"
}
```

Required-when rules (enforced by `[V10]`):
- `dirty_diff_sha256` MUST be a 64-hex string when `worktree_dirty == true`.
- `dirty_diff_sha256` MUST be `null` when `worktree_dirty == false`.
- The block is optional under `schema_version: 1` (grandfather clause for
  pre-Phase-2.z audits).
- The block is **required** under `schema_version: 2`. A missing or
  ill-shaped `audit_context` fails `[V10]`.

When `worktree_dirty == true` the rendered Markdown surfaces a "working
tree audit" italic line under the H1, and the HTML renderer shows an
amber "working-tree audit" badge in the topbar with a hover title quoting
`dirty_files_count` and the short SHA.

## Field rules

- `schema_version` -- `1` (legacy, `audit_context` optional) | `2` (`audit_context` required).
- `repo_name` -- the audited repo's name (no path, no trailing slash).
- `generated_at` -- ISO-8601 UTC timestamp.
- `applications` -- from Step 1 of SKILL.md. At least one entry; the root
  application has `path: "."`.

## summary

```json
{
  "flat_coverage": {"passed": int, "applicable": int, "percent": int},
  "max_tier_hierarchical": int /* 0..5 */,
  "flat_bucket_level": int /* 1..5 */,
  "strongest_pillar": {"id": int, "name": string, "percent": int},
  "weakest_pillar":   {"id": int, "name": string, "percent": int},
  "readiness_tracks": { /* optional -- renderer computes from pillars if absent */
    "assisted":   {"passed": int, "applicable": int, "percent": int},
    "autonomous": {"passed": int, "applicable": int, "percent": int}
  }
}
```

`percent` is an integer 0..100, rounded.

`readiness_tracks` exposes the dual headline (W6):
- `assisted` -- sum across P1-5 (AI-Assisted Readiness). Strong here means the agent can work effectively in this repo.
- `autonomous` -- sum across P1-7 (Autonomous-Agent Readiness, includes Observability + Agent-OS). Strong here means the agent can be trusted to run autonomously.

Both numbers MUST be displayed when present. The renderer never hides `autonomous` in favor of `assisted`; the gap between the two is the Pillar 6+7 work-in-progress signal. If the auditor omits `readiness_tracks`, the HTML renderer recomputes it from `pillars` at render time.

## tiers (exactly 5 entries, L1..L5 in order)

```json
[
  {"level": 1, "label": "Basic",         "applicable": int, "passed": int, "percent": int},
  {"level": 2, "label": "Intermediate",  "applicable": int, "passed": int, "percent": int},
  {"level": 3, "label": "Advanced",      "applicable": int, "passed": int, "percent": int},
  {"level": 4, "label": "Power-user",    "applicable": int, "passed": int, "percent": int},
  {"level": 5, "label": "Self-improving","applicable": int, "passed": int, "percent": int}
]
```

## pillars (exactly 7 entries, P1..P7 in id order)

```json
{
  "id": int /* 1..7 */,
  "name": string,
  "applicable": int,
  "passed": int,
  "percent": int,
  "features": [ /* see feature shape */ ]
}
```

## feature

```json
{
  "num": int /* matches the row number in criteria.md */,
  "name": string,
  "level": int /* 1..5 */,
  "description": string,
  "status": "pass" | "fail" | "na",
  "rationale": string,
  "rationale_kind": "profile_gate" | "missing_precondition" | "subsystem_absence" | "broadened_evidence" | "other" /* required when status=na; recommended for status=pass when evidence path is non-obvious */,
  "remediation_prompt": string | null
}
```

Rules:

- `description` -- copy verbatim from the "What to look for" column in
  `references/criteria.md`. Keep it terse (typically <200 chars) -- this is
  used as a modal subtitle in the HTML report.
- `rationale` -- required for `pass` and `fail`. For `na`, state the
  precondition that doesn't apply.
- `rationale_kind` -- optional but recommended. Disambiguates *why* an N/A
  or non-obvious pass landed:
  - `profile_gate` -- N/A driven by a Step 0 profile dimension (e.g.,
    `accepts_external_contributors=false` triggered #76's N/A). Renderer
    surfaces a "profile gate" badge on the tile + links the precondition to
    the profile summary.
  - `missing_precondition` -- N/A driven by a non-evidence, **process-level**
    constraint that's unsatisfiable on this repo's platform/plan (e.g., #54
    Branch protection on GitHub Free private). Renderer shows the standard
    "—" tile with rationale tooltip.
  - `subsystem_absence` -- N/A because the repo demonstrably has no instance
    of the gated subsystem (DB-using, monorepo, web-facing, perf-sensitive,
    etc.). See `references/applicability-glossary.md` for per-dimension
    detection commands. Renderer shows the standard "—" tile.
  - `broadened_evidence` -- pass via a Phase 2.y broadened evidence path
    (e.g., #73 LICENSE passed via README proprietary statement instead of a
    LICENSE file; #108 passed via `packageManager` field instead of `.npmrc`).
    Renderer shows a subtle marker so reviewers can audit calibration drift.
  - `other` / omitted -- default; no special rendering.
- `remediation_prompt` -- the **fully substituted** prompt text. By the time
  it lands here, every `<REPO_NAME>` is the actual repo name and every
  `<WHY_IT_FAILED -- ...>` placeholder is the per-audit rationale. The HTML
  modal copies this string verbatim to the user's clipboard, so it must be
  ready-to-paste. Null when `status != "fail"` or when no prompt is mapped in
  `prompt-map.json`.

## top_actions (up to 3 entries)

```json
{
  "title": string,    /* required, non-empty -- shown as the action heading */
  "body": string,     /* required, non-empty -- 1-3 sentence description    */
  "feature_refs": [int] /* optional; feature_nums the action targets        */
}
```

When `feature_refs` is provided, the HTML report renders each as a clickable
pill that opens that feature's detail modal.

**Required key names:** `title`, `body`, `feature_refs`. The HTML renderer
(`assets/report-template.html` → `renderActions()`) reads exactly those keys.
Using alternate names like `feature_name`, `note`, or `feature_num` will
cause the report to render **three blank action rows with no warning** --
the JS uses `textContent` against `undefined`, which silently coerces to an
empty string. To prevent this, `scripts/render_html.sh` runs a Python (or
jq) schema check on `top_actions` before substitution and exits with code
**7** when a row is missing `title` or `body`, or when either is empty.
See ERR-20260517-008 for the regression that drove this safety net.

## Worked example

See `fixtures/test-data-minimal.json` in the skill, or the full backfill at
`docs/agent-readiness/2026-05-16-botw-nextjs-readiness-smoke-test-v2-data.json` in
the `.claudebot` repo.

## Field consumption matrix

Both the Markdown and HTML reports derive from this JSON, but they don't render every field. This is intentional -- the JSON is canonical, but each surface picks what it needs.

| Field | Markdown | HTML |
|-------|---------|------|
| `repo_name` | yes (heading) | yes (topbar) |
| `generated_at` | no (only in JSON) | yes (topbar) |
| `applications` | yes (Applications section) | no (single-app focus) |
| `summary.flat_coverage` | yes | yes |
| `summary.max_tier_hierarchical` | yes | yes (topbar + meter) |
| `summary.flat_bucket_level` | yes | yes |
| `summary.strongest_pillar` / `weakest_pillar` | yes | yes |
| `summary.readiness_tracks` | yes (dual-headline lines) | yes (top of hero summary) |
| `repo_profile` | yes (REPOSITORY_PROFILE block after applications) | yes (top of hero summary; tooltip on each profile-gated N/A) |
| `audit_context` | yes (dirty banner under H1 when `worktree_dirty`) | yes (amber "working-tree audit" badge in topbar when `worktree_dirty`) |
| `tiers` | yes (Pass rate by tier table) | no (synthesized from `pillars` only) |
| `pillars` | yes (per-pillar sections + rows) | yes (radar + tile grid) |
| `top_actions` | yes (Top 3 next actions) | yes (actions strip) |

The "no" entries are NOT optional fields -- they're still required in the JSON because the Markdown surface needs them and because keeping the JSON the canonical truth means it must be a superset of every renderer's needs.

## How the renderer consumes this

```bash
bash scripts/render_html.sh <slug>-data.json <slug>.html
```

The script reads `assets/report-template.html`, replaces the placeholder
`<!--AUDIT_DATA_JSON-->` line with the JSON contents (escaped against
`</script`), and writes the result. The template's inline JS parses the
JSON on `DOMContentLoaded` and renders all UI client-side.
