"""Config flow for reer IP BabyCam."""

from collections.abc import Mapping
from ipaddress import ip_address
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from homeassistant.util.network import is_host_valid

from .api import (
    ReerBabyCamAuthError,
    ReerBabyCamClient,
    ReerBabyCamConnectionError,
    ReerBabyCamInfo,
    ReerBabyCamProtocolError,
)
from .const import DOMAIN

_PASSWORD_SELECTOR = TextSelector(
    TextSelectorConfig(
        type=TextSelectorType.PASSWORD,
        autocomplete="current-password",
    )
)
_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): TextSelector(),
        vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
    }
)
_REAUTH_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR})
_RECONFIGURE_SCHEMA = vol.Schema({vol.Required(CONF_HOST): TextSelector()})


def _normalize_host(value: str) -> str:
    """Return a canonical bare IP address or hostname."""
    host = value.strip()
    if not is_host_valid(host):
        raise ValueError
    try:
        return str(ip_address(host))
    except ValueError:
        return host.removesuffix(".").lower()


class ReerBabyCamConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure a reer IP BabyCam entry."""

    async def _async_get_info(
        self, host: str, password: str
    ) -> tuple[ReerBabyCamInfo | None, str | None]:
        """Fetch camera information and map errors for the UI."""
        try:
            info = await ReerBabyCamClient(
                host, password, async_get_clientsession(self.hass)
            ).async_get_info()
        except ReerBabyCamConnectionError:
            return None, "cannot_connect"
        except ReerBabyCamAuthError:
            return None, "invalid_auth"
        except ReerBabyCamProtocolError:
            return None, "invalid_response"
        except Exception:  # noqa: BLE001
            return None, "unknown"
        return info, None

    def _update_and_abort(
        self, entry: ConfigEntry, updates: dict[str, Any]
    ) -> ConfigFlowResult:
        """Update the entry and reload through its listener when available."""
        if entry.update_listeners:
            return self.async_update_and_abort(entry, data_updates=updates)
        return self.async_update_reload_and_abort(
            entry,
            data_updates=updates,
            reload_even_if_entry_is_unchanged=False,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Validate and create a camera entry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                host = _normalize_host(user_input[CONF_HOST])
            except (TypeError, ValueError):
                errors["base"] = "invalid_host"
            else:
                info, error = await self._async_get_info(
                    host, user_input[CONF_PASSWORD]
                )
                if error:
                    errors["base"] = error
                else:
                    assert info is not None
                    await self.async_set_unique_id(info.device_id)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="reer IP BabyCam",
                        data={
                            CONF_HOST: host,
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                        },
                    )

        return self.async_show_form(
            step_id="user", data_schema=_USER_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Start reauthentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Validate a replacement password."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        if user_input is not None:
            info, error = await self._async_get_info(
                entry.data[CONF_HOST], user_input[CONF_PASSWORD]
            )
            if error:
                errors["base"] = error
            elif info is None or info.device_id != entry.unique_id:
                errors["base"] = "wrong_device"
            else:
                return self._update_and_abort(
                    entry, {CONF_PASSWORD: user_input[CONF_PASSWORD]}
                )

        return self.async_show_form(
            step_id="reauth_confirm", data_schema=_REAUTH_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Validate a replacement host."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            try:
                host = _normalize_host(user_input[CONF_HOST])
            except (TypeError, ValueError):
                errors["base"] = "invalid_host"
            else:
                info, error = await self._async_get_info(
                    host, entry.data[CONF_PASSWORD]
                )
                if error:
                    errors["base"] = error
                elif info is None or info.device_id != entry.unique_id:
                    errors["base"] = "wrong_device"
                else:
                    return self._update_and_abort(entry, {CONF_HOST: host})

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                _RECONFIGURE_SCHEMA, {CONF_HOST: entry.data[CONF_HOST]}
            ),
            errors=errors,
        )
