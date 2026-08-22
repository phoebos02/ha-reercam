# reer IP BabyCam

Alpha Home Assistant custom integration for the reer IP BabyCam 80300.

This release is a placeholder: it creates an empty camera entity but does not
connect to the camera or provide images or video yet.

## Installation with HACS

You must already have [HACS](https://hacs.xyz/) installed.

**1. Add and download the repository**

[![Open your Home Assistant instance and add the reer IP BabyCam repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=phoebos02&repository=ha-reercam&category=integration)

Select your Home Assistant instance, add the repository, download **reer IP
BabyCam**, and restart Home Assistant. If HACS offers prereleases, select the
prerelease you intend to install before downloading.

**2. Add the integration after restarting**

[![Open your Home Assistant instance and start reer IP BabyCam setup](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=reer_babycam)

### Manual fallback

1. In HACS, open the three-dot menu and select **Custom repositories**.
2. Enter `https://github.com/phoebos02/ha-reercam`, select **Integration**, and
   choose **Add**.
3. Open **reer IP BabyCam**, select the intended prerelease if applicable, and
   choose **Download**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and select
   **reer IP BabyCam**.

See the [official HACS custom-repository instructions](https://hacs.xyz/docs/faq/custom_repositories/)
if the repository cannot be added with the button.
