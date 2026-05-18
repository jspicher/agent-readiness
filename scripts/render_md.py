#!/usr/bin/env python3
"""render_md.py -- render the Markdown audit report from audit-data JSON.

Sibling to scripts/render_html.sh. Given a validator-clean audit-data
JSON, emits the human-readable Markdown described in SKILL.md Step 5a.

Auditors do NOT hand-author the Markdown. They do NOT write a one-shot
`docs/agent-readiness/_gen_md.py` inside the target repo. The skill
provides this renderer for the same reason it provides the builder and
the HTML renderer: deterministic, identical-input-equals-identical-output,
no target-repo pollution.

Usage:
    python3 scripts/render_md.py <slug>-data.json [--out <slug>.md]

Exit codes:
    0 -- emitted Markdown
    2 -- usage error
    3 -- input file not found
    4 -- input file malformed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


STATUS_GLYPHS = {
    "pass": "✓",  # check mark
    "fail": "✗",  # ballot X
    "na":   "—",  # em-dash
}

PILLAR_TOTAL = {1: 21, 2: 28, 3: 22, 4: 19, 5: 19, 6: 11, 7: 12}


def _load(path: Path) -> dict:
    if not path.is_file():
        print(f"input not found: {path}", file=sys.stderr)
        sys.exit(3)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"input is not valid JSON: {e}", file=sys.stderr)
        sys.exit(4)


def _summary_block(d: dict) -> list[str]:
    s = d.get("summary", {})
    fc = s.get("flat_coverage", {})
    out = [
        "## Summary",
        "",
        f"- Flat coverage: {fc.get('passed', 0)} / {fc.get('applicable', 0)} applicable features ({fc.get('percent', 0)}%)",
        f"- Max tier reached (hierarchical): **L{s.get('max_tier_hierarchical', 0)}** -- highest L where every level 1..L has ≥80% pass (L0 if L1 itself does not reach 80%)",
        f"- Flat-bucket level: **L{s.get('flat_bucket_level', 0)}** -- {fc.get('percent', 0)}% bucketed",
    ]
    strongest = s.get("strongest_pillar") or {}
    weakest = s.get("weakest_pillar") or {}
    if strongest:
        out.append(f"- Strongest pillar: {strongest.get('name', '?')} ({strongest.get('percent', 0)}%)")
    if weakest:
        out.append(f"- Weakest pillar: {weakest.get('name', '?')} ({weakest.get('percent', 0)}%)")
    tracks = s.get("readiness_tracks") or {}
    if tracks:
        a = tracks.get("assisted") or {}
        au = tracks.get("autonomous") or {}
        out.append(
            f"- AI-Assisted readiness (P1-5): **{a.get('percent', 0)}%** "
            f"({a.get('passed', 0)}/{a.get('applicable', 0)})"
        )
        out.append(
            f"- Autonomous-Agent readiness (P1-7): **{au.get('percent', 0)}%** "
            f"({au.get('passed', 0)}/{au.get('applicable', 0)})"
        )
    out.append("")
    return out


def _profile_block(d: dict) -> list[str]:
    p = d.get("repo_profile")
    if not isinstance(p, dict):
        return []
    out = ["## Repository profile", "", "```"]
    out.append(f"repo_kind: {p.get('repo_kind', 'unknown')}")
    if p.get("repo_kind_evidence"):
        out.append(f"  Evidence: {p['repo_kind_evidence']}")
    out.append(f"visibility: {p.get('visibility', 'unknown')}")
    if p.get("visibility_evidence"):
        out.append(f"  Evidence: {p['visibility_evidence']}")
    aec = p.get("accepts_external_contributors")
    aec_str = "unknown" if aec is None else str(aec).lower()
    out.append(f"accepts_external_contributors: {aec_str}")
    if p.get("accepts_external_contributors_evidence"):
        out.append(f"  Evidence: {p['accepts_external_contributors_evidence']}")
    out.append(f"team_scale: {p.get('team_scale', 'unknown')}")
    if p.get("team_scale_evidence"):
        out.append(f"  Evidence: {p['team_scale_evidence']}")
    out.append("```")
    out.append("")
    return out


def _applications_block(d: dict) -> list[str]:
    apps = d.get("applications") or []
    if not apps:
        return []
    out = ["## Applications", ""]
    for i, app in enumerate(apps, start=1):
        path = app.get("path", "?")
        desc = app.get("description", "")
        out.append(f"{i}. `{path}` -- {desc}" if desc else f"{i}. `{path}`")
    out.append("")
    return out


def _pillar_table(d: dict) -> list[str]:
    out = [
        "## Pass rate by pillar",
        "",
        "| Pillar | Pass rate |",
        "|--------|-----------|",
    ]
    for p in d.get("pillars") or []:
        out.append(
            f"| {p['id']}. {p['name']} | {p['percent']}% ({p['passed']}/{p['applicable']} applicable) |"
        )
    out.append("")
    return out


def _tier_table(d: dict) -> list[str]:
    out = [
        "## Pass rate by tier",
        "",
        "| Tier | Pass rate |",
        "|------|-----------|",
    ]
    for t in d.get("tiers") or []:
        out.append(
            f"| L{t['level']} {t['label']} | {t['percent']}% ({t['passed']}/{t['applicable']} applicable) |"
        )
    out.append("")
    return out


def _top_actions_block(d: dict) -> list[str]:
    actions = d.get("top_actions") or []
    if not actions:
        return []
    out = ["## Top next actions", ""]
    for i, a in enumerate(actions, start=1):
        title = a.get("title", "").strip() or "(untitled)"
        body = a.get("body", "").strip()
        refs = a.get("feature_refs") or []
        ref_str = f" (features: {', '.join('#' + str(r) for r in refs)})" if refs else ""
        out.append(f"{i}. **{title}**{ref_str}")
        if body:
            out.append(f"   {body}")
        out.append("")
    return out


def _feature_lines(feature: dict) -> list[str]:
    glyph = STATUS_GLYPHS.get(feature["status"], "?")
    level = feature.get("level", "?")
    name = feature.get("name", "?")
    rationale = (feature.get("rationale") or "").strip()
    kind = feature.get("rationale_kind")
    kind_suffix = f" [{kind}]" if kind else ""

    if feature["status"] == "na":
        line = f"{glyph} #{feature['num']} {name} (L{level}) -- N/A: {rationale}{kind_suffix}"
    else:
        line = f"{glyph} #{feature['num']} {name} (L{level}) -- {rationale}{kind_suffix}"

    out = [line]

    if feature["status"] == "fail":
        prompt_body = feature.get("remediation_prompt")
        if isinstance(prompt_body, str) and prompt_body:
            out.extend([
                "",
                "<details><summary>\U0001F4CB Remediation prompt -- copy/paste into a fresh agent session to fix this</summary>",
                "",
                prompt_body,
                "",
                "</details>",
                "",
            ])
    return out


def _pillar_sections(d: dict) -> list[str]:
    out: list[str] = []
    for p in d.get("pillars") or []:
        total = PILLAR_TOTAL.get(p["id"], len(p.get("features") or []))
        out.append(
            f"## Pillar {p['id']} · {p['name']} ({p['passed']} / {p['applicable']} applicable, {total} total)"
        )
        out.append("")
        for f in p.get("features") or []:
            out.extend(_feature_lines(f))
            out.append("")
        out.append("")
    return out


def _dirty_banner(d: dict) -> list[str]:
    ctx = d.get("audit_context")
    if not isinstance(ctx, dict):
        return []
    if not ctx.get("worktree_dirty"):
        return []
    short_sha = (ctx.get("head_sha") or "")[:7]
    count = ctx.get("dirty_files_count", 0)
    return [
        f"*Audited against working tree with {count} uncommitted change(s) on top of `{short_sha}`.*",
        "",
    ]


def render(d: dict) -> str:
    repo_name = d.get("repo_name", "?")
    lines: list[str] = [f"# Agent Readiness Report: {repo_name}", ""]
    lines.extend(_dirty_banner(d))
    lines.extend(_summary_block(d))
    lines.extend(_profile_block(d))
    lines.extend(_applications_block(d))
    lines.extend(_pillar_table(d))
    lines.extend(_tier_table(d))
    lines.extend(_top_actions_block(d))
    lines.extend(_pillar_sections(d))
    lines.extend([
        "---",
        "",
        "*Generated by [agent-readiness](https://github.com/jspicher/agent-readiness).*",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render the Markdown audit report from audit-data JSON.",
    )
    parser.add_argument("data_json", help="Path to <slug>-data.json")
    parser.add_argument("--out", default=None, help="Path to write Markdown (default: stdout)")
    args = parser.parse_args(argv)

    data = _load(Path(args.data_json))
    md = render(data)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"Wrote {out_path} ({len(md.encode('utf-8'))} bytes)", file=sys.stderr)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
