# Implementation Plan

This is the persistent implementation plan for `architecture-v2.md`. Keep it
updated whenever a step starts, is verified, changes scope, or gains findings.
GitHub Issues are the authoritative findings tracker and session-recovery
record.

## Process

The coordinator follows `codex-prompt-v1.md`:

1. Agree the plan with the user before implementation.
2. Set exactly one step to `started`.
3. Give one Engineer the step's complete goal, existing work, exclusions, and
   acceptance criteria.
4. Give one independent Verifier the architecture, Engineer prompt, report,
   and resulting repository state.
5. Present the result and findings to the user, and update their GitHub Issues.
6. Mark the step `verified` only after a Verifier pass and user agreement.

In user-facing output, render a GitHub finding as plain text containing its
number followed by its title, for example `#2 Finish repository cleanup
verification`; never show a bare number, URL, or hyperlink.

Allowed statuses are `not started`, `started`, and `verified`.

## Recovered baseline

As of 2026-08-23:

- Current `main`: `ea5a6e21e5ca6f89e85ef19456edcfc9bf9e5006`.
- `v0.1.0-alpha.5` is published from
  `db4e78c1e6231321984b0cd965caea23a66fd712`, eight commits behind `main`.
- Current `main` passes Test, Hassfest, and HACS workflows.
- Step 6 replaces the hand-written stubs with 26 tests against Python 3.14.2,
  Home Assistant 2026.8.3, and real aiohttp/yarl; pytest and Ruff pass.
- Alpha.5 implements the narrow HTTP client, runtime setup, one device, one
  camera entity, snapshots, and streaming.
- Configuration validation, config-entry identity, duplicate prevention,
  reauthentication, reconfiguration, complete tests, and complete
  documentation remain unfinished.
- Historical Engineer/Verifier reports were not persisted, so prior work is
  evidence-backed but cannot be retroactively marked `verified` under the
  coordinator protocol.

## Version policy

By user decision on 2026-08-22:

- Step 7a releases the tested current scope as `0.1.0` with its remaining
  limitations stated explicitly.
- Steps 7–10 use the `0.2.0` SemVer line.
- Full architecture-v2 acceptance moves to `0.2.0`; this deliberately
  supersedes the architecture document's original `0.1.0` completion label
  without changing its required behavior or scope boundaries.

## Repository and release policy

- Pull-request workflow triggers remain YAGNI until the repository actually
  uses pull requests.
- Published release tags are immutable: never move or reuse an existing tag.

## Active plan

Step 6 is active. Steps must run in the order below.

### Step 6a — Quick repository and release cleanup

**Status:** `verified`

**Latest result:** Commit `6b898b8` retains and fixes the Release badge,
changes HACS Default to HACS Custom, and follows deletion of the remaining
local alpha.3 tag. Test, Hassfest, and HACS pass on the pushed commit. The final
independent Verifier returned `PASS` with no findings or unverified items; the
user directed work to proceed to Step 6. The completed finding is [#2 Finish
repository cleanup verification](https://github.com/phoebos02/ha-reercam/issues/2).

**Goal:** Resolve the small repository and release-history problems before
establishing the new test baseline.

**Work already completed:** Test, HACS, and Hassfest workflows exist and pass
on current `main`; alpha.5 is published, while the mislabeled public alpha.3
release and remote tag have been deleted.

**Outside this step:** New integration behavior, test-harness replacement,
full README completion, tooling configuration, and new releases.

**Acceptance criteria:**

- [x] Keep `test.yml` for per-check reporting and remove duplicate `ci.yml`.
- [x] README no longer falsely describes the integration as an empty
  placeholder.
- [x] User explicitly accepted the expanded README scope.
- [x] Retain the Release badge as explicitly requested while making its
  prerelease presentation and target accurate.
- [x] Remove the inaccurate HACS Default claim; retain an accurate custom-HACS
  presentation if useful.
- [x] Delete stale alpha.5-specific `Release.md`; GitHub remains the release
  record and this plan owns future release gates.
- [x] Remove unrelated `.vscode/settings.json`.
- [x] Inspect the exact remote alpha.3 release and tag before changing either.
- [x] Delete the mislabeled public alpha.3 release and remote tag after final,
  explicit user approval.
- [x] Delete the remaining local `v0.1.0-alpha.3` tag.
- [x] Local checks pass; retained GitHub workflows pass against the committed
  cleanup.
- [x] Local checks pass against the current badge correction.
- [x] Retained GitHub workflows pass against the committed badge correction.
- [x] Independent Verifier passes and the user agrees the step is complete.

**Tracked finding:** [#2 Finish repository cleanup verification](https://github.com/phoebos02/ha-reercam/issues/2).

**Resolved findings:** [#12 Remove duplicate CI workflow](https://github.com/phoebos02/ha-reercam/issues/12),
[#13 Remove stale alpha.5 release notes file](https://github.com/phoebos02/ha-reercam/issues/13), and
[#14 Remove unrelated VS Code command approval settings](https://github.com/phoebos02/ha-reercam/issues/14).

### Step 6 — Real Home Assistant 2026.8 test baseline

**Status:** `started`

**Latest result:** Commit `ea5a6e2` contains the complete Engineer and coverage
correction passes. The fresh GitHub Test workflow installs Python 3.14.2 and
the pinned Home Assistant 2026.8.3 environment; Test, HACS, and Hassfest all
pass. Final independent reverification returned `PASS` with no findings or
unverified items. By user direction, the Engineer then applied all six
optional Ponytail test simplifications, and a focused follow-up now proves the
HTTP status-to-exception mapping explicitly. The final independent Verifier
returned `PASS` with no findings: all 26 tests, Ruff, dependency and repository
checks pass, the test/dependency diff remains 33 lines smaller, and no
production or CI files changed. The result is ready to commit; post-push Test,
HACS, and Hassfest evidence is still required before Step 6 acceptance.

**Goal:** Verify the existing alpha.5 behavior against Home Assistant 2026.8
and establish the complete minimal test, lint, and CI foundation.

**Work already completed:** Narrow client, CGI parser, error types, runtime
data, entity, and stub-based runnable checks.

**Outside this step:** Configuration-time validation, config-entry identity,
reauthentication, reconfiguration, branding, and documentation expansion.

**Acceptance criteria:**

- Add the minimum reproducible development/test configuration required by the
  target Home Assistant version.
- Existing API, setup, device, snapshot, and stream behavior runs against the
  real Home Assistant test surface and real aiohttp/yarl APIs.
- Replace bespoke module stubs rather than retaining two test systems.
- Cover the existing API and camera requirements from architecture section 20,
  including a real Digest exchange and secret-leak checks.
- Add the smallest useful Ruff gate.
- Pin third-party GitHub Actions to full commit SHAs and use GitHub-native
  Dependabot updates for the `github-actions` ecosystem.
- Fix only compatibility defects in already-implemented scope.
- Tests, Ruff, HACS validation, and Hassfest validation pass.

**Tracked findings:** [#3 Establish a real Home Assistant test environment](https://github.com/phoebos02/ha-reercam/issues/3),
[#4 Complete real API and camera coverage](https://github.com/phoebos02/ha-reercam/issues/4), and
[#5 Add minimal static and reproducible CI checks](https://github.com/phoebos02/ha-reercam/issues/5).

### Step 7a — Release 0.1.0

**Status:** `not started`

**Goal:** Release the tested current functional scope as `0.1.0` before work
begins on the next SemVer line.

**Work already completed:** Steps 6a and 6 provide a clean repository, real
Home Assistant tests, static checks, HACS validation, and Hassfest validation.

**Outside this step:** Configuration validation, duplicate prevention,
reauthentication, reconfiguration, branding, and the `0.2.0` line.

**Acceptance criteria:**

- Manifest and release notes accurately describe the implemented scope and its
  known limitations.
- Release only a clean, pushed commit with all checks passing.
- Obtain explicit user approval before creating/pushing the `v0.1.0` tag or
  publishing the GitHub release.
- Persist a sanitized HACS and physical-camera smoke-test result for setup,
  snapshot, stream, reload/restart, unload/delete, and secret-free logs.

**Tracked finding:** [#10 Record HACS and physical-camera verification](https://github.com/phoebos02/ha-reercam/issues/10).

### Step 7 — Complete config-entry lifecycle for 0.2.0

**Status:** `not started`

**Goal:** Start the `0.2.0` SemVer line and implement architecture sections
12–15 as one cohesive config-entry lifecycle change.

**Work already completed:** Host/password form, protocol client, camera
information lookup, setup retry behavior, unload, and the real test foundation.

**Outside this step:** Branding, full README completion, prerelease
publication, and functionality excluded by architecture section 2.

**Acceptance criteria:**

- Move the manifest to the agreed `0.2.0` development/prerelease version.
- Normalize and validate host input before creating an entry.
- Require the camera ID as config-entry unique ID and prevent duplicates.
- Map config-flow errors without exposing secrets or raw responses.
- Setup verifies that the fetched camera ID equals the config-entry unique ID.
- Authentication failure starts Home Assistant reauthentication with
  `ConfigEntryAuthFailed`.
- Reauthentication accepts only a new password for the same camera, updates
  stored data, and reloads exactly once.
- Reconfiguration accepts only a new host resolving to the same camera,
  updates stored data, and reloads exactly once.
- A different physical camera is rejected in both flows.
- Register the architecture-required update listener and pair it with the
  current non-double-reload flow update helper.
- Complete errors, steps, and abort translations in both translation files.
- Real Home Assistant tests cover every config-flow case in architecture
  section 20.2 and the affected lifecycle/camera paths.

**Tracked findings:** [#6 Validate config flow and enforce camera identity](https://github.com/phoebos02/ha-reercam/issues/6),
[#7 Complete setup, reauthentication, and reconfiguration](https://github.com/phoebos02/ha-reercam/issues/7), and
[#8 Complete real Home Assistant lifecycle coverage](https://github.com/phoebos02/ha-reercam/issues/8).

### Step 8 — 0.2.0 release readiness and branding

**Status:** `not started`

**Goal:** Finish documentation, branding, and any remaining architecture-v2
acceptance work for the `0.2.0` line.

**Work already completed:** Steps 6 and 7 provide the real test suite and the
complete implementation behavior.

**Outside this step:** Functionality excluded by architecture section 2 and
release publication.

**Acceptance criteria:**

- README covers all fourteen requirements in architecture section 22 and only
  documents implemented behavior.
- Clearly disclose that the camera protocol sends authenticated media over
  plain HTTP on the local network.
- Add the required brand assets through the Home Assistant brands process and
  remove HACS `ignore: brands` once the assets are available. Obtain explicit
  user approval before opening any external pull request.
- Close any remaining architecture section 20 coverage gaps.
- All tests, lint/static checks, HACS validation, and Hassfest validation pass.
- The independent Verifier checks the full architecture, repository, tests,
  CI, security properties, and acceptance criteria.
- No required criterion remains missing, partial, or supported only by an
  unstated assumption.
- GitHub Issues record every resolution or deliberate deferral.

**Tracked findings:** [#8 Complete real Home Assistant lifecycle coverage](https://github.com/phoebos02/ha-reercam/issues/8),
[#9 Complete architecture-v2 README](https://github.com/phoebos02/ha-reercam/issues/9), and
[#11 Add Home Assistant brand assets](https://github.com/phoebos02/ha-reercam/issues/11).

### Step 9 — 0.2.0 prerelease and physical verification

**Status:** `not started`

**Goal:** Distribute and physically verify the architecture-complete `0.2.0`
candidate.

**Work already completed:** Step 7a established the final-release path; Step 8
completed architecture acceptance.

**Outside this step:** Final `0.2.0` promotion and new features.

**Acceptance criteria:**

- Use the agreed `0.2.0` prerelease version and prepare accurate release notes.
- Release only a clean, pushed commit with all automated checks passing.
- Obtain explicit user approval before creating/pushing the tag or publishing
  the release.
- Install through HACS and verify setup, identity, metadata, snapshot, live
  stream, reload/restart, unload/delete, and secret-free logs on the physical
  camera.
- Persist a sanitized manual verification result.

**Tracked finding:** [#10 Record HACS and physical-camera verification](https://github.com/phoebos02/ha-reercam/issues/10).

### Step 10 — Final 0.2.0 release

**Status:** `not started`

**Goal:** Promote the physically verified candidate to the final `0.2.0`
version that completes architecture v2.

**Work already completed:** All implementation and verification from Steps
6a–9.

**Outside this step:** Every feature excluded by architecture section 2.

**Acceptance criteria:**

- Update manifest and documentation to `0.2.0`.
- Repeat all automated and release checks on a clean pushed commit.
- Obtain an independent Verifier pass and user agreement.
- Obtain explicit user approval before creating/pushing the final tag or
  publishing the GitHub release.
