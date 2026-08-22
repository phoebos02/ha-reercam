"""reer IP BabyCam integration."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
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
    except ReerBabyCamConnectionError as err:
        raise ConfigEntryNotReady("Could not connect to camera") from err
    except ReerBabyCamAuthError as err:
        raise ConfigEntryError("Camera authentication failed") from err
    except ReerBabyCamProtocolError as err:
        raise ConfigEntryError("Camera returned an invalid response") from err

    entry.runtime_data = ReerBabyCamRuntimeData(client, info)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ReerBabyCamConfigEntry
) -> bool:
    """Unload reer IP BabyCam."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
