"""Tests for the config-entry lifecycle."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResultType
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
DATA = {CONF_HOST: "camera.local", CONF_PASSWORD: "old-password"}


async def _user_flow(hass, user_input, result=INFO):
    flow = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    with patch(
        "custom_components.reer_babycam.ReerBabyCamClient.async_get_info",
        new=AsyncMock(side_effect=result if isinstance(result, Exception) else None,
                      return_value=None if isinstance(result, Exception) else result),
    ):
        return await hass.config_entries.flow.async_configure(
            flow["flow_id"], user_input=user_input
        )


async def _loaded_entry(hass) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=INFO.device_id)
    entry.add_to_hass(hass)
    with patch(
        "custom_components.reer_babycam.ReerBabyCamClient.async_get_info",
        new=AsyncMock(return_value=INFO),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


@pytest.mark.parametrize(
    ("host", "normalized"),
    [
        ("  CAMERA.Local. ", "camera.local"),
        ("2001:0db8:0:0:0:0:0:1", "2001:db8::1"),
    ],
)
async def test_user_form_validates_and_normalizes(hass, host, normalized) -> None:
    flow = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    schema = {
        key.schema: selector
        for key, selector in flow["data_schema"].schema.items()
    }
    assert set(schema) == {CONF_HOST, CONF_PASSWORD}
    assert schema[CONF_PASSWORD].config["type"] == "password"

    with patch(
        "custom_components.reer_babycam.ReerBabyCamClient.async_get_info",
        new=AsyncMock(return_value=INFO),
    ):
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            user_input={
                CONF_HOST: host,
                CONF_PASSWORD: "secret",
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "reer IP BabyCam"
    assert result["data"] == {
        CONF_HOST: normalized,
        CONF_PASSWORD: "secret",
    }
    assert result["result"].unique_id == INFO.device_id


@pytest.mark.parametrize(
    "host",
    [
        "",
        "http://camera.local",
        "admin@camera.local",
        "camera.local:80",
        "camera.local/path",
        "camera.local?query",
        "camera.local#fragment",
        "bad host",
    ],
)
async def test_user_rejects_invalid_host(hass, host) -> None:
    result = await _user_flow(
        hass, {CONF_HOST: host, CONF_PASSWORD: "secret"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_host"}


@pytest.mark.parametrize(
    ("failure", "error"),
    [
        (ReerBabyCamAuthError("secret"), "invalid_auth"),
        (ReerBabyCamConnectionError("secret"), "cannot_connect"),
        (ReerBabyCamProtocolError("secret"), "invalid_response"),
        (RuntimeError("secret"), "unknown"),
    ],
)
async def test_user_maps_errors_without_leaking(hass, caplog, failure, error) -> None:
    result = await _user_flow(hass, DATA, failure)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}
    assert "secret" not in caplog.text


async def test_user_rejects_duplicate_device(hass) -> None:
    MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=INFO.device_id).add_to_hass(
        hass
    )

    result = await _user_flow(hass, DATA)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    ("flow_name", "user_input", "expected_data", "reason"),
    [
        (
            "reauth",
            {CONF_PASSWORD: "new-password"},
            {CONF_HOST: "camera.local", CONF_PASSWORD: "new-password"},
            "reauth_successful",
        ),
        (
            "reconfigure",
            {CONF_HOST: " NEW-CAMERA.Local. "},
            {CONF_HOST: "new-camera.local", CONF_PASSWORD: "old-password"},
            "reconfigure_successful",
        ),
    ],
)
async def test_entry_update_succeeds_and_reloads_once(
    hass, caplog, flow_name, user_input, expected_data, reason
) -> None:
    if flow_name == "reauth":
        entry = MockConfigEntry(
            domain=DOMAIN, data=DATA, unique_id=INFO.device_id
        )
        entry.add_to_hass(hass)
        assert not entry.update_listeners
    else:
        entry = await _loaded_entry(hass)
    flow = await getattr(entry, f"start_{flow_name}_flow")(hass)
    expected_fields = {CONF_PASSWORD} if flow_name == "reauth" else {CONF_HOST}
    schema = {
        key.schema: selector
        for key, selector in flow["data_schema"].schema.items()
    }
    assert set(schema) == expected_fields
    if flow_name == "reauth":
        assert schema[CONF_PASSWORD].config["type"] == "password"

    with (
        patch(
            "custom_components.reer_babycam.ReerBabyCamClient.async_get_info",
            new=AsyncMock(return_value=INFO),
        ),
        patch.object(
            hass.config_entries,
            "async_reload",
            new=AsyncMock(return_value=True),
        ) as reload_entry,
    ):
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], user_input=user_input
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == reason
    assert dict(entry.data) == expected_data
    reload_entry.assert_awaited_once_with(entry.entry_id)
    assert "2026.12" not in caplog.text


@pytest.mark.parametrize(
    ("flow_name", "user_input", "reason"),
    [
        ("reauth", {CONF_PASSWORD: "old-password"}, "reauth_successful"),
        ("reconfigure", {CONF_HOST: "camera.local"}, "reconfigure_successful"),
    ],
)
async def test_unchanged_entry_update_does_not_reload(
    hass, caplog, flow_name, user_input, reason
) -> None:
    if flow_name == "reauth":
        entry = MockConfigEntry(
            domain=DOMAIN, data=DATA, unique_id=INFO.device_id
        )
        entry.add_to_hass(hass)
        assert not entry.update_listeners
    else:
        entry = await _loaded_entry(hass)
    flow = await getattr(entry, f"start_{flow_name}_flow")(hass)

    with (
        patch(
            "custom_components.reer_babycam.ReerBabyCamClient.async_get_info",
            new=AsyncMock(return_value=INFO),
        ),
        patch.object(
            hass.config_entries,
            "async_reload",
            new=AsyncMock(return_value=True),
        ) as reload_entry,
    ):
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], user_input=user_input
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == reason
    assert dict(entry.data) == DATA
    reload_entry.assert_not_awaited()
    assert "2026.12" not in caplog.text


@pytest.mark.parametrize(
    ("flow_name", "user_input", "result", "error"),
    [
        (
            "reauth",
            {CONF_PASSWORD: "bad-password"},
            ReerBabyCamAuthError("bad-password"),
            "invalid_auth",
        ),
        (
            "reauth",
            {CONF_PASSWORD: "new-password"},
            ReerBabyCamInfo("other-camera", None),
            "wrong_device",
        ),
        (
            "reconfigure",
            {CONF_HOST: "offline.local"},
            ReerBabyCamConnectionError("old-password"),
            "cannot_connect",
        ),
        (
            "reconfigure",
            {CONF_HOST: "other.local"},
            ReerBabyCamInfo("other-camera", None),
            "wrong_device",
        ),
    ],
)
async def test_entry_update_failure_changes_nothing(
    hass, caplog, flow_name, user_input, result, error
) -> None:
    entry = await _loaded_entry(hass)
    flow = await getattr(entry, f"start_{flow_name}_flow")(hass)
    original = dict(entry.data)

    with (
        patch(
            "custom_components.reer_babycam.ReerBabyCamClient.async_get_info",
            new=AsyncMock(
                side_effect=result if isinstance(result, Exception) else None,
                return_value=None if isinstance(result, Exception) else result,
            ),
        ),
        patch.object(
            hass.config_entries, "async_reload", new=AsyncMock(return_value=True)
        ) as reload_entry,
    ):
        response = await hass.config_entries.flow.async_configure(
            flow["flow_id"], user_input=user_input
        )
        await hass.async_block_till_done()

    assert response["type"] is FlowResultType.FORM
    assert response["errors"] == {"base": error}
    assert dict(entry.data) == original
    reload_entry.assert_not_awaited()
    assert "bad-password" not in caplog.text
    assert "old-password" not in caplog.text


async def test_reconfigure_rejects_invalid_host(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=INFO.device_id)
    entry.add_to_hass(hass)
    flow = await entry.start_reconfigure_flow(hass)

    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"], user_input={CONF_HOST: "camera.local:80"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_host"}
    assert dict(entry.data) == DATA
