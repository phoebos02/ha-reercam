# Implementation Plan

This is the persistent implementation plan for `architecture-v2.md`. Keep it
updated whenever a step starts, is verified, changes scope, or gains findings.
GitHub Issues are the authoritative findings tracker and session-recovery
record.

## Process

The coordinator follows `codex-prompt-v2.md`:

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

- Final `0.1.0` implementation commit:
  `38c7db887f2e1db91543295c9aef77eab808e730`; `main` may contain later
  plan-only tracking commits.
- `v0.1.0-alpha.5` is published from
  `db4e78c1e6231321984b0cd965caea23a66fd712`, eleven commits before the final
  `0.1.0` implementation.
- Final `v0.1.0` is published from `38c7db8`, installed through HACS, and
  physically verified `PASS` by the user.
- Step 6's final simplification commit is pushed; Test, HACS, and Hassfest all
  pass.
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
- GitHub milestones represent intended release versions; issues represent
  deliverables, not internal engineering steps. Active milestones are `0.2.0`,
  `0.2.1`, and `0.3.0`.
- An issue's milestone records the intended delivery version. Release notes
  remain the definitive record of what actually shipped.
- After every independently verified engineering step, the Coordinator
  reconciles GitHub Issues: close resolved deliverables, create any new
  findings, assign their intended milestones, and confirm no work is tracked
  only in `PLAN.md`. Open issues for later steps are expected at this point.
- Full milestone gates additionally happen at releases: the Engineer reports
  milestone state at candidate handoff, the independent Verifier checks it
  before release PASS, and the Coordinator queries GitHub again immediately
  before every tag or publication.
- Before a release candidate, every implementation issue for that milestone
  must be closed; only the release-and-physical-verification issue may remain
  open. After final publication, close that issue, confirm zero open issues,
  and close the milestone. Any deliberate deferral must first be moved to a
  later milestone with an explanatory comment.

## Active plan

Step 9 release-candidate preparation is active. Architecture v2.1 schedules
the narrow `0.2.1` Camera access release after final `0.2.0` and before any
`0.3.0` implementation; the completed sound proof remains future architecture
evidence only.

**Roadmap:** `0.2.0` is the current baseline; `0.2.1` adds Camera access;
`0.3.0` adds audio with a separate Audio switch.

### Parallel future architecture track — 0.3.0 sound

**Status:** `started`

**Latest result:** The Architect completed the options memo. The preferred
path is one-way listening through the existing ASF camera stream with no
runtime code if the physical stream contains active Home Assistant-compatible
AAC or MP3 audio. Physical stream characterization and a user architecture
decision are required before writing architecture v3. The user approved this
scope: prefer zero code, permit one optional user-operated restream only if
physical evidence proves it necessary, and exclude two-way talkback. The
physical probe is implemented as `camera-audio-probe.py` with ignored local
`camera.txt` and passed Architect review. Its sanitized result proves the ASF
source contains active H.264 Main
video and active 8 kHz mono `adpcm_ima_wav` audio at 32 kbit/s (453 audio
packets in 15 seconds). Because that codec is outside Home Assistant's native
AAC/MP3 remux path, a password-safe ADPCM-to-AAC playback experiment was run:
the pipeline passed technically, and the user physically confirmed audible,
continuous audio for the full 15-second run. Physical playback is `PASS`.

**Goal:** Produce a decision-ready architecture-v3 proposal for adding sound,
preferring one-way audio through the existing camera stream and documenting
alternatives if physical stream evidence or Home Assistant compatibility makes
that non-trivial.

**Sequence gate:** Research and architecture may continue in parallel, but no
`0.3.0` implementation begins until final `0.2.1` below is physically verified.

**Tracked finding:** #17 Design one-way sound support.

### Scheduled architecture-v2.1 track — 0.2.1 Camera access

**Status:** `not started`

**Latest result:** `architecture-v2.1.md` defines one persisted native Camera
access switch. Off blocks new snapshots and streams and terminates active Home
Assistant media, but it explicitly makes no physical sensor, power, vendor-app,
cloud, or microphone privacy claim. No camera write endpoint is authorized.
The future Audio switch remains separate, subordinate to Camera access, and
entirely outside `0.2.1`.

**Goal:** Add the smallest native Home Assistant control for stopping and
resuming this integration's camera/video and snapshot access, with exact and
testable privacy semantics.

**Sequence gate:** Start only after final `0.2.0` ships. Complete and physically
verify final `0.2.1` before any `0.3.0` implementation begins.

**Outside this track:** Guessed or unverified camera write commands, claims of
physical camera privacy, audio playback/transcoding, an Audio switch, talkback,
new runtime dependencies, polling, and speculative abstractions.

**Tracked deliverables:** #21 Specify Camera access control architecture,
#20 Add Camera access control, and #22 Release and physically verify Camera
access.

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

**Status:** `verified`

**Latest result:** Commit `ea5a6e2` contains the complete Engineer and coverage
correction passes. The fresh GitHub Test workflow installs Python 3.14.2 and
the pinned Home Assistant 2026.8.3 environment; Test, HACS, and Hassfest all
pass. Final independent reverification returned `PASS` with no findings or
unverified items. By user direction, the Engineer then applied all six
optional Ponytail test simplifications, and a focused follow-up now proves the
HTTP status-to-exception mapping explicitly. The final independent Verifier
returned `PASS` with no findings: all 26 tests, Ruff, dependency and repository
checks pass, the test/dependency diff remains 33 lines smaller, and no
production or CI files changed. Commit `c130822` is pushed; Test, HACS, and
Hassfest all pass. The user accepted the result and directed the plan to
advance.

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

**Status:** `verified`

**Latest result:** Activated by user direction after Step 6 was committed,
pushed, independently verified, and passed Test, HACS, and Hassfest. Release
preparation is committed and pushed as `44422a5`: the manifest and README say
`0.1.0-rc.1`, the independent Verifier returned `PASS`, and Test, HACS, and
Hassfest pass on the exact candidate. Prerelease `v0.1.0-rc.1` is published and
installed. The user reports all physical verification checks 1–8 passed:
installation visibility, setup, identity/firmware, snapshot/stream, reload,
restart, unload/disable, and deletion cleanup. By explicit user direction,
manual secret-log inspection and a separate sanitized-result artifact were
skipped and remain recorded as unverified rather than passed. The user accepted
the release-candidate result. Final promotion is committed and pushed as
`38c7db8`: the manifest and README say `0.1.0`, the independent Verifier
returned `PASS`, and Test, HACS, and Hassfest pass on the exact final
candidate. Final `v0.1.0` is now published, installed through
HACS, and reported `PASS` by the user. Manual secret-log inspection and a
separate sanitized-result artifact remain explicitly waived/unverified. The
paused `0.2.0` work remains isolated in `stash@{0}`.

**Goal:** Release the tested current functional scope as `0.1.0` before work
begins on the next SemVer line.

**Work already completed:** Steps 6a and 6 provide a clean repository, real
Home Assistant tests, static checks, HACS validation, and Hassfest validation.

**Outside this step:** Configuration validation, duplicate prevention,
reauthentication, reconfiguration, branding, and the `0.2.0` line.

**Acceptance criteria:**

- Manifest and release notes accurately describe the implemented scope and its
  known limitations.
- The release-candidate manifest/README version is `0.1.0-rc.1` and its Git tag
  is `v0.1.0-rc.1`; the manifest never includes the tag's `v` prefix.
- Release only a clean, pushed commit with all checks passing.
- Obtain explicit user approval before creating/pushing the `v0.1.0` tag or
  publishing the GitHub release.
- Persist a sanitized HACS and physical-camera smoke-test result for setup,
  snapshot, stream, reload/restart, unload/delete, and secret-free logs.

**Tracked finding:** [#10 Record HACS and physical-camera verification](https://github.com/phoebos02/ha-reercam/issues/10).

### Step 7 — Complete config-entry lifecycle for 0.2.0

**Status:** `verified`

**Latest result:** Started by explicit user direction after the verified Step 6
implementation was committed and pushed. The Engineer is implementing only
architecture sections 12–15, 19, and their section 20 coverage; Step 8 remains
outside this pass. After final `0.1.0` release and approval of the parallel
sound scope, the Engineer is restoring the preserved `stash@{0}` WIP and
resuming Step 7. The Engineer completed the seven-file lifecycle diff: 50 tests
and all local checks pass, with the original stash retained. The independent
Verifier returned `PASS` with no findings; the only forward note is to recheck
Home Assistant's warned reload-helper behavior before supporting 2026.12.
The pushed commit's Test, HACS, and Hassfest workflows subsequently passed.
Commit `0d9b557` is pushed, and the user accepted the result and directed work
to move immediately to Step 8. Test, HACS, and Hassfest on the pushed commit
are pending background confirmation.

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

**Status:** `verified`

**Latest result:** Started immediately after the independently verified Step 7
commit was pushed, by prior user direction. The Engineer completed the README
and architecture coverage audit, then replaced the deprecated reload behavior
with the minimum listener/no-listener helper split required for Home Assistant
2026.12 compatibility. The first Verifier pass found the no-listener
reauthentication regression; the focused correction restored it. The second
independent Verifier returned `PASS`: 52 tests, Ruff, dependency, compilation,
and diff checks pass, with changed data reloading once and unchanged data zero
times. The user directed us to create original rights-cleared local brand artwork.
Original transparent 256×256 and 512×512 camera/moon icons were added locally
without vendor artwork, the HACS brand ignore was removed, and independent
verification returned `PASS` with 52 tests and all local checks green. Commits
`d3f9658`, `23eeaa6`, `428dba9`, and `7c0f9c5` are pushed. Test, HACS
including brand validation, and Hassfest pass on the exact branding commit.
The user directed work to advance immediately to Step 9.

**Goal:** Finish documentation, branding, and any remaining architecture-v2
acceptance work for the `0.2.0` line.

**Work already completed:** Steps 6 and 7 provide the real test suite and the
complete implementation behavior.

**Outside this step:** Functionality excluded by architecture section 2 and
release publication.

**Acceptance criteria:**

- Use `Home Assistant integration for reer IP BabyCam` as the
  repository-facing title in the README and GitHub repository description;
  retain `reer IP BabyCam` for the Home Assistant and HACS integration name.
- README covers all fourteen requirements in architecture section 22 and only
  documents implemented behavior.
- Clearly disclose that the camera protocol sends authenticated media over
  plain HTTP on the local network.
- Create original, rights-cleared local brand icons without copied vendor
  artwork, text, or trademarked logo elements. Add transparent 256×256 and
  512×512 PNG assets and remove HACS `ignore: brands` only after validation.
- Close any remaining architecture section 20 coverage gaps.
- All tests, lint/static checks, HACS validation, and Hassfest validation pass.
- The independent Verifier checks the full architecture, repository, tests,
  CI, security properties, and acceptance criteria.
- No required criterion remains missing, partial, or supported only by an
  unstated assumption.
- GitHub Issues record every resolution or deliberate deferral.

**Tracked deliverables:** #8 Complete real Home Assistant lifecycle coverage,
#9 Complete architecture-v2 README, #11 Add Home Assistant brand assets,
#18 Use Home Assistant-compatible config entry reloads, and #19 Release and
physically verify architecture v2.

### Step 9 — 0.2.0 prerelease and physical verification

**Status:** `started`

**Latest result:** Started immediately after the independently verified
branding commit was pushed, without waiting for its queued workflows by prior
user direction. The Engineer is preparing only the `0.2.0-rc` candidate and
release handoff; tags and releases remain subject to explicit user approval.

**Goal:** Distribute and physically verify the architecture-complete `0.2.0`
candidate.

**Work already completed:** Step 7a established the final-release path; Step 8
completed architecture acceptance.

**Outside this step:** Final `0.2.0` promotion and new features.

**Acceptance criteria:**

- Use manifest version `0.2.0-rc`, future tag `v0.2.0-rc`, and release title
  `Home Assistant integration for reer IP BabyCam 0.2.0-rc`; prepare accurate
  release notes without committing a redundant notes file.
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

### Step 10a — Implement and verify architecture v2.1 for 0.2.1

**Status:** `not started`

**Goal:** Implement the native Camera access switch from
`architecture-v2.1.md` while preserving the final `0.2.0` behavior and the
architecture-v2 security boundary.

**Work already completed:** Final `0.2.0` is the required baseline;
`architecture-v2.1.md` specifies the privacy semantics, minimal state model,
media cleanup, future audio boundary, and evidence gate.

**Outside this step:** Release publication, camera-side write commands,
physical sensor/power privacy claims, audio behavior or entities, talkback,
new runtime dependencies, polling, and unrelated refactoring.

**Acceptance criteria:**

- Add one persisted Camera access switch on the camera device; existing
  entries default to on.
- Off makes no new snapshot request and returns no stream source or
  credential-bearing media URL.
- Off explicitly terminates active Home Assistant HLS/recording/WebRTC media
  rather than waiting for an idle timeout.
- Off survives reload and restart; on restores normal operation without a
  proactive camera request.
- State updates use the existing config-entry lifecycle and cause exactly one
  reload, with no new storage/coordinator/dispatcher/dependency.
- UI text, README, and tests state that this controls only the integration's
  access and does not claim to disable physical capture or other clients.
- No Audio entity, audio option, transcoder, or speculative camera command is
  introduced.
- Existing checks and the minimum tests in architecture-v2.1 section 10 pass.
- An independent Verifier passes and the user agrees the implementation is
  complete.

### Step 10b — Release and physically verify 0.2.1

**Status:** `not started`

**Goal:** Release the verified Camera access change as `0.2.1` and prove its
limited, documented behavior on the physical camera through HACS.

**Work already completed:** Step 10a provides the independently verified
implementation and automated coverage.

**Outside this step:** Expanding the privacy claim, camera-side write research,
and all `0.3.0` audio implementation.

**Acceptance criteria:**

- Manifest, README, and release notes use `0.2.1` and accurately describe
  Camera access as integration-local control.
- Release only a clean, pushed, independently verified commit with all
  automated checks passing.
- Obtain explicit user approval before creating/pushing a tag or publishing a
  release.
- Install through HACS and prove that off blocks new snapshots and streams,
  stops an already active Home Assistant stream, and survives reload/restart.
- Prove that on restores snapshots and streaming.
- Confirm logs contain no secret, Digest material, or credential URL and
  persist a sanitized physical-verification result.
- Complete final `0.2.1` before allowing any `0.3.0` implementation to begin.

**Tracked deliverable:** #22 Release and physically verify Camera access.

### Step 11 — Complete and verify architecture v3 for 0.3.0

**Status:** `not started`

**Goal:** Turn the successful physical sound experiment into a standalone,
decision-complete architecture for one-way audio and a separate Audio switch.

**Work already completed:** The camera exposes active mono 8 kHz ADPCM audio
on the existing ASF stream. The password-safe ADPCM-to-AAC pipeline passed,
and the user confirmed audible, continuous playback for 15 seconds.

**Outside this step:** Production audio code, two-way talkback, cloud/P2P,
camera write commands, and implementation before final `0.2.1`.

**Acceptance criteria:**

- Select one optional user-operated restream mechanism that copies H.264 and
  converts only ADPCM audio.
- Prove Home Assistant HLS or WebRTC playback and record basic latency and CPU
  observations.
- Specify installation, configuration, credentials, failure, restart, update,
  and removal behavior without storing media.
- Define the separate Audio switch and its subordinate relationship to Camera
  access.
- Produce `architecture-v3.md`, obtain independent verification, and obtain
  user approval before implementation.

**Tracked deliverable:** #17 Design one-way sound support.

### Step 12 — Implement and verify sound support for 0.3.0

**Status:** `not started`

**Goal:** Implement only the approved architecture-v3 one-way audio path and
Audio access control on top of final `0.2.1`.

**Acceptance criteria:**

- Preserve copied H.264 video and convert only the camera's ADPCM audio.
- Keep all media local and prevent credentials from appearing in entities,
  process arguments, logs, diagnostics, or stored media.
- Audio can be disabled independently while Camera access remains the master
  media control.
- Existing camera behavior and all architecture-v3 tests pass.
- An independent Verifier passes before release work begins.

**Tracked deliverables:** #23 Add optional one-way audio restream and #24 Add
separate Audio access control.

### Step 13 — Release and physically verify 0.3.0

**Status:** `not started`

**Goal:** Publish a release candidate, verify sound and privacy controls through
HACS on the physical camera, and then publish final `0.3.0` after acceptance.

**Acceptance criteria:**

- Exact release commits pass Test, HACS, Hassfest, and independent verification.
- HLS or WebRTC delivers audible, continuous audio with acceptable observed
  latency and CPU use.
- Camera access and Audio switches behave as documented across reload/restart.
- Logs remain secret-safe, the user accepts the physical result, and explicit
  approval is obtained before tags or releases are published.

**Tracked deliverable:** #25 Release and physically verify sound support.
