"""Verified local HTTP protocol for reer IP BabyCam."""

from asyncio import TimeoutError
from dataclasses import dataclass
import re

from aiohttp import (
    ClientConnectionError,
    ClientError,
    ClientSession,
    DigestAuthMiddleware,
)
from yarl import URL

from .const import (
    DEFAULT_PORT,
    DEFAULT_USERNAME,
    PARAMS_PATH,
    PROPERTIES_PATH,
    SNAPSHOT_PATH,
    STREAM_PATH,
)


class ReerBabyCamError(Exception):
    """Base camera error."""


class ReerBabyCamConnectionError(ReerBabyCamError):
    """The camera could not be reached."""


class ReerBabyCamAuthError(ReerBabyCamError):
    """The camera rejected the credentials."""


class ReerBabyCamProtocolError(ReerBabyCamError):
    """The camera returned an unexpected response."""


@dataclass(slots=True, frozen=True)
class ReerBabyCamInfo:
    """Verified camera identity and metadata."""

    device_id: str
    firmware_version: str | None


class ReerBabyCamClient:
    """Client for the verified camera endpoints."""

    def __init__(self, host: str, password: str, session: ClientSession) -> None:
        """Initialize the client with Home Assistant's managed session."""
        host = host.strip()
        if host.startswith("[") and host.endswith("]"):
            host = host[1:-1]
        self._base_url = URL.build(scheme="http", host=host, port=DEFAULT_PORT)
        self._password = password
        self._session = session
        self._auth = DigestAuthMiddleware(DEFAULT_USERNAME, password)

    async def async_get_info(self) -> ReerBabyCamInfo:
        """Fetch the exact verified identity and firmware fields."""
        device_id = await self._get_assignment(PARAMS_PATH, "id", required=True)
        assert device_id is not None
        firmware = await self._get_assignment(
            PROPERTIES_PATH, "firmware_ver", required=False
        )
        return ReerBabyCamInfo(device_id=device_id, firmware_version=firmware)

    async def async_get_snapshot(self) -> bytes:
        """Return the camera's JPEG bytes unchanged."""
        try:
            async with self._session.get(
                self._url(SNAPSHOT_PATH),
                allow_redirects=False,
                middlewares=(self._auth,),
            ) as response:
                self._check_status(response.status)
                if response.content_type.lower() not in {"image/jpeg", "image/jpg"}:
                    raise ReerBabyCamProtocolError("Camera returned a non-JPEG image")
                body = await response.read()
                if not body:
                    raise ReerBabyCamProtocolError("Camera returned an empty image")
                return body
        except ReerBabyCamError:
            raise
        except (TimeoutError, ClientConnectionError):
            raise ReerBabyCamConnectionError("Could not connect to camera") from None
        except ClientError:
            raise ReerBabyCamProtocolError("Camera HTTP exchange failed") from None

    def stream_url(self) -> URL:
        """Build the transient credential-bearing verified stream URL."""
        return (
            self._url(STREAM_PATH)
            .with_user(DEFAULT_USERNAME)
            .with_password(self._password)
        )

    async def _get_assignment(
        self, path: str, name: str, *, required: bool
    ) -> str | None:
        try:
            async with self._session.get(
                self._url(path),
                allow_redirects=False,
                middlewares=(self._auth,),
            ) as response:
                self._check_status(response.status)
                text = await response.text(errors="strict")
        except ReerBabyCamError:
            raise
        except (TimeoutError, ClientConnectionError):
            raise ReerBabyCamConnectionError("Could not connect to camera") from None
        except (ClientError, UnicodeError, LookupError):
            raise ReerBabyCamProtocolError("Camera HTTP exchange failed") from None

        return _extract_assignment(text, name, required=required)

    def _url(self, path: str) -> URL:
        return self._base_url.join(URL(path))

    @staticmethod
    def _check_status(status: int) -> None:
        if status in (401, 403):
            raise ReerBabyCamAuthError("Camera rejected the credentials")
        if not 200 <= status < 300:
            raise ReerBabyCamProtocolError("Camera returned an unexpected HTTP status")


def _extract_assignment(text: str, name: str, *, required: bool) -> str | None:
    assignment = re.compile(
        rf"\s*var\s+{re.escape(name)}\s*=\s*"
        rf"(?:'([^'\\]*)'|\"([^\"\\]*)\")\s*;\s*"
    )
    candidate = re.compile(rf"\s*var\s+{re.escape(name)}\b")
    found: str | None = None
    for line in text.splitlines():
        if not candidate.match(line):
            continue
        match = assignment.fullmatch(line)
        value = None if match is None else match[1] or match[2]
        if value is None or not value.strip() or found is not None:
            raise ReerBabyCamProtocolError(f"Camera returned malformed {name}")
        found = value
    if required and found is None:
        raise ReerBabyCamProtocolError(f"Camera response is missing {name}")
    return found
