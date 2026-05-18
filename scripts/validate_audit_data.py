#!/usr/bin/env python3
"""validate_audit_data.py -- structural validator for audit-data JSON.

Runs eleven numbered structural checks against an audit-data JSON file and
related skill artifacts. Used by CI on every PR (see
`.github/workflows/validate.yml`) and recommended as a manual gate before
generating the Markdown / HTML surfaces (SKILL.md Step 4, rule 6).

Exit codes:
    0  -- all checks passed
    7  -- one or more schema violations (continues after each failure so the
          full violation list is reported in one pass)
    2  -- usage error (bad CLI args)
    3  -- referenced file not found

Each violation prints to stderr in the form:
    [V##] <one-line message with the offending key path or filename>

The eleven checks:

    V01  Exactly 7 pillars with id 1..7 in order.
    V02  Exactly 5 tiers with level 1..5 in order.
    V03  Feature numbers in audit data equal the contiguous {1..N} set parsed
         from references/criteria.md (N=132 today; do not hardwire).
         Gated on schema_version >= 2.
    V04  Per-pillar and per-tier applicable/passed/percent recompute from
         features[]. Gated on schema_version >= 2.
    V05  summary.max_tier_hierarchical matches the hierarchical algorithm in
         SKILL.md (0..5; pass-through on empty/applicable=0 since "X / 0" is
         vacuously >=80%). Gated on schema_version >= 2.
    V06  summary.flat_bucket_level matches the bucket of
         summary.flat_coverage.percent.
    V07  Every feature with status="na" carries a valid rationale_kind.
         rationale_kind is also optional-but-validated on pass/fail.
    V08  top_actions <= 3 entries, each with non-empty title+body, and
         feature_refs (if present) only references real feature.num values.
    V09  Every status="fail" feature whose prompt-map entry is HAS_PROMPT must
         have a non-empty remediation_prompt string. Gated on
         schema_version >= 2.
    V10  When schema_version >= 2, top-level audit_context is required and
         well-formed (head_sha, branch, worktree_dirty, dirty_files_count,
         dirty_diff_sha256, captured_at).
    V11  Prompt-map <-> disk drift. Top-level prompts/*.md (excludes
         _graveyard/) must be in 1:1 alignment with HAS_PROMPT entries in
         prompt-map.json.

Byte-identity between the MD <details> block and the JSON
remediation_prompt is an audit-generation invariant (Step 5/7 of SKILL.md),
not a validator check -- you cannot prove byte identity from JSON alone.

CLI:
    validate_audit_data.py <audit-data.json>
        [--prompt-map references/prompt-map.json]
        [--criteria references/criteria.md]
        [--prompts-dir prompts]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


VIOLATIONS: list[str] = []


def fail(code: str, msg: str) -> None:
    """Record a violation; continues so all problems surface in one pass."""
    VIOLATIONS.append(f"[{code}] {msg}")


def parse_criteria_nums(criteria_path: Path) -> set[int]:
    """Extract feature numbers from criteria.md table rows.

    Match rows of the form `^| <int> |`. Dedupe. Return as a set of ints.
    """
    if not criteria_path.is_file():
        print(f"criteria file not found: {criteria_path}", file=sys.stderr)
        sys.exit(3)

    nums: set[int] = set()
    pattern = re.compile(r"^\|\s*(\d+)\s*\|")
    with criteria_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            m = pattern.match(line)
            if m:
                nums.add(int(m.group(1)))
    return nums


def check_contiguous(nums: set[int]) -> tuple[bool, str]:
    """Confirm a set is exactly {1..N} for some N."""
    if not nums:
        return False, "criteria.md parsed zero feature numbers"
    n = max(nums)
    expected = set(range(1, n + 1))
    if nums == expected:
        return True, ""
    missing = sorted(expected - nums)
    extra = sorted(nums - expected)
    parts = []
    if missing:
        parts.append(f"missing={missing}")
    if extra:
        parts.append(f"extra={extra}")
    return False, " ".join(parts)


def recompute_group(features: list[dict]) -> tuple[int, int, int]:
    """Compute (applicable, passed, percent) from a feature list.

    applicable = count(status != "na")
    passed     = count(status == "pass")
    percent    = round(passed / applicable * 100)  if applicable > 0 else 0
    """
    applicable = sum(1 for f in features if f.get("status") != "na")
    passed = sum(1 for f in features if f.get("status") == "pass")
    if applicable > 0:
        percent = round(passed / applicable * 100)
    else:
        percent = 0
    return applicable, passed, percent


def compute_max_tier_hierarchical(tier_stats: dict[int, tuple[int, int]]) -> int:
    """SKILL.md hierarchical algorithm.

    For L in [1..5]: if applicable_L == 0 OR passed_L/applicable_L >= 0.80,
    result := L; else break.

    Empty tiers (applicable=0) count as pass-through because the rule is
    ">=80% of applicable" and 0/0 is vacuously satisfied. Reasonable people
    disagree about this; the alternative (treat empty as stop) would block a
    repo from earning L4 just because no L3 criteria applied. We follow the
    permissive interpretation that matches SKILL.md's text.
    """
    result = 0
    for level in [1, 2, 3, 4, 5]:
        applicable, passed = tier_stats.get(level, (0, 0))
        if applicable == 0 or (passed / applicable) >= 0.80:
            result = level
        else:
            break
    return result


def compute_flat_bucket(percent: float) -> int:
    """Bucket flat-coverage percent to level 1..5.

    0-20  -> 1
    20-40 -> 2
    40-60 -> 3
    60-80 -> 4
    80-100 -> 5

    Lower bound inclusive, upper bound exclusive for the first four buckets;
    L5 is closed on both ends (>=80 caps to 5).
    """
    p = float(percent)
    if p >= 80:
        return 5
    if p >= 60:
        return 4
    if p >= 40:
        return 3
    if p >= 20:
        return 2
    return 1


# --- the 11 checks --------------------------------------------------------- #


def check_v01_pillars(data: dict) -> None:
    pillars = data.get("pillars")
    if not isinstance(pillars, list) or len(pillars) != 7:
        fail("V01", f"pillars must be a list of exactly 7 entries (got {len(pillars) if isinstance(pillars, list) else type(pillars).__name__})")
        return
    ids = [p.get("id") for p in pillars]
    if ids != [1, 2, 3, 4, 5, 6, 7]:
        fail("V01", f"pillars[].id must be [1,2,3,4,5,6,7] in order (got {ids})")


def check_v02_tiers(data: dict) -> None:
    tiers = data.get("tiers")
    if not isinstance(tiers, list) or len(tiers) != 5:
        fail("V02", f"tiers must be a list of exactly 5 entries (got {len(tiers) if isinstance(tiers, list) else type(tiers).__name__})")
        return
    levels = [t.get("level") for t in tiers]
    if levels != [1, 2, 3, 4, 5]:
        fail("V02", f"tiers[].level must be [1,2,3,4,5] in order (got {levels})")


def check_v03_feature_set(data: dict, criteria_nums: set[int]) -> None:
    if data.get("schema_version", 1) < 2:
        return  # legacy fixtures may carry partial feature sets
    ok, detail = check_contiguous(criteria_nums)
    if not ok:
        fail("V03", f"references/criteria.md feature numbers are NOT contiguous {{1..N}}: {detail}")
        return
    audit_nums: set[int] = set()
    pillars = data.get("pillars", [])
    if not isinstance(pillars, list):
        return
    for p in pillars:
        for f in p.get("features", []) or []:
            num = f.get("num")
            if isinstance(num, int):
                audit_nums.add(num)
    if audit_nums != criteria_nums:
        missing = sorted(criteria_nums - audit_nums)
        extra = sorted(audit_nums - criteria_nums)
        parts = []
        if missing:
            parts.append(f"missing={missing[:20]}{'...' if len(missing) > 20 else ''}")
        if extra:
            parts.append(f"extra={extra[:20]}{'...' if len(extra) > 20 else ''}")
        fail("V03", f"pillars[].features[].num set does not equal criteria.md set ({len(audit_nums)} audit vs {len(criteria_nums)} criteria): {' '.join(parts)}")


def check_v04_recompute(data: dict) -> None:
    if data.get("schema_version", 1) < 2:
        return  # legacy fixtures may have hand-tweaked counts
    # Per-pillar
    for p in data.get("pillars", []) or []:
        features = p.get("features", []) or []
        applicable, passed, percent = recompute_group(features)
        pid = p.get("id")
        for key, expected in (("applicable", applicable), ("passed", passed), ("percent", percent)):
            actual = p.get(key)
            if actual != expected:
                fail("V04", f"pillars[id={pid}].{key} = {actual} but recompute from features says {expected}")
    # Per-tier
    by_level: dict[int, list[dict]] = {1: [], 2: [], 3: [], 4: [], 5: []}
    for p in data.get("pillars", []) or []:
        for f in p.get("features", []) or []:
            lvl = f.get("level")
            if isinstance(lvl, int) and lvl in by_level:
                by_level[lvl].append(f)
    for t in data.get("tiers", []) or []:
        level = t.get("level")
        if not isinstance(level, int):
            continue
        applicable, passed, percent = recompute_group(by_level.get(level, []))
        for key, expected in (("applicable", applicable), ("passed", passed), ("percent", percent)):
            actual = t.get(key)
            if actual != expected:
                fail("V04", f"tiers[level={level}].{key} = {actual} but recompute from features says {expected}")


def check_v05_max_tier(data: dict) -> None:
    if data.get("schema_version", 1) < 2:
        return
    summary = data.get("summary", {}) or {}
    declared = summary.get("max_tier_hierarchical")
    by_level: dict[int, tuple[int, int]] = {}
    for t in data.get("tiers", []) or []:
        level = t.get("level")
        if isinstance(level, int):
            by_level[level] = (t.get("applicable", 0) or 0, t.get("passed", 0) or 0)
    expected = compute_max_tier_hierarchical(by_level)
    if declared != expected:
        fail("V05", f"summary.max_tier_hierarchical = {declared} but hierarchical algorithm says {expected}")


def check_v06_flat_bucket(data: dict) -> None:
    summary = data.get("summary", {}) or {}
    fc = summary.get("flat_coverage", {}) or {}
    percent = fc.get("percent")
    declared = summary.get("flat_bucket_level")
    if not isinstance(percent, (int, float)):
        fail("V06", f"summary.flat_coverage.percent must be numeric (got {type(percent).__name__})")
        return
    expected = compute_flat_bucket(percent)
    if declared != expected:
        fail("V06", f"summary.flat_bucket_level = {declared} but bucket of {percent}% is {expected}")


def check_v07_rationale_kind(data: dict) -> None:
    na_kinds = {"profile_gate", "missing_precondition", "subsystem_absence"}
    any_kinds = na_kinds | {"broadened_evidence", "other"}
    for p in data.get("pillars", []) or []:
        pid = p.get("id")
        for f in p.get("features", []) or []:
            status = f.get("status")
            kind = f.get("rationale_kind")
            num = f.get("num")
            if status == "na":
                if kind not in na_kinds:
                    fail("V07", f"pillars[id={pid}].features[num={num}] status=na requires rationale_kind in {sorted(na_kinds)} (got {kind!r})")
            else:
                if kind is not None and kind not in any_kinds:
                    fail("V07", f"pillars[id={pid}].features[num={num}] rationale_kind={kind!r} not in {sorted(any_kinds)}")


def check_v08_top_actions(data: dict) -> None:
    actions = data.get("top_actions")
    if actions is None:
        return
    if not isinstance(actions, list):
        fail("V08", f"top_actions must be a list (got {type(actions).__name__})")
        return
    if len(actions) > 3:
        fail("V08", f"top_actions has {len(actions)} entries (max 3)")
    valid_nums: set[int] = set()
    for p in data.get("pillars", []) or []:
        for f in p.get("features", []) or []:
            num = f.get("num")
            if isinstance(num, int):
                valid_nums.add(num)
    for i, a in enumerate(actions):
        if not isinstance(a, dict):
            fail("V08", f"top_actions[{i}] must be an object")
            continue
        title = a.get("title")
        body = a.get("body")
        if not isinstance(title, str) or not title:
            fail("V08", f"top_actions[{i}].title must be a non-empty string")
        if not isinstance(body, str) or not body:
            fail("V08", f"top_actions[{i}].body must be a non-empty string")
        refs = a.get("feature_refs")
        if refs is None:
            continue
        if not isinstance(refs, list):
            fail("V08", f"top_actions[{i}].feature_refs must be a list of ints")
            continue
        for j, r in enumerate(refs):
            if not isinstance(r, int):
                fail("V08", f"top_actions[{i}].feature_refs[{j}] = {r!r} must be int")
                continue
            if r not in valid_nums:
                fail("V08", f"top_actions[{i}].feature_refs[{j}] = {r} does not match any feature.num in pillars[]")


def check_v09_remediation(data: dict, prompt_map: dict) -> None:
    if data.get("schema_version", 1) < 2:
        return
    has_prompt: dict[int, str] = {}
    for entry in prompt_map.get("features", []) or []:
        num = entry.get("feature_num")
        if entry.get("prompt_status") == "HAS_PROMPT" and isinstance(num, int):
            has_prompt[num] = entry.get("prompt_path", "")
    for p in data.get("pillars", []) or []:
        for f in p.get("features", []) or []:
            if f.get("status") != "fail":
                continue
            num = f.get("num")
            if num not in has_prompt:
                continue  # prompt-map says NEEDS_PROMPT or absent; not required
            rp = f.get("remediation_prompt")
            if not isinstance(rp, str) or not rp:
                fail("V09", f"feature num={num} status=fail and prompt-map says HAS_PROMPT (path={has_prompt[num]}), but remediation_prompt is empty/null")


def check_v10_audit_context(data: dict) -> None:
    schema = data.get("schema_version", 1)
    ctx = data.get("audit_context")
    if schema < 2:
        return  # grandfather clause: v1 may omit audit_context
    if not isinstance(ctx, dict):
        fail("V10", f"audit_context is required when schema_version>=2 (got {type(ctx).__name__})")
        return

    head_sha = ctx.get("head_sha")
    if not (isinstance(head_sha, str) and len(head_sha) >= 7 and re.fullmatch(r"[0-9a-fA-F]+", head_sha)):
        fail("V10", f"audit_context.head_sha must be a hex string of >=7 chars (got {head_sha!r})")

    branch = ctx.get("branch")
    if not isinstance(branch, str):
        fail("V10", f"audit_context.branch must be a string (got {type(branch).__name__})")

    dirty = ctx.get("worktree_dirty")
    if not isinstance(dirty, bool):
        fail("V10", f"audit_context.worktree_dirty must be bool (got {type(dirty).__name__})")

    dcount = ctx.get("dirty_files_count")
    if not (isinstance(dcount, int) and not isinstance(dcount, bool) and dcount >= 0):
        fail("V10", f"audit_context.dirty_files_count must be int >= 0 (got {dcount!r})")

    diff_sha = ctx.get("dirty_diff_sha256", "<missing>")
    if dirty is True:
        if not (isinstance(diff_sha, str) and len(diff_sha) == 64 and re.fullmatch(r"[0-9a-fA-F]+", diff_sha)):
            fail("V10", f"audit_context.dirty_diff_sha256 must be a 64-hex string when worktree_dirty=true (got {diff_sha!r})")
    elif dirty is False:
        if diff_sha is not None:
            fail("V10", f"audit_context.dirty_diff_sha256 must be null when worktree_dirty=false (got {diff_sha!r})")

    captured = ctx.get("captured_at")
    if not isinstance(captured, str) or not captured:
        fail("V10", f"audit_context.captured_at must be a non-empty ISO-8601 string (got {captured!r})")
    elif not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", captured):
        fail("V10", f"audit_context.captured_at must look like ISO-8601 (got {captured!r})")


def check_v11_prompt_drift(prompt_map: dict, prompts_dir: Path) -> None:
    if not prompts_dir.is_dir():
        fail("V11", f"prompts directory not found: {prompts_dir}")
        return
    disk_files: set[str] = set()
    for entry in sorted(prompts_dir.iterdir()):
        if entry.is_file() and entry.name.endswith(".md"):
            disk_files.add(f"{prompts_dir.name}/{entry.name}")

    map_paths_has: dict[str, list[int]] = {}
    map_paths_needs: set[str] = set()
    for f in prompt_map.get("features", []) or []:
        path = f.get("prompt_path")
        status = f.get("prompt_status")
        num = f.get("feature_num")
        if not isinstance(path, str):
            continue
        if status == "HAS_PROMPT":
            map_paths_has.setdefault(path, []).append(num)
        else:
            map_paths_needs.add(path)

    # Every disk file must be referenced by at least one HAS_PROMPT entry.
    for df in disk_files:
        if df not in map_paths_has:
            fail("V11", f"disk file has no HAS_PROMPT prompt-map entry: {df}")

    # Every HAS_PROMPT entry must point at a real disk file.
    for mp, nums in map_paths_has.items():
        if mp not in disk_files:
            fail("V11", f"prompt-map HAS_PROMPT entry references missing disk file: {mp} (feature_num(s)={nums})")


def main(argv: list[str] | None = None) -> int:
    # Default the three skill-internal artifacts to script-relative paths so
    # the validator works from any CWD (e.g., the audited repo root). When
    # CWD happens to be the skill dir, absolute and relative resolve
    # identically, so this is backward-compatible with CI.
    skill_dir = Path(__file__).resolve().parent.parent

    parser = argparse.ArgumentParser(
        description="Validate an audit-data JSON file against eleven structural checks.",
    )
    parser.add_argument("audit_data", help="Path to <slug>-data.json")
    parser.add_argument(
        "--prompt-map",
        default=str(skill_dir / "references" / "prompt-map.json"),
    )
    parser.add_argument(
        "--criteria",
        default=str(skill_dir / "references" / "criteria.md"),
    )
    parser.add_argument(
        "--prompts-dir",
        default=str(skill_dir / "prompts"),
    )
    args = parser.parse_args(argv)

    audit_path = Path(args.audit_data)
    if not audit_path.is_file():
        print(f"audit data file not found: {audit_path}", file=sys.stderr)
        return 3

    try:
        with audit_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        print(f"audit data is not valid JSON: {e}", file=sys.stderr)
        return 3

    prompt_map_path = Path(args.prompt_map)
    if not prompt_map_path.is_file():
        print(f"prompt-map file not found: {prompt_map_path}", file=sys.stderr)
        return 3
    with prompt_map_path.open("r", encoding="utf-8") as fh:
        prompt_map = json.load(fh)

    criteria_path = Path(args.criteria)
    criteria_nums = parse_criteria_nums(criteria_path)
    prompts_dir = Path(args.prompts_dir)

    check_v01_pillars(data)
    check_v02_tiers(data)
    check_v03_feature_set(data, criteria_nums)
    check_v04_recompute(data)
    check_v05_max_tier(data)
    check_v06_flat_bucket(data)
    check_v07_rationale_kind(data)
    check_v08_top_actions(data)
    check_v09_remediation(data, prompt_map)
    check_v10_audit_context(data)
    check_v11_prompt_drift(prompt_map, prompts_dir)

    if VIOLATIONS:
        for v in VIOLATIONS:
            print(v, file=sys.stderr)
        return 7
    return 0


if __name__ == "__main__":
    sys.exit(main())
