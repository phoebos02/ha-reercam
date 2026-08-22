"""Config flow for reer IP BabyCam."""

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN


class ReerBabyCamConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure a reer IP BabyCam entry."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Store connection details without contacting the camera."""
        if user_input is not None:
            return self.async_create_entry(title="reer IP BabyCam", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): TextSelector(),
                    vol.Required(CONF_PASSWORD): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.PASSWORD,
                            autocomplete="current-password",
                        )
                    ),
                }
            ),
        )
