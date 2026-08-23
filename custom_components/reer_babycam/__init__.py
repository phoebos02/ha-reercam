"""reer IP BabyCam integration."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryError,
    ConfigEntryNotReady,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    ReerBabyCamAuthError,
    ReerBabyCamClient,
    ReerBabyCamConnectionError,
    ReerBabyCamInfo,
    ReerBabyCamProtocolError,
)

PLATFORMS = [Platform.CAMERA]


@dataclass(slots=True)
class ReerBabyCamRuntimeData:
    """Data used while a config entry is loaded."""

    client: ReerBabyCamClient
    info: ReerBabyCamInfo


type ReerBabyCamConfigEntry = ConfigEntry[ReerBabyCamRuntimeData]


async def async_setup_entry(
    hass: HomeAssistant, entry: ReerBabyCamConfigEntry
) -> bool:
    """Set up reer IP BabyCam."""
    try:
        client = ReerBabyCamClient(
            entry.data[CONF_HOST],
            entry.data[CONF_PASSWORD],
            async_get_clientsession(hass),
        )
    except KeyError as err:
        raise ConfigEntryError(
            "Entry is missing connection details; remove and add it again"
        ) from err

    try:
        info = await client.async_get_info()
    except ReerBabyCamConnectionError:
        raise ConfigEntryNotReady("Could not connect to camera") from None
    except ReerBabyCamAuthError:
        raise ConfigEntryAuthFailed("Camera authentication failed") from None
    except ReerBabyCamProtocolError:
        raise ConfigEntryError("Camera returned an invalid response") from None

    if not entry.unique_id or info.device_id != entry.unique_id:
        raise ConfigEntryError("Camera identity does not match config entry")

    entry.runtime_data = ReerBabyCamRuntimeData(client, info)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: ReerBabyCamConfigEntry
) -> None:
    """Reload after config-entry data changes."""
    hass.config_entries.async_schedule_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant, entry: ReerBabyCamConfigEntry
) -> bool:
    """Unload reer IP BabyCam."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
