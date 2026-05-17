[Readiness Fix] <REPO_NAME> Git Attributes

Fix the failing signal: Git Attributes ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Git Attributes
**Score**: [0/1]
**Description**: `.gitattributes` normalizes line endings, marks binaries, overrides Linguist stats, and tracks large/binary assets through Git LFS
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Git attributes – check for a checked-in `.gitattributes` at the repo root that defines, at minimum, line-ending normalization, binary handling, Linguist overrides for generated/vendored code, and (if the repo stores assets > 100MB or design files) Git LFS tracking. PASS requires concrete rules, not an empty file or a single `* text=auto` line. Specifically:

1. **Line endings**: a top rule of `* text=auto eol=lf` (or `eol=crlf` only if the repo is Windows-only — rare). Without normalization, Windows clones via `core.autocrlf=true` rewrite line endings on checkout and the next commit shows every file as modified — a common agent footgun that produces noisy diffs and breaks `git blame`.
2. **Binary marking**: explicit `binary` (or `-text -diff`) entries for image, archive, font, and compiled asset extensions the repo actually contains (`*.png`, `*.jpg`, `*.webp`, `*.pdf`, `*.zip`, `*.gz`, `*.woff2`, `*.ico`, `*.so`, `*.dll`, `*.wasm`). Without these, Git tries to diff/merge them as text and corrupts the file on conflict.
3. **Linguist overrides**: `linguist-generated`, `linguist-vendored`, `linguist-documentation`, or `linguist-language=<X>` directives that exclude lockfiles, minified output, and bundled vendor code from GitHub's language statistics, code review diffs, and search results. Without overrides, a TypeScript repo that vendors a 500KB minified JS bundle reads as "60% JavaScript" on GitHub and that bundle pollutes every PR diff.
4. **Git LFS tracking** (if applicable): `filter=lfs diff=lfs merge=lfs -text` lines for any extension the repo legitimately stores at scale (`*.psd`, `*.sketch`, `*.fig`, `*.mp4`, `*.zip > 100MB`, ML model weights `*.pt`/`*.onnx`/`*.gguf`). Required only if the repo actually contains such files; do not add LFS rules for extensions the repo does not use.
5. **`export-ignore`** (npm/library repos only): mark `tests/`, `docs/`, `.github/`, and `.gitattributes` itself with `export-ignore` so they are stripped from `git archive` tarballs published to npm.

A `.gitattributes` containing only `* text=auto` (no `eol=lf`, no binary marks, no Linguist overrides) is a stub and FAILs this signal. A missing file FAILs.

## Your Task

1. Explore the repository to understand the current state related to this signal:
   - Read the existing `.gitattributes` (if any) and note what is already covered.
   - Identify the primary language(s) and frameworks by inspecting `package.json`, `pyproject.toml`, `go.mod`, etc.
   - List binary asset types actually present (`git ls-files | grep -iE '\.(png|jpg|jpeg|gif|webp|pdf|zip|gz|tar|woff2?|otf|ttf|ico|mp4|psd|sketch|fig|so|dll|wasm|pt|onnx)$'`).
   - List generated/vendored paths: `dist/`, `build/`, `out/`, `*.min.js`, `vendor/`, `third_party/`, lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `Gemfile.lock`, `poetry.lock`).
   - Check whether Git LFS is initialized: look for `.gitattributes` `filter=lfs` lines, a `.git/lfs/` directory, or an existing `*.psd`/`*.fig` etc. tracked as text.
2. Make **substantive improvements** by writing a project-tuned `.gitattributes` at the repo root that covers the four categories above. Tune each rule to the repo:
   - Only mark binary extensions the repo actually contains — do not paste a 200-line "everything-ever" template.
   - Only add Linguist overrides for paths that exist (do not `linguist-generated` a `dist/` directory if the repo has no build output).
   - Only add LFS lines if the repo currently stores those file types or has a documented plan to. If you add LFS rules, run `git lfs install` in the repo and `git lfs migrate import --include="*.psd"` to move existing tracked binaries.
3. Verify the file parses and takes effect:
   - `git check-attr -a -- path/to/sample.png` should report `binary: set`, `diff: unset`, `merge: unset`.
   - `git check-attr -a -- src/index.ts` should show `text: auto`, `eol: lf`.
   - `git check-attr -a -- package-lock.json` should show `linguist-generated: true`.
   - Run `git add --renormalize .` once after committing the new `.gitattributes` so existing files pick up `eol=lf`. Commit any normalization diff in a separate commit so the policy commit stays reviewable.
4. Keep changes focused on this signal — do not refactor `.gitignore`, restructure directories, or move assets.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** a one-line `.gitattributes` containing only `* text=auto`. That omits `eol=lf` (which is what actually fixes Windows CRLF churn), omits binary marks, and omits Linguist overrides — it is a stub.
- **NO** a generic "github/gitattributes" community template copy-pasted verbatim covering 40 languages the repo does not use. Every rule must point at a file extension or path the repo actually contains. Dead rules signal zero project knowledge and rot the moment someone trusts the file.
- **NO** marking text files (`.json`, `.yaml`, `.md`, `.svg`) as `binary`. SVG is XML; YAML and JSON are text. Marking them binary disables diffing and blame on files engineers and agents read constantly.
- **NO** Linguist overrides on paths that do not exist (`dist/* linguist-generated=true` in a repo with no `dist/`). Lint your file by listing each path on the left side and confirming it resolves.
- **NO** adding `*.psd filter=lfs diff=lfs merge=lfs -text` to a repo that has no `.psd` files, no LFS billing, and no `git lfs install` run. The rule fails closed: any future `.psd` commit blows up with "git-lfs not installed" or silently lands as a 500MB blob in the regular history.
- **NO** wildcard `* binary` or `* -text` lines. That disables diffing on the entire repo.
- **NO** committing `.gitattributes` without running `git add --renormalize .`. The file applies only to future writes; existing files keep their old line endings until renormalized, so Windows contributors still get CRLF on next checkout.
- **NO** putting LFS rules in `.gitattributes` without also committing `.gitignore` rules for `.git/lfs/objects/` cache directories or documenting `git lfs install` in the README. LFS without onboarding instructions strands new clones.

Examples of BAD fixes:
- A `.gitattributes` containing only:
  ```
  * text=auto
  ```
  This is the default Git inference and does not normalize to LF. Windows clones still flip line endings.
- Pasting the entire `github/gitattributes/Web.gitattributes` (every web extension known) into a Python Django repo. 90% of rules match nothing; the file is unauditable.
- `*.json binary` to "stop noisy diffs in package-lock.json". The fix is `package-lock.json linguist-generated=true` (collapses the diff on GitHub but keeps it readable when needed), not blanket-binary on every JSON in the repo.
- `*.psd filter=lfs diff=lfs merge=lfs -text` in a repo with no `.psd` files and no `git lfs install`. First commit of a real `.psd` will fail or corrupt history.
- `dist/** linguist-generated=true` in a repo whose build output is at `build/`, not `dist/`. Rule never matches.

Examples of GOOD fixes:

- A Node/TypeScript web app `.gitattributes`:
  ```gitattributes
  # Default: normalize all text files to LF on commit, native on checkout.
  # Without eol=lf, Windows clones with core.autocrlf=true produce phantom diffs.
  * text=auto eol=lf

  # Shell + config files: force LF (CRLF breaks shebangs and YAML parsers).
  *.sh        text eol=lf
  *.bash      text eol=lf
  Dockerfile  text eol=lf
  *.yml       text eol=lf
  *.yaml      text eol=lf

  # Windows-only files: force CRLF.
  *.bat       text eol=crlf
  *.cmd       text eol=crlf
  *.ps1       text eol=crlf

  # Binaries: no diff, no merge, no EOL conversion.
  *.png       binary
  *.jpg       binary
  *.jpeg      binary
  *.gif       binary
  *.webp      binary
  *.ico       binary
  *.pdf       binary
  *.woff      binary
  *.woff2     binary
  *.zip       binary
  *.gz        binary
  *.wasm      binary

  # Linguist overrides — keep GitHub language stats and PR diffs honest.
  package-lock.json   linguist-generated=true
  pnpm-lock.yaml      linguist-generated=true
  yarn.lock           linguist-generated=true
  dist/**             linguist-generated=true
  *.min.js            linguist-generated=true
  *.min.css           linguist-generated=true
  vendor/**           linguist-vendored=true
  docs/**             linguist-documentation=true
  ```

- A repo with design assets, add Git LFS tracking (run `git lfs install` first, then commit):
  ```gitattributes
  *.psd       filter=lfs diff=lfs merge=lfs -text
  *.sketch    filter=lfs diff=lfs merge=lfs -text
  *.fig       filter=lfs diff=lfs merge=lfs -text
  *.mp4       filter=lfs diff=lfs merge=lfs -text
  ```

- An ML repo storing model weights:
  ```gitattributes
  *.pt        filter=lfs diff=lfs merge=lfs -text
  *.onnx      filter=lfs diff=lfs merge=lfs -text
  *.gguf      filter=lfs diff=lfs merge=lfs -text
  *.safetensors filter=lfs diff=lfs merge=lfs -text
  ```

- A published npm library — strip non-runtime files from the tarball:
  ```gitattributes
  /tests          export-ignore
  /docs           export-ignore
  /.github        export-ignore
  /.gitattributes export-ignore
  /.gitignore     export-ignore
  ```

- A Python repo with Jupyter notebooks (notebooks are JSON but should be marked `linguist-generated` if committed as outputs — better still, strip outputs with `nbstripout`):
  ```gitattributes
  *.ipynb     linguist-language=Python diff=jupyternotebook
  ```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Git documentation, gitattributes(5): https://git-scm.com/docs/gitattributes
- Git End-of-line conversion (`text`, `eol`, `core.autocrlf`): https://git-scm.com/docs/gitattributes#_end_of_line_conversion
- GitHub Linguist overrides (`linguist-generated`, `linguist-vendored`, `linguist-language`): https://github.com/github-linguist/linguist/blob/main/docs/overrides.md
- Git LFS tutorial (`git lfs install`, `git lfs track`): https://github.com/git-lfs/git-lfs/wiki/Tutorial
- Migrating existing binaries into LFS (`git lfs migrate import`): https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-migrate.adoc
- `export-ignore` for `git archive` / npm tarballs: https://git-scm.com/docs/gitattributes#_creating_an_archive
- Community `.gitattributes` templates (reference only — tune to your repo): https://github.com/gitattributes/gitattributes
- Why `* text=auto` alone is insufficient on Windows: https://adaptivepatchwork.com/2012/03/01/mind-the-end-of-your-line/
</system-reminder>
