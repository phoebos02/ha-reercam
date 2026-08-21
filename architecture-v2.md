# reer IP BabyCam Home Assistant Custom Integration — Architecture Specification v2

**Status:** Implementation architecture
**Architecture version:** 2
**Target Home Assistant:** 2026.8+
**Distribution:** HACS custom integration
**Integration domain:** `reer_babycam`
**Supported device:** reer IP BabyCam 80300
**Verified firmware:** `42.7.3.4.70`
**Protocol basis:** Verified local HTTP/CGI behavior on the supported camera

## 1. Purpose

Implement the smallest useful Home Assistant custom integration for the verified reer IP BabyCam 80300.

Version 1 of the integration has one purpose: expose the camera as a native Home Assistant camera entity using the local HTTP interface already verified on the physical device.

The architecture deliberately favors a narrow implementation over generality. Only behavior required for configuration, identity, still images, and live video is included.

## 2. Hard scope boundaries and explicit exclusions

These are architectural constraints, not backlog items for this version. The implementation agent must not follow, probe, generalize, or implement any of these paths unless a later architecture revision explicitly adds them.

### Protocol and connectivity

* No TCP port `2345`.
* No vendor cloud access.
* No P2P access or SoSoCam connectivity.
* No ReeCam push service.
* No automatic network discovery.
* No generic ReeCam or SoSoCam compatibility layer.
* No protocol probing beyond the verified HTTP endpoints defined in this document.
* No separate protocol package or reusable external Python library.

### Camera control and device configuration

* No PTZ.
* No write CGI calls.
* No `set_params.cgi`.
* No motion or sound configuration.
* No IR or night-mode control.
* No recording management.
* No SMB management.
* No firmware-management functionality.
* No services, buttons, switches, selects, numbers, or other control entities.

### Media

* No two-way audio.
* No audio transcoding.
* No RTSP emulation.
* No WebRTC implementation.
* No go2rtc-specific implementation.
* No alternate or arbitrary stream-profile support.
* No SD/HD selector.
* No stream-profile options flow.

### Home Assistant surface

* No diagnostic sensors.
* No status sensors.
* No continuous status polling.
* No `DataUpdateCoordinator`.
* No diagnostics endpoint.
* No YAML configuration.
* No repair issues.
* No custom WebSocket API.
* No media-source integration.
* No event entities.
* No entity base-class hierarchy for hypothetical future entities.

### Implementation complexity

* No snapshot cache.
* No speculative request serialization or global request lock.
* No migration framework beyond config-entry version `1`.
* No secondary language in the initial implementation.
* No functionality that exists only to support hypothetical future devices or features.

## 3. Verified HTTP contract

The implementation may rely only on the following verified behavior.

### 3.1 HTTP service

The camera exposes an HTTP service on TCP port `80`.

Observed server:

```text
Boa/0.94.14rc21
```

Protected camera endpoints use HTTP Digest authentication with:

```text
realm = "ip camera"
qop = "auth"
algorithm = MD5
```

The supported integration uses:

```text
username = admin
port = 80
```

Both values are fixed constants in version 1.

The user supplies only:

```text
host
password
```

### 3.2 Device identity

Endpoint:

```text
GET /get_params.cgi
```

The authenticated response contains JavaScript-style variable assignments.

Version 1 extracts exactly one field:

```text
id
```

Example form:

```text
var id='...';
```

The value is the stable physical-device identifier used by Home Assistant.

The raw response must not be stored.

### 3.3 Device metadata

Endpoint:

```text
GET /get_properties.cgi
```

Version 1 extracts exactly one field:

```text
firmware_ver
```

Example form:

```text
var firmware_ver='42.7.3.4.70';
```

The raw response must not be stored.

### 3.4 Snapshot

Endpoint:

```text
GET /snapshot.cgi
```

Authentication:

```text
HTTP Digest
```

Verified response:

```text
Content-Type: image/jpeg
```

Observed image:

```text
1280x720 JPEG
```

The integration passes the returned JPEG bytes directly to Home Assistant.

### 3.5 Live stream

Endpoint:

```text
GET /av.asf?stream=1
```

Authentication:

```text
HTTP Digest
```

Verified media:

```text
ASF container
H.264 Main video
1280x720
approximately 15 fps
```

Version 1 always uses:

```text
stream=1
```

The integration returns the camera source URL to Home Assistant's native camera stream subsystem.

## 4. High-level architecture

```text
Home Assistant
│
├── Config Flow
│    └── ReerBabyCamClient
│         ├── GET /get_params.cgi
│         │    └── extract id
│         └── GET /get_properties.cgi
│              └── extract firmware_ver
│
├── ConfigEntry[ReerBabyCamRuntimeData]
│    ├── client
│    └── device_info
│
└── Camera Entity
     ├── async_camera_image()
     │    └── GET /snapshot.cgi
     │
     └── stream_source()
          └── /av.asf?stream=1
               └── Home Assistant stream subsystem
```

## 5. Repository structure

```text
repo-root/
├── custom_components/
│   └── reer_babycam/
│       ├── __init__.py
│       ├── api.py
│       ├── camera.py
│       ├── config_flow.py
│       ├── const.py
│       ├── manifest.json
│       ├── models.py
│       └── translations/
│           └── en.json
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   ├── test_api.py
│   ├── test_camera.py
│   └── test_config_flow.py
├── .github/
│   └── workflows/
│       ├── hacs.yml
│       ├── hassfest.yml
│       └── tests.yml
├── hacs.json
├── pyproject.toml
├── README.md
├── LICENSE
└── architecture-v2.md
```

Files should be added only when required by the implementation or validation tooling.

## 6. Manifest

Target `manifest.json`:

```json
{
  "domain": "reer_babycam",
  "name": "reer IP BabyCam",
  "version": "0.1.0",
  "config_flow": true,
  "dependencies": ["http", "stream"],
  "documentation": "<repository documentation URL>",
  "issue_tracker": "<repository issues URL>",
  "codeowners": ["<GitHub username>"],
  "integration_type": "device",
  "iot_class": "local_polling"
}
```

No additional runtime Python dependency should be added unless Home Assistant's built-in HTTP stack cannot satisfy a verified requirement.

## 7. Constants

`const.py` should contain only stable integration constants required by version 1.

Conceptually:

```python
DOMAIN = "reer_babycam"

DEFAULT_PORT = 80
DEFAULT_USERNAME = "admin"

SNAPSHOT_PATH = "/snapshot.cgi"
STREAM_PATH = "/av.asf?stream=1"
PARAMS_PATH = "/get_params.cgi"
PROPERTIES_PATH = "/get_properties.cgi"

CONF_HOST = "host"
CONF_PASSWORD = "password"
```

Avoid constants for unimplemented camera capabilities.

## 8. Runtime data model

Use small typed dataclasses.

Conceptually:

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

Typed config-entry alias:

```python
type ReerBabyCamConfigEntry = ConfigEntry[ReerBabyCamRuntimeData]
```

No generic camera-capability model is required.

## 9. CGI parsing

The two configuration endpoints return JavaScript-style assignments such as:

```text
var id='example';
var firmware_ver='42.7.3.4.70';
```

The parser exists only to extract the two required string values.

Requirements:

1. Parse response text line-by-line.
2. Recognize only the exact requested variable names.
3. Parse quoted string values safely.
4. Never use `eval`.
5. Ignore unrelated variables.
6. Reject a response when a required value is absent or malformed.
7. Discard the original response immediately after extraction.
8. Never return a generic dictionary of camera configuration.

A small dedicated helper is preferable to a general JavaScript-variable parser.

## 10. API client

`api.py` owns the verified HTTP protocol.

Conceptual public interface:

```python
class ReerBabyCamClient:
    async def async_get_info(self) -> ReerBabyCamInfo: ...
    async def async_get_snapshot(self) -> bytes: ...
    def stream_url(self) -> URL: ...
```

### 10.1 Construction

The client receives:

```text
host
password
Home Assistant-managed async HTTP client
```

It internally uses the fixed:

```text
port = 80
username = admin
```

### 10.2 Authentication

Use HTTP Digest authentication.

Prefer Home Assistant's managed asynchronous HTTP facilities and their supported authentication mechanism.

Do not create a long-lived unmanaged global HTTP session.

### 10.3 `async_get_info()`

Sequence:

```text
GET /get_params.cgi
    → authenticate
    → extract id

GET /get_properties.cgi
    → authenticate
    → extract firmware_ver
```

Return:

```python
ReerBabyCamInfo(
    device_id=...,
    firmware_version=...,
)
```

Requirements:

* `device_id` is mandatory.
* `firmware_version` may be absent.
* Do not retain either raw CGI body.

### 10.4 `async_get_snapshot()`

Request:

```text
GET /snapshot.cgi
```

Validate:

* successful HTTP status
* content type compatible with JPEG
* non-empty response body

Return the JPEG bytes unchanged.

### 10.5 `stream_url()`

Produce the verified source:

```text
http://<encoded-user>:<encoded-password>@<host>:80/av.asf?stream=1
```

Use a URL-construction library so credentials and host data are encoded safely.

The credential-bearing URL is runtime-only and must not be stored in the config entry.

## 11. API errors

Define a minimal exception hierarchy:

```text
ReerBabyCamError
├── ReerBabyCamConnectionError
├── ReerBabyCamAuthError
└── ReerBabyCamProtocolError
```

Mapping:

```text
401 / 403
    → ReerBabyCamAuthError

timeout / DNS failure / connection refused
    → ReerBabyCamConnectionError

unexpected or malformed verified response
    → ReerBabyCamProtocolError
```

Exception messages must not contain the password or credential-bearing URLs.

## 12. Config flow

Configuration is UI-only.

### 12.1 User step

Fields:

| Field    | Required | Stored             |
| -------- | -------: | ------------------ |
| Host     |      Yes | `ConfigEntry.data` |
| Password |      Yes | `ConfigEntry.data` |

Validation sequence:

1. Normalize the host.
2. Create the protocol client.
3. Call `async_get_info()`.
4. Require a non-empty camera `id`.
5. Set config-entry unique ID to the camera `id`.
6. Abort duplicate creation.
7. Create the config entry.

Config entry title:

```text
reer IP BabyCam
```

or, if Home Assistant conventions prefer a more useful generated title:

```text
reer IP BabyCam <short-device-id>
```

### 12.2 Errors

Map failures to:

```text
cannot_connect
invalid_auth
invalid_response
unknown
```

User-visible errors must not include raw protocol responses.

## 13. Reauthentication

Implement Home Assistant's normal reauthentication flow.

User input:

```text
password
```

Validation:

1. Create a client with the existing host and new password.
2. Fetch device info.
3. Confirm that the returned device ID matches the config entry unique ID.
4. Update the stored password.
5. Reload the config entry.

A different physical camera must not be accepted as credential replacement.

## 14. Reconfiguration

Implement Home Assistant's reconfigure flow for:

```text
host
```

Validation:

1. Use the existing password with the proposed host.
2. Fetch device info.
3. Confirm that the returned device ID matches the existing unique ID.
4. Update the stored host.
5. Reload the config entry.

This is the supported mechanism for DHCP/address changes.

## 15. Setup lifecycle

`async_setup_entry()`:

1. Obtain the Home Assistant-managed async HTTP client.
2. Instantiate `ReerBabyCamClient`.
3. Fetch `ReerBabyCamInfo`.
4. Verify that the device ID still matches the config-entry unique ID.
5. Store `ReerBabyCamRuntimeData` in `entry.runtime_data`.
6. Forward setup to the `camera` platform.
7. Register the entry update listener required by Home Assistant conventions.

Authentication failure during setup must trigger Home Assistant reauthentication behavior.

Transient connection failure during setup must use Home Assistant's normal config-entry retry behavior.

`async_unload_entry()` unloads the camera platform cleanly.

## 16. Device registry

Create one Home Assistant device.

Conceptually:

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

The camera `id` is the authoritative identifier.

The IP address is connection data, not identity.

## 17. Camera entity

Create exactly one entity.

Unique ID:

```text
<device_id>_camera
```

Recommended behavior:

```python
_attr_has_entity_name = True
_attr_name = None
```

The entity belongs to the single device registry entry.

### 17.1 Still image

Implement:

```python
async_camera_image()
```

It calls:

```python
client.async_get_snapshot()
```

and returns the JPEG bytes.

### 17.2 Live video

Advertise Home Assistant's camera stream capability.

Implement:

```python
stream_source()
```

It returns:

```python
client.stream_url()
```

The URL corresponds to:

```text
/av.asf?stream=1
```

The Home Assistant stream subsystem owns downstream stream handling.

### 17.3 Availability

Do not introduce a separate background liveness mechanism.

Network failures encountered during actual camera operations are handled through the normal camera/API error path.

## 18. Security and secret handling

The config entry stores:

```text
host
password
```

The password is secret.

Never log:

* password
* Digest authorization material
* credential-bearing stream URL
* raw response bodies from the configuration endpoints

The stream URL containing credentials exists only transiently at runtime.

HTTP redirects must not cause credentials to be forwarded to a different host.

The integration documentation must explain that the camera protocol uses plain HTTP on the local network.

## 19. Translation

Initial implementation supplies:

```text
custom_components/reer_babycam/translations/en.json
```

Translate:

* integration title
* config-flow labels
* config-flow errors
* reauthentication flow
* reconfiguration flow

Do not hard-code user-facing config-flow text in Python.

## 20. Tests

Tests should focus on the actual version-1 contract.

### 20.1 API tests

Cover:

* valid Digest-authenticated identity request
* valid firmware request
* valid snapshot
* authentication failure
* timeout
* connection failure
* malformed identity response
* missing device ID
* malformed firmware response
* safe stream URL generation
* credentials containing URL-reserved characters
* secret-free exception messages

### 20.2 Config-flow tests

Cover:

* successful setup
* invalid password
* connection failure
* invalid protocol response
* duplicate device ID
* successful reauthentication
* failed reauthentication
* reauthentication against a different device
* successful host reconfiguration
* failed host reconfiguration
* host reconfiguration against a different device

### 20.3 Camera tests

Cover:

* one camera entity created
* stable unique ID
* correct device-registry association
* firmware metadata
* snapshot bytes returned
* verified stream URL returned
* authentication/connection errors handled without leaking secrets

## 21. HACS and CI

The repository must be usable as a HACS custom repository.

Root metadata should include:

```text
hacs.json
README.md
LICENSE
```

Continuous integration runs:

1. unit tests
2. lint/static checks
3. HACS validation
4. Hassfest validation

Initial release:

```text
0.1.0
```

## 22. README requirements

Document only the implemented integration.

Include:

1. Supported device: reer IP BabyCam 80300.
2. Verified firmware.
3. Requirement that the camera already be connected to the LAN.
4. How to determine the camera IP address.
5. HACS custom-repository installation.
6. Home Assistant UI setup.
7. Required host and camera password.
8. Snapshot behavior.
9. Live-video behavior.
10. Plain-HTTP security characteristic.
11. Reauthentication procedure.
12. Reconfiguration after an IP-address change.
13. Troubleshooting authentication errors.
14. Troubleshooting connectivity errors.

Do not document functionality outside version-1 scope.

## 23. Acceptance criteria

Version `0.1.0` is complete when all of the following are true:

* [ ] Installable as a HACS custom repository.
* [ ] Addable entirely through the Home Assistant UI.
* [ ] User supplies only host and password.
* [ ] HTTP Digest authentication works.
* [ ] Camera `id` becomes the config-entry unique ID.
* [ ] Exactly one Home Assistant device is created.
* [ ] Exactly one camera entity is created.
* [ ] Firmware version appears in device metadata when available.
* [ ] `/snapshot.cgi` provides the Home Assistant still image.
* [ ] `/av.asf?stream=1` provides the Home Assistant live source.
* [ ] Password changes can be resolved through reauthentication.
* [ ] IP-address changes can be resolved through reconfiguration.
* [ ] Raw configuration responses are never persisted.
* [ ] Passwords and credential-bearing URLs do not appear in logs or exceptions.
* [ ] Automated tests pass.
* [ ] HACS validation passes.
* [ ] Hassfest validation passes.

## 24. Implementation-agent constraints

This architecture is authoritative for version `0.1.0`.

The implementation agent should implement the smallest codebase that satisfies the documented contract and acceptance criteria.

If a current Home Assistant API differs from a mechanical detail in this document, the implementation agent may make the smallest necessary compatibility adjustment. It must document that adjustment and must not expand functional scope while doing so.

When uncertain, prefer omission over abstraction or speculative functionality.
