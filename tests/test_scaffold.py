"""Runnable scaffold lifecycle check without external dependencies."""

import asyncio
from enum import IntFlag
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace


class ConfigFlow:
    def __init_subclass__(cls, domain: str, **kwargs: object) -> None:
        cls.domain = domain

    def async_create_entry(self, **result: object) -> dict[str, object]:
        return result

    def async_show_form(self, **result: object) -> dict[str, object]:
        return result


class ConfigEntry:
    def __class_getitem__(cls, item: object):
        return cls

    def __init__(self, entry_id: str, data: dict[str, str] | None = None) -> None:
        self.entry_id = entry_id
        self.data = data or {}
        self.runtime_data = None


class Camera:
    pass


class CameraEntityFeature(IntFlag):
    STREAM = 2


class DeviceInfo(dict):
    pass


class ConfigEntryError(Exception):
    pass


class ConfigEntryNotReady(Exception):
    pass


class Schema:
    def __init__(self, schema: dict[str, object]) -> None:
        self.schema = schema


class TextSelectorConfig:
    def __init__(self, type: str = "text", autocomplete: str | None = None) -> None:
        self.type = type
        self.autocomplete = autocomplete


class TextSelector:
    def __init__(self, config: TextSelectorConfig | None = None) -> None:
        self.config = config or TextSelectorConfig()


def install_home_assistant_stubs() -> None:
    """Install the tiny Home Assistant surface used by this scaffold."""
    modules = {
        "homeassistant": ModuleType("homeassistant"),
        "homeassistant.components": ModuleType("homeassistant.components"),
        "homeassistant.components.camera": ModuleType("homeassistant.components.camera"),
        "homeassistant.config_entries": ModuleType("homeassistant.config_entries"),
        "homeassistant.const": ModuleType("homeassistant.const"),
        "homeassistant.core": ModuleType("homeassistant.core"),
        "homeassistant.exceptions": ModuleType("homeassistant.exceptions"),
        "homeassistant.helpers": ModuleType("homeassistant.helpers"),
        "homeassistant.helpers.aiohttp_client": ModuleType(
            "homeassistant.helpers.aiohttp_client"
        ),
        "homeassistant.helpers.device_registry": ModuleType(
            "homeassistant.helpers.device_registry"
        ),
        "homeassistant.helpers.entity_platform": ModuleType(
            "homeassistant.helpers.entity_platform"
        ),
        "homeassistant.helpers.selector": ModuleType("homeassistant.helpers.selector"),
        "voluptuous": ModuleType("voluptuous"),
    }
    modules["homeassistant.components.camera"].Camera = Camera
    modules["homeassistant.components.camera"].CameraEntityFeature = CameraEntityFeature
    modules["homeassistant.config_entries"].ConfigEntry = ConfigEntry
    modules["homeassistant.config_entries"].ConfigFlow = ConfigFlow
    modules["homeassistant.config_entries"].ConfigFlowResult = dict
    modules["homeassistant.const"].CONF_HOST = "host"
    modules["homeassistant.const"].CONF_PASSWORD = "password"
    modules["homeassistant.const"].Platform = SimpleNamespace(CAMERA="camera")
    modules["homeassistant.core"].HomeAssistant = object
    modules["homeassistant.exceptions"].ConfigEntryError = ConfigEntryError
    modules["homeassistant.exceptions"].ConfigEntryNotReady = ConfigEntryNotReady
    modules["homeassistant.helpers.aiohttp_client"].async_get_clientsession = (
        lambda hass: hass.session
    )
    modules["homeassistant.helpers.device_registry"].DeviceInfo = DeviceInfo
    modules[
        "homeassistant.helpers.entity_platform"
    ].AddConfigEntryEntitiesCallback = object
    modules["homeassistant.helpers.selector"].TextSelector = TextSelector
    modules["homeassistant.helpers.selector"].TextSelectorConfig = TextSelectorConfig
    modules["homeassistant.helpers.selector"].TextSelectorType = SimpleNamespace(
        PASSWORD="password"
    )
    modules["voluptuous"].Required = lambda key: key
    modules["voluptuous"].Schema = Schema
    sys.modules.update(modules)


async def check_scaffold() -> None:
    """Check config creation, setup, entity/device creation, and unload."""
    sys.path.insert(0, str(Path(__file__).parents[1]))
    from test_api import (
        ClientConnectionError,
        Response,
        Session,
        install_http_stubs,
    )

    install_http_stubs()
    install_home_assistant_stubs()

    from custom_components.reer_babycam import (
        async_setup_entry,
        async_unload_entry,
    )
    from custom_components.reer_babycam.api import (
        ReerBabyCamAuthError,
        ReerBabyCamConnectionError,
    )
    from custom_components.reer_babycam.camera import (
        ReerBabyCam,
        async_setup_entry as async_setup_camera,
    )
    from custom_components.reer_babycam.config_flow import ReerBabyCamConfigFlow

    flow = ReerBabyCamConfigFlow()
    flow_result = await flow.async_step_user()
    schema = flow_result["data_schema"].schema
    assert flow_result["step_id"] == "user"
    assert list(schema) == ["host", "password"]
    assert schema["host"].config.type == "text"
    assert schema["password"].config.type == "password"
    assert schema["password"].config.autocomplete == "current-password"

    user_input = {"host": "192.0.2.1", "password": "secret"}
    flow_result = await flow.async_step_user(user_input)
    assert flow_result == {"title": "reer IP BabyCam", "data": user_input}

    class ConfigEntries:
        def __init__(self) -> None:
            self.forwarded = 0

        async def async_forward_entry_setups(self, entry, platforms):
            assert platforms == ["camera"]
            self.forwarded += 1

        async def async_unload_platforms(self, entry, platforms):
            assert platforms == ["camera"]
            return True

    snapshot = b"\xff\xd8jpeg\xff\xd9"
    session = Session(
        Response(text="var id='camera-1';"),
        Response(text="var firmware_ver='42.7.3.4.70';"),
        Response(body=snapshot, content_type="image/jpeg"),
    )
    entry = ConfigEntry("placeholder", user_input)
    hass = SimpleNamespace(config_entries=ConfigEntries(), session=session)
    assert await async_setup_entry(hass, entry)
    assert entry.runtime_data.info.device_id == "camera-1"
    assert hass.config_entries.forwarded == 1

    entities = []
    await async_setup_camera(hass, entry, entities.extend)
    assert len(entities) == 1 and isinstance(entities[0], ReerBabyCam)
    assert entities[0]._attr_unique_id == "camera-1_camera"
    assert entities[0]._attr_supported_features == CameraEntityFeature.STREAM
    assert entities[0]._attr_device_info["identifiers"] == {
        ("reer_babycam", "camera-1")
    }
    assert entities[0]._attr_device_info == {
        "identifiers": {("reer_babycam", "camera-1")},
        "manufacturer": "reer",
        "model": "IP BabyCam 80300",
        "name": "reer IP BabyCam",
        "serial_number": "camera-1",
        "sw_version": "42.7.3.4.70",
    }
    assert await entities[0].async_camera_image() == snapshot
    assert await entities[0].stream_source() == (
        "http://admin:secret@192.0.2.1:80/av.asf?stream=1"
    )
    for response, expected_error in (
        (Response(status=401), ReerBabyCamAuthError),
        (ClientConnectionError("secret"), ReerBabyCamConnectionError),
    ):
        session.results.append(response)
        try:
            await entities[0].async_camera_image()
        except expected_error as err:
            assert "secret" not in str(err)
        else:
            raise AssertionError(f"Expected {expected_error.__name__}")
    assert await async_unload_entry(hass, entry)

    optional_firmware_entry = ConfigEntry("optional", user_input)
    optional_hass = SimpleNamespace(
        config_entries=ConfigEntries(),
        session=Session(
            Response(text="var id='camera-2';"),
            Response(),
        ),
    )
    assert await async_setup_entry(optional_hass, optional_firmware_entry)
    optional_entities = []
    await async_setup_camera(
        optional_hass, optional_firmware_entry, optional_entities.extend
    )
    assert optional_entities[0]._attr_device_info["sw_version"] is None

    password = "do-not-leak"
    failures = (
        (Session(Response(status=401)), ConfigEntryError),
        (Session(ClientConnectionError(password)), ConfigEntryNotReady),
    )
    for failing_session, expected_error in failures:
        failing_entry = ConfigEntry(
            "failure", {"host": "camera.local", "password": password}
        )
        failing_hass = SimpleNamespace(
            config_entries=ConfigEntries(), session=failing_session
        )
        try:
            await async_setup_entry(failing_hass, failing_entry)
        except expected_error as err:
            assert password not in str(err)
        else:
            raise AssertionError(f"Expected {expected_error.__name__}")


if __name__ == "__main__":
    asyncio.run(check_scaffold())
