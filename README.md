# Home Assistant integration for reer IP BabyCam

[![Release](https://img.shields.io/github/v/release/phoebos02/ha-reercam?sort=semver)](https://github.com/phoebos02/ha-reercam/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](#installation-with-hacs)
[![HACS validation](https://github.com/phoebos02/ha-reercam/actions/workflows/hacs.yml/badge.svg)](https://github.com/phoebos02/ha-reercam/actions/workflows/hacs.yml)
[![Hassfest validation](https://github.com/phoebos02/ha-reercam/actions/workflows/hassfest.yml/badge.svg)](https://github.com/phoebos02/ha-reercam/actions/workflows/hassfest.yml)
[![Tests](https://github.com/phoebos02/ha-reercam/actions/workflows/test.yml/badge.svg)](https://github.com/phoebos02/ha-reercam/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/phoebos02/ha-reercam)](LICENSE)

Home Assistant custom integration for the reer IP BabyCam 80300.

Version 0.1.0-rc.1 connects to the camera over the local network and provides
snapshots and live video through a Home Assistant camera entity.

## Features

- Local-network connection; no cloud account required.
- JPEG snapshots and live video from the camera's ASF stream.
- Home Assistant UI setup through a config flow.
- Camera ID and firmware version when exposed by the camera.

## Installation with HACS

You must already have [HACS](https://hacs.xyz/) installed.

**1. Add and download the repository**

[![Open your Home Assistant instance and add the reer IP BabyCam repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=phoebos02&repository=ha-reercam&category=integration)

Select your Home Assistant instance, add the repository, download **reer IP
BabyCam**, and restart Home Assistant.

**2. Add the integration after restarting**

[![Open your Home Assistant instance and start reer IP BabyCam setup](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=reer_babycam)

### Manual fallback

1. In HACS, open the three-dot menu and select **Custom repositories**.
2. Enter `https://github.com/phoebos02/ha-reercam`, select **Integration**, and
   choose **Add**.
3. Open **reer IP BabyCam** and choose **Download**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and select
   **reer IP BabyCam**.

See the [official HACS custom-repository instructions](https://hacs.xyz/docs/faq/custom_repositories/)
if the repository cannot be added with the button.

## Configuration

During setup, enter the camera's local hostname or IP address and the password
for its `admin` user. Version 0.1.0-rc.1 stores these values before contacting the
camera; the config form does not yet validate the connection. Use a DHCP
reservation or static IP address so Home Assistant can continue to find the
camera after network changes.

## Requirements and status

- It currently supports the reer IP BabyCam 80300.
- The camera must be reachable from Home Assistant on the local network.
- Camera traffic uses authenticated plain HTTP and should remain on a trusted
  local network.
- Camera identity and duplicate entries are not checked in the config form.
- Reauthentication and host reconfiguration flows are not available yet.

## Support

Report problems through [GitHub Issues](https://github.com/phoebos02/ha-reercam/issues).
Include the integration and Home Assistant versions plus sanitized logs. Never
include the camera password or a stream URL containing credentials.

## Disclaimer

reer and IP BabyCam are trademarks of their respective owners. This project is
independent and is not affiliated with, endorsed by, or supported by reer.

## License

This project is licensed under the [MIT License](LICENSE).
