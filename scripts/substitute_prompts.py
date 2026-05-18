#!/usr/bin/env python3
"""substitute_prompts.py -- resolve and template a remediation prompt.

Given a feature number, the audited repo's name, and the audit rationale
("why it failed"), returns the prompt body with placeholders substituted.
Used as a library by scripts/build_audit_data.py and exposed as a CLI for
manual lookups.

Placeholders substituted (literal string replacement):
    <REPO_NAME>
    <WHY_IT_FAILED -- populated from rationale in your readiness report>

Resolution rules mirror SKILL.md Step 7:
    1. Look up the feature in references/prompt-map.json.
    2. If `prompt_status == "HAS_PROMPT"`: open prompt_path. Required to exist.
    3. If `prompt_status == "NEEDS_PROMPT"` AND a file exists at prompt_path
       OR prompts/<proposed_filename>: open whichever exists.
    4. Otherwise: return None. Caller decides whether that's an error (the
       builder treats it as null `remediation_prompt`; V09 only fires when
       prompt-map says HAS_PROMPT and the substituted text is empty).

CLI:
    python3 scripts/substitute_prompts.py \\
        --feature-num 3 \\
        --repo-name my-repo \\
        --rationale "Only .cursor/rules/ found; no AGENTS.md"

Library:
    from substitute_prompts import substitute, load_prompt_map
    pmap = load_prompt_map(skill_dir)
    body = substitute(feature_num=3, repo_name="my-repo",
                      rationale="...", prompt_map=pmap, skill_dir=skill_dir)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


REPO_NAME_PLACEHOLDER = "<REPO_NAME>"
WHY_PLACEHOLDER = "<WHY_IT_FAILED -- populated from rationale in your readiness report>"


def load_prompt_map(skill_dir: Path) -> dict:
    """Load references/prompt-map.json from the given skill directory."""
    path = skill_dir / "references" / "prompt-map.json"
    if not path.is_file():
        raise FileNotFoundError(f"prompt-map.json not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _resolve_prompt_file(entry: dict, skill_dir: Path) -> Optional[Path]:
    """Pick the right prompt file for a prompt-map entry, or None."""
    prompt_path = entry.get("prompt_path")
    status = entry.get("prompt_status")
    proposed = entry.get("proposed_filename")

    candidates: list[Path] = []
    if isinstance(prompt_path, str) and prompt_path:
        candidates.append(skill_dir / prompt_path)
    if status == "NEEDS_PROMPT" and isinstance(proposed, str) and proposed:
        candidates.append(skill_dir / "prompts" / proposed)

    for c in candidates:
        if c.is_file():
            return c
    return None


def substitute(
    feature_num: int,
    repo_name: str,
    rationale: str,
    *,
    prompt_map: dict,
    skill_dir: Path,
) -> Optional[str]:
    """Return the substituted prompt body, or None when no prompt is mapped.

    Substitution is literal-string `.replace()` -- no regex, no escaping
    concerns. The prompt body's quality-boundary section is preserved
    verbatim.
    """
    if not isinstance(feature_num, int):
        raise TypeError(f"feature_num must be int (got {type(feature_num).__name__})")
    if not isinstance(repo_name, str) or not repo_name:
        raise ValueError("repo_name must be a non-empty string")
    if not isinstance(rationale, str) or not rationale:
        raise ValueError("rationale must be a non-empty string")

    entry = None
    for f in prompt_map.get("features", []) or []:
        if f.get("feature_num") == feature_num:
            entry = f
            break
    if entry is None:
        return None

    prompt_file = _resolve_prompt_file(entry, skill_dir)
    if prompt_file is None:
        return None

    with prompt_file.open("r", encoding="utf-8") as fh:
        body = fh.read()

    body = body.replace(REPO_NAME_PLACEHOLDER, repo_name)
    body = body.replace(WHY_PLACEHOLDER, rationale)
    return body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve a remediation prompt and substitute placeholders.",
    )
    parser.add_argument("--feature-num", type=int, required=True)
    parser.add_argument("--repo-name", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument(
        "--skill-dir",
        default=None,
        help=(
            "Path to the skill root (containing SKILL.md, scripts/, "
            "references/, prompts/). Defaults to the parent of this script's "
            "directory."
        ),
    )
    args = parser.parse_args(argv)

    if args.skill_dir:
        skill_dir = Path(args.skill_dir)
    else:
        skill_dir = Path(__file__).resolve().parent.parent

    try:
        prompt_map = load_prompt_map(skill_dir)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 3

    body = substitute(
        feature_num=args.feature_num,
        repo_name=args.repo_name,
        rationale=args.rationale,
        prompt_map=prompt_map,
        skill_dir=skill_dir,
    )
    if body is None:
        print(
            f"no prompt mapped for feature_num={args.feature_num}",
            file=sys.stderr,
        )
        return 4

    sys.stdout.reconfigure(encoding="utf-8")  # Windows guard
    sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
