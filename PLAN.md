# Implementation Plan

Persistent execution state for this repository. The coordinator follows
`codex-prompt-v2.md`; GitHub Issues are the deliverable/finding ledger, and
GitHub milestones are the intended release versions.

Allowed statuses: `not started` → `started` → `verified`.

## Roadmap

Pull-request triggers remain YAGNI until the repository uses pull requests.

Roadmap:

1. `0.2.0`: complete architecture v2 and release it.
2. `0.2.1`: add and physically verify Camera access.
3. `0.3.0`: add and physically verify one-way audio and Audio access.

## Verified history

- **Step 6a — Repository cleanup:** `6b898b8`; Test, HACS, and Hassfest pass.
- **Step 6 — Real Home Assistant baseline:** `ea5a6e2` and `c130822`; Python
  3.14.2, Home Assistant 2026.8.3, real aiohttp/yarl, 26 tests, Ruff, HACS, and
  Hassfest pass.
- **Step 7a — Release 0.1.0:** final implementation `38c7db8`; `v0.1.0` is
  published, installed through HACS, and physically verified PASS.
- **Step 7 — Config-entry lifecycle:** `0d9b557`; validation, identity,
  duplicate prevention, setup, reauthentication, reconfiguration, and real
  Home Assistant coverage pass.
- **Step 8 — 0.2.0 readiness:** `d3f9658`, `23eeaa6`, `428dba9`, and `7c0f9c5`;
  README, Home Assistant 2026.12-compatible reload behavior, 52 tests, media
  probes, v2.1 roadmap, original local branding, Test, HACS, and Hassfest pass.

Git history and closed GitHub Issues are the detailed record for completed
steps; their former acceptance checklists are intentionally not duplicated.

## Active work

### Step 9 — 0.2.0 release candidate and physical verification

**Status:** `started`

**Latest result:** The Engineer prepared manifest/README version `0.2.0-rc` and
then resolved the newly opened README simplification request by removing
duplicate Scope, stream, lifecycle, and manual-HACS text while preserving all
fourteen architecture-v2 documentation requirements. Independent verification
and the final milestone audit are pending. No tag or release exists.

**Goal:** Publish and physically verify the architecture-v2 release candidate.

**Outside:** Final `0.2.0`, Camera access, audio, and unrelated refactoring.

**Acceptance criteria:**

- Manifest and README use `0.2.0-rc`; future tag is `v0.2.0-rc`; release title
  is `Home Assistant integration for reer IP BabyCam 0.2.0-rc` and type is
  prerelease.
- README remains concise while covering the fourteen architecture-v2 topics,
  security warning, release badge, and implemented behavior.
- Full local checks and exact-commit Test, HACS, and Hassfest pass.
- Milestone `0.2.0` has no open implementation issue; only the release issue
  may remain.
- Obtain explicit approval before tagging or publishing.
- Install through HACS and verify branding, setup, normalization, identity,
  firmware, duplicate prevention, snapshot, live stream, reauthentication,
  reconfiguration, reload/restart, unload/delete, and logs on the physical
  camera.
- Persist the agreed physical pass/fail result.

**Tracked:** #19 Release and physically verify architecture v2; #26 Simplify
Readme.

### Step 11 — Complete architecture v3 for 0.3.0

**Status:** `started`

**Mode:** Parallel architecture work only; this does not authorize `0.3.0`
implementation.

**Latest result:** `architecture-v3.md` is drafted as a complete replacement
for v2 and v2.1. It preserves still-true text/contracts, incorporates Camera
access, and adds optional one-way audio through a user-operated local go2rtc
restream that copies H.264 and converts ADPCM to AAC/Opus. It awaits independent
verification and user approval.

**Goal:** Produce a decision-complete standalone architecture v3 without
starting `0.3.0` implementation before final `0.2.1`.

**Acceptance criteria:**

- Every v2 and v2.1 section is preserved or explicitly superseded.
- Existing ASF remains authoritative; audio is optional, local, and one-way.
- The integration does not own FFmpeg, go2rtc, subprocesses, or WebRTC
  signaling.
- Audio access is separate and subordinate to Camera access.
- Existing `0.2.x` entries require no migration unless audio is configured.
- HLS and WebRTC physical playback, latency, and CPU remain release gates.
- Independent Verifier PASS and user approval precede implementation.

**Tracked:** #17 Design one-way sound support.

## Scheduled work

### Step 10 — Final 0.2.0 release

**Status:** `not started`

**Goal:** Promote the physically verified RC to final `0.2.0`.

**Acceptance criteria:**

- Manifest and README use `0.2.0`.
- Full local checks and exact-commit Test, HACS, and Hassfest pass.
- Independent Verifier and user accept the final candidate.
- Immediately before publication, only #19 Release and physically verify
  architecture v2 may remain open.
- Obtain explicit approval before tagging or publishing.
- After publication, close the release issue, confirm zero open `0.2.0`
  issues, and close the milestone.

### Step 10a — Implement Camera access for 0.2.1

**Status:** `not started`

**Goal:** Implement `architecture-v2.1.md` on final `0.2.0`.

**Outside:** Camera write commands, physical sensor/power privacy claims,
audio, talkback, new runtime dependencies, polling, and unrelated refactoring.

**Acceptance criteria:**

- Add one persisted Camera access switch on the camera device; existing entries
  default to on.
- Off makes no snapshot request, returns no stream source/credential URL, and
  explicitly stops active Home Assistant media.
- Off survives reload/restart; on restores access without a proactive request.
- Updates use the existing lifecycle and reload exactly once.
- UI, README, and tests state that this controls only the integration's access.
- No Audio entity, transcoder, or speculative camera command is added.
- Architecture-v2.1 tests and existing checks pass; independent Verifier and
  user accept the implementation.

**Tracked:** #20 Add Camera access control.

### Step 10b — Release and physically verify 0.2.1

**Status:** `not started`

**Goal:** Release Camera access before any `0.3.0` implementation.

**Acceptance criteria:**

- Release metadata accurately describes integration-local access control.
- Full checks and exact-commit workflows pass; obtain explicit release approval.
- HACS verification proves off blocks/stops snapshots and streams across
  reload/restart, and on restores them.
- After publication, close #22 Release and physically verify Camera access,
  confirm zero open `0.2.1` issues, and close the milestone.

**Tracked:** #22 Release and physically verify Camera access.

### Step 12 — Implement sound support for 0.3.0

**Status:** `not started`

**Sequence gate:** Start only after Step 11 is verified and final `0.2.1` is
published and physically verified.

**Goal:** Implement only the approved architecture-v3 one-way audio path and
Audio access switch.

**Acceptance criteria:**

- Preserve copied H.264 and convert only ADPCM audio through the approved local
  restream boundary.
- Audio can be disabled independently; Camera access remains the master media
  control.
- Existing camera behavior and architecture-v3 tests pass.
- Independent Verifier and user accept the implementation.

**Tracked:** #23 Add optional one-way audio restream; #24 Add separate Audio
access control.

### Step 13 — Release and physically verify 0.3.0

**Status:** `not started`

**Goal:** Release sound support after physical Home Assistant playback proof.

**Acceptance criteria:**

- Exact release commits pass local checks, Test, HACS, Hassfest, and independent
  verification.
- HLS and WebRTC deliver audible continuous audio with accepted latency and CPU
  observations.
- Camera access and Audio access behave as documented across reload/restart.
- Obtain explicit approval before tags/releases; after final publication close
  #25 Release and physically verify sound support, confirm zero open `0.3.0`
  issues, and close the milestone.

**Tracked:** #25 Release and physically verify sound support.
