#!/usr/bin/env python3
"""build_audit_data.py -- assemble an audit-data JSON from per-feature judgments.

Closes the gap between the auditor's actual output (132 status+rationale
judgments) and the validator's structural requirements (recomputed pillar /
tier / summary aggregates, substituted remediation prompts, byte-identical
description strings from criteria.md). Without this script, auditors must
hand-write all of that arithmetic and transcribe 132 description strings --
which is the failure mode that drove ERR-20260518-001 (agent wrote a
disposable generator inside the audited repo).

Usage:
    python3 scripts/build_audit_data.py judgments.json \\
        [--out docs/agent-readiness/<slug>-data.json] \\
        [--criteria references/criteria.json] \\
        [--prompt-map references/prompt-map.json] \\
        [--prompts-dir prompts] \\
        [--skill-dir .]                # defaults to parent of this script's dir
        [--allow-missing-judgments]    # tests only; never use for real audits

Exit codes:
    0  -- emitted audit-data JSON
    2  -- usage error
    3  -- input file not found
    4  -- input file malformed / missing required keys
    5  -- judgment(s) missing for one or more features (without --allow-missing)
    6  -- judgment has bad shape (invalid status, missing rationale, etc.)

The judgments input file (JSON; YAML accepted if PyYAML is installed):

    {
      "schema_version": 2,
      "repo_name": "freelogo-staging",
      "generated_at": "2026-05-18T00:00:00Z",     # optional; auto-filled to now
      "audit_context": { ... output of capture_audit_context.sh ... },
      "repo_profile": { ... Step 0 dimensions ... },
      "applications": [{"path": ".", "description": "..."}],
      "judgments": {
        "1":   {"status": "pass", "rationale": "Found AGENTS.md at root."},
        "5":   {"status": "na",   "rationale_kind": "profile_gate",
                "rationale": "team_scale=solo AND visibility=private."},
        "20":  {"status": "fail", "rationale": "No CI freshness check."},
        ...
      },
      "top_actions": [
        {"title": "...", "body": "...", "feature_refs": [3, 20]}
      ]
    }

The output is validator-clean by construction (V01-V11 all pass), assuming:
- judgments cover every feature listed in references/criteria.json,
- na features carry a valid rationale_kind,
- audit_context is well-formed for schema_version >= 2,
- top_actions follows the V08 shape (title+body non-empty, feature_refs real).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

# substitute_prompts.py sits in the same directory as this script.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from substitute_prompts import load_prompt_map, substitute  # noqa: E402


TIER_LABELS = {
    1: "Basic",
    2: "Intermediate",
    3: "Advanced",
    4: "Power-user",
    5: "Self-improving",
}

VALID_STATUSES = {"pass", "fail", "na"}
VALID_NA_KINDS = {"profile_gate", "missing_precondition", "subsystem_absence"}
VALID_ANY_KINDS = VALID_NA_KINDS | {"broadened_evidence", "other"}


# --- input loading --------------------------------------------------------- #


def _load_input(path: Path) -> dict:
    if not path.is_file():
        print(f"input not found: {path}", file=sys.stderr)
        sys.exit(3)
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError:
            print(
                "input is YAML but PyYAML is not installed (pip install pyyaml). "
                "Either install it or convert the input to JSON.",
                file=sys.stderr,
            )
            sys.exit(2)
        return yaml.safe_load(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"input is not valid JSON: {e}", file=sys.stderr)
        sys.exit(4)


def _require(data: dict, key: str, source: str) -> Any:
    if key not in data:
        print(f"{source}: missing required key '{key}'", file=sys.stderr)
        sys.exit(4)
    return data[key]


# --- aggregate math (matches validate_audit_data.py) ----------------------- #


def _group_stats(features: list[dict]) -> tuple[int, int, int]:
    applicable = sum(1 for f in features if f["status"] != "na")
    passed = sum(1 for f in features if f["status"] == "pass")
    percent = round(passed / applicable * 100) if applicable > 0 else 0
    return applicable, passed, percent


def _max_tier_hierarchical(tier_stats: dict[int, tuple[int, int]]) -> int:
    """Same algorithm as validate_audit_data.compute_max_tier_hierarchical."""
    result = 0
    for level in (1, 2, 3, 4, 5):
        applicable, passed = tier_stats.get(level, (0, 0))
        if applicable == 0 or (passed / applicable) >= 0.80:
            result = level
        else:
            break
    return result


def _flat_bucket(percent: float) -> int:
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


# --- build ---------------------------------------------------------------- #


def _validate_judgment(num: int, j: dict) -> None:
    if not isinstance(j, dict):
        print(f"judgments[{num}] must be an object", file=sys.stderr)
        sys.exit(6)
    status = j.get("status")
    if status not in VALID_STATUSES:
        print(
            f"judgments[{num}].status = {status!r} (expected one of {sorted(VALID_STATUSES)})",
            file=sys.stderr,
        )
        sys.exit(6)
    rationale = j.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        print(
            f"judgments[{num}].rationale must be a non-empty string",
            file=sys.stderr,
        )
        sys.exit(6)
    kind = j.get("rationale_kind")
    if status == "na":
        if kind not in VALID_NA_KINDS:
            print(
                f"judgments[{num}] status=na requires rationale_kind in "
                f"{sorted(VALID_NA_KINDS)} (got {kind!r})",
                file=sys.stderr,
            )
            sys.exit(6)
    else:
        if kind is not None and kind not in VALID_ANY_KINDS:
            print(
                f"judgments[{num}].rationale_kind = {kind!r} not in "
                f"{sorted(VALID_ANY_KINDS)}",
                file=sys.stderr,
            )
            sys.exit(6)


def build(
    input_path: Path,
    criteria_path: Path,
    prompt_map_path: Path,
    skill_dir: Path,
    allow_missing: bool,
) -> dict:
    src = _load_input(input_path)
    if not isinstance(src, dict):
        print(f"input is not a JSON/YAML object (got {type(src).__name__})", file=sys.stderr)
        sys.exit(4)

    schema_version = src.get("schema_version", 2)
    repo_name = _require(src, "repo_name", "input")
    audit_context = src.get("audit_context")
    repo_profile = src.get("repo_profile")
    applications = _require(src, "applications", "input")
    judgments_raw = _require(src, "judgments", "input")
    top_actions = src.get("top_actions", [])
    generated_at = src.get("generated_at") or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if not isinstance(judgments_raw, dict):
        print("input.judgments must be an object keyed by feature number", file=sys.stderr)
        sys.exit(4)

    # Normalize judgment keys to ints (accept int or numeric string)
    judgments: dict[int, dict] = {}
    for k, v in judgments_raw.items():
        try:
            judgments[int(k)] = v
        except (TypeError, ValueError):
            print(f"judgments key {k!r} is not a valid feature number", file=sys.stderr)
            sys.exit(4)

    # Load criteria
    if not criteria_path.is_file():
        print(
            f"criteria.json not found at {criteria_path}. "
            f"Run scripts/extract_criteria.py first.",
            file=sys.stderr,
        )
        sys.exit(3)
    criteria = json.loads(criteria_path.read_text(encoding="utf-8"))
    criteria_features = {f["num"]: f for f in criteria.get("features", [])}
    if not criteria_features:
        print(f"criteria.json has no features", file=sys.stderr)
        sys.exit(4)

    # Load prompt-map
    if not prompt_map_path.is_file():
        print(f"prompt-map.json not found at {prompt_map_path}", file=sys.stderr)
        sys.exit(3)
    prompt_map = json.loads(prompt_map_path.read_text(encoding="utf-8"))

    # Check for missing judgments
    missing = sorted(set(criteria_features) - set(judgments))
    if missing and not allow_missing:
        print(
            f"missing judgments for {len(missing)} feature(s); first few: "
            f"{missing[:10]}. Use --allow-missing-judgments to bypass "
            f"(tests only; never for real audits).",
            file=sys.stderr,
        )
        sys.exit(5)

    extras = sorted(set(judgments) - set(criteria_features))
    if extras:
        print(
            f"warning: judgments include unknown feature number(s): {extras}",
            file=sys.stderr,
        )

    # Build per-feature records
    all_features: list[dict] = []
    for num in sorted(criteria_features):
        crit = criteria_features[num]
        if num not in judgments:
            # allow-missing path: synthesize a fail with a placeholder rationale
            j = {"status": "fail", "rationale": "MISSING JUDGMENT -- builder default"}
        else:
            j = judgments[num]
            _validate_judgment(num, j)

        feature_rec: dict = {
            "num": num,
            "name": crit["name"],
            "level": crit["level"],
            "description": crit["description"],
            "status": j["status"],
            "rationale": j["rationale"],
        }
        kind = j.get("rationale_kind")
        if kind is not None:
            feature_rec["rationale_kind"] = kind

        # Remediation prompt for fails only
        if j["status"] == "fail":
            try:
                body = substitute(
                    feature_num=num,
                    repo_name=repo_name,
                    rationale=j["rationale"],
                    prompt_map=prompt_map,
                    skill_dir=skill_dir,
                )
            except (TypeError, ValueError) as e:
                print(f"prompt substitution error for feature #{num}: {e}", file=sys.stderr)
                sys.exit(6)
            feature_rec["remediation_prompt"] = body  # may be None
        else:
            feature_rec["remediation_prompt"] = None

        all_features.append(feature_rec)

    # Group by pillar
    pillars: list[dict] = []
    for pillar_id in (1, 2, 3, 4, 5, 6, 7):
        pillar_features = [
            f for f in all_features
            if criteria_features[f["num"]]["pillar"] == pillar_id
        ]
        applicable, passed, percent = _group_stats(pillar_features)
        # All features in a pillar share the same pillar_name; pull the first.
        pillar_name = next(
            (criteria_features[f["num"]]["pillar_name"] for f in pillar_features),
            "",
        )
        pillars.append({
            "id": pillar_id,
            "name": pillar_name,
            "applicable": applicable,
            "passed": passed,
            "percent": percent,
            "features": pillar_features,
        })

    # Group by tier
    tiers: list[dict] = []
    by_level: dict[int, list[dict]] = {1: [], 2: [], 3: [], 4: [], 5: []}
    for f in all_features:
        by_level[f["level"]].append(f)
    for level in (1, 2, 3, 4, 5):
        applicable, passed, percent = _group_stats(by_level[level])
        tiers.append({
            "level": level,
            "label": TIER_LABELS[level],
            "applicable": applicable,
            "passed": passed,
            "percent": percent,
        })

    # Summary
    flat_applicable, flat_passed, flat_percent = _group_stats(all_features)
    tier_stats = {t["level"]: (t["applicable"], t["passed"]) for t in tiers}
    max_tier = _max_tier_hierarchical(tier_stats)
    flat_bucket = _flat_bucket(flat_percent)

    strongest = max(pillars, key=lambda p: (p["percent"], -p["id"]))
    weakest = min(pillars, key=lambda p: (p["percent"], p["id"]))

    # Readiness tracks: P1-5 = assisted, P1-7 = autonomous
    def _track_stats(pillar_ids: list[int]) -> dict:
        feats = [
            f for p in pillars if p["id"] in pillar_ids for f in p["features"]
        ]
        a, pa, pc = _group_stats(feats)
        return {"passed": pa, "applicable": a, "percent": pc}

    summary: dict = {
        "flat_coverage": {
            "passed": flat_passed,
            "applicable": flat_applicable,
            "percent": flat_percent,
        },
        "max_tier_hierarchical": max_tier,
        "flat_bucket_level": flat_bucket,
        "strongest_pillar": {
            "id": strongest["id"],
            "name": strongest["name"],
            "percent": strongest["percent"],
        },
        "weakest_pillar": {
            "id": weakest["id"],
            "name": weakest["name"],
            "percent": weakest["percent"],
        },
        "readiness_tracks": {
            "assisted": _track_stats([1, 2, 3, 4, 5]),
            "autonomous": _track_stats([1, 2, 3, 4, 5, 6, 7]),
        },
    }

    out: dict = {
        "schema_version": schema_version,
        "repo_name": repo_name,
        "generated_at": generated_at,
    }
    if audit_context is not None:
        out["audit_context"] = audit_context
    if repo_profile is not None:
        out["repo_profile"] = repo_profile
    out["applications"] = applications
    out["summary"] = summary
    out["tiers"] = tiers
    out["pillars"] = pillars
    out["top_actions"] = top_actions
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assemble an audit-data JSON from per-feature judgments.",
    )
    parser.add_argument("input", help="Path to judgments.json (or .yaml)")
    parser.add_argument("--out", default=None, help="Write to this path (default: stdout)")
    parser.add_argument("--criteria", default=None)
    parser.add_argument("--prompt-map", default=None)
    parser.add_argument("--skill-dir", default=None)
    parser.add_argument(
        "--allow-missing-judgments",
        action="store_true",
        help="Synthesize a 'fail' for any feature without a judgment. Tests only.",
    )
    args = parser.parse_args(argv)

    skill_dir = Path(args.skill_dir).resolve() if args.skill_dir else Path(__file__).resolve().parent.parent
    criteria_path = Path(args.criteria) if args.criteria else skill_dir / "references" / "criteria.json"
    prompt_map_path = Path(args.prompt_map) if args.prompt_map else skill_dir / "references" / "prompt-map.json"

    out = build(
        input_path=Path(args.input),
        criteria_path=criteria_path,
        prompt_map_path=prompt_map_path,
        skill_dir=skill_dir,
        allow_missing=args.allow_missing_judgments,
    )

    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
