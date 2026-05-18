#!/usr/bin/env python3
"""extract_criteria.py -- parse references/criteria.md into criteria.json.

Walks the markdown taxonomy and emits a machine-readable mirror that the
audit-data builder (scripts/build_audit_data.py) joins against per-feature
judgments. Run this whenever criteria.md changes:

    python3 scripts/extract_criteria.py [--criteria references/criteria.md] \\
        [--out references/criteria.json]

Exit codes:
    0 -- emitted criteria.json
    2 -- usage error
    3 -- criteria.md not found
    4 -- parse error (feature numbers not contiguous, or row malformed)

The output schema:

    {
      "schema_version": 1,
      "_meta": {
        "generated_from": "references/criteria.md",
        "feature_count": 132,
        "pillar_counts": {"1": 21, "2": 28, ...}
      },
      "features": [
        {
          "num": 1,
          "pillar": 1,
          "pillar_name": "Agent Instructions",
          "level": 2,                          # int, not "L2"
          "name": "Agent instruction file",
          "description": "A dedicated file telling agents how to work...",
          "evidence": "AGENTS.md, CLAUDE.md, COPILOT.md at root",
          "conditional_note": null             # raw "*(...)*" qualifier if present
        },
        ...
      ]
    }
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PILLAR_HEADING_RE = re.compile(r"^##\s+Pillar\s+(\d+)\s+·\s+(.+?)(?:\s+\*\(.+\)\*)?\s*$")
TABLE_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*L(\d)\s*\|(.+)$")
BOLD_NAME_RE = re.compile(r"^\*\*(.+?)\*\*\s*(\*\(.+?\)\*)?\s*$")


def parse_feature_row(row_body: str) -> tuple[str, str | None, str, str]:
    """Split the remaining cells of a feature row.

    row_body is everything after `| {num} | L{lvl} |` -- so:
        " **name** *(qualifier)* | description | evidence |"

    Splits on the next 3 unescaped pipes. Returns (name, conditional_note,
    description, evidence). conditional_note is the raw "*(...)*" text or None.
    """
    parts = [p.strip() for p in row_body.split("|")]
    if len(parts) < 4:
        raise ValueError(f"row has too few cells: {row_body!r}")
    raw_name = parts[0]
    description = parts[1]
    evidence = parts[2]

    m = BOLD_NAME_RE.match(raw_name)
    if not m:
        cleaned = raw_name.strip("*").strip()
        return cleaned, None, description, evidence

    name = m.group(1).strip()
    conditional_note = m.group(2)
    if conditional_note is not None:
        conditional_note = conditional_note.strip().strip("*").strip("()").strip()
    return name, conditional_note, description, evidence


def extract(criteria_path: Path) -> dict:
    if not criteria_path.is_file():
        print(f"criteria file not found: {criteria_path}", file=sys.stderr)
        sys.exit(3)

    features: list[dict] = []
    current_pillar: int | None = None
    current_pillar_name: str | None = None

    with criteria_path.open("r", encoding="utf-8") as fh:
        for line_no, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n")

            m_pillar = PILLAR_HEADING_RE.match(line)
            if m_pillar:
                current_pillar = int(m_pillar.group(1))
                current_pillar_name = m_pillar.group(2).strip()
                continue

            m_row = TABLE_ROW_RE.match(line)
            if not m_row:
                continue

            num = int(m_row.group(1))
            level = int(m_row.group(2))
            row_body = m_row.group(3)

            if current_pillar is None or current_pillar_name is None:
                print(
                    f"line {line_no}: feature {num} appears before any pillar heading",
                    file=sys.stderr,
                )
                sys.exit(4)

            try:
                name, cond, desc, evidence = parse_feature_row(row_body)
            except ValueError as e:
                print(f"line {line_no}: {e}", file=sys.stderr)
                sys.exit(4)

            features.append({
                "num": num,
                "pillar": current_pillar,
                "pillar_name": current_pillar_name,
                "level": level,
                "name": name,
                "description": desc,
                "evidence": evidence,
                "conditional_note": cond,
            })

    nums = [f["num"] for f in features]
    if sorted(nums) != list(range(1, len(nums) + 1)):
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
        extra = sorted(set(nums) - set(range(1, len(nums) + 1)))
        print(
            f"feature numbers not contiguous {{1..N}}; missing={missing} extra={extra}",
            file=sys.stderr,
        )
        sys.exit(4)

    pillar_counts: dict[str, int] = {}
    for f in features:
        key = str(f["pillar"])
        pillar_counts[key] = pillar_counts.get(key, 0) + 1

    return {
        "schema_version": 1,
        "_meta": {
            "generated_from": str(criteria_path).replace("\\", "/"),
            "feature_count": len(features),
            "pillar_counts": pillar_counts,
        },
        "features": features,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract criteria.md into criteria.json.",
    )
    parser.add_argument("--criteria", default="references/criteria.md")
    parser.add_argument("--out", default="references/criteria.json")
    args = parser.parse_args(argv)

    out = extract(Path(args.criteria))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(
        f"Wrote {out_path} -- {out['_meta']['feature_count']} features "
        f"across {len(out['_meta']['pillar_counts'])} pillars",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
