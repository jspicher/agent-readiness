#!/usr/bin/env python3
"""lint_prompt_placeholders.py -- guardrail against unresolved <PLACEHOLDER> tokens.

Walks top-level `prompts/*.md` (NOT `prompts/_graveyard/`) and reports any
remaining uppercase placeholder tokens of the form `<WORD_WITH_UNDERSCORES>`
that haven't been filtered through the allowlist.

Two kinds of code context are skipped, matching the markdown-linter convention
used by markdownlint / prettier / vale:

  1. Triple-backtick (or triple-tilde) fenced code blocks. The whole block
     is skipped between the opening and closing fence.
  2. Single-backtick inline code spans within a non-fenced line. Tokens
     wrapped in `...` are deliberate documentation of values the reader
     fills in by hand (e.g., `ghcr.io/<OWNER>/<IMAGE>` in a command
     example). These are not audit-pipeline substitution failures.

Anything OUTSIDE both contexts that matches the placeholder regex is flagged.
That catches the case the lint actually cares about: a prose sentence with a
bare `<OWNER>` token the audit pipeline should have substituted.

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
# Non-greedy inline-code span: a backtick, one-or-more non-backtick non-newline
# chars, a closing backtick. We strip these out before scanning the remaining
# prose for placeholder tokens. Double-backtick spans (`` ` ``) are rare in
# this corpus and would require a more elaborate state machine; revisit only
# if a real false-positive appears.
INLINE_CODE_RE = re.compile(r"`[^`\n]+?`")


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
        # Strip inline-code spans before scanning. A `<TOKEN>` inside backticks
        # is documentation, not a substitution failure.
        scannable = INLINE_CODE_RE.sub("", line)
        for m in PLACEHOLDER_RE.finditer(scannable):
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
