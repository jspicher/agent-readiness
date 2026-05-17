[Readiness Fix] <REPO_NAME> AI Usage Policy

Fix the failing signal: AI Usage Policy ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: AI Usage Policy
**Score**: [0/1]
**Description**: Documented guidelines for AI/agent contributions
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

AI usage policy — check for a checked-in, discoverable document that tells human contributors AND agents what kinds of AI assistance are permitted, what must be disclosed, and what is banned outright. PASS requires a policy that covers ALL of the following topics, not just "AI is allowed" or "AI is banned":

1. **Disclosure requirement** — when must AI involvement be flagged? Per-commit trailer (`Assisted-by:` / `Generated-by:` / `Co-authored-by:`), PR-description checkbox, or commit-message section. A policy that says "disclose if you want" is unenforceable and FAILs. The threshold must be concrete: e.g. "disclose any contribution where AI generated more than a single-line completion" or "disclose any contribution where AI authored a function body, test case, or doc section".
2. **Allowed tools / agents** — which assistants are sanctioned (Copilot, Cursor, Claude Code, Factory droid, Codeium, etc.) and which are off-limits. A blanket "any AI tool" with no scoping is a stub. An enterprise repo on a paid tier MUST name the procured tool; a hobby repo MAY allow any tool but MUST still require disclosure.
3. **IP / licensing constraints** — what the contributor warrants about the training data and output license. At minimum the policy must require the contributor to confirm (a) they have the right to submit the contribution under the project's license, (b) the AI tool is not configured to ingest copyleft training data that would taint the output, and (c) the contribution does not include verbatim memorized code from a license-incompatible source. For DCO repos, this maps to "only humans may sign off — the AI cannot certify the DCO".
4. **Attribution mechanism** — the exact format the contributor uses. `Assisted-by: claude-sonnet-4.5 [Claude Code]` in the commit trailer, `Co-authored-by:` in the commit message, an `AI-Assisted:` checkbox in the PR template, or a `## AI assistance` section in the PR description. Pick one and document the format with a concrete example.
5. **Banned use cases** — what AI must NOT be used for. At minimum: (a) generating issue/PR text designed to look like a human-authored bug report (slop PRs), (b) reviewing or approving other contributors' PRs as the sole reviewer, (c) bypassing security review on dependency bumps or auth code, (d) generating commit messages for code the contributor has not read end-to-end. Optionally: doc translations without a human translator review, generated test data for security-sensitive flows.
6. **Discoverability** — the policy lives at a path humans AND agents will find: `CONTRIBUTING.md` (preferred — human contributors read it; agents are instructed to read it), `AGENTS.md` (agents read it on session start), `.github/CONTRIBUTING.md`, or a top-level `AI-POLICY.md` linked from `README.md` AND from `AGENTS.md`/`CLAUDE.md`. A policy buried in a private wiki, a Notion page, or a Slack pin FAILs — agents cannot read it and external contributors will not find it.

Also verify the policy is internally consistent:
- If `CONTRIBUTING.md` allows AI-assisted PRs but `AGENTS.md` tells the agent "do not run autonomously without approval", which wins? The policy must reconcile or one of the documents is dead.
- If the repo uses DCO/CLA, the policy must clarify that the human contributor — not the AI tool — signs off and bears legal accountability.
- If the policy names a tool the team does not actually have licenses for, or omits a tool the team uses daily, the policy is aspirational rather than operative and will be ignored within a month.

A `README.md` sentence saying "we use AI sometimes" or "no AI please" is a stance, not a policy, and FAILs this signal.

## Your Task

1. Explore the repository to understand the current state related to this signal:
   - Search for existing AI policy artifacts: `AI-POLICY.md`, `AI_POLICY.md`, `CONTRIBUTING.md` (look for a `## AI` / `## Generative AI` / `## AI-assisted` section), `AGENTS.md`, `CLAUDE.md`, `.github/PULL_REQUEST_TEMPLATE.md` (look for an AI-disclosure checkbox), `CODE_OF_CONDUCT.md`.
   - Check `git log` for existing `Assisted-by:` / `Co-authored-by: *bot*` / `Generated-by:` trailers — if the team is already attributing AI work informally, codify that format.
   - Identify which AI tools the team actually uses: look in `.claude/`, `.factory/`, `.cursor/`, `.continue/`, `.github/copilot-*`, `.aider*`, `.opencode/`, lockfiles for `@anthropic-ai/*`, `openai`, IDE config in `.vscode/extensions.json`.
   - Check the project's license — a GPL/AGPL project has stricter IP concerns than MIT/Apache. The policy must respect the license.
   - Note whether the repo uses DCO (`signed-off-by` in commit history) or a CLA — the IP section of the policy must align.
2. Make **substantive improvements** by writing a real, project-tuned AI policy:
   - Add a `## AI-assisted contributions` section to `CONTRIBUTING.md` covering all six required topics. If `CONTRIBUTING.md` does not exist, create it. Do NOT put the policy in a standalone `AI-POLICY.md` unless `CONTRIBUTING.md` already exists and is structured to link out — agents are far more likely to read `CONTRIBUTING.md` than to find a sibling file.
   - Cross-reference from `AGENTS.md` / `CLAUDE.md` so agents discover the policy at session start: a `## AI policy` section with a one-line summary and a link to `CONTRIBUTING.md#ai-assisted-contributions`.
   - Extend `.github/PULL_REQUEST_TEMPLATE.md` with a `## AI assistance` section (checkbox + free-text field for tool name and scope) so the disclosure is captured at the merge gate, not just in commit trailers people forget.
   - If the repo uses DCO, add the `Assisted-by:` trailer format to the contributor docs alongside the existing `Signed-off-by:` instructions.
3. Verify the policy is discoverable and enforceable:
   - From a fresh clone, run `grep -r "AI-assisted" CONTRIBUTING.md AGENTS.md CLAUDE.md .github/` and confirm every reference resolves.
   - Open the PR template in a draft PR and confirm the AI-disclosure section renders.
   - If you added a commit trailer convention, write one commit with the trailer and confirm `git log --format='%(trailers)'` shows it.
4. Keep changes focused on this signal — do not refactor the rest of `CONTRIBUTING.md` or rewrite the code of conduct.
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** blanket ban ("no AI contributions accepted") without an enforcement mechanism — bans without detection drive AI use underground and the maintainer reviews undisclosed AI slop anyway. If the project genuinely bans AI, the policy MUST pair the ban with a detection signal (commit-trailer check in CI, required PR-template attestation, reviewer guidance for spotting LLM-style prose) and an explicit rejection workflow. A bare "no AI" sentence is unenforceable and trains contributors to lie.
- **NO** blanket allow ("AI is fine, do whatever") with no disclosure requirement — this is the opposite failure. Reviewers cannot calibrate scrutiny if they do not know which PRs were AI-authored, and the project cannot defend itself against a future copyleft-training-data lawsuit if it never tracked AI provenance.
- **NO** policy that ignores agentic workflows — a 2023-era policy that talks only about "AI code completion" (Copilot autocomplete) and says nothing about autonomous agents opening PRs, running tools, or generating multi-file changes is obsolete. The 2026 reality is Claude Code / Factory droid / Cursor agents opening 50-line PRs end-to-end; the policy must name them.
- **NO** policy that contradicts `CONTRIBUTING.md` or `AGENTS.md`. If `CONTRIBUTING.md` requires `Signed-off-by:` and `AGENTS.md` tells the agent to author commits, the policy must clarify that the human (not the agent) adds the sign-off. Internal contradictions get the policy ignored.
- **NO** policy in a private wiki, Notion page, Slack pin, or `docs/internal/`. External contributors and agents must be able to read it from a clone. If the policy is internal, the public `CONTRIBUTING.md` must at least state the disclosure requirement and link to the internal doc for employees.
- **NO** policy that names a tool the team does not have a license for (`"all contributors must use GitHub Copilot Enterprise"` when nobody has access) or omits a tool the team actively uses (`.claude/` checked in but Claude Code unmentioned). The policy must reflect the actual toolchain.
- **NO** copy-paste of the Linux Foundation generative AI policy verbatim. The LF policy is a model, not a drop-in — it assumes DCO, CLA, and a specific governance structure most projects do not have. Tune it.
- **NO** burying the policy at the bottom of a 2000-line `CONTRIBUTING.md`. Put the `## AI-assisted contributions` section in the first third of the doc, with a link in the table of contents.

Examples of BAD fixes:
- Adding to `README.md`: "We accept AI-generated code as long as it's good." No disclosure, no attribution format, no banned cases, no IP section. The signal stays failed.
- Creating `AI-POLICY.md` with the single line "Use AI responsibly." Aspirational, unenforceable, and nobody reads a standalone file the rest of the docs do not link to.
- A `CONTRIBUTING.md` AI section that says "disclose AI use in your PR description" but provides no format, no example, and no PR-template field to capture it. Contributors will write "used AI" and reviewers cannot tell which tool, which scope, or whether it was a one-line completion or a 500-line generation.
- A policy that allows "Copilot, Cursor, and Claude" but the repo's `.claude/settings.json` and `.factory/settings.json` show the team uses Factory droid — the policy omits the tool the team actually ships with.
- A blanket ban ("no AI-assisted contributions") on a project whose maintainers' commit history clearly shows `Co-authored-by: copilot-swe-agent[bot]`. Hypocrisy training contributors to ignore the rule.
- A policy added to `CONTRIBUTING.md` but `AGENTS.md` is silent — the agent never reads `CONTRIBUTING.md` (most agent runtimes only auto-load `AGENTS.md`/`CLAUDE.md`) and authors a 200-line PR with no disclosure. The signal looks satisfied on paper but fails in practice.

Examples of GOOD fixes:

**1. `CONTRIBUTING.md` section** (replace `<REPO_NAME>`, `<LICENSE>`, tool list with the repo's actual values):

```markdown
## AI-assisted contributions

<REPO_NAME> accepts contributions developed with AI assistance, subject to the rules below. Contributors are responsible for every line they submit, regardless of who or what wrote it.

### Disclosure

Disclose AI involvement when AI generated **more than a trivial completion** — anything from a single function body upward, any test case, any non-trivial doc section, or any AI-authored commit message.

Disclosure goes in two places:

1. **Commit trailer** — add an `Assisted-by:` line to the commit message:
   ```
   Add OAuth token refresh

   Assisted-by: claude-sonnet-4.5 [Claude Code]
   Signed-off-by: Jane Doe <jane@example.com>
   ```
   For substantial AI authorship (e.g. an entire file scaffolded by the tool), use `Generated-by:` instead. Only humans add `Signed-off-by:` — the AI cannot certify the DCO.

2. **PR description** — check the `AI assistance` box in the PR template and name the tool + scope.

Single-line completions (autocomplete of a variable name, a one-line if-guard) do not require disclosure.

### Allowed tools

The following AI tools are sanctioned for use in this repo:

- **GitHub Copilot** (autocomplete + chat) — covered by the org Copilot Enterprise license
- **Claude Code** (Anthropic) — for agent workflows; see `.claude/settings.json` for the permission policy
- **Factory droid** — for agent workflows; see `.factory/settings.json`
- **Cursor** — IDE-level use only; do not commit `.cursor/rules/` overrides without review

Use of any other tool requires opening an issue first so we can assess license terms and training-data provenance.

### IP and licensing

By submitting a contribution, you warrant that:

- You have the right to submit the contribution under <REPO_NAME>'s license (`<LICENSE>`).
- The AI tool you used is not configured to ingest or output copyleft training data that would taint the contribution. (Copilot Business/Enterprise's "Suggestions matching public code: blocked" setting satisfies this for Copilot; equivalent settings exist for other tools.)
- The contribution does not include verbatim memorized code from a license-incompatible source. If the tool returned a long, suspiciously-specific snippet, search GitHub for it before committing.

For DCO-signed projects: the human contributor signs off and bears legal accountability. The AI tool does not sign off.

### Banned uses

Do NOT use AI to:

- Generate issue or PR text designed to look like a human-authored bug report or feature request (slop PRs). Reviewers will close these and may ban repeat offenders.
- Review or approve other contributors' PRs as the sole reviewer. AI-assisted review is fine as a second opinion; the human reviewer signs off.
- Bypass security review on dependency bumps, authentication code, or cryptography. AI-assisted code in these areas requires a human security reviewer.
- Author commit messages for code you have not read end-to-end. If you cannot explain the diff in your own words, do not submit it.
- Translate user-facing docs without a human translator review.

### Increased scrutiny

PRs disclosed as AI-assisted may receive extra scrutiny — more tests requested, more explanation of intent, more detail on how the tool was used. This is not a punishment; it is calibration. The disclosure is what makes the scrutiny possible.
```

**2. `AGENTS.md` cross-reference** (so the agent discovers the policy at session start):

```markdown
## AI policy

This repo accepts AI-assisted contributions under the rules in [`CONTRIBUTING.md#ai-assisted-contributions`](./CONTRIBUTING.md#ai-assisted-contributions). The short version:

- **Disclose** any commit where you authored more than a trivial completion. Use the `Assisted-by: <model> [<tool>]` commit trailer.
- **Do not** add `Signed-off-by:` on the human's behalf — only the human signs the DCO.
- **Do not** generate slop PRs, sole-reviewer approvals, or commit messages for code the human has not reviewed.
- **Check** the `AI assistance` box in the PR template when you open the PR.
```

**3. `.github/PULL_REQUEST_TEMPLATE.md` extension**:

```markdown
## AI assistance

- [ ] This PR was developed with AI assistance
- **Tool(s)**: <e.g. Claude Code, Copilot, Factory droid; leave blank if not applicable>
- **Scope**: <one line — autocomplete only / scaffolded a module / wrote tests / full agent authorship>

See [CONTRIBUTING.md#ai-assisted-contributions](../CONTRIBUTING.md#ai-assisted-contributions) for what counts as AI assistance and what must be disclosed.
```

**4. (Optional) CI check that enforces the trailer** — `.github/workflows/ai-disclosure.yml`:

```yaml
name: AI disclosure check
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Verify Assisted-by trailer if PR is marked AI-assisted
        run: |
          if grep -q '^\- \[x\] This PR was developed with AI assistance' <(gh pr view ${{ github.event.pull_request.number }} --json body -q .body); then
            git log origin/${{ github.base_ref }}..HEAD --format='%(trailers:key=Assisted-by,key=Generated-by)' | grep -q . \
              || { echo "PR marked AI-assisted but no Assisted-by / Generated-by trailer found in commits"; exit 1; }
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

The CI check is not required for the signal to pass, but it converts the policy from a written rule into an enforced one.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed: which file got the policy section, where the AGENTS.md cross-reference lives, whether the PR template was extended, and how you confirmed the policy is discoverable (e.g., "grepped from a fresh clone, all links resolve; opened a draft PR and confirmed the AI-assistance checkbox renders")

## References

- Linux Foundation Generative AI Policy (model policy with `Assisted-by:` / `Generated-by:` trailer formats): https://www.linuxfoundation.org/legal/generative-ai
- Linux kernel AI Coding Assistants policy (`Assisted-by: AGENT_NAME:MODEL_VERSION` trailer, DCO accountability, no AI Signed-off-by): https://docs.kernel.org/process/coding-assistants.html
- OpenInfra Foundation Policy for AI Generated Content (disclosure thresholds, allowed-tool scoping): https://openinfra.org/legal/ai-policy/
- CPython Developer's Guide — Generative AI (acceptable / unacceptable uses, slop-PR enforcement): https://devguide.python.org/
- Curated list of open-source AI contribution policies (Apache, Fedora, QEMU, NetBSD, GNOME Loupe, Drupal, LLVM): https://github.com/melissawm/open-source-ai-contribution-policies
- Red Hat — AI-assisted development and open source (legal / cultural analysis of disclosure regimes): https://www.redhat.com/en/blog/ai-assisted-development-and-open-source-navigating-legal-issues
- DigitalOcean — Contributing AI-Generated Code with Care (CONTRIBUTING.md examples, minimal-to-best PR blurbs): https://www.digitalocean.com/community/tutorials/ai-coding-tools-open-source
- Probabl — Maintaining open source in the age of generative AI (maintainer + contributor recommendations): https://blog.probabl.ai/maintaining-open-source-age-of-gen-ai
- Anthropic Usage Policies (banned use cases reference for derivative AI tool policies): https://www.anthropic.com/legal/aup
- OpenAI Usage Policies (reference for output-handling and attribution norms): https://openai.com/policies/usage-policies
</system-reminder>
