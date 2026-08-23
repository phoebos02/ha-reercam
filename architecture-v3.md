# reer IP BabyCam Home Assistant Custom Integration — Architecture Specification v3

**Status:** Implementation architecture

**Architecture version:** 3

**Release line:** `0.3.0`

**Baseline releases:** `0.2.0` architecture v2, `0.2.1` architecture v2.1

**Target Home Assistant:** 2026.8+

**Distribution:** HACS custom integration

**Integration domain:** `reer_babycam`

**Supported device:** reer IP BabyCam 80300

**Verified firmware:** `42.7.3.4.70`
**Protocol basis:** Verified local HTTP/CGI and physical media behavior on the supported camera

## 0. Authority, supersession, and change markers

This document fully incorporates and supersedes `architecture-v2.md` and
`architecture-v2.1.md`. An implementer must use this document alone and must
not need either earlier architecture.

Requirements are marked to make the delta auditable:

- **[V2 unchanged]** preserves an architecture-v2 contract substantially
  unchanged.
- **[V2.1 incorporated]** preserves the Camera access architecture and its
  privacy limitation.
- **[V3 added]** adds or changes behavior for one-way listening.

The release sequence is fixed: `0.2.0` is the v2 baseline, `0.2.1` adds Camera
access, and `0.3.0` adds optional one-way audio and a separate Audio switch.
Final `0.2.1` must be physically verified before `0.3.0` implementation starts.

## 1. Purpose

**[V2 unchanged, V3 extended]**

Implement the smallest useful Home Assistant custom integration for the
verified reer IP BabyCam 80300.

The integration exposes the camera as one native Home Assistant camera entity
using the verified local HTTP interface. It supports UI configuration,
physical identity, metadata, still images, live video, password
reauthentication, host reconfiguration, and integration-local Camera access
control.

Version `0.3.0` adds optional one-way listening through that existing camera
entity. The camera's existing ASF stream remains the only camera media source.
Because its audio codec is not accepted by Home Assistant's native HLS remux
path, sound is enabled only through one explicitly configured, user-operated,
local restream. The integration does not own a transcoder process.

The architecture deliberately favors a narrow implementation over generality.
Only physically verified behavior and the minimum native Home Assistant
surface required for this device are included.

## 2. Hard scope boundaries and explicit exclusions

These are architectural constraints, not backlog items for `0.3.0`. The
implementation must not follow, probe, generalize, or implement these paths
unless a later architecture revision explicitly adds them.

### 2.1 Protocol and connectivity

**[V2 unchanged]**

- No TCP port `2345` camera protocol.
- No vendor cloud access.
- No P2P access or SoSoCam connectivity.
- No ReeCam push service.
- No automatic network discovery.
- No generic ReeCam or SoSoCam compatibility layer.
- No protocol probing beyond the verified camera endpoints in section 3.
- No separate camera-protocol package or reusable external Python library.
- No public or internet-hosted restream.

### 2.2 Camera control and device configuration

**[V2 unchanged, with the v2.1 switch exception]**

- No PTZ.
- No camera write CGI calls.
- No `set_params.cgi`.
- No camera-side motion or sound configuration.
- No IR or night-mode control.
- No recording management.
- No SMB management.
- No firmware-management functionality.
- No guessed privacy, power, microphone, or media-disable command.
- No services, buttons, selects, numbers, or controls other than the two
  switches defined in sections 16 and 21.

### 2.3 Media

**[V3 changed]**

- One-way listening only.
- No two-way audio or talkback.
- No camera speaker/output path.
- No recording management or integration-owned media storage.
- No RTSP emulation by the integration.
- No integration-owned FFmpeg, PyAV, go2rtc, subprocess, watchdog, or proxy.
- No arbitrary stream profiles, SD/HD selector, or profile options flow.
- No video transcoding; H.264 must be copied unchanged.
- Audio conversion is limited to the external restream contract in section 18.
- No alternative camera endpoint unless separately physically verified and a
  later architecture authorizes it.

### 2.4 Home Assistant surface

**[V2 unchanged, with v2.1/v3 switch exceptions]**

- No diagnostic or status sensors.
- No continuous status polling.
- No `DataUpdateCoordinator`.
- No diagnostics endpoint.
- No YAML configuration for the integration.
- No repair issues.
- No custom WebSocket API.
- No media-source integration.
- No event entities.
- No entity base-class hierarchy for hypothetical future entities.
- Exactly one camera entity, one Camera access switch, and, only when a local
  restream is configured, one Audio switch.

### 2.5 Implementation complexity

**[V2 unchanged]**

- No snapshot cache.
- No speculative request serialization or global request lock.
- No config-entry migration framework beyond version `1`; missing options use
  safe defaults as specified in section 22.
- No secondary user-interface language is required for `0.3.0`.
- No functionality for hypothetical devices or capabilities.
- No abstraction layer over multiple restream products.
- No background restream health monitor or automatic fallback.

## 3. Verified camera HTTP and media contract

The integration may rely only on the following verified camera behavior.

### 3.1 HTTP service

**[V2 unchanged]**

The camera exposes an HTTP service on TCP port `80`. The observed server is
`Boa/0.94.14rc21`.

Protected camera endpoints use HTTP Digest authentication with:

```text
realm = "ip camera"
qop = "auth"
algorithm = MD5
```

The supported integration uses fixed `username = admin` and `port = 80`. The
user supplies only camera `host` and `password` during initial setup.

### 3.2 Device identity

**[V2 unchanged]**

Endpoint: `GET /get_params.cgi`.

The authenticated JavaScript-style response contains `var id='...';`.
Exactly `id` is extracted as the stable physical-device identifier. The raw
response must not be stored.

### 3.3 Device metadata

**[V2 unchanged]**

Endpoint: `GET /get_properties.cgi`.

Exactly `firmware_ver` is extracted from a JavaScript-style assignment such as
`var firmware_ver='42.7.3.4.70';`. Firmware may be absent. The raw response
must not be stored.

### 3.4 Snapshot

**[V2 unchanged]**

Endpoint: `GET /snapshot.cgi`, protected with HTTP Digest. The verified
response is non-empty `image/jpeg`; the observed image is 1280×720. The
integration passes the returned JPEG bytes directly to Home Assistant.

### 3.5 Live video source

**[V2 unchanged]**

Endpoint: `GET /av.asf?stream=1`, protected with HTTP Digest.

Verified video:

```text
ASF container
H.264 Main
1280x720
approximately 15 fps
```

The integration always uses `stream=1`. Without an optional restream, it
returns the credential-bearing camera URL to Home Assistant's native camera
stream subsystem.

### 3.6 Audio evidence

**[V3 added]**

A password-safe physical probe of the same `/av.asf?stream=1` source proved:

```text
stream index 1
codec adpcm_ima_wav
mono
8000 Hz
32000 bit/s
453 non-empty packets during 15 seconds
```

The simultaneous H.264 Main video stream produced 263 non-empty packets during
the same 15 seconds. A password-safe pipeline copied the input into FFmpeg,
converted only audio to AAC-LC mono 16 kHz at 32 kbit/s, and played it locally.
The processes passed technically and the user physically confirmed audible,
continuous audio for the full 15-second run. Physical ADPCM-to-AAC playback is
`PASS`.

This proves camera audio and the conversion, but not Home Assistant HLS or
WebRTC delivery. Those remain mandatory physical gates in section 28.

### 3.7 Home Assistant 2026.8 codec boundary

**[V3 added]**

The installed Home Assistant 2026.8 stream worker accepts only `aac` and `mp3`
audio for its HLS/fMP4 remux and discards any other audio track. It remuxes; it
does not encode ADPCM to AAC. Therefore the camera's ADPCM audio is omitted by
the native HLS path. This conclusion follows directly from the installed
`homeassistant.components.stream.const.AUDIO_CODECS` and worker selection
logic and must be rechecked when raising the minimum Home Assistant version.

## 4. High-level architecture

**[V2 preserved, v2.1/v3 extended]**

```text
Home Assistant
│
├── Config Flow
│    └── ReerBabyCamClient
│         ├── GET /get_params.cgi → id
│         └── GET /get_properties.cgi → firmware_ver
│
├── ConfigEntry[ReerBabyCamRuntimeData]
│    ├── data: camera host + password
│    ├── options: camera_enabled
│    ├── options: optional audio_restream_url + audio_enabled
│    ├── client
│    └── device_info
│
├── Camera access switch
│    └── master integration-local media gate
│
├── Audio switch (only when restream configured)
│    └── selects video-only or video+audio restream view
│
└── Camera entity
     ├── async_camera_image() → GET /snapshot.cgi
     └── stream_source()
          ├── Camera access off → no source
          ├── no restream → camera ASF URL
          ├── Audio off → local RTSP restream, H.264 only
          └── Audio on → local RTSP restream, H.264 + AAC + Opus

User-operated local restream (optional deployment)
│
├── protected camera secret file
├── Digest HTTP /av.asf?stream=1 input
├── H.264 copy
├── ADPCM → AAC-LC/16 kHz/mono/32 kbit/s
└── ADPCM → Opus/16 kHz/mono/32 kbit/s for WebRTC
```

The optional deployment is one user-operated go2rtc service. It is not a
runtime dependency managed by the custom integration.

## 5. Repository structure

**[V2 preserved, v3 extended only where required]**

```text
repo-root/
├── custom_components/reer_babycam/
│   ├── __init__.py
│   ├── api.py
│   ├── camera.py
│   ├── config_flow.py
│   ├── const.py
│   ├── switch.py
│   ├── manifest.json
│   ├── strings.json
│   └── translations/en.json
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_camera.py
│   ├── test_config_flow.py
│   └── test_switch.py
├── examples/go2rtc/             # only if needed for the reviewed deployment
│   ├── README.md
│   └── password-safe helper/config templates
├── .github/workflows/
├── hacs.json
├── pyproject.toml
├── README.md
├── LICENSE
└── architecture-v3.md
```

Files are added only when required by implementation or validation tooling.
Do not add `models.py`, a base entity, or a restream package merely to match
this conceptual tree.

## 6. Manifest and dependencies

**[V2 unchanged except release version]**

The manifest retains:

```json
{
  "domain": "reer_babycam",
  "name": "reer IP BabyCam",
  "version": "0.3.0",
  "config_flow": true,
  "dependencies": ["http", "stream"],
  "integration_type": "device",
  "iot_class": "local_polling"
}
```

It also retains the real documentation URL, issue tracker, and code owner.
No new Python runtime dependency is added. In particular, `av`, FFmpeg,
go2rtc, or a process manager must not be declared by this integration.

Home Assistant's own optional go2rtc provider may deliver WebRTC, but the
integration does not depend on or call go2rtc APIs.

## 7. Constants

**[V2 preserved, v2.1/v3 extended]**

`const.py` contains only stable values used by implemented behavior:

```text
DOMAIN = reer_babycam
DEFAULT_PORT = 80
DEFAULT_USERNAME = admin
PARAMS_PATH = /get_params.cgi
PROPERTIES_PATH = /get_properties.cgi
SNAPSHOT_PATH = /snapshot.cgi
STREAM_PATH = /av.asf?stream=1
CONF_CAMERA_ENABLED = camera_enabled
CONF_AUDIO_ENABLED = audio_enabled
CONF_AUDIO_RESTREAM_URL = audio_restream_url
```

Use Home Assistant's `CONF_HOST` and `CONF_PASSWORD`. Avoid constants for
unimplemented camera capabilities.

## 8. Runtime and persisted state model

**[V2 preserved, v2.1/v3 extended]**

Keep the small typed data model:

```python
@dataclass(slots=True, frozen=True)
class ReerBabyCamInfo:
    device_id: str
    firmware_version: str | None


@dataclass(slots=True)
class ReerBabyCamRuntimeData:
    client: ReerBabyCamClient
    info: ReerBabyCamInfo
```

Use `ConfigEntry[ReerBabyCamRuntimeData]`. No capability model is required.

Persist:

| Location | Key | Default when missing | Meaning |
| --- | --- | --- | --- |
| `entry.data` | `host` | none | normalized camera host |
| `entry.data` | `password` | none | camera secret |
| `entry.options` | `camera_enabled` | `true` | integration-local master media access |
| `entry.options` | `audio_restream_url` | absent | optional local RTSP restream base URL |
| `entry.options` | `audio_enabled` | `false` | one-way listening requested |

The two booleans are configuration state, not device-reported state. No
`RestoreEntity`, extra storage, coordinator, dispatcher, cache, or polling is
required.

## 9. CGI parsing

**[V2 unchanged]**

The parser exists only to extract `id` and `firmware_ver` from exact
JavaScript-style quoted string assignments.

Requirements:

1. Parse response text line-by-line.
2. Recognize only the exact requested variable name.
3. Parse quoted string values safely.
4. Never use `eval`.
5. Ignore unrelated variables.
6. Reject a required value that is absent, empty, duplicated, or malformed.
7. Discard the original response immediately after extraction.
8. Never return a generic dictionary of camera configuration.

## 10. API client and errors

**[V2 unchanged]**

`api.py` owns only the verified camera HTTP protocol:

```python
class ReerBabyCamClient:
    async def async_get_info(self) -> ReerBabyCamInfo: ...
    async def async_get_snapshot(self) -> bytes: ...
    def stream_url(self) -> URL: ...
```

The client receives normalized camera `host`, camera `password`, and the Home
Assistant-managed async HTTP session. It uses fixed port 80 and username
`admin`. It must not create a long-lived unmanaged global session.

`async_get_info()` performs the two verified GET requests, requires a non-empty
device ID, permits missing firmware, returns only the typed values, and retains
no raw response.

`async_get_snapshot()` validates successful status, JPEG-compatible content
type, and non-empty body, then returns the bytes unchanged.

`stream_url()` constructs
`http://<encoded-user>:<encoded-password>@<host>:80/av.asf?stream=1` with a
real URL library. The URL is runtime-only and is never stored.

Keep the minimal hierarchy:

```text
ReerBabyCamError
├── ReerBabyCamConnectionError
├── ReerBabyCamAuthError
└── ReerBabyCamProtocolError
```

Map 401/403 to authentication; timeout, DNS failure, and refusal to connection;
and unexpected status/body to protocol. Exception messages must contain no
password, raw response, lower-level secret, or credential-bearing URL.

All HTTP requests disable redirects so credentials cannot be forwarded to a
different host.

## 11. Configuration, reauthentication, and reconfiguration

### 11.1 User setup

**[V2 unchanged]**

Configuration is UI-only. The user supplies required camera `host` and
`password`. Normalize the host; reject schemes, credentials, ports, paths,
queries, fragments, and invalid host syntax. Validate through
`async_get_info()`, require camera `id`, set it as config-entry unique ID,
abort duplicates, and create the entry titled `reer IP BabyCam`.

Map failures to `cannot_connect`, `invalid_auth`, `invalid_response`, or
`unknown`. User-visible errors contain no raw protocol response.

### 11.2 Reauthentication

**[V2 unchanged]**

Accept only a replacement camera password. Use the existing host, fetch info,
require the same device ID, update stored password, and reload exactly once.
A different physical camera must not be accepted.

### 11.3 Reconfiguration

**[V2 unchanged]**

Accept only a replacement camera host. Use the existing password, normalize
and validate the host, fetch info, require the same device ID, update the host,
and reload exactly once. This remains the DHCP/address-change mechanism.

### 11.4 Audio restream options

**[V3 added]**

Add the minimum Home Assistant options flow for one optional field:
`audio_restream_url`. Blank removes the restream configuration.

The accepted URL contract is deliberately narrow:

- `rtsp` scheme only;
- literal loopback, private, or link-local IP address only;
- explicit port and non-empty path;
- no username, password, query, fragment, or embedded control character;
- no DNS name and no public/multicast/unspecified address.

Normalize and store the non-secret base URL without a query. Do not contact or
probe the service during the options flow. Successful changed options reload
exactly once; unchanged input reloads zero times.

When the URL is first added, `audio_enabled` remains or defaults to `false` so
listening requires an explicit switch-on. Removing it also removes
`audio_enabled`; the Audio entity disappears after reload.

The integration does not collect camera credentials for the restream. The
user configures those separately in the protected restream deployment.

## 12. Setup and unload lifecycle

**[V2 preserved, v2.1/v3 extended]**

`async_setup_entry()`:

1. Obtain Home Assistant's managed async HTTP client.
2. Instantiate `ReerBabyCamClient`.
3. Fetch `ReerBabyCamInfo`.
4. Verify that the device ID equals the config-entry unique ID.
5. Store `ReerBabyCamRuntimeData` in `entry.runtime_data`.
6. Forward setup to camera and switch platforms.
7. Register the existing entry update listener.

Authentication failure triggers Home Assistant reauthentication. Transient
connection failure uses config-entry retry. Protocol or identity failure is a
safe config-entry error.

`async_unload_entry()` explicitly stops active Home Assistant stream workers
and WebRTC provider sessions, then unloads camera and switch platforms. It
must leave no listener or media worker behind. Toggling either switch stops
active media before the options-triggered reload so a previous source cannot
continue until idle timeout.

## 13. Device registry

**[V2 unchanged]**

Create one Home Assistant device:

```python
DeviceInfo(
    identifiers={(DOMAIN, info.device_id)},
    manufacturer="reer",
    model="IP BabyCam 80300",
    name="reer IP BabyCam",
    serial_number=info.device_id,
    sw_version=info.firmware_version,
)
```

The camera `id` is authoritative. Camera and both switches belong to this
device. IP addresses and the restream URL are connection data, not identity.

## 14. Camera entity

**[V2 preserved, v2.1/v3 extended]**

Create exactly one camera entity with unique ID `<device_id>_camera`,
`has_entity_name = true`, and no entity-level name. It belongs to the single
device and advertises Home Assistant's camera stream feature.

### 14.1 Still image

`async_camera_image()`:

- returns `None` without an API request when Camera access is off;
- otherwise calls `client.async_get_snapshot()` and returns JPEG bytes;
- does not use the restream for snapshots;
- does not cache snapshots.

Width and height hints may be accepted by the method signature but are not
sent to the camera because no such verified endpoint behavior exists.

### 14.2 Live stream source

`stream_source()` returns `str | None` according to the state matrix in
section 21. It never starts a process and never probes a source.

The Home Assistant stream subsystem owns HLS handling. A registered Home
Assistant go2rtc provider may own WebRTC signaling and transport. The custom
integration implements neither HLS nor WebRTC itself.

### 14.3 Camera state and availability

The camera entity remains registered while the entry is loaded so dashboards
and automations retain a stable entity. Its `is_on` state mirrors Camera
access, allowing Home Assistant's native camera views to reject requests while
off. Do not add the camera platform's duplicate ON/OFF feature; the dedicated
Camera access switch is the only control.

Do not introduce background liveness. Network and restream failures are
reported only when the user requests media. The entity is not marked
unavailable merely because no health check has run.

## 15. Stream lifecycle and source changes

**[V2.1 incorporated, V3 extended]**

Camera access or Audio access changes can alter or remove the source. Before
persisting/reloading a changed option, the implementation must:

1. stop the camera's active Home Assistant `Stream`, removing outputs and its
   worker;
2. close/unregister active WebRTC provider sessions through Home Assistant's
   native camera lifecycle;
3. update options once;
4. allow the existing listener to reload exactly once.

Do not wait for Home Assistant's stream idle timeout. On the next request,
Home Assistant creates a stream from the new source.

Unchanged switch state or unchanged options cause no reload. Turning a switch
on performs no proactive camera or restream request.

## 16. Camera access switch and privacy boundary

**[V2.1 incorporated]**

Add one native `SwitchEntity`:

```text
entity name = Camera access
unique ID = <device_id>_camera_access
state = entry.options[camera_enabled], default true
```

It is available whenever the config entry is loaded; it is not a camera
liveness indicator.

When Camera access is off, the integration guarantees that it:

- makes no new snapshot request;
- returns no stream source and constructs/returns no credential-bearing media
  URL;
- terminates active Home Assistant HLS/recording streams and WebRTC sessions;
- prevents Audio access from bypassing the master gate;
- preserves the state across reload and Home Assistant restart.

It does **not** claim that it:

- powers down the camera, image sensor, or microphone;
- prevents the vendor app, cloud/P2P service, or another LAN client from
  accessing the camera;
- prevents camera firmware from capturing, buffering, or transmitting media;
- provides physical privacy equivalent to a shutter or power removal.

The entity must be named **Camera access**, not Privacy mode or Camera power.
Users requiring physical privacy must use a physical shutter or remove power
until a device-side control is independently established.

No camera write call is added. A later device-side control requires all of:

1. an actual official-app privacy operation;
2. sanitized before/after evidence from the verified read-only CGI responses;
3. the sanitized method/path/parameter names used by the official app;
4. proof that independent snapshot and stream clients are blocked;
5. reversibility, restart, and failure tests;
6. a new architecture decision and explicit user approval.

Even then, call it camera media output disabled unless vendor evidence proves
that the physical sensor is powered down.

## 17. Why a restream is required for sound

**[V3 added]**

The zero-code preference was tested first. The ASF source has real audio, but
Home Assistant 2026.8 HLS accepts only AAC or MP3 and drops the camera's
`adpcm_ima_wav` track. Returning the existing source unchanged therefore does
not satisfy one-way listening through HLS.

Home Assistant does not expose a native audio-only camera/listening entity
that fits this use case. A `media_player` or sensor would misrepresent the
device and is prohibited. The integration also must not manage FFmpeg or PyAV.

The minimum viable design is consequently one optional user-operated local
restream. Users who do not configure it retain the `0.2.1` camera, snapshot,
and Camera access behavior with no additional service and no Audio entity.

## 18. Selected user-operated restream contract

**[V3 added]**

### 18.1 Product and ownership

Use one user-operated go2rtc service with its bundled FFmpeg. The reference
and Home Assistant 2026.8-recommended version at architecture time is
go2rtc `1.9.14`; the exact image/version used for release must be pinned and
recorded in physical verification.

The user installs, configures, starts, updates, rolls back, and removes this
service. HACS does none of those tasks. The custom integration does not call
the go2rtc API, generate its configuration, start subprocesses, or supervise
the service.

### 18.2 Media transformation

The single named restream must ingest only the verified camera ASF source and
publish these tracks:

```text
video: H.264 copied bit-for-bit; no decode or encode
audio 1: AAC-LC, mono, 16000 Hz, 32000 bit/s
audio 2: Opus, mono, 16000 Hz input, 32000 bit/s, low-delay application
```

The first audio track must be AAC because Home Assistant's HLS worker selects
the first supported audio track. The Opus track exists only for WebRTC codec
negotiation. No image scaling, rotation, filtering, or video encode is allowed.

The integration derives two non-secret RTSP consumer URLs from the stored base
URL using a URL library:

```text
Audio access off: ?video=h264
Audio access on:  ?video=h264&audio=aac&audio=opus
```

These are go2rtc's documented codec filters. The base URL stored in options
contains no query. Query construction must preserve the two ordered `audio`
values and must not use string concatenation.

### 18.3 Password-safe input

The reference deployment must not place the camera password or
credential-bearing camera URL in a command line, process listing, go2rtc
stream URL, integration option, log, or generated media.

Use this boundary:

1. A protected restream-side curl configuration file, readable only by the
   service account, contains the camera URL and Digest `admin` credential.
2. A small reviewed helper is launched by go2rtc's `exec` source only on
   demand. Its arguments contain only the local go2rtc output URL/mode.
3. `curl --config <protected-file>` reads the secret from the file and writes
   ASF bytes to stdout; stderr is sanitized or suppressed.
4. FFmpeg reads `pipe:0`, maps H.264 with `copy`, encodes only the two audio
   outputs, and publishes to go2rtc's local RTSP ingest URL.
5. Neither helper nor go2rtc prints raw commands/configuration at debug or
   trace level in normal operation.

The repository may provide a minimal reviewed example helper and templates,
but never a real `camera.txt`, password, address, generated config, or media
file. The user's protected file remains outside version control.

If a target deployment cannot keep the password out of process arguments and
logs, audio setup fails the security gate and must not be documented as
supported there.

### 18.4 Network exposure

The restream must be reachable from Home Assistant but remain on the trusted
local network. Bind/firewall its RTSP service so only Home Assistant and the
restream host can reach it. Do not expose its RTSP, API, Web UI, WebRTC, or
helper endpoints to the internet.

The integration supports no credentials in `audio_restream_url`. This avoids
a second credential-bearing runtime URL. If network isolation cannot protect
the RTSP output, the deployment is unsupported in `0.3.0`.

### 18.5 Demand, media retention, and process count

The restream starts the helper/FFmpeg producer only when a consumer requests
the stream and stops it when the final consumer disconnects. It writes no
recording, segment, snapshot, credential file, or packet capture beyond its
protected static configuration.

Multiple Home Assistant consumers should share one producer. Physical
verification must confirm that normal concurrent HLS/WebRTC viewing does not
spawn redundant camera input/transcode producers.

## 19. HLS and WebRTC delivery contract

**[V3 added]**

### 19.1 HLS

HLS is mandatory for `0.3.0`. Home Assistant opens the local RTSP restream,
copies H.264 and the first AAC track into its native fragmented-MP4/HLS
output, and serves the authenticated frontend as usual.

The integration does not return go2rtc's HLS URL and does not bypass Home
Assistant's camera authentication/token path.

### 19.2 WebRTC

WebRTC is mandatory physical verification for the selected dual-audio design.
When Home Assistant has its supported go2rtc provider, that provider receives
the camera's local RTSP source and should select the Opus track. The integration
does not implement WebRTC signaling, ICE, SDP, or a provider.

Before final release, the Home Assistant frontend must prove that WebRTC uses
H.264 plus Opus and that audio is audible and continuous. If WebRTC cannot
select Opus on the target Home Assistant/go2rtc versions, final `0.3.0` is
blocked pending an architecture correction; do not silently claim WebRTC audio
or add integration-owned negotiation code.

### 19.3 No hidden codec fallback

When Audio access is off, the source exposes only H.264. Neither Home
Assistant HLS nor its go2rtc fallback may receive an audio track to transcode.
When on, AAC and Opus must both be visible at the restream boundary. Tests and
physical probes verify the exact track lists.

## 20. Audio restream options and entity creation

**[V3 added]**

Without `audio_restream_url`:

- do not create an Audio switch;
- keep the direct v2 camera ASF source while Camera access is on;
- make no sound-support claim for HLS or WebRTC;
- add no dependency or background task.

With `audio_restream_url`:

- create exactly one Audio access switch;
- use the restream for all live video, even when Audio access is off, so the
  explicit video-only filter is enforceable;
- keep snapshots on the direct verified camera endpoint;
- fail closed if the restream is unavailable; never fall back silently to the
  unfiltered direct ASF source.

Removing the option restores the direct legacy source after one reload and
removes the Audio entity. Removing it is also the supported recovery path if
the external service is abandoned.

## 21. Audio access switch and complete state matrix

**[V3 added]**

Add the switch only when a restream is configured:

```text
entity name = Audio access
unique ID = <device_id>_audio_access
state = entry.options[audio_enabled], default false
```

It is available whenever the config entry and configured restream option are
loaded. Restream liveness is not polled and does not change entity availability.

The switch means: include or exclude a listenable audio track in media this
integration supplies to Home Assistant. It does not power down or mute the
physical microphone and does not affect other clients.

| Camera access | Restream configured | Audio access | Snapshot | Stream source | Audio switch |
| --- | --- | --- | --- | --- | --- |
| off | either | either | none | none | cannot bypass master gate |
| on | no | n/a | direct JPEG | direct camera ASF | absent |
| on | yes | off | direct JPEG | restream H.264 only | off |
| on | yes | on | direct JPEG | restream H.264 + AAC + Opus | on |

Camera access is the master control. Turning it off stops all current video
and audio sessions but does not rewrite the remembered Audio access preference.
Turning Camera access back on restores the prior Audio preference.

Audio access off explicitly stops existing media before selecting the
video-only source. Audio access on does the same before selecting the
dual-audio source. Both persist across reload and restart.

## 22. Migration from 0.2.x

**[V2.1 incorporated, V3 added]**

Keep config-entry version `1`; no migration handler is needed.

- Existing `0.2.0` entries missing `camera_enabled` default to `true`.
- Existing `0.2.1` entries retain their Camera access value.
- Every existing entry lacks `audio_restream_url`, so it keeps direct snapshot
  and video behavior and gains no Audio entity.
- Missing `audio_enabled` defaults to `false`.
- Unique ID, entry title, device identifier, camera unique ID, host, password,
  and entity registry association do not change.
- No camera or restream network request occurs merely because Home Assistant
  upgraded the integration.

Opting into audio is a separate user action through integration options.
Downgrading to `0.2.1` ignores unknown options; users should remove the
restream option first if the older UI cannot manage it.

## 23. Failure, restart, update, and removal behavior

**[V3 added, v2 lifecycle preserved]**

### Camera failures

Authentication during entry setup starts reauthentication. Transient camera
connection failure retries setup. Snapshot failures follow the existing safe
camera/API path. No secret enters the error text.

### Restream failures

The integration performs no health polling. When configured restream media
cannot open or ends, Home Assistant's native stream/provider reports the
failure. Snapshot remains available while Camera access is on. The Audio
switch remains a persisted preference, not a liveness sensor.

Do not fall back to direct ASF: that could violate the selected audio filter
and hide a broken deployment. The user may turn Camera access off, repair the
service, or remove the restream option to return deliberately to legacy video.

### Restart and reconnection

After Home Assistant or restream restart, no media process starts until a
viewer requests a stream. The next request rebuilds the source from persisted
options. Normal Home Assistant/go2rtc retry behavior may reconnect; the custom
integration adds no retry worker.

### Updates

The README records the physically tested Home Assistant, go2rtc, FFmpeg, and
browser versions. External restream updates are manual and pinned; users test
an update before replacing the working version. The integration never updates
or downloads external binaries.

### Removal

Removing the config entry stops Home Assistant media, unloads entities, and
removes integration state. It does not modify the external service. The user
separately stops/removes go2rtc and securely deletes its camera secret file.

## 24. Performance, latency, and resource behavior

**[V3 added]**

- H.264 is copied; any observed video encoder is a release blocker.
- Only the 8 kHz mono audio is decoded/encoded, once to AAC and once to Opus.
- Hardware acceleration is unnecessary and must not be required for audio-only
  conversion.
- Idle audio configuration consumes no producer/transcoder CPU.
- One active shared producer is expected for normal concurrent consumers.
- The helper and restream must terminate promptly after the last consumer.

Physical verification records, without secrets:

- idle and active CPU and memory for the restream/FFmpeg processes;
- producer/process count for one HLS viewer, one WebRTC viewer, and both;
- time from opening a camera card to audible media;
- observed end-to-end video and audio latency;
- observed A/V synchronization and five-minute continuity.

No hardware-independent CPU percentage is promised. Release requires no
sustained dropouts, no host health warning or resource exhaustion, no video
encode, and explicit user acceptance of the recorded latency and load.

## 25. Security and privacy

**[V2 preserved, v2.1/v3 extended]**

The config entry stores camera host and password. The optional base restream
URL is non-secret by contract. Never log or expose:

- camera or restream password;
- Digest authorization material;
- credential-bearing camera stream URL;
- raw CGI response;
- protected restream configuration contents;
- external process command containing a secret;
- media packets, samples, or recordings.

Camera HTTP requests never follow redirects. The credential-bearing direct
URL exists transiently only when Camera access is on and no restream is
configured.

The camera protocol sends authenticated snapshots and media over unencrypted
HTTP on the LAN. Digest authentication does not encrypt media. The restream
input and local RTSP output also require a trusted, isolated network. Neither
endpoint may be internet-exposed.

Camera access and Audio access control only this integration's supplied media.
They do not disable physical capture, the microphone, vendor services, or
other clients. Documentation and translations must never overclaim.

## 26. Translation and user-facing text

**[V2 preserved, v2.1/v3 extended]**

Keep English translations in both `strings.json` and
`translations/en.json`. Translate:

- integration title;
- setup fields and errors;
- reauthentication and reconfiguration;
- restream options field and validation errors;
- Camera access entity name;
- Audio access entity name;
- accurate option descriptions and abort reasons.

Do not hard-code config/option-flow text in Python. Do not call either switch
Privacy, Power, Microphone, or Mute camera.

## 27. Automated tests

Tests use the existing real Home Assistant 2026.8 custom-component harness,
aiohttp, yarl, pytest, and Ruff. Do not add a second harness or a runtime media
dependency merely for tests.

### 27.1 API tests — **[V2 unchanged]**

Cover:

- valid real Digest identity and firmware exchange;
- optional firmware;
- valid JPEG snapshot;
- 401/403 authentication failure;
- timeout and connection failure;
- unexpected HTTP status;
- malformed/missing/duplicate identity;
- malformed firmware;
- redirect refusal;
- safe stream URL and reserved-character credentials;
- secret-free exceptions and logs.

### 27.2 Config-flow tests — **[V2 preserved, V3 extended]**

Cover:

- successful normalized setup;
- invalid host, password, connection, protocol response, and unknown error;
- duplicate physical device;
- successful/failed reauthentication and wrong-device rejection;
- successful/failed host reconfiguration and wrong-device rejection;
- changed data reloads once and unchanged data zero times;
- accepted local RTSP restream URL;
- rejection of public IP, hostname, missing port/path, credentials, wrong
  scheme, query, fragment, and control characters;
- add, unchanged, change, and remove restream options with correct reload
  counts;
- no network request during restream option validation;
- no secret or raw input in errors/logs.

### 27.3 Camera/device tests — **[V2 preserved, v2.1/v3 extended]**

Cover:

- exactly one camera entity and device;
- stable unique ID and device-registry association;
- manufacturer, model, serial, and optional firmware metadata;
- snapshot bytes and direct verified stream URL;
- existing entries default Camera access on;
- Camera access off returns no image/source and makes no client call;
- off stops an already active HLS stream and WebRTC sessions;
- off/on survive reload/restart; on performs no proactive request;
- unload stops active media and unloads both platforms;
- direct legacy source remains for entries without restream;
- restream Audio-off URL contains only the H.264 filter;
- restream Audio-on URL contains ordered H.264, AAC, and Opus filters;
- URL construction is deterministic and contains no credentials;
- configured restream failure does not silently return the direct ASF URL;
- camera/API failures remain secret-free.

### 27.4 Switch tests — **[V2.1 incorporated, V3 added]**

Cover:

- Camera access and camera share a device and have stable unique IDs;
- Camera access state/default, single persistence update, and one reload;
- Audio entity is absent without restream and present with restream;
- Audio and camera share a device; Audio unique ID is stable;
- Audio defaults off when first configured;
- Audio updates once/reloads once; unchanged state does nothing;
- master Camera access off prevents either Audio state from supplying media;
- Camera access cycle preserves the remembered Audio preference;
- removing restream removes Audio state/entity after reload;
- neither switch claims or calls a camera-side control.

### 27.5 Reference restream tests — **[V3 added]**

If the repository ships helper/templates, cover the smallest security-critical
surface:

- syntax/config validation without a physical camera;
- no password or credential URL in process arguments or output;
- H.264 uses copy and no video encoder;
- audio maps to AAC first and Opus second with specified parameters;
- timeout/termination cleans up child processes;
- expected curl 23 downstream-close handling is not treated as camera failure;
- failures emit only sanitized category and process status.

Do not turn physical media behavior into a large mocked process framework.
Use the physical verification in section 28 for the actual codec pipeline.

## 28. Physical verification

Automated tests cannot prove camera, browser, network, or audio behavior. A
sanitized result is required before release.

### 28.1 Preserve baseline behavior

Through HACS on the physical camera, verify setup, identity, firmware,
snapshot, direct video before audio opt-in, reload, restart, unload/disable,
deletion, reauthentication, reconfiguration, and secret-free logs.

### 28.2 Camera access

Verify that off blocks new snapshots/streams, terminates an already active
HLS/WebRTC session, persists through reload/restart, and on restores operation.
Also confirm explicitly that another client/vendor app remains unaffected so
the documented integration-only privacy boundary is accurate.

### 28.3 Restream boundary

Record sanitized versions of Home Assistant, go2rtc, FFmpeg, browser/client,
and platform. Prove with a media probe:

- input ASF contains H.264 Main plus mono 8 kHz ADPCM;
- Audio-off RTSP contains H.264 and no audio;
- Audio-on RTSP contains copied H.264, AAC first, and Opus second;
- no video encoder runs and no media is stored;
- camera credentials are absent from process listings and normal/error logs.

### 28.4 HLS proof

Open the camera through Home Assistant's HLS path and verify visible video plus
audible, continuous audio for at least five minutes. Exercise Audio off/on
during an active view and prove that the old session stops and the new source
takes effect. Record startup latency, A/V sync, continuity, CPU, memory, and
process count.

### 28.5 WebRTC proof

With Home Assistant's supported go2rtc provider, open the same entity through
WebRTC in the supported frontend/browser. Prove negotiated H.264 plus Opus,
audible continuous audio for at least five minutes, Audio off/on behavior,
Camera access master-off behavior, restart recovery, and closed sessions on
unload. Record the same performance observations.

### 28.6 Failure proof

Stop the restream during viewing. Confirm clean session failure, continued
snapshot operation, no direct-source fallback, no secret leak, and recovery on
the next request after restart. Remove the restream option and prove deliberate
return to legacy direct video with the Audio entity removed.

Any failed HLS, WebRTC, switch, security, or cleanup requirement blocks final
`0.3.0`. Do not relabel an unverified path as supported.

## 29. HACS, CI, documentation, and release gates

### 29.1 HACS and CI — **[V2 unchanged]**

Keep the HACS custom-repository metadata, README, LICENSE, validated brand
assets, pinned GitHub Actions, and dependency updates. CI runs:

1. pytest against the pinned Home Assistant target;
2. Ruff/static checks;
3. HACS validation;
4. Hassfest validation.

### 29.2 README — **[V2 preserved, v2.1/v3 extended]**

Document only implemented behavior. Include all of:

1. Supported reer IP BabyCam 80300 and verified firmware.
2. Camera already connected to the trusted LAN.
3. How to determine/reserve its IP address.
4. HACS custom-repository installation and Home Assistant restart.
5. Home Assistant UI setup with camera host and password.
6. Fixed `admin`/port 80 behavior and normalized host rules.
7. Device identity, duplicate prevention, and firmware metadata.
8. On-demand JPEG snapshots.
9. Native live-video behavior.
10. Plain-HTTP/Digest security characteristics and no internet exposure.
11. Password reauthentication.
12. Same-camera host reconfiguration.
13. Authentication troubleshooting.
14. Connectivity/invalid-response troubleshooting.
15. Camera access guarantee and explicit physical-privacy limitation.
16. Audio as optional one-way listening only; no talkback.
17. The physically verified ADPCM source and why native HLS cannot use it.
18. Exact supported local restream deployment, pinned tested versions, secret
    file permissions, network isolation, and no stored media.
19. How to configure/remove the local RTSP restream option.
20. Audio access semantics and Camera access master relationship.
21. HLS and WebRTC requirements and supported-client results.
22. Expected demand-based CPU/latency behavior and observed release values.
23. Restream failure, restart, update, rollback, and removal procedures.
24. Sanitized support information and an explicit list of data never to share.

Do not imply that HACS installs go2rtc/FFmpeg, that either switch disables the
physical sensor/microphone, or that any unverified browser/deployment works.

### 29.3 Release gates

The `0.3.0` release candidate requires:

- final, physically verified `0.2.1` as its baseline;
- every required implementation issue for the milestone closed;
- complete automated checks and independent architecture verification;
- accurate manifest/README/release notes and immutable candidate tag;
- explicit user approval before tag creation or publication;
- HACS installation and all sanitized physical results from section 28.

Final `0.3.0` requires the exact final commit to pass Test, HACS, Hassfest, and
independent verification; zero open milestone deliverables; user acceptance
of HLS/WebRTC, latency/load, privacy wording, and secret handling; and explicit
approval before the final tag/release.

Published tags are immutable and never moved or reused.

## 30. Complete acceptance criteria

Version `0.3.0` is complete only when all are true:

- [ ] Installable and updateable as a HACS custom repository.
- [ ] Addable entirely through the Home Assistant UI with camera host/password.
- [ ] Digest identity, firmware, snapshot, and direct video contracts pass.
- [ ] Camera ID is config-entry identity; exactly one device/camera exists.
- [ ] Duplicate prevention, setup retry, reauthentication, and same-device host
      reconfiguration pass without secret leakage.
- [ ] Camera access persists, stops all integration media, and is documented as
      integration-only rather than physical privacy.
- [ ] Existing `0.2.x` entries upgrade without data migration or behavior loss.
- [ ] Audio remains absent and dependency-free until a valid local restream is
      explicitly configured.
- [ ] The one supported go2rtc deployment keeps camera credentials out of
      process arguments/logs and keeps all media local and unstored.
- [ ] H.264 is copied; ADPCM alone is converted to AAC and Opus.
- [ ] Audio-off restream exposes no audio; Audio-on exposes AAC first and Opus.
- [ ] Audio access is a separate persisted switch subordinate to Camera access.
- [ ] Home Assistant HLS delivers five minutes of continuous audible audio.
- [ ] Home Assistant WebRTC negotiates Opus and delivers five minutes of
      continuous audible audio.
- [ ] Toggle, active-session cleanup, restart, failure, and removal tests pass.
- [ ] Latency, A/V sync, CPU, memory, and process counts are recorded and
      explicitly accepted by the user with no resource exhaustion/dropouts.
- [ ] Passwords, Digest material, credential URLs, raw CGI bodies, and media do
      not appear in logs, exceptions, diagnostics, artifacts, or releases.
- [ ] README and release notes state every deployment and privacy limitation.
- [ ] Pytest, Ruff, HACS, Hassfest, and independent verification pass on the
      exact release commit.
- [ ] Physical HACS verification passes and the user approves publication.

## 31. Minimum implementation change set

**[V2 preserved, v2.1/v3 extended]**

The expected integration changes are limited to:

- `__init__.py`: forward/unload camera and switch platforms, preserve the
  one-reload listener, and stop media before unload/reload;
- `camera.py`: enforce Camera access and select the direct, video-only, or
  dual-audio source from persisted options;
- `config_flow.py`: add the narrow restream options flow without changing the
  existing setup, reauthentication, or reconfiguration contracts;
- `const.py`: add only the three implemented option keys;
- `switch.py`: implement Camera access and conditional Audio access without a
  speculative entity hierarchy;
- `manifest.json`: advance the release version only; add no runtime package;
- `strings.json` and `translations/en.json`: add accurate switch/options text;
- existing tests plus `test_switch.py` only if separation makes the suite
  clearer;
- README and release documentation;
- a minimal password-safe restream example only if it is required to make the
  supported external deployment reproducible.

`api.py` remains unchanged because `0.3.0` adds no camera endpoint. Do not
modify it merely to represent restream behavior.

## 32. Implementation-agent constraints

This architecture is authoritative and standalone for `0.3.0`.

Implement the smallest codebase that satisfies the documented contract. Keep
the current v2 code and tests unchanged except where Camera access, restream
source selection, Audio access, options, cleanup, translations, documentation,
or their direct coverage require a change.

If a current Home Assistant API differs from a mechanical detail here, make
the smallest compatibility adjustment, document it, and do not expand scope.
If the selected external restream cannot satisfy the security, HLS, or WebRTC
gates, stop and return to architecture; do not add an integration-managed
transcoder, generic backend interface, speculative camera endpoint, or silent
fallback.

When uncertain, prefer omission over abstraction or unverified behavior.

## 33. Primary implementation evidence

This architecture is based on:

- the verified camera HTTP/CGI behavior and firmware listed in section 3;
- sanitized `camera-audio-probe.py` output proving H.264 plus active ADPCM;
- sanitized `camera-audio-playback-test.py` process PASS and the user's
  audible, continuous 15-second physical PASS;
- installed Home Assistant 2026.8.3 stream worker code limiting HLS audio to
  AAC/MP3 and remuxing rather than transcoding;
- installed Home Assistant camera and go2rtc provider lifecycle code;
- official go2rtc 1.9.14 FFmpeg, codec-filter, RTSP, demand-start, and
  multi-audio-track documentation.

## 34. Supersession completeness map

This map is informational; the requirements above are authoritative. It
confirms that no earlier section must be consulted.

| Architecture v2 section | Represented in v3 |
| --- | --- |
| 1 Purpose | 1 |
| 2 Scope/exclusions | 2 |
| 3 Verified HTTP contract | 3 |
| 4 High-level architecture | 4 |
| 5 Repository structure | 5 |
| 6 Manifest | 6 |
| 7 Constants | 7 |
| 8 Runtime data | 8 |
| 9 CGI parsing | 9 |
| 10 API client | 10 |
| 11 API errors | 10 |
| 12 Config flow | 11.1 |
| 13 Reauthentication | 11.2 |
| 14 Reconfiguration | 11.3 |
| 15 Setup lifecycle | 12 |
| 16 Device registry | 13 |
| 17 Camera entity | 14–15 |
| 18 Security | 25 |
| 19 Translation | 26 |
| 20 Tests | 27 |
| 21 HACS/CI | 29.1 |
| 22 README | 29.2 |
| 23 Acceptance | 30 |
| 24 Agent constraints | 32 |

| Architecture v2.1 section | Represented in v3 |
| --- | --- |
| 1 Relationship/roadmap | 0–1, 22 |
| 2 Privacy semantics | 16, 25 |
| 3 Revised scope | 2 |
| 4 Minimal state | 8, 22 |
| 5 Camera access switch | 16, 21 |
| 6 Camera behavior off | 14–16 |
| 7 Future audio provision | 3.6, 17–24 |
| 8 Physical-control evidence gate | 16 |
| 9 Change set | 31 |
| 10 Tests | 27 |
| 11 Documentation/acceptance | 28–30 |

The former v2 bans on switches, audio conversion, and go2rtc-specific scope
are changed only as explicitly marked: two native access switches are now
allowed, while conversion remains entirely inside the one optional external
restream. The integration still implements no go2rtc API/process management,
WebRTC signaling, camera write command, or speculative protocol.
