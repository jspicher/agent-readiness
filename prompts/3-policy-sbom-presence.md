[Readiness Fix] <REPO_NAME> SBOM Presence

Fix the failing signal: SBOM Presence ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: SBOM Presence
**Score**: [0/1]
**Description**: Software Bill of Materials generated or committed so downstream consumers and agents can reason about every component shipped in a build
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

SBOM presence – check for a Software Bill of Materials that is either committed to the repo or produced as a build artifact by CI. PASS requires at least one of the following, with the SBOM tied to a real build (not an empty scaffold):

1. **Committed SBOM file** in a standard format and a non-trivial component list. Acceptable filenames include `sbom.json`, `sbom.cdx.json`, `sbom.spdx.json`, `bom.json`, `cyclonedx.json`, or any file whose schema URL identifies it as CycloneDX (`http://cyclonedx.org/schema/bom/1.4`, `.../1.5`, `.../1.6`, `.../1.7`) or SPDX (`spdxVersion: "SPDX-2.3"` or `"SPDX-3.0.1"`). A file with `"components": []` or `"packages": []` is FAIL — it is a scaffold, not an SBOM.
2. **CI workflow that generates an SBOM on release or push** using a recognized generator: `anchore/sbom-action`, `CycloneDX/gh-node-module-generatebom`, `aquasecurity/trivy-action` with `format: cyclonedx` or `spdx-json`, `microsoft/sbom-tool`, `CycloneDX/cyclonedx-cli`, `cdxgen`, or `npm sbom --sbom-format=cyclonedx` / `npm sbom --sbom-format=spdx`. The workflow must upload the SBOM as a release asset, workflow artifact, OCI attestation (cosign attest --predicate), or via `actions/attest-sbom`. A workflow that generates an SBOM and discards it (no upload, no attestation) is FAIL.
3. **GitHub native dependency-graph SBOM is NOT sufficient on its own**. The endpoint `GET /repos/{owner}/{repo}/dependency-graph/sbom` exists for every repo with Dependabot enabled and produces an SPDX 2.3 document on demand. Counting this as the signal lets every public GitHub repo PASS without effort. It can be referenced as a fallback in `SECURITY.md`, but the signal requires a generated-and-published SBOM tied to a build artifact (container image, release tarball, binary).
4. **Container-image SBOM attestation**: a build that runs `cosign attest --predicate sbom.cdx.json --type cyclonedx <image>` (or the equivalent `actions/attest-sbom@v2`) and pushes the attestation alongside the image in OCI. Verify with `cosign verify-attestation` or `gh attestation verify`.

Also verify the SBOM is **refreshed**: a single `sbom.json` committed 18 months ago and never regenerated is stale and FAILs. Look for either (a) the file mtime inside a recent release artifact, (b) a workflow that regenerates it on every tag/release, or (c) an `actions/attest-sbom` step on the build job.

A `SECURITY.md` line that says "SBOM available on request" is documentation, not an artifact, and FAILs this signal.

## Your Task

1. Explore the repository to understand the current state — list every `sbom*.json`, `bom*.json`, `cyclonedx*`, `spdx*` file; check `.github/workflows/*.yml` for any of the generators named above; identify the primary build artifact (container image? npm/PyPI/crates package? Go binary? release tarball?). The SBOM must describe THAT artifact, not the source tree.
2. Make **substantive improvements** by wiring SBOM generation into the release path:
   - **Pick the right generator for the stack**. Container build → `anchore/sbom-action@v0` against the image digest (the most ecosystem-agnostic). Pure Node → `npm sbom --sbom-format=cyclonedx` (built into npm 10+; defaults to CycloneDX 1.5 — for 1.6 use `@cyclonedx/cyclonedx-npm@^2 --spec-version 1.6` instead, which is a separate npm package with finer-grained control). Python → `cyclonedx-py` or `trivy fs --format cyclonedx`. Multi-language monorepo → `cdxgen` or `syft` (both walk many ecosystems in one pass). Go binaries → `syft` on the built binary, NOT `go mod`.
   - **Generate from the built artifact**, not the source tree. Source-tree SBOMs miss the actual packages that ended up in the container (different base image, multi-stage build, vendored deps). Run the generator against the image digest or the produced binary.
   - **Pin the generator version**. `anchore/sbom-action@v0.20.0`, `syft v1.x.x` — never `@latest` or `@main` in a compliance pipeline.
   - **Choose a format and commit to it**. CycloneDX 1.6 JSON is the modern default (best vulnerability/VEX tooling support, EU CRA-compatible). SPDX 2.3 JSON if your downstream consumers (US federal customers, large enterprises with SPDX-only ingestion) require it. Generate both if uncertain — most tools support a single command for each.
   - **Publish it**. Either (a) attach the SBOM to the GitHub release with `anchore/sbom-action`'s built-in release upload, (b) push it as an OCI attestation with `actions/attest-sbom@v2` or `cosign attest --predicate sbom.cdx.json --type cyclonedx <image>@<digest>`, or (c) both. An SBOM that lives only in a workflow artifact (90-day retention) is not durable.
   - **Document where consumers can find it**. Add one line to `SECURITY.md` or `README.md`: "SBOM is published as a release asset (`sbom.cdx.json`) and as a CycloneDX attestation on the container image. Verify with `cosign verify-attestation --type cyclonedx ghcr.io/<org>/<repo>@<digest>`."
3. Verify the SBOM actually contains components: run the generator locally, then `jq '.components | length' sbom.cdx.json` (CycloneDX) or `jq '.packages | length' sbom.spdx.json` (SPDX). Expect a number that roughly matches the lockfile (package-lock.json, poetry.lock, go.sum, etc.). A count of 0 or 1 means the generator ran against the wrong target.
4. Validate the schema: `cyclonedx validate --input-file sbom.cdx.json` or `pyspdxtools --infile sbom.spdx.json`. A schema-invalid SBOM is rejected by downstream scanners (Dependency-Track, Grype, etc.).
5. Keep changes focused on this signal — do not refactor the build itself.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** committing an SBOM with `"components": []` or one package. A scaffolded `bom.json` with no real components is strictly worse than no SBOM because it gives downstream scanners false coverage.
- **NO** generating the SBOM from the source tree when the release artifact is a container or binary. Source-tree SBOMs list dev dependencies and miss runtime packages baked into the base image. The signal is about what you SHIP, not what you check in.
- **NO** SBOMs that only enumerate direct dependencies. CycloneDX requires a `dependencies` graph and SPDX requires `relationships` entries; an SBOM with 12 entries for a repo whose lockfile has 1,800 entries is a direct-only SBOM and useless for vulnerability triage (you cannot find a transitive `liblzma` or `log4j` in it).
- **NO** generating the SBOM but never uploading it anywhere. A workflow that runs `syft .` and exits has zero artifacts after the 90-day retention window. The SBOM must be attached to a release, pushed as an OCI attestation, or both.
- **NO** committing a one-time `sbom.json` and never refreshing it. Lockfiles drift weekly; an SBOM committed at v1.2.0 and never regenerated for v1.7.0 is misinformation. Generate on every tag/release.
- **NO** relying solely on `gh api /repos/{owner}/{repo}/dependency-graph/sbom`. This works for every public repo, ties to no specific build, and lists what GitHub's dependency graph thinks is there — not what your build actually shipped. It is acceptable as a fallback link in `SECURITY.md`, but not as the primary signal.
- **NO** pinning the generator to `@latest`. `anchore/sbom-action@latest` reaches a new major version overnight and silently changes output shape, breaking downstream Dependency-Track ingestion. Pin to a tag (`@v0.20.0`) or a SHA.
- **NO** picking a format your downstream tooling cannot read. If your customers run Dependency-Track or Grype, CycloneDX is the path of least resistance. If a government customer demands SPDX, generate SPDX. For EU CRA / BSI TR-03183-2 scope, CycloneDX 1.6+ or SPDX 3.0.1+ is required; for other downstream tooling CycloneDX 1.5 is still widely accepted.
- **NO** generating the SBOM AFTER you publish the release. The generation step must run on the same artifact digest that gets published, in the same workflow, before the release is marked latest.

Examples of BAD fixes:
- Adding `sbom.json` to the repo root containing `{"bomFormat":"CycloneDX","specVersion":"1.5","components":[]}` — empty components array, no provenance, never refreshed. Signal still FAILs.
- A workflow step `- run: syft dir:. -o cyclonedx-json > sbom.json` with no `upload-artifact`, no release attach, no `attest-sbom`. The file vanishes when the runner terminates.
- Generating an SPDX SBOM from the source tree of a project whose release artifact is a Docker image. The SBOM lists `pytest` and `eslint` (dev deps) but misses `glibc`, `openssl`, and `liblzma` from the base image — the exact components a CVE triage cares about.
- Adding `gh api /repos/${{ github.repository }}/dependency-graph/sbom > sbom.json` to a workflow. This is GitHub's view of the dependency graph, not your build's SBOM, and works for any repo with Dependabot — it does not represent project effort.
- A `SECURITY.md` saying "Contact security@example.com for our SBOM." That is a process, not an artifact. Auditors and agents both FAIL it.
- `anchore/sbom-action@main` — unpinned, will break on the next breaking release of the action.

Examples of GOOD fixes:

- For a Node.js container build, add `.github/workflows/release.yml` step that generates and attests a CycloneDX SBOM tied to the image digest:

  ```yaml
  jobs:
    release:
      runs-on: ubuntu-latest
      permissions:
        contents: write       # upload release asset
        packages: write       # push image
        id-token: write       # OIDC for cosign / attest-sbom
        attestations: write   # actions/attest-sbom
      steps:
        - uses: actions/checkout@v4

        - id: build
          uses: docker/build-push-action@v6
          with:
            push: true
            tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}

        - name: Generate CycloneDX SBOM from image digest
          uses: anchore/sbom-action@v0.20.0
          with:
            image: ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
            format: cyclonedx-json
            output-file: sbom.cdx.json
            upload-release-assets: true     # attaches to gh release on tag push

        - name: Attest SBOM to the image
          uses: actions/attest-sbom@v2
          with:
            subject-name: ghcr.io/${{ github.repository }}
            subject-digest: ${{ steps.build.outputs.digest }}
            sbom-path: sbom.cdx.json
            push-to-registry: true

        - name: Sanity check component count
          run: |
            COUNT=$(jq '.components | length' sbom.cdx.json)
            echo "SBOM components: $COUNT"
            test "$COUNT" -gt 10 || { echo "SBOM looks empty/direct-only"; exit 1; }
  ```

- For a pure-Node package (no container), use the npm built-in (npm 10+):

  ```yaml
  - run: npm ci
  - run: npm sbom --sbom-format=cyclonedx > sbom.cdx.json
  - run: npx --yes @cyclonedx/cyclonedx-cli validate --input-file sbom.cdx.json
  - uses: softprops/action-gh-release@v2
    if: startsWith(github.ref, 'refs/tags/')
    with:
      files: sbom.cdx.json
  ```

- For a Python project, prefer Trivy or cyclonedx-py over a source-tree-only generator:

  ```yaml
  - uses: aquasecurity/trivy-action@0.28.0
    with:
      scan-type: image
      image-ref: ghcr.io/${{ github.repository }}:${{ github.ref_name }}
      format: cyclonedx
      output: sbom.cdx.json
  ```

- A `SECURITY.md` block that documents discovery and verification:
  ```
  ## SBOM
  Every tagged release publishes a CycloneDX 1.6 SBOM as `sbom.cdx.json` on the
  GitHub release and as a CycloneDX attestation on the container image. Verify:

      gh release download <tag> -p sbom.cdx.json
      cosign verify-attestation --type cyclonedx \
        --certificate-identity-regexp 'https://github.com/<org>/<repo>/' \
        --certificate-oidc-issuer https://token.actions.githubusercontent.com \
        ghcr.io/<org>/<repo>@<digest>
  ```

## Why this matters

The xz-utils backdoor (CVE-2024-3094, CVSS 10.0, disclosed 29 March 2024) was a maintainer-implanted supply-chain attack that put a sshd authentication bypass into liblzma 5.6.0 and 5.6.1. It was caught by accident — Andres Freund at Microsoft noticed sshd login latency had increased by half a second. Before that accidental catch, the only deterministic way to know whether your fleet was exposed was to grep an SBOM for the affected liblzma version. Organizations with current, transitive SBOMs answered the "are we vulnerable?" question in hours; everyone else spent days SSH-ing into machines running `strings $(which xz)`.

Log4Shell (December 2021) and the SolarWinds Orion compromise (December 2020) made the same point earlier. Both targeted transitive dependencies — the components a developer never types but a build silently pulls in. An SBOM that only lists direct dependencies (the `dependencies` block of `package.json`, the top of `requirements.txt`) misses exactly the dependencies these incidents weaponized. Generating from the built artifact and including the full dependency graph is what makes an SBOM useful during an incident — and it is the only difference between "we ship an SBOM" and "the SBOM helped us."

US Executive Order 14028 and the corresponding NTIA Minimum Elements (July 2021), CISA's Framing Software Component Transparency (3rd ed., October 2024), and the EU Cyber Resilience Act (via BSI TR-03183-2, requiring CycloneDX 1.6+ or SPDX 3.0.1+ in JSON or XML) have moved SBOMs from a "nice to have" to a procurement gate. Federal customers and EU CRA-scope products will not buy software without a conformant SBOM, refreshed per release.

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed, which generator and format you picked and why, and how a downstream consumer can verify the SBOM

## References

- CycloneDX 1.6 specification release (2024-04-09, includes CBOM + Attestations): https://github.com/CycloneDX/specification/releases/tag/1.6
- CycloneDX format reference (1.6 JSON/XML): https://cyclonedx.org/docs/1.6/json/
- SPDX 2.3 specification: https://spdx.github.io/spdx-spec/v2.3/
- Anchore `sbom-action` GitHub Action (Syft wrapper, format options spdx-json / cyclonedx-json, release upload built in): https://github.com/anchore/sbom-action
- Syft (Anchore's SBOM generator, the engine behind sbom-action): https://github.com/anchore/syft
- `actions/attest-sbom@v2` — generate signed SBOM attestations via GitHub OIDC: https://github.com/actions/attest-sbom
- `npm sbom` built-in command (npm 10+, CycloneDX or SPDX output): https://docs.npmjs.com/cli/v10/commands/npm-sbom
- `@cyclonedx/cyclonedx-npm` (more accurate than `npm sbom` for npm projects): https://github.com/CycloneDX/cyclonedx-node-npm
- `cdxgen` (multi-language SBOM generator, ~30 ecosystems in one pass): https://github.com/CycloneDX/cdxgen
- Trivy SBOM generation (`trivy fs|image --format cyclonedx|spdx-json`): https://trivy.dev/latest/docs/supply-chain/sbom/
- Microsoft `sbom-tool` (SPDX 2.2 / 3.0 generator used by Windows + Azure builds): https://github.com/microsoft/sbom-tool
- Cosign `attest` / `verify-attestation` (CycloneDX predicate type for OCI attestations): https://docs.sigstore.dev/cosign/verifying/attestation/
- GitHub native dependency-graph SBOM REST endpoint (acceptable as fallback, not as primary signal): https://docs.github.com/en/rest/dependency-graph/sboms
- NTIA Minimum Elements For a Software Bill of Materials (July 2021, the EO 14028 baseline): https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom
- CISA Framing Software Component Transparency, 3rd ed. (October 2024 — current US guidance): https://www.cisa.gov/resources-tools/resources/framing-software-component-transparency-2024
- EU CRA / BSI TR-03183-2 (requires CycloneDX 1.6+ or SPDX 3.0.1+ for products in CRA scope): https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TR03183/BSI-TR-03183-2.html
- CVE-2024-3094 xz-utils / liblzma backdoor (the canonical "SBOMs would have made triage minutes not days" incident): https://openssf.org/blog/2024/03/30/xz-backdoor-cve-2024-3094/
</system-reminder>
