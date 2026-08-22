"""Camera entity for reer IP BabyCam."""

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ReerBabyCamConfigEntry
from .api import ReerBabyCamClient, ReerBabyCamInfo
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ReerBabyCamConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the camera."""
    data = entry.runtime_data
    async_add_entities([ReerBabyCam(data.client, data.info)])


class ReerBabyCam(Camera):
    """reer IP BabyCam entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, client: ReerBabyCamClient, info: ReerBabyCamInfo) -> None:
        """Initialize the camera."""
        super().__init__()
        self._client = client
        self._attr_unique_id = f"{info.device_id}_camera"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, info.device_id)},
            manufacturer="reer",
            model="IP BabyCam 80300",
            name="reer IP BabyCam",
            serial_number=info.device_id,
            sw_version=info.firmware_version,
        )

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes:
        """Return a still image."""
        return await self._client.async_get_snapshot()

    async def stream_source(self) -> str:
        """Return the verified native stream source."""
        return str(self._client.stream_url())
