"""Runnable scaffold lifecycle check without external dependencies."""

import asyncio
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace


class ConfigFlow:
    def __init_subclass__(cls, domain: str, **kwargs: object) -> None:
        cls.domain = domain

    def async_create_entry(self, **result: object) -> dict[str, object]:
        return result


class ConfigEntry:
    def __init__(self, entry_id: str) -> None:
        self.entry_id = entry_id


class Camera:
    pass


class DeviceInfo(dict):
    pass


def install_home_assistant_stubs() -> None:
    """Install the tiny Home Assistant surface used by this scaffold."""
    modules = {
        "homeassistant": ModuleType("homeassistant"),
        "homeassistant.components": ModuleType("homeassistant.components"),
        "homeassistant.components.camera": ModuleType("homeassistant.components.camera"),
        "homeassistant.config_entries": ModuleType("homeassistant.config_entries"),
        "homeassistant.const": ModuleType("homeassistant.const"),
        "homeassistant.core": ModuleType("homeassistant.core"),
        "homeassistant.helpers": ModuleType("homeassistant.helpers"),
        "homeassistant.helpers.device_registry": ModuleType(
            "homeassistant.helpers.device_registry"
        ),
        "homeassistant.helpers.entity_platform": ModuleType(
            "homeassistant.helpers.entity_platform"
        ),
    }
    modules["homeassistant.components.camera"].Camera = Camera
    modules["homeassistant.config_entries"].ConfigEntry = ConfigEntry
    modules["homeassistant.config_entries"].ConfigFlow = ConfigFlow
    modules["homeassistant.config_entries"].ConfigFlowResult = dict
    modules["homeassistant.const"].Platform = SimpleNamespace(CAMERA="camera")
    modules["homeassistant.core"].HomeAssistant = object
    modules["homeassistant.helpers.device_registry"].DeviceInfo = DeviceInfo
    modules[
        "homeassistant.helpers.entity_platform"
    ].AddConfigEntryEntitiesCallback = object
    sys.modules.update(modules)


async def check_scaffold() -> None:
    """Check config creation, setup, entity/device creation, and unload."""
    sys.path.insert(0, str(Path(__file__).parents[1]))
    install_home_assistant_stubs()

    from custom_components.reer_babycam import async_setup_entry, async_unload_entry
    from custom_components.reer_babycam.camera import (
        ReerBabyCam,
        async_setup_entry as async_setup_camera,
    )
    from custom_components.reer_babycam.config_flow import ReerBabyCamConfigFlow

    flow_result = await ReerBabyCamConfigFlow().async_step_user()
    assert flow_result == {"title": "reer IP BabyCam", "data": {}}

    class ConfigEntries:
        async def async_forward_entry_setups(self, entry, platforms):
            assert platforms == ["camera"]

        async def async_unload_platforms(self, entry, platforms):
            assert platforms == ["camera"]
            return True

    entry = ConfigEntry("placeholder")
    hass = SimpleNamespace(config_entries=ConfigEntries())
    assert await async_setup_entry(hass, entry)

    entities = []
    await async_setup_camera(hass, entry, entities.extend)
    assert len(entities) == 1 and isinstance(entities[0], ReerBabyCam)
    assert entities[0]._attr_unique_id == "placeholder_camera"
    assert entities[0]._attr_device_info["identifiers"] == {
        ("reer_babycam", "placeholder")
    }
    assert await async_unload_entry(hass, entry)


if __name__ == "__main__":
    asyncio.run(check_scaffold())
