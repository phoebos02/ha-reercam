# Home Assistant integration for reer IP BabyCam

[![Release](https://img.shields.io/github/v/release/phoebos02/ha-reercam?sort=semver)](https://github.com/phoebos02/ha-reercam/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](#installation-with-hacs)
[![HACS validation](https://github.com/phoebos02/ha-reercam/actions/workflows/hacs.yml/badge.svg)](https://github.com/phoebos02/ha-reercam/actions/workflows/hacs.yml)
[![Hassfest validation](https://github.com/phoebos02/ha-reercam/actions/workflows/hassfest.yml/badge.svg)](https://github.com/phoebos02/ha-reercam/actions/workflows/hassfest.yml)
[![Tests](https://github.com/phoebos02/ha-reercam/actions/workflows/test.yml/badge.svg)](https://github.com/phoebos02/ha-reercam/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/phoebos02/ha-reercam)](LICENSE)

Version 0.2.0-rc supports the reer IP BabyCam 80300 and is verified with
firmware `42.7.3.4.70`.

> [!WARNING]
> The camera uses HTTP Digest authentication over plain HTTP. Authentication
> does not encrypt the video, snapshots, or authentication exchange. Keep the
> camera on a trusted local network and never expose its HTTP port to the
> internet.

## Features

- One local camera entity and device; no cloud account required.
- Validated Home Assistant UI setup with physical-device duplicate prevention.
- JPEG snapshots fetched on demand.
- The verified ASF/H.264 `stream=1` source through Home Assistant's native
  camera stream subsystem.
- Password reauthentication and same-camera host reconfiguration.
- No sound, recording, motion, PTZ, settings, discovery, or additional
  entities.

## Before installation

Connect the camera to the same trusted LAN as Home Assistant first. Find its
address in your router's DHCP lease or connected-device list, then reserve that
address in DHCP. A stable local DNS hostname is also suitable. This integration
does not discover or connect the camera to Wi-Fi.

## Installation with HACS

You must already have [HACS](https://hacs.xyz/) installed.

[![Open your Home Assistant instance and add the reer IP BabyCam repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=phoebos02&repository=ha-reercam&category=integration)

Select your Home Assistant instance, add the repository, download **reer IP
BabyCam**, and restart Home Assistant.

[![Open your Home Assistant instance and start reer IP BabyCam setup](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=reer_babycam)

See the [official HACS custom-repository instructions](https://hacs.xyz/docs/faq/custom_repositories/)
if the repository cannot be added with the button.

For updates, open **reer IP BabyCam** in HACS, install the offered update, and
restart Home Assistant.

## Configuration

Go to **Settings → Devices & services → Add integration** and select **reer IP
BabyCam**. Enter:

- **Host:** the camera's bare hostname or IP address. Do not include a URL
  scheme, credentials, port, path, query, or fragment. Harmless whitespace,
  hostname case, a trailing dot, and IP notation are normalized.
- **Password:** the password for the camera's fixed `admin` user.

Setup contacts the camera before saving. Its physical camera ID becomes the
config-entry identity, so the same camera cannot be added twice. Only the
normalized host and password are stored.

## Change the password or address

- **Password:** Follow Home Assistant's reauthentication prompt in **Settings
  → Devices & services** and enter the camera's current `admin` password.
- **Host:** Open the integration entry in **Settings → Devices & services**,
  choose **Reconfigure**, and enter the new bare hostname or IP address. The
  existing password is reused.

Both flows require the original physical camera and reload the entry once
after a successful change.

## Troubleshooting

### Authentication

Confirm that the password belongs to the camera's `admin` user. If the camera
password changed, complete Home Assistant's reauthentication prompt. A wrong
password or a different physical camera is rejected without changing the
saved entry.

### Connectivity or invalid response

- Confirm that Home Assistant can reach the camera on the same LAN and that
  the saved host still matches its DHCP lease or local DNS name.
- Enter only a bare hostname or IP address; the camera protocol uses fixed HTTP
  port 80.
- Restart Home Assistant after installing or updating through HACS.
- An invalid-response error means the address did not return the expected reer
  camera identity or firmware data. Check that it points to a supported reer IP
  BabyCam 80300; firmware `42.7.3.4.70` is the verified version.

## Support

Report problems through [GitHub Issues](https://github.com/phoebos02/ha-reercam/issues).
Include the integration and Home Assistant versions plus sanitized logs. Never
include the camera password, Digest authorization header, raw CGI response, or
a URL containing credentials.

## Disclaimer

reer and IP BabyCam are trademarks of their respective owners. This project is
independent and is not affiliated with, endorsed by, or supported by reer.

## License

This project is licensed under the [MIT License](LICENSE).
