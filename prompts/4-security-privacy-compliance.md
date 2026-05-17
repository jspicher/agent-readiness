[Readiness Fix] <REPO_NAME> Privacy Compliance

Fix the failing signal: Privacy Compliance ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Privacy Compliance
**Score**: [0/1]
**Description**: GDPR/CCPA compliance infrastructure configured
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Privacy compliance – Check for privacy compliance infrastructure. Look for: 1) Consent management SDK/library (OneTrust, Cookiebot, custom consent banner). 2) Data retention policies documented. 3) GDPR/CCPA request handling code or documentation (data export, deletion endpoints). 4) Privacy-by-design patterns (data minimization configs, anonymization utilities). 5) Cookie/tracking consent implementation. PASS if evidence of privacy compliance infrastructure exists. Skip for apps without end-user data collection (e.g., internal tools, libraries, infrastructure).

## Your Task

1. Explore the repository to understand the current state related to this signal
2. Make **substantive improvements** to the codebase that genuinely address the signal
3. Verify your fix addresses the issue (e.g., run linter if fixing lint_config, run tests if adding tests)
4. Keep changes focused on this signal - don't refactor unrelated code
5. When done with code changes, open a PULL REQUEST with the changes and return the PR URL

## CRITICAL: Quality Standards — LEGAL LIABILITY WARNING

**Privacy compliance is a LEGAL domain.** GDPR, CCPA, PIPEDA, LGPD, and similar regimes carry regulator fines (up to 4% of global annual turnover under GDPR Art. 83) and private rights of action. A repository's `PRIVACY.md` or consent banner that CLAIMS compliance the code does not deliver creates **direct legal exposure for the repo owner**, NOT just a failed audit signal.

**This signal verifies that privacy *infrastructure* exists in the repo. It does NOT verify the application is actually compliant — that is a legal determination requiring counsel.** Your fix MUST NOT claim compliance the code does not implement.

Required guardrails on any fix:

- **NO** asserting "this repo is GDPR compliant" / "CCPA compliant" / "HIPAA compliant" in any committed file. Compliance is determined by a Data Protection Officer + counsel reviewing data flows, sub-processors, retention, and lawful basis — not by the presence of code patterns.
- **NO** committing a `PRIVACY.md` / privacy notice that lists data categories, retention windows, or lawful bases that contradict reality. A privacy notice is a binding public statement; mismatches between the notice and actual practice are the primary regulator-finding vector.
- **NO** wiring a consent banner that defaults to "all cookies accepted" or sets non-essential cookies before consent is recorded. Under GDPR/ePrivacy and CCPA opt-out frameworks, pre-checked consent is non-compliant by design.
- **NO** "data subject request" endpoints that return a placeholder JSON and never actually look up the user's data. A non-functional export/delete endpoint that LOOKS compliant is worse than no endpoint because it appears in the audit trail as evidence of a feature that does not exist.
- **NO** anonymization utilities that hash a primary key with a static salt — that is pseudonymization (still personal data under GDPR), not anonymization. Misnaming it in code/comments propagates the misclassification into operational decisions.
- **NO** empty placeholder files (e.g., empty `PRIVACY.md`, stub `consent.ts` with `export {}`), no minimal implementations, no disabling checks, no trivial changes that game the metric.

Examples of BAD fixes:
- Adding a `PRIVACY.md` that says "This project is GDPR compliant." with no data-flow analysis, no DPA process, no documented sub-processors, no retention table grounded in actual code.
- A "consent banner" component that records the user's choice to `localStorage` but the analytics SDK initializes on page-load before the banner renders — cookies are dropped before consent.
- A `/api/user/export` endpoint that returns `{ "user": "<id>", "data": "Contact us to retrieve your data." }` — visible-but-non-functional, attracts regulator attention without satisfying Art. 15.
- An `anonymize()` helper that returns `sha256(email + "static_salt")` — reversible by anyone with the salt; still personal data under GDPR Recital 26.
- Importing a third-party consent library (OneTrust, Cookiebot) without configuring purposes, categories, or vendor list — the banner renders but consent state is meaningless.

Examples of GOOD fixes — **infrastructure only, no compliance claims**:
- Adding a CONSENT layer that BLOCKS non-essential SDK loads until the user has recorded consent, with categories (analytics / advertising / functional) routed to the right SDKs. Document the implementation in `docs/privacy/consent-architecture.md` — NOT in a `PRIVACY.md` user-facing notice.
- Adding `/api/user/export` and `/api/user/delete` endpoints that actually enumerate the user's records across the application's data stores (DB tables, S3 prefixes, downstream queues). Include integration tests with seeded fixtures verifying the export contains the seeded data and the delete leaves no residue. Document the data scope in `docs/privacy/dsar-data-map.md` — note that the legal "right of access" / "right of erasure" surface area is broader than this code path and requires DPO review.
- Adding a `docs/privacy/data-flow.md` that enumerates every PII field captured, the lawful basis the team believes applies, the sub-processors that receive each field, and the retention window — marked as a draft for legal review, NOT as a binding compliance statement.
- Adding code-level data-minimization: a Zod/Pydantic schema at the API boundary that strips fields the backend does not need, with tests confirming a request with extra fields drops them before storage.

If the repository does not collect end-user data (internal tool, library, infrastructure), do NOT manufacture privacy infrastructure to pass this signal. Add a note to README explaining the data-collection scope is zero and the signal is N/A.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase
</system-reminder>
