"""Tests for the current unvalidated config flow boundary."""

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResultType

from custom_components.reer_babycam.const import DOMAIN

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_user_form_and_entry_creation(hass) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    schema = {
        key.schema: selector
        for key, selector in result["data_schema"].schema.items()
    }
    assert set(schema) == {CONF_HOST, CONF_PASSWORD}
    assert schema[CONF_PASSWORD].config["type"] == "password"

    data = {CONF_HOST: "camera.local", CONF_PASSWORD: "secret"}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=data
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "reer IP BabyCam"
    assert result["data"] == data
