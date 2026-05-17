[Readiness Fix] <REPO_NAME> License

Fix the failing signal: License ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: License
**Score**: [0/1]
**Description**: Clear license at root
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

License at repository root – check for a top-level `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `MIT-LICENSE`, `COPYING`, or `COPYING.LESSER` file whose contents are an unmodified, attributable copy of an SPDX-recognized license (https://spdx.org/licenses/) with the copyright `[year] [holder]` line correctly substituted. PASS requires ALL of:

1. **A LICENSE file exists at the repository root** (not buried in `docs/legal/`, not only inside subpackages). GitHub's license detector only inspects the root and recognized variants — files at non-standard paths are invisible to it and to downstream package managers.
2. **The file contains an SPDX-recognized license text** (MIT, Apache-2.0, BSD-3-Clause, BSD-2-Clause, GPL-3.0-only, GPL-3.0-or-later, LGPL-3.0-or-later, MPL-2.0, ISC, Unlicense, CC0-1.0, AGPL-3.0-or-later, BlueOak-1.0.0, etc.). Verify against the SPDX License List; a custom "All rights reserved" blurb or a paraphrased MIT clone is a FAIL — downstream tooling (npm, GitHub, FOSSA, ScanCode) cannot classify it and treats the repo as proprietary.
3. **Copyright placeholders are filled in** with a real year (or year range) and a real holder name. `Copyright (c) [year] [fullname]` left literal is a FAIL. `Copyright (c) 2019 Facebook, Inc.` in a 2026 fork of an unrelated repo is also a FAIL — the holder must match the project's actual owner.
4. **The manifest declares the same license** using the SPDX identifier:
   - `package.json` → `"license": "MIT"` (string; SPDX ID). Arrays (`"licenses": [...]`) are deprecated since npm 4. `"license": "SEE LICENSE IN <filename>"` is only valid for non-SPDX licenses.
   - `Cargo.toml` → `license = "MIT OR Apache-2.0"` (SPDX expression) OR `license-file = "LICENSE"` for non-SPDX licenses (mutually exclusive).
   - `pyproject.toml` → `license = "MIT"` (PEP 639, SPDX string) and/or trove classifier `License :: OSI Approved :: MIT License`. The legacy `license = {file = "LICENSE"}` table form still works but is being deprecated.
   - `composer.json` → `"license": "MIT"` (SPDX ID or array of IDs for dual-licensing).
   - `*.gemspec` → `spec.license = "MIT"` (single SPDX ID) or `spec.licenses = ["MIT", "Apache-2.0"]`.
   - `go.mod` has no license field; the root LICENSE file is the only signal.
5. **The manifest license and the LICENSE file agree.** A `package.json` claiming `"license": "MIT"` paired with an `Apache-2.0` LICENSE file is a FAIL — pkg.go.dev, npm's license badge, and `license-checker` will all disagree about what the project actually is, and downstream consumers cannot trust either source.

A README sentence saying "MIT licensed" without a LICENSE file is documentation, not a license grant, and FAILs this signal. GitHub explicitly warns "no license" defaults to exclusive copyright — meaning agents (and humans) have no legal right to copy, modify, or distribute the code, which blocks every realistic agent workflow including forking, vendoring, and PR contributions.

## Your Task

1. Explore the repository to determine the current state: list every `LICENSE*`, `COPYING*`, `MIT-LICENSE*`, `UNLICENSE*` file (at root and recursively), every manifest file (`package.json`, `Cargo.toml`, `pyproject.toml`, `setup.cfg`, `setup.py`, `composer.json`, `*.gemspec`, `go.mod`), and any `README.md` license section. Note the upstream project (if this is a fork) and the actual copyright holder (organization name in `package.json` `author`/`publisher`, git commit authors, or CONTRIBUTING.md).
2. Pick the right license — if the project already uses one in its manifest or README, honor that choice. Otherwise, default to the ecosystem norm: **MIT** for most Node/Python/Ruby/PHP libraries, **Apache-2.0** when patent grant matters (most enterprise code), **MIT OR Apache-2.0** dual for Rust (matches the rest of the Rust ecosystem and `cargo new`'s default), **BSD-3-Clause** for academic forks, **MPL-2.0** for weak-copyleft, **AGPL-3.0-or-later** for hosted-service moats. Use https://choosealicense.com to break ties.
3. Write the LICENSE file at repository root using the **unmodified** canonical text from https://spdx.org/licenses/ (or the SPDX `text` JSON field). Substitute `<year>` with the current year (or `2019-2026` for a long-lived project) and `<copyright holders>` with the real owner. Save as `LICENSE` (no extension) unless the project already uses `LICENSE.md` or `COPYING`.
4. Update the manifest(s) to declare the matching SPDX identifier. If the project is dual-licensed, use an SPDX expression (`"MIT OR Apache-2.0"`) and ship BOTH license files (e.g. `LICENSE-MIT` + `LICENSE-APACHE`) per Rust convention.
5. Verify: run `gh api repos/<owner>/<repo>/license` (or push and wait ~1 minute, then refresh the repo homepage) and confirm GitHub's "About" sidebar now shows the license name. For Node, `npx license-checker --production --summary` from a consumer should show the new license. For Cargo, `cargo metadata --format-version 1 | jq '.packages[0].license'`.
6. Keep changes focused on this signal — do not relicense any third-party vendored code, do not edit per-file SPDX headers in existing source unless explicitly asked.
7. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** leaving `[year]` / `[fullname]` / `<copyright holders>` placeholders literal in the LICENSE file. GitHub's license detector still classifies the file but every downstream attribution notice ships the placeholder verbatim. Substitute real values.
- **NO** copying a LICENSE file from another project without changing the copyright holder line. Shipping `Copyright (c) 2011-2024 GitHub Inc.` in your repo because you copied the MIT text from `github/docs` is a misappropriation of their attribution, not a license for your code.
- **NO** paraphrased or "lightly edited" license text. Tools (GitHub's licensee gem, ScanCode, FOSSA, npm) match against canonical SPDX text; a single reworded sentence drops the match and the repo is silently classified as "Other" or proprietary.
- **NO** manifest/LICENSE mismatch. `"license": "MIT"` in `package.json` next to an `Apache-2.0` LICENSE file actively lies to every consumer and is worse than no manifest field at all.
- **NO** `"license": "UNLICENSED"` or `"license": "SEE LICENSE IN LICENSE"` paired with a real OSI license. The first means "proprietary, you may not use this"; the second hides the license from npmjs.com's badge and from `npm view <pkg> license`. Use the SPDX ID.
- **NO** `LICENSE.txt` in `docs/`, `legal/`, or a subpackage as the only copy. GitHub does not detect non-root LICENSE files; the repo's About sidebar will show "No license".
- **NO** "All rights reserved" custom blurbs for a project that clearly wants outside contributions. That text revokes every right an agent or contributor would need.
- **NO** adding a LICENSE file without updating the manifest's `license` field — half-done is worse than not-done because it produces conflicting signals.
- **NO** SPDX header comments inside every source file as a substitute for a root LICENSE. Per-file headers are a complement, not a replacement.

Examples of BAD fixes:
- Creating `LICENSE` containing `Copyright (c) [year] [fullname]\n\nPermission is hereby granted...` — placeholders unfilled, holder unknown, the file is unenforceable boilerplate.
- Adding `LICENSE.md` with the text "This project is MIT licensed. See https://opensource.org/licenses/MIT" — that's a pointer, not a grant; GitHub will not classify the repo as MIT.
- Updating `package.json` to `"license": "MIT"` while the existing `LICENSE` file is BSD-3-Clause text. Now the repo lies in two places.
- Picking AGPL-3.0-or-later for a permissively-licensed dependency hub without warning maintainers — relicensing is a load-bearing decision, ask the user when in doubt.
- Dropping `LICENSE.apache-2.0` and `LICENSE.mit` into a Rust crate but leaving `license = "MIT"` (single ID) in `Cargo.toml`. Use `license = "MIT OR Apache-2.0"` so cargo and crates.io see both.
- Copying the MIT text but leaving `Copyright (c) 2014 Evan You` (from a Vue fork) when the project is now maintained by a different organization.

Examples of GOOD fixes:
- For a Node library named `acme-utils` owned by Acme Corp:
  ```
  LICENSE (at repo root, no extension):
  MIT License

  Copyright (c) 2026 Acme Corp

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
  ```
  Paired with `package.json`:
  ```json
  {
    "name": "acme-utils",
    "version": "1.4.0",
    "license": "MIT",
    "author": "Acme Corp <eng@acme.example>"
  }
  ```
  And optionally per-file SPDX header on new source files:
  ```ts
  // SPDX-License-Identifier: MIT
  // SPDX-FileCopyrightText: 2026 Acme Corp
  ```
- For a Rust crate, ship `LICENSE-MIT` + `LICENSE-APACHE` at root with both canonical SPDX texts, and set `Cargo.toml`:
  ```toml
  [package]
  name = "acme-core"
  version = "0.3.0"
  license = "MIT OR Apache-2.0"
  ```
- For a Python package using PEP 639, `pyproject.toml`:
  ```toml
  [project]
  name = "acme-core"
  version = "0.3.0"
  license = "Apache-2.0"
  license-files = ["LICENSE"]
  ```
- For a long-lived project with many contributors, use a year range and a generic holder line: `Copyright (c) 2019-2026 The Acme Authors`, and add an `AUTHORS` file enumerating contributors.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- SPDX License List (canonical IDs + text): https://spdx.org/licenses/
- SPDX License Expressions (dual/multi-licensing syntax): https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/
- choosealicense.com (decision guide): https://choosealicense.com/
- GitHub: Adding a license to a repository: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-license-to-a-repository
- GitHub: Licensing a repository (no-license default = exclusive copyright): https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository
- GitHub's license detection library (licensee): https://github.com/licensee/licensee
- npm `package.json` license field: https://docs.npmjs.com/cli/v10/configuring-npm/package-json#license
- Cargo manifest `license` / `license-file`: https://doc.rust-lang.org/cargo/reference/manifest.html#the-license-and-license-file-fields
- Rust API Guidelines on dual MIT/Apache-2.0 licensing: https://rust-lang.github.io/api-guidelines/necessities.html#crate-and-its-dependencies-have-a-permissive-license-c-permissive
- PEP 639 (Python license metadata): https://peps.python.org/pep-0639/
- PyPI trove classifiers (License): https://pypi.org/classifiers/
- REUSE Specification (per-file SPDX headers + LICENSES/ folder): https://reuse.software/spec/
</system-reminder>
