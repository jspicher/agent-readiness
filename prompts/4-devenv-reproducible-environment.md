[Readiness Fix] <REPO_NAME> Reproducible Environment

Fix the failing signal: Reproducible Environment ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Reproducible Environment
**Score**: [0/1]
**Description**: Declarative, hermetic dev environment that pins every toolchain dependency so an agent (and every human) gets a byte-identical shell on first clone
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Reproducible, hermetic dev environment — check for a checked-in declarative manifest that fully resolves the toolchain (compiler, interpreter, system libs, CLIs) with a companion lockfile. PASS requires one of the following, with both the manifest AND its lockfile committed:

1. **Nix flakes**: `flake.nix` defining `devShells.default` (or per-system shells) via `pkgs.mkShell { buildInputs = [ ... ]; }`, paired with a committed `flake.lock`. The flake MUST pin `nixpkgs` to a specific channel branch (e.g. `github:NixOS/nixpkgs/nixos-24.11`) or a specific revision — never `nixpkgs/master` or `nixpkgs-unstable` without a rev. A flake without `flake.lock` is a FAIL (resolution is non-deterministic on every `nix develop`).
2. **Legacy `shell.nix`**: acceptable when paired with `niv` (`nix/sources.json`) or `npins` pinning nixpkgs to a specific revision. A bare `shell.nix` with `import <nixpkgs> {}` (channel-relative) is a FAIL — it resolves to whatever the user's `nix-channel --list` happens to point at.
3. **Devbox** (Jetify, Nix-backed): `devbox.json` with `packages` enumerated at specific versions (e.g. `"nodejs@20.11.1"`, not `"nodejs@latest"`), AND a committed `devbox.lock` produced by `devbox install`. Missing lockfile = FAIL.
4. **Pixi** (Conda-Forge, Rust-backed): `pixi.toml` (or `pyproject.toml` with `[tool.pixi]`) with `[dependencies]` and `[feature.*.dependencies]` resolved, AND a committed `pixi.lock`. Useful for Python/scientific stacks; satisfies the signal when both files are present.

**Note on lighter tools**: `mise` (`.mise.toml` or `.tool-versions`) and `asdf` (`.tool-versions`) pin language runtimes but do NOT pin system libraries (openssl, libpq, ffmpeg, GDAL). They satisfy the toolchain pinning signal (#99) but not this hermetic-environment signal — they sit atop the host's package manager and break across macOS/Linux/WSL. Cite them as evidence ONLY when the repo is pure-language (e.g. a Python lib with no native deps) AND the README explicitly states host-OS prerequisites with versions.

Also verify the environment actually activates: a `direnv` hook (`.envrc` containing `use flake`, `use devbox`, or `use nix`) is strongly preferred so the shell auto-loads on `cd`. Without direnv, the agent has to remember to run `nix develop` / `devbox shell` / `pixi shell` for every command — which it won't.

A README sentence saying "install Node 20 and Python 3.12" is documentation, not a reproducible environment, and FAILs this signal.

## Your Task

1. Explore the repository to understand the current state — list every `flake.nix`, `flake.lock`, `shell.nix`, `default.nix`, `devbox.json`, `devbox.lock`, `pixi.toml`, `pixi.lock`, `.envrc`, `.tool-versions`, `.mise.toml`, `Dockerfile`, and `.devcontainer/devcontainer.json`. Note which language runtimes, system libs, and CLIs the repo actually depends on (read `package.json` engines, `pyproject.toml`, `Cargo.toml`, install steps in CI, install steps in the README).
2. Pick the right tool for the stack and commit BOTH the manifest and the lockfile:
   - **Nix flake** for repos with native deps (Python + C extensions, Node + sharp/canvas, Rust workspaces, Go with cgo). Pin `nixpkgs` to a stable channel rev.
   - **Devbox** for teams that want Nix benefits without writing Nix syntax. Run `devbox init`, add packages with `devbox add nodejs@20.11.1 python@3.12.7 ...`, commit `devbox.json` AND `devbox.lock`.
   - **Pixi** for Python/data-science stacks where Conda-Forge is the canonical source (PyTorch + CUDA, GDAL, scientific libs). Commit `pixi.toml` AND `pixi.lock`.
3. Add a `.envrc` with the matching direnv hook (`use flake`, `use devbox`, or `use pixi`) so the environment auto-loads. Add `.envrc` to `.gitignore` ONLY for the local-allow file (`.envrc.local`); the project `.envrc` is committed.
4. Verify activation works on a clean clone: in a fresh shell, `nix develop --command node --version` (or `devbox run -- node --version`, `pixi run node --version`) MUST print the pinned version without prompting for missing tools.
5. Keep changes focused on this signal — do not refactor unrelated config.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** committing `flake.nix` without `flake.lock`. The lockfile IS the reproducibility — without it, `nix develop` resolves against whatever `nixpkgs` revision the user's flake registry currently points at.
- **NO** pinning to `nixpkgs-unstable`, `nixpkgs/master`, or any unpinned channel. Use a release branch (`nixos-24.11`, `nixos-25.05`) or a specific commit SHA (`github:NixOS/nixpkgs/abc123...`).
- **NO** `devbox.json` with `"nodejs@latest"`, `"python@3"`, or any floating version. Pin to the full version (`nodejs@20.11.1`). Missing `devbox.lock` is a hard FAIL — `devbox install` MUST be run and the resulting lockfile committed.
- **NO** `pixi.toml` without `pixi.lock`. The lockfile is generated by `pixi install` and contains the resolved package hashes.
- **NO** claiming `.tool-versions` or `.mise.toml` alone satisfies this signal — those are for #99 (Toolchain Versions Pinned). They do not pin system libs and are not hermetic. If the repo has only `.tool-versions`, you must ADD a hermetic layer (Nix/Devbox/Pixi) on top, not just point at the existing file.
- **NO** writing a Dockerfile and calling it done — that's a different signal (#97 Dev Container). A Dockerfile satisfies #97 but does not give the agent a fast local shell with `direnv` activation.
- **NO** `shell.nix` containing `import <nixpkgs> {}`. The angle-bracket import resolves against the user's NIX_PATH and is non-reproducible by definition. Use `niv`, `npins`, or migrate to flakes.
- **NO** package lists copied from a tutorial that don't match what the repo actually uses. A Node monorepo with `python311` in its flake but no Python code signals zero project knowledge.
- **NO** committing the `.envrc` without also adding `.direnv/` to `.gitignore` — direnv writes a cache directory that must not be tracked.

Examples of BAD fixes:
- Committing `flake.nix` with `inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable"` and no `flake.lock`. `nix develop` resolves to a different revision on every developer's machine.
- A `devbox.json` containing `{"packages": ["nodejs", "python"]}` — no version pins, no lockfile. `devbox shell` installs the current latest from Nixpkgs unstable.
- Adding `.mise.toml` to a repo that depends on `libpq`, `openssl`, and `ffmpeg` and claiming the environment is reproducible. The agent will hit "ffmpeg: command not found" on first run.
- A `flake.nix` with 47 packages copy-pasted from a generic template, including `rustup`, `gcc14`, `postgresql_16`, and `chromium`, on a repo that is a pure TypeScript library.
- Writing `shell.nix` that uses `with import <nixpkgs> {};` — works on the author's machine, breaks for everyone else.

Examples of GOOD fixes:

- For a Node + native deps repo, `flake.nix`:
  ```nix
  {
    description = "<REPO_NAME> dev environment";
    inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    inputs.flake-utils.url = "github:numtide/flake-utils";
    outputs = { self, nixpkgs, flake-utils }:
      flake-utils.lib.eachDefaultSystem (system:
        let pkgs = import nixpkgs { inherit system; };
        in {
          devShells.default = pkgs.mkShell {
            buildInputs = [
              pkgs.nodejs_20
              pkgs.pnpm
              pkgs.python311          # node-gyp
              pkgs.pkg-config
              pkgs.vips               # sharp
              pkgs.postgresql_16      # libpq for pg native bindings
            ];
            shellHook = ''
              export NODE_OPTIONS="--max-old-space-size=4096"
            '';
          };
        });
  }
  ```
  Paired with a committed `flake.lock` (generated by `nix flake update`) and `.envrc`:
  ```sh
  use flake
  dotenv_if_exists .env.local
  ```
  And `.gitignore`:
  ```
  .direnv/
  .envrc.local
  ```

- For a Python data repo, `pixi.toml`:
  ```toml
  [project]
  name = "<REPO_NAME>"
  channels = ["conda-forge", "pytorch"]
  platforms = ["linux-64", "osx-arm64"]

  [dependencies]
  python = "3.12.*"
  pytorch = "2.4.*"
  gdal = "3.9.*"
  ffmpeg = "7.0.*"
  ruff = "0.6.*"
  pytest = "8.*"
  ```
  Committed alongside `pixi.lock` (generated by `pixi install`) and `.envrc` containing `watch_file pixi.lock` + `eval "$(pixi shell-hook)"`.

- For a polyglot repo using Devbox, `devbox.json`:
  ```json
  {
    "packages": [
      "nodejs@20.11.1",
      "pnpm@9.12.3",
      "python@3.12.7",
      "uv@0.4.27",
      "postgresql@16.4",
      "redis@7.4.1"
    ],
    "shell": {
      "init_hook": ["echo \"<REPO_NAME> devbox shell ready\""]
    }
  }
  ```
  With `devbox.lock` committed (generated by `devbox install`) and `.envrc` containing `use devbox`.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Nix flakes reference (`flake.nix` schema, `flake.lock` format): https://nixos.wiki/wiki/Flakes
- Determinate Systems flake guide (devShells, direnv integration): https://zero-to-nix.com/concepts/dev-env
- `nixpkgs` channels & release branches: https://nixos.org/manual/nixpkgs/stable/#chap-overview
- niv / npins (pin nixpkgs without flakes): https://github.com/nmattia/niv and https://github.com/andir/npins
- Devbox docs (Jetify, Nix-backed reproducible shells): https://www.jetify.com/devbox/docs
- Devbox lockfile reference: https://www.jetify.com/devbox/docs/configuration/devbox_lock
- Pixi docs (Conda-Forge reproducible environments): https://pixi.sh/latest/
- Pixi lockfile spec: https://pixi.sh/latest/features/lockfile/
- direnv `use flake` / `use devbox` / `use nix` stdlib: https://direnv.net/man/direnv-stdlib.1.html
- mise vs Nix tradeoffs (why `.tool-versions` is not hermetic): https://mise.jdx.dev/about.html#comparison-to-asdf
- COMPEL agent baseline, Control 7 (hermetic build environments for agents): https://www.compelframework.org/articles/model-context-protocol-security-standards
</system-reminder>
