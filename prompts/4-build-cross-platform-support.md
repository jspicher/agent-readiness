[Readiness Fix] <REPO_NAME> Cross-platform Support

Fix the failing signal: Cross-platform Support ([0/1])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: Cross-platform Support
**Score**: [0/1]
**Description**: Builds on multiple OS/arch
**Why it failed**: <WHY_IT_FAILED -- populated from rationale in your readiness report>

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

Cross-platform support — check that the repo actually **produces build artifacts for more than one OS/arch tuple**, not just that CI runs tests on multiple OSes (that is signal #62 — Multi-platform CI). PASS requires at least one of the following, checked into the repo:

1. **Cross-compilation in the build script or release workflow**, with multiple target tuples invoked from a single host:
   - Rust: `cargo build --target x86_64-unknown-linux-gnu` AND `cargo build --target aarch64-apple-darwin` (or similar) — at least two distinct `--target` values, driven by a script, `Makefile`, `justfile`, or release workflow.
   - Go: `GOOS=linux GOARCH=amd64 go build` AND `GOOS=darwin GOARCH=arm64 go build` (or similar) — two or more `GOOS`/`GOARCH` combinations, ideally enumerated in a matrix or release tool config.
   - Zig: `zig build -Dtarget=x86_64-linux-gnu` AND `zig build -Dtarget=aarch64-macos`, or `zig cc -target <tuple>` invoked for multiple targets.
   - C/C++: a CMake / Meson / Bazel toolchain file per target invoked from one host, or an `xcompile.sh` wrapper.
2. **GoReleaser** (`.goreleaser.yaml` / `.goreleaser.yml`) with `builds[].goos` and `builds[].goarch` arrays that expand to **>1 OS/arch combination**, AND a release workflow that runs `goreleaser release`. A `.goreleaser.yaml` checked in but never invoked from CI is half-credit only if the file alone is the deliverable (e.g. a release-engineering template repo).
3. **Multi-arch container images** built with `docker buildx build --platform linux/amd64,linux/arm64 ...` (or `docker manifest create` for the legacy path) pushed under a single tag, AND a CI step that runs that buildx command. A `Dockerfile` that only builds for the host arch FAILs — buildx with a single `--platform` value also FAILs.
4. **Per-platform release jobs that actually produce artifacts**: a release workflow (e.g. `.github/workflows/release.yml`) where each matrix entry runs the project's build for a different OS/arch tuple and uploads the resulting binary/installer/image with `actions/upload-artifact@v4` or `softprops/action-gh-release@v2`. A workflow that runs `npm test` on three OSes is signal #62, not #106 — the criterion here is **artifact production** for a target the project ships.

A README sentence saying "supports Linux, macOS, and Windows" without any script, target list, or release workflow FAILs. A CI matrix that runs unit tests on three OSes but only uploads one binary built on `ubuntu-latest` FAILs (the macOS and Windows users get a Linux binary). A `Dockerfile` with `FROM node:20` and no buildx invocation FAILs even if the base image is multi-arch — the published image still inherits the build host's arch.

## Your Task

1. Inventory what the repo actually ships: look for `Cargo.toml` `[package]` metadata, `go.mod`, `.goreleaser.y*ml`, `Dockerfile`, `package.json` `bin`/`os`/`cpu` fields, `setup.py`/`pyproject.toml` `classifiers`, `.github/workflows/release.yml`, `Makefile` / `justfile` targets named `release*` / `dist*` / `cross*`. Note the platforms the README or release notes claim to support — those are the required targets.
2. Decide which mechanism fits the project:
   - **Go binary or CLI** → add `.goreleaser.yaml` and a release workflow; GoReleaser handles cross-compile, archive packaging, checksums, and GitHub release upload in one step.
   - **Rust binary or CLI** → add a release workflow using `taiki-e/upload-rust-binary-action@v1` or `cargo-dist` (`dist init`), with explicit `--target` per matrix entry and `cross` for foreign-libc targets.
   - **Container image** → add a `docker buildx` step using `docker/setup-qemu-action@v3`, `docker/setup-buildx-action@v3`, and `docker/build-push-action@v6` with `platforms: linux/amd64,linux/arm64`.
   - **Node CLI / npm package** with native deps → add `prebuildify` or `node-pre-gyp` build matrix per `os × arch`, upload prebuilt binaries to GitHub release, and add `npm` install hook to fetch the matching one. Pure-JS packages do not need this signal — verify before adding ceremony.
3. Make **substantive improvements**: write the cross-compile script or release workflow, list the actual targets the project supports (not the toolchain's full default set), and wire it into CI. Targets must be reachable from the host runner — Go and Zig cross-compile from anywhere; Rust needs `rustup target add <tuple>` and sometimes `cross`; CGO needs a per-target C toolchain (zig cc, musl-cross, osxcross) or you must set `CGO_ENABLED=0`.
4. Verify each target actually produces a binary: run the script locally (or push and watch the release workflow), then `file dist/<name>_linux_amd64` / `lipo -info` / `docker buildx imagetools inspect <image>` and confirm the arch matches the target tuple. A binary labelled `darwin_arm64` that `file` reports as `Mach-O 64-bit executable x86_64` is a misconfigured build, not a fix.
5. Keep changes focused on this signal — do not refactor unrelated workflows.
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL.

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** confusing #62 (multi-platform CI — tests on multiple OS) with #106 (cross-platform build — artifacts FOR multiple platforms). A matrix that runs `npm test` on Ubuntu / macOS / Windows and uploads one Linux tarball at the end still fails this signal. Each target the project claims to support must have a corresponding artifact in the release.
- **NO** `docker buildx build --platform linux/arm64` running on `ubuntu-latest` with QEMU emulation as the **only** path for arm64. QEMU is fine for small CLIs but for anything that compiles native code it is 5–20x slower and frequently miscompiles (rosetta-style bugs in numpy, sharp, libvips, ffmpeg wheels). For production arm64 images, build on a native ARM runner (`ubuntu-22.04-arm`, `ubuntu-24.04-arm`) and use buildx only to assemble the manifest from per-arch native builds.
- **NO** forgetting `CGO_ENABLED=0` when cross-compiling Go to a foreign OS without a C toolchain. `GOOS=linux GOARCH=arm64 go build` from a darwin/amd64 host with default `CGO_ENABLED=1` will fail with `cgo: C compiler not available` the first time the dependency tree pulls in a cgo package (sqlite, libpq, mattn/go-sqlite3). Either set `CGO_ENABLED=0` (pure-Go only) or wire in `zig cc` as the C compiler (`CC="zig cc -target aarch64-linux-musl"`).
- **NO** `cargo build --release` followed by `cp target/release/<bin> dist/` and calling that a "Linux build" when the release workflow runs on `macos-latest` — that uploads a darwin binary under a `linux` name and ships broken artifacts. Always use `--target <tuple>` AND read from `target/<tuple>/release/`.
- **NO** GoReleaser config that lists `goos: [linux, darwin, windows]` and `goarch: [amd64, arm64]` (= 6 builds) but the project actually only supports linux/amd64 and darwin/arm64 — the four extra builds will silently produce broken or untested binaries and users will file bugs against arches you never intended to ship. Trim `builds[].ignore` to the combinations you actually test.
- **NO** publishing a multi-arch image tag where one arch was built on the wrong base. `docker buildx build --platform linux/amd64,linux/arm64 -t repo:tag --push` with `FROM node:20-alpine` works because the base manifest has both arches; with `FROM node:20-alpine-amd64` (or any single-arch pinned base) the arm64 layer will fail to pull or run. Always pin to a multi-arch base or use a `--platform=$BUILDPLATFORM` cross-build pattern with `--platform=$TARGETPLATFORM` final stage.
- **NO** missing platforms from the release. If the README says "Windows, macOS, Linux" but `.goreleaser.yaml` skips `windows`, users will open issues asking where the `.exe` is. Either ship every documented platform or update the docs.
- **NO** committing a `Dockerfile.arm64` and `Dockerfile.amd64` pair built by separate jobs and pushed under different tags (`repo:v1-amd64`, `repo:v1-arm64`) without assembling a manifest. `docker pull repo:v1` on an arm64 host will fail or pull amd64. Use `docker buildx imagetools create` to assemble a single multi-arch tag.

Examples of BAD fixes:
- `.goreleaser.yaml`:
  ```yaml
  builds:
    - goos: [linux]
      goarch: [amd64]
  ```
  One platform — strictly equivalent to `go build`. No cross-platform value, satisfies the schema but not the signal.
- A `release.yml` matrix with three OSes that all run `cargo build --release` (no `--target`) and upload `target/release/<bin>` — produces three host-arch binaries, none of which are cross-compiled, and none labelled correctly.
- `docker buildx build --platform linux/amd64,linux/arm64 -t repo:latest .` with no `--push` and no `--load` — buildx exits successfully but the image is discarded; nothing ships.
- A Makefile target `cross:` that runs `GOOS=darwin go build` but omits `GOARCH`, defaulting to the host arch — produces `darwin_amd64` on an amd64 runner and `darwin_arm64` on an M-series runner, with no way to ship both.
- Setting `platforms: linux/amd64,linux/arm64,linux/arm/v7,linux/ppc64le,linux/s390x` on a Node web app whose users run x86 servers — wastes 10+ minutes per build for zero user value.

Examples of GOOD fixes:

- For a Go CLI, drop in a `.goreleaser.yaml` and wire it to a tag-triggered release workflow:
  ```yaml
  # .goreleaser.yaml
  version: 2
  before:
    hooks:
      - go mod tidy
  builds:
    - id: <BINARY_NAME>
      binary: <BINARY_NAME>
      env: [CGO_ENABLED=0]
      goos: [linux, darwin, windows]
      goarch: [amd64, arm64]
      ignore:
        - { goos: windows, goarch: arm64 } # not tested upstream yet
      ldflags:
        - -s -w -X main.version={{.Version}} -X main.commit={{.ShortCommit}}
  archives:
    - id: default
      formats: [tar.gz]
      format_overrides:
        - { goos: windows, formats: [zip] }
      name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
  checksum:
    name_template: "checksums.txt"
  ```
  ```yaml
  # .github/workflows/release.yml
  on:
    push:
      tags: ['v*.*.*']
  permissions: { contents: write }
  jobs:
    goreleaser:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
          with: { fetch-depth: 0 }
        - uses: actions/setup-go@v5
          with: { go-version: stable }
        - uses: goreleaser/goreleaser-action@v6
          with: { distribution: goreleaser, version: '~> v2', args: release --clean }
          env: { GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }} }
  ```
  Five binaries (3 OS × 2 arch − 1 ignore) plus checksums, signed and uploaded to the GitHub release, all from one `ubuntu-latest` runner.

- For a Rust CLI, use a release matrix with explicit targets and the `cross` helper for foreign-libc tuples:
  ```yaml
  # .github/workflows/release.yml
  on: { push: { tags: ['v*.*.*'] } }
  permissions: { contents: write }
  jobs:
    build:
      runs-on: ${{ matrix.os }}
      strategy:
        fail-fast: false
        matrix:
          include:
            - { os: ubuntu-latest,    target: x86_64-unknown-linux-gnu,    use-cross: false }
            - { os: ubuntu-latest,    target: aarch64-unknown-linux-gnu,   use-cross: true  }
            - { os: ubuntu-latest,    target: x86_64-unknown-linux-musl,   use-cross: true  }
            - { os: macos-latest,     target: aarch64-apple-darwin,        use-cross: false }
            - { os: macos-13,         target: x86_64-apple-darwin,         use-cross: false }
            - { os: windows-latest,   target: x86_64-pc-windows-msvc,      use-cross: false }
      steps:
        - uses: actions/checkout@v4
        - uses: dtolnay/rust-toolchain@stable
          with: { targets: ${{ matrix.target }} }
        - uses: taiki-e/upload-rust-binary-action@v1
          with:
            bin: <BINARY_NAME>
            target: ${{ matrix.target }}
            tar: unix
            zip: windows
            token: ${{ secrets.GITHUB_TOKEN }}
  ```
  Each matrix entry produces a native binary for the named target (cross-compiled via `cross` for the non-host Linux tuples) and uploads it to the release.

- For a container image, build a true multi-arch manifest using native arm64 runners (no QEMU):
  ```yaml
  # .github/workflows/image.yml
  on:
    push:
      tags: ['v*.*.*']
  permissions: { contents: read, packages: write }
  jobs:
    image:
      strategy:
        fail-fast: false
        matrix:
          include:
            - { os: ubuntu-latest,     platform: linux/amd64, suffix: amd64 }
            - { os: ubuntu-24.04-arm,  platform: linux/arm64, suffix: arm64 }
      runs-on: ${{ matrix.os }}
      steps:
        - uses: actions/checkout@v4
        - uses: docker/setup-buildx-action@v3
        - uses: docker/login-action@v3
          with:
            registry: ghcr.io
            username: ${{ github.actor }}
            password: ${{ secrets.GITHUB_TOKEN }}
        - uses: docker/build-push-action@v6
          with:
            context: .
            platforms: ${{ matrix.platform }}
            push: true
            tags: ghcr.io/<OWNER>/<IMAGE>:${{ github.ref_name }}-${{ matrix.suffix }}
    manifest:
      needs: image
      runs-on: ubuntu-latest
      steps:
        - uses: docker/setup-buildx-action@v3
        - uses: docker/login-action@v3
          with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
        - run: |
            docker buildx imagetools create \
              -t ghcr.io/<OWNER>/<IMAGE>:${{ github.ref_name }} \
              ghcr.io/<OWNER>/<IMAGE>:${{ github.ref_name }}-amd64 \
              ghcr.io/<OWNER>/<IMAGE>:${{ github.ref_name }}-arm64
  ```
  Each arch builds on its own native runner (no QEMU emulation), then a single manifest tag is assembled. `docker pull ghcr.io/<OWNER>/<IMAGE>:<tag>` from either arch gets the right layer.

- For a Go binary cross-compiled with cgo (sqlite, libpq) using `zig cc`:
  ```bash
  # scripts/cross.sh
  set -euo pipefail
  mkdir -p dist
  for tuple in linux/amd64 linux/arm64 darwin/arm64; do
    GOOS=${tuple%/*} GOARCH=${tuple#*/} \
    CGO_ENABLED=1 \
    CC="zig cc -target ${tuple#*/}-${tuple%/*}-gnu" \
    go build -trimpath -ldflags="-s -w" \
      -o "dist/<BINARY_NAME>_${tuple%/*}_${tuple#*/}" .
  done
  ```

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase

## References

- GoReleaser builds & cross-compilation: https://goreleaser.com/customization/builds/go/
- GoReleaser GitHub Action: https://github.com/goreleaser/goreleaser-action
- Go cross-compilation (`GOOS`/`GOARCH` value table): https://go.dev/doc/install/source#environment
- Rust `--target` and `rustup target add`: https://doc.rust-lang.org/cargo/commands/cargo-build.html
- `cross` for Rust foreign-libc cross-compilation: https://github.com/cross-rs/cross
- `cargo-dist` (multi-platform Rust release tooling): https://opensource.axo.dev/cargo-dist/
- `taiki-e/upload-rust-binary-action`: https://github.com/taiki-e/upload-rust-binary-action
- Docker buildx multi-platform builds: https://docs.docker.com/build/building/multi-platform/
- `docker/build-push-action` (multi-arch usage): https://github.com/docker/build-push-action#examples
- `docker buildx imagetools create` (manifest assembly): https://docs.docker.com/reference/cli/docker/buildx/imagetools/create/
- GitHub-hosted ARM64 Linux runners (`ubuntu-22.04-arm`, `ubuntu-24.04-arm`): https://github.blog/changelog/2025-01-16-linux-arm64-hosted-runners-now-available-for-free-in-public-repositories-public-preview/
- Zig as a cross C compiler (`zig cc -target`): https://andrewkelley.me/post/zig-cc-powerful-drop-in-replacement-gcc-clang.html
- Dockerfile `BUILDPLATFORM`/`TARGETPLATFORM` cross-build pattern: https://docs.docker.com/build/building/multi-platform/#cross-compilation
</system-reminder>
