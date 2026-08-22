"""Tests for the existing Home Assistant config-entry and camera behavior."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientConnectionError
from homeassistant.components.camera.const import DATA_COMPONENT
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PASSWORD, STATE_UNAVAILABLE
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.reer_babycam.api import (
    ReerBabyCamAuthError,
    ReerBabyCamConnectionError,
    ReerBabyCamInfo,
    ReerBabyCamProtocolError,
)
from custom_components.reer_babycam.const import DOMAIN

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")

INFO = ReerBabyCamInfo("camera-1", "42.7.3.4.70")
DATA = {CONF_HOST: "camera.local", CONF_PASSWORD: "do-not-leak"}
JPEG = b"\xff\xd8jpeg\xff\xd9"


async def _setup(hass, info: ReerBabyCamInfo = INFO) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=DATA)
    entry.add_to_hass(hass)
    with patch(
        "custom_components.reer_babycam.ReerBabyCamClient.async_get_info",
        new=AsyncMock(return_value=info),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


async def test_setup_camera_device_snapshot_stream_and_unload(hass) -> None:
    entry = await _setup(hass)

    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data.info == INFO

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "camera", DOMAIN, "camera-1_camera"
    )
    assert entity_id is not None
    entity_entry = entity_registry.async_get(entity_id)
    assert entity_entry is not None
    assert entity_entry.unique_id == "camera-1_camera"
    assert er.async_entries_for_config_entry(entity_registry, entry.entry_id) == [
        entity_entry
    ]

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(
        identifiers={(DOMAIN, "camera-1")}
    )
    assert device is not None
    assert dr.async_entries_for_config_entry(device_registry, entry.entry_id) == [
        device
    ]
    assert entity_entry.device_id == device.id
    assert device.manufacturer == "reer"
    assert device.model == "IP BabyCam 80300"
    assert device.name == "reer IP BabyCam"
    assert device.serial_number == "camera-1"
    assert device.sw_version == "42.7.3.4.70"

    camera = hass.data[DATA_COMPONENT].get_entity(entity_id)
    assert camera is not None
    with patch.object(
        entry.runtime_data.client,
        "async_get_snapshot",
        new=AsyncMock(return_value=JPEG),
    ):
        assert await camera.async_camera_image() == JPEG
    assert await camera.stream_source() == (
        "http://admin:do-not-leak@camera.local/av.asf?stream=1"
    )

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert hass.data[DATA_COMPONENT].get_entity(entity_id) is None
    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE


async def test_optional_firmware(hass) -> None:
    await _setup(hass, ReerBabyCamInfo("camera-2", None))
    device = dr.async_get(hass).async_get_device(
        identifiers={(DOMAIN, "camera-2")}
    )
    assert device is not None
    assert device.sw_version is None


@pytest.mark.parametrize(
    ("failure", "error_type", "message"),
    [
        ("auth", ReerBabyCamAuthError, "rejected"),
        ("connection", ReerBabyCamConnectionError, "connect"),
    ],
)
async def test_snapshot_errors_are_secret_free(
    hass, caplog, failure, error_type, message
) -> None:
    entry = await _setup(hass)
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "camera", DOMAIN, "camera-1_camera"
    )
    camera = hass.data[DATA_COMPONENT].get_entity(entity_id)
    assert camera is not None

    secret_error = "lower-level-secret http://admin:do-not-leak@camera.local/"
    if failure == "auth":
        response = MagicMock(status=401)
        request = MagicMock()
        request.__aenter__ = AsyncMock(return_value=response)
        get = MagicMock(return_value=request)
    else:
        get = MagicMock(side_effect=ClientConnectionError(secret_error))

    with patch.object(entry.runtime_data.client._session, "get", get):
        with pytest.raises(error_type, match=message) as error:
            await camera.async_camera_image()

    output = f"{error.value}\n{caplog.text}"
    assert DATA[CONF_PASSWORD] not in output
    assert "http://admin:do-not-leak@camera.local/" not in output
    assert "lower-level-secret" not in output


@pytest.mark.parametrize(
    ("error", "state"),
    [
        (ReerBabyCamConnectionError("do-not-leak"), ConfigEntryState.SETUP_RETRY),
        (ReerBabyCamAuthError("do-not-leak"), ConfigEntryState.SETUP_ERROR),
        (ReerBabyCamProtocolError("do-not-leak"), ConfigEntryState.SETUP_ERROR),
    ],
)
async def test_setup_error_mapping_is_secret_free(hass, caplog, error, state) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data=DATA)
    entry.add_to_hass(hass)

    with patch(
        "custom_components.reer_babycam.ReerBabyCamClient.async_get_info",
        new=AsyncMock(side_effect=error),
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is state
    assert "do-not-leak" not in caplog.text
