# Architecture v2.1 — Camera access control for 0.2.1

## 1. Relationship to architecture v2

This document is the narrow architecture delta for release `0.2.1`. It keeps
the local-only, secret-safe, minimal design and the implemented `0.2.0`
baseline from `architecture-v2.md`. Where this document is silent,
`architecture-v2.md` remains authoritative.

The only new runtime feature is a Home Assistant switch that lets the user
stop and resume this integration's access to camera video and snapshots. This
document does not authorize an unverified camera write command. Audio remains
future `0.3.0` work.

The roadmap is explicit: `0.2.0` is the current architecture-v2 baseline,
`0.2.1` adds Camera access, and `0.3.0` adds audio with its own separate Audio
switch.

## 2. Privacy semantics and evidence boundary

No documented or physically verified camera command is currently known to
power down the image sensor, disable capture in the camera firmware, or block
other clients. The locally verified read-only surface remains:

- `GET /get_params.cgi`
- `GET /get_properties.cgi`
- `GET /snapshot.cgi`
- `GET /av.asf?stream=1`

Therefore the entity must be named **Camera access**, not **Privacy mode** or
**Camera power**.

When Camera access is off, the integration guarantees that it:

- makes no new snapshot request;
- does not provide a new stream source or credential-bearing media URL;
- terminates its active Home Assistant stream outputs and workers, including
  HLS/recording use and any registered WebRTC provider sessions;
- preserves the off state across reload and Home Assistant restart.

It does **not** claim that it:

- powers down the camera, image sensor, or microphone;
- prevents the vendor app, cloud/P2P service, or another LAN client from
  accessing the camera;
- prevents camera firmware from capturing, buffering, or transmitting media;
- provides physical privacy equivalent to a shutter or power removal.

Users requiring physical privacy must use a physical shutter or remove power
until a device-side control has been independently established.

## 3. Revised scope boundary

Architecture v2's ban on switches is revised only for one native Home
Assistant `SwitchEntity`: Camera access. The bans on guessed write CGI calls,
generic protocol probing, polling, coordinators, new dependencies, cloud/P2P,
and unrelated controls remain.

In particular, v2.1 does not add `set_params.cgi`, a vendor privacy command,
audio playback, audio transcoding, microphone control, or two-way talkback.

## 4. Minimal state model

Persist one boolean, `camera_enabled`, in `ConfigEntry.options`:

- a missing option means `true`, preserving behavior for existing users;
- switch-on stores `true`;
- switch-off stores `false`;
- the existing config-entry update/reload lifecycle applies the new state;
- no separate storage, coordinator, dispatcher, restore cache, or polling is
  introduced.

This is intentionally configuration state, not a reported device state. The
switch must not imply that it has read back a camera-side privacy status.

## 5. Camera access switch

Add one switch entity on the same device as the camera:

- entity name: `Camera access`;
- unique ID: `<device_id>_camera_access`;
- state: the persisted `camera_enabled` option;
- available whenever the config entry is loaded;
- turn-off updates the option and causes one reload through the existing
  listener;
- turn-on updates the option and causes one reload through the existing
  listener;
- turning on performs no proactive network request.

Do not add the camera platform's duplicate on/off feature. A separate switch
is required by the user and leaves room for a distinct future audio control.

## 6. Camera behavior while off

The camera entity remains registered so dashboards and automations retain a
stable entity. Its media methods enforce the access state:

- `async_camera_image()` returns no image without calling the API client;
- `stream_source()` returns no source without constructing or returning a
  credential-bearing URL;
- transition to off explicitly stops any active Home Assistant stream before
  reload/removal; it must not rely only on an idle timeout;
- unload also stops active media cleanly.

The implementation should use Home Assistant's native camera stream lifecycle
and native switch platform. It must not manage its own FFmpeg process or add a
runtime dependency.

## 7. Future audio-switch provision

Physical evidence already establishes that the ASF stream contains active
H.264 Main video and active mono 8 kHz, 32 kbit/s `adpcm_ima_wav` audio. A
password-safe local ADPCM-to-AAC playback experiment completed technically,
and the user physically confirmed that audio was audible and continuous for
the full 15-second run. The physical playback result is `PASS`.

Audio support remains exclusively `0.3.0` scope. V2.1 creates no Audio entity,
option, translation, transcoder, or process. Architecture v3 may later add a
separate Audio switch with these semantics:

- Camera access is the master media-access switch;
- Camera access off stops both video and any future audio path;
- Audio off may mute/withhold audio while Camera access stays on;
- Audio on cannot bypass Camera access off.

No abstraction is required in `0.2.1` to prepare for this; the relationship is
documented now and implemented only when the audio architecture is approved.

## 8. Evidence gate for any physical camera control

A later design may replace the limited integration-access semantics only after
all of the following are established on the physical camera:

1. Confirm that the official app exposes a camera-off or privacy operation. If
   it does not, stop; do not probe speculative write endpoints.
2. Compare the already verified `get_params.cgi` response before and after the
   official operation, retaining only assignment names and relevant sanitized
   boolean values.
3. Observe the official app's local request, retaining only method, path,
   parameter names, and sanitized values—never passwords, Digest headers, raw
   packet captures, or complete responses.
4. Prove the operation is reversible and that an independent client can no
   longer fetch both snapshot and stream while it is active.
5. Verify behavior after camera restart and on command failure.

Even a verified firmware command should be described as **camera media output
disabled** unless vendor evidence proves that the physical sensor is powered
down. No write call enters the integration without architecture review and
explicit user approval.

## 9. Expected implementation change set

The smallest expected production change is:

- `custom_components/reer_babycam/__init__.py`: forward/unload the switch
  platform and preserve one-reload behavior;
- `custom_components/reer_babycam/camera.py`: enforce off-state media gates
  and stop active streams;
- `custom_components/reer_babycam/const.py`: the option key/default;
- `custom_components/reer_babycam/switch.py`: the single entity;
- `custom_components/reer_babycam/manifest.json`: include the switch platform
  only if required by the integration's platform declaration pattern;
- `custom_components/reer_babycam/strings.json` and translations: accurate
  Camera access wording;
- tests for switch, persistence, media gating, and cleanup;
- README documentation of the exact privacy boundary.

`api.py` must remain unchanged unless the physical-control evidence gate is
completed and a separate architecture decision authorizes a verified endpoint.

## 10. Minimum tests

Tests must demonstrate:

1. Existing entries without the option default to Camera access on.
2. The switch and camera share the same device; unique IDs are stable.
3. Turning off persists once and causes exactly one lifecycle reload.
4. Turning off stops an already active Home Assistant stream.
5. Snapshot returns no image and performs no client request while off.
6. Stream source returns no value and never exposes/builds a media URL while
   off.
7. Off survives reload and Home Assistant restart.
8. Turning on persists once, reloads once, and restores normal snapshot and
   stream behavior without a proactive request.
9. Unload while media is active stops the stream and unloads both platforms.
10. Failures and logs contain no password, Digest material, or credential URL.
11. No Audio switch/entity exists in `0.2.1`.

Reuse the existing real Home Assistant test environment and fakes. Do not add
a second harness or tests for speculative camera commands.

## 11. Documentation and acceptance

README and release notes must call the feature Camera access and explain both
the guarantee and limitation from section 2. They must not use a privacy,
power, sensor-off, or microphone-off claim.

`0.2.1` is accepted when:

- all tests above and existing `0.2.0` checks pass;
- an independent Verifier confirms the implementation matches this delta and
  architecture v2;
- a physical HACS test proves off blocks new snapshots/streams, stops an
  active Home Assistant stream, persists across restart, and on restores
  operation;
- the user accepts that this is Home Assistant integration access control,
  not verified physical-camera privacy;
- `0.2.1` is released before any `0.3.0` implementation begins.
