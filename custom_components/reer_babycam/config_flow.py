"""Config flow for reer IP BabyCam."""

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class ReerBabyCamConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create a placeholder reer IP BabyCam entry."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the entry without network configuration."""
        return self.async_create_entry(title="reer IP BabyCam", data={})
