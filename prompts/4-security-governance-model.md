[Readiness Fix] <REPO_NAME> Governance Model

Fix the failing signal: Governance Model ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Governance Model
**Score**: [0/1]
**Description**: Documented maintainer roles, decision-making process, and escalation paths
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Governance model – check for a checked-in, human-readable document that names the people (or roles) who can merge, release, and resolve disputes for this repo. PASS requires at least one of the following, with concrete content (not a stub):

1. **GOVERNANCE.md** at repo root or in `.github/` / `docs/` describing (a) the governance archetype the project follows (BDFL, meritocracy, technical steering committee, Apache PMC, CNCF-style TOC subproject), (b) the named roles (e.g. Maintainer, Reviewer, Triager, TSC member, Release Manager) with the rights and responsibilities of each, (c) the decision-making process (lazy consensus, majority vote, RFC/PEP process), (d) how disputes escalate (who breaks ties, what quorum is required), and (e) how new maintainers are nominated and how existing maintainers step down or move to emeritus. A document that only says "decisions are made by consensus" without defining who is in the consensus group is a FAIL.
2. **MAINTAINERS.md** (CNCF convention) or `OWNERS` files listing the current humans by GitHub handle, with role (`maintainer`, `reviewer`, `approver`, `emeritus`) and area of responsibility. The list MUST be current — if the top three contributors over the last 12 months are not on it, the file is stale and FAILs. Note: `CODEOWNERS` is a separate signal (auto-review routing); it does not satisfy governance because it does not describe decision-making or escalation.
3. **Charter / Steering doc** for foundation-hosted projects (CNCF, Apache, Eclipse) that links to the foundation's bylaws AND a project-specific addendum naming the current PMC / TSC / TOC members and their terms.

Also verify the document is reachable: a `GOVERNANCE.md` linked from `README.md` and `CONTRIBUTING.md` is found by both humans and agents; one buried in `docs/internal/legacy/` is not. A `MAINTAINERS.md` with no commit in the last 12 months is presumed stale unless the contributor graph confirms the same people are still active.

A `CONTRIBUTING.md` paragraph saying "the core team will review your PR" without naming the core team or its decision process is documentation, not governance, and FAILs this signal.

## Your Task

1. Explore the repository to understand the current state — list `GOVERNANCE.md`, `MAINTAINERS.md`, `OWNERS`, `CHARTER.md`, `STEERING.md`, `.github/GOVERNANCE.md`, and any `CONTRIBUTING.md` / `README.md` sections that mention governance. Run `git shortlog -sne --since="12 months ago" | head -20` to identify the active maintainers who must appear in `MAINTAINERS.md`.
2. Pick an archetype that matches the project's reality — do not invent a TSC for a two-person repo, and do not call a 40-contributor project a BDFL if no single person actually holds veto.
   - **BDFL**: one named person with final say; works for early-stage or single-author projects (Python pre-2018, Linux kernel).
   - **Meritocracy / lazy consensus**: any maintainer can merge; objections within N business days block; works for small (3-8) maintainer teams (most CNCF sandbox projects).
   - **Technical Steering Committee (TSC)**: elected/appointed body with named seats, term lengths, and quorum rules; works for multi-org projects (Node.js, OpenTelemetry, Kubernetes SIGs).
   - **Apache PMC**: PMC Chair + members + committers, decisions by lazy consensus with binding +1 votes from PMC members; works for foundation-hosted projects.
3. Make **substantive improvements** by writing real, project-tuned governance:
   - Create `GOVERNANCE.md` at repo root naming the archetype, the roles, the decision process, the escalation path, the new-maintainer nomination process, and the emeritus / step-down process.
   - Create `MAINTAINERS.md` at repo root with a table of current maintainers (GitHub handle, role, area, joined date) and an `Emeritus` section for former maintainers.
   - Link both files from `README.md` (under a "Governance" or "Project" heading) and from `CONTRIBUTING.md` (under a "How decisions are made" section).
4. Verify the result: confirm every person merging to `main` in the last 90 days appears in `MAINTAINERS.md` (or is explicitly flagged as a bot / external contributor); confirm `GOVERNANCE.md` answers the five questions (who decides, how, how to escalate, how to join, how to leave) without using the word "consensus" undefined.
5. Keep changes focused on this signal — do not rewrite `CONTRIBUTING.md` end-to-end, do not add a Code of Conduct (separate signal), do not edit `CODEOWNERS`.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** vague "decisions are made by consensus" without naming who is in the consensus group, what quorum is required, and what happens when consensus fails. Undefined consensus is the most common governance failure mode — it lets the loudest contributor win and burns out everyone else.
- **NO** `MAINTAINERS.md` that lists people who left the project 18 months ago. A stale list is worse than no list because agents (and new contributors) will tag the wrong humans.
- **NO** missing escalation path. Every governance doc MUST answer "what happens when two maintainers disagree and neither will yield" — name the tie-breaker (BDFL, TSC chair, PMC vote, foundation board).
- **NO** missing emeritus / step-down process. Maintainers leave; without a documented off-ramp, dormant accounts accumulate merge rights for years and become an attack surface.
- **NO** burying Code of Conduct enforcement inside governance ("the maintainers will handle CoC violations") without naming the CoC committee or the reporting address. CoC enforcement is its own role with its own escalation — link to `CODE_OF_CONDUCT.md`, do not absorb it.
- **NO** copying the Kubernetes governance doc verbatim into a 3-person side project. Right-size the archetype to the actual contributor count.
- **NO** putting governance in `README.md` as a paragraph. `README.md` rots faster than dedicated files and is not where humans (or agents) look for decision authority.
- **NO** `OWNERS` files with `approvers: []` and `reviewers: []` empty — that is a stub that locks no one in and lets anyone merge.

Examples of BAD fixes:

- A `GOVERNANCE.md` containing only: "This project follows a consensus-based model. The maintainers will make decisions together." Names nobody, defines nothing, escalates nowhere.
- A `MAINTAINERS.md` with five names where `git shortlog --since="12 months ago"` shows three of them have not committed in over a year and the top two recent contributors are missing.
- Adding `GOVERNANCE.md` that says "see CONTRIBUTING.md" while `CONTRIBUTING.md` says "see GOVERNANCE.md". Circular reference, zero content.
- Listing maintainers by first name only ("Alice, Bob, Carol") with no GitHub handles — agents cannot route PRs or @-mention them.

Examples of GOOD fixes:

- **GOVERNANCE.md skeleton (meritocracy archetype):**

  ```markdown
  # Governance

  This project follows a **meritocratic, lazy-consensus** model.

  ## Roles

  | Role | Rights | Responsibilities |
  |---|---|---|
  | **Contributor** | Open issues, submit PRs | Follow CONTRIBUTING.md |
  | **Reviewer** | Approve PRs (non-binding) | Review PRs in their area within 5 business days |
  | **Maintainer** | Merge PRs, cut releases, vote | Triage issues, mentor reviewers, attend monthly sync |
  | **Lead Maintainer** | Tie-breaking vote, security disclosure point of contact | Quarterly roadmap, conflict resolution |

  Current holders of each role are listed in [MAINTAINERS.md](./MAINTAINERS.md).

  ## Decision-making

  - **Routine changes** (bug fixes, docs, dependency bumps): one maintainer approval + green CI = merge.
  - **Substantive changes** (new public API, breaking change, new dependency >100KB): open a `proposal/` issue, wait 7 calendar days for objections (lazy consensus). Any maintainer's `-1` blocks; resolution requires either withdrawal of the `-1` or a majority vote of maintainers.
  - **Releases**: cut by any maintainer following [RELEASE.md](./RELEASE.md); semver enforced.

  ## Escalation

  Disputes that maintainers cannot resolve within 14 days escalate to the **Lead Maintainer**, whose decision is final for this repository. Disputes involving the Lead Maintainer escalate to a majority vote of the remaining maintainers.

  Code of Conduct violations follow a separate process — see [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

  ## Becoming a maintainer

  Nomination by an existing maintainer after the candidate has:

  1. Authored 5+ merged PRs over the past 6 months, AND
  2. Reviewed 10+ PRs (with substantive feedback, not LGTM), AND
  3. Demonstrated familiarity with at least two subsystems.

  Nomination posted as an issue; lazy-consensus approval over 7 days; added to `MAINTAINERS.md` on approval.

  ## Stepping down / Emeritus

  Maintainers inactive for 6 months are moved to `Emeritus` in `MAINTAINERS.md` (merge rights revoked, can be reinstated on request). Voluntary step-down: open a PR moving yourself to Emeritus.
  ```

- **MAINTAINERS.md table:**

  ```markdown
  # Maintainers

  See [GOVERNANCE.md](./GOVERNANCE.md) for role definitions.

  ## Active

  | Handle | Role | Area | Joined |
  |---|---|---|---|
  | @alice | Lead Maintainer | Architecture, releases | 2023-01 |
  | @bob | Maintainer | Backend, database | 2023-04 |
  | @carol | Maintainer | Frontend, UX | 2024-02 |
  | @dave | Reviewer | Docs, examples | 2024-09 |

  ## Emeritus

  | Handle | Role (when active) | Active | Step-down |
  |---|---|---|---|
  | @eve | Maintainer | 2022-08 → 2024-06 | Moved to other project |
  ```

- For a foundation-hosted project, a `GOVERNANCE.md` that links to the foundation's charter (e.g. `https://github.com/cncf/foundation/blob/main/charter.md`) AND a `MAINTAINERS.md` that lists the current TOC subproject leads with term end dates.

- A `README.md` section that says: "Governance: this project follows a meritocratic lazy-consensus model — see [GOVERNANCE.md](./GOVERNANCE.md). Current maintainers are listed in [MAINTAINERS.md](./MAINTAINERS.md)."

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- CNCF project governance template (MAINTAINERS.md convention): https://contribute.cncf.io/maintainers/templates/governance-maintainer/
- CNCF MAINTAINERS.md template: https://github.com/cncf/project-template/blob/main/MAINTAINERS.md
- Kubernetes governance (TSC + SIG model): https://github.com/kubernetes/community/blob/master/governance.md
- Node.js governance (TSC + Collaborator model): https://github.com/nodejs/node/blob/main/GOVERNANCE.md
- Rust governance (Leadership Council + teams): https://github.com/rust-lang/rust/blob/master/GOVERNANCE.md
- OpenTelemetry governance (Governance Committee + Technical Committee): https://github.com/open-telemetry/community/blob/main/governance-charter.md
- Apache Software Foundation PMC guide: https://www.apache.org/foundation/how-it-works.html#pmc
- Producing Open Source Software, Karl Fogel — chapter on governance archetypes (BDFL vs consensus vs voting): https://producingoss.com/en/governance.html
- CHAOSS metrics for maintainer health (used to validate non-stale MAINTAINERS.md): https://chaoss.community/kb/metrics-model-collaboration-development-index/
</system-reminder>
