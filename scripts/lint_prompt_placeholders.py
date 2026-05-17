#!/usr/bin/env python3
"""lint_prompt_placeholders.py -- guardrail against unresolved <PLACEHOLDER> tokens.

Walks top-level `prompts/*.md` (NOT `prompts/_graveyard/`) and reports any
remaining uppercase placeholder tokens of the form `<WORD_WITH_UNDERSCORES>`
that haven't been filtered through the allowlist. Tokens inside triple-backtick
or triple-tilde fenced code blocks are skipped (those are usually deliberate
examples, e.g., `<TODO>` in a sample script).

Allowlist:
    <REPO_NAME>           -- substituted by the audit at Step 7
    <WHY_IT_FAILED*>      -- substituted by the audit at Step 7 (prefix match)

Regex is case-sensitive uppercase-only by design. Lowercase prompt-design
wrappers like `<system-reminder>` are correctly excluded. Do not widen
without updating the allowlist.

Exit codes:
    0  -- clean
    8  -- one or more violations found (printed as `path:line:token`)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"<[A-Z][A-Z0-9_]*>")
ALLOWED = {"<REPO_NAME>"}
FENCE_RE = re.compile(r"^(```|~~~)")


def lint_file(path: Path) -> list[str]:
    """Return a list of `path:line:token` violation strings for one file."""
    violations: list[str] = []
    in_fence = False
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [f"{path}: read error: {e}"]

    for lineno, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line.lstrip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in PLACEHOLDER_RE.finditer(line):
            tok = m.group(0)
            if tok in ALLOWED:
                continue
            if tok.startswith("<WHY_IT_FAILED"):
                continue
            violations.append(f"{path}:{lineno}:{tok}")
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint top-level prompts/*.md for unresolved <UPPERCASE> placeholders.",
    )
    parser.add_argument("--prompts-dir", default="prompts")
    args = parser.parse_args(argv)

    prompts_dir = Path(args.prompts_dir)
    if not prompts_dir.is_dir():
        print(f"prompts directory not found: {prompts_dir}", file=sys.stderr)
        return 2

    all_violations: list[str] = []
    for entry in sorted(prompts_dir.iterdir()):
        if not entry.is_file() or not entry.name.endswith(".md"):
            continue
        # _graveyard is a sibling directory, not a file, so iterdir at the
        # top level naturally excludes it. This branch only runs on top-level
        # files; defensive comment in case the layout ever changes.
        all_violations.extend(lint_file(entry))

    if all_violations:
        for v in all_violations:
            print(v)
        return 8
    return 0


if __name__ == "__main__":
    sys.exit(main())
