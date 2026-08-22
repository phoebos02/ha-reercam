"""Runnable checks for the verified BabyCam HTTP contract."""

import asyncio
from pathlib import Path
import sys
from types import ModuleType
from urllib.parse import quote, urljoin, urlsplit


class ClientError(Exception):
    pass


class ClientConnectionError(ClientError):
    pass


class DigestAuthMiddleware:
    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = password


class URL:
    def __init__(self, value: str) -> None:
        self.value = value
        self.user: str | None = None
        self.password: str | None = None

    @classmethod
    def build(cls, *, scheme: str, host: str, port: int):
        rendered_host = f"[{host}]" if ":" in host else host
        return cls(f"{scheme}://{rendered_host}:{port}")

    def join(self, other):
        return type(self)(urljoin(f"{self.value}/", other.value))

    def with_user(self, user: str):
        result = type(self)(self.value)
        result.user, result.password = user, self.password
        return result

    def with_password(self, password: str):
        result = type(self)(self.value)
        result.user, result.password = self.user, password
        return result

    def __str__(self) -> str:
        if self.user is None:
            return self.value
        parts = urlsplit(self.value)
        credentials = quote(self.user, safe="")
        if self.password is not None:
            credentials += f":{quote(self.password, safe='')}"
        return f"{parts.scheme}://{credentials}@{parts.netloc}{parts.path}" + (
            f"?{parts.query}" if parts.query else ""
        )


def install_http_stubs() -> None:
    aiohttp = ModuleType("aiohttp")
    aiohttp.ClientConnectionError = ClientConnectionError
    aiohttp.ClientError = ClientError
    aiohttp.ClientSession = object
    aiohttp.DigestAuthMiddleware = DigestAuthMiddleware
    yarl = ModuleType("yarl")
    yarl.URL = URL
    sys.modules.update({"aiohttp": aiohttp, "yarl": yarl})


class Response:
    def __init__(
        self,
        *,
        status: int = 200,
        text: str = "",
        body: bytes = b"",
        content_type: str = "text/plain",
    ) -> None:
        self.status = status
        self._text = text
        self._body = body
        self.content_type = content_type

    async def text(self, *, errors: str) -> str:
        assert errors == "strict"
        return self._text

    async def read(self) -> bytes:
        return self._body


class RequestContext:
    def __init__(self, result: Response | BaseException) -> None:
        self.result = result

    async def __aenter__(self) -> Response:
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result

    async def __aexit__(self, *args: object) -> None:
        pass


class Session:
    def __init__(self, *results: Response | BaseException) -> None:
        self.results = list(results)
        self.requests: list[tuple[str, dict[str, object]]] = []

    def get(self, url: URL, **kwargs: object) -> RequestContext:
        self.requests.append((str(url), kwargs))
        return RequestContext(self.results.pop(0))


async def check_api() -> None:
    sys.path.insert(0, str(Path(__file__).parents[1]))
    install_http_stubs()
    from test_scaffold import install_home_assistant_stubs

    install_home_assistant_stubs()

    from custom_components.reer_babycam.api import (
        ReerBabyCamAuthError,
        ReerBabyCamClient,
        ReerBabyCamConnectionError,
        ReerBabyCamProtocolError,
    )

    password = "s/e:c@r?e#t%"
    session = Session(
        Response(text="var ignored='x';\nvar id='camera-1';"),
        Response(text='var firmware_ver="42.7.3.4.70";'),
    )
    client = ReerBabyCamClient("192.0.2.1", password, session)
    info = await client.async_get_info()
    assert info.device_id == "camera-1"
    assert info.firmware_version == "42.7.3.4.70"
    assert [request[0] for request in session.requests] == [
        "http://192.0.2.1:80/get_params.cgi",
        "http://192.0.2.1:80/get_properties.cgi",
    ]
    for _, kwargs in session.requests:
        assert kwargs["allow_redirects"] is False
        middleware = kwargs["middlewares"][0]
        assert (middleware.login, middleware.password) == ("admin", password)

    snapshot = b"\xff\xd8jpeg\xff\xd9"
    session = Session(Response(body=snapshot, content_type="image/jpeg"))
    assert (
        await ReerBabyCamClient(
            "camera.local", password, session
        ).async_get_snapshot()
        == snapshot
    )

    stream_url = ReerBabyCamClient(
        "[2001:db8::1]", password, Session()
    ).stream_url()
    stream = str(stream_url)
    assert stream_url.password == password
    assert password not in stream
    assert stream.endswith("@[2001:db8::1]:80/av.asf?stream=1")

    info = await ReerBabyCamClient(
        "camera.local",
        password,
        Session(Response(text="var id='camera-2';"), Response()),
    ).async_get_info()
    assert info.firmware_version is None

    cases = [
        (Session(Response(status=401)), ReerBabyCamAuthError),
        (Session(asyncio.TimeoutError(password)), ReerBabyCamConnectionError),
        (Session(ClientConnectionError(password)), ReerBabyCamConnectionError),
        (Session(Response(text="var id=broken;")), ReerBabyCamProtocolError),
        (Session(Response(text=f"var id={password};")), ReerBabyCamProtocolError),
        (Session(Response(text="var other='x';")), ReerBabyCamProtocolError),
        (Session(Response(status=302)), ReerBabyCamProtocolError),
    ]
    for failing_session, error_type in cases:
        try:
            client = ReerBabyCamClient("camera.local", password, failing_session)
            await client.async_get_info()
        except error_type as err:
            assert password not in str(err)
        else:
            raise AssertionError(f"Expected {error_type.__name__}")

    session = Session(
        Response(text="var id='camera-1';"),
        Response(text="var firmware_ver=broken;"),
    )
    try:
        await ReerBabyCamClient("camera.local", password, session).async_get_info()
    except ReerBabyCamProtocolError as err:
        assert password not in str(err)
    else:
        raise AssertionError("Expected malformed firmware to fail")

    for response in (
        Response(body=b"", content_type="image/jpeg"),
        Response(body=snapshot, content_type="text/plain"),
    ):
        try:
            client = ReerBabyCamClient("camera.local", password, Session(response))
            await client.async_get_snapshot()
        except ReerBabyCamProtocolError as err:
            assert password not in str(err)
        else:
            raise AssertionError("Expected invalid snapshot to fail")


if __name__ == "__main__":
    asyncio.run(check_api())
