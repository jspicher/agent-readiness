[Readiness Fix] <REPO_NAME> Security Policy

Fix the failing signal: Security Policy ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Security Policy
**Score**: [0/1]
**Description**: Repository documents how to report vulnerabilities through a checked-in security policy that GitHub's UI surfaces on the Security tab.
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Security policy – check for a `SECURITY.md` file that GitHub will surface on the repo's Security tab. PASS requires ALL of the following:

1. **File location GitHub recognizes**: `SECURITY.md` (case-insensitive) at one of `./SECURITY.md`, `./.github/SECURITY.md`, or `./docs/SECURITY.md`. Any other path (e.g. `./security/policy.md`, `./SECURITY.txt`, a section inside `README.md`) is invisible to GitHub's "Report a vulnerability" UI and FAILS. If the org owns a `.github` repo with a default `SECURITY.md`, the per-repo signal still requires an explicit file or an explicit pointer in `./.github/SECURITY.md` that says "see https://github.com/<org>/.github/blob/main/SECURITY.md" — assume nothing.
2. **A real reporting channel** — not "open an issue" (that's public disclosure, the opposite of what a policy is for). Acceptable channels: (a) GitHub Private Vulnerability Reporting (PVR) enabled on the repo with an instruction to use the "Report a vulnerability" button on the Security tab; (b) a monitored security inbox (`security@<domain>`, NOT a personal address that will rotate when someone leaves); (c) a third-party disclosure platform URL (HackerOne, Bugcrowd, huntr.dev). At least one channel must be present. PVR enabled WITHOUT a SECURITY.md still fails because researchers landing on the repo without scrolling to the Security tab will not discover it.
3. **Supported Versions table** listing which release lines receive security fixes. A table with one row (`main: ✅`) is acceptable for single-version projects; the table itself is the contract. "We support the latest version" prose without a table FAILS — it's the unambiguous version mapping that lets a reporter know whether their finding is in scope.
4. **Response SLA** — concrete numbers for (a) acknowledgement of receipt and (b) initial triage / status update. "We will respond as soon as possible" is not an SLA. Typical: ack within 3 business days, triage within 7 business days.
5. **What to include in a report** — at minimum: affected version, reproduction steps, impact assessment. Without this, reports arrive as "your app is insecure" with no actionable content.
6. **For deployed web apps**: a `/.well-known/security.txt` (RFC 9116) file served from the production host, with at minimum `Contact:` and `Expires:` fields. The `Contact:` value MUST match the channel in SECURITY.md; the `Expires:` date MUST be in the future (RFC 9116 recommends ≤ 1 year out). A repo that ships a web service but has no security.txt FAILS this signal even if SECURITY.md is perfect.

Also verify: open the repo on github.com → Security tab → confirm the "Security policy" card shows the file (not "No security policy") and the "Private vulnerability reporting" row says "Enabled". A SECURITY.md that GitHub doesn't recognize is a documentation file, not a policy.

A `README.md` paragraph titled "Security" saying "please email us if you find a bug" is prose, not a policy, and FAILS this signal.

## Your Task

1. Explore the repository to determine current state — check for `SECURITY.md` at all three valid paths, check `.github/` for an org-level pointer, check whether the repo deploys a web service (look at `Dockerfile`, `vercel.json`, `next.config.*`, `wrangler.toml`, `.github/workflows/deploy*`), and confirm via `gh api repos/<owner>/<repo>/private-vulnerability-reporting --jq .enabled` whether PVR is already enabled (response `true` = yes; 404 = repo lacks the feature flag).
2. Make **substantive improvements**:
   - Write `SECURITY.md` (root or `.github/`) covering all six criteria above. Tune the supported versions table to the repo's actual release lines (read `package.json` version, `CHANGELOG.md`, or `git tag` for the last 12 months). Tune "what to include" to the stack (e.g. browser repro for a frontend, request/response pair for an API, container ID for a Docker image).
   - Enable Private Vulnerability Reporting on the repo: `gh api -X PUT repos/<owner>/<repo>/private-vulnerability-reporting` (requires admin token; this is the dedicated endpoint added 2023-08-16 — the older `security_and_analysis` PATCH does NOT accept a `private_vulnerability_reporting` key). If you do not have admin, document the exact click-path in the PR description so the maintainer can flip it in one step.
   - If the repo deploys a web service, add `public/.well-known/security.txt` (or the framework's equivalent static-asset path) with a real `Contact:`, an `Expires:` date 11 months out, and `Preferred-Languages: en`. Sign it with PGP if the project already publishes a PGP key; otherwise plain text is RFC 9116-compliant.
3. Verify the fix:
   - `gh api repos/<owner>/<repo>/community/profile --jq .files.code_of_conduct,.files.contributing,.files.license` (the same endpoint reports `security_policy.url` — confirm it's non-null and points to your file).
   - `gh api repos/<owner>/<repo>/private-vulnerability-reporting --jq .enabled` returns `true`.
   - Hit `https://<production-host>/.well-known/security.txt` and confirm it returns 200 with `Content-Type: text/plain` and parses cleanly at `https://securitytxt.org/` or `https://www.sitesecurityscore.com/tools/security-txt-validator`.
4. Keep changes focused on this signal — do not refactor unrelated security config (Dependabot, code scanning, branch protection are separate signals).
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** SECURITY.md that consists of one sentence: "Please email security@example.com if you find a vulnerability." That fails criteria 3, 4, and 5 and signals the maintainer did not read the prompt.
- **NO** personal email addresses as the reporting channel (`jdoe@gmail.com`, `firstname.lastname@company.com`). The address MUST be a role inbox that survives the person leaving — `security@<domain>`, a HackerOne URL, or PVR. A personal address rotates and the policy bounces silently.
- **NO** "report by opening an issue" instructions — public issues are public disclosure, which is the failure mode the policy exists to prevent.
- **NO** copy-paste of GitHub's default template without filling in real values. The placeholders (`5.1.x ✅`, `< 4.0 ❌`, `security@example.com`) MUST be replaced with the project's actual versions and contact. Reviewers grep for `example.com` and `5.1.x` to catch this.
- **NO** Supported Versions table that contradicts reality (e.g. listing `v2.x ✅` when the last v2 release was 18 months ago and has known unpatched CVEs).
- **NO** "Expires:" date in the past on `security.txt` — the file is treated as stale and most scanners FAIL it. Set it 11 months out and add a calendar reminder, or automate regeneration in CI.
- **NO** committing the file to a path GitHub does not recognize (`./docs/security/policy.md`, `./SECURITY.txt`, `./.well-known/SECURITY.md` inside the repo). GitHub only looks at `./SECURITY.md`, `./.github/SECURITY.md`, `./docs/SECURITY.md`.
- **NO** enabling PVR without also writing SECURITY.md. The PVR button is only discoverable from the Security tab; researchers landing on the README will email a random committer instead.
- **NO** SECURITY.md that promises "24-hour response" when the maintainer is a solo dev who checks email weekly. The SLA is a contract — pick a number you'll actually hit.

Examples of BAD fixes:
- A `SECURITY.md` with `Please report issues to me@my-personal-domain.com` and nothing else — fails 3, 4, 5, and the email will bounce in 18 months.
- Copy-pasting the GitHub-suggested template verbatim with `5.1.x` and `example.com` left in — the file validates as Markdown but the contact channel is fictional.
- Enabling PVR alone via `gh api -X PUT .../private-vulnerability-reporting` and closing the ticket — researchers without GitHub accounts (most security firms file through dedicated channels) cannot report.
- Adding `public/security.txt` (missing the `/.well-known/` prefix) — RFC 9116 §3 permits root as a legacy/fallback path but mandates the well-known path for new deployments and most scanners prefer the well-known location; use `/.well-known/security.txt`.
- A Supported Versions table listing every minor version back to 1.0 as supported — sets an unmaintainable scope; reporters will hold you to it.

Examples of GOOD fixes:
- A complete `SECURITY.md` at repo root:
  ```markdown
  # Security Policy

  ## Supported Versions

  | Version | Supported          |
  | ------- | ------------------ |
  | 4.x     | :white_check_mark: |
  | 3.x     | :white_check_mark: (security fixes only, until 2026-12-31) |
  | < 3.0   | :x:                |

  ## Reporting a Vulnerability

  **Do not open a public GitHub issue for security vulnerabilities.**

  Preferred channel: use GitHub's [Private Vulnerability Reporting](https://github.com/<OWNER>/<REPO>/security/advisories/new) button on the Security tab.

  Alternative: email `security@<DOMAIN>` (monitored by the platform team, PGP key at https://<DOMAIN>/.well-known/pgp.asc).

  ### What to include
  - Affected version (`git rev-parse HEAD` of the deployed commit, or the npm/PyPI version)
  - Reproduction steps — for the API, a minimal `curl` command; for the web UI, browser + steps + screenshot
  - Impact assessment (what data/permissions the vulnerability exposes)
  - Your proposed CVSS v3.1 vector if you have one

  ### Response SLA
  | Stage                          | Target            |
  | ------------------------------ | ----------------- |
  | Acknowledgement of receipt     | 3 business days   |
  | Initial triage / severity call | 7 business days   |
  | Fix or mitigation in `main`    | 30 days (critical/high), 90 days (medium/low) |
  | Public advisory + CVE          | After fix ships and a 7-day patch window for downstream consumers |

  We credit reporters in the GitHub Security Advisory unless you request anonymity.

  ## Out of Scope
  - Vulnerabilities in dependencies — file with the upstream project; we'll bump after their fix lands.
  - Findings on `*.staging.<DOMAIN>` or `*.preview.<DOMAIN>` — these are ephemeral environments without production data.
  - Self-XSS, missing security headers without exploit, automated scanner output without proof of concept.
  ```
- Enable PVR (admin token required; use the dedicated endpoint added 2023-08-16, NOT the legacy `security_and_analysis` PATCH which does not accept a `private_vulnerability_reporting` key):
  ```bash
  gh api -X PUT repos/<OWNER>/<REPO>/private-vulnerability-reporting
  ```
  Confirm:
  ```bash
  gh api repos/<OWNER>/<REPO>/private-vulnerability-reporting --jq .enabled
  # → true
  ```
- For a deployed web app, add `public/.well-known/security.txt`:
  ```
  Contact: mailto:security@<DOMAIN>
  Contact: https://github.com/<OWNER>/<REPO>/security/advisories/new
  Expires: 2027-04-15T00:00:00Z
  Preferred-Languages: en
  Canonical: https://<DOMAIN>/.well-known/security.txt
  Policy: https://github.com/<OWNER>/<REPO>/blob/main/SECURITY.md
  ```
  And a CI step that regenerates `Expires:` 11 months out on every release tag, or a `.github/workflows/security-txt-refresh.yml` cron that opens a PR when `Expires:` is within 30 days of today.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- GitHub: Adding a security policy to your repository: https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository
- GitHub: Configuring Private Vulnerability Reporting for a repository: https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository
- GitHub: Privately reporting a security vulnerability: https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability
- GitHub: Coordinated disclosure of security vulnerabilities: https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/about-coordinated-disclosure-of-security-vulnerabilities
- GitHub Blog: Maintainer's guide to vulnerability disclosure: https://github.blog/security/vulnerability-research/a-maintainers-guide-to-vulnerability-disclosure-github-tools-to-make-it-simple/
- Open Source Guides: Security best practices for your project: https://opensource.guide/security-best-practices-for-your-project/
- RFC 9116 (security.txt): https://www.rfc-editor.org/rfc/rfc9116.html
- securitytxt.org generator + validator: https://securitytxt.org/
- Example reference policy (sigstore): https://github.com/sigstore/.github/blob/main/SECURITY.md
</system-reminder>
