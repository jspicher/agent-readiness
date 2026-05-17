[Readiness Fix] <REPO_NAME> Cloud Dev Environment

Fix the failing signal: Cloud Dev Environment ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Cloud Dev Environment
**Score**: [0/1]
**Description**: Cloud-based workspace configuration so a contributor (human or agent) can spin up a fully-provisioned dev environment in a browser tab without touching their laptop
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Cloud dev environment configured — a checked-in manifest that a hosted workspace provider can read to build, provision, and start the project on demand. PASS requires at least one of the following, fully wired (not just a stub file):

1. **GitHub Codespaces**: `.devcontainer/devcontainer.json` (or `.devcontainer/<name>/devcontainer.json` for multi-config repos) that (a) pins a real `image` or `build.dockerfile`, (b) declares the runtime via `features` (e.g. `ghcr.io/devcontainers/features/node:1`, `.../python:1`, `.../docker-in-docker:2`), (c) installs deps via `postCreateCommand` or `onCreateCommand` (e.g. `pnpm install --frozen-lockfile`), and (d) exposes the dev server with `forwardPorts` + `portsAttributes`. Plus a `.github/workflows/codespaces-prebuilds.yml` (or repo Settings → Codespaces → Prebuilds) so cold starts are seconds, not minutes. A bare `{"image": "mcr.microsoft.com/devcontainers/base:ubuntu"}` with no features, no postCreate, and no prebuild is a FAIL.
2. **Gitpod**: `.gitpod.yml` at repo root with (a) a real `image` (either a public tag or `image.file: .gitpod.Dockerfile`), (b) a `tasks` block whose `init` runs the dependency install + build and `command` starts the dev server, (c) a `ports` block with `onOpen: open-preview` or `notify` for the actual app port, and (d) `vscode.extensions` listing the language tooling the project needs. Prebuilds enabled via `github.prebuilds` (or repo connected in Gitpod dashboard). A one-line `image: gitpod/workspace-full` with no tasks is a FAIL.
3. **Coder / Coder OSS**: a Terraform template in `.coder/` (or a repo-referenced template in the Coder deployment) that pins the workspace image, declares `coder_agent` startup scripts that install deps and start services, and uses `coder_app` to surface the dev server URL. The repo must contain enough config that a Coder admin can `coder templates push` from it.
4. **DevPod / Daytona / Replit**: checked-in provider config — `devpod.yaml`, `.daytona/workspace.yaml`, or `.replit` + `replit.nix` — that pulls in deps, runs install, and starts the app. For Replit, `.replit` MUST declare `run` and `entrypoint`, and `replit.nix` MUST pin the language toolchain (not rely on Replit's autodetect).

Also verify the manifest actually boots: for Codespaces, launch a Codespace from the branch and confirm `postCreateCommand` succeeds and the forwarded port serves the app. For Gitpod, open the repo via `https://gitpod.io/#https://github.com/<org>/<repo>` and confirm `tasks.init` exits 0. A devcontainer.json that has never been built in the cloud (only in local VS Code) and a `.gitpod.yml` with a typo in the task command both FAIL — the signal is "a new contributor can click a button and code", not "a file exists at the right path".

A README link to "click here to open in Codespaces" with no `.devcontainer/` behind it is documentation, not configuration, and FAILs.

## Your Task

1. Explore the repository to identify (a) which cloud workspace provider, if any, is referenced anywhere (README badges, CONTRIBUTING.md, `.devcontainer/`, `.gitpod.yml`, `.coder/`, `.replit`), (b) the actual runtime + package manager + dev-server command the repo uses today, and (c) every port the app and its sidecars bind to (web, API, DB, queue, mailcatcher).
2. Make **substantive improvements** by adding a real, project-tuned cloud manifest:
   - Pick the provider that matches the repo's existing tooling (Codespaces if the repo is on github.com and already has any `.devcontainer/`; Gitpod if the team already has a workspace; Coder if there's a self-hosted deployment). Do not add three configs to "cover all bases" — one that works beats three that drift.
   - For Codespaces: write `.devcontainer/devcontainer.json` with a pinned image or Dockerfile, `features` for the language runtime + docker-in-docker if the app needs containers, `postCreateCommand` that runs the real install command (`pnpm install --frozen-lockfile`, `uv sync`, `bundle install`), `forwardPorts` for every app port, `portsAttributes` to set `onAutoForward: notify` and a human label, and `customizations.vscode.extensions` listing the editor tools the team actually uses. Add a `.github/workflows/codespaces-prebuilds.yml` that triggers prebuilds on `push` to the default branch and any branch matching `release/*`.
   - For Gitpod: write `.gitpod.yml` with `image`, a `tasks` block whose `init` does dep install + any one-time codegen and `command` starts the dev server, `ports` for each app port with `onOpen` and `visibility`, `vscode.extensions`, and `github.prebuilds` enabled for the default branch + PRs.
   - Add a one-paragraph "Open in the cloud" section to `README.md` with the Codespaces "Open in GitHub Codespaces" button (`https://github.com/codespaces/new?repo=<repo-id>&ref=<branch>`) or the Gitpod button (`https://gitpod.io/button/open-in-gitpod.svg`), pointing to the branch the manifest lives on so the first click works.
3. Verify the manifest actually boots end-to-end:
   - For Codespaces, run `devcontainer up --workspace-folder .` locally with the `@devcontainers/cli` package (`npm i -g @devcontainers/cli`) — this builds the same image Codespaces will build. Then push the branch and create a Codespace from it via `gh codespace create -R <repo> -b <branch>`; confirm `postCreateCommand` exits 0 and the forwarded port responds with 200.
   - For Gitpod, push the branch and open `https://gitpod.io/#https://github.com/<org>/<repo>/tree/<branch>`; confirm the workspace reaches "running" and the dev server URL loads.
   - Capture the build duration. If cold start is over 3 minutes, enable prebuilds before merging — agents will not wait 5 minutes for `npm install`.
4. Keep changes focused on this signal — do not refactor the build itself, do not add new CI jobs unrelated to the dev environment, do not migrate package managers.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** copying the Microsoft `mcr.microsoft.com/devcontainers/universal` image with no features and no `postCreateCommand`. Universal images boot in 90+ seconds and still need every dep installed at first use — that is a stub, not a dev environment.
- **NO** `.devcontainer/devcontainer.json` that was authored in local VS Code and never opened in Codespaces. Local devcontainer behavior diverges from Codespaces in three predictable ways: secret mounting (`localEnv` does not work in Codespaces — use `secrets`), port forwarding (Codespaces auto-forwards but requires `portsAttributes` for HTTPS upgrade), and `postStartCommand` timing (Codespaces runs it on every resume, local runs it once). Build it in the cloud or it does not count.
- **NO** missing `forwardPorts`. Without it, the contributor opens a Codespace, runs `pnpm dev`, sees "listening on :3000", clicks the Ports tab, sees nothing, and gives up. Forward every port the app + its sidecars bind to.
- **NO** `postCreateCommand: "echo done"` or a `postCreateCommand` that silently swallows failure (`pnpm install || true`). If install fails, the workspace MUST fail loudly so the contributor knows before they waste 20 minutes debugging "why is `next` not found".
- **NO** prebuilds left disabled. A 4-minute cold start on every PR review session is a dev-environment tax that pushes contributors back to laptops. Enable prebuilds on the default branch at minimum; add `release/*` and `main` if the repo has long-lived feature branches.
- **NO** committing a `.devcontainer/devcontainer.json` that references a private base image the org's Codespaces accounts cannot pull. Test with a fresh user account or confirm the registry is in the Codespaces image-pull allowlist.
- **NO** `.gitpod.yml` with `tasks: - command: npm start` and no `init`. Gitpod will run `npm start` before `node_modules` exists and the workspace will land on a red error screen. `init` runs once at workspace creation; `command` runs on every workspace start — split them.
- **NO** a `.replit` file that hardcodes a Replit-specific path (`/home/runner/...`) or relies on Replit's autodetect for the toolchain. Pin everything in `replit.nix`.
- **NO** adding three provider configs (Codespaces + Gitpod + Coder) "to give people options". Each one rots independently; pick the one the team uses and own it.
- **NO** README badge linking to a Codespaces URL that points at `main` when the manifest lives on a feature branch — the first click 404s the contributor.

Examples of BAD fixes:
- `.devcontainer/devcontainer.json` containing `{"image": "mcr.microsoft.com/devcontainers/base:ubuntu"}` and nothing else. The contributor lands in a bare Ubuntu shell with no Node, no Python, no project deps — they could have gotten this from `docker run` in 10 seconds.
- A `.gitpod.yml` with `image: gitpod/workspace-full` and `tasks: [{command: "code ."}]`. Workspace-full is 3GB+ and `code .` does nothing useful as the workspace command.
- A `.devcontainer/devcontainer.json` whose `postCreateCommand: "npm install"` runs in a repo that uses pnpm — install completes but generates a competing `package-lock.json` that conflicts with the committed `pnpm-lock.yaml`. Match the package manager the repo actually uses.
- Adding `"forwardPorts": [3000]` for a Next.js app that also runs Postgres on 5432, Redis on 6379, and Mailhog on 8025 — three of the four sidecars are invisible to the contributor.
- A `codespaces-prebuilds.yml` that builds prebuilds only on a tag push pattern the repo never uses, so prebuilds never actually run.

Examples of GOOD fixes:

For a Next.js + Postgres repo using Codespaces, `.devcontainer/devcontainer.json`:
```json
{
  "$schema": "https://raw.githubusercontent.com/devcontainers/spec/main/schemas/devContainer.schema.json",
  "name": "<REPO_NAME>",
  "image": "mcr.microsoft.com/devcontainers/typescript-node:1-22-bookworm",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers-extra/features/pnpm:2": {}
  },
  "forwardPorts": [3000, 5432, 6379, 8025],
  "portsAttributes": {
    "3000": { "label": "Next.js dev", "onAutoForward": "notify" },
    "5432": { "label": "Postgres",    "onAutoForward": "silent" },
    "6379": { "label": "Redis",       "onAutoForward": "silent" },
    "8025": { "label": "Mailhog UI",  "onAutoForward": "openBrowser" }
  },
  "onCreateCommand": "docker compose -f .devcontainer/docker-compose.deps.yml up -d",
  "postCreateCommand": "pnpm install --frozen-lockfile && pnpm db:migrate && pnpm db:seed",
  "postStartCommand": "docker compose -f .devcontainer/docker-compose.deps.yml start",
  "remoteUser": "node",
  "hostRequirements": { "cpus": 4, "memory": "8gb", "storage": "32gb" },
  "secrets": {
    "GITHUB_TOKEN":      { "description": "Used by gh and Octokit calls in dev" },
    "OPENAI_API_KEY":    { "description": "Required for /api/chat", "documentationUrl": "https://platform.openai.com/api-keys" }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "bradlc.vscode-tailwindcss",
        "Prisma.prisma",
        "GitHub.vscode-github-actions",
        "anthropic.claude-code"
      ],
      "settings": {
        "editor.formatOnSave": true,
        "typescript.tsdk": "node_modules/typescript/lib"
      }
    },
    "codespaces": {
      "openFiles": ["README.md", "CONTRIBUTING.md"]
    }
  }
}
```

Paired `.github/workflows/codespaces-prebuilds.yml`:
```yaml
# NOTE: GitHub Codespaces prebuilds are NOT configured via a user-authored workflow.
# There is no `github/codespaces-precaching-action`; prebuilds are managed in the
# repository's Settings → Codespaces → Prebuild configurations UI, or via the REST API
# (POST /repos/{owner}/{repo}/codespaces/prebuild-configurations).
# Configure the prebuild there, select the regions and machine SKU, and GitHub will
# trigger rebuilds on `push` to the configured branches automatically.
# Docs: https://docs.github.com/en/codespaces/prebuilding-your-codespaces/configuring-prebuilds
```

If you need a CI-side hook (e.g., to validate the devcontainer builds before publishing a prebuild config), use the `devcontainers/ci` action against your committed `devcontainer.json`:

```yaml
name: Devcontainer validate
on:
  pull_request:
    paths: ['.devcontainer/**']
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: devcontainers/ci@v0.3
        with:
          push: never
          runCmd: echo "devcontainer built successfully"
```

Equivalent Gitpod alternative, `.gitpod.yml`:
```yaml
image:
  file: .gitpod.Dockerfile
tasks:
  - name: setup
    init: |
      pnpm install --frozen-lockfile
      pnpm db:migrate
      pnpm db:seed
    command: pnpm dev
  - name: deps
    command: docker compose -f .devcontainer/docker-compose.deps.yml up
ports:
  - port: 3000
    onOpen: open-preview
    visibility: public
  - port: 5432
    onOpen: ignore
    visibility: private
  - port: 6379
    onOpen: ignore
    visibility: private
  - port: 8025
    onOpen: notify
    visibility: private
vscode:
  extensions:
    - dbaeumer.vscode-eslint
    - esbenp.prettier-vscode
    - bradlc.vscode-tailwindcss
    - Prisma.prisma
github:
  prebuilds:
    master: true
    branches: true
    pullRequests: true
    pullRequestsFromForks: false
    addCheck: true
    addComment: false
    addBadge: true
```

For a Python / uv repo using Codespaces, swap the base image to `mcr.microsoft.com/devcontainers/python:1-3.12-bookworm`, install `uv` via `postCreateCommand` (e.g., `pip install uv && uv sync --frozen && uv run pre-commit install`) — note: `ghcr.io/astral-sh/uv:1` is a Docker image for running uv standalone, NOT a devcontainer feature; for a feature use the community `ghcr.io/devcontainers-extra/features/uv:1` or install uv directly in `postCreateCommand`.

A README block worth adding:
```markdown
## Open in the cloud

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/<org>/<repo>?quickstart=1)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/<org>/<repo>)

Both buttons land you in a fully-provisioned workspace in under 60 seconds (prebuilds enabled on `main`). Set `OPENAI_API_KEY` and `DATABASE_URL` in your account secrets before the first launch — the workspace will prompt you on cold start otherwise.
```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, which provider you wired up, the measured cold-start time before vs after prebuilds, and any project-specific gotchas the next contributor needs to know

## References

- GitHub Codespaces — devcontainer.json reference: https://containers.dev/implementors/json_reference/
- GitHub Codespaces — introduction & setup: https://docs.github.com/en/codespaces/overview
- GitHub Codespaces — prebuilding your codespaces: https://docs.github.com/en/codespaces/prebuilding-your-codespaces/about-github-codespaces-prebuilds
- GitHub Codespaces — managing encrypted secrets: https://docs.github.com/en/codespaces/managing-codespaces-for-your-organization/managing-development-environment-secrets-for-your-repository-or-organization
- Dev Containers — features index: https://containers.dev/features
- Dev Containers CLI (test the build locally before pushing): https://github.com/devcontainers/cli
- Gitpod — `.gitpod.yml` reference: https://www.gitpod.io/docs/references/gitpod-yml
- Gitpod — prebuilds: https://www.gitpod.io/docs/configure/projects/prebuilds
- Coder — template Terraform reference: https://coder.com/docs/templates
- DevPod — provider configuration: https://devpod.sh/docs/developing-in-workspaces/configure-devcontainer-json
- Daytona — workspace configuration: https://www.daytona.io/docs/configuration/
- Replit — `.replit` and `replit.nix`: https://docs.replit.com/replit-workspace/configuring-repl
</system-reminder>
