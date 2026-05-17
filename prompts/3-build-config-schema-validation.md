[Readiness Fix] <REPO_NAME> Config / Schema Validation

Fix the failing signal: Config / Schema Validation ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Config / Schema Validation
**Score**: [0/1]
**Description**: YAML, JSON, and other config files are validated automatically — invalid syntax, unknown keys, or schema violations fail CI before they reach an agent or a human reviewer
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Config / schema validation – every checked-in config format the repo uses (YAML, JSON, TOML, GitHub Actions workflows, JSON Schema-bearing files) must be validated automatically. PASS requires at least one of the following, **actually wired into CI or a pre-commit hook that CI also runs**:

1. **YAML**: `yamllint` (with a checked-in `.yamllint` or `.yamllint.yaml`) OR `prettier --check '**/*.{yml,yaml}'`. A `.yamllint` file with `extends: default` but no CI invocation is a FAIL.
2. **JSON**: every file that declares `"$schema": "..."` MUST be validated against that schema — via `ajv-cli` (`ajv validate -s <schema> -d <file>`), `check-jsonschema --check-metaschema`, or `prettier --check '**/*.json'` for syntax-only. A `$schema` reference with no validation step is a FAIL.
3. **GitHub Actions**: `actionlint` (https://github.com/rhysd/actionlint) run on `.github/workflows/*.yml`. Either as a workflow step via `reviewdog/action-actionlint@v1` / the official download-script pattern / `docker://rhysd/actionlint:1.7.12`, or a pre-commit hook (`repo: https://github.com/rhysd/actionlint`). NOTE: `rhysd/actionlint@vX` does NOT work as a `uses:` ref — the maintainer explicitly declined to ship an `action.yml` (rhysd/actionlint#262, PR #479). A workflow that breaks every push because of a typo'd `uses:` ref is the failure this catches.
4. **TOML**: `taplo lint` (`taplo check` / `taplo fmt --check`) for `pyproject.toml`, `Cargo.toml`, `.taplo.toml`. Schemas auto-resolved from https://taplo.tamasfe.dev/configuration/.
5. **Multi-format**: `check-jsonschema` (Python) covers JSON, YAML, and TOML in one tool — accepts `--builtin-schema vendor.github-workflows`, `--schemafile <url>`, or `--check-metaschema`. Acceptable as the single validator for a polyglot repo.

Also verify the validator is **invoked**: grep `.github/workflows/`, `.pre-commit-config.yaml`, `Makefile`, `package.json` scripts, `noxfile.py`, `tox.ini`. An installed dev dependency that nothing calls is dead config and FAILs this signal.

A README sentence saying "please run yamllint before committing" is documentation, not validation, and FAILs this signal.

## Your Task

1. Inventory every config format the repo actually uses — run `git ls-files '*.yml' '*.yaml' '*.json' '*.toml' '.github/workflows/*'` and list distinct formats. Check existing CI workflows and `.pre-commit-config.yaml` for any validators already declared.
2. Pick the validators that match the formats present (don't add `taplo` to a repo with no TOML; don't add `actionlint` if there's no `.github/workflows/`). Make **substantive improvements**:
   - **YAML**: add `.yamllint.yaml` tuned to the repo's style (line-length, indentation matching existing files — don't dump `extends: default` and watch CI explode on every file). Wire `yamllint .` into a CI step AND a pre-commit hook.
   - **JSON**: for every file containing `"$schema"`, add an `ajv-cli` or `check-jsonschema --schemafile <url>` invocation. For schema-less JSON, run `prettier --check` or `jq empty <file>` to catch syntax errors.
   - **GitHub Actions**: add `actionlint` either as a workflow step (`uses: reviewdog/action-actionlint@v1` — there is NO `rhysd/actionlint@vX` action; the upstream repo intentionally has no `action.yml`) or via the pre-commit hook from the actionlint repo.
   - **TOML**: add `taplo check` if `pyproject.toml`, `Cargo.toml`, or `Cargo.lock` exists.
   - Prefer a single `check-jsonschema` step for polyglot repos with mixed JSON/YAML/TOML — it reduces tool sprawl.
3. Verify the fix: run each validator locally first and clean up any failures it surfaces (do not just suppress them with `ignore:` rules to make CI green — fix the underlying invalid files, or document the suppression with a comment explaining why). Then push to a branch and confirm the CI job runs and reports.
4. If you add a pre-commit hook, ALSO run pre-commit in CI (`pre-commit/action@v3.0.1` or `pre-commit run --all-files` in a workflow step). A pre-commit-only hook is bypassable with `--no-verify` and provides zero enforcement when an agent commits via API.
5. Keep changes focused on this signal — do not refactor unrelated config.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** validator installed as a dev dependency but never invoked. `npm install --save-dev ajv-cli` with no `package.json` script and no CI step is dead config — the metric stays failed and you've added supply-chain surface for nothing.
- **NO** `.yamllint` containing `extends: default` with the validator wired to `|| true` or `continue-on-error: true` to keep CI green. A non-blocking lint job is theatre.
- **NO** `$schema` references pointing to nonexistent or moved URLs (e.g. an old `schemastore.org/draft-04` path) with no validation step that would have caught the broken ref. If you add `$schema`, also add the validation invocation.
- **NO** putting validation only in `.husky/pre-commit` or `.pre-commit-config.yaml` without a corresponding CI job — pre-commit is skipped by `git commit --no-verify`, by GitHub web-UI commits, and by every agent that commits through the REST API. CI is the actual enforcement layer.
- **NO** pinning `actionlint` (or any validator) to `@main` / `@latest` / a moving tag. Pin a SHA or a real version tag (`@v1.7.7`) so the validator itself doesn't break CI on an upstream change.
- **NO** silencing real failures with broad `ignore:` blocks. If `yamllint` finds 200 line-length violations, fix them or raise the limit globally — don't ignore the whole `docs/` tree to hide the problem.
- **NO** documenting the policy in prose ("contributors should run `yamllint`") without a machine-enforced check. Prose is unenforceable; agents will skip it.

Examples of BAD fixes:
- Adding `.yamllint` with `extends: default` and nothing in CI — the file exists, no one runs it, every YAML in the repo is still un-validated.
- Wiring `actionlint` as `continue-on-error: true` so the job reports failures but never blocks merge — equivalent to no validator.
- Declaring `"$schema": "https://json.schemastore.org/dependabot-2.0.json"` on `.github/dependabot.yml` with no `ajv` / `check-jsonschema` step — the editor uses the schema for hints, CI uses nothing.
- A pre-commit hook running `prettier --check '**/*.json'` with no CI mirror — an agent commits via `gh api repos/...` and the hook never runs.
- Trying to `uses: rhysd/actionlint@<anything>` — the upstream repo intentionally has no `action.yml`, so the workflow will fail with "Unable to resolve action". Use `reviewdog/action-actionlint@v1`, the install-via-bash pattern, or `docker://rhysd/actionlint:1.7.12`. Don't pin `@main` either way — pulls untrusted code at runtime.

Examples of GOOD fixes:
- For a polyglot repo (YAML + JSON + GH Actions + TOML), one CI workflow step using `check-jsonschema`:
  ```yaml
  # .github/workflows/validate-config.yml
  name: validate-config
  on:
    pull_request:
      paths:
        - '**/*.yml'
        - '**/*.yaml'
        - '**/*.json'
        - '**/*.toml'
        - '.github/workflows/**'
  jobs:
    validate:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: '3.12'
        - run: pipx install check-jsonschema==0.29.4 yamllint==1.35.1
        - name: yamllint
          run: yamllint --strict .
        - name: validate GitHub Actions workflows
          run: check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/*.yml
        - name: validate dependabot config
          if: hashFiles('.github/dependabot.yml') != ''
          run: check-jsonschema --builtin-schema vendor.dependabot .github/dependabot.yml
        - name: validate JSON files with $schema refs
          run: |
            find . -name '*.json' -not -path './node_modules/*' -not -path './.git/*' \
              -exec grep -l '"\$schema"' {} \; \
              | xargs -r -n1 check-jsonschema --check-metaschema
        - uses: reviewdog/action-actionlint@v1
  ```
- A `.yamllint.yaml` tuned to the repo, not a copy-paste default:
  ```yaml
  extends: default
  rules:
    line-length:
      max: 160          # matches existing comments / GH Actions run blocks
      level: warning
    document-start: disable     # not all our YAMLs start with ---
    truthy:
      allowed-values: ['true', 'false', 'on', 'off']  # GH Actions uses 'on:'
  ignore: |
    .github/workflows/codeql-analysis.yml    # vendor-generated, won't fix here
  ```
- A `.pre-commit-config.yaml` block mirrored by a CI `pre-commit run --all-files` step:
  ```yaml
  repos:
    - repo: https://github.com/adrienverge/yamllint
      rev: v1.35.1
      hooks:
        - id: yamllint
          args: [--strict]
    - repo: https://github.com/rhysd/actionlint
      rev: v1.7.7
      hooks:
        - id: actionlint
    - repo: https://github.com/python-jsonschema/check-jsonschema
      rev: 0.29.4
      hooks:
        - id: check-github-workflows
        - id: check-dependabot
        - id: check-renovate
  ```
- For a TypeScript repo, an `ajv-cli` script in `package.json` invoked by CI:
  ```json
  {
    "scripts": {
      "validate:config": "ajv validate -s schemas/app-config.schema.json -d 'config/*.json' --strict=true --all-errors"
    }
  }
  ```
  with `.github/workflows/ci.yml` calling `pnpm run validate:config` on every PR.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- yamllint (rules, config, CLI): https://yamllint.readthedocs.io/en/stable/
- actionlint (GitHub Actions linter, pre-commit + GH Action): https://github.com/rhysd/actionlint
- check-jsonschema (multi-format JSON/YAML/TOML validator, built-in schemas): https://check-jsonschema.readthedocs.io/en/stable/
- ajv-cli (JSON Schema CLI for `$schema`-bearing files): https://github.com/ajv-validator/ajv-cli
- taplo (TOML linter / formatter / schema validator): https://taplo.tamasfe.dev/
- JSON SchemaStore (canonical `$schema` URLs for common config files): https://www.schemastore.org/json/
- pre-commit framework: https://pre-commit.com/
- pre-commit GitHub Action (run hooks in CI so `--no-verify` doesn't bypass): https://github.com/pre-commit/action
- prettier `--check` for JSON/YAML syntax: https://prettier.io/docs/en/cli.html#--check
</system-reminder>
