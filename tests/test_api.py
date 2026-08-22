"""Tests for the verified reer BabyCam HTTP contract."""

import asyncio
import hashlib
import re
from collections.abc import Callable

import pytest
from aiohttp import ClientSession, ClientTimeout, web

from custom_components.reer_babycam import api
from custom_components.reer_babycam.api import (
    ReerBabyCamAuthError,
    ReerBabyCamClient,
    ReerBabyCamConnectionError,
    ReerBabyCamProtocolError,
)

PASSWORD = "s/e:c@r?e#t%"
JPEG = b"\xff\xd8jpeg\xff\xd9"


async def _server(aiohttp_server, monkeypatch, handler: Callable):
    app = web.Application()
    app.router.add_get("/{path:.*}", handler)
    server = await aiohttp_server(app)
    monkeypatch.setattr(api, "DEFAULT_PORT", server.port)
    return server


def _digest_fields(header: str) -> dict[str, str]:
    return {
        key: quoted or bare
        for key, quoted, bare in re.findall(
            r'(\w+)=(?:"([^"]*)"|([^,\s]+))', header.removeprefix("Digest ")
        )
    }


@pytest.mark.usefixtures("socket_enabled")
async def test_real_digest_exchange(aiohttp_server, monkeypatch) -> None:
    """Complete and validate an actual aiohttp Digest exchange."""
    nonce = "test-nonce"
    authenticated: list[str] = []

    async def handler(request: web.Request) -> web.Response:
        if not (authorization := request.headers.get("Authorization")):
            return web.Response(
                status=401,
                headers={
                    "WWW-Authenticate": (
                        f'Digest realm="ip camera", nonce="{nonce}", '
                        'qop="auth", algorithm=MD5'
                    )
                },
            )
        fields = _digest_fields(authorization)
        ha1 = hashlib.md5(f"admin:ip camera:{PASSWORD}".encode()).hexdigest()
        ha2 = hashlib.md5(f"GET:{fields['uri']}".encode()).hexdigest()
        expected = hashlib.md5(
            (
                f"{ha1}:{nonce}:{fields['nc']}:{fields['cnonce']}:"
                f"{fields['qop']}:{ha2}"
            ).encode()
        ).hexdigest()
        assert fields["username"] == "admin"
        assert fields["response"] == expected
        authenticated.append(request.path)
        text = (
            "var ignored='x';\nvar id='camera-1';"
            if request.path == "/get_params.cgi"
            else 'var firmware_ver="42.7.3.4.70";'
        )
        return web.Response(text=text)

    server = await _server(aiohttp_server, monkeypatch, handler)
    async with ClientSession() as session:
        info = await ReerBabyCamClient(server.host, PASSWORD, session).async_get_info()

    assert info.device_id == "camera-1"
    assert info.firmware_version == "42.7.3.4.70"
    assert authenticated == ["/get_params.cgi", "/get_properties.cgi"]


@pytest.mark.usefixtures("socket_enabled")
async def test_optional_firmware(aiohttp_server, monkeypatch) -> None:
    async def handler(request: web.Request) -> web.Response:
        text = "var id='camera-1';" if request.path == "/get_params.cgi" else ""
        return web.Response(text=text)

    server = await _server(aiohttp_server, monkeypatch, handler)
    async with ClientSession() as session:
        info = await ReerBabyCamClient(server.host, PASSWORD, session).async_get_info()

    assert info.firmware_version is None


@pytest.mark.usefixtures("socket_enabled")
@pytest.mark.parametrize("status", [401, 403])
async def test_auth_statuses(aiohttp_server, monkeypatch, status: int) -> None:
    async def handler(_: web.Request) -> web.Response:
        return web.Response(status=status)

    server = await _server(aiohttp_server, monkeypatch, handler)
    async with ClientSession() as session:
        with pytest.raises(ReerBabyCamAuthError, match="rejected"):
            await ReerBabyCamClient(server.host, PASSWORD, session).async_get_info()


@pytest.mark.usefixtures("socket_enabled")
async def test_timeout(aiohttp_server, monkeypatch) -> None:
    async def handler(_: web.Request) -> web.Response:
        await asyncio.sleep(1)
        return web.Response()

    server = await _server(aiohttp_server, monkeypatch, handler)
    async with ClientSession(timeout=ClientTimeout(total=0.01)) as session:
        with pytest.raises(ReerBabyCamConnectionError, match="connect"):
            await ReerBabyCamClient(server.host, PASSWORD, session).async_get_info()


@pytest.mark.usefixtures("socket_enabled")
async def test_connection_failure(monkeypatch, unused_tcp_port: int) -> None:
    monkeypatch.setattr(api, "DEFAULT_PORT", unused_tcp_port)
    async with ClientSession() as session:
        with pytest.raises(ReerBabyCamConnectionError, match="connect") as error:
            await ReerBabyCamClient("127.0.0.1", PASSWORD, session).async_get_info()
    assert PASSWORD not in str(error.value)


@pytest.mark.usefixtures("socket_enabled")
async def test_redirect_is_not_followed(aiohttp_server, monkeypatch) -> None:
    forwarded = False

    async def target(_: web.Request) -> web.Response:
        nonlocal forwarded
        forwarded = True
        return web.Response(text="var id='wrong';")

    target_app = web.Application()
    target_app.router.add_get("/target", target)
    target_server = await aiohttp_server(target_app)

    async def redirect(_: web.Request) -> web.Response:
        raise web.HTTPFound(f"http://{target_server.host}:{target_server.port}/target")

    server = await _server(aiohttp_server, monkeypatch, redirect)
    async with ClientSession() as session:
        with pytest.raises(ReerBabyCamProtocolError, match="status"):
            await ReerBabyCamClient(server.host, PASSWORD, session).async_get_info()
    assert forwarded is False


@pytest.mark.usefixtures("socket_enabled")
@pytest.mark.parametrize("status", [302, 500])
async def test_unexpected_status(aiohttp_server, monkeypatch, status: int) -> None:
    async def handler(_: web.Request) -> web.Response:
        return web.Response(status=status)

    server = await _server(aiohttp_server, monkeypatch, handler)
    async with ClientSession() as session:
        with pytest.raises(ReerBabyCamProtocolError, match="status"):
            await ReerBabyCamClient(server.host, PASSWORD, session).async_get_info()


@pytest.mark.usefixtures("socket_enabled")
@pytest.mark.parametrize(
    "body",
    [
        "var other='x';",
        "var id=broken;",
        "var id='';",
        "var id='one';\nvar id='two';",
    ],
)
async def test_invalid_identity(aiohttp_server, monkeypatch, body: str) -> None:
    async def handler(_: web.Request) -> web.Response:
        return web.Response(text=body)

    server = await _server(aiohttp_server, monkeypatch, handler)
    async with ClientSession() as session:
        with pytest.raises(ReerBabyCamProtocolError):
            await ReerBabyCamClient(server.host, PASSWORD, session).async_get_info()


@pytest.mark.usefixtures("socket_enabled")
async def test_malformed_firmware(aiohttp_server, monkeypatch) -> None:
    async def handler(request: web.Request) -> web.Response:
        text = (
            "var id='camera-1';"
            if request.path == "/get_params.cgi"
            else "var firmware_ver=broken;"
        )
        return web.Response(text=text)

    server = await _server(aiohttp_server, monkeypatch, handler)
    async with ClientSession() as session:
        with pytest.raises(ReerBabyCamProtocolError, match="firmware_ver"):
            await ReerBabyCamClient(server.host, PASSWORD, session).async_get_info()


@pytest.mark.usefixtures("socket_enabled")
async def test_snapshot(aiohttp_server, monkeypatch) -> None:
    async def handler(_: web.Request) -> web.Response:
        return web.Response(body=JPEG, content_type="image/jpeg")

    server = await _server(aiohttp_server, monkeypatch, handler)
    async with ClientSession() as session:
        assert (
            await ReerBabyCamClient(
                server.host, PASSWORD, session
            ).async_get_snapshot()
            == JPEG
        )


@pytest.mark.usefixtures("socket_enabled")
@pytest.mark.parametrize(
    ("status", "body", "content_type"),
    [
        (401, JPEG, "image/jpeg"),
        (500, JPEG, "image/jpeg"),
        (200, b"", "image/jpeg"),
        (200, JPEG, "text/plain"),
    ],
)
async def test_invalid_snapshot(
    aiohttp_server,
    monkeypatch,
    status: int,
    body: bytes,
    content_type: str,
) -> None:
    async def handler(_: web.Request) -> web.Response:
        return web.Response(status=status, body=body, content_type=content_type)

    server = await _server(aiohttp_server, monkeypatch, handler)
    async with ClientSession() as session:
        with pytest.raises((ReerBabyCamAuthError, ReerBabyCamProtocolError)) as error:
            await ReerBabyCamClient(
                server.host, PASSWORD, session
            ).async_get_snapshot()
    assert PASSWORD not in str(error.value)


def test_stream_url_uses_real_yarl_and_escapes_credentials() -> None:
    client = ReerBabyCamClient("[2001:db8::1]", PASSWORD, None)  # type: ignore[arg-type]
    url = client.stream_url()

    assert url.password == PASSWORD
    assert str(url) == (
        "http://admin:s%2Fe%3Ac%40r%3Fe%23t%25@[2001:db8::1]/av.asf?stream=1"
    )
