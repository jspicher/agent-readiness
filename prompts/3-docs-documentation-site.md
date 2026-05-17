[Readiness Fix] <REPO_NAME> Documentation Site or Directory

Fix the failing signal: Documentation Site or Directory ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Documentation Site or Directory
**Score**: [0/1]
**Description**: Organized docs beyond the README — a `docs/` tree or a documentation site (Docusaurus, Mintlify, VitePress, MkDocs Material, Sphinx, Nextra, Starlight) with conceptual structure: intro, guides, reference, and (if applicable) API.
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Documentation site or directory — check for organized documentation beyond the README. PASS requires at least one of:

1. **Docs site config + content**: a generator config (`docusaurus.config.{ts,js}`, `mint.json` / `docs.json`, `.vitepress/config.{ts,mjs}`, `mkdocs.yml`, `conf.py` for Sphinx, `theme.config.{tsx,jsx}` for Nextra, `astro.config.mjs` + `@astrojs/starlight`) AND a populated source tree (typically `docs/`, `content/docs/`, or `pages/`) with **at least three substantive pages** organized into conceptual sections.
2. **Plain `docs/` directory**: a `docs/` (or `documentation/`) folder at repo root containing **at least three Markdown files** organized into subdirectories or a clear index (`docs/README.md` / `docs/index.md` linking to siblings). A single `docs/architecture.md` next to the README is not enough.
3. **Wiki sync**: a checked-in `docs/` tree that mirrors a published wiki/site, with the build step in CI (`.github/workflows/docs.yml`, Vercel/Netlify integration, GitHub Pages action).

The structure must show conceptual organization for human and agent readers — at minimum an introduction/getting-started, task-oriented guides (how-to), and a reference section. If the project exposes an API, an API reference section (auto-generated from OpenAPI or code comments — see signal #11) should sit alongside but is evaluated separately.

A `README.md` alone — no matter how long — FAILs this signal. A `docs/` folder containing only one file FAILs. A docs-site config (`docusaurus.config.ts`) with an empty `docs/` directory FAILs. A docs site that builds locally but is not deployed FAILs only if no `docs/` source exists either (source presence is sufficient for this signal; deployment is signal #12 territory).

## Your Task

1. Explore the repository to understand the current state:
   - List the contents of any `docs/`, `documentation/`, `content/docs/`, `pages/`, or `website/` directories.
   - Look for generator configs: `docusaurus.config.*`, `mint.json` / `docs.json`, `.vitepress/`, `mkdocs.yml`, `conf.py`, `theme.config.*`, `astro.config.*` with `@astrojs/starlight`.
   - Read the README to identify what guides/concepts already live there that should be promoted into `docs/`.
   - Inventory the project's actual features, public APIs, deploy targets, and configuration surface so the new docs reflect reality, not boilerplate.
2. Make **substantive improvements**:
   - If `docs/` does not exist, create one at the repo root with at least the following conceptual sections (as subdirectories or numbered files): `getting-started/`, `guides/`, `reference/`, and `architecture/` (or `concepts/`). Drop a `docs/README.md` (or `docs/index.md`) that links to each section.
   - Populate each section with **real content extracted from the README, code comments, ADRs, and existing scattered Markdown** — not Lorem ipsum. Minimum three substantive pages total (one per section), each ≥ 100 lines of prose-and-code that an agent could act on.
   - If the repo would benefit from a site (public docs, multiple versions, search), add a generator config tuned to the stack: Docusaurus 3.x for React/TS monorepos, VitePress 1.x for Vue/JS, MkDocs Material 9.x or Sphinx 8.x for Python, Starlight (Astro 5.x) for minimal-JS sites, Mintlify (`docs.json`) for API-first products. Wire it up so `npm run docs` (or `mkdocs serve` / `make html`) builds locally.
   - Add an `AGENTS.md` (or extend the existing one) with a `## Documentation map` section pointing agents at the entry points — agents must not have to grep to find the architecture doc.
   - If a site is added, also add a CI job that builds the docs on every PR (`.github/workflows/docs.yml` running `npm run docs:build` or `mkdocs build --strict`) so broken links fail the build.
3. Verify the fix:
   - Run the generator's build command (e.g. `npm run docs:build`, `mkdocs build --strict`, `sphinx-build -W -b html docs docs/_build`) and confirm it exits 0 with **strict mode enabled** (warnings = errors).
   - For a plain `docs/` directory, run a link checker (`lychee docs/ --no-progress`, `markdown-link-check docs/**/*.md`) and confirm internal links resolve.
   - Open `docs/README.md` (or the built site's index) and confirm each section link lands on a populated page.
4. Keep changes focused on this signal — do not refactor unrelated code or rewrite the existing README from scratch (extract from it; do not delete it).
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** `docs/` directory containing a single `README.md` that just re-exports the root README. Three substantive pages, organized by purpose, or it FAILs.
- **NO** orphan tutorial files — every `.md` under `docs/` must be reachable from `docs/README.md`, `docs/index.md`, or the site's `sidebars.{ts,js}` / `mkdocs.yml` `nav:` / VitePress `themeConfig.sidebar`. A page no one can find is a page that does not exist.
- **NO** generator config (`docusaurus.config.ts`, `mkdocs.yml`, etc.) committed without populating the source directory it points at. An empty docs site is strictly worse than no docs site — it advertises content that does not exist.
- **NO** Lorem ipsum, "TODO: write this section", or AI-generated filler that does not reflect the actual codebase. Each page must cite real file paths, real commands, real env vars from the repo.
- **NO** copying a Docusaurus / Mintlify starter template verbatim with `intro.md`, `tutorial-basics/`, and `tutorial-extras/` untouched. Those folder names signal zero customization.
- **NO** navigation that contradicts the file structure — every entry in `sidebars.ts` / `mkdocs.yml` `nav:` must resolve to a file that exists, and every file under `docs/` (except partials prefixed with `_`) must appear in the nav.
- **NO** docs that duplicate the README without adding depth. If `docs/getting-started.md` is byte-identical to the README's Quick Start, delete one.
- **NO** committing a site config without a build script in `package.json` (or `Makefile`). `npm run docs:build` (or equivalent) must exist and exit 0.
- **NO** adding the site to `.gitignore`'s `build/` / `dist/` pattern, then forgetting to commit the source. Check `git status` after the build.
- **NO** moving the entire README into `docs/` and leaving the repo root with an empty README. The README must still answer "what is this and how do I install it" in ≤ 100 lines; depth lives in `docs/`.

Examples of BAD fixes:
- Creating `docs/architecture.md` with one sentence: "See the README for details." — that is misdirection, not documentation.
- Running `npx create-docusaurus@latest website classic` and committing the unmodified starter. The sidebar shows `Tutorial - Basics > Create a Page` — verbatim Meta template content with zero project specificity.
- Adding `mkdocs.yml` pointing at `docs/index.md`, where `docs/index.md` is one line: `# Welcome`. `mkdocs build --strict` passes; the signal does not.
- Generating 47 stub pages with an LLM, each containing 3 bullet points of generic advice ("Always write clear code"). Volume is not structure.
- Setting up Mintlify with `docs.json` listing 8 pages, but only 2 of those `.mdx` files exist on disk. Mintlify cloud will render a broken nav.

Examples of GOOD fixes:
- For a TypeScript SaaS monorepo, scaffold Docusaurus 3.x:

  ```
  docs/
    intro.md                    # what the product is, who it's for
    getting-started/
      installation.md           # actual npm install + env setup
      first-request.md          # end-to-end happy-path with curl
    guides/
      authentication.md         # OAuth flow with real redirect URIs
      webhooks.md               # signature verification with sample payload
      rate-limits.md            # actual limits from src/config/limits.ts
    reference/
      cli.md                    # every flag in packages/cli/src/commands/
      config.md                 # every key in schema.ts with defaults
      errors.md                 # error codes from src/errors.ts
    architecture/
      overview.md               # service diagram, request lifecycle
      data-model.md             # ER diagram from prisma/schema.prisma
      adrs.md                   # index of docs/adr/*.md
  docusaurus.config.ts          # tuned with project name, repo URL, edit-on-github
  sidebars.ts                   # matches the tree above 1:1
  ```

  Minimal `docusaurus.config.ts`:

  ```ts
  import type {Config} from '@docusaurus/types';
  import {themes as prismThemes} from 'prism-react-renderer';

  const config: Config = {
    title: '<PROJECT_NAME>',
    tagline: '<ONE_LINE_TAGLINE>',
    favicon: 'img/favicon.ico',
    url: 'https://<DOCS_DOMAIN>',
    baseUrl: '/',
    organizationName: '<GH_ORG>',
    projectName: '<REPO_NAME>',
    onBrokenLinks: 'throw',
    onBrokenMarkdownLinks: 'throw',
    presets: [
      ['classic', {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/<GH_ORG>/<REPO_NAME>/edit/main/',
        },
        blog: false,
      }],
    ],
    themeConfig: {
      navbar: {
        title: '<PROJECT_NAME>',
        items: [
          {type: 'docSidebar', sidebarId: 'mainSidebar', position: 'left', label: 'Docs'},
          {href: 'https://github.com/<GH_ORG>/<REPO_NAME>', label: 'GitHub', position: 'right'},
        ],
      },
      prism: {theme: prismThemes.github, darkTheme: prismThemes.dracula},
    },
  };

  export default config;
  ```

  Paired `package.json` scripts:

  ```json
  {
    "scripts": {
      "docs:start": "docusaurus start",
      "docs:build": "docusaurus build",
      "docs:serve": "docusaurus serve"
    }
  }
  ```

  Paired CI (`.github/workflows/docs.yml`):

  ```yaml
  name: docs
  on:
    pull_request:
      paths: ['docs/**', 'docusaurus.config.ts', 'sidebars.ts', 'package.json']
    push:
      branches: [main]
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with: {node-version: '20', cache: 'npm'}
        - run: npm ci
        - run: npm run docs:build
  ```

- For a Python library, scaffold MkDocs Material:

  ```yaml
  # mkdocs.yml
  site_name: <PROJECT_NAME>
  repo_url: https://github.com/<GH_ORG>/<REPO_NAME>
  edit_uri: edit/main/docs/
  theme:
    name: material
    features: [navigation.sections, navigation.expand, content.code.copy, search.suggest]
  plugins:
    - search
    - mkdocstrings:
        handlers:
          python:
            options: {show_source: true, docstring_style: google}
  nav:
    - Home: index.md
    - Getting Started:
        - Installation: getting-started/installation.md
        - Quickstart: getting-started/quickstart.md
    - Guides:
        - Configuration: guides/configuration.md
        - Deployment: guides/deployment.md
    - Reference:
        - CLI: reference/cli.md
        - API: reference/api.md
    - Architecture: architecture/overview.md
  strict: true
  ```

  Build verification: `mkdocs build --strict` (warnings → errors).

- For an API-first product, a minimal Mintlify `docs.json`:

  ```json
  {
    "$schema": "https://mintlify.com/docs.json",
    "theme": "mint",
    "name": "<PROJECT_NAME>",
    "navigation": {
      "tabs": [
        {
          "tab": "Guides",
          "groups": [
            {"group": "Get Started", "pages": ["introduction", "quickstart"]},
            {"group": "Guides", "pages": ["guides/authentication", "guides/webhooks"]}
          ]
        },
        {
          "tab": "API Reference",
          "openapi": "openapi.yaml"
        }
      ]
    }
  }
  ```

  Every page listed in `pages` MUST exist as `.mdx` on disk; Mintlify CI will 404 otherwise.

- Add an `AGENTS.md` snippet so agents skip the search step:

  ```
  ## Documentation map
  - Quick start, install, env vars: README.md
  - Architecture, data model, ADR index: docs/architecture/
  - How-to guides (auth, webhooks, deploys): docs/guides/
  - CLI flags, config keys, error codes: docs/reference/
  - Auto-generated API reference: built from openapi.yaml → docs/reference/api.md
  - Docs build: `npm run docs:build` (strict mode, fails on broken links)
  ```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- Docusaurus 3.x docs (configuration, sidebars, versioning): https://docusaurus.io/docs
- Mintlify docs (`docs.json` schema, deploy): https://mintlify.com/docs
- VitePress 1.x (`.vitepress/config.ts`, sidebar): https://vitepress.dev/reference/site-config
- MkDocs Material 9.x (nav, mkdocstrings): https://squidfunk.github.io/mkdocs-material/
- Sphinx 8.x (`conf.py`, autodoc, MyST): https://www.sphinx-doc.org/
- Astro Starlight (minimal-JS docs sites): https://starlight.astro.build/
- Nextra 3.x (Next.js-native docs theme): https://nextra.site/
- Write the Docs — Docs as Code: https://www.writethedocs.org/guide/docs-as-code/
- Diátaxis framework (tutorials / how-to / reference / explanation): https://diataxis.fr/
- AGENTS.md spec (machine-readable agent guide): https://agents.md/
- markdown-link-check (CI link verification): https://github.com/tcort/markdown-link-check
- lychee (fast link checker, Rust): https://github.com/lycheeverse/lychee
</system-reminder>
